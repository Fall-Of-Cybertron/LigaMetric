'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { Database } from 'lucide-react';
import { Navbar } from '@/components/layout/Navbar';
import { MobileBottomNav } from '@/components/layout/MobileBottomNav';
import { SearchModal } from '@/components/search/SearchModal';
import { LanguageProvider } from '@/components/layout/LanguageProvider';
import { syncStatusData } from '@/lib/data';

export function AppShell({ children }: { children: React.ReactNode }) {
  const [searchOpen, setSearchOpen] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setSearchOpen((prev) => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <LanguageProvider>
      <div className="min-h-screen flex flex-col bg-[#090D16] text-slate-100">
        <Navbar onOpenSearch={() => setSearchOpen(true)} />
        <main className="flex-1 mx-auto w-full max-w-7xl px-3 sm:px-6 py-5">
          {children}
        </main>
        <footer className="border-t border-[#1F2937] bg-[#090D16] py-6 pb-24 md:pb-6 text-xs text-slate-400">
          <div className="mx-auto max-w-7xl px-3 sm:px-6 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <span className="font-semibold text-slate-200">Süper Lig İstatistik &amp; Analiz Merkezi</span> ·{' '}
              <span>Statik Gold JSON Mimarisi (`output: &apos;export&apos;`)</span>
            </div>

              <Link
                href="/veri-guncelligi"
                className="inline-flex items-center gap-2 rounded-xl border border-emerald-500/35 bg-emerald-500/10 hover:bg-emerald-500/15 px-3 py-1.5 text-[11px] text-emerald-300 transition-colors w-fit"
              >
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <Database className="w-3.5 h-3.5" />
                <span className="tabular-nums">
                  Son Güncelleme: <strong>{syncStatusData.lastSyncedAt}</strong> · Detaylı Maç:{' '}
                  <strong>
                    {syncStatusData.detailedMatchesCount}/{syncStatusData.totalFinishedMatches}
                  </strong>{' '}
                  (%{syncStatusData.completionPercent.toFixed(0)})
                </span>
              </Link>
            </div>

            <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-[#1F2937]/70 text-[11px]">
              <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5">
                <Link href="/veri-guncelligi" className="text-cyan-400 hover:text-cyan-300 font-medium">
                  Veri Güncelliği Raporu
                </Link>
                <Link href="/veri-guncelligi#hakkimizda" className="hover:text-cyan-300">
                  Hakkımızda &amp; Metodoloji
                </Link>
                <Link href="/veri-guncelligi#gizlilik" className="hover:text-cyan-300">
                  Gizlilik Politikası
                </Link>
              </div>
            <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5 text-slate-500">
              <Link href="/" className="hover:text-cyan-400">Genel Bakış</Link>
              <Link href="/standings" className="hover:text-cyan-400">Puan Durumu</Link>
              <Link href="/matches" className="hover:text-cyan-400">Fikstür &amp; Maçlar</Link>
              <Link href="/market-and-predictions" className="hover:text-cyan-400">Piyasa &amp; Analiz</Link>
            </div>
            </div>
          </div>
        </footer>
        <MobileBottomNav onOpenSearch={() => setSearchOpen(true)} />
        <SearchModal isOpen={searchOpen} onClose={() => setSearchOpen(false)} />
      </div>
    </LanguageProvider>
  );
}
