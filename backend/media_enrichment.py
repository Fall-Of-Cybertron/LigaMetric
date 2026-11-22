"""Highlightly dışı açık medya zenginleştirme modülü (sıfır Highlightly kotası harcar).

1. Türkiye'de (TR) erişilemeyen coğrafi engelli YouTube özetlerini tespit eder;
   beIN SPORTS Türkiye vb. açık özetleri bularak maç bazlı çoklu klip listesi üretir.
2. Wikipedia / Wikimedia REST API üzerinden kadrodaki gerçek oyuncular için
   profil fotoğrafı URL'lerini (thumbnail) çözer ve `bronze/media/media_cache.json` +
   Turso `bronze_archive` üzerinde önbelleğe alır.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from highlightly_client import BRONZE_DIR
from turso_client import TursoClient

BACKEND_DIR = Path(__file__).resolve().parent


def _atomic_write_text(target: Path, text: str) -> None:
    """Windows dosya kilidi dostu atomik yazma yardımcısı."""
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(f"{target.name}.{os.getpid()}.tmp")
    tmp.write_text(text, encoding="utf-8")
    for attempt in range(4):
        try:
            os.replace(tmp, target)
            return
        except PermissionError:
            if attempt == 3:
                try:
                    tmp.unlink(missing_ok=True)
                except OSError:
                    pass
                target.write_text(text, encoding="utf-8")
                return
            time.sleep(0.08 * (attempt + 1))
ROOT_DIR = BACKEND_DIR.parent
GOLD_DIR = ROOT_DIR / "web" / "src" / "data"
MEDIA_DIR = BRONZE_DIR / "media"
MEDIA_CACHE_PATH = MEDIA_DIR / "media_cache.json"
TURSO_MEDIA_KEY = "media/media_cache.json"

BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)
WIKI_UA = "SiperLig/1.0 (https://siperlig.local; educational football analytics)"

FOOTBALL_KEYWORDS = (
    "football",
    "soccer",
    "futbol",
    "goalkeeper",
    "kaleci",
    "midfielder",
    "orta saha",
    "forward",
    "striker",
    "winger",
    "forvet",
    "defender",
    "centre-back",
    "full-back",
    "defans",
    "süper lig",
    "super lig",
    "millî futbolcu",
    "national team",
)

BAD_VIDEO_TERMS = (
    "fc 26",
    "fc 25",
    "fc26",
    "fc25",
    "fifa",
    "efootball",
    "pes 20",
    "canli",
    "live stream",
    "simulasyon",
    "tahmin",
    "iddaa",
    "yorum",
    "tepkisi",
    "basin toplantisi",
    "mac sonucu",
    "radyo",
    "shorts",
)

CLUB_SEARCH_TOKENS: dict[str, list[str]] = {
    "galatasaray": ["galatasaray"],
    "fenerbahce": ["fenerbahce"],
    "besiktas": ["besiktas"],
    "trabzonspor": ["trabzonspor"],
    "basaksehir": ["basaksehir"],
    "samsunspor": ["samsunspor"],
    "goztepe": ["goztepe"],
    "eyupspor": ["eyupspor"],
    "rizespor": ["rizespor"],
    "konyaspor": ["konyaspor"],
    "kasimpasa": ["kasimpasa"],
    "antalyaspor": ["antalyaspor"],
    "alanyaspor": ["alanyaspor"],
    "gaziantep-fk": ["gaziantep"],
    "kayserispor": ["kayserispor"],
    "kocaelispor": ["kocaelispor"],
    "genclerbirligi": ["genclerbirligi"],
    "corumspor": ["corum"],
    "fatih-karagumruk": ["karagumruk"],
    "karagumruk": ["karagumruk"],
    "bodrum-fk": ["bodrum"],
    "sivasspor": ["sivasspor"],
    "hatayspor": ["hatayspor"],
    "amed": ["amed"],
    "erzurumspor": ["erzurum"],
}

TR_TRANS = str.maketrans("çğıİöşüÇĞÖŞÜ", "cgiiosuCGOSU")


def _norm_ascii(text: str) -> str:
    low = text.translate(TR_TRANS).lower()
    low = re.sub(r"[^a-z0-9\s]", " ", low)
    return re.sub(r"\s+", " ", low).strip()


def _unwrap_data(payload: Any) -> list[Any]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        d = payload.get("data")
        if isinstance(d, list):
            return d
        if isinstance(d, dict):
            return [d]
        return [payload]
    return []


def _http_get_text(
    url: str, headers: dict[str, str], timeout: int = 8, retries: int = 2
) -> tuple[int, str]:
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status, resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as err:
            if err.code in (429, 503) and attempt < retries:
                time.sleep(1.5 * (attempt + 1))
                continue
            return err.code, ""
        except (urllib.error.URLError, TimeoutError, OSError):
            if attempt < retries:
                time.sleep(0.5 * (attempt + 1))
                continue
            return 0, ""
    return 0, ""


def load_media_cache() -> dict[str, Any]:
    """Yerel veya Turso Bronze arşivinden medya önbelleğini yükler."""
    default_doc: dict[str, Any] = {
        "updatedAt": "",
        "yt_tr_checks": {},
        "match_highlights": {},
        "player_photos": {},
    }
    if MEDIA_CACHE_PATH.exists():
        try:
            loaded = json.loads(MEDIA_CACHE_PATH.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                for k, v in default_doc.items():
                    loaded.setdefault(k, v)
                return loaded
        except (OSError, json.JSONDecodeError):
            pass

    turso = TursoClient()
    if turso.enabled:
        try:
            res = turso.get_bronze(TURSO_MEDIA_KEY)
            if res and isinstance(res[0], dict):
                loaded = res[0]
                for k, v in default_doc.items():
                    loaded.setdefault(k, v)
                MEDIA_DIR.mkdir(parents=True, exist_ok=True)
                _atomic_write_text(
                    MEDIA_CACHE_PATH, json.dumps(loaded, indent=2, ensure_ascii=False)
                )
                return loaded
        except Exception as err:
            print(f"[MediaEnrich] Turso medya cache okuma hatası: {err}")

    return default_doc


def save_media_cache(cache: dict[str, Any]) -> None:
    """Medya önbelleğini hem diske hem Turso bronze_archive tablosuna yazar."""
    tsi_now = datetime.now(timezone(timedelta(hours=3))).isoformat()
    cache["updatedAt"] = tsi_now
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    payload_text = json.dumps(cache, indent=2, ensure_ascii=False)
    _atomic_write_text(MEDIA_CACHE_PATH, payload_text)

    turso = TursoClient()
    if turso.enabled:
        try:
            sha = hashlib.sha256(payload_text.encode("utf-8")).hexdigest()
            turso.upsert_bronze(
                cache_key=TURSO_MEDIA_KEY,
                cache_group="media",
                sha256=sha,
                byte_size=len(payload_text.encode("utf-8")),
                immutable=False,
                payload_text=payload_text,
                archived_at=tsi_now,
            )
        except Exception as err:
            print(f"[MediaEnrich] Turso medya cache yazma uyarısı: {err}")


def extract_youtube_id(url: str) -> str | None:
    """Embed, watch veya youtu.be URL'sinden 11 karakterlik YouTube ID çıkarır."""
    if not url:
        return None
    for pattern in (
        r"youtube\.com/embed/([a-zA-Z0-9_-]{11})",
        r"youtube-nocookie\.com/embed/([a-zA-Z0-9_-]{11})",
        r"[?&]v=([a-zA-Z0-9_-]{11})",
        r"youtu\.be/([a-zA-Z0-9_-]{11})",
    ):
        m = re.search(pattern, url)
        if m:
            return m.group(1)
    return None


def is_youtube_playable_in_tr(
    video_id: str, cache: dict[str, Any], lock: threading.Lock
) -> bool:
    """YouTube sayfasındaki availableCountries bilgisinden videonun TR'de açık olup olmadığını doğrular."""
    with lock:
        cached = cache["yt_tr_checks"].get(video_id)
    if isinstance(cached, bool):
        return cached

    status, html = _http_get_text(
        f"https://www.youtube.com/watch?v={video_id}&hl=tr&gl=TR",
        headers={"User-Agent": BROWSER_UA, "Accept-Language": "tr-TR,tr;q=0.9"},
        timeout=9,
    )
    if status != 200 or not html:
        return False

    playable = True
    lower_html = html.lower()
    if (
        "not available in your country" in lower_html
        or "ülkenizde kullanılamıyor" in lower_html
        or "videoyu ülkenizde oynatılamıyor" in lower_html
    ):
        playable = False
    else:
        m_countries = re.search(r'"availableCountries":\[([^\]]+)\]', html)
        if m_countries:
            playable = '"TR"' in m_countries.group(1)
        elif '"status":"UNPLAYABLE"' in html or '"status":"LOGIN_REQUIRED"' in html:
            playable = False

    with lock:
        cache["yt_tr_checks"][video_id] = playable
    return playable


def _iter_video_renderers(node: Any):
    if isinstance(node, dict):
        if "videoRenderer" in node and isinstance(node["videoRenderer"], dict):
            yield node["videoRenderer"]
        for val in node.values():
            if isinstance(val, (dict, list)):
                yield from _iter_video_renderers(val)
    elif isinstance(node, list):
        for item in node:
            if isinstance(item, (dict, list)):
                yield from _iter_video_renderers(item)


def _club_tokens(club_id: str, club_name: str) -> list[str]:
    if club_id in CLUB_SEARCH_TOKENS:
        return CLUB_SEARCH_TOKENS[club_id]
    words = [w for w in _norm_ascii(club_name).split() if w not in ("fk", "sk", "jk", "a", "s", "spor", "kulubu")]
    return words[:1] if words else [_norm_ascii(club_name)]


def _search_youtube_tr_highlight(
    home_id: str,
    home_name: str,
    away_id: str,
    away_name: str,
    round_num: int,
    cache: dict[str, Any],
    lock: threading.Lock,
) -> tuple[str, str, str] | None:
    """YouTube aramasıyla TR'de açık resmi beIN SPORTS Türkiye maç özetini bulur."""
    h_tokens = _club_tokens(home_id, home_name)
    a_tokens = _club_tokens(away_id, away_name)
    queries = [
        f"beIN SPORTS Türkiye {home_name} {away_name} {round_num}. hafta maç özeti 2026/27",
        f"{home_name} {away_name} {round_num}. hafta maç özeti Süper Lig",
    ]
    seen_vids: set[str] = set()
    candidates: list[tuple[int, str, str, str]] = []

    for query in queries:
        q_enc = urllib.parse.quote_plus(query)
        status, html = _http_get_text(
            f"https://www.youtube.com/results?search_query={q_enc}&hl=tr&gl=TR",
            headers={"User-Agent": BROWSER_UA, "Accept-Language": "tr-TR,tr;q=0.9"},
            timeout=9,
        )
        if status != 200 or not html:
            continue

        m_data = re.search(r"var ytInitialData\s*=\s*(\{.*?\});\s*</script>", html, re.S)
        if not m_data:
            m_data = re.search(r"ytInitialData\s*=\s*(\{.*?\});\s*", html, re.S)
        if not m_data:
            continue
        try:
            data = json.loads(m_data.group(1))
        except json.JSONDecodeError:
            continue

        for vr in _iter_video_renderers(data):
            vid = str(vr.get("videoId") or "")
            if len(vid) != 11 or vid in seen_vids:
                continue
            seen_vids.add(vid)

            title_runs = ((vr.get("title") or {}).get("runs") or [])
            title_raw = "".join(str(r.get("text") or "") for r in title_runs).strip()
            owner_runs = (
                ((vr.get("ownerText") or {}).get("runs"))
                or ((vr.get("longBylineText") or {}).get("runs"))
                or []
            )
            channel_raw = "".join(str(r.get("text") or "") for r in owner_runs).strip()

            t_norm = _norm_ascii(title_raw)
            c_norm = _norm_ascii(channel_raw)

            if any(bad in t_norm for bad in BAD_VIDEO_TERMS):
                continue
            if not (any(ht in t_norm for ht in h_tokens) and any(at in t_norm for at in a_tokens)):
                continue

            # Özet videosu sinyalleri kontrolü
            has_summary_cue = any(k in t_norm for k in ("ozet", "ozeti", "highlights"))
            if not has_summary_cue:
                continue

            score = 0
            if "bein" in c_norm:
                score += 60
            elif "trt" in c_norm or "super lig" in c_norm:
                score += 20
            if f"{round_num} hafta" in t_norm or f"{round_num}. hafta" in title_raw.lower():
                score += 25
            if "2026" in t_norm or "26 27" in t_norm or "2026 27" in t_norm:
                score += 15
            if "genis" in t_norm:
                score += 5
            if "mac ozeti" in t_norm:
                score += 10
            # Rakip sırası ev sahibi - deplasman uyuşuyorsa ek puan
            h_pos = min((t_norm.find(ht) for ht in h_tokens if ht in t_norm), default=999)
            a_pos = min((t_norm.find(at) for at in a_tokens if at in t_norm), default=999)
            if h_pos < a_pos:
                score += 10

            candidates.append((score, vid, title_raw, channel_raw))

        if any(sc >= 75 for sc, *_ in candidates):
            break

    candidates.sort(key=lambda x: x[0], reverse=True)
    for score, vid, title_raw, channel_raw in candidates[:5]:
        if is_youtube_playable_in_tr(vid, cache, lock):
            return vid, title_raw, channel_raw
    return None


def resolve_tr_open_highlights(
    cache: dict[str, Any],
    matches_gold: list[dict[str, Any]],
    force_recheck_blocked: bool = False,
    max_matches: int | None = None,
    max_workers: int = 6,
) -> dict[str, int]:
    """Maç özetlerinin Türkiye erişilebilirliğini doğrular; engelli/eksik olanları çözer."""
    from sync_highlightly import normalize_name, resolve_club_id

    # Mevcut kulüp sözlüğü oluştur (Gold clubs.json üzerinden)
    clubs_path = GOLD_DIR / "clubs.json"
    clubs_by_norm: dict[str, str] = {}
    if clubs_path.exists():
        for c in json.loads(clubs_path.read_text(encoding="utf-8")):
            clubs_by_norm[normalize_name(c["name"])] = c["id"]

    hl_clips_by_pair: dict[tuple[str, str], list[dict[str, str]]] = {}
    highlights_dir = BRONZE_DIR / "highlights"
    if highlights_dir.exists():
        for fpath in sorted(highlights_dir.glob("*.json")):
            raw = json.loads(fpath.read_text(encoding="utf-8"))
            for hl in _unwrap_data(raw):
                if not isinstance(hl, dict):
                    continue
                embed = str(hl.get("embedUrl") or hl.get("url") or "").strip()
                if not embed:
                    continue
                match_obj = hl.get("match") if isinstance(hl.get("match"), dict) else {}
                h_id = resolve_club_id(str((match_obj.get("homeTeam") or {}).get("name") or ""), clubs_by_norm)
                a_id = resolve_club_id(str((match_obj.get("awayTeam") or {}).get("name") or ""), clubs_by_norm)
                if not (h_id and a_id):
                    continue
                clip_cat = str(hl.get("category") or "match-highlights")
                clip_title = str(hl.get("title") or ("Maç Özeti" if clip_cat == "match-highlights" else "Gol Klibi"))
                clip_img = str(hl.get("imgUrl") or "")
                bucket = hl_clips_by_pair.setdefault((h_id, a_id), [])
                if not any(existing["embedUrl"] == embed for existing in bucket):
                    bucket.append(
                        {
                            "title": clip_title,
                            "embedUrl": embed,
                            "imgUrl": clip_img,
                            "category": clip_cat,
                        }
                    )

    lock = threading.Lock()
    sorted_matches = sorted(
        matches_gold,
        key=lambda m: (int(m.get("round") or 0), str(m.get("date") or "")),
        reverse=True,
    )
    if max_matches:
        sorted_matches = sorted_matches[:max_matches]

    stats = {"checked": 0, "resolved": 0, "already_cached": 0, "goal_clips": 0, "blocked_replaced": 0}

    def process_match(m: dict[str, Any]) -> None:
        mid = m["id"]
        with lock:
            existing = cache["match_highlights"].get(mid)
            if (
                existing
                and isinstance(existing, dict)
                and existing.get("embedUrl")
                and "jfKfPfyJRdk" not in existing["embedUrl"]
                and not force_recheck_blocked
            ):
                stats["already_cached"] += 1
                return

        stats["checked"] += 1
        h_id = m["homeClubId"]
        a_id = m["awayClubId"]
        h_name = m["homeClubName"]
        a_name = m["awayClubName"]
        r_num = int(m.get("round") or 11)

        pair_clips = hl_clips_by_pair.get((h_id, a_id), [])
        tr_open_summaries: list[dict[str, str]] = []
        tr_open_goals: list[dict[str, str]] = []
        had_blocked_hl = False

        for clip in pair_clips:
            vid = extract_youtube_id(clip["embedUrl"])
            is_open = is_youtube_playable_in_tr(vid, cache, lock) if vid else True
            if not is_open:
                had_blocked_hl = True
                continue
            item = {
                "title": clip["title"],
                "embedUrl": clip["embedUrl"],
                "category": clip["category"],
            }
            if clip["category"] == "match-highlights":
                tr_open_summaries.append(item)
            else:
                tr_open_goals.append(item)

        # Mevcut embedUrl cache dışı ama TR açıksa kontrol et
        if not tr_open_summaries and m.get("highlightEmbedUrl") and "jfKfPfyJRdk" not in m["highlightEmbedUrl"]:
            cur_vid = extract_youtube_id(m["highlightEmbedUrl"])
            if cur_vid and is_youtube_playable_in_tr(cur_vid, cache, lock):
                tr_open_summaries.append(
                    {
                        "title": "Maç Özeti",
                        "embedUrl": f"https://www.youtube.com/embed/{cur_vid}",
                        "category": "match-highlights",
                    }
                )
            elif cur_vid:
                had_blocked_hl = True

        # TR'de açık ana özet yoksa beIN SPORTS Türkiye YouTube araması yap
        if not tr_open_summaries:
            yt_found = _search_youtube_tr_highlight(h_id, h_name, a_id, a_name, r_num, cache, lock)
            if yt_found:
                vid, yt_title, yt_channel = yt_found
                label = "beIN SPORTS Maç Özeti" if "bein" in _norm_ascii(yt_channel) else yt_title[:60]
                tr_open_summaries.append(
                    {
                        "title": label,
                        "embedUrl": f"https://www.youtube.com/embed/{vid}",
                        "category": "match-highlights",
                    }
                )
                if had_blocked_hl:
                    with lock:
                        stats["blocked_replaced"] += 1

        all_clips: list[dict[str, str]] = []
        seen_urls: set[str] = set()
        for c_item in tr_open_summaries + tr_open_goals:
            if c_item["embedUrl"] not in seen_urls:
                seen_urls.add(c_item["embedUrl"])
                all_clips.append(c_item)

        if all_clips:
            main_embed = all_clips[0]["embedUrl"]
            main_vid = extract_youtube_id(main_embed)
            main_img = (
                f"https://i.ytimg.com/vi/{main_vid}/hqdefault.jpg"
                if main_vid
                else (m.get("highlightImgUrl") or "")
            )
            with lock:
                cache["match_highlights"][mid] = {
                    "embedUrl": main_embed,
                    "imgUrl": main_img,
                    "clips": all_clips,
                }
                stats["resolved"] += 1
                stats["goal_clips"] += len(tr_open_goals)

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [pool.submit(process_match, m) for m in sorted_matches]
        for fut in as_completed(futures):
            fut.result()

    return stats


def _is_abbreviated_name(full_name: str) -> bool:
    return bool(re.match(r"^[A-ZÇĞİÖŞÜ]\.\s", full_name.strip()))


def _is_football_summary(summary_json: dict[str, Any]) -> bool:
    if summary_json.get("type") == "disambiguation":
        return False
    blob = (
        str(summary_json.get("description") or "")
        + " "
        + str(summary_json.get("extract") or "")
    ).lower()
    return any(kw in blob for kw in FOOTBALL_KEYWORDS)


_WIKI_RATE_LOCK = threading.Lock()
_LAST_WIKI_CALL = 0.0


def _pace_wiki_call(min_interval: float = 0.09) -> None:
    global _LAST_WIKI_CALL
    with _WIKI_RATE_LOCK:
        now = time.monotonic()
        wait = min_interval - (now - _LAST_WIKI_CALL)
        if wait > 0:
            time.sleep(wait)
        _LAST_WIKI_CALL = time.monotonic()


def _query_wiki_summary_status(lang: str, title: str) -> tuple[int, dict[str, Any] | None]:
    _pace_wiki_call()
    enc = urllib.parse.quote(title.strip().replace(" ", "_"), safe="")
    url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{enc}"
    status, body = _http_get_text(
        url, headers={"User-Agent": WIKI_UA, "Accept": "application/json"}, timeout=6
    )
    if status != 200 or not body:
        return status, None
    try:
        return status, json.loads(body)
    except json.JSONDecodeError:
        return status, None


def _query_wiki_summary(lang: str, title: str) -> dict[str, Any] | None:
    _, data = _query_wiki_summary_status(lang, title)
    return data


def _search_wiki_title_status(lang: str, full_name: str, suffix: str) -> tuple[int, str | None]:
    _pace_wiki_call()
    q = urllib.parse.quote_plus(f"{full_name} {suffix}")
    url = (
        f"https://{lang}.wikipedia.org/w/api.php"
        f"?action=query&list=search&srsearch={q}&format=json&srlimit=3"
    )
    status, body = _http_get_text(
        url, headers={"User-Agent": WIKI_UA, "Accept": "application/json"}, timeout=6
    )
    if status != 200 or not body:
        return status, None
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return status, None
    name_parts = [p for p in _norm_ascii(full_name).split() if len(p) >= 2]
    if not name_parts:
        return status, None
    last_name = name_parts[-1]
    for hit in (data.get("query") or {}).get("search") or []:
        title = str(hit.get("title") or "")
        t_norm = _norm_ascii(title)
        if last_name in t_norm and all(p[:3] in t_norm for p in name_parts):
            return status, title
    return status, None


def _fetch_wikipedia_photo_with_status(full_name: str) -> tuple[str | None, bool]:
    """(photo_url_or_None, had_transient_error) döndürür; geçici hatalarda None önbelleğe alınmaz."""
    clean_name = re.sub(r"\s+", " ", full_name.strip())
    if not clean_name or _is_abbreviated_name(clean_name):
        return None, False

    transient_err = False
    for lang in ("en", "tr"):
        st, summary = _query_wiki_summary_status(lang, clean_name)
        if st in (0, 429, 503):
            transient_err = True
        if summary and _is_football_summary(summary):
            thumb = (summary.get("thumbnail") or {}).get("source")
            if thumb:
                return str(thumb), False

    for lang, suffix in (("en", "footballer"), ("tr", "futbolcu")):
        st_s, matched_title = _search_wiki_title_status(lang, clean_name, suffix)
        if st_s in (0, 429, 503):
            transient_err = True
        if not matched_title:
            continue
        st_q, summary = _query_wiki_summary_status(lang, matched_title)
        if st_q in (0, 429, 503):
            transient_err = True
        if summary and _is_football_summary(summary):
            thumb = (summary.get("thumbnail") or {}).get("source")
            if thumb:
                return str(thumb), False

    return None, transient_err


def fetch_wikipedia_player_photo(full_name: str) -> str | None:
    """İngilizce veya Türkçe Wikipedia özetinden doğrulanmış futbolcu fotoğrafı URL'si döndürür."""
    photo, _ = _fetch_wikipedia_photo_with_status(full_name)
    return photo


def resolve_player_photos(
    cache: dict[str, Any],
    players_gold: list[dict[str, Any]],
    retry_missing: bool = False,
    max_players: int | None = None,
    max_workers: int = 3,
) -> dict[str, int]:
    """Kadro oyuncularının fotoğraflarını Wikipedia REST API ile çözer ve önbelleğe yazar."""
    lock = threading.Lock()
    prioritized = sorted(
        players_gold,
        key=lambda p: (
            not _is_abbreviated_name(str(p.get("fullName") or p.get("name") or "")),
            int(p.get("gamesPlayed") or 0),
            int(p.get("currentMarketValueEur") or 0),
        ),
        reverse=True,
    )
    if max_players:
        prioritized = prioritized[:max_players]

    stats = {"checked": 0, "found": 0, "skipped_abbreviated": 0, "cached": 0, "transient_errors": 0}

    def process_player(p: dict[str, Any]) -> None:
        pid = str(p["id"])
        full_name = str(p.get("fullName") or p.get("name") or "").strip()
        if _is_abbreviated_name(full_name):
            with lock:
                stats["skipped_abbreviated"] += 1
            return

        with lock:
            existing_val = cache["player_photos"].get(pid)
            if isinstance(existing_val, str) and existing_val.startswith("http"):
                stats["cached"] += 1
                return
            if pid in cache["player_photos"] and not retry_missing:
                stats["cached"] += 1
                return

        photo, had_transient = _fetch_wikipedia_photo_with_status(full_name)
        with lock:
            if photo or not had_transient:
                cache["player_photos"][pid] = photo
            stats["checked"] += 1
            if had_transient:
                stats["transient_errors"] += 1
            if photo:
                stats["found"] += 1

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [pool.submit(process_player, p) for p in prioritized]
        for fut in as_completed(futures):
            fut.result()

    return stats


def run_enrichment(
    skip_highlights: bool = False,
    skip_photos: bool = False,
    retry_missing_photos: bool = False,
    force_recheck_blocked: bool = False,
    max_matches: int | None = None,
    max_players: int | None = None,
) -> dict[str, Any]:
    """Highlightly dışı tüm medya zenginleştirme adımlarını çalıştırır ve cache'i kaydeder."""
    cache = load_media_cache()
    result: dict[str, Any] = {}

    if not skip_highlights:
        matches_path = GOLD_DIR / "matches.json"
        matches_gold = json.loads(matches_path.read_text(encoding="utf-8")) if matches_path.exists() else []
        hl_stats = resolve_tr_open_highlights(
            cache,
            matches_gold,
            force_recheck_blocked=force_recheck_blocked,
            max_matches=max_matches,
        )
        result["highlights"] = hl_stats
        print(f"[MediaEnrich] TR Maç Özetleri: {hl_stats}")

    if not skip_photos:
        players_path = GOLD_DIR / "players.json"
        players_gold = json.loads(players_path.read_text(encoding="utf-8")) if players_path.exists() else []
        photo_stats = resolve_player_photos(
            cache,
            players_gold,
            retry_missing=retry_missing_photos,
            max_players=max_players,
        )
        result["photos"] = photo_stats
        print(f"[MediaEnrich] Oyuncu Fotoğrafları (Wikipedia): {photo_stats}")

    save_media_cache(cache)
    total_hl = len(cache["match_highlights"])
    total_photos = sum(1 for v in cache["player_photos"].values() if v)
    print(f"[MediaEnrich] Toplam Cache -> {total_hl} TR-açık maç özeti, {total_photos} oyuncu fotoğrafı.")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="SiperLig Medya Zenginleştirme (TR Özet + Oyuncu Fotoğrafı)")
    parser.add_argument("--skip-highlights", action="store_true", help="YouTube TR özet kontrolünü atla")
    parser.add_argument("--skip-photos", action="store_true", help="Wikipedia oyuncu fotoğrafı taramasını atla")
    parser.add_argument("--retry-missing-photos", action="store_true", help="Daha önce None kaydedilen oyuncuları yeniden dene")
    parser.add_argument("--force-recheck-blocked", action="store_true", help="Önbellekteki özetleri TR erişimi için yeniden doğrula")
    parser.add_argument("--max-matches", type=int, default=None, help="En fazla kaç maç kontrol edilsin")
    parser.add_argument("--max-players", type=int, default=None, help="En fazla kaç oyuncu kontrol edilsin")
    args = parser.parse_args()

    t0 = time.time()
    run_enrichment(
        skip_highlights=args.skip_highlights,
        skip_photos=args.skip_photos,
        retry_missing_photos=args.retry_missing_photos,
        force_recheck_blocked=args.force_recheck_blocked,
        max_matches=args.max_matches,
        max_players=args.max_players,
    )
    print(f"[MediaEnrich] Tamamlandı ({time.time() - t0:.1f}s).")


if __name__ == "__main__":
    main()
