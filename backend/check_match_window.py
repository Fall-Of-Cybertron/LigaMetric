"""API kotası harcamadan maç bitiş penceresini kontrol eden GitHub Actions kapı betiği."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

SYNC_STATUS_PATH = (
    Path(__file__).resolve().parent.parent / "web" / "src" / "data" / "sync-status.json"
)
TSI_TZ = timezone(timedelta(hours=3))


def _write_github_output(should_run: bool) -> None:
    """GitHub Actions adım çıktısına should_run değerini yazar."""
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    with open(output_path, "a", encoding="utf-8") as fh:
        fh.write(f"should_run={'true' if should_run else 'false'}\n")


def _parse_utc(raw: str) -> datetime | None:
    """ISO-8601 başlama saatini UTC timezone-aware datetime nesnesine çevirir."""
    if not raw:
        return None
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def evaluate_match_window(
    upcoming: list[dict[str, Any]],
    now_utc: datetime,
    min_after_min: int,
    max_after_min: int,
) -> tuple[list[tuple[dict[str, Any], float]], dict[str, Any] | None]:
    """Maç bitiş penceresine giren maçları ve sıradaki ilk gelecek maçı döndürür."""
    due_matches: list[tuple[dict[str, Any], float]] = []
    future_candidates: list[tuple[datetime, dict[str, Any]]] = []

    for item in upcoming:
        kickoff_utc = _parse_utc(str(item.get("dateUtc") or ""))
        if kickoff_utc is None:
            continue
        elapsed_min = (now_utc - kickoff_utc).total_seconds() / 60.0
        if min_after_min <= elapsed_min <= max_after_min:
            due_matches.append((item, elapsed_min))
        elif elapsed_min < min_after_min:
            future_candidates.append((kickoff_utc, item))

    future_candidates.sort(key=lambda pair: pair[0])
    next_match = future_candidates[0][1] if future_candidates else None
    return due_matches, next_match


def main() -> None:
    """CLI giriş noktası."""
    parser = argparse.ArgumentParser(
        description="Yaklaşan Süper Lig maçlarının bitiş penceresini kontrol eder."
    )
    parser.add_argument(
        "--min-after-kickoff-min",
        type=int,
        default=125,
        help="Maç başlangıcından itibaren en erken tetikleme süresi (dakika).",
    )
    parser.add_argument(
        "--max-after-kickoff-min",
        type=int,
        default=300,
        help="Maç başlangıcından itibaren en geç tetikleme süresi (dakika).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Pencere kontrolünü atlayıp should_run=true döndürür.",
    )
    args = parser.parse_args()

    now_utc = datetime.now(timezone.utc)
    now_tsi = now_utc.astimezone(TSI_TZ)
    print(f"[MatchGate] Şu an: {now_utc.strftime('%Y-%m-%d %H:%M UTC')} / {now_tsi.strftime('%H:%M TSİ')}")

    if args.force:
        print("[MatchGate] --force etkin (manuel tetikleme veya sabah kontrolü) -> should_run=true")
        _write_github_output(True)
        return

    if not SYNC_STATUS_PATH.exists():
        print(f"[MatchGate] {SYNC_STATUS_PATH} bulunamadı -> should_run=false")
        _write_github_output(False)
        return

    try:
        doc = json.loads(SYNC_STATUS_PATH.read_text(encoding="utf-8"))
        upcoming = doc.get("upcomingKickoffs") or []
    except Exception as exc:
        print(f"[MatchGate] sync-status.json okunamadı ({exc}) -> should_run=false")
        _write_github_output(False)
        return

    due_matches, next_match = evaluate_match_window(
        upcoming=upcoming,
        now_utc=now_utc,
        min_after_min=args.min_after_kickoff_min,
        max_after_min=args.max_after_kickoff_min,
    )

    if due_matches:
        print(
            f"[MatchGate] Bitiş penceresinde ({args.min_after_kickoff_min}-{args.max_after_kickoff_min} dk) "
            f"{len(due_matches)} maç bulundu -> should_run=true"
        )
        for m, elapsed in due_matches:
            print(
                f"  - {m.get('home')} vs {m.get('away')} "
                f"(ID: {m.get('id')}, Başlama: {m.get('dateUtc')}, Geçen: {elapsed:.0f} dk)"
            )
        _write_github_output(True)
        return

    print("[MatchGate] Maç sonrası güncelleme penceresinde maç yok -> should_run=false")
    if next_match:
        ko_utc = _parse_utc(str(next_match.get("dateUtc") or ""))
        if ko_utc:
            ko_tsi = ko_utc.astimezone(TSI_TZ)
            trigger_tsi = ko_tsi + timedelta(minutes=args.min_after_kickoff_min)
            print(
                f"[MatchGate] Sıradaki hedef: {next_match.get('home')} vs {next_match.get('away')} | "
                f"Başlama: {ko_utc.strftime('%Y-%m-%d %H:%M UTC')} ({ko_tsi.strftime('%d.%m %H:%M TSİ')}) | "
                f"Erken güncelleme penceresi: ~{trigger_tsi.strftime('%d.%m %H:%M TSİ')}"
            )
    else:
        print("[MatchGate] upcomingKickoffs içinde beklenen yeni maç kaydı bulunamadı.")
    _write_github_output(False)


if __name__ == "__main__":
    main()
