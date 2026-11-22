# LigaMetric — Süper Lig İstatistik & Analiz Merkezi

**LigaMetric**, Türkiye Süper Lig maçları, puan durumu, detaylı maç olayları, taktiksel kadrolar, oyuncu profilleri (genel bakış, performans/kariyer, piyasa değeri/transferler, sakatlık geçmişi), medya özetleri ve çok dilli (**TR / EN / DE**) arayüz sunan statik Next.js (`output: 'export'`) futbol analiz platformudur.

## Mimari & Yasal Veri Güvenliği

- **Bronze Katmanı (Turso / libSQL):** Harici Highlightly API'sinden çekilen tüm ham yanıtlar (`backend/data/bronze/`) ve kota defteri (`backend/data/quota_state.json`) **kesinlikle GitHub'a yüklenmez** (`.gitignore` ile engellidir). Ham önbellek yalnızca özel **Turso (libSQL)** veritabanında saklanır.
- **Gold Katmanı (`web/src/data/*.json`):** Uygulama için işlenmiş, birleştirilmiş ve temizlenmiş özet veri dosyalarıdır. GitHub deposunda yalnızca bu kaynak kodlar ve Gold özet veriler yer alır.
- **Statik Dağıtım:** `web/` altında Next.js `output: 'export'` ile tamamen statik HTML/JS/CSS üretilir.

## Otomatik Günlük Veri Güncelleme (GitHub Actions)

[`.github/workflows/auto-harvest.yml`](.github/workflows/auto-harvest.yml) iş akışı her gün **04:00 UTC (07:00 TSİ)** saatinde (veya manuel `workflow_dispatch` tetiklemesiyle) otomatik olarak şu adımları çalıştırır:

1. `python backend/turso_client.py pull-bronze` — Turso'dan mevcut Bronze önbelleğini çeker.
2. `python backend/auto_harvester.py --batch-budget "$BUDGET" --refresh-feeds` — Günlük güvenli kota kapsamında yeni oynanan maçları ve fikstürü toplar, Turso'ya yazar.
3. `python backend/media_enrichment.py --max-matches 25 --max-players 50` — Türkiye'den erişilebilen maç özetlerini ve oyuncu portrelerini zenginleştirir.
4. `python backend/sync_highlightly.py merge` — Güncel Gold özet JSON dosyalarını üretir.
5. `cd web && npm ci && npm run build` — Statik siteyi derleyip doğrular.
6. Yalnızca `web/src/data/*.json` değişikliklerini depoya işler.

### Gerekli GitHub Actions Gizli Anahtarları (`Settings → Secrets and variables → Actions`)

Otomatik veri çekicinin çalışması için aşağıdaki 5 gizli anahtar tanımlanmalıdır:

| Secret Adı | Açıklama |
| --- | --- |
| `HIGHLIGHTLY_API_KEY_1` | 1. Highlightly API anahtarı |
| `HIGHLIGHTLY_API_KEY_2` | 2. Highlightly API anahtarı |
| `HIGHLIGHTLY_API_KEY_3` | 3. Highlightly API anahtarı |
| `TURSO_DATABASE_URL` | Turso libSQL veritabanı bağlantı URL'si (`libsql://...`) |
| `TURSO_AUTH_TOKEN` | Turso veritabanı erişim token'ı |

## Yerel Kurulum & Çalıştırma

```bash
# 1. Ortam değişkenlerini hazırlayın (backend/.env dosyasını Git'e eklemeyin)
cp backend/.env.example backend/.env

# 2. Verileri güncelleyin ve Gold JSON üretin
python backend/auto_harvester.py --batch-budget 240 --refresh-feeds
python backend/media_enrichment.py --max-matches 25 --max-players 50
python backend/sync_highlightly.py merge

# 3. Statik web uygulamasını geliştirin veya derleyin
cd web
npm ci
npm run build
```
