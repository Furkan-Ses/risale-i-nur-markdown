# risale-i-nur-corpus

Bu repo, **Risale-i Nur Külliyatı'nın tamamını yüksek kaliteli `.md` korpusuna dönüştürme** çalışmasıdır. İlk aşama, kitapların güvenilir Markdown sürümlerini üretmek ve temizlemektir. Nihai hedef ise bu korpusu **AI için çok iyi indekslenmiş, hızlı taranabilir, semantik olarak güvenilir bir context havuzuna** dönüştürmektir.

Bu sistem kritik; çünkü hedef metin **dini metin**. Bu yüzden:

- OCR kalıntısı bırakılmamalı
- kelime veya cümle düzeyinde **anlam bozucu hata** bulunmamalı
- başlık kayması, noktalama ve editoryal farklar raporlanmalı
- AI'nin hızlı cevap verebilmesi için indeks yapısı açık, sade ve makinece okunabilir olmalı

Uzun vadeli amaç, insanların Risale'deki konu, başlık ve ilgilerine göre hızlı arama yapabildiği; daha sonra da bu veriyle güçlü bir **chat bot / rehber okuma sistemi** kurulabildiği bir altyapı inşa etmektir.

## Proje amacı

| Aşama | Amaç |
| --- | --- |
| 1 | Tüm Risale-i Nur kitaplarını güvenilir `.md` dosyalarına dönüştürmek |
| 2 | Bu metinleri başlık, bölüm, kitap ve konu düzeyinde indekslemek |
| 3 | AI için hızlı retrieval / context havuzu oluşturmak |
| 4 | İnsanların konuya göre okuma ve keşif yapabildiği bir sohbet / arama sistemi kurmak |

## Temel kalite ilkeleri

| İlke | Açıklama |
| --- | --- |
| Metin sadakati | Anlamı bozacak kelime, cümle, OCR veya kırık pasaj kabul edilmez |
| Editoryal şeffaflık | Noktalama, imla, başlık ve edisyon farkları saklanmaz; raporlanır |
| Provenans | Hangi metnin nereden geldiği açık tutulur |
| AI erişilebilirliği | İnsan ve makine için sade indeks, JSON katalog ve temiz bölümleme sağlanır |

## Ali Tekdemir indeks mantığı ve bu repodaki karşılığı

Ali Tekdemir reposunda temel akış şudur:

1. üst seviye içindekiler (`01 İçindekiler.md`)
2. her kitap için ayrı klasör
3. her kitapta bir `00` index dosyası
4. ardından bölüm `.md` dosyaları

Bu repo bunu daha AI-dostu hale getirir:

| Katman | Amaç | Yol |
| --- | --- | --- |
| Upstream | Kaynağı ve orijinal indeks mantığını korumak | `upstream/alitekdemir/obsidian-markdown/` |
| Canonical | Düzeltilmiş ve güvenilen yerel referansları saklamak | `canonical/furkan/` |
| AI layer | Retrieval ve citation-first kullanım için yapısal kopya üretmek | `ai/` |
| Human index | İnsan/LLM için sade Markdown indeksler | `indexes/` |
| Machine index | JSON katalog ve karşılaştırma verileri | `generated/json/` |
| Audit reports | İnsan tarafından okunacak kalite ve fark raporları | `reports/comparisons/` |

## Sözler için nasıl indeksleniyor?

`Sözler` için artık iki paralel görünüm var:

1. **Upstream görünüm** — Ali Tekdemir / Hizmet Vakfı zincirinden gelen bölüm dosyaları
2. **Canonical görünüm** — düzeltilmiş yerel `Sozler.md` ve `by_heading/` dosyaları

Bu ikisi birlikte `indexes/books/01-sozler.md` içinde gösterilir. Böylece:

- upstream bölüm nerede görülebilir,
- yerel kanonik bölüm nerede duruyor,
- AI hangi dosyaları önce okumalı,
- hangi referansın “doğru baz” olduğu

tek yerden izlenebilir.

## Markdown kirliliği nasıl yönetilir?

Repo içinde rastgele yerlere `.md` notları bırakılmamalıdır. Düzen şöyledir:

| Tür | Yer |
| --- | --- |
| Ana proje açıklaması | `README.md` |
| AI için hazırlanmış güvenli kopya | `ai/` |
| Kalıcı indeks belgeleri | `indexes/` |
| Karşılaştırma / kalite raporları | `reports/comparisons/` |
| Makine çıktıları | `generated/json/` |
| Birleşik metin çıktıları | `generated/text/` |
| Geçici çalışma notları | Repo dışı session/workspace alanı |

Bu sayede repo kökü temiz kalır ve `.md` dosyaları sadece anlamlı, kalıcı yerlerde tutulur.

## Provenans

- Upstream açıklaması ve lisans notu: `upstream/alitekdemir/README.upstream.md`
- Ali Tekdemir kaynağı README'sinde **CC BY-ND 4.0** lisansı belirtilir
- Metin kökeni: Hizmet Vakfı / DİB asıl nüsha zinciri

## AI kullanım katmanı

`ai/` klasörü, kanonik metinlerin yeniden yazılmadan AI retrieval için hazırlanmış ikinci katmanıdır. Burada:

- kitap ve bölüm kopyaları zengin frontmatter ile tutulur,
- chunk / pasaj dosyaları stabil kimliklerle üretilir,
- answer policy ile cite zorunluluğu açıkça tanımlanır,
- AI sistemleri metni doğrudan değil, izlenebilir ve atıflı bir katman üzerinden okur.

Bu katmanın amacı, özellikle dinî metinlerde yanlış yönlendirme riskini azaltmak ve her cevabı geri izlenebilir hale getirmektir.

## Şu anki durum

- `Sözler` için kanonik yerel metin temizlendi
- anlam bozucu OCR kalıntıları temizlendi
- official/public ve upstream kaynaklarla karşılaştırma yapıldı
- doğrulanmış kitaplar `canonical/furkan/` altında kitap ve bölüm düzeyinde tutuluyor
- AI retrieval için ayrı `ai/` katmanı üretilebiliyor
- indeks yapısı geniş Külliyat hedefi düşünülerek kurulmaya başlandı

## Yeniden üretim

```bash
python3 scripts/build_catalog.py
python3 scripts/compare_all_upstream_official.py
python3 scripts/import_verified_books.py
python3 scripts/build_ai_corpus.py
```
