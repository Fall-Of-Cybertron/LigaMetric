'use client';

import React, { useMemo, useState } from 'react';
import Link from 'next/link';
import {
  Activity,
  ArrowRight,
  ArrowRightLeft,
  BarChart2,
  HeartPulse,
  Radio,
  ShieldAlert,
  TrendingUp,
} from 'lucide-react';
import type { Player } from '@/types/football';
import {
  formatDateTr,
  formatMarketValue,
  formatRating,
  getInjuryRiskBadgeClass,
  getRatingBadgeClass,
} from '@/lib/format';
import { ClubBadge } from '@/components/common/ClubBadge';
import { InjurySkeletonMap } from '@/components/player/InjurySkeletonMap';
import { MarketValueTimeline } from '@/components/player/MarketValueTimeline';

interface PlayerProfileTabsProps {
  player: Player;
  clubName?: string;
}

type ProfileTabId = 'overview' | 'performance' | 'market' | 'injuries';

function RadialMetricRing({
  label,
  valueLabel,
  percent,
  color,
  subLabel,
}: {
  label: string;
  valueLabel: string;
  percent: number;
  color: string;
  subLabel?: string;
}) {
  const clamped = Math.min(100, Math.max(0, percent));
  const r = 30;
  const circ = 2 * Math.PI * r;
  const dashOffset = circ * (1 - clamped / 100);

  return (
    <div className="flex flex-col items-center rounded-xl border border-[#1F2937] bg-[#090D16]/75 p-3 text-center">
      <div className="relative w-20 h-20 flex items-center justify-center">
        <svg viewBox="0 0 76 76" className="w-full h-full -rotate-90">
          <circle cx="38" cy="38" r={r} fill="none" stroke="#1F2937" strokeWidth="6" />
          <circle
            cx="38"
            cy="38"
            r={r}
            fill="none"
            stroke={color}
            strokeWidth="6"
            strokeLinecap="round"
            strokeDasharray={circ}
            strokeDashoffset={dashOffset}
          />
        </svg>
        <span className="tabular-nums absolute text-sm font-bold text-slate-100">{valueLabel}</span>
      </div>
      <div className="mt-1.5 text-xs font-semibold text-slate-200">{label}</div>
      {subLabel && <div className="text-[10px] text-slate-400 tabular-nums">{subLabel}</div>}
    </div>
  );
}

export function PlayerProfileTabs({ player, clubName }: PlayerProfileTabsProps) {
  const [activeTab, setActiveTab] = useState<ProfileTabId>('overview');
  const isGoalkeeper = player.positionGroup === 'GK';

  const injurySummary = useMemo(() => {
    const regions = Object.values(player.injuries.anatomyRegions);
    const anatCount = regions.reduce((s, r) => s + r.count, 0);
    const anatDays = regions.reduce((s, r) => s + r.totalDays, 0);
    const anatMissed = regions.reduce((s, r) => s + r.missedGames, 0);
    const sysCount = player.injuries.systemicRecords.length;
    const sysDays = player.injuries.systemicRecords.reduce((s, r) => s + r.days, 0);
    const sysMissed = player.injuries.systemicRecords.reduce((s, r) => s + r.missedGames, 0);
    return {
      totalCount: anatCount + sysCount,
      totalDays: anatDays + sysDays,
      totalMissed: anatMissed + sysMissed,
    };
  }, [player.injuries]);

  const tabs: { id: ProfileTabId; label: string; icon: React.ComponentType<{ className?: string }>; count?: number }[] = [
    { id: 'overview', label: 'Genel Bakış', icon: BarChart2 },
    { id: 'performance', label: 'Performans & Kariyer', icon: Activity, count: player.perClub.length },
    { id: 'market', label: 'Piyasa Değeri & Transferler', icon: TrendingUp, count: player.transfers.length },
    { id: 'injuries', label: 'Sakatlık Geçmişi', icon: HeartPulse, count: injurySummary.totalCount },
  ];

  const renderPerformanceRings = () => (
    <section className="rounded-2xl border border-[#1F2937] bg-[#111827] p-4 sm:p-5 space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <BarChart2 className="w-4 h-4 text-cyan-400" />
          <h2 className="text-sm sm:text-base font-bold text-slate-100">
            {isGoalkeeper
              ? 'Kaleci Performans Halkaları & PSxG +/- Analizi'
              : '2026 Süper Lig Per-90 Performans Halkaları'}
          </h2>
        </div>
        {clubName && (
          <Link href={`/clubs/${player.clubId}`} className="text-xs text-cyan-400 hover:text-cyan-300">
            {clubName} Kadrosuna Dön →
          </Link>
        )}
      </div>

      {isGoalkeeper ? (
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
          <RadialMetricRing
            label="PSxG +/-"
            valueLabel={`${(player.PSxG_plus_minus ?? 0) >= 0 ? '+' : ''}${(
              player.PSxG_plus_minus ?? 0
            ).toFixed(1)}`}
            percent={Math.min(100, Math.max(15, 50 + (player.PSxG_plus_minus ?? 0) * 6))}
            color="#10B981"
            subLabel="Önlenen Gol"
          />
          <RadialMetricRing
            label="Kurtarış Yüzdesi"
            valueLabel={`%${(player.savePercentage ?? 72).toFixed(1)}`}
            percent={player.savePercentage ?? 72}
            color="#06B6D4"
            subLabel="İsabetli Şut"
          />
          <RadialMetricRing
            label="Gol Yemeden Maç"
            valueLabel={`${player.cleanSheets ?? 0}`}
            percent={((player.cleanSheets ?? 0) / Math.max(1, player.gamesPlayed)) * 100}
            color="#A855F7"
            subLabel={`${player.gamesPlayed} maçta`}
          />
          <RadialMetricRing
            label="Pas İsabeti"
            valueLabel={`%${player.passAccuracy.toFixed(1)}`}
            percent={player.passAccuracy}
            color="#38BDF8"
            subLabel="Oyun Kurulumu"
          />
          <RadialMetricRing
            label="Sezon Reytingi"
            valueLabel={formatRating(player.avgMatchRating)}
            percent={player.avgMatchRating * 10}
            color="#F59E0B"
            subLabel="10 üzerinden"
          />
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
          <RadialMetricRing
            label="90 Dk Başına Gol"
            valueLabel={player.per90Goals.toFixed(2)}
            percent={Math.min(100, player.per90Goals * 95)}
            color="#10B981"
            subLabel={`${player.goals} Gol (xG: ${player.xG.toFixed(1)})`}
          />
          <RadialMetricRing
            label="90 Dk Başına Asist"
            valueLabel={player.per90Assists.toFixed(2)}
            percent={Math.min(100, player.per90Assists * 120)}
            color="#06B6D4"
            subLabel={`${player.assists} Asist (xA: ${player.xA.toFixed(1)})`}
          />
          <RadialMetricRing
            label="Kilit Pas / 90"
            valueLabel={player.keyPassesPer90.toFixed(2)}
            percent={Math.min(100, player.keyPassesPer90 * 28)}
            color="#A855F7"
            subLabel="Şans Yaratma"
          />
          <RadialMetricRing
            label="Pas İsabeti"
            valueLabel={`%${player.passAccuracy.toFixed(1)}`}
            percent={player.passAccuracy}
            color="#38BDF8"
            subLabel={`Prog/90: ${player.progressiveActionsPer90.toFixed(1)}`}
          />
          <RadialMetricRing
            label="Ortalama Reyting"
            valueLabel={formatRating(player.avgMatchRating)}
            percent={player.avgMatchRating * 10}
            color="#F59E0B"
            subLabel={`${player.yellowCards} Sarı · ${player.redCards} Kırmızı`}
          />
        </div>
      )}
    </section>
  );

  return (
    <div className="space-y-5">
      {/* Transfermarkt-Style Category Navigation Bar */}
      <nav
        className="flex items-center gap-1.5 overflow-x-auto no-scrollbar rounded-2xl border border-[#1F2937] bg-[#111827] p-1.5"
        aria-label="Oyuncu Profil Kategorileri"
      >
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const active = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id)}
              className={`inline-flex shrink-0 items-center gap-2 rounded-xl px-3.5 py-2 text-xs font-semibold transition-all ${
                active
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/45 shadow-sm'
                  : 'text-slate-400 hover:text-slate-100 hover:bg-[#1E293B]/60 border border-transparent'
              }`}
            >
              <Icon className="w-3.5 h-3.5 shrink-0" />
              <span>{tab.label}</span>
              {typeof tab.count === 'number' && (
                <span
                  className={`tabular-nums rounded-md px-1.5 py-0.5 text-[10px] font-bold ${
                    active
                      ? 'bg-[#090D16] text-cyan-300 border border-cyan-500/30'
                      : 'bg-[#090D16]/80 text-slate-400 border border-[#1F2937]'
                  }`}
                >
                  {tab.count}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* TAB 1: Genel Bakış */}
      {activeTab === 'overview' && (
        <div className="space-y-5">
          {renderPerformanceRings()}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {/* Market Summary Card */}
            <section className="rounded-2xl border border-[#1F2937] bg-[#111827] p-4 sm:p-5 flex flex-col justify-between gap-4">
              <div className="space-y-3">
                <div className="flex items-center justify-between border-b border-[#1F2937] pb-2.5">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-emerald-400" />
                    <h3 className="text-sm font-bold text-slate-100">Piyasa Değeri &amp; Sözleşme Özeti</h3>
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-2.5 text-xs">
                  <div className="rounded-xl border border-[#1F2937] bg-[#090D16] p-3">
                    <div className="text-[10px] text-slate-400">Güncel Değer</div>
                    <div className="tabular-nums text-sm font-black text-emerald-400 mt-0.5">
                      {formatMarketValue(player.currentMarketValueEur)}
                    </div>
                  </div>
                  <div className="rounded-xl border border-[#1F2937] bg-[#090D16] p-3">
                    <div className="text-[10px] text-slate-400">Zirve Değer</div>
                    <div className="tabular-nums text-sm font-bold text-slate-100 mt-0.5">
                      {formatMarketValue(player.peakMarketValueEur)}
                    </div>
                  </div>
                  <div className="rounded-xl border border-[#1F2937] bg-[#090D16] p-3">
                    <div className="text-[10px] text-slate-400">Sözleşme Bitişi</div>
                    <div className="tabular-nums text-xs font-bold text-amber-300 mt-1">
                      {formatDateTr(player.contractExpiry)}
                    </div>
                  </div>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setActiveTab('market')}
                className="inline-flex items-center justify-between w-full rounded-xl border border-[#1F2937] bg-[#090D16]/80 hover:border-cyan-500/45 px-3.5 py-2 text-xs font-semibold text-cyan-400 hover:text-cyan-300 transition-colors"
              >
                <span>Piyasa &amp; Transferler Sekmesine Git</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </section>

            {/* Injury Summary Card */}
            <section className="rounded-2xl border border-[#1F2937] bg-[#111827] p-4 sm:p-5 flex flex-col justify-between gap-4">
              <div className="space-y-3">
                <div className="flex items-center justify-between border-b border-[#1F2937] pb-2.5">
                  <div className="flex items-center gap-2">
                    <HeartPulse className="w-4 h-4 text-rose-400" />
                    <h3 className="text-sm font-bold text-slate-100">Sakatlık &amp; Kondisyon Özeti</h3>
                  </div>
                  <span
                    className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-semibold ${getInjuryRiskBadgeClass(
                      player.injuryRisk
                    )}`}
                  >
                    <ShieldAlert className="w-3 h-3" />
                    {player.injuryRisk}
                  </span>
                </div>
                <div className="grid grid-cols-3 gap-2.5 text-xs">
                  <div className="rounded-xl border border-[#1F2937] bg-[#090D16] p-3">
                    <div className="text-[10px] text-slate-400">Toplam Kayıt</div>
                    <div className="tabular-nums text-sm font-black text-slate-100 mt-0.5">
                      {injurySummary.totalCount}
                    </div>
                  </div>
                  <div className="rounded-xl border border-[#1F2937] bg-[#090D16] p-3">
                    <div className="text-[10px] text-slate-400">Uzak Kalınan</div>
                    <div className="tabular-nums text-sm font-bold text-amber-300 mt-0.5">
                      {injurySummary.totalDays} Gün
                    </div>
                  </div>
                  <div className="rounded-xl border border-[#1F2937] bg-[#090D16] p-3">
                    <div className="text-[10px] text-slate-400">Kaçırılan Maç</div>
                    <div className="tabular-nums text-sm font-bold text-rose-400 mt-0.5">
                      {injurySummary.totalMissed} Maç
                    </div>
                  </div>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setActiveTab('injuries')}
                className="inline-flex items-center justify-between w-full rounded-xl border border-[#1F2937] bg-[#090D16]/80 hover:border-cyan-500/45 px-3.5 py-2 text-xs font-semibold text-cyan-400 hover:text-cyan-300 transition-colors"
              >
                <span>Sakatlık Geçmişi Sekmesine Git</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </section>
          </div>
        </div>
      )}

      {/* TAB 2: Performans & Kariyer */}
      {activeTab === 'performance' && (
        <div className="space-y-5">
          {renderPerformanceRings()}

          <section className="rounded-2xl border border-[#1F2937] bg-[#111827] p-4 sm:p-5 space-y-3">
            <h3 className="text-sm font-bold text-slate-100 border-b border-[#1F2937] pb-2.5">
              2026 Süper Lig Sezon İstatistik Özeti
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3 text-xs">
              <div className="rounded-xl border border-[#1F2937] bg-[#090D16] p-3">
                <div className="text-[10px] text-slate-400">Oynanan Maç</div>
                <div className="tabular-nums text-base font-bold text-slate-100 mt-0.5">
                  {player.gamesPlayed}
                </div>
              </div>
              <div className="rounded-xl border border-[#1F2937] bg-[#090D16] p-3">
                <div className="text-[10px] text-slate-400">Dakika</div>
                <div className="tabular-nums text-base font-bold text-slate-100 mt-0.5">
                  {player.minutesPlayed}&apos;
                </div>
              </div>
              <div className="rounded-xl border border-[#1F2937] bg-[#090D16] p-3">
                <div className="text-[10px] text-slate-400">Gol / xG</div>
                <div className="tabular-nums text-base font-bold text-emerald-400 mt-0.5">
                  {player.goals} / {player.xG.toFixed(1)}
                </div>
              </div>
              <div className="rounded-xl border border-[#1F2937] bg-[#090D16] p-3">
                <div className="text-[10px] text-slate-400">Asist / xA</div>
                <div className="tabular-nums text-base font-bold text-cyan-300 mt-0.5">
                  {player.assists} / {player.xA.toFixed(1)}
                </div>
              </div>
              <div className="rounded-xl border border-[#1F2937] bg-[#090D16] p-3">
                <div className="text-[10px] text-slate-400">Kilit Pas / 90</div>
                <div className="tabular-nums text-base font-bold text-slate-100 mt-0.5">
                  {player.keyPassesPer90.toFixed(2)}
                </div>
              </div>
              <div className="rounded-xl border border-[#1F2937] bg-[#090D16] p-3">
                <div className="text-[10px] text-slate-400">Disiplin</div>
                <div className="tabular-nums text-sm font-bold text-amber-300 mt-1">
                  {player.yellowCards} Sarı · {player.redCards} Kırmızı
                </div>
              </div>
            </div>
          </section>

          <section className="rounded-2xl border border-[#1F2937] bg-[#111827] overflow-hidden">
            <div className="px-4 py-3.5 border-b border-[#1F2937]">
              <h2 className="text-sm sm:text-base font-bold text-slate-100">
                Kulüp &amp; Turnuva Kariyer Özeti
              </h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-[#090D16]/80 text-[11px] uppercase text-slate-400 border-b border-[#1F2937]">
                  <tr>
                    <th className="px-4 py-2.5">Kulüp</th>
                    <th className="px-3 py-2.5">Turnuva</th>
                    <th className="px-3 py-2.5">Dönem</th>
                    <th className="px-3 py-2.5 text-center">Maç</th>
                    <th className="px-3 py-2.5 text-right">Dakika</th>
                    <th className="px-3 py-2.5 text-center">Gol</th>
                    <th className="px-3 py-2.5 text-center">Asist</th>
                    <th className="px-4 py-2.5 text-right">Ort. Reyting</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#1F2937]/70">
                  {player.perClub.map((c, idx) => (
                    <tr key={`pc-${idx}`} className="hover:bg-[#1E293B]/60">
                      <td className="px-4 py-2.5">
                        <Link
                          href={`/clubs/${c.clubId}`}
                          className="inline-flex items-center gap-2 font-semibold text-slate-100 hover:text-cyan-300"
                        >
                          <ClubBadge clubId={c.clubId} size="xs" />
                          <span>{c.clubName}</span>
                        </Link>
                      </td>
                      <td className="px-3 py-2.5 text-slate-300">{c.competition}</td>
                      <td className="px-3 py-2.5 tabular-nums text-slate-400">{c.seasonRange}</td>
                      <td className="px-3 py-2.5 text-center tabular-nums text-slate-200">{c.games}</td>
                      <td className="px-3 py-2.5 text-right tabular-nums text-slate-400">
                        {c.minutes}&apos;
                      </td>
                      <td className="px-3 py-2.5 text-center tabular-nums text-emerald-400 font-semibold">
                        {c.goals}
                      </td>
                      <td className="px-3 py-2.5 text-center tabular-nums text-cyan-300 font-semibold">
                        {c.assists}
                      </td>
                      <td className="px-4 py-2.5 text-right">
                        <span
                          className={`tabular-nums inline-block rounded border px-1.5 py-0.5 text-[11px] font-bold ${getRatingBadgeClass(
                            c.avgRating
                          )}`}
                        >
                          {formatRating(c.avgRating)}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </div>
      )}

      {/* TAB 3: Piyasa Değeri & Transferler */}
      {activeTab === 'market' && (
        <div className="space-y-5">
          <MarketValueTimeline
            history={player.marketValueHistory}
            peakValueEur={player.peakMarketValueEur}
          />

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <section className="lg:col-span-7 rounded-2xl border border-[#1F2937] bg-[#111827] overflow-hidden">
              <div className="flex items-center gap-2 px-4 py-3.5 border-b border-[#1F2937]">
                <ArrowRightLeft className="w-4 h-4 text-cyan-400" />
                <h2 className="text-sm sm:text-base font-bold text-slate-100">
                  Bonservis &amp; Transfer Geçmişi
                </h2>
              </div>

              {player.transfers.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-[#090D16]/80 text-[11px] uppercase text-slate-400 border-b border-[#1F2937]">
                      <tr>
                        <th className="px-4 py-2.5">Sezon</th>
                        <th className="px-3 py-2.5">Tarih</th>
                        <th className="px-3 py-2.5">Ayrıldığı</th>
                        <th className="px-3 py-2.5">Katıldığı</th>
                        <th className="px-3 py-2.5 text-right">Piyasa Değeri</th>
                        <th className="px-4 py-2.5 text-right text-emerald-400">Bedel</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#1F2937]/70">
                      {player.transfers.map((tr, idx) => (
                        <tr key={`tr-${idx}`} className="hover:bg-[#1E293B]/60">
                          <td className="px-4 py-2.5 tabular-nums font-medium text-slate-200">
                            {tr.season}
                          </td>
                          <td className="px-3 py-2.5 tabular-nums text-slate-400">
                            {formatDateTr(tr.transferDate)}
                          </td>
                          <td className="px-3 py-2.5">
                            {tr.fromClubId ? (
                              <Link
                                href={`/clubs/${tr.fromClubId}`}
                                className="inline-flex items-center gap-1.5 text-slate-300 hover:text-cyan-300"
                              >
                                <ClubBadge clubId={tr.fromClubId} size="xs" />
                                <span>{tr.from}</span>
                              </Link>
                            ) : (
                              <span className="text-slate-300">{tr.from}</span>
                            )}
                          </td>
                          <td className="px-3 py-2.5">
                            {tr.toClubId ? (
                              <Link
                                href={`/clubs/${tr.toClubId}`}
                                className="inline-flex items-center gap-1.5 font-semibold text-slate-100 hover:text-cyan-300"
                              >
                                <ClubBadge clubId={tr.toClubId} size="xs" />
                                <span>{tr.to}</span>
                              </Link>
                            ) : (
                              <span className="font-semibold text-slate-100">{tr.to}</span>
                            )}
                          </td>
                          <td className="px-3 py-2.5 text-right tabular-nums text-slate-400">
                            {formatMarketValue(tr.marketValue)}
                          </td>
                          <td className="px-4 py-2.5 text-right tabular-nums font-bold text-emerald-400">
                            {tr.fee}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="p-6 text-xs text-slate-400">
                  Kulüp altyapısı / istikrarlı kadro oyuncusu; yakın dönem bonservis hareketi yok.
                </div>
              )}
            </section>

            <section className="lg:col-span-5 rounded-2xl border border-[#1F2937] bg-[#111827] p-4 sm:p-5 space-y-3">
              <div className="flex items-center justify-between border-b border-[#1F2937] pb-3">
                <div className="flex items-center gap-2">
                  <Radio className="w-4 h-4 text-emerald-400" />
                  <h2 className="text-sm sm:text-base font-bold text-slate-100">
                    Transfer Gündemi
                  </h2>
                </div>
                <Link
                  href="/market-and-predictions"
                  className="text-xs text-cyan-400 hover:text-cyan-300"
                >
                  Piyasa &amp; Analiz →
                </Link>
              </div>

              {player.rumours.length > 0 ? (
                <div className="space-y-3">
                  {player.rumours.map((r, idx) => (
                    <div
                      key={`rum-${idx}`}
                      className="rounded-xl border border-[#1F2937] bg-[#090D16]/80 p-3 space-y-2"
                    >
                      <div className="flex items-center justify-between gap-2">
                        {r.clubId ? (
                          <Link
                            href={`/clubs/${r.clubId}`}
                            className="inline-flex items-center gap-2 text-xs font-bold text-slate-100 hover:text-cyan-300"
                          >
                            <ClubBadge clubId={r.clubId} size="xs" />
                            <span>{r.club}</span>
                          </Link>
                        ) : (
                          <span className="text-xs font-bold text-slate-100">{r.club}</span>
                        )}
                        <span className="tabular-nums text-xs font-bold text-cyan-300">
                          %{r.transferProbability}
                        </span>
                      </div>
                      <div className="h-2 w-full rounded-full bg-[#1F2937] overflow-hidden">
                        <div
                          className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-emerald-400"
                          style={{ width: `${r.transferProbability}%` }}
                        />
                      </div>
                      <div className="flex items-center justify-between text-[11px] text-slate-400">
                        <span>Kaynak: {r.source}</span>
                        <span className="tabular-nums">{formatDateTr(r.rumourDate)}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="py-6 text-center text-xs text-slate-400">
                  Şu anda aktif transfer söylentisi bulunmamaktadır.
                </div>
              )}
            </section>
          </div>
        </div>
      )}

      {/* TAB 4: Sakatlık Geçmişi */}
      {activeTab === 'injuries' && (
        <InjurySkeletonMap injuries={player.injuries} playerName={player.fullName} />
      )}
    </div>
  );
}
