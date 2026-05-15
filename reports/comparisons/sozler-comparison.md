# Sözler Comparison Report

- Doğrulanmış kitap kaynağı: `books/sozler/Sozler.md`
- Kaynak aynası: `sources/official-markdown-mirror/obsidian-markdown/01 Sözler/`
- Karşılaştırma yöntemi: frontmatter ve HTML etiketleri temizlenmiş, bölüm bazlı normalize metin karşılaştırması

## Summary

- Ortak bölüm sayısı: **36**
- Genel benzerlik oranı: **0.9005**
- Toplam farklı token: **39741**
- Yalnız yerelde bulunan bölümler: **2**
- Yalnız upstream'de bulunan bölümler: **0**

- En büyük fark bloğu: **Onuncu Söz** (31783 farklı token, benzerlik 0.2697)

### Local-only sections

- Anglikan Kilisesine Cevab (`books/sozler/by_heading/035 - Anglikan Kilisesine Cevab.md`)
- Kapak ve Giriş (`books/sozler/by_heading/000 - Kapak ve Giriş.md`)

## Lowest-similarity overlapping sections

| Bölüm | Benzerlik | Fark tokenı | Yerel | Upstream |
| --- | ---: | ---: | --- | --- |
| Onuncu Söz | 0.2697 | 31783 | `books/sozler/by_heading/010 - Onuncu Söz.md` | `sources/official-markdown-mirror/obsidian-markdown/01 Sözler/10 Onuncu Söz.md` |
| Birinci Söz | 0.8020 | 740 | `books/sozler/by_heading/001 - Birinci Söz.md` | `sources/official-markdown-mirror/obsidian-markdown/01 Sözler/01 Birinci Söz.md` |
| Ondördüncü Söz | 0.8067 | 850 | `books/sozler/by_heading/014 - Ondördüncü Söz.md` | `sources/official-markdown-mirror/obsidian-markdown/01 Sözler/14 On Dördüncü Söz.md` |
| Onikinci Söz | 0.8236 | 363 | `books/sozler/by_heading/012 - Onikinci Söz.md` | `sources/official-markdown-mirror/obsidian-markdown/01 Sözler/12 On İkinci Söz.md` |
| Yedinci Söz | 0.8296 | 214 | `books/sozler/by_heading/007 - Yedinci Söz.md` | `sources/official-markdown-mirror/obsidian-markdown/01 Sözler/07 Yedinci Söz.md` |
| Onüçüncü Söz | 0.8320 | 1464 | `books/sozler/by_heading/013 - Onüçüncü Söz.md` | `sources/official-markdown-mirror/obsidian-markdown/01 Sözler/13 On Üçüncü Söz.md` |
| Beşinci Söz | 0.8365 | 113 | `books/sozler/by_heading/005 - Beşinci Söz.md` | `sources/official-markdown-mirror/obsidian-markdown/01 Sözler/05 Beşinci Söz.md` |
| Dokuzuncu Söz | 0.8475 | 366 | `books/sozler/by_heading/009 - Dokuzuncu Söz.md` | `sources/official-markdown-mirror/obsidian-markdown/01 Sözler/09 Dokuzuncu Söz.md` |
| Üçüncü Söz | 0.8498 | 110 | `books/sozler/by_heading/003 - Üçüncü Söz.md` | `sources/official-markdown-mirror/obsidian-markdown/01 Sözler/03 Üçüncü Söz.md` |
| Altıncı Söz | 0.8535 | 197 | `books/sozler/by_heading/006 - Altıncı Söz.md` | `sources/official-markdown-mirror/obsidian-markdown/01 Sözler/06 Altıncı Söz.md` |

## Notes

- `Kapak ve Giriş` ile `Anglikan Kilisesine Cevab` yalnız yerel kanonik sette bulunduğu için genel benzerlik hesabına dahil edilmedi.
- Benzerlik metriği, sayfa işaretleri, markdown başlıkları, HTML etiketleri ve dipnot numaraları temizlendikten sonra token dizileri üzerinden hesaplandı.
- Upstream birleştirilmiş çıktı `generated/text/upstream-sozler-merged.md` dosyasına yazıldı.
- Ayrıntılı sayısal veri `generated/json/sozler-comparison.json` içinde tutulur.

