"""Kalan gerçek Süper Lig maçlarını kota korumalı olarak yavaş yavaş indiren ve siteyi güncelleyen toplayıcı."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any

from highlightly_client import BRONZE_DIR, HighlightlyClient
from media_enrichment import load_media_cache, save_media_cache
from sync_highlightly import (
    GOLD_DIR,
    WEB_DIR,
    find_super_lig_league_info,
    merge_bronze_into_gold,
    unwrap_data,
)


def list_harvest_progress() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Önbellekteki oynanmış (Finished) maçları indirilenler ve bekleyenler olarak ayırır."""
    matches_dir = BRONZE_DIR / "matches"
    details_dir = BRONZE_DIR / "match_details"
    lineups_dir = BRONZE_DIR / "lineups"

    finished_by_id: dict[int, dict[str, Any]] = {}
    if matches_dir.exists():
        for fpath in sorted(matches_dir.glob("*.json")):
            raw = json.loads(fpath.read_text(encoding="utf-8"))
            for m in unwrap_data(raw):
                if isinstance(m, dict) and m.get("id") is not None:
                    if (m.get("state") or {}).get("description") == "Finished":
                        finished_by_id[int(m["id"])] = m

    sorted_finished = sorted(
        finished_by_id.values(),
        key=lambda m: str(m.get("date") or ""),
        reverse=True,
    )

    completed: list[dict[str, Any]] = []
    pending: list[dict[str, Any]] = []
    for m in sorted_finished:
        mid = int(m["id"])
        has_detail = (details_dir / f"match_{mid}.json").exists()
        has_lineup = (lineups_dir / f"lineup_{mid}.json").exists()
        if has_detail and has_lineup:
            completed.append(m)
        else:
            pending.append(m)

    return completed, pending


def refresh_live_round_feeds(client: HighlightlyClient, season: str) -> None:
    """Zamanlanmış otomatik çalışmada güncel puan durumu, fikstür ve video özetlerini yeniler."""
    country = os.environ.get("SUPER_LIG_COUNTRY", "Turkey")
    league_hint = os.environ.get("SUPER_LIG_LEAGUE_NAME", "Süper Lig")
    league_id, detected_season = find_super_lig_league_info(client, country, league_hint)
    if not league_id:
        return
    active_season = detected_season or season

    client.get(
        "/standings",
        params={"leagueId": league_id, "season": active_season},
        cache_group="standings",
        cache_name=f"standings_{league_id}_{active_season}",
        force_refresh=True,
    )
    page0 = client.get(
        "/matches",
        params={"leagueId": league_id, "season": active_season},
        cache_group="matches",
        cache_name=f"matches_{league_id}_{active_season}",
        force_refresh=True,
    )
    total_count = 0
    if isinstance(page0, dict) and isinstance(page0.get("pagination"), dict):
        total_count = int(page0["pagination"].get("totalCount") or 0)
    for offset in (100, 200):
        if client.budget_stopped or (total_count and offset >= total_count):
            break
        client.get(
            "/matches",
            params={"leagueId": league_id, "season": active_season, "offset": offset},
            cache_group="matches",
            cache_name=f"matches_{league_id}_{active_season}_offset{offset}",
            force_refresh=True,
        )
    client.get(
        "/highlights",
        params={"leagueId": league_id, "season": active_season},
        cache_group="highlights",
        cache_name=f"highlights_{league_id}_{active_season}",
        force_refresh=True,
    )


def ensure_historical_standings(client: HighlightlyClient, league_id: str = "173537") -> None:
    """2023–2025 geçmiş Süper Lig sezonlarının puan durumlarını kalıcı önbelleğe tek seferlik indirir."""
    for yr in ("2023", "2024", "2025"):
        if client.budget_stopped:
            break
        client.get(
            "/standings",
            params={"leagueId": league_id, "season": yr},
            cache_group="standings",
            cache_name=f"standings_{league_id}_{yr}",
        )


def harvest_player_profiles_if_spare_quota(
    client: HighlightlyClient,
    reserve_quota: int = 60,
    ttl_days: int = 7,
    max_missing: int = 180,
    max_refresh: int = 75,
) -> int:
    """Maç rezervi düşüldükten sonra eksik ve süresi (7 gün) dolmuş oyuncu profil ve istatistiklerini çeker."""
    players_path = GOLD_DIR / "players.json"
    if not players_path.exists():
        return 0

    players_gold = json.loads(players_path.read_text(encoding="utf-8"))
    media_cache = load_media_cache()
    players_dir = BRONZE_DIR / "players"
    stats_dir = BRONZE_DIR / "player_stats"
    now_ts = time.time()
    ttl_seconds = ttl_days * 86400

    missing_profiles: list[tuple[int, int, str, int]] = []
    missing_stats: list[tuple[int, int, str, int]] = []
    stale_targets: list[tuple[float, int, str, str, int]] = []

    for p in players_gold:
        pid = str(p.get("id") or "")
        if not pid.startswith("hl-"):
            continue
        raw_id = pid[3:]
        if not raw_id.isdigit():
            continue
        games = int(p.get("gamesPlayed") or 0)
        mv = int(p.get("currentMarketValueEur") or 0)
        hl_pid = int(raw_id)

        pfile = players_dir / f"player_{raw_id}.json"
        if not pfile.exists():
            missing_profiles.append((games, mv, pid, hl_pid))
        elif (now_ts - pfile.stat().st_mtime) > ttl_seconds:
            stale_targets.append((pfile.stat().st_mtime, -games, "profile", pid, hl_pid))

        sfile = stats_dir / f"stats_{raw_id}.json"
        if not sfile.exists():
            missing_stats.append((games, mv, pid, hl_pid))
        elif (now_ts - sfile.stat().st_mtime) > ttl_seconds:
            stale_targets.append((sfile.stat().st_mtime, -games, "stats", pid, hl_pid))

    missing_profiles.sort(reverse=True)
    missing_stats.sort(reverse=True)
    stale_targets.sort()

    fetched = 0
    photos_updated = False

    def _fetch_endpoint(kind: str, pid: str, hl_pid: int, force_refresh: bool) -> bool:
        nonlocal fetched, photos_updated
        if client.budget_stopped or client.total_remaining_safe_quota() <= reserve_quota:
            return False
        if kind == "profile":
            res = client.get(
                f"/players/{hl_pid}",
                cache_group="players",
                cache_name=f"player_{hl_pid}",
                force_refresh=force_refresh,
            )
            fetched += 1
            items = unwrap_data(res)
            if items and isinstance(items[0], dict):
                photo = items[0].get("logo") or items[0].get("photo") or items[0].get("image")
                if isinstance(photo, str) and photo.startswith("http"):
                    media_cache.setdefault("player_photos", {})[pid] = photo
                    photos_updated = True
        else:
            client.get(
                f"/players/{hl_pid}/statistics",
                cache_group="player_stats",
                cache_name=f"stats_{hl_pid}",
                force_refresh=force_refresh,
            )
            fetched += 1
        return True

    # 1) Öncelik: Eksik /players/{id} profilleri, ardından eksik /players/{id}/statistics kayıtları
    missing_queue: list[tuple[str, str, int]] = [
        ("profile", pid, hl_pid) for _, _, pid, hl_pid in missing_profiles
    ] + [
        ("stats", pid, hl_pid) for _, _, pid, hl_pid in missing_stats
    ]
    for kind, pid, hl_pid in missing_queue[:max_missing]:
        if not _fetch_endpoint(kind, pid, hl_pid, force_refresh=False):
            break

    # 2) Öncelik: TTL (7 gün) süresi dolmuş profil ve istatistikler
    if not client.budget_stopped and client.total_remaining_safe_quota() > reserve_quota:
        for _, _, kind, pid, hl_pid in stale_targets[:max_refresh]:
            if not _fetch_endpoint(kind, pid, hl_pid, force_refresh=True):
                break

    if photos_updated:
        save_media_cache(media_cache)
    return fetched


def run_batch(
    batch_budget: int,
    refresh_feeds: bool,
    run_build: bool,
    season: str,
    harvest_profiles: bool = False,
) -> tuple[int, int]:
    client = HighlightlyClient(max_requests_per_run=batch_budget)

    try:
        if refresh_feeds:
            refresh_live_round_feeds(client, season)

        ensure_historical_standings(client)

        completed, pending = list_harvest_progress()
        print(
            f"[AutoHarvester] İlerleme: {len(completed)}/{len(completed) + len(pending)} "
            f"oynanmış maç tamamlandı | Bekleyen: {len(pending)} | Kalan Güvenli Kota: {client.total_remaining_safe_quota()}"
        )

        for m in pending:
            if client.budget_stopped:
                break
            mid = int(m["id"])
            client.get(f"/matches/{mid}", cache_group="match_details", cache_name=f"match_{mid}")
            if client.budget_stopped:
                break
            client.get(f"/lineups/{mid}", cache_group="lineups", cache_name=f"lineup_{mid}")

        if harvest_profiles and not pending and not client.budget_stopped and client.total_remaining_safe_quota() > 60:
            pf_count = harvest_player_profiles_if_spare_quota(client)
            if pf_count > 0:
                print(f"[AutoHarvester] Artan kota ile {pf_count} oyuncu profili (/players) çekildi/yenilendi.")
    except RuntimeError as err:
        print(f"[AutoHarvester] Kota sınırı uyarısı: {err}")

    merge_res = merge_bronze_into_gold()
    completed_after, pending_after = list_harvest_progress()
    print(
        f"[AutoHarvester] Tur Bitti -> Harcanan API: {client.requests_made_this_run}, "
        f"Tamamlanan Maç: {len(completed_after)}/{len(completed_after) + len(pending_after)}, "
        f"Gold: {merge_res}"
    )

    if run_build and client.requests_made_this_run > 0:
        print("[AutoHarvester] Live Server / statik HTML (npm run build) güncelleniyor...")
        subprocess.run("npm run build", cwd=WEB_DIR, shell=True, check=True)

    return len(completed_after), len(pending_after)


def main() -> None:
    parser = argparse.ArgumentParser(description="SiperLig Otomatik Kademeli Veri Toplayıcı")
    parser.add_argument("--status", action="store_true", help="İlerleme ve kalan kota durumunu göster")
    parser.add_argument("--batch-budget", type=int, default=10, help="Her partide en fazla kaç API isteği atılsın")
    parser.add_argument("--interval-seconds", type=int, default=180, help="--loop modunda partiler arası bekleme süresi (sn)")
    parser.add_argument("--loop", action="store_true", help="Bekleyen maçlar bitene veya kota dolana kadar arka planda çalıştır")
    parser.add_argument("--refresh-feeds", action="store_true", help="Güncel puan durumu, fikstür ve özet listesini de yenile")
    parser.add_argument("--harvest-profiles", action="store_true", help="Rezerv üstü kota ile eksik ve 7+ günlük oyuncu profillerini çek/yenile")
    parser.add_argument("--build", action="store_true", help="Yeni veri indiğinde web/ npm run build çalıştır")
    parser.add_argument("--season", type=str, default=os.environ.get("SUPER_LIG_SEASON", "2026"))

    args = parser.parse_args()

    if args.status:
        client = HighlightlyClient(max_requests_per_run=0)
        completed, pending = list_harvest_progress()
        print(f"Tamamlanan Maç Detayı : {len(completed)} / {len(completed) + len(pending)}")
        print(f"Bekleyen Maç Detayı   : {len(pending)}")
        print(f"Kayıtlı API Anahtarı  : {len(client.keys)}")
        print(f"Bugün Kalan Kota      : {client.total_remaining_safe_quota()}")
        return

    if not args.loop:
        run_batch(
            batch_budget=args.batch_budget,
            refresh_feeds=args.refresh_feeds,
            run_build=args.build,
            season=args.season,
            harvest_profiles=args.harvest_profiles,
        )
        return

    print(f"[AutoHarvester] Sürekli kademeli toplama başlatıldı (parti={args.batch_budget} istek, aralık={args.interval_seconds} sn)...")
    while True:
        client_check = HighlightlyClient(max_requests_per_run=0)
        if client_check.total_remaining_safe_quota() <= 0:
            print("[AutoHarvester] Günlük güvenli kota tamamlandı; yarın devam etmek üzere duruluyor.")
            break

        _, pending_count = run_batch(
            batch_budget=args.batch_budget,
            refresh_feeds=args.refresh_feeds,
            run_build=args.build,
            season=args.season,
            harvest_profiles=args.harvest_profiles,
        )
        if pending_count == 0:
            print("[AutoHarvester] Tüm oynanmış Süper Lig maçlarının detayları başarıyla tamamlandı!")
            break

        print(f"[AutoHarvester] {args.interval_seconds} saniye bekleniyor (Durdurmak için Ctrl+C)...")
        time.sleep(args.interval_seconds)


if __name__ == "__main__":
    main()
