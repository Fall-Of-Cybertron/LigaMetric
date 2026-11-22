"""Turso (libSQL) HTTP v2 Pipeline API istemcisi ve Bronze/Gold göç (migration) aracı."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


BACKEND_DIR = Path(__file__).resolve().parent
ROOT_DIR = BACKEND_DIR.parent
DATA_DIR = BACKEND_DIR / "data"
BRONZE_DIR = DATA_DIR / "bronze"
MANIFEST_FILE = BRONZE_DIR / "manifest.json"
QUOTA_FILE = DATA_DIR / "quota_state.json"
GOLD_DIR = ROOT_DIR / "web" / "src" / "data"
DEFAULT_ENV_PATH = BACKEND_DIR / ".env"

PLACEHOLDER_PREFIXES = ("buraya_", "your_", "example_", "<")


def _load_env(env_path: Path = DEFAULT_ENV_PATH) -> None:
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if k not in os.environ or not os.environ[k]:
            os.environ[k] = v


def _is_configured_val(val: str) -> bool:
    v = val.strip()
    return bool(v) and not any(v.lower().startswith(p) for p in PLACEHOLDER_PREFIXES)


def _encode_arg(val: Any) -> dict[str, Any]:
    if val is None:
        return {"type": "null"}
    if isinstance(val, bool):
        return {"type": "integer", "value": "1" if val else "0"}
    if isinstance(val, int):
        return {"type": "integer", "value": str(val)}
    if isinstance(val, float):
        return {"type": "float", "value": val}
    return {"type": "text", "value": str(val)}


def _decode_cell(cell: dict[str, Any]) -> Any:
    ctype = cell.get("type")
    if ctype == "null":
        return None
    val = cell.get("value")
    if ctype == "integer":
        return int(val)
    if ctype == "float":
        return float(val)
    return val


class TursoClient:
    """Harici bağımlılık gerektirmeyen Turso /v2/pipeline HTTP istemcisi."""

    def __init__(self, db_url: str | None = None, auth_token: str | None = None) -> None:
        _load_env()
        raw_url = (db_url or os.environ.get("TURSO_DATABASE_URL", "")).strip()
        raw_token = (auth_token or os.environ.get("TURSO_AUTH_TOKEN", "")).strip()

        self.enabled = _is_configured_val(raw_url) and _is_configured_val(raw_token)
        if raw_url.startswith("libsql://"):
            raw_url = "https://" + raw_url[len("libsql://") :]
        self.base_url = raw_url.rstrip("/")
        self.pipeline_url = f"{self.base_url}/v2/pipeline" if self.base_url else ""
        self.auth_token = raw_token
        self._schema_ready = False

    def execute_batch(self, statements: list[tuple[str, list[Any] | None]]) -> list[list[dict[str, Any]]]:
        if not self.enabled:
            raise RuntimeError("TURSO_DATABASE_URL veya TURSO_AUTH_TOKEN yapılandırılmamış.")

        reqs: list[dict[str, Any]] = []
        for sql, args in statements:
            stmt: dict[str, Any] = {"sql": sql}
            if args:
                stmt["args"] = [_encode_arg(a) for a in args]
            reqs.append({"type": "execute", "stmt": stmt})
        reqs.append({"type": "close"})

        body = json.dumps({"requests": reqs}, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            self.pipeline_url,
            data=body,
            headers={
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json",
                "User-Agent": "SiperLig-TursoClient/1.0",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as err:
            err_text = err.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"Turso HTTP {err.code}: {err_text[:300]}") from err

        parsed_results: list[list[dict[str, Any]]] = []
        for item in data.get("results", []):
            if item.get("type") == "error":
                msg = (item.get("error") or {}).get("message", "Bilinmeyen Turso SQL hatası")
                raise RuntimeError(f"Turso SQL Hatası: {msg}")
            if item.get("type") != "ok":
                continue
            res = (item.get("response") or {}).get("result")
            if not isinstance(res, dict):
                continue
            cols = [c.get("name", f"col_{i}") for i, c in enumerate(res.get("cols") or [])]
            rows_out: list[dict[str, Any]] = []
            for raw_row in res.get("rows") or []:
                row_dict = {
                    cols[i]: _decode_cell(cell)
                    for i, cell in enumerate(raw_row)
                    if i < len(cols)
                }
                rows_out.append(row_dict)
            parsed_results.append(rows_out)
        return parsed_results

    def execute(self, sql: str, args: list[Any] | None = None) -> list[dict[str, Any]]:
        results = self.execute_batch([(sql, args)])
        return results[0] if results else []

    def init_schema(self) -> None:
        if not self.enabled or self._schema_ready:
            return
        self.execute_batch([
            (
                """
                CREATE TABLE IF NOT EXISTS bronze_archive (
                    cache_key TEXT PRIMARY KEY,
                    cache_group TEXT NOT NULL,
                    sha256 TEXT NOT NULL,
                    byte_size INTEGER NOT NULL,
                    immutable INTEGER NOT NULL DEFAULT 0,
                    payload_json TEXT NOT NULL,
                    archived_at TEXT NOT NULL
                )
                """,
                None,
            ),
            (
                """
                CREATE TABLE IF NOT EXISTS quota_ledger (
                    quota_date TEXT NOT NULL,
                    key_fingerprint TEXT NOT NULL,
                    used_count INTEGER NOT NULL DEFAULT 0,
                    exhausted INTEGER NOT NULL DEFAULT 0,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (quota_date, key_fingerprint)
                )
                """,
                None,
            ),
            (
                """
                CREATE TABLE IF NOT EXISTS gold_datasets (
                    dataset_key TEXT PRIMARY KEY,
                    payload_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """,
                None,
            ),
        ])
        self._schema_ready = True

    def get_bronze(self, cache_key: str) -> tuple[Any, bool] | None:
        if not self.enabled:
            return None
        self.init_schema()
        rows = self.execute(
            "SELECT payload_json, immutable FROM bronze_archive WHERE cache_key = ?",
            [cache_key],
        )
        if not rows:
            return None
        row = rows[0]
        return json.loads(row["payload_json"]), bool(row.get("immutable"))

    def upsert_bronze(
        self,
        cache_key: str,
        cache_group: str,
        sha256: str,
        byte_size: int,
        immutable: bool,
        payload_text: str,
        archived_at: str | None = None,
    ) -> None:
        if not self.enabled:
            return
        self.init_schema()
        ts = archived_at or datetime.now(timezone(timedelta(hours=3))).isoformat()
        self.execute(
            """
            INSERT INTO bronze_archive (cache_key, cache_group, sha256, byte_size, immutable, payload_json, archived_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(cache_key) DO UPDATE SET
                cache_group = excluded.cache_group,
                sha256 = excluded.sha256,
                byte_size = excluded.byte_size,
                immutable = MAX(bronze_archive.immutable, excluded.immutable),
                payload_json = excluded.payload_json,
                archived_at = excluded.archived_at
            """,
            [cache_key, cache_group, sha256, byte_size, 1 if immutable else 0, payload_text, ts],
        )

    def load_quota_for_date(self, quota_date: str) -> dict[str, dict[str, Any]]:
        if not self.enabled:
            return {}
        self.init_schema()
        rows = self.execute(
            "SELECT key_fingerprint, used_count, exhausted FROM quota_ledger WHERE quota_date = ?",
            [quota_date],
        )
        return {
            r["key_fingerprint"]: {"used": int(r["used_count"]), "exhausted": bool(r["exhausted"])}
            for r in rows
        }

    def upsert_quota(self, quota_date: str, fingerprint: str, used: int, exhausted: bool) -> None:
        if not self.enabled:
            return
        self.init_schema()
        ts = datetime.now(timezone(timedelta(hours=3))).isoformat()
        self.execute(
            """
            INSERT INTO quota_ledger (quota_date, key_fingerprint, used_count, exhausted, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(quota_date, key_fingerprint) DO UPDATE SET
                used_count = MAX(quota_ledger.used_count, excluded.used_count),
                exhausted = MAX(quota_ledger.exhausted, excluded.exhausted),
                updated_at = excluded.updated_at
            """,
            [quota_date, fingerprint, used, 1 if exhausted else 0, ts],
        )

    def upsert_gold(self, dataset_key: str, payload_text: str) -> None:
        if not self.enabled:
            return
        self.init_schema()
        ts = datetime.now(timezone(timedelta(hours=3))).isoformat()
        self.execute(
            """
            INSERT INTO gold_datasets (dataset_key, payload_json, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(dataset_key) DO UPDATE SET
                payload_json = excluded.payload_json,
                updated_at = excluded.updated_at
            """,
            [dataset_key, payload_text, ts],
        )

    def pull_all_bronze_to_disk(self) -> int:
        if not self.enabled:
            return 0
        self.init_schema()
        keys_rows = self.execute("SELECT cache_key FROM bronze_archive ORDER BY cache_key")
        manifest: dict[str, Any] = {"updatedAt": datetime.now(timezone(timedelta(hours=3))).isoformat(), "files": {}}
        if MANIFEST_FILE.exists():
            try:
                manifest = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass

        pulled = 0
        for kr in keys_rows:
            ckey = kr["cache_key"]
            target = BRONZE_DIR / ckey
            rows = self.execute(
                "SELECT sha256, byte_size, immutable, payload_json, archived_at FROM bronze_archive WHERE cache_key = ?",
                [ckey],
            )
            if not rows:
                continue
            r = rows[0]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(r["payload_json"], encoding="utf-8")
            manifest.setdefault("files", {})[ckey] = {
                "sha256": r["sha256"],
                "bytes": int(r["byte_size"]),
                "immutable": bool(r["immutable"]),
                "archivedAt": r["archived_at"],
            }
            pulled += 1

        MANIFEST_FILE.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST_FILE.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        return pulled

    def pull_all_gold_to_disk(self) -> int:
        if not self.enabled:
            return 0
        self.init_schema()
        rows = self.execute("SELECT dataset_key, payload_json FROM gold_datasets")
        GOLD_DIR.mkdir(parents=True, exist_ok=True)
        count = 0
        for r in rows:
            target = GOLD_DIR / f"{r['dataset_key']}.json"
            target.write_text(r["payload_json"], encoding="utf-8")
            count += 1
        return count


def cmd_status(client: TursoClient) -> None:
    print("=== Turso (libSQL) Veritabanı Durumu ===")
    if not client.enabled:
        print("Durum: PASİF (backend/.env içine TURSO_DATABASE_URL ve TURSO_AUTH_TOKEN girilmedi)")
        print("Bilgi: Turso aktif edilene kadar tüm veriler yerel disk önbelleğinde güvenle tutulur.")
        return

    client.init_schema()
    bronze_stats = client.execute(
        "SELECT COUNT(*) AS cnt, COALESCE(SUM(byte_size), 0) AS total_bytes, COALESCE(SUM(immutable), 0) AS imm_cnt FROM bronze_archive"
    )[0]
    gold_stats = client.execute("SELECT COUNT(*) AS cnt FROM gold_datasets")[0]
    quota_stats = client.execute("SELECT COUNT(*) AS cnt FROM quota_ledger")[0]

    mb = round(int(bronze_stats["total_bytes"]) / (1024 * 1024), 2)
    print(f"Durum           : BAĞLI ({client.base_url})")
    print(f"Bronze Arşiv    : {bronze_stats['cnt']} dosya ({bronze_stats['imm_cnt']} immutable kilitli, {mb} MB)")
    print(f"Gold Tablolar   : {gold_stats['cnt']} veri seti")
    print(f"Kota Kayıtları  : {quota_stats['cnt']} satır")


def cmd_migrate_up(client: TursoClient) -> None:
    if not client.enabled:
        raise RuntimeError("Turso'ya aktarım için önce backend/.env içine TURSO_DATABASE_URL ve TURSO_AUTH_TOKEN ekleyin.")

    client.init_schema()
    manifest_files: dict[str, Any] = {}
    if MANIFEST_FILE.exists():
        manifest_files = json.loads(MANIFEST_FILE.read_text(encoding="utf-8")).get("files", {})

    uploaded_bronze = 0
    for fpath in sorted(BRONZE_DIR.rglob("*.json")):
        if fpath == MANIFEST_FILE:
            continue
        rel = fpath.relative_to(BRONZE_DIR).as_posix()
        text = fpath.read_text(encoding="utf-8")
        raw_bytes = text.encode("utf-8")
        meta = manifest_files.get(rel, {})
        sha = meta.get("sha256") or hashlib.sha256(raw_bytes).hexdigest()
        imm = bool(meta.get("immutable", False))
        archived_at = meta.get("archivedAt")
        client.upsert_bronze(
            cache_key=rel,
            cache_group=fpath.parent.name,
            sha256=sha,
            byte_size=len(raw_bytes),
            immutable=imm,
            payload_text=text,
            archived_at=archived_at,
        )
        uploaded_bronze += 1

    uploaded_quota = 0
    if QUOTA_FILE.exists():
        qdata = json.loads(QUOTA_FILE.read_text(encoding="utf-8"))
        qdate = qdata.get("date", "")
        for fp, entry in (qdata.get("keys") or {}).items():
            client.upsert_quota(qdate, fp, int(entry.get("used", 0)), bool(entry.get("exhausted", False)))
            uploaded_quota += 1

    uploaded_gold = 0
    for gname in ("standings", "clubs", "players", "matches", "sync-status"):
        gpath = GOLD_DIR / f"{gname}.json"
        if gpath.exists():
            client.upsert_gold(gname, gpath.read_text(encoding="utf-8"))
            uploaded_gold += 1

    print(
        f"Turso göçü tamamlandı -> Bronze: {uploaded_bronze} JSON, "
        f"Kota: {uploaded_quota} kayıt, Gold: {uploaded_gold} veri seti."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="SiperLig Turso Veritabanı Yönetimi")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status", help="Turso bağlantı ve tablo durumunu göster")
    sub.add_parser("migrate-up", help="Yerel Bronze ve Gold JSON dosyalarını Turso veritabanına aktar")
    sub.add_parser("pull-bronze", help="Turso bronze_archive kayıtlarını yerel diske indir")
    sub.add_parser("pull-gold", help="Turso gold_datasets kayıtlarını web/src/data içine indir")

    args = parser.parse_args()
    client = TursoClient()

    if args.cmd == "status":
        cmd_status(client)
    elif args.cmd == "migrate-up":
        cmd_migrate_up(client)
    elif args.cmd == "pull-bronze":
        cnt = client.pull_all_bronze_to_disk()
        print(f"Turso -> Yerel Bronze indirildi: {cnt} dosya")
    elif args.cmd == "pull-gold":
        cnt = client.pull_all_gold_to_disk()
        print(f"Turso -> Yerel Gold indirildi: {cnt} dosya")


if __name__ == "__main__":
    main()
