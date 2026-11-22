'use client';

import React, { useMemo, useState } from 'react';
import Link from 'next/link';
import { ExternalLink, Film, PlayCircle, Search, Users } from 'lucide-react';
import type { HighlightClip } from '@/types/football';

interface MatchHighlightPlayerProps {
  highlightEmbedUrl: string;
  highlightClips?: HighlightClip[];
  homeClubId: string;
  homeClubName: string;
  awayClubId: string;
  awayClubName: string;
  round: number;
}

function toYoutubeWatchUrl(embedUrl: string): string {
  const match = embedUrl.match(/youtube(?:-nocookie)?\.com\/embed\/([a-zA-Z0-9_-]{11})/);
  if (match) {
    return `https://www.youtube.com/watch?v=${match[1]}`;
  }
  return embedUrl;
}

export function MatchHighlightPlayer({
  highlightEmbedUrl,
  highlightClips,
  homeClubId,
  homeClubName,
  awayClubId,
  awayClubName,
  round,
}: MatchHighlightPlayerProps) {
  const clips = useMemo<HighlightClip[]>(() => {
    const validClips = (highlightClips ?? []).filter(
      (c) => c.embedUrl && !c.embedUrl.includes('jfKfPfyJRdk')
    );
    if (validClips.length > 0) return validClips;

    if (highlightEmbedUrl && !highlightEmbedUrl.includes('jfKfPfyJRdk')) {
      return [
        {
          title: 'Maç Özeti',
          embedUrl: highlightEmbedUrl,
          category: 'match-highlights',
        },
      ];
    }
    return [];
  }, [highlightClips, highlightEmbedUrl]);

  const [selectedIndex, setSelectedIndex] = useState(0);
  const safeIdx = selectedIndex < clips.length ? selectedIndex : 0;
  const activeClip = clips[safeIdx];

  const watchUrl = activeClip ? toYoutubeWatchUrl(activeClip.embedUrl) : '';
  const searchQuery = encodeURIComponent(
    `beIN SPORTS Türkiye ${homeClubName} ${awayClubName} ${round}. hafta maç özeti`
  );
  const ytSearchUrl = `https://www.youtube.com/results?search_query=${searchQuery}`;

  return (
    <section className="lg:col-span-6 rounded-2xl border border-[#1F2937] bg-[#111827] p-4 sm:p-5 space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[#1F2937] pb-3">
        <div className="flex items-center gap-2">
          <PlayCircle className="w-4 h-4 text-rose-400" />
          <h2 className="text-sm sm:text-base font-bold text-slate-100">
            Maçın Golleri &amp; Video Özeti
          </h2>
        </div>

        {activeClip ? (
          <a
            href={watchUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 rounded-lg border border-rose-500/35 bg-rose-500/10 px-2.5 py-1 text-[11px] font-semibold text-rose-300 hover:bg-rose-500/20 transition-colors"
          >
            <span>YouTube&apos;da İzle</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        ) : (
          <span className="text-[11px] text-slate-400">TR Erişim Doğrulaması</span>
        )}
      </div>

      {clips.length > 1 && (
        <div className="flex flex-wrap items-center gap-1.5">
          {clips.map((clip, idx) => {
            const isSelected = idx === safeIdx;
            const badgeText =
              clip.category === 'match-highlights'
                ? idx === 0
                  ? 'Ana Maç Özeti'
                  : clip.title
                : clip.title.length > 34
                  ? `${clip.title.slice(0, 34)}…`
                  : clip.title;
            return (
              <button
                key={`${clip.embedUrl}-${idx}`}
                type="button"
                onClick={() => setSelectedIndex(idx)}
                className={`inline-flex items-center gap-1.5 rounded-lg border px-2.5 py-1 text-[11px] font-semibold transition-colors ${
                  isSelected
                    ? 'border-cyan-500/45 bg-cyan-500/15 text-cyan-300'
                    : 'border-[#1F2937] bg-[#090D16] text-slate-400 hover:text-slate-200'
                }`}
              >
                <Film className="w-3 h-3 shrink-0" />
                <span>{badgeText}</span>
              </button>
            );
          })}
        </div>
      )}

      {activeClip ? (
        <div className="relative aspect-video w-full overflow-hidden rounded-xl border border-[#1F2937] bg-[#090D16]">
          <iframe
            key={activeClip.embedUrl}
            src={activeClip.embedUrl}
            title={`${homeClubName} - ${awayClubName} · ${activeClip.title}`}
            className="absolute inset-0 h-full w-full"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
        </div>
      ) : (
        <div className="flex aspect-video w-full flex-col items-center justify-center gap-3 rounded-xl border border-[#1F2937] bg-[#090D16] p-6 text-center">
          <PlayCircle className="w-10 h-10 text-slate-500" />
          <div className="space-y-1 max-w-sm">
            <p className="text-sm font-semibold text-slate-200">
              Türkiye&apos;de açık gömülü özet klibi bulunamadı
            </p>
            <p className="text-xs text-slate-400">
              Yayıncı kuruluş coğrafi kısıtı veya arşiv gecikmesi nedeniyle YouTube üzerinden resmi özeti doğrudan arayabilirsiniz.
            </p>
          </div>
          <a
            href={ytSearchUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 rounded-xl border border-cyan-500/40 bg-cyan-500/15 px-3.5 py-2 text-xs font-semibold text-cyan-300 hover:bg-cyan-500/25 transition-colors"
          >
            <Search className="w-3.5 h-3.5" />
            <span>YouTube&apos;da Resmi Özeti Ara</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      )}

      <div className="flex items-center justify-between text-[11px] text-slate-400">
        <span>
          <Link href={`/clubs/${homeClubId}`} className="hover:text-cyan-300">
            {homeClubName}
          </Link>{' '}
          vs{' '}
          <Link href={`/clubs/${awayClubId}`} className="hover:text-cyan-300">
            {awayClubName}
          </Link>
        </span>
        <span className="inline-flex items-center gap-1">
          <Users className="w-3 h-3" /> {round}. Hafta Özeti
        </span>
      </div>
    </section>
  );
}
