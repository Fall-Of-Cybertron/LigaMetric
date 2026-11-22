import React from 'react';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { User, CalendarClock, ShieldAlert } from 'lucide-react';
import { allPlayers, getClubById, getPlayerById } from '@/lib/data';
import {
  formatDateTr,
  formatMarketValue,
  formatRating,
  getInjuryRiskBadgeClass,
  getMonthsUntilExpiry,
  getRatingBadgeClass,
  isContractExpiringWithinOneYear,
} from '@/lib/format';
import { ClubBadge } from '@/components/common/ClubBadge';
import { PlayerAvatar } from '@/components/common/PlayerAvatar';
import { PlayerProfileTabs } from '@/components/player/PlayerProfileTabs';

export function generateStaticParams() {
  return allPlayers.map((player) => ({
    id: player.id,
  }));
}

export default function PlayerDetailPage({ params }: { params: { id: string } }) {
  const player = getPlayerById(params.id);
  if (!player) {
    notFound();
  }

  const club = getClubById(player.clubId);
  const expiringSoon = isContractExpiringWithinOneYear(player.contractExpiry);
  const monthsLeft = getMonthsUntilExpiry(player.contractExpiry);
  const isGoalkeeper = player.positionGroup === 'GK';

  return (
    <div className="space-y-6">
      {/* Player Bio & Contract Header */}
      <section className="rounded-2xl border border-[#1F2937] bg-[#111827] p-5 sm:p-6">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="flex items-start gap-4">
            <div className="relative shrink-0">
              <PlayerAvatar
                photoUrl={player.photoUrl}
                name={player.fullName}
                shirtNumber={player.shirtNumber}
                size="xl"
                rounded="xl"
                className="border-cyan-500/40 shadow-lg"
              />
              {player.photoUrl && (
                <span className="tabular-nums absolute -top-2 -left-2 rounded-lg border border-cyan-500/40 bg-[#090D16] px-1.5 py-0.5 text-[11px] font-black text-cyan-300 shadow">
                  #{player.shirtNumber}
                </span>
              )}
              <span
                className={`tabular-nums absolute -bottom-2 -right-2 rounded-lg border px-1.5 py-0.5 text-xs font-bold ${getRatingBadgeClass(
                  player.avgMatchRating
                )}`}
              >
                {formatRating(player.avgMatchRating)}
              </span>
            </div>

            <div>
              <div className="flex flex-wrap items-center gap-2">
                <Link
                  href={`/clubs/${player.clubId}`}
                  className="inline-flex items-center gap-1.5 rounded-lg border border-[#1F2937] bg-[#090D16] hover:border-cyan-500/50 px-2.5 py-1 text-xs font-semibold text-slate-200 hover:text-cyan-300 transition-colors"
                >
                  <ClubBadge clubId={player.clubId} size="xs" />
                  <span>{player.clubName}</span>
                </Link>
                <span className="rounded-lg bg-cyan-500/15 border border-cyan-500/35 px-2.5 py-1 text-xs font-semibold text-cyan-300">
                  {player.positionMain}
                </span>
                <span
                  className={`inline-flex items-center gap-1 rounded-lg border px-2.5 py-1 text-xs font-semibold ${getInjuryRiskBadgeClass(
                    player.injuryRisk
                  )}`}
                >
                  <ShieldAlert className="w-3.5 h-3.5" />
                  Sakatlık Riski: {player.injuryRisk}
                </span>
              </div>

              <h1 className="mt-2 text-2xl sm:text-3xl font-bold text-slate-50">
                {player.fullName}
              </h1>

              <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1.5 text-xs text-slate-400">
                <span className="inline-flex items-center gap-1">
                  <User className="w-3.5 h-3.5 text-cyan-400" />
                  {player.citizenship} · <span className="tabular-nums">{player.age} yaş</span> (
                  {formatDateTr(player.birthDate)})
                </span>
                <span className="tabular-nums">Boy: {player.height} cm</span>
                <span>Ayak: {player.foot}</span>
                {player.positionSecondary.length > 0 && (
                  <span>Yan Mevki: {player.positionSecondary.join(', ')}</span>
                )}
              </div>
            </div>
          </div>

          {/* Market Value & Contract KPI Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 shrink-0">
            <div className="rounded-xl border border-[#1F2937] bg-[#090D16] px-4 py-3">
              <div className="text-[10px] uppercase tracking-wider text-slate-400">Güncel Değer</div>
              <div className="tabular-nums mt-0.5 text-lg sm:text-xl font-black text-emerald-400">
                {formatMarketValue(player.currentMarketValueEur)}
              </div>
              <div className="tabular-nums text-[11px] text-slate-400">
                Zirve: {formatMarketValue(player.peakMarketValueEur)}
              </div>
            </div>

            <div className="rounded-xl border border-[#1F2937] bg-[#090D16] px-4 py-3">
              <div className="text-[10px] uppercase tracking-wider text-slate-400 flex items-center gap-1">
                <CalendarClock className="w-3 h-3 text-amber-400" />
                Sözleşme Bitişi
              </div>
              <div
                className={`tabular-nums mt-0.5 text-sm sm:text-base font-bold ${
                  expiringSoon ? 'text-amber-300' : 'text-slate-100'
                }`}
              >
                {formatDateTr(player.contractExpiry)}
              </div>
              <div className="tabular-nums text-[11px] text-slate-400">
                {monthsLeft} ay kaldı {expiringSoon ? '· Kritik' : ''}
              </div>
            </div>

            <div className="col-span-2 sm:col-span-1 rounded-xl border border-[#1F2937] bg-[#090D16] px-4 py-3">
              <div className="text-[10px] uppercase tracking-wider text-slate-400">2026 Süper Lig</div>
              <div className="tabular-nums mt-0.5 text-sm sm:text-base font-bold text-cyan-300">
                {player.gamesPlayed} Maç · {player.minutesPlayed}&apos;
              </div>
              <div className="tabular-nums text-[11px] text-slate-400">
                {isGoalkeeper
                  ? `PSxG +/-: ${(player.PSxG_plus_minus ?? 0) >= 0 ? '+' : ''}${(
                      player.PSxG_plus_minus ?? 0
                    ).toFixed(1)}`
                  : `${player.goals} Gol · ${player.assists} Asist`}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Categorized Profile Tabs (Transfermarkt Style) */}
      <PlayerProfileTabs player={player} clubName={club?.name} />
    </div>
  );
}
