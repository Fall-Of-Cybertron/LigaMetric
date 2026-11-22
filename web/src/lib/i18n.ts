export type Locale = 'tr' | 'en' | 'de';

export const LOCALES: { code: Locale; label: string; name: string }[] = [
  { code: 'tr', label: 'TR', name: 'Türkçe' },
  { code: 'en', label: 'EN', name: 'English' },
  { code: 'de', label: 'DE', name: 'Deutsch' },
];

const EXACT_TRANSLATIONS: Record<string, { en: string; de: string }> = {
  // Brand & Navigation
  'SÜPER LİG': { en: 'SÜPER LİG', de: 'SÜPER LİG' },
  'İstatistik & Analiz': { en: 'Statistics & Analytics', de: 'Statistik & Analyse' },
  'İstihbarat & Değer': { en: 'Statistics & Analytics', de: 'Statistik & Analyse' },
  'Süper Lig İstatistik & Analiz Merkezi': {
    en: 'Süper Lig Statistics & Analytics Center',
    de: 'Süper Lig Statistik- & Analysezentrum',
  },
  'Süper Lig İstihbarat Portalı': {
    en: 'Süper Lig Statistics & Analytics Center',
    de: 'Süper Lig Statistik- & Analysezentrum',
  },
  "Statik Gold JSON Mimarisi (`output: 'export'`)": {
    en: "Static Gold JSON Architecture (`output: 'export'`)",
    de: "Statische Gold-JSON-Architektur (`output: 'export'`)",
  },
  'Süper Lig İstihbarat & Transfermarkt Portalı': {
    en: 'Süper Lig Statistics & Analytics Center',
    de: 'Süper Lig Statistik- & Analysezentrum',
  },
  'Genel Bakış': { en: 'Overview', de: 'Übersicht' },
  'Lig Vitrini': { en: 'Overview', de: 'Übersicht' },
  'Puan Durumu': { en: 'Standings', de: 'Tabelle' },
  'Puan & Kulüpler': { en: 'Standings', de: 'Tabelle' },
  'Fikstür & Maçlar': { en: 'Fixtures & Matches', de: 'Spielplan & Spiele' },
  'Maç Merkezi': { en: 'Fixtures & Matches', de: 'Spielplan & Spiele' },
  'Maç Detayı →': { en: 'Match Details →', de: 'Spieldetails →' },
  'Maç Merkezi →': { en: 'Match Details →', de: 'Spieldetails →' },
  'Piyasa & Analiz': { en: 'Market & Analytics', de: 'Markt & Analyse' },
  'Transfer & Tahmin': { en: 'Market & Analytics', de: 'Markt & Analyse' },
  'Trendyol Süper Lig Fikstür & Maçlar': {
    en: 'Trendyol Süper Lig Fixtures & Matches',
    de: 'Trendyol Süper Lig Spielplan & Spiele',
  },
  'Süper Lig İstatistik, Kadro Değeri & Maç Analizleri': {
    en: 'Süper Lig Statistics, Squad Valuations & Match Analytics',
    de: 'Süper Lig Statistiken, Kaderwerte & Spielanalysen',
  },
  "Süper Lig'in En Değerli 10 Futbolcusu": {
    en: 'Top 10 Most Valuable Süper Lig Players',
    de: 'Die 10 wertvollsten Spieler der Süper Lig',
  },
  'Piyasa Değeri & Sözleşme Analizi': {
    en: 'Market Value & Contract Analytics',
    de: 'Marktwert- & Vertragsanalyse',
  },
  'Piyasa Değeri, Sözleşme Takvimi & Tahmin Analizi': {
    en: 'Market Value, Contract Schedule & Prediction Analytics',
    de: 'Marktwert, Vertragskalender & Prognoseanalyse',
  },
  'Sözleşmesi Bitecek Oyuncular, Transfer Gündemi & Model Performansı': {
    en: 'Expiring Contracts, Transfer News & Model Performance',
    de: 'Auslaufende Verträge, Transfernews & Modellleistung',
  },
  'Sözleşme Bitiş Takvimi': { en: 'Contract Expiry Schedule', de: 'Vertragsende-Kalender' },
  'Poisson Tahmin Modeli Doğruluk Analizi': {
    en: 'Poisson Prediction Model Accuracy Analysis',
    de: 'Poisson-Prognosemodell Genauigkeitsanalyse',
  },
  'Performans & Kariyer': { en: 'Performance & Career', de: 'Leistung & Karriere' },
  'Piyasa Değeri & Transferler': { en: 'Market Value & Transfers', de: 'Marktwert & Transfers' },
  'Sakatlık Geçmişi': { en: 'Injury History', de: 'Verletzungshistorie' },
  'Piyasa Değeri & Sözleşme Özeti': { en: 'Market Value & Contract Summary', de: 'Marktwert- & Vertragsübersicht' },
  'Sakatlık & Kondisyon Özeti': { en: 'Injury & Fitness Summary', de: 'Verletzungs- & Fitnessübersicht' },
  'Piyasa & Transferler Sekmesine Git': { en: 'Go to Market & Transfers Tab', de: 'Zum Tab Markt & Transfers' },
  'Sakatlık Geçmişi Sekmesine Git': { en: 'Go to Injury History Tab', de: 'Zum Tab Verletzungshistorie' },
  'Transfer Gündemi': { en: 'Transfer Market News', de: 'Transfermarkt-Gerüchte' },
  'Piyasa & Analiz →': { en: 'Market & Analytics →', de: 'Markt & Analyse →' },
  '2026 Süper Lig Sezon İstatistik Özeti': {
    en: '2026 Süper Lig Season Stats Summary',
    de: '2026 Süper Lig Saisonstatistik-Übersicht',
  },
  'Gol / xG': { en: 'Goals / xG', de: 'Tore / xG' },
  'Asist / xA': { en: 'Assists / xA', de: 'Vorlagen / xA' },
  'Disiplin': { en: 'Discipline', de: 'Disziplin' },
  'Oyuncu Profil Kategorileri': { en: 'Player Profile Sections', de: 'Spielerprofil-Kategorien' },
  'Toplam Kayıt': { en: 'Total Records', de: 'Einträge gesamt' },
  'Uzak Kalınan': { en: 'Days Missed', de: 'Ausfallzeit' },
  'Kaçırılan Maç': { en: 'Games Missed', de: 'Verpasste Spiele' },
  '. Hafta Görünümü': { en: ' · Round Overview', de: '. Spieltag Übersicht' },
  '. Hafta Maç Sonuçları': { en: ' · Round Match Results', de: '. Spieltag Ergebnisse' },
  'Oyuncu, kulüp, maç ara...': { en: 'Search player, club, match...', de: 'Spieler, Verein, Spiel suchen...' },
  'Kulüpler:': { en: 'Clubs:', de: 'Vereine:' },
  'Ana Sayfa': { en: 'Home', de: 'Start' },
  'Puan & Kulüp': { en: 'Table & Clubs', de: 'Tabelle' },
  'Maçlar': { en: 'Matches', de: 'Spiele' },
  'Piyasa': { en: 'Market', de: 'Markt' },
  'Ara': { en: 'Search', de: 'Suche' },
  'Vitrin': { en: 'Overview', de: 'Übersicht' },

  // Footer & Transparency
  'Veri Güncelliği Raporu': { en: 'Data Freshness Report', de: 'Datenaktualitätsbericht' },
  'Hakkımızda & Metodoloji': { en: 'About & Methodology', de: 'Über uns & Methodik' },
  'Gizlilik Politikası': { en: 'Privacy Policy', de: 'Datenschutz' },
  'Son Güncelleme:': { en: 'Last Updated:', de: 'Letztes Update:' },
  'Detaylı Maç:': { en: 'Detailed Matches:', de: 'Detailspiele:' },
  'Canlı Veri Şeffaflık & Senkronizasyon Raporu': {
    en: 'Live Data Transparency & Sync Report',
    de: 'Live-Datentransparenz & Sync-Bericht',
  },
  'Veri Güncelliği, Hakkımızda & Gizlilik İlkeleri': {
    en: 'Data Freshness, About & Privacy Principles',
    de: 'Datenaktualität, Über uns & Datenschutz',
  },
  'Son Veri Senkronizasyonu': { en: 'Latest Data Sync', de: 'Letzte Datensynchronisierung' },
  'Tam Detaylı Maç': { en: 'Full Detailed Matches', de: 'Vollständige Detailspiele' },
  '40 İstatistik + 2D Kadro': { en: '40 Stats + 2D Lineup', de: '40 Statistiken + 2D-Aufstellung' },
  'Sırada Bekleyen': { en: 'Queued Matches', de: 'Ausstehende Spiele' },
  'Skor & Fikstür Hazır': { en: 'Score & Fixture Ready', de: 'Ergebnis & Spielplan bereit' },
  'Skor & Fikstür Hazır (Detay Sırada)': {
    en: 'Score & Fixture Ready (Details Queued)',
    de: 'Ergebnis bereit (Details folgen)',
  },
  'Gerçek Kadro Kapsamı': { en: 'Real Squad Coverage', de: 'Reale Kaderabdeckung' },
  'Video Özeti (YouTube)': { en: 'Video Highlights (YouTube)', de: 'Video-Highlights (YouTube)' },
  'Gömülü Oynatıcı': { en: 'Embedded Player', de: 'Eingebetteter Player' },
  'Bronze Önbellek': { en: 'Bronze Cache', de: 'Bronze-Cache' },
  'Kalıcı Arşiv': { en: 'Permanent Archive', de: 'Dauerarchiv' },
  'Oynanmış Maçların Tam Detay İndirme İlerlemesi': {
    en: 'Full Match Detail Ingestion Progress',
    de: 'Fortschritt der vollständigen Spieldatenerfassung',
  },
  'Hafta Bazlı Veri Tamamlanma Matrisi (11. Hafta → 1. Hafta)': {
    en: 'Round-by-Round Data Completion Matrix (R11 → R1)',
    de: 'Datenvollständigkeit pro Spieltag (11. → 1. Spieltag)',
  },
  'Tam Detay': { en: 'Full Detail', de: 'Volldetails' },
  'Detay Sırada': { en: 'Queued', de: 'Ausstehend' },
  '18 Süper Lig Kulübü — Kadro & Maç Veri Kapsamı': {
    en: '18 Süper Lig Clubs — Squad & Match Data Coverage',
    de: '18 Süper-Lig-Vereine — Kader- & Spieldatenabdeckung',
  },
  'Kadro Durumu': { en: 'Squad Status', de: 'Kaderstatus' },
  'Kayıtlı Oyuncu': { en: 'Registered Players', de: 'Registrierte Spieler' },
  'Oynanan Maç': { en: 'Matches Played', de: 'Gespielte Spiele' },
  'Gerçek 2026/27 Kadrosu': { en: 'Real 2026/27 Squad', de: 'Realer Kader 2026/27' },
  'Bekleniyor': { en: 'Pending', de: 'Ausstehend' },
  'Hakkımızda & Veri Metodolojisi': { en: 'About & Data Methodology', de: 'Über uns & Datenmethodik' },
  'Bronze → Gold Veri Hattı:': { en: 'Bronze → Gold Data Pipeline:', de: 'Bronze → Gold Datenpipeline:' },
  'Sıfır Sunucu Mimarisi:': { en: 'Zero-Server Static Architecture:', de: 'Serverlose statische Architektur:' },
  'Gizlilik Politikası & Kullanım İlkeleri': { en: 'Privacy Policy & Terms', de: 'Datenschutz & Nutzungsrichtlinien' },
  'Çerezsiz ve Takipçisiz Yapı:': { en: 'Cookie-Free & Tracker-Free:', de: 'Ohne Cookies & Tracker:' },
  'Yerel İstemci Araması:': { en: 'Local Client-Side Search:', de: 'Lokale Client-Suche:' },
  'API Güvenliği & Telif:': { en: 'API Security & Copyright:', de: 'API-Sicherheit & Urheberrecht:' },
  ', Trendyol Süper Lig kulüplerini, futbolcu kadro değerlerini, anatomik sakatlık geçmişlerini ve maç içi istatistiklerini çapraz bağlantılı statik bir mimaride sunar.': {
    en: ' delivers Trendyol Süper Lig clubs, squad valuations, anatomical injury histories, and match analytics in a cross-linked static architecture.',
    de: ' präsentiert Vereine, Kaderwerte, anatomische Verletzungshistorien und Spielstatistiken der Trendyol Süper Lig in einer verknüpften statischen Architektur.',
  },
  'Maç skorları, puan durumu, 2D saha dizilişleri, kale hedef şut bölgeleri ve gol özetleri kota korumalı veri toplayıcı tarafından günlük olarak toplanır, ham JSON önbelleğinde (Bronze) saklanır ve doğrulama sonrası statik Gold JSON dosyalarına dönüştürülür.': {
    en: 'Match scores, standings, 2D lineups, goal target zones, and video highlights are gathered daily by a quota-guarded collector into Bronze storage and transformed into verified Gold JSON datasets.',
    de: 'Spielergebnisse, Tabellen, 2D-Aufstellungen, Schusszonen und Highlights werden täglich über einen kontingentgeschützten Sammler im Bronze-Archiv gespeichert und in verifizierte Gold-JSONs überführt.',
  },
  'Tüm sayfalar derleme anında statik HTML olarak üretilir (`output: \'export\'`). Çalışma anında harici veritabanına istek atılmaz; böylece yüksek hız ve sıfır gecikme sağlanır.': {
    en: 'All pages are pre-rendered as static HTML at build time (`output: \'export\'`). No runtime database queries are made, ensuring maximum speed and zero latency.',
    de: 'Alle Seiten werden beim Build als statisches HTML generiert (`output: \'export\'`). Zur Laufzeit erfolgen keine externen Datenbankabfragen für maximale Geschwindigkeit.',
  },
  'Bu portal ziyaretçilerden kişisel veri toplamaz, üçüncü taraf reklam çerezleri veya analitik izleyicileri kullanmaz.': {
    en: 'This portal collects no personal visitor data and uses no third-party advertising cookies or analytics trackers.',
    de: 'Dieses Portal erhebt keine personenbezogenen Daten und verwendet weder Werbe-Cookies noch Analyse-Tracker.',
  },
  'arama çubuğuna yazdığınız sorgular herhangi bir sunucuya gönderilmez; tamamen tarayıcınızın belleğindeki yerel veri üzerinde çalışır.': {
    en: 'queries typed into the search bar are never sent to any server; search runs strictly in your browser over local dataset memory.',
    de: 'Suchanfragen werden an keinen Server gesendet, sondern laufen vollständig lokal im Arbeitsspeicher Ihres Browsers.',
  },
  'Gömülü YouTube maç özetleri resmi yayıncı bağlantılarından iframe üzerinden sunulur. Veri erişim anahtarları yalnızca güvenli sunucu gizli anahtarları içinde saklanır ve ön yüze kesinlikle aktarılmaz.': {
    en: 'Embedded YouTube match highlights are served from official broadcaster links via iframe. Data API keys are stored solely in server secrets and never exposed to the frontend.',
    de: 'Eingebettete YouTube-Highlights werden über offizielle Senderlinks im iframe bereitgestellt. API-Schlüssel bleiben sicher auf dem Server und werden nie an das Frontend übertragen.',
  },

  // Search Modal
  'Global Oyuncu ve Kulüp Arama': { en: 'Global Player & Club Search', de: 'Globale Spieler- & Vereinssuche' },
  'Oyuncu, kulüp, teknik direktör veya maç ara (ör. Osimhen, Uğurcan, Şişli...)': {
    en: 'Search player, club, coach, or match...',
    de: 'Spieler, Verein, Trainer oder Spiel suchen...',
  },
  'Temizle': { en: 'Clear', de: 'Leeren' },
  'Kapat': { en: 'Close', de: 'Schließen' },
  'En Değerli Yıldızlar': { en: 'Top Valued Stars', de: 'Wertvollste Stars' },
  'Eşleşen Oyuncular': { en: 'Matching Players', de: 'Gefundene Spieler' },
  'Kulüpler': { en: 'Clubs', de: 'Vereine' },
  'Türkçe karakter duyarsız arama aktif (İ→i, Ş→s, Ğ→g, Ç→c)': {
    en: 'Diacritic-insensitive search active (İ→i, Ş→s, Ğ→g, Ç→c)',
    de: 'Diakritika-tolerante Suche aktiv (İ→i, Ş→s, Ğ→g, Ç→c)',
  },
  'Enter: İlk sonuca git · ESC: Kapat': {
    en: 'Enter: Go to first result · ESC: Close',
    de: 'Enter: Erstes Ergebnis · ESC: Schließen',
  },

  // Home Page
  'Trendyol Süper Lig · 2026/27 Sezonu': { en: 'Trendyol Süper Lig · 2026/27 Season', de: 'Trendyol Süper Lig · Saison 2026/27' },
  'Lig, Kadro Değerleri & Taktik Analiz Vitrini': {
    en: 'League, Squad Value & Tactical Analytics Hub',
    de: 'Liga-, Kaderwert- & Taktikanalyse-Portal',
  },
  'Toplam Lig Değeri': { en: 'Total League Value', de: 'Gesamtwert der Liga' },
  'İzlenen Oyuncu': { en: 'Tracked Players', de: 'Erfasste Spieler' },
  'Süper Lig Puan Durumu Özeti': { en: 'Süper Lig Standings Summary', de: 'Süper Lig Tabellen-Kurzübersicht' },
  'Tam Tablo & Trendler': { en: 'Full Table & Trends', de: 'Vollständige Tabelle & Trends' },
  'Takım': { en: 'Team', de: 'Verein' },
  'Form': { en: 'Form', de: 'Form' },
  'Puan': { en: 'Pts', de: 'Pkt' },
  'Haftanın Altın 11\'i (4-3-3)': { en: 'Team of the Week (4-3-3)', de: 'Elf der Woche (4-3-3)' },
  'Gol Krallığı': { en: 'Top Scorers', de: 'Torjägerliste' },
  'Asist Liderleri': { en: 'Assist Leaders', de: 'Vorlagengeber' },
  'Kaleci PSxG +/- Liderleri': { en: 'Goalkeeper PSxG +/- Leaders', de: 'Torhüter PSxG +/- Spitzenreiter' },
  'Gol': { en: 'Goals', de: 'Tore' },
  'Asist': { en: 'Assists', de: 'Vorlagen' },
  'Asist:': { en: 'Assist:', de: 'Vorlage:' },
  'Giren:': { en: 'Sub in:', de: 'Einwechslung:' },
  'Süper Lig\'in En Değerli 10 Futbolcusu (Transfermarkt Radarı)': {
    en: 'Top 10 Most Valuable Süper Lig Players (Transfermarkt Radar)',
    de: 'Die 10 wertvollsten Spieler der Süper Lig (Transfermarkt-Radar)',
  },
  'Sözleşme & Transfer Radarı': { en: 'Contract & Transfer Radar', de: 'Vertrags- & Transferradar' },
  'Oyuncu': { en: 'Player', de: 'Spieler' },
  'Kulüp': { en: 'Club', de: 'Verein' },
  'Pozisyon': { en: 'Position', de: 'Position' },
  'Yaş': { en: 'Age', de: 'Alter' },
  'Sakatlık Riski': { en: 'Injury Risk', de: 'Verletzungsrisiko' },
  'Reyting': { en: 'Rating', de: 'Bewertung' },
  'Zirve Değer': { en: 'Peak Value', de: 'Höchstwert' },
  'Güncel Değer': { en: 'Current Value', de: 'Aktueller Wert' },
  'Kulüp Taktik DNA & Kadro Değerleri': {
    en: 'Club Tactical DNA & Squad Valuations',
    de: 'Vereins-Taktik-DNA & Kaderwerte',
  },

  // Positions, Feet, Risk, Styles, Transfers
  'Kaleci': { en: 'Goalkeeper', de: 'Torwart' },
  'Defans': { en: 'Defender', de: 'Abwehr' },
  'Orta Saha': { en: 'Midfielder', de: 'Mittelfeld' },
  'Forvet': { en: 'Forward', de: 'Sturm' },
  'Mevki': { en: 'Pos', de: 'Pos' },
  'Uyruk': { en: 'Nationality', de: 'Nationalität' },
  'Ayak': { en: 'Foot', de: 'Fuß' },
  'Sağ': { en: 'Right', de: 'Rechts' },
  'Sol': { en: 'Left', de: 'Links' },
  'Çift': { en: 'Both', de: 'Beidfüßig' },
  'Sağ Ayak': { en: 'Right Foot', de: 'Rechtsfuß' },
  'Sol Ayak': { en: 'Left Foot', de: 'Linksfuß' },
  'Düşük': { en: 'Low', de: 'Gering' },
  'Orta': { en: 'Medium', de: 'Mittel' },
  'Yüksek': { en: 'High', de: 'Hoch' },
  'Kritik': { en: 'Critical', de: 'Kritisch' },
  'Dikine Baskı': { en: 'Vertical Press', de: 'Vertikales Pressing' },
  'Uzun Top / Geçiş': { en: 'Direct / Transition', de: 'Langball / Umschaltspiel' },
  'Kısır Pas': { en: 'Compact Possession', de: 'Kompaktes Passspiel' },
  'Bonservis': { en: 'Transfer Fee', de: 'Ablöse' },
  'Kiralık': { en: 'Loan', de: 'Leihe' },
  'Bedelsiz': { en: 'Free Transfer', de: 'Ablösefrei' },
  'Altyapı': { en: 'Youth Academy', de: 'Jugend' },

  // Standings & Club Detail
  'Süper Lig Puan Durumu & Kulüp Metrikleri': {
    en: 'Süper Lig Standings & Club Metrics',
    de: 'Süper Lig Tabelle & Vereinsmetriken',
  },
  'Genel': { en: 'Overall', de: 'Gesamt' },
  'İç Saha': { en: 'Home', de: 'Heim' },
  'Dış Saha': { en: 'Away', de: 'Auswärts' },
  'Son 5 Maç': { en: 'Last 5 Matches', de: 'Letzte 5 Spiele' },
  'Oyun Stili': { en: 'Play Style', de: 'Spielstil' },
  'Gol - xG': { en: 'Goals - xG', de: 'Tore - xG' },
  'Kadro Değeri': { en: 'Squad Value', de: 'Kaderwert' },
  '2023–2026 Çok Sezonlu Gelişim Trendleri': {
    en: '2023–2026 Multi-Season Progression Trends',
    de: '2023–2026 Mehrjahres-Entwicklungstrends',
  },
  'Maç Başı Puan (PPG) & Sıralama Karşılaştırması': {
    en: 'Points Per Game (PPG) & Rank Comparison',
    de: 'Punkte pro Spiel (PPG) & Tabellenvergleich',
  },
  'Sezonlara Göre Maç Başı Puan (PPG) Eğrisi': {
    en: 'Points Per Game (PPG) Trend by Season',
    de: 'PPG-Verlauf nach Saison',
  },
  'En fazla 5 kulüp seçebilirsiniz': { en: 'You can select up to 5 clubs', de: 'Maximal 5 Vereine auswählbar' },
  '2026 PPG': { en: '2026 PPG', de: '2026 PPG' },
  'Yaş Ortalaması': { en: 'Average Age', de: 'Durchschnittsalter' },
  'Gol - xG Sapması': { en: 'Goals - xG Delta', de: 'Tore - xG Differenz' },
  '3. Bölge Pas Yoğ.': { en: 'Final 3rd Pass Int.', de: 'Letztes-Drittel-Passint.' },
  'Hücum xG': { en: 'Attack xG', de: 'Offensiv-xG' },
  'Savunma xGA': { en: 'Defense xGA', de: 'Defensiv-xGA' },
  'Ort. Topla Oynama': { en: 'Avg Possession', de: 'Ø Ballbesitz' },
  'Baskı (PPDA)': { en: 'Pressing (PPDA)', de: 'Pressing (PPDA)' },
  'Teknik Direktör:': { en: 'Head Coach:', de: 'Cheftrainer:' },
  'Güncel Kadro & Sözleşme / Sakatlık Matrisi': {
    en: 'Current Squad & Contract / Injury Matrix',
    de: 'Aktueller Kader & Vertrags- / Verletzungsmatrix',
  },
  'Oyuncu künyesi için isme tıklayın': {
    en: 'Click player name for full profile',
    de: 'Für Spielerprofil auf Namen klicken',
  },
  'Kulüp Fikstürü & Analiz Edilen Maçlar': {
    en: 'Club Fixtures & Analyzed Matches',
    de: 'Vereins-Spielplan & Analysierte Spiele',
  },
  'Tüm Maç Merkezi': { en: 'Full Match Center', de: 'Zum Spielzentrum' },
  'Sözleşme Bitiş': { en: 'Contract Expiry', de: 'Vertragsende' },
  'Sözleşme Bitişi': { en: 'Contract Expiry', de: 'Vertragsende' },
  'Sözleşmesi <1 Yıl': { en: 'Contract <1 Yr', de: 'Vertrag <1 J.' },
  '<1 Yıl': { en: '<1 Yr', de: '<1 J.' },
  'Sırala:': { en: 'Sort:', de: 'Sortieren:' },
  'Değer': { en: 'Value', de: 'Wert' },
  'G / A': { en: 'G / A', de: 'T / V' },
  'Tümü': { en: 'All', de: 'Alle' },

  // Player Profile & Skeleton Map
  '2026 Süper Lig': { en: '2026 Süper Lig', de: '2026 Süper Lig' },
  '2026 Süper Lig Per-90 Performans Halkaları': {
    en: '2026 Süper Lig Per-90 Performance Rings',
    de: '2026 Süper Lig Per-90-Leistungsringe',
  },
  'Kaleci Performans Halkaları & PSxG +/- Analizi': {
    en: 'Goalkeeper Performance Rings & PSxG +/- Analysis',
    de: 'Torhüter-Leistungsringe & PSxG +/- Analyse',
  },
  '90 Dk Başına Gol': { en: 'Goals per 90', de: 'Tore pro 90 Min.' },
  '90 Dk Başına Asist': { en: 'Assists per 90', de: 'Vorlagen pro 90 Min.' },
  'Pas İsabeti': { en: 'Pass Accuracy', de: 'Passquote' },
  'Şans Yaratma': { en: 'Chance Creation', de: 'Chancenkreierung' },
  'Kurtarış Yüzdesi': { en: 'Save Percentage', de: 'Fangquote' },
  'Gol Yemeden Maç': { en: 'Clean Sheets', de: 'Zu-Null-Spiele' },
  'Önlenen Gol': { en: 'Goals Prevented', de: 'Verhinderte Tore' },
  '10 üzerinden': { en: 'out of 10', de: 'von 10' },
  'Etkileşimli İskelet Sakatlık Haritası': {
    en: 'Interactive Anatomical Injury Map',
    de: 'Interaktive Verletzungskarte',
  },
  'Anatomik Bölgeler (Dokunarak Eşleştirin)': {
    en: 'Anatomical Zones (Tap to Inspect)',
    de: 'Körperregionen (Zum Prüfen antippen)',
  },
  'Döndür': { en: 'Rotate', de: 'Drehen' },
  'Ön Görünüm': { en: 'Front View', de: 'Vorderansicht' },
  'Arka Görünüm': { en: 'Back View', de: 'Rückansicht' },
  'Toplam Kayıt:': { en: 'Total Records:', de: 'Einträge gesamt:' },
  'Uzak Kalınan:': { en: 'Days Missed:', de: 'Ausfalltage:' },
  'Kaçırılan Maç:': { en: 'Games Missed:', de: 'Verpasste Spiele:' },
  '0 Sakatlık': { en: '0 Injuries', de: '0 Verletzungen' },
  '1 Sakatlık': { en: '1 Injury', de: '1 Verletzung' },
  '2 Sakatlık': { en: '2 Injuries', de: '2 Verletzungen' },
  '3+ (Kronik)': { en: '3+ (Chronic)', de: '3+ (Chronisch)' },
  'Tarih Aralığı': { en: 'Date Range', de: 'Zeitraum' },
  'Sakatlık Nedeni': { en: 'Injury Reason', de: 'Verletzungsgrund' },
  'Gün': { en: 'Days', de: 'Tage' },
  'Bu anatomik bölgede kaydedilmiş resmi bir sakatlık bulunmamaktadır.': {
    en: 'No official injuries recorded in this anatomical region.',
    de: 'Für diese Körperregion sind keine Verletzungen erfasst.',
  },
  'Hastalık & Kondisyon Geçmişi (Sistemik Kayıtlar)': {
    en: 'Illness & Fitness History (Systemic Records)',
    de: 'Krankheits- & Fitnesshistorie (Systemisch)',
  },
  'İskelet haritasından bağımsızdır': {
    en: 'Independent from anatomical map',
    de: 'Unabhängig von der Anatomiekarte',
  },
  'Kayıtlı hastalık, ateş veya kondisyon/dinlenme eksikliği bulunmamaktadır.': {
    en: 'No recorded illness, fever, or fitness absences.',
    de: 'Keine Krankheits-, Fieber- oder Fitnessausfälle verzeichnet.',
  },
  'Baş / Yüz': { en: 'Head / Face', de: 'Kopf / Gesicht' },
  'Omuz': { en: 'Shoulder', de: 'Schulter' },
  'Göğüs / Kaburga': { en: 'Chest / Ribs', de: 'Brust / Rippen' },
  'Sırt / Bel': { en: 'Back / Spine', de: 'Rücken / Lenden' },
  'Kol / El Bileği': { en: 'Arm / Wrist', de: 'Arm / Handgelenk' },
  'Kasık': { en: 'Groin', de: 'Leiste' },
  'Ön Üst Adale': { en: 'Quadriceps', de: 'Oberschenkel vorn' },
  'Arka Adale (Hamstring)': { en: 'Hamstring', de: 'Hinterer Oberschenkel' },
  'Diz': { en: 'Knee', de: 'Knie' },
  'Baldır': { en: 'Calf', de: 'Wade' },
  'Ayak Bileği / Ayak': { en: 'Ankle / Foot', de: 'Knöchel / Fuß' },
  'Diğer / Genel Kas': { en: 'Other / General Muscle', de: 'Sonstige / Muskel' },
  'Transfermarkt Piyasa Değeri Eğrisi': {
    en: 'Transfermarkt Market Value Curve',
    de: 'Transfermarkt-Marktwertkurve',
  },
  'Seçili Tarih Değeri': { en: 'Value at Selected Date', de: 'Wert zum gewählten Datum' },
  'Bonservis & Transfer Geçmişi': { en: 'Transfer History', de: 'Transferhistorie' },
  'Sezon': { en: 'Season', de: 'Saison' },
  'Tarih': { en: 'Date', de: 'Datum' },
  'Ayrıldığı': { en: 'Left', de: 'Abgebend' },
  'Katıldığı': { en: 'Joined', de: 'Aufnehmend' },
  'Piyasa Değeri': { en: 'Market Value', de: 'Marktwert' },
  'Bedel': { en: 'Fee', de: 'Ablöse' },
  'Kulüp & Turnuva Kariyer Özeti': { en: 'Club & Competition Career Summary', de: 'Vereins- & Wettbewerbsbilanz' },
  'Turnuva': { en: 'Competition', de: 'Wettbewerb' },
  'Dönem': { en: 'Period', de: 'Zeitraum' },
  'Dakika': { en: 'Minutes', de: 'Minuten' },
  'Ort. Reyting': { en: 'Avg Rating', de: 'Ø Bewertung' },
  'Aktif Transfer Söylentileri': { en: 'Active Transfer Rumours', de: 'Aktive Transfergerüchte' },
  'Kulüp altyapısı / istikrarlı kadro oyuncusu; yakın dönem bonservis hareketi yok.': {
    en: 'Academy graduate / established squad player; no recent transfer fee movement.',
    de: 'Vereinseigenes Talent / Stammspieler; keine aktuellen Ablösebewegungen.',
  },
  'Şu anda aktif transfer söylentisi bulunmamaktadır.': {
    en: 'No active transfer rumours at the moment.',
    de: 'Derzeit keine aktiven Transfergerüchte.',
  },
  'Bu Avrupa / partner kulübü için Süper Lig transfer ve söylenti veritabanında bağlantılı kayıtlar mevcuttur.': {
    en: 'Linked records exist in the Süper Lig transfer and rumour database for this partner club.',
    de: 'Für diesen Partnerverein liegen verknüpfte Transfer- und Gerüchtedaten in der Süper-Lig-Datenbank vor.',
  },

  // Match Center & Match Detail
  'Trendyol Süper Lig Maç Merkezi': { en: 'Trendyol Süper Lig Match Center', de: 'Trendyol Süper Lig Spielzentrum' },
  'Analiz Edilen Maçlar, xG & Poisson Doğrulamaları': {
    en: 'Analyzed Matches, xG & Poisson Validations',
    de: 'Analysierte Spiele, xG & Poisson-Validierung',
  },
  'İlk Yarı:': { en: 'Half-Time:', de: 'Halbzeit:' },
  'Poisson vs. API Maç Önü Tahmini': { en: 'Poisson vs. API Prematch Forecast', de: 'Poisson vs. API Spielprognose' },
  'SiperLig Poisson Modeli': { en: 'SiperLig Poisson Model', de: 'SiperLig Poisson-Modell' },
  'X (Beraberlik)': { en: 'X (Draw)', de: 'X (Unentschieden)' },
  'Beraberlik': { en: 'Draw', de: 'Unentschieden' },
  'Beklenen xG': { en: 'Expected xG', de: 'Erwartete xG' },
  'En Olası Skor': { en: 'Most Likely Score', de: 'Wahrscheinlichstes Ergebnis' },
  'Doğru': { en: 'Correct', de: 'Treffer' },
  'Sürpriz': { en: 'Upset', de: 'Überraschung' },
  'YouTube Özeti Mevcut': { en: 'YouTube Highlights Available', de: 'YouTube-Highlights verfügbar' },
  '2D Gerçek Diziliş Sahası & Maç Reytingleri': {
    en: '2D Real Formations Pitch & Match Ratings',
    de: '2D-Aufstellung & Spielerbewertungen',
  },
  'Sarı Kart': { en: 'Yellow Card', de: 'Gelbe Karte' },
  'Kırmızı Kart': { en: 'Red Card', de: 'Rote Karte' },
  '2. Sarıdan Kırmızı Kart': { en: 'Second Yellow → Red Card', de: 'Gelb-Rote Karte' },
  '40 Takım İstatistiği Kıyaslaması': { en: 'Team Statistics Comparison', de: 'Teamstatistik-Vergleich' },
  'Genel & Topla Oynama': { en: 'Overview & Possession', de: 'Allgemein & Ballbesitz' },
  'Hücum & xG': { en: 'Attacking & xG', de: 'Angriff & xG' },
  'Pas & Kurulum': { en: 'Passing & Build-up', de: 'Passspiel & Aufbau' },
  'Savunma & İkili Mücadele': { en: 'Defense & Duels', de: 'Abwehr & Zweikämpfe' },
  'Disiplin & Duran Top': { en: 'Discipline & Set Pieces', de: 'Disziplin & Standards' },
  'Topla Oynama (%)': { en: 'Possession (%)', de: 'Ballbesitz (%)' },
  'Gol Beklentisi (xG)': { en: 'Expected Goals (xG)', de: 'Expected Goals (xG)' },
  'Asist Beklentisi (xA)': { en: 'Expected Assists (xA)', de: 'Expected Assists (xA)' },
  'Net Gol Pozisyonu': { en: 'Big Chances Created', de: 'Großchancen' },
  'Toplam Hücum': { en: 'Total Attacks', de: 'Angriffe gesamt' },
  'İsabetli Şut': { en: 'Shots on Target', de: 'Schüsse aufs Tor' },
  'İsabetsiz Şut': { en: 'Shots off Target', de: 'Schüsse neben das Tor' },
  'Engellenen Şut': { en: 'Blocked Shots', de: 'Geblockte Schüsse' },
  'Ceza Sahası İçi Şut': { en: 'Shots Inside Box', de: 'Schüsse im Strafraum' },
  'Ceza Sahası Dışı Şut': { en: 'Shots Outside Box', de: 'Schüsse außerhalb Strafraum' },
  'Şut İsabet Oranı (%)': { en: 'Shot Accuracy (%)', de: 'Schussgenauigkeit (%)' },
  'Toplam Pas': { en: 'Total Passes', de: 'Pässe gesamt' },
  'İsabetli Pas': { en: 'Accurate Passes', de: 'Genaue Pässe' },
  'Hatalı Pas': { en: 'Failed Passes', de: 'Fehlpässe' },
  '3. Bölgeye Pas': { en: 'Passes into Final Third', de: 'Pässe ins letzte Drittel' },
  'Kilit Pas': { en: 'Key Passes', de: 'Schlüsselpässe' },
  'Kendi Yarı Sahasında Pas': { en: 'Passes in Own Half', de: 'Pässe in eigener Hälfte' },
  'Rakip Yarı Sahada Pas': { en: 'Passes in Opp. Half', de: 'Pässe in gegn. Hälfte' },
  'Geri Pas': { en: 'Backward Passes', de: 'Rückpässe' },
  'Uzun Pas': { en: 'Long Passes', de: 'Lange Pässe' },
  'İsabetli Uzun Pas': { en: 'Accurate Long Balls', de: 'Genaue lange Bälle' },
  'Orta Denemesi': { en: 'Crosses', de: 'Flanken' },
  'İsabetli Orta': { en: 'Accurate Crosses', de: 'Genaue Flanken' },
  'Çalım Denemesi': { en: 'Dribbles Attempted', de: 'Dribblings gesamt' },
  'Başarılı Çalım': { en: 'Successful Dribbles', de: 'Erfolgreiche Dribblings' },
  'Hava Topu Mücadelesi': { en: 'Aerial Duels', de: 'Kopfballduelle' },
  'Kazanılan Hava Topu': { en: 'Aerial Duels Won', de: 'Gewonnene Kopfballduelle' },
  'Top Çalma (Tackle)': { en: 'Tackles', de: 'Tacklings' },
  'Başarılı Top Çalma': { en: 'Tackles Won', de: 'Erfolgreiche Tacklings' },
  'Pas Arası (Interception)': { en: 'Interceptions', de: 'Abgefangene Pässe' },
  'Uzaklaştırma': { en: 'Clearances', de: 'Befreiungsschläge' },
  'Kaleci Kurtarışı': { en: 'Goalkeeper Saves', de: 'Torwartparaden' },
  'Köşe Vuruşu': { en: 'Corners', de: 'Ecken' },
  'Serbest Vuruş': { en: 'Free Kicks', de: 'Freistöße' },
  'Taç Atışı': { en: 'Throw-Ins', de: 'Einwürfe' },
  'Kale Vuruşu': { en: 'Goal Kicks', de: 'Abstöße' },
  'Ofsayt': { en: 'Offsides', de: 'Abseits' },
  'Yapılan Faul': { en: 'Fouls Committed', de: 'Begangene Fouls' },
  'Sarı Kart Sayısı': { en: 'Yellow Cards', de: 'Gelbe Karten' },
  'Kırmızı Kart Sayısı': { en: 'Red Cards', de: 'Rote Karten' },

  // Match Events & Highlight Player
  'Dakika Bazlı Maç Olayları': { en: 'Match Timeline Events', de: 'Spielereignisse nach Minute' },
  'GOL': { en: 'GOAL', de: 'TOR' },
  'SARI KART': { en: 'YELLOW CARD', de: 'GELBE KARTE' },
  'KIRMIZI KART': { en: 'RED CARD', de: 'ROTE KARTE' },
  '2. SARI → KIRMIZI': { en: '2ND YELLOW → RED', de: 'GELB-ROT' },
  'DEĞİŞİKLİK': { en: 'SUB', de: 'WECHSEL' },
  'Akan Oyun Golü': { en: 'Open Play Goal', de: 'Tor aus dem Spiel' },
  'Penaltı Golü': { en: 'Penalty Goal', de: 'Elfmetertor' },
  'Kendi Kalesine Gol': { en: 'Own Goal', de: 'Eigentor' },
  'Maçın Golleri & Video Özeti': { en: 'Match Goals & Video Highlights', de: 'Tore & Video-Highlights' },
  'YouTube\'da İzle': { en: 'Watch on YouTube', de: 'Auf YouTube ansehen' },
  'TR Erişim Doğrulaması': { en: 'TR Access Check', de: 'TR-Zugriffsprüfung' },
  'Ana Maç Özeti': { en: 'Full Match Highlights', de: 'Spiel-Highlights' },
  'Maç Özeti': { en: 'Match Highlights', de: 'Spiel-Highlights' },
  'Gol Klibi': { en: 'Goal Clip', de: 'Tor-Clip' },
  'Türkiye\'de açık gömülü özet klibi bulunamadı': {
    en: 'No region-unblocked embedded highlight clip found',
    de: 'Kein frei zugänglicher eingebetteter Highlight-Clip gefunden',
  },
  'Yayıncı kuruluş coğrafi kısıtı veya arşiv gecikmesi nedeniyle YouTube üzerinden resmi özeti doğrudan arayabilirsiniz.': {
    en: 'Due to broadcaster geo-restrictions or archive delay, you can search for the official highlights directly on YouTube.',
    de: 'Aufgrund regionaler Sende-Beschränkungen können Sie die offiziellen Highlights direkt auf YouTube suchen.',
  },
  'YouTube\'da Resmi Özeti Ara': { en: 'Search Official Highlights on YouTube', de: 'Offizielle Highlights auf YouTube suchen' },

  // Shot Target Matrix & BoxScore & Live Probabilities
  'Kale Şut Köşe Haritası (6 Kale Bölgesi + Direk Dışı)': {
    en: 'Goal Target Shot Map (6 Goal Zones + Off Target)',
    de: 'Tor-Schusszonen-Karte (6 Zielzonen + Daneben)',
  },
  'Üst Direk Üstü (Close High)': { en: 'Over Crossbar (High)', de: 'Über die Latte' },
  'Üst Direk Üstü': { en: 'Over Crossbar', de: 'Über die Latte' },
  'Sol Dış': { en: 'Wide Left', de: 'Links vorbei' },
  'Sağ Dış': { en: 'Wide Right', de: 'Rechts vorbei' },
  'Üst Sol': { en: 'Top Left', de: 'Oben Links' },
  'Üst Orta': { en: 'Top Center', de: 'Oben Mitte' },
  'Üst Sağ': { en: 'Top Right', de: 'Oben Rechts' },
  'Alt Sol': { en: 'Bottom Left', de: 'Unten Links' },
  'Alt Orta': { en: 'Bottom Center', de: 'Unten Mitte' },
  'Alt Sağ': { en: 'Bottom Right', de: 'Unten Rechts' },
  'Tüm Şut Olayları': { en: 'All Shot Events', de: 'Alle Schüsse' },
  'Her İki Takım': { en: 'Both Teams', de: 'Beide Teams' },
  'İsabetli': { en: 'On Target', de: 'Aufs Tor' },
  'KURTARIŞ': { en: 'SAVED', de: 'GEHALTEN' },
  'Oyuncu Maç Reytingleri & BoxScore': { en: 'Player Match Ratings & BoxScore', de: 'Spielerbewertungen & BoxScore' },
  'Dakika Bazlı Canlı Kazanma Olasılığı Eğrisi': {
    en: 'Live Win Probability Timeline Curve',
    de: 'Live-Siegwahrscheinlichkeitskurve',
  },
  'Şut': { en: 'Shots', de: 'Schüsse' },
  'K.Pas': { en: 'Key P.', de: 'Schl.P.' },
  'Pas %': { en: 'Pass %', de: 'Pass %' },
  'Hafta': { en: 'Round', de: 'Spieltag' },
  'Skor': { en: 'Score', de: 'Ergebnis' },
  'Maç': { en: 'Match', de: 'Spiel' },

  // Market & Predictions Page
  'Transfer İstihbaratı & Poisson Tahmin Karnesi': {
    en: 'Transfer Intelligence & Poisson Forecast Scorecard',
    de: 'Transfer-Analyse & Poisson-Prognosebilanz',
  },
  'Sözleşmesi Biten Yıldızlar, Söylenti Radarı & Model Doğruluğu': {
    en: 'Expiring Contracts, Rumour Radar & Model Accuracy',
    de: 'Auslaufende Verträge, Gerüchte-Radar & Modellgenauigkeit',
  },
  'Sözleşmesi 1 Yıldan Az Kalan Oyuncular': {
    en: 'Players With Less Than 1 Year Remaining',
    de: 'Spieler mit weniger als 1 Jahr Restvertrag',
  },
  'Bosman / Serbest Kalma Radarı': { en: 'Bosman / Free Agent Radar', de: 'Bosman- / Ablösefrei-Radar' },
  'Transfer İhtimali Yüksek Yıldızlar': { en: 'High-Probability Transfer Targets', de: 'Wahrscheinliche Transferziele' },
  'Radara Git →': { en: 'Go to Radar →', de: 'Zum Radar →' },
  'Poisson Modeli Süper Lig Doğruluk Karnesi': {
    en: 'Poisson Model Süper Lig Accuracy Scorecard',
    de: 'Poisson-Modell Süper-Lig-Trefferbilanz',
  },
  'Model Performans Denetimi': { en: 'Model Performance Audit', de: 'Modell-Leistungsprüfung' },
  'Poisson İsabeti': { en: 'Poisson Accuracy', de: 'Poisson-Genauigkeit' },
  'Poisson Doğruluk': { en: 'Poisson Hit Rate', de: 'Poisson-Trefferquote' },
  'API Konsensüs': { en: 'API Consensus', de: 'API-Konsens' },
  'Poisson Brier Skoru': { en: 'Poisson Brier Score', de: 'Poisson Brier-Score' },
  'API Brier Skoru': { en: 'API Brier Score', de: 'API Brier-Score' },
  'Poisson (1 / X / 2)': { en: 'Poisson (1 / X / 2)', de: 'Poisson (1 / X / 2)' },
  'API (1 / X / 2)': { en: 'API (1 / X / 2)', de: 'API (1 / X / 2)' },
  'Poisson Durumu': { en: 'Poisson Status', de: 'Poisson-Status' },
  'Tümünü İncele →': { en: 'Inspect All →', de: 'Alle ansehen →' },

  // Split JSX TextNode fragments
  'Lig #': { en: 'League #', de: 'Liga #' },
  'Söylenti': { en: 'Rumours', de: 'Gerüchte' },
  'Sonuç:': { en: 'Outcome:', de: 'Ergebnis:' },
  'Beklenen Gol:': { en: 'Expected Goals:', de: 'Erwartete Tore:' },
  'En Olası Skor:': { en: 'Most Likely Score:', de: 'Wahrscheinlichstes Ergebnis:' },
  '2.5 Üst: %': { en: 'Over 2.5: %', de: 'Über 2,5: %' },
  'Sapma': { en: 'Missed', de: 'Abweichung' },
  '. Hafta İstihbaratı': { en: ' · Round Intelligence', de: '. Spieltag Analyse' },
  '. Hafta Maç Skorları (Detay için skora tıklayın)': {
    en: ' · Match Scores (Click score for analytics)',
    de: '. Spieltag Ergebnisse (Für Details Ergebnis anklicken)',
  },
  'Sakatlık Riski:': { en: 'Injury Risk:', de: 'Verletzungsrisiko:' },
  'ay kaldı': { en: 'months left', de: 'Monate übrig' },
  'ay kaldı · Kritik': { en: 'months left · Critical', de: 'Monate übrig · Kritisch' },
  'Kadrosuna Dön →': { en: 'Squad →', de: 'Kader →' },
  'Trendyol Süper Lig (': { en: 'Trendyol Süper Lig (Round ', de: 'Trendyol Süper Lig (Stand ' },
  '. Hafta itibarıyla) verilerinin son güncellenme zamanı ve hafta bazlı tamamlanma durumu.': {
    en: ') latest data sync timestamp and round-by-round completion status.',
    de: '. Spieltag) letzte Datenaktualisierung und Spieltags-Status.',
  },
  'Bölge filtresini temizle (': { en: 'Clear zone filter (', de: 'Zonenfilter zurücksetzen (' },
  'Anatomik Sakatlık Yoğunluğu': { en: 'Anatomical Injury Density', de: 'Anatomische Verletzungsdichte' },
  'Bölgesi Kayıtları': { en: 'Zone Records', de: 'Zonen-Einträge' },
  'için eşleşen oyuncu, kulüp veya maç bulunamadı.': {
    en: 'matched no players, clubs, or matches.',
    de: 'lieferte keine passenden Spieler, Vereine oder Spiele.',
  },
  '3. Bölge: %': { en: 'Final 3rd: %', de: 'Letztes Drittel: %' },
};

const TR_MONTHS: Record<string, { en: string; de: string }> = {
  Oca: { en: 'Jan', de: 'Jan' },
  'Şub': { en: 'Feb', de: 'Feb' },
  Mar: { en: 'Mar', de: 'Mär' },
  Nis: { en: 'Apr', de: 'Apr' },
  May: { en: 'May', de: 'Mai' },
  Haz: { en: 'Jun', de: 'Jun' },
  Tem: { en: 'Jul', de: 'Jul' },
  'Ağu': { en: 'Aug', de: 'Aug' },
  Eyl: { en: 'Sep', de: 'Sep' },
  Eki: { en: 'Oct', de: 'Okt' },
  Kas: { en: 'Nov', de: 'Nov' },
  Ara: { en: 'Dec', de: 'Dez' },
};

function translateSegment(seg: string, lang: Exclude<Locale, 'tr'>): string {
  const exact = EXACT_TRANSLATIONS[seg];
  if (exact) return exact[lang];

  // Dynamic round / age / count / date patterns
  let m: RegExpMatchArray | null;

  if ((m = seg.match(/^(\d+)\.\s*Hafta$/))) {
    return lang === 'en' ? `Round ${m[1]}` : `${m[1]}. Spieltag`;
  }
  if ((m = seg.match(/^(\d+)\.\s*Hafta Özeti$/))) {
    return lang === 'en' ? `Round ${m[1]} Highlights` : `Highlights ${m[1]}. Spieltag`;
  }
  if ((m = seg.match(/^([0-9]{4}\/[0-9]{2}) Sezonu$/))) {
    return lang === 'en' ? `${m[1]} Season` : `Saison ${m[1]}`;
  }
  if ((m = seg.match(/^2026 \((\d+)H\)$/))) {
    return lang === 'en' ? `2026 (R${m[1]})` : `2026 (${m[1]}. Sp.)`;
  }
  if ((m = seg.match(/^Tümü \((\d+)\)$/))) {
    return lang === 'en' ? `All (${m[1]})` : `Alle (${m[1]})`;
  }
  if ((m = seg.match(/^(\d+) yaş$/))) {
    return lang === 'en' ? `${m[1]} yrs` : `${m[1]} J.`;
  }
  if ((m = seg.match(/^(\d+) Gol$/))) {
    return lang === 'en' ? `${m[1]} Goals` : `${m[1]} Tore`;
  }
  if ((m = seg.match(/^(\d+) Asist$/))) {
    return lang === 'en' ? `${m[1]} Assists` : `${m[1]} Vorlagen`;
  }
  if ((m = seg.match(/^(\d+) Maç$/))) {
    return lang === 'en' ? `${m[1]} Matches` : `${m[1]} Spiele`;
  }
  if ((m = seg.match(/^(\d+) Futbolcu$/))) {
    return lang === 'en' ? `${m[1]} Players` : `${m[1]} Spieler`;
  }
  if ((m = seg.match(/^(\d+) İstatistik$/))) {
    return lang === 'en' ? `${m[1]} Stats` : `${m[1]} Statistiken`;
  }
  if ((m = seg.match(/^(\d+) Şut Bölgesi$/))) {
    return lang === 'en' ? `${m[1]} Shot Zones` : `${m[1]} Schusszonen`;
  }
  if ((m = seg.match(/^(\d+) Olay$/))) {
    return lang === 'en' ? `${m[1]} Events` : `${m[1]} Ereignisse`;
  }
  if ((m = seg.match(/^(\d+) Gün$/))) {
    return lang === 'en' ? `${m[1]} Days` : `${m[1]} Tage`;
  }
  if ((m = seg.match(/^(\d+)\s+G$/))) {
    return lang === 'en' ? `${m[1]} D` : `${m[1]} T`;
  }
  if ((m = seg.match(/^(\d+) maçta$/))) {
    return lang === 'en' ? `in ${m[1]} matches` : `in ${m[1]} Spielen`;
  }
  if ((m = seg.match(/^Kurtarış: %(.+)$/))) {
    return lang === 'en' ? `Saves: ${m[1]}%` : `Paraden: ${m[1]}%`;
  }
  if ((m = seg.match(/^Süre: (.+)$/))) {
    return lang === 'en' ? `Min: ${m[1]}` : `Min.: ${m[1]}`;
  }
  if ((m = seg.match(/^(.+?) Bölgesi Şutları$/))) {
    const zoneTr = m[1];
    const zoneTranslated = EXACT_TRANSLATIONS[zoneTr]?.[lang] ?? zoneTr;
    return lang === 'en' ? `${zoneTranslated} Zone Shots` : `Schüsse ${zoneTranslated}`;
  }
  if ((m = seg.match(/^Anatomik İskelet Haritası \((Ön|Arka) Görünüm\)$/))) {
    const face = m[1] === 'Ön' ? (lang === 'en' ? 'Front View' : 'Vorderansicht') : lang === 'en' ? 'Back View' : 'Rückansicht';
    return lang === 'en' ? `Anatomical Injury Map (${face})` : `Anatomische Verletzungskarte (${face})`;
  }
  if ((m = seg.match(/^(.+?) arması$/))) {
    return lang === 'en' ? `${m[1]} crest` : `${m[1]} Wappen`;
  }
  if ((m = seg.match(/^(.+?) Kadrosu & Taktik DNA$/))) {
    return lang === 'en' ? `${m[1]} Squad & Tactical DNA` : `${m[1]} Kader & Taktik-DNA`;
  }
  if ((m = seg.match(/^(\d{2}) (Oca|Şub|Mar|Nis|May|Haz|Tem|Ağu|Eyl|Eki|Kas|Ara) (\d{4})$/))) {
    const mon = TR_MONTHS[m[2]]?.[lang] ?? m[2];
    return `${m[1]} ${mon} ${m[3]}`;
  }
  if ((m = seg.match(/^(\d+) Gol \(xG: (.+)\)$/))) {
    return lang === 'en' ? `${m[1]} Goals (xG: ${m[2]})` : `${m[1]} Tore (xG: ${m[2]})`;
  }
  if ((m = seg.match(/^(\d+) Sarı$/))) {
    return lang === 'en' ? `${m[1]} Yellow` : `${m[1]} Gelb`;
  }
  if ((m = seg.match(/^(\d+) Kırmızı$/))) {
    return lang === 'en' ? `${m[1]} Red` : `${m[1]} Rot`;
  }
  if (seg.includes('Trendyol Süper Lig') && seg.includes('itibarıyla')) {
    const mm = seg.match(/^([^\s]+)\s+Trendyol Süper Lig\s+\((\d+)\.\s*Hafta itibarıyla\)/);
    if (mm) {
      return lang === 'en'
        ? `${mm[1]} Trendyol Süper Lig (as of Round ${mm[2]}) last updated timestamp and round completion status.`
        : `${mm[1]} Trendyol Süper Lig (Stand ${mm[2]}. Spieltag) Zeitstempel der letzten Aktualisierung und Spieltags-Fortschritt.`;
    }
  }
  if (seg.includes('seyirci)')) {
    return seg.replace('seyirci)', lang === 'en' ? 'capacity)' : 'Plätze)');
  }

  return seg;
}

export function translateText(raw: string, lang: Locale): string {
  if (lang === 'tr' || !raw) return raw;

  const edgeMatch = raw.match(/^(\s*)([\s\S]*?)(\s*)$/);
  if (!edgeMatch) return raw;
  const [, leading, trimmed, trailing] = edgeMatch;
  if (!trimmed) return raw;

  const direct = EXACT_TRANSLATIONS[trimmed];
  if (direct) {
    return `${leading}${direct[lang]}${trailing}`;
  }

  if (trimmed.includes(' · ')) {
    const parts = trimmed.split(' · ').map((part) => translateSegment(part.trim(), lang));
    return `${leading}${parts.join(' · ')}${trailing}`;
  }

  if (trimmed.startsWith('· ')) {
    const rest = trimmed.slice(2).trim();
    return `${leading}· ${translateSegment(rest, lang)}${trailing}`;
  }

  const single = translateSegment(trimmed, lang);
  return `${leading}${single}${trailing}`;
}
