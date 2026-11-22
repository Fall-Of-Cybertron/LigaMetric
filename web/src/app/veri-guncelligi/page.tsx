import React from 'react';
import Link from 'next/link';
import {
  Database,
  CheckCircle2,
  Clock,
  ShieldCheck,
  Info,
  Lock,
  Layers,
  Video,
  Users,
} from 'lucide-react';
import { syncStatusData } from '@/lib/data';
import { formatDateTr } from '@/lib/format';
import { ClubBadge } from '@/components/common/ClubBadge';

export default function DataFreshnessPage() {
  return (
    <div className="space-y-6">
      {/* Top Status & Completion Header */}
      <section className="rounded-2xl border border-[#1F2937] bg-[#111827] p-5 sm:p-6 space-y-5">
        <div className="flex flex-wrap items-start justify-between gap-4 border-b border-[#1F2937] pb-4">
          <div>
            <div className="flex items-center gap-2 text-xs font-semibold text-emerald-400 uppercase tracking-wider">
              <Database className="w-3.5 h-3.5" />
              Canlı Veri Şeffaflık &amp; Senkronizasyon Raporu
            </div>
            <h1 className="mt-1 text-xl sm:text-2xl font-bold text-slate-50">
              Veri Güncelliği, Hakkımızda &amp; Gizlilik İlkeleri
            </h1>
            <p className="mt-1 text-xs sm:text-sm text-slate-400">
              {syncStatusData.season} Trendyol Süper Lig ({syncStatusData.currentRound}. Hafta itibarıyla)
              verilerinin son güncellenme zamanı ve hafta bazlı tamamlanma durumu.
            </p>
          </div>

          <div className="rounded-xl border border-emerald-500/35 bg-emerald-500/10 px-4 py-2.5 text-right shrink-0">
            <div className="text-[10px] uppercase tracking-wider text-emerald-300 font-semibold">
              Son Veri Senkronizasyonu
            </div>
            <div className="tabular-nums text-sm sm:text-base font-bold text-slate-50 mt-0.5">
              {syncStatusData.lastSyncedAt}
            </div>
          </div>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
          <div className="rounded-xl border border-[#1F2937] bg-[#090D16] p-3">
            <div className="text-[10px] uppercase text-slate-400">Tam Detaylı Maç</div>
            <div className="tabular-nums text-lg font-black text-emerald-400 mt-0.5">
              {syncStatusData.detailedMatchesCount} / {syncStatusData.totalFinishedMatches}
            </div>
            <div className="text-[10px] text-slate-500">40 İstatistik + 2D Kadro</div>
          </div>

          <div className="rounded-xl border border-[#1F2937] bg-[#090D16] p-3">
            <div className="text-[10px] uppercase text-slate-400">Sırada Bekleyen</div>
            <div className="tabular-nums text-lg font-black text-amber-300 mt-0.5">
              {syncStatusData.pendingMatchesCount} Maç
            </div>
            <div className="text-[10px] text-slate-500">Skor &amp; Fikstür Hazır</div>
          </div>

          <div className="rounded-xl border border-[#1F2937] bg-[#090D16] p-3">
            <div className="text-[10px] uppercase text-slate-400">Gerçek Kadro Kapsamı</div>
            <div className="tabular-nums text-lg font-black text-cyan-300 mt-0.5">
              {syncStatusData.clubsWithRealSquads} / 18
            </div>
            <div className="text-[10px] text-slate-500">
              {syncStatusData.totalPlayersCount} Futbolcu
            </div>
          </div>

          <div className="rounded-xl border border-[#1F2937] bg-[#090D16] p-3">
            <div className="text-[10px] uppercase text-slate-400">Video Özeti (YouTube)</div>
            <div className="tabular-nums text-lg font-black text-rose-400 mt-0.5">
              {syncStatusData.highlightsCount} Maç
            </div>
            <div className="text-[10px] text-slate-500">Gömülü Oynatıcı</div>
          </div>

          <div className="col-span-2 sm:col-span-1 rounded-xl border border-[#1F2937] bg-[#090D16] p-3">
            <div className="text-[10px] uppercase text-slate-400">Bronze Önbellek</div>
            <div className="tabular-nums text-lg font-black text-slate-100 mt-0.5">
              {syncStatusData.bronzeFilesCount} JSON
            </div>
            <div className="text-[10px] text-slate-500">Kalıcı Arşiv</div>
          </div>
        </div>

        {/* Overall Progress Bar */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between text-xs">
            <span className="font-semibold text-slate-300">
              Oynanmış Maçların Tam Detay İndirme İlerlemesi
            </span>
            <span className="tabular-nums font-bold text-cyan-300">
              %{syncStatusData.completionPercent.toFixed(1)}
            </span>
          </div>
          <div className="h-2.5 w-full rounded-full bg-[#090D16] border border-[#1F2937] overflow-hidden">
            <div
              className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-emerald-400 transition-all"
              style={{ width: `${syncStatusData.completionPercent}%` }}
            />
          </div>
        </div>

        {/* Quick Section Anchors */}
        <div className="flex flex-wrap gap-2 pt-1 text-xs">
          <a
            href="#hafta-matrisi"
            className="rounded-lg border border-[#1F2937] bg-[#090D16] hover:border-cyan-500/40 px-3 py-1.5 text-slate-300 hover:text-cyan-300"
          >
            Hafta Bazlı Maç Matrisi
          </a>
          <a
            href="#kulup-kapsam"
            className="rounded-lg border border-[#1F2937] bg-[#090D16] hover:border-cyan-500/40 px-3 py-1.5 text-slate-300 hover:text-cyan-300"
          >
            18 Kulüp Kadro Kapsamı
          </a>
          <a
            href="#hakkimizda"
            className="rounded-lg border border-[#1F2937] bg-[#090D16] hover:border-cyan-500/40 px-3 py-1.5 text-slate-300 hover:text-cyan-300"
          >
            Hakkımızda &amp; Metodoloji
          </a>
          <a
            href="#gizlilik"
            className="rounded-lg border border-[#1F2937] bg-[#090D16] hover:border-cyan-500/40 px-3 py-1.5 text-slate-300 hover:text-cyan-300"
          >
            Gizlilik Politikası
          </a>
        </div>
      </section>

      {/* Round-by-Round Match Completion Matrix */}
      <section id="hafta-matrisi" className="space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h2 className="text-base sm:text-lg font-bold text-slate-100 flex items-center gap-2">
            <Layers className="w-4 h-4 text-cyan-400" />
            Hafta Bazlı Veri Tamamlanma Matrisi (11. Hafta → 1. Hafta)
          </h2>
          <div className="flex items-center gap-3 text-[11px] text-slate-400">
            <span className="inline-flex items-center gap-1 text-emerald-400">
              <CheckCircle2 className="w-3.5 h-3.5" /> Tam Detay (40 İstatistik + Kadro + Şut)
            </span>
            <span className="inline-flex items-center gap-1 text-amber-300">
              <Clock className="w-3.5 h-3.5" /> Skor &amp; Fikstür Hazır (Detay Sırada)
            </span>
          </div>
        </div>

        <div className="space-y-3">
          {syncStatusData.rounds.map((r) => {
            const pct = r.totalMatches > 0 ? Math.round((r.detailedMatches / r.totalMatches) * 100) : 0;
            return (
              <div
                key={`sync-round-${r.round}`}
                className="rounded-2xl border border-[#1F2937] bg-[#111827] overflow-hidden"
              >
                <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-3 border-b border-[#1F2937] bg-[#090D16]/70">
                  <div className="flex items-center gap-3">
                    <span className="tabular-nums rounded-lg bg-cyan-500/15 border border-cyan-500/35 px-2.5 py-0.5 text-xs font-bold text-cyan-300">
                      {r.round}. Hafta
                    </span>
                    <span className="tabular-nums text-xs text-slate-300">
                      <strong className="text-emerald-400">{r.detailedMatches}</strong> / {r.totalMatches}{' '}
                      Maç Tam Detaylı
                    </span>
                  </div>
                  <div className="flex items-center gap-2 w-36">
                    <div className="h-1.5 flex-1 rounded-full bg-[#1F2937] overflow-hidden">
                      <div
                        className="h-full bg-emerald-400 rounded-full"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                    <span className="tabular-nums text-[11px] font-bold text-slate-300 w-9 text-right">
                      %{pct}
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2.5 p-3">
                  {r.matches.map((m) => (
                    <Link
                      key={m.id}
                      href={`/matches/${m.id}`}
                      className={`group block rounded-xl border p-3 space-y-2 text-xs hover:border-cyan-500/50 transition-colors cursor-pointer ${
                        m.hasFullDetails
                          ? 'border-emerald-500/30 bg-[#090D16]/90'
                          : 'border-[#1F2937] bg-[#090D16]/45'
                      }`}
                    >
                      <div className="flex items-center justify-between gap-2 text-[11px] text-slate-400">
                        <span className="tabular-nums">{formatDateTr(m.date)}</span>
                        <div className="flex items-center gap-1.5">
                          {m.hasHighlight && (
                            <span
                              title="YouTube Özeti Mevcut"
                              className="inline-flex items-center gap-0.5 text-rose-400"
                            >
                              <Video className="w-3 h-3" />
                            </span>
                          )}
                          {m.hasFullDetails ? (
                            <span className="inline-flex items-center gap-1 rounded bg-emerald-500/15 border border-emerald-500/35 px-1.5 py-0.5 text-[10px] font-semibold text-emerald-300">
                              <CheckCircle2 className="w-3 h-3" /> Tam Detay
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 rounded bg-amber-500/10 border border-amber-500/30 px-1.5 py-0.5 text-[10px] font-semibold text-amber-300">
                              <Clock className="w-3 h-3" /> Detay Sırada
                            </span>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center justify-between gap-2">
                        <div className="inline-flex items-center gap-1.5 font-semibold text-slate-200 group-hover:text-cyan-300 truncate flex-1 min-w-0">
                          <ClubBadge clubId={m.homeClubId} size="xs" />
                          <span className="truncate">{m.homeClubName}</span>
                        </div>
                        <span className="tabular-nums shrink-0 rounded bg-[#111827] border border-[#1F2937] group-hover:border-cyan-400 px-2 py-0.5 font-bold text-cyan-300">
                          {m.homeScore} - {m.awayScore}
                        </span>
                        <div className="inline-flex items-center justify-end gap-1.5 font-semibold text-slate-200 group-hover:text-cyan-300 truncate flex-1 min-w-0 text-right">
                          <span className="truncate">{m.awayClubName}</span>
                          <ClubBadge clubId={m.awayClubId} size="xs" />
                        </div>
                      </div>

                      {m.hasFullDetails && (
                        <div className="tabular-nums text-[10px] text-slate-400 flex items-center justify-between pt-1 border-t border-[#1F2937]/70">
                          <span>{m.statsCount} İstatistik</span>
                          <span>{m.shotsCount} Şut Bölgesi</span>
                          <span>{m.eventsCount} Olay</span>
                        </div>
                      )}
                    </Link>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* 18-Club Squad & Match Data Coverage Table */}
      <section
        id="kulup-kapsam"
        className="rounded-2xl border border-[#1F2937] bg-[#111827] overflow-hidden"
      >
        <div className="px-4 py-3.5 border-b border-[#1F2937] flex items-center gap-2">
          <Users className="w-4 h-4 text-emerald-400" />
          <h2 className="text-sm sm:text-base font-bold text-slate-100">
            18 Süper Lig Kulübü — Kadro &amp; Maç Veri Kapsamı
          </h2>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#090D16]/85 text-[11px] uppercase text-slate-400 border-b border-[#1F2937]">
              <tr>
                <th className="sticky left-0 z-10 bg-[#090D16] px-4 py-2.5">Kulüp</th>
                <th className="px-3 py-2.5 text-center">Kadro Durumu</th>
                <th className="px-3 py-2.5 text-center">Kayıtlı Oyuncu</th>
                <th className="px-3 py-2.5 text-center">Oynanan Maç</th>
                <th className="px-4 py-2.5 text-right">Tam Detaylı Maç</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1F2937]/70">
              {syncStatusData.clubCoverage.map((c) => (
                <tr key={c.clubId} className="hover:bg-[#1E293B]/60">
                  <td className="sticky left-0 z-10 bg-[#111827] px-4 py-2.5">
                    <Link
                      href={`/clubs/${c.clubId}`}
                      className="inline-flex items-center gap-2 font-semibold text-slate-100 hover:text-cyan-300"
                    >
                      <ClubBadge clubId={c.clubId} size="xs" />
                      <span>{c.clubName}</span>
                    </Link>
                  </td>
                  <td className="px-3 py-2.5 text-center">
                    {c.hasRealSquad ? (
                      <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/15 border border-emerald-500/35 px-2 py-0.5 text-[10px] font-semibold text-emerald-300">
                        <CheckCircle2 className="w-3 h-3" /> Gerçek 2026/27 Kadrosu
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 rounded-full bg-amber-500/15 border border-amber-500/35 px-2 py-0.5 text-[10px] font-semibold text-amber-300">
                        <Clock className="w-3 h-3" /> Bekleniyor
                      </span>
                    )}
                  </td>
                  <td className="px-3 py-2.5 text-center tabular-nums text-slate-200 font-semibold">
                    {c.squadCount}
                  </td>
                  <td className="px-3 py-2.5 text-center tabular-nums text-slate-300">
                    {c.playedMatches}
                  </td>
                  <td className="px-4 py-2.5 text-right tabular-nums font-bold text-cyan-300">
                    {c.detailedMatches} / {c.playedMatches}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* About & Methodology + Privacy Policy */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <section
          id="hakkimizda"
          className="rounded-2xl border border-[#1F2937] bg-[#111827] p-5 space-y-3"
        >
          <div className="flex items-center gap-2 border-b border-[#1F2937] pb-3">
            <Info className="w-4 h-4 text-cyan-400" />
            <h2 className="text-base font-bold text-slate-100">Hakkımızda &amp; Veri Metodolojisi</h2>
          </div>
          <div className="space-y-2.5 text-xs sm:text-sm text-slate-300 leading-relaxed">
            <p>
              <strong className="text-slate-100">Süper Lig İstatistik &amp; Analiz Merkezi</strong>, Trendyol Süper Lig
              kulüplerini, futbolcu kadro değerlerini, anatomik sakatlık geçmişlerini ve maç içi
              istatistiklerini çapraz bağlantılı statik bir mimaride sunar.
            </p>
            <p>
              <strong className="text-cyan-300">Bronze → Gold Veri Hattı:</strong> Maç skorları,
              puan durumu, 2D saha dizilişleri, kale hedef şut bölgeleri ve gol özetleri kota
              korumalı veri toplayıcı tarafından günlük olarak toplanır, ham JSON önbelleğinde
              (Bronze) saklanır ve doğrulama sonrası statik Gold JSON dosyalarına dönüştürülür.
            </p>
            <p>
              <strong className="text-emerald-400">Sıfır Sunucu Mimarisi:</strong> Tüm sayfalar
              derleme anında statik HTML olarak üretilir (`output: &apos;export&apos;`). Çalışma anında
              harici veritabanına istek atılmaz; böylece yüksek hız ve sıfır gecikme sağlanır.
            </p>
          </div>
        </section>

        <section
          id="gizlilik"
          className="rounded-2xl border border-[#1F2937] bg-[#111827] p-5 space-y-3"
        >
          <div className="flex items-center gap-2 border-b border-[#1F2937] pb-3">
            <Lock className="w-4 h-4 text-emerald-400" />
            <h2 className="text-base font-bold text-slate-100">
              Gizlilik Politikası &amp; Kullanım İlkeleri
            </h2>
          </div>
          <div className="space-y-2.5 text-xs sm:text-sm text-slate-300 leading-relaxed">
            <p className="flex items-start gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span>
                <strong className="text-slate-100">Çerezsiz ve Takipçisiz Yapı:</strong> Bu portal
                ziyaretçilerden kişisel veri toplamaz, üçüncü taraf reklam çerezleri veya analitik
                izleyicileri kullanmaz.
              </span>
            </p>
            <p>
              <strong className="text-slate-100">Yerel İstemci Araması:</strong> <kbd className="rounded bg-[#090D16] border border-[#1F2937] px-1.5 py-0.5 text-[11px]">⌘K</kbd> arama çubuğuna yazdığınız
              sorgular herhangi bir sunucuya gönderilmez; tamamen tarayıcınızın belleğindeki yerel
              veri üzerinde çalışır.
            </p>
            <p>
              <strong className="text-slate-100">API Güvenliği &amp; Telif:</strong> Gömülü YouTube
              maç özetleri resmi yayıncı bağlantılarından iframe üzerinden sunulur. Veri erişim
              anahtarları yalnızca güvenli sunucu gizli anahtarları içinde saklanır ve ön yüze
              kesinlikle aktarılmaz.
            </p>
          </div>
        </section>
      </div>
    </div>
  );
}
