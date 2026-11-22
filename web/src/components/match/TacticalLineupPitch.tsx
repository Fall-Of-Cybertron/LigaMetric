'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Users } from 'lucide-react';
import type { LineupPlayerNode, MatchInitialLineup } from '@/types/football';
import { formatRating, getRatingBadgeClass } from '@/lib/format';
import { ClubBadge } from '@/components/common/ClubBadge';
import { PlayerAvatar } from '@/components/common/PlayerAvatar';

interface TacticalLineupPitchProps {
  lineup: MatchInitialLineup;
  homeClubId: string;
  homeClubName: string;
  awayClubId: string;
  awayClubName: string;
}

function GoalBallIcon() {
  return (
    <svg viewBox="0 0 16 16" className="w-2.5 h-2.5 shrink-0" fill="none" aria-hidden="true">
      <circle cx="8" cy="8" r="6.2" stroke="currentColor" strokeWidth="1.5" />
      <polygon points="8,4.6 10.7,6.6 9.7,9.8 6.3,9.8 5.3,6.6" fill="currentColor" />
      <path
        d="M8 2V4.6M13.5 6L10.7 6.6M11.6 12.6L9.7 9.8M4.4 12.6L6.3 9.8M2.5 6L5.3 6.6"
        stroke="currentColor"
        strokeWidth="1.1"
        strokeLinecap="round"
      />
    </svg>
  );
}

function AssistBootIcon() {
  return (
    <svg viewBox="0 0 16 16" className="w-3 h-3 shrink-0" fill="currentColor" aria-hidden="true">
      <path d="M2.2 10.6V6.2c0-.4.3-.7.7-.7h1.4c.3 0 .6.2.7.5.5 1.3 1.7 2.1 3.3 2.4l3.5.7c1 .2 1.7 1 1.7 2v.4c0 .4-.3.6-.7.6H2.8c-.3 0-.6-.2-.6-.5v-1zm1.3 2.1h1.3v1.1H3.5v-1.1zm3.7 0h1.3v1.1H7.2v-1.1zm3.8 0h1.3v1.1H11v-1.1z" />
    </svg>
  );
}

function PitchTeamColumn({
  rows,
  clubId,
  clubName,
  formation,
  invertAttackDirection = false,
}: {
  rows: LineupPlayerNode[][];
  clubId: string;
  clubName: string;
  formation: string;
  invertAttackDirection?: boolean;
}) {
  const orderedRows = invertAttackDirection ? [...rows].reverse() : rows;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between px-1">
        <Link
          href={`/clubs/${clubId}`}
          className="inline-flex items-center gap-2 text-xs font-bold text-slate-100 hover:text-cyan-300"
        >
          <ClubBadge clubId={clubId} size="xs" />
          <span>{clubName}</span>
        </Link>
        <span className="tabular-nums rounded-md bg-[#090D16] border border-[#1F2937] px-2 py-0.5 text-[11px] font-semibold text-cyan-300">
          {formation}
        </span>
      </div>

      <div
        className="relative rounded-2xl border border-emerald-500/25 p-4 flex flex-col justify-between gap-4 min-h-[430px] overflow-hidden"
        style={{
          background:
            'linear-gradient(180deg, rgba(16,185,129,0.12) 0%, rgba(9,13,22,0.92) 50%, rgba(6,182,212,0.10) 100%)',
        }}
      >
        {/* Turf Markings */}
        <div className="pointer-events-none absolute inset-3 rounded-xl border border-emerald-500/20">
          <div className="absolute top-1/2 left-0 right-0 border-t border-emerald-500/15" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-24 h-24 rounded-full border border-emerald-500/15" />
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-32 h-12 border-b border-x border-emerald-500/20" />
          <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-32 h-12 border-t border-x border-emerald-500/20" />
        </div>

        {orderedRows.map((row, rIdx) => (
          <div
            key={`line-${clubId}-${rIdx}`}
            className="relative z-10 flex items-center justify-around gap-1.5"
          >
            {row.map((node) => (
              <Link
                key={node.playerId}
                href={`/players/${node.playerId}`}
                className="flex flex-col items-center text-center group max-w-[78px]"
              >
                <div className="relative flex items-center justify-center w-10 h-10 sm:w-11 sm:h-11 rounded-full bg-[#111827] border-2 border-cyan-500/45 group-hover:border-cyan-300 shadow-md transition-all">
                  <PlayerAvatar
                    photoUrl={node.photoUrl}
                    name={node.name}
                    shirtNumber={node.shirtNumber}
                    size="md"
                    rounded="full"
                    className="border-0 bg-transparent"
                  />
                  {/* Top-Left Card Badge */}
                  {(node.yellowCard || node.redCard) && (
                    <div className="absolute -top-1.5 -left-1.5 z-20 flex items-center rounded-md bg-[#090D16]/90 border border-[#1F2937] p-0.5 shadow-md">
                      {node.yellowCard && node.redCard ? (
                        <span
                          title="2. Sarıdan Kırmızı Kart"
                          className="inline-flex items-center"
                        >
                          <span className="w-2 h-3 rounded-[2px] bg-amber-400 border border-black/80" />
                          <span className="-ml-1 w-2 h-3 rounded-[2px] bg-rose-600 border border-white/80" />
                        </span>
                      ) : node.redCard ? (
                        <span
                          title="Kırmızı Kart"
                          className="w-2.5 h-3.5 rounded-[2px] bg-rose-600 border border-white/80"
                        />
                      ) : (
                        <span
                          title="Sarı Kart"
                          className="w-2.5 h-3.5 rounded-[2px] bg-amber-400 border border-black/80"
                        />
                      )}
                    </div>
                  )}

                  {/* Bottom-Left Shirt Number */}
                  {node.photoUrl && (
                    <span className="tabular-nums absolute -bottom-1 -left-1.5 z-20 rounded bg-[#090D16] border border-[#1F2937] px-1 text-[8.5px] font-bold text-slate-200 leading-tight shadow">
                      {node.shirtNumber}
                    </span>
                  )}

                  {/* Top-Right Match Rating Badge */}
                  <span
                    className={`tabular-nums absolute -top-2 -right-2.5 z-20 rounded border px-1 py-0.5 text-[9.5px] font-bold leading-none shadow ${getRatingBadgeClass(
                      node.matchRating
                    )}`}
                  >
                    {formatRating(node.matchRating)}
                  </span>

                  {/* Bottom-Right Goals & Assists Pills */}
                  {(node.goals > 0 || node.assists > 0) && (
                    <div className="absolute -bottom-1.5 -right-2 z-20 flex items-center gap-0.5">
                      {node.goals > 0 && (
                        <span
                          title={`${node.goals} Gol`}
                          className="tabular-nums inline-flex items-center gap-0.5 rounded-full bg-[#090D16]/95 border border-emerald-400/60 text-emerald-300 px-1.5 py-0.5 text-[9px] font-bold leading-none shadow-md"
                        >
                          <GoalBallIcon />
                          {node.goals > 1 && <span>{node.goals}</span>}
                        </span>
                      )}
                      {node.assists > 0 && (
                        <span
                          title={`${node.assists} Asist`}
                          className="tabular-nums inline-flex items-center gap-0.5 rounded-full bg-[#090D16]/95 border border-cyan-400/60 text-cyan-300 px-1.5 py-0.5 text-[9px] font-bold leading-none shadow-md"
                        >
                          <AssistBootIcon />
                          {node.assists > 1 && <span>{node.assists}</span>}
                        </span>
                      )}
                    </div>
                  )}
                </div>

                <span className="mt-1.5 text-[10.5px] font-semibold text-slate-100 group-hover:text-cyan-300 truncate max-w-[76px]">
                  {node.name}
                </span>
              </Link>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

export function TacticalLineupPitch({
  lineup,
  homeClubId,
  homeClubName,
  awayClubId,
  awayClubName,
}: TacticalLineupPitchProps) {
  const [mobileSide, setMobileSide] = useState<'home' | 'away'>('home');

  return (
    <section className="rounded-2xl border border-[#1F2937] bg-[#111827] p-4 sm:p-5 space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[#1F2937] pb-3">
        <div className="flex items-center gap-2">
          <Users className="w-4 h-4 text-cyan-400" />
          <h2 className="text-sm sm:text-base font-bold text-slate-100">
            2D Gerçek Diziliş Sahası &amp; Maç Reytingleri
          </h2>
        </div>

        {/* Mobile Switcher */}
        <div className="flex lg:hidden rounded-xl bg-[#090D16] border border-[#1F2937] p-0.5 text-xs">
          <button
            type="button"
            onClick={() => setMobileSide('home')}
            className={`px-3 py-1 rounded-lg font-semibold ${
              mobileSide === 'home' ? 'bg-cyan-500/20 text-cyan-300' : 'text-slate-400'
            }`}
          >
            {homeClubName}
          </button>
          <button
            type="button"
            onClick={() => setMobileSide('away')}
            className={`px-3 py-1 rounded-lg font-semibold ${
              mobileSide === 'away' ? 'bg-emerald-500/20 text-emerald-300' : 'text-slate-400'
            }`}
          >
            {awayClubName}
          </button>
        </div>
      </div>

      {/* Mobile: single active team */}
      <div className="lg:hidden">
        {mobileSide === 'home' ? (
          <PitchTeamColumn
            rows={lineup.home}
            clubId={homeClubId}
            clubName={homeClubName}
            formation={lineup.homeFormation}
            invertAttackDirection
          />
        ) : (
          <PitchTeamColumn
            rows={lineup.away}
            clubId={awayClubId}
            clubName={awayClubName}
            formation={lineup.awayFormation}
            invertAttackDirection
          />
        )}
      </div>

      {/* Desktop: side-by-side comparison */}
      <div className="hidden lg:grid lg:grid-cols-2 gap-5">
        <PitchTeamColumn
          rows={lineup.home}
          clubId={homeClubId}
          clubName={homeClubName}
          formation={lineup.homeFormation}
          invertAttackDirection
        />
        <PitchTeamColumn
          rows={lineup.away}
          clubId={awayClubId}
          clubName={awayClubName}
          formation={lineup.awayFormation}
          invertAttackDirection
        />
      </div>
    </section>
  );
}
