# risale-i-nur-markdown

Doğrulanmış **Risale-i Nur Markdown korpusu**. Bu repo iki ana kullanım senaryosuna göre düzenlenmiştir:

1. **İnsanlar için okuma katmanı** - kitapları doğrudan, temiz ve düzenli Markdown olarak okumak  
2. **AI sistemleri için veri katmanı** - pasaj, bölüm, manifest ve açık atıf yapısıyla retrieval / RAG / chatbot kullanımını kolaylaştırmak

## Bu repo ne sağlar?

- doğrulanmış kitaplar için temiz `books/` katmanı
- AI sistemleri için yapılandırılmış `ai/` katmanı
- kalite ve karşılaştırma raporları
- yeniden üretilebilir katalog ve build scriptleri
- kamuya açık, profesyonel ve gezinmesi kolay bir klasör yapısı

## Hızlı başlangıç

### Okumak için

- `books/` altındaki klasörler doğrudan okuma içindir
- her kitapta birleşik bir `.md` dosyası ve `by_heading/` bölüm klasörü bulunur
- kitaplar arası gezinme için `indexes/README.md` kullanılabilir
- bu klasör, **insan okuyucular için ana görünüm**dür

### AI / RAG / search için

- `ai/passages/all-passages.jsonl` - en uygun toplu ingestion girişi
- `ai/catalog.json` - AI katmanının üst seviye kataloğu
- `ai/ANSWERING_POLICY.md` - güvenli cevaplama ve atıf kuralları
- `ai/books/<slug>/sections/*.md` - section düzeyinde zenginleştirilmiş kaynaklar
- AI kullanımında esas alınacak kitap kopyaları **`ai/books/`** altındadır; üstteki `books/` klasörü insan okuması içindir

### Kalite kontrol için

- `reports/comparisons/all-upstream-public-summary.md`
- `reports/comparisons/books/*.md`
- `generated/json/all-upstream-public-summary.json`

## Repo yapısı

| Yol | Amaç |
| --- | --- |
| `books/` | İnsan okuyucular için doğrulanmış ana okuma katmanı |
| `ai/` | AI / retrieval / citation-first kullanım katmanı |
| `indexes/` | Gezinme ve katalog belgeleri |
| `reports/comparisons/` | İnsan tarafından okunacak kalite raporları |
| `generated/json/` | Makinece okunabilir katalog ve karşılaştırma çıktıları |
| `generated/text/` | Birleşik yardımcı metin çıktıları |
| `sources/official-markdown-mirror/` | Kaynak aynası ve yeniden üretim referansı |
| `scripts/` | Katalog, karşılaştırma ve AI build scriptleri |

## Editoryal ilke

- anlam bozucu OCR kalıntıları kabul edilmez
- kelime ve cümle sadakati önceliklidir
- noktalama, başlık veya edisyon farkları saklanmaz; raporlanır
- AI katmanı metni yeniden yazmaz; yalnızca daha güvenli erişim için yapılandırır

## Provenans

Bu repo içindeki kaynak aynası, başlangıçta **Ali Tekdemir** tarafından yayımlanan **Risale-i-Nur-Diyanet** deposundaki Markdown korpusundan içe aktarılmıştır. Bu atıf özellikle burada tutulur; repo içindeki diğer klasörlerde kişi/repo bazlı atıf tekrar edilmez.

Metin hattı daha sonra repo içinde resmi Hizmet Vakfı yayımlarıyla karşılaştırılmış ve doğrulama raporları üretilmiştir.

Kısaca:

- kişi ve repo atfı: **Ali Tekdemir / Risale-i-Nur-Diyanet**
- teknik kaynak aynası: `sources/official-markdown-mirror/`
- doğrulanmış insan okuma katmanı: `books/`
- AI için türetilmiş kullanım katmanı: `ai/`

## Obsidian ve graphify

Bu repo **Obsidian-ready** ve **Graphify-ready** olacak şekilde düzenlenmiştir.

### Obsidian

Obsidian uygulaması repoya gömülü gelmez; ancak repo düz Markdown yapısıyla doğrudan vault olarak açılabilir.

Önerilen kullanım:

- bütün repoyu vault olarak açıp `books/`, `ai/`, `indexes/` arasında gezinmek
- veya yalnızca `books/` klasörünü ayrı bir vault olarak kullanmak

### Graphify

Graphify, bu korpus üzerinde bilgi grafı, GraphRAG, konu kümeleri ve keşif odaklı AI navigasyonu kurmak için mantıklıdır. Bu yüzden repo yapısı graphify çalıştırmaya uygun tutuldu; fakat üretilen `graphify-out/` çıktıları repoya dahil edilmez.

İsteğe bağlı kurulum:

```bash
python3 -m pip install -r requirements.txt
python3 -m pip install -r requirements-optional.txt
```

Hazır komutlar:

```bash
make catalog
make compare
make ai
make graphify
make graphify-deep
```

## Yeniden üretim

```bash
python3 scripts/compare_all_upstream_official.py
python3 scripts/compare_sozler.py
python3 scripts/compare_sozler_official.py
python3 scripts/compare_mektubat_official.py
python3 scripts/build_catalog.py
python3 scripts/build_ai_corpus.py
```
