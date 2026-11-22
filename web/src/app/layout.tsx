import type { Metadata } from 'next';
import './globals.css';
import { AppShell } from '@/components/layout/AppShell';

export const metadata: Metadata = {
  title: 'Süper Lig İstatistik & Analiz Merkezi',
  description:
    'Trendyol Süper Lig kulüp kadro değerleri, çapraz bağlantılı futbolcu profilleri, etkileşimli sakatlık geçmişi ve Poisson maç analizleri.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="tr" className="dark">
      <body className="bg-[#090D16] text-slate-100 antialiased selection:bg-cyan-500/30 selection:text-cyan-200">
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
