# AI Corpus Layer

Bu klasör, `books/` altındaki doğrulanmış metinlerin AI retrieval için hazırlanmış yapısal kopyasıdır.
Üst düzey `books/` klasörü insan okuması içindir; bu klasör ise AI sistemlerinin kullanacağı türetilmiş kopyayı içerir.

## Amaç

- metni yeniden yazmadan AI dostu bir kopya üretmek
- kitap / bölüm / pasaj düzeyinde stabil kimlik vermek
- cevaplarda güvenilir atıf ve izlenebilir provenans sağlamak
- yanlış yönlendirme riskini azaltmak

## Yapı

- `books/` - AI için frontmatter ile zenginleştirilmiş kitap ve bölüm kopyaları
- `manifests/` - kitap bazlı yapısal JSON manifestleri
- `passages/` - retrieval için chunk JSONL dosyaları
- `catalog.json` - tüm AI katmanının üst seviye kataloğu
- `ANSWERING_POLICY.md` - chatbot / retrieval ajanı için güvenlik kuralları

## Kapsam

- Kitap sayısı: **15**
- Bölüm sayısı: **296**
- Pasaj sayısı: **3079**

## Üretim

```bash
python3 scripts/build_ai_corpus.py
```
