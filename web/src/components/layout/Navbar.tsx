'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Search, Activity, Trophy, Swords, TrendingUp, Globe } from 'lucide-react';
import { superLigClubs } from '@/lib/data';
import { ClubBadge } from '@/components/common/ClubBadge';
import { LOCALES } from '@/lib/i18n';
import { useLanguage } from '@/components/layout/LanguageProvider';

interface NavbarProps {
  onOpenSearch: () => void;
}

const NAV_ITEMS = [
  { href: '/', label: 'Genel Bakış', icon: Activity },
  { href: '/standings', label: 'Puan Durumu', icon: Trophy },
  { href: '/matches', label: 'Fikstür & Maçlar', icon: Swords },
  { href: '/market-and-predictions', label: 'Piyasa & Analiz', icon: TrendingUp },
];

export function Navbar({ onOpenSearch }: NavbarProps) {
  const pathname = usePathname();
  const { lang, setLang } = useLanguage();

  return (
    <header className="sticky top-0 z-40 border-b border-[#1F2937] bg-[#090D16]/90 backdrop-blur-md">
      <div className="mx-auto max-w-7xl px-3 sm:px-6">
        <div className="flex h-14 items-center justify-between gap-3">
          <div className="flex items-center gap-6">
            <Link href="/" className="flex items-center gap-2.5 group shrink-0">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-cyan-500 to-emerald-500 text-[#090D16] font-black text-sm shadow-[0_0_16px_rgba(6,182,212,0.35)]">
                SL
              </div>
              <div className="leading-none">
                <div className="text-sm font-bold tracking-wide text-slate-100 group-hover:text-cyan-300 transition-colors">
                  SÜPER LİG
                </div>
                <div className="text-[10px] font-medium tracking-widest text-cyan-400 uppercase">
                  İstatistik &amp; Analiz
                </div>
              </div>
            </Link>

            <nav className="hidden md:flex items-center gap-1">
              {NAV_ITEMS.map((item) => {
                const Icon = item.icon;
                const active =
                  item.href === '/'
                    ? pathname === '/'
                    : pathname?.startsWith(item.href);
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
                      active
                        ? 'bg-[#1E293B] text-cyan-300 border border-cyan-500/30'
                        : 'text-slate-300 hover:text-white hover:bg-[#111827]'
                    }`}
                  >
                    <Icon className="w-3.5 h-3.5" />
                    {item.label}
                  </Link>
                );
              })}
            </nav>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <button
              type="button"
              onClick={onOpenSearch}
              className="flex items-center justify-between gap-2 rounded-xl border border-[#1F2937] bg-[#111827] hover:border-cyan-500/40 hover:bg-[#1E293B]/70 px-2.5 sm:px-3 py-1.5 text-xs text-slate-400 transition-all w-32 sm:w-64"
            >
              <span className="flex items-center gap-2 truncate">
                <Search className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                <span className="truncate">Oyuncu, kulüp, maç ara...</span>
              </span>
              <kbd className="hidden sm:inline-flex items-center gap-0.5 rounded bg-[#090D16] border border-[#1F2937] px-1.5 py-0.5 text-[10px] font-mono text-slate-400">
                ⌘K
              </kbd>
            </button>

            <div
              data-no-i18n="true"
              className="inline-flex items-center rounded-xl border border-[#1F2937] bg-[#111827] p-0.5"
              role="group"
              aria-label="Language"
            >
              <Globe className="w-3.5 h-3.5 text-slate-500 ml-1.5 mr-1 hidden sm:block" />
              {LOCALES.map((loc) => {
                const isSelected = lang === loc.code;
                return (
                  <button
                    key={loc.code}
                    type="button"
                    onClick={() => setLang(loc.code)}
                    title={loc.name}
                    className={`rounded-lg px-2 py-1 text-[10.5px] font-bold transition-colors ${
                      isSelected
                        ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                        : 'text-slate-400 hover:text-slate-100 border border-transparent'
                    }`}
                  >
                    {loc.label}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* 18-Club Quick Crest Ribbon */}
        <div className="flex items-center gap-1.5 overflow-x-auto no-scrollbar py-2 border-t border-[#1F2937]/70">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-500 shrink-0 pr-1">
            Kulüpler:
          </span>
          {superLigClubs.map((club) => {
            const active = pathname === `/clubs/${club.id}`;
            return (
              <Link
                key={club.id}
                href={`/clubs/${club.id}`}
                title={`${club.name} Kadrosu & Taktik DNA`}
                className={`flex items-center gap-1.5 rounded-lg px-1.5 py-1 transition-all shrink-0 border ${
                  active
                    ? 'bg-[#1E293B] border-cyan-500/50 text-cyan-300'
                    : 'border-transparent hover:bg-[#111827] hover:border-[#1F2937] text-slate-300'
                }`}
              >
                <ClubBadge clubId={club.id} size="xs" />
                <span className="text-[11px] font-medium hidden lg:inline">{club.shortName}</span>
              </Link>
            );
          })}
        </div>
      </div>
    </header>
  );
}
