"""Highlightly Football API verilerini kademeli çekip web/src/data Gold JSON dosyalarıyla birleştiren hat."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path
from typing import Any

from highlightly_client import BRONZE_DIR, HighlightlyClient

try:
    from turso_client import TursoClient
except ImportError:
    from backend.turso_client import TursoClient


ROOT_DIR = Path(__file__).resolve().parent.parent
WEB_DIR = ROOT_DIR / "web"
GOLD_DIR = WEB_DIR / "src" / "data"

CLUB_ALIASES: dict[str, str] = {
    "galatasaray": "galatasaray",
    "fenerbahce": "fenerbahce",
    "besiktas": "besiktas",
    "trabzonspor": "trabzonspor",
    "samsunspor": "samsunspor",
    "eyupspor": "eyupspor",
    "goztepe": "goztepe",
    "basaksehir": "basaksehir",
    "istanbul basaksehir": "basaksehir",
    "rams basaksehir": "basaksehir",
    "kasimpasa": "kasimpasa",
    "sivasspor": "sivasspor",
    "konyaspor": "konyaspor",
    "rizespor": "rizespor",
    "caykur rizespor": "rizespor",
    "antalyaspor": "antalyaspor",
    "gaziantep": "gaziantep-fk",
    "gaziantep fk": "gaziantep-fk",
    "gazisehir gaziantep": "gaziantep-fk",
    "alanyaspor": "alanyaspor",
    "kayserispor": "kayserispor",
    "bodrum": "bodrum-fk",
    "bodrum fk": "bodrum-fk",
    "hatayspor": "hatayspor",
    "amed": "amed",
    "amed sk": "amed",
    "kocaelispor": "kocaelispor",
    "kocaelispor fk": "kocaelispor",
    "yeni corumspor": "corumspor",
    "corum fk": "corumspor",
    "erzurum bb": "erzurumspor",
    "erzurumspor fk": "erzurumspor",
    "genclerbirligi": "genclerbirligi",
}

NEW_CLUB_DEFAULTS: dict[str, dict[str, Any]] = {
    "amed": {
        "name": "Amed SK",
        "shortName": "AMD",
        "primaryColor": "#15803D",
        "accentColor": "#DC2626",
        "city": "Diyarbakır",
        "stadium": "Diyarbakır Stadyumu",
        "coach": "Servet Çetin",
        "founded": 1972,
        "playStyle": "Dikine Baskı",
    },
    "kocaelispor": {
        "name": "Kocaelispor FK",
        "shortName": "KOC",
        "primaryColor": "#16A34A",
        "accentColor": "#111827",
        "city": "Kocaeli",
        "stadium": "Yıldız Entegre Kocaeli",
        "coach": "Ertuğrul Sağlam",
        "founded": 1966,
        "playStyle": "Dikine Baskı",
    },
    "corumspor": {
        "name": "Çorum FK",
        "shortName": "ÇOR",
        "primaryColor": "#DC2626",
        "accentColor": "#111827",
        "city": "Çorum",
        "stadium": "Çorum Şehir Stadyumu",
        "coach": "Serkan Özbalta",
        "founded": 1997,
        "playStyle": "Uzun Top / Geçiş",
    },
    "erzurumspor": {
        "name": "Erzurumspor FK",
        "shortName": "ERZ",
        "primaryColor": "#1D4ED8",
        "accentColor": "#FFFFFF",
        "city": "Erzurum",
        "stadium": "Kazım Karabekir",
        "coach": "Hakan Kutlu",
        "founded": 2005,
        "playStyle": "Uzun Top / Geçiş",
    },
    "genclerbirligi": {
        "name": "Gençlerbirliği",
        "shortName": "GB",
        "primaryColor": "#B91C1C",
        "accentColor": "#111827",
        "city": "Ankara",
        "stadium": "Eryaman Stadyumu",
        "coach": "Recep Karatepe",
        "founded": 1923,
        "playStyle": "Kısır Pas",
    },
}

ANATOMY_REGIONS = [
    "head", "shoulder", "chest_ribs", "arm_wrist", "groin",
    "thigh_front", "hamstring", "knee", "calf", "ankle_foot", "back", "other",
]

STAT_META_BY_NAME: dict[str, tuple[str, str, str, str]] = {
    "Possession": ("possession", "Topla Oynama (%)", "Genel & Topla Oynama", "%"),
    "Expected Goals": ("expected_goals", "Gol Beklentisi (xG)", "Hücum & xG", ""),
    "Expected Assists": ("expected_assists", "Asist Beklentisi (xA)", "Hücum & xG", ""),
    "Big Chances Created": ("big_chances", "Net Gol Pozisyonu", "Hücum & xG", ""),
    "Attacks": ("attacks", "Toplam Hücum", "Hücum & xG", ""),
    "Shots on target": ("shots_on_target", "İsabetli Şut", "Hücum & xG", ""),
    "Shots off target": ("shots_off_target", "İsabetsiz Şut", "Hücum & xG", ""),
    "Blocked shots": ("blocked_shots", "Engellenen Şut", "Hücum & xG", ""),
    "Shots within penalty area": ("shots_inside_box", "Ceza Sahası İçi Şut", "Hücum & xG", ""),
    "Shots outside penalty area": ("shots_outside_box", "Ceza Sahası Dışı Şut", "Hücum & xG", ""),
    "Shots accuracy": ("shots_accuracy", "Şut İsabet Oranı (%)", "Hücum & xG", "%"),
    "Total passes": ("total_passes", "Toplam Pas", "Pas & Kurulum", ""),
    "Successful passes": ("accurate_passes", "İsabetli Pas", "Pas & Kurulum", ""),
    "Failed passes": ("failed_passes", "Hatalı Pas", "Pas & Kurulum", ""),
    "Passes Into Final Third": ("final_third_passes", "3. Bölgeye Pas", "Pas & Kurulum", ""),
    "Key Passes": ("key_passes", "Kilit Pas", "Pas & Kurulum", ""),
    "Passes Own Half": ("passes_own_half", "Kendi Yarı Sahasında Pas", "Pas & Kurulum", ""),
    "Passes Opposition Half": ("passes_opp_half", "Rakip Yarı Sahada Pas", "Pas & Kurulum", ""),
    "Backward Passes": ("backward_passes", "Geri Pas", "Pas & Kurulum", ""),
    "Long Passes": ("long_passes", "Uzun Pas", "Pas & Kurulum", ""),
    "Successful Long Passes": ("long_balls", "İsabetli Uzun Pas", "Pas & Kurulum", ""),
    "Crosses": ("crosses", "Orta Denemesi", "Pas & Kurulum", ""),
    "Successful Crosses": ("crosses_accurate", "İsabetli Orta", "Pas & Kurulum", ""),
    "Dribbles": ("dribbles", "Çalım Denemesi", "Genel & Topla Oynama", ""),
    "Successful Dribbles": ("dribbles_completed", "Başarılı Çalım", "Genel & Topla Oynama", ""),
    "Aerial Duels": ("aerial_duels", "Hava Topu Mücadelesi", "Savunma & İkili Mücadele", ""),
    "Successful Aerial Duels": ("aerial_duels_won", "Kazanılan Hava Topu", "Savunma & İkili Mücadele", ""),
    "Tackles": ("tackles", "Top Çalma (Tackle)", "Savunma & İkili Mücadele", ""),
    "Successful Tackles": ("tackles_won", "Başarılı Top Çalma", "Savunma & İkili Mücadele", ""),
    "Interceptions": ("interceptions", "Pas Arası (Interception)", "Savunma & İkili Mücadele", ""),
    "Clearances": ("clearances", "Uzaklaştırma", "Savunma & İkili Mücadele", ""),
    "Goalkeeper saves": ("goalkeeper_saves", "Kaleci Kurtarışı", "Savunma & İkili Mücadele", ""),
    "Corners": ("corners", "Köşe Vuruşu", "Disiplin & Duran Top", ""),
    "Free Kicks": ("free_kicks", "Serbest Vuruş", "Disiplin & Duran Top", ""),
    "Throw-Ins": ("throw_ins", "Taç Atışı", "Disiplin & Duran Top", ""),
    "Goal Kicks": ("goal_kicks", "Kale Vuruşu", "Disiplin & Duran Top", ""),
    "Offsides": ("offsides", "Ofsayt", "Disiplin & Duran Top", ""),
    "Fouls": ("fouls", "Yapılan Faul", "Disiplin & Duran Top", ""),
    "Yellow cards": ("yellow_cards", "Sarı Kart", "Disiplin & Duran Top", ""),
    "Red cards": ("red_cards", "Kırmızı Kart", "Disiplin & Duran Top", ""),
}


def _fix_mojibake(text: str) -> str:
    """Latin-1 olarak yanlış okunmuş UTF-8 dizgilerini (ör. 'R. LuÃ\\xads') düzeltir."""
    if any(ch in text for ch in ("Ã", "Ä", "Å")):
        try:
            return text.encode("latin1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            return text
    return text


def normalize_name(text: str) -> str:
    text = _fix_mojibake(text)
    tr_map = str.maketrans("İIıŞşĞğÜüÖöÇçØøŁłĐđ", "iiissgguuooccoolldd")
    cleaned = text.replace("-", " ").replace("æ", "ae").replace("Æ", "Ae").translate(tr_map)
    cleaned = unicodedata.normalize("NFD", cleaned)
    cleaned = "".join(ch for ch in cleaned if unicodedata.category(ch) != "Mn")
    return " ".join(cleaned.lower().strip().split())


def resolve_club_id(api_team_name: str, clubs_by_norm: dict[str, str]) -> str | None:
    norm = normalize_name(api_team_name)
    if not norm:
        return None
    if norm in CLUB_ALIASES:
        return CLUB_ALIASES[norm]
    if norm in clubs_by_norm:
        return clubs_by_norm[norm]
    for alias, cid in CLUB_ALIASES.items():
        if alias in norm or norm in alias:
            return cid
    return None


def unwrap_data(payload: Any) -> list[Any]:
    if payload is None:
        return []
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        if isinstance(payload.get("groups"), list):
            combined: list[Any] = []
            for grp in payload["groups"]:
                if isinstance(grp, dict) and isinstance(grp.get("standings"), list):
                    combined.extend(grp["standings"])
            if combined:
                return combined
        for key in ("data", "response", "leagues", "matches", "standings", "highlights"):
            val = payload.get(key)
            if isinstance(val, list):
                return val
        return [payload]
    return []


def find_super_lig_league_info(
    client: HighlightlyClient, country: str, name_hint: str
) -> tuple[int | str | None, str | None]:
    payload = client.get(
        "/leagues",
        params={"countryName": country},
        cache_group="leagues",
        cache_name=f"leagues_{country.lower()}",
    )
    items = unwrap_data(payload)
    if not items and payload is not None:
        payload = client.get("/leagues", cache_group="leagues", cache_name="leagues_all")
        items = unwrap_data(payload)

    hint_norm = normalize_name(name_hint)
    country_norm = normalize_name(country)

    for item in items:
        if not isinstance(item, dict):
            continue
        lname = normalize_name(str(item.get("name") or item.get("leagueName") or ""))
        c_obj = item.get("country") if isinstance(item.get("country"), dict) else {}
        cname = normalize_name(str(c_obj.get("name") or item.get("countryName") or ""))
        if ("super lig" in lname or hint_norm in lname) and (not cname or country_norm in cname or "turk" in cname):
            lid = item.get("id") or item.get("leagueId")
            seasons = item.get("seasons")
            latest_season: str | None = None
            if isinstance(seasons, list) and seasons:
                numeric_seasons = [
                    str(s.get("season") if isinstance(s, dict) else s)
                    for s in seasons
                    if (s.get("season") if isinstance(s, dict) else s) is not None
                ]
                if numeric_seasons:
                    latest_season = sorted(numeric_seasons)[-1]
            return lid, latest_season

    return None, None


def _ensure_club_exists(
    club_id: str,
    api_team_name: str,
    clubs_list: list[dict[str, Any]],
) -> dict[str, Any]:
    for c in clubs_list:
        if c["id"] == club_id:
            return c

    meta = NEW_CLUB_DEFAULTS.get(
        club_id,
        {
            "name": api_team_name,
            "shortName": api_team_name[:3].upper(),
            "primaryColor": "#1E293B",
            "accentColor": "#06B6D4",
            "city": "Türkiye",
            "stadium": f"{api_team_name} Stadyumu",
            "coach": "Teknik Direktör",
            "founded": 1965,
            "playStyle": "Uzun Top / Geçiş",
        },
    )

    new_club = {
        "id": club_id,
        "name": meta["name"],
        "shortName": meta["shortName"],
        "logo": meta["shortName"],
        "primaryColor": meta["primaryColor"],
        "accentColor": meta["accentColor"],
        "city": meta["city"],
        "stadium": meta["stadium"],
        "coach": meta["coach"],
        "founded": meta["founded"],
        "isSuperLig": True,
        "leagueName": "Trendyol Süper Lig",
        "totalMarketValueEur": 14500000,
        "averageAge": 26.2,
        "playStyle": meta["playStyle"],
        "goalsMinusXg": 0.4,
        "finalThirdPassIntensity": 57.5,
        "xGFor": 14.2,
        "xGAgainst": 13.8,
        "possessionAvg": 48.5,
        "ppda": 10.6,
        "squad": [],
        "fixtures": [],
    }
    clubs_list.append(new_club)
    return new_club


def _slugify_player(name: str, club_id: str) -> str:
    norm = normalize_name(name).replace(" ", "-").replace(".", "")
    clean = "".join(ch for ch in norm if ch.isalnum() or ch == "-")
    return f"{club_id}-{clean}" if clean else f"{club_id}-player"


def _map_pos(pos_raw: str) -> tuple[str, str]:
    p = pos_raw.lower()
    if "goal" in p:
        return "Kaleci", "GK"
    if "def" in p or "back" in p:
        return "Defans", "DF"
    if "forw" in p or "strik" in p or "att" in p:
        return "Forvet", "FW"
    return "Orta Saha", "MF"


def _shorten_name(full_name: str) -> str:
    parts = full_name.strip().split()
    if len(parts) >= 2:
        return f"{parts[0][0]}. {' '.join(parts[1:])}"
    return full_name


def _parse_dmy_to_iso(raw: Any) -> str:
    """DD/MM/YYYY, DD.MM.YYYY veya İngilizce ay tarihini YYYY-MM-DD biçimine çevirir."""
    s = str(raw or "").strip()
    if not s or s in ("-", "—", "N/A"):
        return "—"
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        return s
    m = re.fullmatch(r"(\d{1,2})[./](\d{1,2})[./](\d{4})", s)
    if m:
        return f"{m.group(3)}-{m.group(2).zfill(2)}-{m.group(1).zfill(2)}"
    for fmt in ("%b %d, %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return "—"


def _compute_age_from_iso(iso_date: str) -> int:
    """YYYY-MM-DD doğum tarihinden güncel yaşı hesaplar."""
    if not iso_date or iso_date == "—":
        return 0
    try:
        bday = datetime.strptime(iso_date, "%Y-%m-%d").date()
    except ValueError:
        return 0
    today = datetime.now(timezone(timedelta(hours=3))).date()
    return max(0, (today.year - bday.year) - ((today.month, today.day) < (bday.month, bday.day)))


def _parse_height_cm(raw: Any) -> int:
    """Örn. '1,96 m' veya '185 cm' değerini santimetre tam sayıya çevirir."""
    if isinstance(raw, (int, float)) and raw > 0:
        return int(round(raw * 100)) if raw < 3 else int(round(raw))
    s = str(raw or "").replace("\xa0", " ").replace(",", ".").strip().lower()
    m = re.search(r"(\d+(?:\.\d+)?)", s)
    if not m:
        return 0
    val = float(m.group(1))
    if "cm" not in s and 0 < val < 3.0:
        return int(round(val * 100))
    return int(round(val)) if 120 <= val <= 230 else 0


def _parse_eur_amount(raw: Any) -> int:
    """Örn. '€1.00M' veya '€800.00K' değerini Euro tam sayıya çevirir."""
    if isinstance(raw, (int, float)):
        return max(0, int(round(raw)))
    s = str(raw or "").replace(",", ".").strip().lower()
    if not s or "free" in s or s in ("-", "—", "n/a", "?"):
        return 0
    m = re.search(r"(\d+(?:\.\d+)?)\s*(bn|b|m|k)?", s)
    if not m:
        return 0
    num = float(m.group(1))
    unit = m.group(2) or ""
    mult = {"bn": 1_000_000_000, "b": 1_000_000_000, "m": 1_000_000, "k": 1_000}.get(unit, 1)
    return int(round(num * mult))


def _map_foot(raw: Any) -> str:
    s = str(raw or "").strip().lower()
    if s in ("right", "sağ"):
        return "Sağ"
    if s in ("left", "sol"):
        return "Sol"
    if s in ("both", "two", "çift"):
        return "Çift"
    return "—"


def _map_transfer_type(raw: Any, fee_raw: Any) -> str:
    s = str(raw or "").strip().lower()
    f = str(fee_raw or "").strip().lower()
    if "loan" in s or "kiral" in s:
        return "Kiralık"
    if "youth" in s or "altyap" in s or "u19" in s or "u21" in s:
        return "Altyapı"
    if "free" in s or "free" in f or not fee_raw or fee_raw in ("-", "—"):
        return "Bedelsiz"
    return "Bonservis"


_INJURY_REGION_KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("head", ("head", "concussion", "nose", "jaw", "eye", "face", "cheek", "skull", "tooth", "ear")),
    ("shoulder", ("shoulder", "collarbone", "clavicle", "acromioclavicular")),
    ("chest_ribs", ("rib", "chest", "pneumothorax", "lung", "sternum")),
    ("back", ("back", "spine", "lumbar", "sciatica", "vertebra", "neck")),
    ("arm_wrist", ("arm", "elbow", "wrist", "hand", "finger", "thumb", "forearm")),
    ("groin", ("groin", "adductor", "pubalgia", "hip", "pelvis", "abdomen", "hernia")),
    ("thigh_front", ("thigh", "quadricep", "rectus femoris")),
    ("hamstring", ("hamstring", "biceps femoris")),
    ("knee", ("knee", "cruciate", "acl", "mcl", "lcl", "meniscus", "patella", "kneecap")),
    ("calf", ("calf", "achilles", "soleus", "shin", "tibia", "fibula", "gastrocnemius")),
    ("ankle_foot", ("ankle", "foot", "toe", "heel", "metatarsal", "plantar", "instep", "syndesmosis")),
)


def _classify_injury_reason(reason: str) -> tuple[str | None, str]:
    """İngilizce sakatlık nedenini anatomi bölgesine veya sistemik kategoriye ayırır."""
    low = reason.lower()
    if any(k in low for k in ("ill", "flu", "virus", "fever", "cold", "corona", "covid", "sick", "infection")):
        return None, "Hastalık"
    if any(k in low for k in ("fitness", "fatigue", "tired")):
        return None, "Kondisyon"
    if any(k in low for k in ("rest", "knock-out rest")):
        return None, "Dinlenme"
    for region_id, keywords in _INJURY_REGION_KEYWORDS:
        if any(kw in low for kw in keywords):
            return region_id, ""
    return "other", ""


def _apply_real_player_profile(
    p: dict[str, Any],
    raw_prof: dict[str, Any],
    clubs_by_norm: dict[str, str],
) -> None:
    """Highlightly /players/{id} gerçek profil verilerini oyuncu kaydına uygular."""
    prof = raw_prof.get("profile") if isinstance(raw_prof.get("profile"), dict) else {}

    best_full = str(prof.get("fullName") or raw_prof.get("name") or raw_prof.get("fullName") or "").strip()
    if best_full and not re.match(r"^[A-ZÇĞİÖŞÜ]\.\s", best_full):
        cur_full = str(p.get("fullName") or "")
        if not cur_full or re.match(r"^[A-ZÇĞİÖŞÜ]\.\s", cur_full) or len(best_full) > len(cur_full):
            p["fullName"] = best_full
            p["name"] = _shorten_name(best_full) if " " in best_full else best_full

    citizenship = str(prof.get("citizenship") or "").strip()
    if citizenship:
        p["citizenship"] = citizenship

    foot = _map_foot(prof.get("foot"))
    if foot != "—":
        p["foot"] = foot

    height_cm = _parse_height_cm(prof.get("height"))
    if height_cm > 0:
        p["height"] = height_cm

    birth_iso = _parse_dmy_to_iso(prof.get("birthDate"))
    if birth_iso != "—":
        p["birthDate"] = birth_iso
        age = _compute_age_from_iso(birth_iso)
        if age > 0:
            p["age"] = age

    club_block = prof.get("club") if isinstance(prof.get("club"), dict) else {}
    expiry_iso = _parse_dmy_to_iso(club_block.get("contractExpiry"))
    if expiry_iso != "—":
        p["contractExpiry"] = expiry_iso

    pos_block = prof.get("position") if isinstance(prof.get("position"), dict) else {}
    sec_pos = pos_block.get("secondary")
    if isinstance(sec_pos, list):
        p["positionSecondary"] = [str(x).strip() for x in sec_pos if x]
    elif isinstance(sec_pos, str) and sec_pos.strip():
        p["positionSecondary"] = [sec_pos.strip()]

    # Market Value History & Peak/Current Value
    mv_raw = raw_prof.get("marketValue") if isinstance(raw_prof.get("marketValue"), list) else []
    mv_points: list[dict[str, Any]] = []
    for item in mv_raw:
        if not isinstance(item, dict):
            continue
        val = int(item.get("value") or 0)
        rec_iso = _parse_dmy_to_iso(item.get("recordedDate"))
        club_name = str(item.get("club") or "").strip()
        if val <= 0 or rec_iso == "—":
            continue
        mv_points.append({
            "recordedDate": rec_iso,
            "value": val,
            "clubId": resolve_club_id(club_name, clubs_by_norm) or "",
            "club": club_name or "—",
            "age": int(item.get("age") or p.get("age") or 0),
        })
    if mv_points:
        mv_points.sort(key=lambda pt: pt["recordedDate"])
        p["marketValueHistory"] = mv_points
        p["currentMarketValueEur"] = mv_points[-1]["value"]
        p["peakMarketValueEur"] = max(pt["value"] for pt in mv_points)

    # Real Transfer History (including foreign clubs)
    tr_raw = raw_prof.get("transfers") if isinstance(raw_prof.get("transfers"), list) else []
    transfers: list[dict[str, Any]] = []
    for tr in tr_raw:
        if not isinstance(tr, dict):
            continue
        from_name = str(tr.get("from") or "—").strip()
        to_name = str(tr.get("to") or "—").strip()
        fee_raw = tr.get("fee")
        fee_eur = _parse_eur_amount(fee_raw)
        tr_type = _map_transfer_type(tr.get("type"), fee_raw)
        fee_label = str(fee_raw).strip() if fee_raw else ("Kiralık" if tr_type == "Kiralık" else "Bedelsiz")
        transfers.append({
            "season": str(tr.get("season") or "—").strip(),
            "transferDate": _parse_dmy_to_iso(tr.get("transferDate")),
            "fromClubId": resolve_club_id(from_name, clubs_by_norm) or "",
            "from": from_name,
            "toClubId": resolve_club_id(to_name, clubs_by_norm) or "",
            "to": to_name,
            "fee": fee_label,
            "feeEur": fee_eur,
            "marketValue": _parse_eur_amount(tr.get("marketValue")),
            "type": tr_type,
        })
    if transfers or "transfers" in raw_prof:
        p["transfers"] = transfers

    # Active Transfer Rumours (current only)
    rum_block = raw_prof.get("rumours") if isinstance(raw_prof.get("rumours"), dict) else {}
    cur_rums = rum_block.get("current") if isinstance(rum_block.get("current"), list) else []
    rumours: list[dict[str, Any]] = []
    for r in cur_rums:
        if not isinstance(r, dict):
            continue
        r_club = str(r.get("club") or "").strip()
        if not r_club:
            continue
        prob_raw = str(r.get("transferProbability") or "0").replace("%", "").strip()
        prob = int(prob_raw) if prob_raw.isdigit() else 0
        rumours.append({
            "clubId": resolve_club_id(r_club, clubs_by_norm) or "",
            "club": r_club,
            "rumourDate": _parse_dmy_to_iso(r.get("rumourDate")),
            "transferProbability": prob,
            "source": "Transfermarkt",
        })
    if rumours or "rumours" in raw_prof:
        p["rumours"] = rumours

    # Real Injuries mapped into Anatomy Regions & Systemic Records
    inj_raw = raw_prof.get("injuries") if isinstance(raw_prof.get("injuries"), list) else []
    if inj_raw or "injuries" in raw_prof:
        anatomy = {
            r: {"count": 0, "totalDays": 0, "missedGames": 0, "heatLevel": 0, "records": []}
            for r in ANATOMY_REGIONS
        }
        systemic: list[dict[str, Any]] = []
        total_days = 0
        total_missed = 0
        total_cnt = 0

        for inj in inj_raw:
            if not isinstance(inj, dict):
                continue
            reason = str(inj.get("reason") or "Unknown").strip()
            from_iso = _parse_dmy_to_iso(inj.get("fromDate"))
            to_iso = _parse_dmy_to_iso(inj.get("toDate"))
            days = int(inj.get("absentDurationInDays") or 0)
            missed = int(inj.get("missedGames") or 0)
            total_days += days
            total_missed += missed
            total_cnt += 1

            reg_id, sys_cat = _classify_injury_reason(reason)
            if reg_id is None:
                systemic.append({
                    "reason": reason,
                    "category": sys_cat,
                    "fromDate": from_iso,
                    "toDate": to_iso,
                    "days": days,
                    "missedGames": missed,
                    "clubId": p["clubId"],
                    "clubName": p["clubName"],
                })
            else:
                slot = anatomy[reg_id]
                slot["count"] += 1
                slot["totalDays"] += days
                slot["missedGames"] += missed
                slot["records"].append({
                    "reason": reason,
                    "fromDate": from_iso,
                    "toDate": to_iso,
                    "days": days,
                    "missedGames": missed,
                    "clubId": p["clubId"],
                    "clubName": p["clubName"],
                })

        for slot in anatomy.values():
            c = slot["count"]
            slot["heatLevel"] = 3 if c >= 3 else 2 if c == 2 else 1 if c == 1 else 0

        p["injuries"] = {"anatomyRegions": anatomy, "systemicRecords": systemic}
        if total_cnt == 0:
            p["injuryRisk"] = "Düşük"
        elif total_missed >= 25 or total_days >= 180 or total_cnt >= 6:
            p["injuryRisk"] = "Kritik"
        elif total_missed >= 12 or total_days >= 90 or total_cnt >= 4:
            p["injuryRisk"] = "Yüksek"
        elif total_missed >= 4 or total_days >= 21 or total_cnt >= 2:
            p["injuryRisk"] = "Orta"
        else:
            p["injuryRisk"] = "Düşük"


def _create_player_record(
    player_id: str,
    full_name: str,
    club_id: str,
    club_name: str,
    pos_main: str,
    pos_group: str,
    shirt_no: int,
    seed_template: dict[str, Any] | None = None,
) -> dict[str, Any]:
    anatomy = {
        r: {"count": 0, "totalDays": 0, "missedGames": 0, "heatLevel": 0, "records": []}
        for r in ANATOMY_REGIONS
    }
    return {
        "id": player_id,
        "name": _shorten_name(full_name) if " " in full_name else full_name,
        "fullName": full_name,
        "shirtNumber": shirt_no or 99,
        "clubId": club_id,
        "clubName": club_name,
        "positionMain": pos_main,
        "positionGroup": pos_group,
        "positionSecondary": [],
        "foot": "—",
        "height": 0,
        "birthDate": "—",
        "age": 0,
        "citizenship": "—",
        "contractExpiry": "—",
        "currentMarketValueEur": 0,
        "peakMarketValueEur": 0,
        "injuryRisk": "Düşük",
        "gamesPlayed": 0,
        "minutesPlayed": 0,
        "goals": 0,
        "assists": 0,
        "yellowCards": 0,
        "redCards": 0,
        "xG": 0.0,
        "xA": 0.0,
        "avgMatchRating": 7.05,
        "per90Goals": 0.0,
        "per90Assists": 0.0,
        "passAccuracy": 80.5,
        "keyPassesPer90": 0.0,
        "progressiveActionsPer90": 3.6,
        **({"cleanSheets": 0, "savePercentage": 74.0, "PSxG_plus_minus": 1.5} if pos_group == "GK" else {}),
        "marketValueHistory": [],
        "transfers": [],
        "rumours": [],
        "perClub": [
            {
                "clubId": club_id,
                "clubName": club_name,
                "competition": "Süper Lig",
                "seasonRange": "2026/27",
                "games": 0,
                "minutes": 0,
                "goals": 0,
                "assists": 0,
                "avgRating": 7.05,
            }
        ],
        "injuries": {"anatomyRegions": anatomy, "systemicRecords": []},
    }


def _normalize_goal_target(raw_target: str | None, outcome: str) -> str:
    if not raw_target:
        return "Close High" if outcome == "Missed" else "Low Center"
    t = (
        raw_target.replace("Centre", "Center")
        .replace("CloseLeft", "Close Left")
        .replace("CloseRight", "Close Right")
        .strip()
    )
    valid = {
        "High Left", "High Center", "High Right",
        "Low Left", "Low Center", "Low Right",
        "Close Left", "Close Right", "Close High",
    }
    return t if t in valid else "Low Center"


def _parse_pct(val: Any) -> int:
    if isinstance(val, (int, float)):
        return int(round(val * 100 if val <= 1 else val))
    s = str(val or "0").replace("%", "").strip()
    try:
        return int(round(float(s)))
    except ValueError:
        return 33


def merge_bronze_into_gold() -> dict[str, int]:
    """Bronze klasöründeki gerçek Highlightly verilerini web/src/data Gold JSON dosyalarına işler."""
    from media_enrichment import extract_youtube_id, load_media_cache, save_media_cache

    standings_path = GOLD_DIR / "standings.json"
    clubs_path = GOLD_DIR / "clubs.json"
    players_path = GOLD_DIR / "players.json"
    matches_path = GOLD_DIR / "matches.json"

    standings_doc = json.loads(standings_path.read_text(encoding="utf-8"))
    clubs_list: list[dict[str, Any]] = json.loads(clubs_path.read_text(encoding="utf-8"))
    seed_players_list: list[dict[str, Any]] = json.loads(players_path.read_text(encoding="utf-8"))

    media_cache = load_media_cache()
    yt_tr_checks: dict[str, bool] = media_cache.get("yt_tr_checks") or {}
    cached_hl_by_gold_id: dict[str, dict[str, Any]] = media_cache.get("match_highlights") or {}
    photo_map: dict[str, str] = {
        str(pid): str(url)
        for pid, url in (media_cache.get("player_photos") or {}).items()
        if isinstance(url, str) and url.startswith("http")
    }
    player_profiles_by_id: dict[str, dict[str, Any]] = {}
    players_bronze_dir = BRONZE_DIR / "players"
    if players_bronze_dir.exists():
        for pf in sorted(players_bronze_dir.glob("player_*.json")):
            m_pid = re.search(r"player_(\d+)\.json", pf.name)
            if not m_pid:
                continue
            try:
                p_raw = json.loads(pf.read_text(encoding="utf-8"))
                p_items = unwrap_data(p_raw)
                if p_items and isinstance(p_items[0], dict):
                    canon_pid = f"hl-{m_pid.group(1)}"
                    player_profiles_by_id[canon_pid] = p_items[0]
                    p_url = p_items[0].get("logo") or p_items[0].get("photo") or p_items[0].get("image")
                    if isinstance(p_url, str) and p_url.startswith("http"):
                        photo_map.setdefault(canon_pid, p_url)
            except (OSError, json.JSONDecodeError):
                continue

    club_logos: dict[str, str] = {}

    # Index existing seed players by normalized fullName/name so known stars keep their rich injury & transfer histories
    seed_by_norm: dict[str, dict[str, Any]] = {}
    for sp in seed_players_list:
        seed_by_norm[normalize_name(sp["fullName"])] = sp
        seed_by_norm.setdefault(normalize_name(sp["name"]), sp)

    clubs_by_id = {c["id"]: c for c in clubs_list}
    clubs_by_norm = {normalize_name(c["name"]): c["id"] for c in clubs_list}

    updated_standings = 0
    updated_highlights = 0
    detailed_matches_count = 0

    # 1) Standings merge (2023-2025 historical + 2026 active 18 real Super Lig teams)
    standings_dir = BRONZE_DIR / "standings"
    active_super_lig_ids: set[str] = set()
    hist_trends_by_club: dict[str, dict[str, dict[str, Any]]] = {}

    if standings_dir.exists():
        all_standing_files = sorted(standings_dir.glob("*.json"))
        for sf in all_standing_files:
            year_match = re.search(r"_(202[0-5])_", sf.name)
            if not year_match:
                continue
            yr = year_match.group(1)
            raw_hist = json.loads(sf.read_text(encoding="utf-8"))
            for h_row in unwrap_data(raw_hist):
                if not isinstance(h_row, dict):
                    continue
                t_info = h_row.get("team") if isinstance(h_row.get("team"), dict) else {}
                t_name = str(t_info.get("name") or h_row.get("teamName") or "")
                cid = resolve_club_id(t_name, clubs_by_norm)
                if not cid:
                    continue
                t_logo = str(t_info.get("logo") or "")
                if t_logo.startswith("http"):
                    club_logos.setdefault(cid, t_logo)
                tot = h_row.get("total") if isinstance(h_row.get("total"), dict) else {}
                games = max(1, int(tot.get("games") or 38))
                pts = int(h_row.get("points") or 0)
                gf = int(tot.get("scoredGoals") or 0)
                ga = int(tot.get("receivedGoals") or 0)
                rank = int(h_row.get("position") or 18)
                hist_trends_by_club.setdefault(cid, {})[yr] = {
                    "season": yr,
                    "rank": rank,
                    "points": pts,
                    "goalsFor": gf,
                    "goalsAgainst": ga,
                    "ppg": round(pts / games, 2),
                    "xgDiff": round((gf - ga) * 0.08, 1),
                }

        standing_files_2026 = [f for f in all_standing_files if "_2026" in f.name] or all_standing_files
        if standing_files_2026:
            raw = json.loads(standing_files_2026[-1].read_text(encoding="utf-8"))
            api_rows = unwrap_data(raw)
            existing_by_club = {row["clubId"]: row for row in standings_doc.get("standings", [])}
            new_standings: list[dict[str, Any]] = []

            for api_row in api_rows:
                if not isinstance(api_row, dict):
                    continue
                team_info = api_row.get("team") if isinstance(api_row.get("team"), dict) else {}
                team_name = str(team_info.get("name") or api_row.get("teamName") or "")
                cid = resolve_club_id(team_name, clubs_by_norm)
                if not cid:
                    cid = normalize_name(team_name).replace(" ", "-")
                active_super_lig_ids.add(cid)

                t_logo = str(team_info.get("logo") or "")
                if t_logo.startswith("http"):
                    club_logos[cid] = t_logo

                club_obj = _ensure_club_exists(cid, team_name, clubs_list)
                if cid in club_logos:
                    club_obj["logo"] = club_logos[cid]
                clubs_by_id[cid] = club_obj
                clubs_by_norm[normalize_name(team_name)] = cid

                base_row = existing_by_club.get(cid)
                if not base_row:
                    base_row = {
                        "rank": int(api_row.get("position") or 1),
                        "clubId": cid,
                        "clubName": club_obj["name"],
                        "shortName": club_obj["shortName"],
                        "logo": club_obj["logo"],
                        "overall": {"played": 0, "won": 0, "drawn": 0, "lost": 0, "goalsFor": 0, "goalsAgainst": 0, "goalDifference": 0, "points": 0},
                        "home": {"played": 0, "won": 0, "drawn": 0, "lost": 0, "goalsFor": 0, "goalsAgainst": 0, "goalDifference": 0, "points": 0},
                        "away": {"played": 0, "won": 0, "drawn": 0, "lost": 0, "goalsFor": 0, "goalsAgainst": 0, "goalDifference": 0, "points": 0},
                        "form": [],
                        "recentMatches": [],
                        "seasonTrends": [],
                    }

                base_row["rank"] = int(api_row.get("position") or base_row["rank"])
                base_row["clubName"] = club_obj["name"]
                base_row["shortName"] = club_obj["shortName"]
                if cid in club_logos:
                    base_row["logo"] = club_logos[cid]
                base_row["overall"]["points"] = int(api_row.get("points", base_row["overall"]["points"]))

                for split_key, api_key in (("overall", "total"), ("home", "home"), ("away", "away")):
                    block = api_row.get(api_key) if isinstance(api_row.get(api_key), dict) else None
                    if block:
                        played = int(block.get("games", 0))
                        won = int(block.get("wins", 0))
                        drawn = int(block.get("draws", 0))
                        lost = int(block.get("loses", 0))
                        gf = int(block.get("scoredGoals", 0))
                        ga = int(block.get("receivedGoals", 0))
                        base_row[split_key] = {
                            "played": played,
                            "won": won,
                            "drawn": drawn,
                            "lost": lost,
                            "goalsFor": gf,
                            "goalsAgainst": ga,
                            "goalDifference": gf - ga,
                            "points": int(api_row.get("points", won * 3 + drawn)) if split_key == "overall" else won * 3 + drawn,
                        }

                # Synthesize 2023-2026 Season Trends from real Bronze standings
                old_trends_map = {t["season"][:4]: t for t in base_row.get("seasonTrends", [])}
                synthesized_trends: list[dict[str, Any]] = []
                for yr in ("2023", "2024", "2025"):
                    if cid in hist_trends_by_club and yr in hist_trends_by_club[cid]:
                        synthesized_trends.append(hist_trends_by_club[cid][yr])
                    elif yr in old_trends_map:
                        synthesized_trends.append(old_trends_map[yr])
                    else:
                        synthesized_trends.append({
                            "season": yr, "rank": 18, "points": 38, "goalsFor": 35, "goalsAgainst": 52, "ppg": 1.0, "xgDiff": -1.5,
                        })
                p_count = max(1, base_row["overall"]["played"])
                synthesized_trends.append({
                    "season": f"2026 ({p_count}H)",
                    "rank": base_row["rank"],
                    "points": base_row["overall"]["points"],
                    "goalsFor": base_row["overall"]["goalsFor"],
                    "goalsAgainst": base_row["overall"]["goalsAgainst"],
                    "ppg": round(base_row["overall"]["points"] / p_count, 2),
                    "xgDiff": round((base_row["overall"]["goalsFor"] - base_row["overall"]["goalsAgainst"]) * 0.15, 1),
                })
                base_row["seasonTrends"] = synthesized_trends

                new_standings.append(base_row)
                updated_standings += 1

            if len(new_standings) >= 18:
                new_standings.sort(key=lambda r: r["rank"])
                standings_doc["standings"] = new_standings
                standings_doc["currentRound"] = max((r["overall"]["played"] for r in new_standings), default=11)
                for c in clubs_list:
                    if c["id"] in active_super_lig_ids:
                        c["isSuperLig"] = True
                    elif c.get("leagueName") == "Trendyol Süper Lig":
                        c["isSuperLig"] = False
                        c["leagueName"] = "TFF 1. Lig"

    # 2) Build highlights lookup (collects all clips per match including goal-clips)
    hl_clips_by_api_id: dict[int, list[dict[str, str]]] = {}
    hl_clips_by_pair: dict[tuple[str, str], list[dict[str, str]]] = {}
    highlights_dir = BRONZE_DIR / "highlights"
    if highlights_dir.exists():
        for fpath in sorted(highlights_dir.glob("*.json")):
            raw = json.loads(fpath.read_text(encoding="utf-8"))
            for hl in unwrap_data(raw):
                if not isinstance(hl, dict):
                    continue
                embed = str(hl.get("embedUrl") or hl.get("url") or "").strip()
                img = str(hl.get("imgUrl") or "").strip()
                clip_cat = str(hl.get("category") or "match-highlights")
                clip_title = str(hl.get("title") or ("Maç Özeti" if clip_cat == "match-highlights" else "Gol Klibi"))
                match_obj = hl.get("match") if isinstance(hl.get("match"), dict) else {}
                h_team_obj = match_obj.get("homeTeam") or {}
                a_team_obj = match_obj.get("awayTeam") or {}
                h_id = resolve_club_id(str(h_team_obj.get("name") or ""), clubs_by_norm)
                a_id = resolve_club_id(str(a_team_obj.get("name") or ""), clubs_by_norm)
                if h_id and str(h_team_obj.get("logo") or "").startswith("http"):
                    club_logos.setdefault(h_id, str(h_team_obj["logo"]))
                if a_id and str(a_team_obj.get("logo") or "").startswith("http"):
                    club_logos.setdefault(a_id, str(a_team_obj["logo"]))
                if not embed:
                    continue
                clip_item = {"title": clip_title, "embedUrl": embed, "imgUrl": img, "category": clip_cat}
                api_mid = match_obj.get("id")
                if api_mid:
                    bucket = hl_clips_by_api_id.setdefault(int(api_mid), [])
                    if not any(x["embedUrl"] == embed for x in bucket):
                        bucket.append(clip_item)
                if h_id and a_id:
                    p_bucket = hl_clips_by_pair.setdefault((h_id, a_id), [])
                    if not any(x["embedUrl"] == embed for x in p_bucket):
                        p_bucket.append(clip_item)

    # 3) Collect ALL real Highlightly players from downloaded lineups & match_details
    real_players_by_hl_id: dict[int, dict[str, Any]] = {}
    real_players_by_id: dict[str, dict[str, Any]] = {}
    real_players_by_club_norm: dict[tuple[str, str], dict[str, Any]] = {}
    clubs_with_real_lineups: set[str] = set()
    player_perf_acc: dict[str, dict[str, Any]] = {}

    details_dir = BRONZE_DIR / "match_details"
    lineups_dir = BRONZE_DIR / "lineups"

    detail_by_api_id: dict[int, dict[str, Any]] = {}
    if details_dir.exists():
        for fpath in sorted(details_dir.glob("*.json")):
            raw = json.loads(fpath.read_text(encoding="utf-8"))
            for dm in unwrap_data(raw):
                if isinstance(dm, dict) and dm.get("id") is not None:
                    detail_by_api_id[int(dm["id"])] = dm

    lineup_by_api_id: dict[int, dict[str, Any]] = {}
    if lineups_dir.exists():
        for fpath in sorted(lineups_dir.glob("*.json")):
            m = re.search(r"lineup_(\d+)\.json", fpath.name)
            if not m:
                continue
            api_mid = int(m.group(1))
            raw = json.loads(fpath.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                lineup_by_api_id[api_mid] = raw

    def _index_player_norms(club_id: str, rec: dict[str, Any], *names: str) -> None:
        for nm in names:
            n_norm = normalize_name(nm)
            if not n_norm:
                continue
            real_players_by_club_norm.setdefault((club_id, n_norm), rec)
            n_nodot = n_norm.replace(".", "").strip()
            if n_nodot:
                real_players_by_club_norm.setdefault((club_id, n_nodot), rec)
            if " " in nm:
                short_n = normalize_name(_shorten_name(nm)).replace(".", "").strip()
                if short_n:
                    real_players_by_club_norm.setdefault((club_id, short_n), rec)

    def _is_same_club_player(parts: list[str], kp: list[str]) -> bool:
        if not parts or not kp:
            return False
        p_clean = [w.replace(".", "") for w in parts if w.replace(".", "")]
        k_clean = [w.replace(".", "") for w in kp if w.replace(".", "")]
        if not p_clean or not k_clean:
            return False
        if len(p_clean) >= 2 and len(k_clean) >= 2 and (
            set(p_clean).issubset(set(k_clean)) or set(k_clean).issubset(set(p_clean))
        ):
            return True
        if p_clean[-1] != k_clean[-1]:
            return False
        if len(p_clean) == 1 or len(k_clean) == 1:
            return True
        f_p, f_k = p_clean[0], k_clean[0]
        if f_p[0] != f_k[0]:
            return False
        # At least one side is an initial (<=2 chars), a 2-3 char nickname with same 2-char prefix, or 4-char prefix match
        if len(f_p) <= 2 or len(f_k) <= 2:
            return True
        if (len(f_p) <= 3 or len(f_k) <= 3) and f_p[:2] == f_k[:2]:
            return True
        if f_p[:4] == f_k[:4]:
            return True
        return False

    def _upgrade_player_identity(
        existing: dict[str, Any],
        hl_pid: int | None,
        raw_name: str,
        club_id: str,
        shirt_no: int,
    ) -> dict[str, Any]:
        # Upgrade abbreviated or shorter/accent-stripped name when a richer full name arrives
        cur_full = existing["fullName"]
        raw_clean = _fix_mojibake(raw_name.strip())
        cur_has_dot = "." in cur_full or len(cur_full.split()[0]) <= 2
        raw_has_dot = "." in raw_clean or (bool(raw_clean) and len(raw_clean.split()[0]) <= 2)
        should_upgrade_name = (
            (cur_has_dot and not raw_has_dot)
            or (not raw_has_dot and len(raw_clean) > len(cur_full) and not cur_full.lower().startswith(raw_clean.lower()))
            or (normalize_name(raw_clean) == normalize_name(cur_full) and raw_clean != cur_full and sum(ord(c) > 127 for c in raw_clean) > sum(ord(c) > 127 for c in cur_full))
        )
        if should_upgrade_name and raw_clean:
            existing["fullName"] = raw_clean
            existing["name"] = _shorten_name(raw_clean) if " " in raw_clean else raw_clean
        if shirt_no and shirt_no != 99 and existing["shirtNumber"] in (0, 9, 99):
            existing["shirtNumber"] = shirt_no
        if hl_pid is not None and hl_pid not in real_players_by_hl_id:
            real_players_by_hl_id[hl_pid] = existing
        _index_player_norms(club_id, existing, raw_clean, existing["fullName"])
        return existing

    def register_real_player(
        hl_pid: int | None,
        raw_name: str,
        club_id: str,
        pos_raw: str,
        shirt_no: int,
        allow_create: bool = True,
    ) -> dict[str, Any]:
        raw_clean = _fix_mojibake(raw_name.strip())
        if hl_pid is not None and hl_pid in real_players_by_hl_id:
            return _upgrade_player_identity(real_players_by_hl_id[hl_pid], hl_pid, raw_clean, club_id, shirt_no)

        norm = normalize_name(raw_clean)
        norm_nodot = norm.replace(".", "").strip()
        if (club_id, norm) in real_players_by_club_norm:
            return _upgrade_player_identity(real_players_by_club_norm[(club_id, norm)], hl_pid, raw_clean, club_id, shirt_no)
        if norm_nodot and (club_id, norm_nodot) in real_players_by_club_norm:
            return _upgrade_player_identity(real_players_by_club_norm[(club_id, norm_nodot)], hl_pid, raw_clean, club_id, shirt_no)

        # Match abbreviated / omitted-middle / reversed names in BOTH directions within same club
        parts = norm.split()
        if parts:
            # Scan unique club players rather than norm keys to upgrade deterministically
            seen_pids: set[str] = set()
            for (cid_k, _), p_val in list(real_players_by_club_norm.items()):
                if cid_k != club_id or p_val["id"] in seen_pids:
                    continue
                seen_pids.add(p_val["id"])
                kp = normalize_name(p_val["fullName"]).split()
                if _is_same_club_player(parts, kp) or (len(parts) >= 2 and set(parts) == set(kp)):
                    return _upgrade_player_identity(p_val, hl_pid, raw_clean, club_id, shirt_no)

        club_name = clubs_by_id[club_id]["name"]
        pos_main, pos_group = _map_pos(pos_raw)
        if not allow_create:
            # E.g., manager/coach card events not belonging to playing squad
            temp_id = f"hl-{hl_pid}" if hl_pid is not None else _slugify_player(raw_clean, club_id)
            player_perf_acc.setdefault(
                temp_id,
                {"games": 0, "minutes": 0, "goals": 0, "assists": 0, "yc": 0, "rc": 0, "rating_sum": 0.0, "shots": 0},
            )
            return _create_player_record(temp_id, raw_clean, club_id, club_name, pos_main, pos_group, shirt_no)

        seed_tpl = seed_by_norm.get(norm)
        pid = f"hl-{hl_pid}" if hl_pid is not None else _slugify_player(raw_clean, club_id)
        if pid in real_players_by_id:
            return _upgrade_player_identity(real_players_by_id[pid], hl_pid, raw_clean, club_id, shirt_no)

        rec = _create_player_record(
            pid, raw_clean, club_id, club_name, pos_main, pos_group, shirt_no, seed_template=seed_tpl
        )
        if hl_pid is not None:
            real_players_by_hl_id[hl_pid] = rec
        real_players_by_id[pid] = rec
        _index_player_norms(club_id, rec, raw_clean)
        player_perf_acc[pid] = {"games": 0, "minutes": 0, "goals": 0, "assists": 0, "yc": 0, "rc": 0, "rating_sum": 0.0, "shots": 0}
        return rec

    # Pre-register lineup players in two passes: full unabbreviated names first, then abbreviated names
    lineup_entries: list[tuple[bool, int | None, str, str, str, int]] = []
    for api_mid, ldata in lineup_by_api_id.items():
        for team_key in ("homeTeam", "awayTeam"):
            tblock = ldata.get(team_key)
            if not isinstance(tblock, dict):
                continue
            raw_tname = str(tblock.get("name") or "")
            cid = resolve_club_id(raw_tname, clubs_by_norm)
            if not cid:
                continue
            if tblock.get("initialLineup"):
                clubs_with_real_lineups.add(cid)
            nodes: list[dict[str, Any]] = []
            for row in tblock.get("initialLineup") or []:
                nodes.extend(n for n in row if isinstance(n, dict) and n.get("name"))
            nodes.extend(n for n in (tblock.get("substitutes") or []) if isinstance(n, dict) and n.get("name"))
            for node in nodes:
                rname = _fix_mojibake(str(node["name"]).strip())
                is_full = "." not in rname and len(rname.split()[0]) > 2
                lineup_entries.append((
                    is_full,
                    int(node["id"]) if node.get("id") else None,
                    rname,
                    cid,
                    str(node.get("position") or "Midfielder"),
                    int(node.get("number") or 0),
                ))

    lineup_entries.sort(key=lambda item: (item[0], item[1] is not None), reverse=True)
    for _, hl_pid, rname, cid, ppos, pnum in lineup_entries:
        register_real_player(hl_pid, rname, cid, ppos, pnum)

    def _resolve_photo_url(p_obj: dict[str, Any]) -> str | None:
        pid = p_obj["id"]
        if pid in photo_map:
            return photo_map[pid]
        fname = p_obj["fullName"]
        cid = p_obj["clubId"]
        candidates = [_slugify_player(fname, cid)]
        parts = fname.split()
        if len(parts) >= 3:
            candidates.append(_slugify_player(f"{parts[0]} {parts[-1]}", cid))
        for cand in candidates:
            if cand in photo_map:
                photo_map[pid] = photo_map[cand]
                return photo_map[pid]
        return None

    for rec in real_players_by_id.values():
        _resolve_photo_url(rec)

    # 4) Load ALL real Finished matches from bronze/matches/*.json
    all_raw_matches: dict[int, dict[str, Any]] = {}
    matches_dir = BRONZE_DIR / "matches"
    if matches_dir.exists():
        for fpath in sorted(matches_dir.glob("*.json")):
            raw = json.loads(fpath.read_text(encoding="utf-8"))
            for m in unwrap_data(raw):
                if isinstance(m, dict) and m.get("id") is not None:
                    state = m.get("state") or {}
                    if state.get("description") == "Finished":
                        all_raw_matches[int(m["id"])] = m

    sorted_finished = sorted(
        all_raw_matches.values(),
        key=lambda m: str(m.get("date") or ""),
        reverse=True,
    )

    real_matches_gold: list[dict[str, Any]] = []
    club_dna_acc: dict[str, dict[str, Any]] = {}
    gk_acc: dict[str, dict[str, Any]] = {}

    def _club_dna(cid: str) -> dict[str, Any]:
        return club_dna_acc.setdefault(
            cid,
            {
                "matches": 0, "xg_for": 0.0, "xg_against": 0.0, "goals_for": 0,
                "poss_sum": 0.0, "final_third_sum": 0.0, "total_pass_sum": 0.0,
                "long_pass_sum": 0.0, "tackles_sum": 0.0, "interceptions_sum": 0.0,
            },
        )

    for base_m in sorted_finished:
        api_mid = int(base_m["id"])
        dm = detail_by_api_id.get(api_mid)
        m_src = dm if dm else base_m

        state = m_src.get("state") or {}
        score_str = str((state.get("score") or {}).get("current") or "")
        parts = [p.strip() for p in score_str.split("-")]
        if len(parts) != 2 or not (parts[0].isdigit() and parts[1].isdigit()):
            continue
        hs, as_ = int(parts[0]), int(parts[1])

        h_team_obj = m_src.get("homeTeam") or {}
        a_team_obj = m_src.get("awayTeam") or {}
        h_raw_name = str(h_team_obj.get("name") or "")
        a_raw_name = str(a_team_obj.get("name") or "")
        h_id = resolve_club_id(h_raw_name, clubs_by_norm) or normalize_name(h_raw_name).replace(" ", "-")
        a_id = resolve_club_id(a_raw_name, clubs_by_norm) or normalize_name(a_raw_name).replace(" ", "-")
        if str(h_team_obj.get("logo") or "").startswith("http"):
            club_logos.setdefault(h_id, str(h_team_obj["logo"]))
        if str(a_team_obj.get("logo") or "").startswith("http"):
            club_logos.setdefault(a_id, str(a_team_obj["logo"]))
        h_club = _ensure_club_exists(h_id, h_raw_name, clubs_list)
        a_club = _ensure_club_exists(a_id, a_raw_name, clubs_list)
        if h_id in club_logos:
            h_club["logo"] = club_logos[h_id]
        if a_id in club_logos:
            a_club["logo"] = club_logos[a_id]
        clubs_by_id[h_id] = h_club
        clubs_by_id[a_id] = a_club

        round_str = str(m_src.get("round") or "")
        round_match = re.search(r"(\d+)$", round_str)
        round_num = int(round_match.group(1)) if round_match else 11
        date_iso = str(m_src.get("date") or "2026-11-08T15:00:00.000Z")
        date_str = date_iso[:10]
        time_str = date_iso[11:16] if len(date_iso) >= 16 else "19:00"
        gold_id = f"hl-{h_id}-{a_id}-r{round_num}"

        lineup_json = lineup_by_api_id.get(api_mid, {})
        has_real_detail = dm is not None

        scorer_counts: dict[str, int] = {}
        assist_counts: dict[str, int] = {}
        yellow_set: set[str] = set()
        red_set: set[str] = set()
        sub_out_min: dict[str, int] = {}
        red_out_min: dict[str, int] = {}
        sub_in_records: dict[str, list[tuple[dict[str, Any], int]]] = {h_id: [], a_id: []}
        ht_home_goals = 0
        ht_away_goals = 0
        gold_events: list[dict[str, Any]] = []

        def _ev_sort_key(ev_item: dict[str, Any]) -> tuple[int, int, int]:
            m_str = str(ev_item.get("time") or "45")
            base_m = int(re.sub(r"[^0-9]", "", m_str.split("+")[0]) or 45)
            add_m = int(re.sub(r"[^0-9]", "", m_str.split("+")[1]) or 0) if "+" in m_str else 0
            et = str(ev_item.get("type") or "")
            prio = 0 if et in ("Goal", "Penalty", "Own Goal") else 1 if "Yellow" in et else 2 if "Red" in et else 3
            return (base_m, add_m, prio)

        if has_real_detail:
            detailed_matches_count += 1
            for ev_idx, ev in enumerate(sorted((dm.get("events") or []), key=_ev_sort_key)):
                ev_type_raw = str(ev.get("type") or "")
                ev_team_name = str((ev.get("team") or {}).get("name") or "")
                ev_cid = resolve_club_id(ev_team_name, clubs_by_norm) or h_id
                min_raw = str(ev.get("time") or "45")
                min_num = int(re.sub(r"[^0-9]", "", min_raw.split("+")[0]) or 45)
                added_num = int(re.sub(r"[^0-9]", "", min_raw.split("+")[1]) or 0) if "+" in min_raw else None

                allow_ev_create = ev_cid not in clubs_with_real_lineups

                if ev_type_raw == "Substitution":
                    out_raw = _fix_mojibake(str(ev.get("player") or "").strip())
                    if not out_raw or out_raw.lower() == "oyuncu":
                        continue
                    out_p = register_real_player(
                        int(ev["playerId"]) if ev.get("playerId") else None,
                        out_raw,
                        ev_cid,
                        "Midfielder",
                        10,
                        allow_create=allow_ev_create,
                    )
                    if out_p["id"] not in real_players_by_id:
                        continue
                    sub_out_min[out_p["id"]] = min_num
                    in_name = _fix_mojibake(str(ev.get("substituted") or "").strip())
                    in_pid = int(ev["assistingPlayerId"]) if ev.get("assistingPlayerId") else None
                    if in_name and in_name.lower() != "oyuncu":
                        in_p = register_real_player(
                            in_pid,
                            in_name,
                            ev_cid,
                            "Midfielder",
                            99,
                            allow_create=allow_ev_create,
                        )
                        if in_p["id"] in real_players_by_id:
                            sub_in_records.setdefault(ev_cid, []).append((in_p, min_num))
                            gold_events.append({
                                "id": f"{gold_id}-ev-{ev_idx}",
                                "minute": min_num,
                                **({"addedTime": added_num} if added_num else {}),
                                "type": "substitution",
                                "clubId": ev_cid,
                                "playerId": out_p["id"],
                                "playerName": out_p["name"],
                                "assistPlayerId": in_p["id"],
                                "assistPlayerName": in_p["name"],
                                "detail": "",
                            })
                    continue

                if ev_type_raw in ("Goal", "Penalty", "Own Goal"):
                    ev_type = "goal"
                    ev_detail = (
                        "Penaltı Golü"
                        if ev_type_raw == "Penalty"
                        else "Kendi Kalesine Gol"
                        if ev_type_raw == "Own Goal"
                        else "Akan Oyun Golü"
                    )
                elif "Second Yellow" in ev_type_raw or "Red" in ev_type_raw:
                    ev_type = "red_card"
                    ev_detail = "2. Sarıdan Kırmızı Kart" if "Second Yellow" in ev_type_raw else ""
                elif "Yellow" in ev_type_raw:
                    ev_type = "yellow_card"
                    ev_detail = ""
                else:
                    continue

                ev_raw_pname = _fix_mojibake(str(ev.get("player") or "").strip())
                if not ev_raw_pname or ev_raw_pname.lower() == "oyuncu":
                    continue
                coach_norm = normalize_name(str((clubs_by_id.get(ev_cid) or {}).get("coach") or ""))
                ev_pnorm = normalize_name(ev_raw_pname)
                if (
                    ev_type != "goal"
                    and coach_norm
                    and ev_pnorm
                    and _is_same_club_player(ev_pnorm.split(), coach_norm.split())
                ):
                    continue

                p_obj = register_real_player(
                    int(ev["playerId"]) if ev.get("playerId") else None,
                    ev_raw_pname,
                    ev_cid,
                    "Midfielder",
                    10,
                    allow_create=allow_ev_create,
                )
                if p_obj["id"] not in real_players_by_id:
                    continue
                assist_pid = None
                assist_pname = None
                if ev_type == "goal":
                    scorer_counts[p_obj["id"]] = scorer_counts.get(p_obj["id"], 0) + 1
                    player_perf_acc[p_obj["id"]]["goals"] += 1
                    if min_num <= 45:
                        if ev_cid == h_id:
                            ht_home_goals += 1
                        else:
                            ht_away_goals += 1
                    if ev.get("assist"):
                        assist_raw = _fix_mojibake(str(ev["assist"]).strip())
                        if assist_raw and assist_raw.lower() != "oyuncu":
                            a_obj = register_real_player(
                                int(ev["assistingPlayerId"]) if ev.get("assistingPlayerId") else None,
                                assist_raw,
                                ev_cid,
                                "Midfielder",
                                8,
                                allow_create=allow_ev_create,
                            )
                            if a_obj["id"] in real_players_by_id:
                                assist_pid = a_obj["id"]
                                assist_pname = a_obj["name"]
                                assist_counts[a_obj["id"]] = assist_counts.get(a_obj["id"], 0) + 1
                                player_perf_acc[a_obj["id"]]["assists"] += 1
                elif ev_type == "yellow_card":
                    yellow_set.add(p_obj["id"])
                    player_perf_acc[p_obj["id"]]["yc"] += 1
                elif ev_type == "red_card":
                    if "Second Yellow" in ev_type_raw or p_obj["id"] in yellow_set:
                        yellow_set.add(p_obj["id"])
                        ev_detail = "2. Sarıdan Kırmızı Kart"
                        for idx_back in range(len(gold_events) - 1, -1, -1):
                            prev_ev = gold_events[idx_back]
                            if prev_ev["minute"] != min_num:
                                break
                            if prev_ev["type"] == "yellow_card" and prev_ev["playerId"] == p_obj["id"]:
                                gold_events.pop(idx_back)
                                player_perf_acc[p_obj["id"]]["yc"] = max(
                                    0, player_perf_acc[p_obj["id"]]["yc"] - 1
                                )
                                break
                    red_set.add(p_obj["id"])
                    red_out_min.setdefault(p_obj["id"], min_num)
                    player_perf_acc[p_obj["id"]]["rc"] += 1

                gold_events.append({
                    "id": f"{gold_id}-ev-{ev_idx}",
                    "minute": min_num,
                    **({"addedTime": added_num} if added_num else {}),
                    "type": ev_type,
                    "clubId": ev_cid,
                    "playerId": p_obj["id"],
                    "playerName": p_obj["name"],
                    **({"assistPlayerId": assist_pid, "assistPlayerName": assist_pname} if assist_pid else {}),
                    "detail": ev_detail,
                })

        box_score: list[dict[str, Any]] = []
        match_gk_ids: dict[str, str] = {}

        def build_side(team_key: str, cid: str, cname: str) -> tuple[str, list[list[dict[str, Any]]]]:
            side_data = lineup_json.get(team_key) if isinstance(lineup_json.get(team_key), dict) else {}
            formation = str(side_data.get("formation") or "4-2-3-1")
            raw_matrix = side_data.get("initialLineup") or []
            matrix: list[list[dict[str, Any]]] = []
            seen_in_box: set[str] = set()
            for row in raw_matrix:
                row_nodes: list[dict[str, Any]] = []
                for node in row:
                    p_raw_name = str(node.get("name") or "Oyuncu")
                    p_num = int(node.get("number") or 0)
                    p_pos = str(node.get("position") or "Midfielder")
                    p_obj = register_real_player(
                        int(node["id"]) if node.get("id") else None,
                        p_raw_name,
                        cid,
                        p_pos,
                        p_num,
                    )
                    pid = p_obj["id"]
                    seen_in_box.add(pid)
                    g_cnt = scorer_counts.get(pid, 0)
                    a_cnt = assist_counts.get(pid, 0)
                    yc = pid in yellow_set
                    rc = pid in red_set
                    sub_min = sub_out_min.get(pid)
                    sent_off_min = red_out_min.get(pid)
                    mins_played = min(x for x in (sub_min, sent_off_min, 90) if x is not None)
                    won_side = (cid == h_id and hs > as_) or (cid == a_id and as_ > hs)
                    rating = round(min(9.8, 6.85 + g_cnt * 0.85 + a_cnt * 0.45 + (0.3 if won_side else 0.0)), 2)

                    if has_real_detail:
                        acc = player_perf_acc[pid]
                        acc["games"] += 1
                        acc["minutes"] += mins_played
                        acc["rating_sum"] += rating

                    pos_tr, pos_grp = _map_pos(p_pos)
                    if pos_grp == "GK" and cid not in match_gk_ids:
                        match_gk_ids[cid] = pid

                    row_nodes.append({
                        "playerId": pid,
                        "name": p_obj["name"],
                        **({"photoUrl": photo_map[pid]} if pid in photo_map else {}),
                        "shirtNumber": p_num or p_obj["shirtNumber"],
                        "position": pos_tr,
                        "matchRating": rating,
                        "goals": g_cnt,
                        "assists": a_cnt,
                        "yellowCard": yc,
                        "redCard": rc,
                        **({"substitutedMinute": sub_min} if sub_min else {}),
                    })
                    box_score.append({
                        "playerId": pid,
                        "playerName": p_obj["name"],
                        "clubId": cid,
                        "clubName": cname,
                        "position": pos_tr,
                        "minutesPlayed": mins_played,
                        "goals": g_cnt,
                        "assists": a_cnt,
                        "shots": g_cnt + (0 if pos_tr == "Kaleci" else 1),
                        "xG": round(g_cnt * 0.42 + (0 if pos_tr == "Kaleci" else 0.12), 2),
                        "xA": round(a_cnt * 0.35 + (0 if pos_tr == "Kaleci" else 0.08), 2),
                        "keyPasses": a_cnt + (0 if pos_tr == "Kaleci" else 1),
                        "passAccuracy": 81.5,
                        "tacklesWon": 2,
                        "matchRating": rating,
                    })
                if row_nodes:
                    matrix.append(row_nodes)

            # Include substitutes who entered the match in box_score & season player minutes
            for in_p, in_min in sub_in_records.get(cid, []):
                pid = in_p["id"]
                if pid in seen_in_box:
                    continue
                seen_in_box.add(pid)
                mins_played = max(1, 90 - in_min)
                g_cnt = scorer_counts.get(pid, 0)
                a_cnt = assist_counts.get(pid, 0)
                rating = round(min(9.5, 6.55 + g_cnt * 0.8 + a_cnt * 0.45), 2)
                if has_real_detail:
                    acc = player_perf_acc[pid]
                    acc["games"] += 1
                    acc["minutes"] += mins_played
                    acc["rating_sum"] += rating
                box_score.append({
                    "playerId": pid,
                    "playerName": in_p["name"],
                    "clubId": cid,
                    "clubName": cname,
                    "position": in_p["positionMain"],
                    "minutesPlayed": mins_played,
                    "goals": g_cnt,
                    "assists": a_cnt,
                    "shots": g_cnt,
                    "xG": round(g_cnt * 0.38, 2),
                    "xA": round(a_cnt * 0.32, 2),
                    "keyPasses": a_cnt,
                    "passAccuracy": 79.0,
                    "tacklesWon": 1,
                    "matchRating": rating,
                })
            return formation, matrix

        h_form, h_matrix = build_side("homeTeam", h_id, h_club["name"])
        a_form, a_matrix = build_side("awayTeam", a_id, a_club["name"])

        # Stats
        raw_stats_list = (dm.get("statistics") or []) if dm else []
        home_stats_map: dict[str, Any] = {}
        away_stats_map: dict[str, Any] = {}
        for blk in raw_stats_list:
            b_name = str((blk.get("team") or {}).get("name") or "")
            b_cid = resolve_club_id(b_name, clubs_by_norm)
            target_map = home_stats_map if b_cid == h_id else away_stats_map
            for s_item in blk.get("statistics") or []:
                target_map[str(s_item.get("displayName") or "")] = s_item.get("value", 0)

        gold_stats: list[dict[str, Any]] = []
        if home_stats_map or away_stats_map:
            for api_disp, (s_key, tr_label, s_cat, unit) in STAT_META_BY_NAME.items():
                hv = home_stats_map.get(api_disp, 0)
                av = away_stats_map.get(api_disp, 0)
                h_num = float(hv or 0)
                a_num = float(av or 0)
                if unit == "%":
                    if h_num <= 1 and a_num <= 1 and (h_num > 0 or a_num > 0):
                        h_num = round(h_num * 100, 1)
                        a_num = round(a_num * 100, 1)
                    h_str = f"%{int(round(h_num))}" if h_num == int(h_num) else f"%{h_num}"
                    a_str = f"%{int(round(a_num))}" if a_num == int(a_num) else f"%{a_num}"
                else:
                    h_str = int(h_num) if h_num == int(h_num) else round(h_num, 2)
                    a_str = int(a_num) if a_num == int(a_num) else round(a_num, 2)
                gold_stats.append({
                    "key": s_key,
                    "label": tr_label,
                    "category": s_cat,
                    "homeValue": h_str,
                    "awayValue": a_str,
                    "homeNumeric": h_num,
                    "awayNumeric": a_num,
                    **({"unit": unit} if unit else {}),
                })
        else:
            gold_stats = [
                {"key": "expected_goals", "label": "Gol Beklentisi (xG)", "category": "Hücum & xG", "homeValue": round(hs * 0.78 + 0.3, 2), "awayValue": round(as_ * 0.78 + 0.3, 2), "homeNumeric": round(hs * 0.78 + 0.3, 2), "awayNumeric": round(as_ * 0.78 + 0.3, 2)},
                {"key": "possession", "label": "Topla Oynama (%)", "category": "Genel & Topla Oynama", "homeValue": "%52", "awayValue": "%48", "homeNumeric": 52, "awayNumeric": 48, "unit": "%"},
            ]

        # Shots
        gold_shots: list[dict[str, Any]] = []
        if dm:
            for side_key, cid, cname in (("homeTeam", h_id, h_club["name"]), ("awayTeam", a_id, a_club["name"])):
                allow_sh_create = cid not in clubs_with_real_lineups
                for sh_idx, sh in enumerate((dm.get(side_key) or {}).get("shots") or []):
                    sh_raw_name = _fix_mojibake(str(sh.get("playerName") or "").strip())
                    if not sh_raw_name or sh_raw_name.lower() == "oyuncu":
                        continue
                    p_obj = register_real_player(
                        None,
                        sh_raw_name,
                        cid,
                        "Forward",
                        9,
                        allow_create=allow_sh_create,
                    )
                    if p_obj["id"] not in real_players_by_id:
                        continue
                    outcome = str(sh.get("outcome") or "Missed")
                    min_clean = int(re.sub(r"[^0-9]", "", str(sh.get("time") or "45").split("+")[0]) or 45)
                    player_perf_acc[p_obj["id"]]["shots"] += 1
                    gold_shots.append({
                        "id": f"{gold_id}-sh-{cid}-{sh_idx}",
                        "minute": min_clean,
                        "clubId": cid,
                        "playerId": p_obj["id"],
                        "playerName": p_obj["name"],
                        "xG": 0.34 if outcome == "Goal" else 0.11,
                        "psxG": 0.68 if outcome == "Goal" else (0.24 if outcome == "Saved" else 0),
                        "goalTarget": _normalize_goal_target(sh.get("goalTarget"), outcome),
                        "outcome": outcome if outcome in ("Goal", "Saved", "Blocked", "Missed") else "Missed",
                        "bodyPart": "Sağ Ayak",
                        "distanceMeters": 14,
                    })

        # Predictions
        preds = (dm.get("predictions") or {}) if dm else {}
        pre_list = preds.get("prematch") or []
        last_pre = pre_list[-1]["probabilities"] if pre_list else {"home": "42%", "draw": "26%", "away": "32%"}
        p_h = _parse_pct(last_pre.get("home"))
        p_d = _parse_pct(last_pre.get("draw"))
        p_a = max(1, 100 - p_h - p_d)
        actual = "1" if hs > as_ else "X" if hs == as_ else "2"
        p_pick = "1" if p_h >= p_d and p_h >= p_a else "2" if p_a >= p_h and p_a >= p_d else "X"
        ovec = (1, 0, 0) if actual == "1" else (0, 1, 0) if actual == "X" else (0, 0, 1)
        brier_p = round((((p_h / 100) - ovec[0]) ** 2 + ((p_d / 100) - ovec[1]) ** 2 + ((p_a / 100) - ovec[2]) ** 2) / 3, 2)

        live_raw = preds.get("live") or []
        live_probs: list[dict[str, Any]] = []
        if live_raw:
            step = max(1, round(90 / max(1, len(live_raw))))
            for idx, lp in enumerate(live_raw):
                pr = lp.get("probabilities") or {}
                live_probs.append({
                    "minute": min(90, idx * step),
                    "homeWin": _parse_pct(pr.get("home")),
                    "draw": _parse_pct(pr.get("draw")),
                    "awayWin": _parse_pct(pr.get("away")),
                })
            live_probs[-1]["minute"] = 90
        else:
            live_probs = [
                {"minute": 0, "homeWin": p_h, "draw": p_d, "awayWin": p_a},
                {"minute": 90, "homeWin": 100 if actual == "1" else 0, "draw": 100 if actual == "X" else 0, "awayWin": 100 if actual == "2" else 0},
            ]

        raw_pair_clips = hl_clips_by_api_id.get(api_mid) or hl_clips_by_pair.get((h_id, a_id)) or []
        tr_open_hl_clips: list[dict[str, str]] = []
        for clip in raw_pair_clips:
            vid = extract_youtube_id(clip["embedUrl"])
            if vid and yt_tr_checks.get(vid) is False:
                continue
            tr_open_hl_clips.append(clip)

        cached_hl = cached_hl_by_gold_id.get(gold_id)
        merged_clips: list[dict[str, str]] = []
        seen_clip_urls: set[str] = set()
        if isinstance(cached_hl, dict):
            for c_item in cached_hl.get("clips") or []:
                eu = str(c_item.get("embedUrl") or "")
                if eu and eu not in seen_clip_urls:
                    seen_clip_urls.add(eu)
                    merged_clips.append({
                        "title": str(c_item.get("title") or "Maç Özeti"),
                        "embedUrl": eu,
                        "category": str(c_item.get("category") or "match-highlights"),
                    })
        for c_item in sorted(tr_open_hl_clips, key=lambda x: 0 if x["category"] == "match-highlights" else 1):
            eu = c_item["embedUrl"]
            if eu and eu not in seen_clip_urls:
                seen_clip_urls.add(eu)
                merged_clips.append({
                    "title": c_item["title"],
                    "embedUrl": eu,
                    "category": c_item["category"],
                })

        merged_clips.sort(key=lambda x: 0 if x["category"] == "match-highlights" else 1)

        if merged_clips:
            hl_embed = (cached_hl.get("embedUrl") if isinstance(cached_hl, dict) else None) or merged_clips[0]["embedUrl"]
            main_vid = extract_youtube_id(hl_embed)
            hl_img = (
                (cached_hl.get("imgUrl") if isinstance(cached_hl, dict) else None)
                or (f"https://i.ytimg.com/vi/{main_vid}/hqdefault.jpg" if main_vid else "")
            )
            updated_highlights += 1
        else:
            hl_embed = ""
            hl_img = ""

        venue_obj = (dm.get("venue") or {}) if dm else {}
        ref_obj = (dm.get("referee") or {}) if dm else {}
        fc_obj = (dm.get("forecast") or {}) if dm else {}
        cap_str = str(venue_obj.get("capacity") or "18000")
        cap_int = int(re.sub(r"[^0-9]", "", cap_str) or 18000)
        h_xg = float(home_stats_map.get("Expected Goals") or round(hs * 0.78 + 0.35, 2))
        a_xg = float(away_stats_map.get("Expected Goals") or round(as_ * 0.78 + 0.35, 2))

        if has_real_detail and (home_stats_map or away_stats_map):
            h_poss = float(home_stats_map.get("Possession") or 0.5)
            a_poss = float(away_stats_map.get("Possession") or 0.5)
            h_poss = h_poss * 100 if h_poss <= 1 else h_poss
            a_poss = a_poss * 100 if a_poss <= 1 else a_poss

            hd = _club_dna(h_id)
            hd["matches"] += 1
            hd["xg_for"] += h_xg
            hd["xg_against"] += a_xg
            hd["goals_for"] += hs
            hd["poss_sum"] += h_poss
            hd["final_third_sum"] += float(home_stats_map.get("Passes Into Final Third") or 0)
            hd["total_pass_sum"] += float(home_stats_map.get("Total passes") or 1)
            hd["long_pass_sum"] += float(home_stats_map.get("Long Passes") or 0)
            hd["tackles_sum"] += float(home_stats_map.get("Tackles") or 0)
            hd["interceptions_sum"] += float(home_stats_map.get("Interceptions") or 0)

            ad = _club_dna(a_id)
            ad["matches"] += 1
            ad["xg_for"] += a_xg
            ad["xg_against"] += h_xg
            ad["goals_for"] += as_
            ad["poss_sum"] += a_poss
            ad["final_third_sum"] += float(away_stats_map.get("Passes Into Final Third") or 0)
            ad["total_pass_sum"] += float(away_stats_map.get("Total passes") or 1)
            ad["long_pass_sum"] += float(away_stats_map.get("Long Passes") or 0)
            ad["tackles_sum"] += float(away_stats_map.get("Tackles") or 0)
            ad["interceptions_sum"] += float(away_stats_map.get("Interceptions") or 0)

            for gk_cid, conceded, opp_xg, saves_key in (
                (h_id, as_, a_xg, home_stats_map.get("Goalkeeper saves")),
                (a_id, hs, h_xg, away_stats_map.get("Goalkeeper saves")),
            ):
                gk_pid = match_gk_ids.get(gk_cid)
                if gk_pid:
                    gka = gk_acc.setdefault(gk_pid, {"matches": 0, "saves": 0, "conceded": 0, "opp_xg": 0.0, "clean_sheets": 0})
                    gka["matches"] += 1
                    gka["saves"] += int(float(saves_key or 0))
                    gka["conceded"] += conceded
                    gka["opp_xg"] += opp_xg
                    if conceded == 0:
                        gka["clean_sheets"] += 1

        real_matches_gold.append({
            "id": gold_id,
            "round": round_num,
            "season": "2026/27",
            "date": date_str,
            "kickoffTime": time_str,
            "venue": venue_obj.get("name") or h_club["stadium"],
            "attendance": cap_int,
            "referee": ref_obj.get("name") or "TFF Hakem Kurulu",
            "forecast": f"{fc_obj.get('temperature', '14°C')} · {fc_obj.get('status', 'Açık')}".strip(" ·"),
            "homeClubId": h_id,
            "homeClubName": h_club["name"],
            "awayClubId": a_id,
            "awayClubName": a_club["name"],
            "homeScore": hs,
            "awayScore": as_,
            "halfTimeScore": f"{ht_home_goals}-{ht_away_goals}" if has_real_detail else f"{hs // 2}-{as_ // 2}",
            "stats": gold_stats,
            "initialLineup": {
                "homeFormation": h_form,
                "awayFormation": a_form,
                "home": h_matrix,
                "away": a_matrix,
            },
            "boxScore": box_score,
            "events": gold_events,
            "shots": gold_shots,
            "prematch": {
                "poisson": {
                    "homeWinProb": p_h,
                    "drawProb": p_d,
                    "awayWinProb": p_a,
                    "expectedHomeGoals": round(h_xg, 2),
                    "expectedAwayGoals": round(a_xg, 2),
                    "mostLikelyScore": f"{hs}-{as_}",
                    "over25Prob": min(88, max(35, int((h_xg + a_xg) * 25))),
                },
                "api": {
                    "homeWinProb": p_h,
                    "drawProb": p_d,
                    "awayWinProb": p_a,
                    "provider": "Highlightly Prematch ML Modeli",
                },
                "actualOutcome": actual,
                "poissonCorrect": p_pick == actual,
                "apiCorrect": p_pick == actual,
                "poissonBrierScore": brier_p,
                "apiBrierScore": brier_p,
            },
            "liveProbabilities": live_probs,
            "highlightEmbedUrl": hl_embed,
            "highlightImgUrl": hl_img,
            "highlightClips": merged_clips,
        })

    # 5) Finalize players.json & clubs.json squads (real Highlightly squads replace fake seed squads!)
    final_players: list[dict[str, Any]] = []
    for p in real_players_by_id.values():
        acc = player_perf_acc.get(p["id"], {})
        games = max(1, acc.get("games", 0))
        mins = max(90, acc.get("minutes", 0))
        goals = acc.get("goals", 0)
        assists = acc.get("assists", 0)
        avg_r = round(acc["rating_sum"] / acc["games"], 2) if acc.get("games", 0) > 0 else 7.05
        p["gamesPlayed"] = acc.get("games", 1)
        p["minutesPlayed"] = acc.get("minutes", 90)
        p["goals"] = goals
        p["assists"] = assists
        p["yellowCards"] = acc.get("yc", 0)
        p["redCards"] = acc.get("rc", 0)
        p["xG"] = round(goals * 0.78 + acc.get("shots", 0) * 0.08, 2)
        p["xA"] = round(assists * 0.72 + games * 0.12, 2)
        p["avgMatchRating"] = avg_r
        p["per90Goals"] = round(goals * (90 / mins), 2)
        p["per90Assists"] = round(assists * (90 / mins), 2)
        p["keyPassesPer90"] = round(0.7 + assists * 0.4, 2)
        if p["positionGroup"] == "GK" and p["id"] in gk_acc:
            gka = gk_acc[p["id"]]
            total_faced = max(1, gka["saves"] + gka["conceded"])
            p["cleanSheets"] = gka["clean_sheets"]
            p["savePercentage"] = round((gka["saves"] / total_faced) * 100, 1)
            p["PSxG_plus_minus"] = round(gka["opp_xg"] - gka["conceded"], 1)
        p["perClub"] = [
            {
                "clubId": p["clubId"],
                "clubName": p["clubName"],
                "competition": "Süper Lig",
                "seasonRange": "2026/27",
                "games": p["gamesPlayed"],
                "minutes": p["minutesPlayed"],
                "goals": goals,
                "assists": assists,
                "avgRating": avg_r,
            }
        ]
        if p["id"] in player_profiles_by_id:
            _apply_real_player_profile(p, player_profiles_by_id[p["id"]], clubs_by_norm)
        final_players.append(p)

    # Keep seed players ONLY for Super Lig clubs that don't have a real lineup downloaded yet
    for sp in seed_players_list:
        cid = sp["clubId"]
        if not str(sp.get("id", "")).startswith("hl-") and cid not in clubs_with_real_lineups and cid in active_super_lig_ids:
            final_players.append(sp)

    # Apply resolved Wikipedia / Highlightly player portraits (migrating legacy slug keys to canonical IDs)
    cache_photos = media_cache.setdefault("player_photos", {})
    cache_dirty = False
    for p in final_players:
        p_photo = _resolve_photo_url(p)
        if p_photo:
            p["photoUrl"] = p_photo
            if cache_photos.get(p["id"]) != p_photo:
                cache_photos[p["id"]] = p_photo
                cache_dirty = True
        else:
            p.pop("photoUrl", None)

    valid_player_ids = {p["id"] for p in final_players}
    stale_keys = [k for k in list(cache_photos.keys()) if not k.startswith("hl-") and k not in valid_player_ids]
    if stale_keys:
        for sk in stale_keys:
            del cache_photos[sk]
        cache_dirty = True
    if cache_dirty:
        save_media_cache(media_cache)

    # Apply real PNG team logos globally across clubs and standings
    for c in clubs_list:
        if c["id"] in club_logos:
            c["logo"] = club_logos[c["id"]]
    for row in standings_doc.get("standings", []):
        if row.get("clubId") in club_logos:
            row["logo"] = club_logos[row["clubId"]]

    # Rebuild squads & fixtures for clubs
    for c in clubs_list:
        c["fixtures"] = []
        if c["id"] in clubs_with_real_lineups or c.get("isSuperLig"):
            club_players = [p for p in final_players if p["clubId"] == c["id"]]
            c["squad"] = sorted(
                [
                    {
                        "playerId": p["id"],
                        "name": p["name"],
                        **({"photoUrl": p["photoUrl"]} if p.get("photoUrl") else {}),
                        "shirtNumber": p["shirtNumber"],
                        "positionMain": p["positionMain"],
                        "positionGroup": p["positionGroup"],
                        "age": p["age"],
                        "citizenship": p["citizenship"],
                        "foot": p["foot"],
                        "contractExpiry": p["contractExpiry"],
                        "currentMarketValueEur": p["currentMarketValueEur"],
                        "avgMatchRating": p["avgMatchRating"],
                        "gamesPlayed": p["gamesPlayed"],
                        "goals": p["goals"],
                        "assists": p["assists"],
                        "xG": p["xG"],
                        "injuryRisk": p["injuryRisk"],
                        "missedGamesTotal": (
                            sum(r["missedGames"] for r in p["injuries"]["anatomyRegions"].values())
                            + sum(s["missedGames"] for s in p["injuries"]["systemicRecords"])
                        ),
                    }
                    for p in club_players
                ],
                key=lambda m: m["currentMarketValueEur"],
                reverse=True,
            )
            if club_players:
                c["totalMarketValueEur"] = sum(
                    p["currentMarketValueEur"] for p in club_players if p["currentMarketValueEur"] > 0
                )
                ages_known = [p["age"] for p in club_players if p["age"] > 0]
                c["averageAge"] = round(sum(ages_known) / len(ages_known), 1) if ages_known else 0
            dna = club_dna_acc.get(c["id"])
            if dna and dna["matches"] > 0:
                mcnt = dna["matches"]
                poss = round(dna["poss_sum"] / mcnt, 1)
                xg_f_avg = dna["xg_for"] / mcnt
                xg_a_avg = dna["xg_against"] / mcnt
                total_p = max(1.0, dna["total_pass_sum"])
                f3_ratio = min(89.0, max(35.0, round((dna["final_third_sum"] / total_p) * 300, 1)))
                long_ratio = dna["long_pass_sum"] / total_p
                def_actions = (dna["tackles_sum"] + dna["interceptions_sum"]) / mcnt
                ppda_val = round(max(6.2, min(14.8, 14.2 - def_actions * 0.22)), 1)
                # Scale xG to season games played for consistency with goalsFor
                played_season = next((r["overall"]["played"] for r in standings_doc["standings"] if r["clubId"] == c["id"]), mcnt)
                c["xGFor"] = round(xg_f_avg * played_season, 1)
                c["xGAgainst"] = round(xg_a_avg * played_season, 1)
                c["goalsMinusXg"] = round(dna["goals_for"] - dna["xg_for"], 1)
                c["possessionAvg"] = poss
                c["finalThirdPassIntensity"] = f3_ratio
                c["ppda"] = ppda_val
                c["playStyle"] = (
                    "Dikine Baskı" if poss >= 53.0 and ppda_val <= 9.8
                    else "Uzun Top / Geçiş" if long_ratio >= 0.14 or poss < 47.0
                    else "Kısır Pas"
                )
        else:
            c["squad"] = []

    # Attach real fixtures & last-5 recentMatches from all 99 real finished matches
    if real_matches_gold:
        latest_round = max(m["round"] for m in real_matches_gold)
        standings_doc["currentRound"] = latest_round

        for m in real_matches_gold:
            hc = clubs_by_id.get(m["homeClubId"])
            ac = clubs_by_id.get(m["awayClubId"])
            h_res = "W" if m["homeScore"] > m["awayScore"] else "D" if m["homeScore"] == m["awayScore"] else "L"
            a_res = "W" if m["awayScore"] > m["homeScore"] else "D" if m["homeScore"] == m["awayScore"] else "L"
            if hc:
                hc["fixtures"].append({
                    "matchId": m["id"], "round": m["round"], "date": m["date"], "isHome": True,
                    "opponentClubId": m["awayClubId"], "opponentName": m["awayClubName"],
                    "opponentShortName": ac["shortName"] if ac else m["awayClubId"][:3].upper(),
                    "homeScore": m["homeScore"], "awayScore": m["awayScore"], "result": h_res,
                })
            if ac:
                ac["fixtures"].append({
                    "matchId": m["id"], "round": m["round"], "date": m["date"], "isHome": False,
                    "opponentClubId": m["homeClubId"], "opponentName": m["homeClubName"],
                    "opponentShortName": hc["shortName"] if hc else m["homeClubId"][:3].upper(),
                    "homeScore": m["homeScore"], "awayScore": m["awayScore"], "result": a_res,
                })

        for row in standings_doc["standings"]:
            cid = row["clubId"]
            club_fx = (clubs_by_id.get(cid) or {}).get("fixtures", [])[:5]
            row["form"] = [fx["result"] for fx in club_fx]
            row["recentMatches"] = [
                {
                    "matchId": fx["matchId"],
                    "result": fx["result"],
                    "opponentClubId": fx["opponentClubId"],
                    "opponentName": fx["opponentName"],
                    "score": f"{fx['homeScore']}-{fx['awayScore']}",
                    "isHome": fx["isHome"],
                }
                for fx in club_fx
            ]

    # Keep only valid clubIds for links while preserving foreign transfer & market history
    valid_club_ids = {c["id"] for c in clubs_list}
    for p in final_players:
        for tr in p.get("transfers", []):
            if tr.get("fromClubId") not in valid_club_ids:
                tr["fromClubId"] = ""
            if tr.get("toClubId") not in valid_club_ids:
                tr["toClubId"] = ""
        for rum in p.get("rumours", []):
            if rum.get("clubId") not in valid_club_ids:
                rum["clubId"] = ""
        for pt in p.get("marketValueHistory", []):
            if pt.get("clubId") not in valid_club_ids:
                pt["clubId"] = ""
        p["perClub"] = [pc for pc in p.get("perClub", []) if pc["clubId"] in valid_club_ids]

    standings_path.write_text(json.dumps(standings_doc, indent=2, ensure_ascii=False), encoding="utf-8")
    clubs_path.write_text(json.dumps(clubs_list, indent=2, ensure_ascii=False), encoding="utf-8")
    players_path.write_text(json.dumps(final_players, indent=2, ensure_ascii=False), encoding="utf-8")
    matches_path.write_text(json.dumps(real_matches_gold, indent=2, ensure_ascii=False), encoding="utf-8")

    # 6) Build sync-status.json for frontend transparency & live status page
    tsi_tz = timezone(timedelta(hours=3))
    now_tsi = datetime.now(tsi_tz)
    standings_doc["updatedAt"] = now_tsi.isoformat()
    standings_path.write_text(json.dumps(standings_doc, indent=2, ensure_ascii=False), encoding="utf-8")

    rounds_map: dict[int, list[dict[str, Any]]] = {}
    detailed_ids: set[str] = set()
    real_highlights_count = 0

    for m in real_matches_gold:
        has_lineup = bool(m["initialLineup"]["home"]) and bool(m["initialLineup"]["away"])
        has_full = len(m["stats"]) >= 10 and has_lineup
        has_hl = bool(m.get("highlightEmbedUrl")) and "jfKfPfyJRdk" not in m["highlightEmbedUrl"]
        if has_full:
            detailed_ids.add(m["id"])
        if has_hl:
            real_highlights_count += 1
        rounds_map.setdefault(m["round"], []).append({
            "id": m["id"],
            "date": m["date"],
            "homeClubId": m["homeClubId"],
            "homeClubName": m["homeClubName"],
            "awayClubId": m["awayClubId"],
            "awayClubName": m["awayClubName"],
            "homeScore": m["homeScore"],
            "awayScore": m["awayScore"],
            "hasFullDetails": has_full,
            "hasLineup": has_lineup,
            "hasHighlight": has_hl,
            "statsCount": len(m["stats"]),
            "shotsCount": len(m["shots"]),
            "eventsCount": len(m["events"]),
        })

    round_summaries = []
    for r_num in sorted(rounds_map.keys(), reverse=True):
        m_items = rounds_map[r_num]
        round_summaries.append({
            "round": r_num,
            "totalMatches": len(m_items),
            "detailedMatches": sum(1 for x in m_items if x["hasFullDetails"]),
            "matches": m_items,
        })

    club_coverage = []
    for row in standings_doc["standings"]:
        cid = row["clubId"]
        c_obj = clubs_by_id.get(cid)
        c_matches = [m for m in real_matches_gold if m["homeClubId"] == cid or m["awayClubId"] == cid]
        club_coverage.append({
            "clubId": cid,
            "clubName": c_obj["name"] if c_obj else row["clubName"],
            "squadCount": len(c_obj["squad"]) if c_obj else 0,
            "hasRealSquad": cid in clubs_with_real_lineups,
            "playedMatches": len(c_matches),
            "detailedMatches": sum(1 for m in c_matches if m["id"] in detailed_ids),
        })

    total_finished = len(real_matches_gold)
    detailed_cnt = len(detailed_ids)
    bronze_files_cnt = (
        len([p for p in BRONZE_DIR.rglob("*.json") if p.name != "manifest.json"])
        if BRONZE_DIR.exists()
        else 0
    )

    # Yaklaşan / henüz tamamlanmamış maçların başlama saatlerini çıkar (maç sonrası tetikleyici için)
    upcoming_by_id: dict[int, dict[str, Any]] = {}
    matches_bronze_dir = BRONZE_DIR / "matches"
    if matches_bronze_dir.exists():
        for fpath in sorted(matches_bronze_dir.glob("*.json")):
            try:
                raw_m = json.loads(fpath.read_text(encoding="utf-8"))
            except Exception:
                continue
            for m in unwrap_data(raw_m):
                if not isinstance(m, dict) or m.get("id") is None or not m.get("date"):
                    continue
                if (m.get("state") or {}).get("description") == "Finished":
                    continue
                upcoming_by_id[int(m["id"])] = m

    upcoming_sorted = sorted(upcoming_by_id.values(), key=lambda m: str(m.get("date") or ""))
    upcoming_kickoffs = [
        {
            "id": int(m["id"]),
            "dateUtc": str(m.get("date") or ""),
            "home": str((m.get("homeTeam") or {}).get("name") or ""),
            "away": str((m.get("awayTeam") or {}).get("name") or ""),
            "state": str((m.get("state") or {}).get("description") or ""),
        }
        for m in upcoming_sorted[:25]
    ]

    sync_status_doc = {
        "lastSyncedAt": now_tsi.strftime("%d.%m.%Y %H:%M TSİ"),
        "lastSyncedIso": now_tsi.isoformat(),
        "season": standings_doc.get("season", "2026/27"),
        "currentRound": standings_doc.get("currentRound", 11),
        "totalFinishedMatches": total_finished,
        "detailedMatchesCount": detailed_cnt,
        "pendingMatchesCount": max(0, total_finished - detailed_cnt),
        "completionPercent": round((detailed_cnt / total_finished) * 100, 1) if total_finished else 0.0,
        "highlightsCount": real_highlights_count,
        "clubsWithRealSquads": len(clubs_with_real_lineups),
        "totalPlayersCount": len(final_players),
        "bronzeFilesCount": bronze_files_cnt,
        "upcomingKickoffs": upcoming_kickoffs,
        "rounds": round_summaries,
        "clubCoverage": club_coverage,
    }
    sync_status_path = GOLD_DIR / "sync-status.json"
    sync_status_path.write_text(json.dumps(sync_status_doc, indent=2, ensure_ascii=False), encoding="utf-8")

    # 7) Push synthesized Gold datasets to Turso if configured
    turso = TursoClient()
    if turso.enabled:
        try:
            for gname, gpath in (
                ("standings", standings_path),
                ("clubs", clubs_path),
                ("players", players_path),
                ("matches", matches_path),
                ("sync-status", sync_status_path),
            ):
                turso.upsert_gold(gname, gpath.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"[Turso Gold Uyarısı] {exc}")

    return {
        "standings_rows": updated_standings,
        "highlights": updated_highlights,
        "total_real_matches": len(real_matches_gold),
        "detailed_matches": detailed_cnt,
        "real_squad_clubs": len(clubs_with_real_lineups),
        "total_players": len(final_players),
    }


def cmd_status(client: HighlightlyClient) -> None:
    statuses = client.get_key_statuses()
    print("=== Highlightly Çoklu API Anahtarı Kota Durumu ===")
    print(f"Base URL     : {client.base_url}")
    print(f"Auth Modu    : {client.auth_mode}")
    print(f"Kayıtlı Key  : {len(statuses)}")
    if not statuses:
        print("Uyarı        : backend/.env içinde henüz aktif API anahtarı tanımlı değil.")
    else:
        for s in statuses:
            state = "DOLU" if s.exhausted else "AKTİF"
            print(
                f"  #{s.index:<2} {s.fingerprint} -> Kullanılan: {s.used}/{s.safe_limit} "
                f"(Limit: {s.daily_limit}) | Kalan Güvenli: {s.remaining_safe} [{state}]"
            )
    print(f"Toplam Kalan Güvenli Kota (Bugün): {client.total_remaining_safe_quota()}")

    bronze_files = list(BRONZE_DIR.rglob("*.json")) if BRONZE_DIR.exists() else []
    print(f"Bronze Önbellek Dosyası           : {len(bronze_files)} JSON")


def cmd_sync(client: HighlightlyClient, season: str, league_id_override: str | None, run_build: bool) -> None:
    country = os.environ.get("SUPER_LIG_COUNTRY", "Turkey")
    league_hint = os.environ.get("SUPER_LIG_LEAGUE_NAME", "Süper Lig")

    if not client.keys:
        print("Hata: backend/.env içinde geçerli HIGHLIGHTLY_API_KEY_* tanımlanmamış.")
        sys.exit(1)

    league_id: int | str | None = league_id_override
    detected_season: str | None = None
    if not league_id:
        league_id, detected_season = find_super_lig_league_info(client, country, league_hint)

    active_season = detected_season or season

    if not league_id:
        print("Süper Lig leagueId bulunamadı.")
    else:
        print(f"[1/4] Süper Lig bulundu: leagueId={league_id}, season={active_season} (URL: {client.base_url}, auth: {client.auth_mode})")

        client.get(
            "/standings",
            params={"leagueId": league_id, "season": active_season},
            cache_group="standings",
            cache_name=f"standings_{league_id}_{active_season}",
        )

        all_api_matches: list[dict[str, Any]] = []
        page0 = client.get(
            "/matches",
            params={"leagueId": league_id, "season": active_season},
            cache_group="matches",
            cache_name=f"matches_{league_id}_{active_season}",
        )
        all_api_matches.extend(x for x in unwrap_data(page0) if isinstance(x, dict))

        total_count = 0
        if isinstance(page0, dict) and isinstance(page0.get("pagination"), dict):
            total_count = int(page0["pagination"].get("totalCount") or 0)

        for offset in (100, 200):
            if client.budget_stopped or (total_count and offset >= total_count):
                break
            page_n = client.get(
                "/matches",
                params={"leagueId": league_id, "season": active_season, "offset": offset},
                cache_group="matches",
                cache_name=f"matches_{league_id}_{active_season}_offset{offset}",
            )
            all_api_matches.extend(x for x in unwrap_data(page_n) if isinstance(x, dict))

        client.get(
            "/highlights",
            params={"leagueId": league_id, "season": active_season},
            cache_group="highlights",
            cache_name=f"highlights_{league_id}_{active_season}",
        )

        finished_matches = [
            m
            for m in all_api_matches
            if isinstance(m.get("state"), dict) and m["state"].get("description") == "Finished"
        ]
        finished_matches.sort(key=lambda m: str(m.get("date") or ""), reverse=True)
        print(f"[2/4] Toplam fikstür: {len(all_api_matches)}, Oynanmış (Finished) maç: {len(finished_matches)}")

        for m in finished_matches:
            if client.budget_stopped:
                break
            mid = m.get("id")
            if not mid:
                continue
            client.get(f"/matches/{mid}", cache_group="match_details", cache_name=f"match_{mid}")
            if client.budget_stopped:
                break
            client.get(f"/lineups/{mid}", cache_group="lineups", cache_name=f"lineup_{mid}")

    stats = merge_bronze_into_gold()
    print(
        f"[3/4] Özet -> Bu tur atılan API isteği: {client.requests_made_this_run}, "
        f"Önbellekten okunan: {client.cache_hits_this_run}, "
        f"Gold birleştirme: {stats}"
    )
    if client.budget_stopped:
        print(
            f"[Bilgi] Güvenli çalıştırma bütçesi ({client.run_budget} istek) dolduğu için duruldu. "
            "Kaldığınız yerden devam etmek için komutu tekrar çalıştırabilirsiniz."
        )

    if run_build:
        print("[4/4] web/ statik HTML derlemesi (npm run build) başlatılıyor...")
        subprocess.run("npm run build", cwd=WEB_DIR, shell=True, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="SiperLig Highlightly Veri Çekici")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="Kayıtlı API anahtarlarını ve kalan kotayı göster")

    sync_p = sub.add_parser("sync", help="Kota korumalı olarak verileri kademeli çek ve birleştir")
    sync_p.add_argument("--budget", type=int, default=None, help="Bu çalıştırmada maksimum canlı API isteği")
    sync_p.add_argument("--season", type=str, default=None, help="Sezon yılı (örn. 2026)")
    sync_p.add_argument("--league-id", type=str, default=None, help="Süper Lig ID'si biliniyorsa doğrudan verin")
    sync_p.add_argument("--build", action="store_true", help="Senkronizasyon sonrası web/ npm run build çalıştır")

    sub.add_parser("merge", help="İstek atmadan sadece Bronze önbelleğini Gold JSON'a aktar")

    args = parser.parse_args()
    client = HighlightlyClient(max_requests_per_run=getattr(args, "budget", None))

    if args.command == "status":
        cmd_status(client)
    elif args.command == "merge":
        res = merge_bronze_into_gold()
        print(f"Bronze -> Gold birleştirme tamamlandı: {res}")
    elif args.command == "sync":
        season = args.season or os.environ.get("SUPER_LIG_SEASON", "2026")
        cmd_sync(client, season=season, league_id_override=args.league_id, run_build=args.build)


if __name__ == "__main__":
    main()
