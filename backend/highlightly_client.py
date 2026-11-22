"""Kota korumalı ve çoklu API anahtarlı Highlightly Football istemcisi."""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

try:
    from turso_client import TursoClient
except ImportError:
    from backend.turso_client import TursoClient


BACKEND_DIR = Path(__file__).resolve().parent
DATA_DIR = BACKEND_DIR / "data"
BRONZE_DIR = DATA_DIR / "bronze"
MANIFEST_FILE = BRONZE_DIR / "manifest.json"
QUOTA_FILE = DATA_DIR / "quota_state.json"
DEFAULT_ENV_PATH = BACKEND_DIR / ".env"

PLACEHOLDER_PREFIXES = ("buraya_", "your_", "example_", "<")


def load_env_file(env_path: Path = DEFAULT_ENV_PATH) -> dict[str, str]:
    """Standart kütüphane ile .env dosyasını okur ve os.environ'a ekler."""
    parsed: dict[str, str] = {}
    if not env_path.exists():
        return parsed

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1].strip()
        parsed[key] = value
        if key not in os.environ or not os.environ[key]:
            os.environ[key] = value
    return parsed


def _is_valid_key(value: str) -> bool:
    v = value.strip()
    if not v:
        return False
    lower = v.lower()
    return not any(lower.startswith(prefix) for prefix in PLACEHOLDER_PREFIXES)


def collect_api_keys() -> list[str]:
    """HIGHLIGHTLY_API_KEY_* ve HIGHLIGHTLY_API_KEYS değişkenlerinden tüm anahtarları toplar."""
    keys: list[str] = []
    seen: set[str] = set()

    numbered: list[tuple[int, str]] = []
    for k, v in os.environ.items():
        match = re.fullmatch(r"HIGHLIGHTLY_API_KEY_(\d+)", k)
        if match and _is_valid_key(v):
            numbered.append((int(match.group(1)), v.strip()))

    numbered.sort(key=lambda item: item[0])
    for _, key_val in numbered:
        if key_val not in seen:
            seen.add(key_val)
            keys.append(key_val)

    single = os.environ.get("HIGHLIGHTLY_API_KEY", "").strip()
    if _is_valid_key(single) and single not in seen:
        seen.add(single)
        keys.append(single)

    multi_raw = os.environ.get("HIGHLIGHTLY_API_KEYS", "")
    for part in multi_raw.split(","):
        candidate = part.strip()
        if _is_valid_key(candidate) and candidate not in seen:
            seen.add(candidate)
            keys.append(candidate)

    return keys


def _key_fingerprint(api_key: str) -> str:
    digest = hashlib.sha256(api_key.encode("utf-8")).hexdigest()[:8]
    tail = api_key[-4:] if len(api_key) >= 4 else "****"
    return f"key_{digest} (***{tail})"


@dataclass
class KeyQuotaInfo:
    index: int
    fingerprint: str
    used: int
    safe_limit: int
    daily_limit: int
    exhausted: bool

    @property
    def remaining_safe(self) -> int:
        if self.exhausted:
            return 0
        return max(0, self.safe_limit - self.used)


class HighlightlyClient:
    """Çoklu API anahtarı döndüren, disk önbellekli ve kota korumalı Highlightly istemcisi."""

    def __init__(self, max_requests_per_run: int | None = None) -> None:
        load_env_file()
        BRONZE_DIR.mkdir(parents=True, exist_ok=True)

        self.base_url = os.environ.get(
            "HIGHLIGHTLY_BASE_URL", "https://sports.highlightly.net/football"
        ).rstrip("/")
        self.auth_mode = os.environ.get("HIGHLIGHTLY_AUTH_MODE", "x-rapidapi-key").strip().lower()
        self.rapidapi_host = os.environ.get("HIGHLIGHTLY_RAPIDAPI_HOST", "").strip()

        self.daily_limit = int(os.environ.get("DAILY_LIMIT_PER_KEY", "100"))
        self.safe_limit = int(os.environ.get("SAFE_LIMIT_PER_KEY", "99"))
        default_budget = int(os.environ.get("DEFAULT_RUN_BUDGET", "15"))
        self.run_budget = default_budget if max_requests_per_run is None else max_requests_per_run

        self.keys = collect_api_keys()
        self.requests_made_this_run = 0
        self.cache_hits_this_run = 0
        self.budget_stopped = False
        self.turso = TursoClient()
        self._quota_state = self._load_quota_state()
        if self.turso.enabled:
            self._merge_remote_quota()
        self._manifest = self._load_and_backfill_manifest()

    @staticmethod
    def _atomic_write_text(target: Path, content: str) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = target.with_suffix(target.suffix + ".tmp")
        tmp_path.write_text(content, encoding="utf-8")
        for attempt in range(6):
            try:
                os.replace(tmp_path, target)
                return
            except PermissionError:
                if attempt < 5:
                    time.sleep(0.08 * (attempt + 1))
                else:
                    target.write_text(content, encoding="utf-8")
                    try:
                        tmp_path.unlink(missing_ok=True)
                    except OSError:
                        pass

    @staticmethod
    def _determine_immutable(cache_group: str, cache_name: str, payload: Any) -> bool:
        if cache_group in ("leagues", "statistics"):
            return True
        if cache_group == "standings" and any(y in cache_name for y in ("2019", "2020", "2021", "2022", "2023", "2024", "2025")):
            return True
        if cache_group == "match_details":
            items = payload if isinstance(payload, list) else [payload]
            return any(
                isinstance(it, dict) and (it.get("state") or {}).get("description") == "Finished"
                for it in items
            )
        if cache_group == "lineups" and isinstance(payload, dict):
            ht = payload.get("homeTeam") or {}
            return bool(ht.get("initialLineup"))
        return False

    def _load_and_backfill_manifest(self) -> dict[str, Any]:
        manifest: dict[str, Any] = {"updatedAt": "", "files": {}}
        if MANIFEST_FILE.exists():
            try:
                loaded = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
                if isinstance(loaded, dict) and isinstance(loaded.get("files"), dict):
                    manifest = loaded
            except (json.JSONDecodeError, OSError):
                pass

        changed = False
        files_map: dict[str, Any] = manifest["files"]
        for fpath in sorted(BRONZE_DIR.rglob("*.json")):
            if fpath == MANIFEST_FILE:
                continue
            rel = fpath.relative_to(BRONZE_DIR).as_posix()
            if rel not in files_map:
                raw_bytes = fpath.read_bytes()
                sha = hashlib.sha256(raw_bytes).hexdigest()
                group = fpath.parent.name
                try:
                    parsed = json.loads(raw_bytes.decode("utf-8"))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    parsed = None
                files_map[rel] = {
                    "sha256": sha,
                    "bytes": len(raw_bytes),
                    "immutable": self._determine_immutable(group, fpath.stem, parsed),
                    "archivedAt": datetime.now(timezone(timedelta(hours=3))).isoformat(),
                }
                changed = True

        if changed or not MANIFEST_FILE.exists():
            manifest["updatedAt"] = datetime.now(timezone(timedelta(hours=3))).isoformat()
            self._atomic_write_text(
                MANIFEST_FILE,
                json.dumps(manifest, indent=2, ensure_ascii=False),
            )
        return manifest

    def _record_manifest_entry(self, cache_file: Path, cache_group: str, cache_name: str, raw_text: str, payload: Any) -> None:
        rel = cache_file.relative_to(BRONZE_DIR).as_posix()
        raw_bytes = raw_text.encode("utf-8")
        self._manifest.setdefault("files", {})[rel] = {
            "sha256": hashlib.sha256(raw_bytes).hexdigest(),
            "bytes": len(raw_bytes),
            "immutable": self._determine_immutable(cache_group, cache_name, payload),
            "archivedAt": datetime.now(timezone(timedelta(hours=3))).isoformat(),
        }
        self._manifest["updatedAt"] = datetime.now(timezone(timedelta(hours=3))).isoformat()
        self._atomic_write_text(
            MANIFEST_FILE,
            json.dumps(self._manifest, indent=2, ensure_ascii=False),
        )

    def _today_str(self) -> str:
        return date.today().isoformat()

    def _load_quota_state(self) -> dict[str, Any]:
        today = self._today_str()
        if QUOTA_FILE.exists():
            try:
                data = json.loads(QUOTA_FILE.read_text(encoding="utf-8"))
                if data.get("date") == today:
                    return data
            except (json.JSONDecodeError, OSError):
                pass
        return {"date": today, "keys": {}}

    def _save_quota_state(self) -> None:
        QUOTA_FILE.parent.mkdir(parents=True, exist_ok=True)
        QUOTA_FILE.write_text(
            json.dumps(self._quota_state, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _merge_remote_quota(self) -> None:
        try:
            remote_keys = self.turso.load_quota_for_date(self._today_str())
        except Exception:
            return
        local_keys = self._quota_state.setdefault("keys", {})
        for fp, r_entry in remote_keys.items():
            l_entry = local_keys.setdefault(fp, {"used": 0, "exhausted": False})
            l_entry["used"] = max(int(l_entry.get("used", 0)), int(r_entry.get("used", 0)))
            l_entry["exhausted"] = bool(l_entry.get("exhausted", False)) or bool(r_entry.get("exhausted", False))
        self._save_quota_state()

    def get_key_statuses(self) -> list[KeyQuotaInfo]:
        statuses: list[KeyQuotaInfo] = []
        key_map: dict[str, Any] = self._quota_state.setdefault("keys", {})
        for idx, k in enumerate(self.keys, start=1):
            fp = _key_fingerprint(k)
            entry = key_map.get(fp, {})
            used = int(entry.get("used", 0))
            exhausted = bool(entry.get("exhausted", False)) or used >= self.safe_limit
            statuses.append(
                KeyQuotaInfo(
                    index=idx,
                    fingerprint=fp,
                    used=used,
                    safe_limit=self.safe_limit,
                    daily_limit=self.daily_limit,
                    exhausted=exhausted,
                )
            )
        return statuses

    def total_remaining_safe_quota(self) -> int:
        return sum(s.remaining_safe for s in self.get_key_statuses())

    def _pick_next_key(self) -> tuple[int, str, str] | None:
        key_map: dict[str, Any] = self._quota_state.setdefault("keys", {})
        for idx, k in enumerate(self.keys, start=1):
            fp = _key_fingerprint(k)
            entry = key_map.setdefault(fp, {"used": 0, "exhausted": False})
            if not entry.get("exhausted", False) and int(entry.get("used", 0)) < self.safe_limit:
                return idx, k, fp
        return None

    def _increment_key_usage(self, fp: str, mark_exhausted: bool = False) -> None:
        key_map: dict[str, Any] = self._quota_state.setdefault("keys", {})
        entry = key_map.setdefault(fp, {"used": 0, "exhausted": False})
        entry["used"] = int(entry.get("used", 0)) + 1
        if mark_exhausted or entry["used"] >= self.safe_limit:
            entry["exhausted"] = True
        self._save_quota_state()
        if self.turso.enabled:
            try:
                self.turso.upsert_quota(self._today_str(), fp, int(entry["used"]), bool(entry["exhausted"]))
            except Exception as exc:
                print(f"[Turso Kota Uyarısı] {exc}")

    def _build_headers(self, api_key: str, auth_mode: str | None = None, base_url: str | None = None) -> dict[str, str]:
        mode = auth_mode or self.auth_mode
        b_url = base_url or self.base_url
        headers = {
            "Accept": "application/json",
            "User-Agent": "SiperLig-DataPipeline/1.0",
        }
        if mode == "bearer":
            headers["Authorization"] = f"Bearer {api_key}"
        elif mode == "x-api-key":
            headers["x-api-key"] = api_key
        else:
            headers["x-rapidapi-key"] = api_key
            if self.rapidapi_host:
                headers["x-rapidapi-host"] = self.rapidapi_host
            elif "rapidapi.com" in b_url:
                headers["x-rapidapi-host"] = urllib.parse.urlparse(b_url).netloc
        return headers

    def _candidate_profiles(self) -> list[tuple[str, str]]:
        """İlk doğrulamada çalışan (base_url, auth_mode) çiftini bulmak için aday listesi döner."""
        base_candidates = [self.base_url]
        for alt in ("https://sports.highlightly.net/football", "https://soccer.highlightly.net"):
            if alt not in base_candidates:
                base_candidates.append(alt)

        mode_candidates = [self.auth_mode]
        for m in ("x-rapidapi-key", "bearer", "x-api-key"):
            if m not in mode_candidates:
                mode_candidates.append(m)

        profiles: list[tuple[str, str]] = []
        for b in base_candidates:
            for m in mode_candidates:
                profiles.append((b, m))
        return profiles

    def _cache_path(self, cache_group: str, cache_name: str, params: dict[str, Any] | None) -> Path:
        safe_name = re.sub(r"[^a-zA-Z0-9._-]", "_", cache_name)
        if params:
            encoded = urllib.parse.urlencode(sorted((k, str(v)) for k, v in params.items() if v is not None))
            if encoded:
                short_hash = hashlib.md5(encoded.encode("utf-8")).hexdigest()[:8]
                safe_name = f"{safe_name}_{short_hash}"
        return BRONZE_DIR / cache_group / f"{safe_name}.json"

    def get(
        self,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
        cache_group: str = "misc",
        cache_name: str = "response",
        force_refresh: bool = False,
    ) -> dict[str, Any] | list[Any] | None:
        """Önce Bronze disk önbelleğini ve Turso bulut arşivini kontrol eder; değişmez (immutable) ise asla tekrar API'ye gitmez."""
        cache_file = self._cache_path(cache_group, cache_name, params)
        rel = cache_file.relative_to(BRONZE_DIR).as_posix()
        if cache_file.exists():
            entry_meta = self._manifest.get("files", {}).get(rel, {})
            is_immutable = bool(entry_meta.get("immutable", False))
            if is_immutable or not force_refresh:
                self.cache_hits_this_run += 1
                return json.loads(cache_file.read_text(encoding="utf-8"))

        if self.turso.enabled:
            try:
                remote = self.turso.get_bronze(rel)
                if remote is not None:
                    remote_payload, remote_immutable = remote
                    if remote_immutable or not force_refresh:
                        formatted_remote = json.dumps(remote_payload, indent=2, ensure_ascii=False)
                        self._atomic_write_text(cache_file, formatted_remote)
                        self._record_manifest_entry(cache_file, cache_group, cache_name, formatted_remote, remote_payload)
                        self.cache_hits_this_run += 1
                        return remote_payload
            except Exception as exc:
                print(f"[Turso Okuma Uyarısı] {exc}")

        if self.requests_made_this_run >= self.run_budget:
            self.budget_stopped = True
            return None

        if not self.keys:
            raise RuntimeError(
                "backend/.env içinde kayıtlı geçerli HIGHLIGHTLY_API_KEY bulunamadı. "
                "Lütfen anahtarlarınızı backend/.env dosyasına ekleyin."
            )

        clean_ep = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        query = ""
        if params:
            filtered = {k: v for k, v in params.items() if v is not None and v != ""}
            if filtered:
                query = "?" + urllib.parse.urlencode(filtered)

        # Key rotation loop
        while True:
            picked = self._pick_next_key()
            if picked is None:
                raise RuntimeError(
                    "Tüm kayıtlı API anahtarlarının günlük güvenli kotası doldu. "
                    "Yarın tekrar çalıştırabilir veya yeni bir anahtar ekleyebilirsiniz."
                )

            idx, api_key, fp = picked
            profiles = (
                [(self.base_url, self.auth_mode)]
                if getattr(self, "_profile_verified", False)
                else self._candidate_profiles()
            )

            auth_rejected_all = False
            last_err_body = ""
            rotate_key = False

            for cand_base, cand_mode in profiles:
                url = f"{cand_base}{clean_ep}{query}"
                req = urllib.request.Request(
                    url,
                    headers=self._build_headers(api_key, auth_mode=cand_mode, base_url=cand_base),
                    method="GET",
                )
                try:
                    with urllib.request.urlopen(req, timeout=25) as resp:
                        raw = resp.read().decode("utf-8")
                        payload = json.loads(raw)
                        self.base_url = cand_base
                        self.auth_mode = cand_mode
                        self._profile_verified = True
                        self._increment_key_usage(fp, mark_exhausted=False)
                        self.requests_made_this_run += 1
                        formatted_text = json.dumps(payload, indent=2, ensure_ascii=False)
                        self._atomic_write_text(cache_file, formatted_text)
                        self._record_manifest_entry(cache_file, cache_group, cache_name, formatted_text, payload)
                        if self.turso.enabled:
                            try:
                                meta_imm = bool(self._manifest.get("files", {}).get(rel, {}).get("immutable", False))
                                raw_b = formatted_text.encode("utf-8")
                                self.turso.upsert_bronze(
                                    cache_key=rel,
                                    cache_group=cache_group,
                                    sha256=hashlib.sha256(raw_b).hexdigest(),
                                    byte_size=len(raw_b),
                                    immutable=meta_imm,
                                    payload_text=formatted_text,
                                )
                            except Exception as exc:
                                print(f"[Turso Yazma Uyarısı] {exc}")
                        time.sleep(0.35)
                        return payload
                except urllib.error.HTTPError as err:
                    err_body = err.read().decode("utf-8", errors="ignore")
                    last_err_body = err_body
                    if err.code == 429:
                        print(f"[Kota] Anahtar #{idx} ({fp}) 429 sınırına ulaştı, sıradaki anahtara geçiliyor...")
                        self._increment_key_usage(fp, mark_exhausted=True)
                        rotate_key = True
                        break
                    if err.code in (401, 403):
                        auth_rejected_all = True
                        continue
                    if err.code in (400, 422):
                        print(f"[Parametre {err.code}] {cand_base}{clean_ep}{query} -> {err_body[:180]}")
                        self.base_url = cand_base
                        self.auth_mode = cand_mode
                        self._profile_verified = True
                        self._increment_key_usage(fp, mark_exhausted=False)
                        self.requests_made_this_run += 1
                        return None
                    if err.code == 404:
                        print(f"[404] Veri bulunamadı: {cand_base}{clean_ep}{query}")
                        self.base_url = cand_base
                        self.auth_mode = cand_mode
                        self._profile_verified = True
                        self._increment_key_usage(fp, mark_exhausted=False)
                        self.requests_made_this_run += 1
                        return None
                    raise RuntimeError(f"Highlightly HTTP {err.code}: {err_body[:300]}") from err

            if rotate_key:
                continue
            if auth_rejected_all:
                print(
                    f"[Yetki Hatası 401/403] Anahtar #{idx} ({fp}) tüm doğrulama modlarında reddedildi. "
                    f"Yanıt: {last_err_body[:160]}"
                )
                self._increment_key_usage(fp, mark_exhausted=True)
                continue
