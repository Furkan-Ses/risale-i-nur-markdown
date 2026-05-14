# Corpus Index

Bu indeks, Ali Tekdemir'in Obsidian tipi içindekiler mantığını korurken daha sade ve AI-dostu bir erişim katmanı ekler.

## İndeks mantığı

1. **Ali modeli:** `01 İçindekiler.md` -> kitap klasörü -> kitap içi `00` index -> bölüm dosyaları
2. **Bu repo modeli:** `README.md` -> `indexes/README.md` -> `indexes/books/*.md` -> kanonik / upstream metinler -> `generated/json/catalog.json`
3. **Sözler için ek katman:** düzeltilmiş yerel kanonik `Sozler.md` ve `by_heading/` dosyaları ayrıca indekslenir

## Upstream books

| # | Kitap | Bölüm | Upstream index | Yeni indeks |
| --- | --- | ---: | --- | --- |
| 1 | Sözler | 36 | [00 SÖZLER.md](../upstream/alitekdemir/obsidian-markdown/01 Sözler/00 SÖZLER.md) | [01-sozler.md](books/01-sozler.md) |
| 2 | Mektubat | 39 | [00 MEKTUBAT.md](../upstream/alitekdemir/obsidian-markdown/02 Mektubat/00 MEKTUBAT.md) | [02-mektubat.md](books/02-mektubat.md) |
| 3 | Lem'alar | 36 | [00 LEM’ALAR.md](../upstream/alitekdemir/obsidian-markdown/03 Lem'alar/00 LEM’ALAR.md) | [03-lemalar.md](books/03-lemalar.md) |
| 4 | Şuâlar | 18 | [00 ŞUÂLAR.md](../upstream/alitekdemir/obsidian-markdown/04 Şuâlar/00 ŞUÂLAR.md) | [04-sualar.md](books/04-sualar.md) |
| 5 | Tarihçe-i Hayat | 12 | [00 TARİHÇE-İ HAYAT.md](../upstream/alitekdemir/obsidian-markdown/05 Tarihçe-i Hayat/00 TARİHÇE-İ HAYAT.md) | [05-tarihce-i-hayat.md](books/05-tarihce-i-hayat.md) |
| 6 | Mesnevî-i Nuriye | 16 | [00 MESNEVÎ-İ NURİYE.md](../upstream/alitekdemir/obsidian-markdown/06 Mesnevî-i Nuriye/00 MESNEVÎ-İ NURİYE.md) | [06-mesnevi-i-nuriye.md](books/06-mesnevi-i-nuriye.md) |
| 7 | İşaratü'l-i'caz | 27 | [00 İŞARATÜ’L-İ’CAZ.md](../upstream/alitekdemir/obsidian-markdown/07 İşaratü'l-i'caz/00 İŞARATÜ’L-İ’CAZ.md) | [07-isaratul-icaz.md](books/07-isaratul-icaz.md) |
| 8 | Sikke-i Tasdik-i Gaybî | 8 | [00 SİKKE-İ TASDİK-İ GAYBÎ.md](../upstream/alitekdemir/obsidian-markdown/08 Sikke-i Tasdik-i Gaybî/00 SİKKE-İ TASDİK-İ GAYBÎ.md) | [08-sikke-i-tasdik-i-gaybi.md](books/08-sikke-i-tasdik-i-gaybi.md) |
| 9 | Barla Lâhikası | 20 | [00 BARLA LÂHİKASI.md](../upstream/alitekdemir/obsidian-markdown/09 Barla Lâhikası/00 BARLA LÂHİKASI.md) | [09-barla-lahikasi.md](books/09-barla-lahikasi.md) |
| 10 | Kastamonu Lâhikası | 13 | [00 KASTAMONU LÂHİKASI.md](../upstream/alitekdemir/obsidian-markdown/10 Kastamonu Lâhikası/00 KASTAMONU LÂHİKASI.md) | [10-kastamonu-lahikasi.md](books/10-kastamonu-lahikasi.md) |
| 11 | Emirdağ Lâhikası 1 | 15 | [00 EMİRDAĞ LÂHİKASI - I.md](../upstream/alitekdemir/obsidian-markdown/11 Emirdağ Lâhikası 1/00 EMİRDAĞ LÂHİKASI - I.md) | [11-emirdag-lahikasi-1.md](books/11-emirdag-lahikasi-1.md) |
| 12 | Emirdağ Lâhikası 2 | 12 | [00 EMİRDAĞ LÂHİKASI - II.md](../upstream/alitekdemir/obsidian-markdown/12 Emirdağ Lâhikası 2/00 EMİRDAĞ LÂHİKASI - II.md) | [12-emirdag-lahikasi-2.md](books/12-emirdag-lahikasi-2.md) |
| 13 | Asâ-yı Musa | 25 | [000 ASÂ-YI MUSA.md](../upstream/alitekdemir/obsidian-markdown/13 Asâ-yı Musa/000 ASÂ-YI MUSA.md) | [13-asa-yi-musa.md](books/13-asa-yi-musa.md) |
| 14 | Muhakemat | 6 | [00 MUHAKEMAT.md](../upstream/alitekdemir/obsidian-markdown/14 Muhakemat/00 MUHAKEMAT.md) | [14-muhakemat.md](books/14-muhakemat.md) |
| 15 | Küçük Kitaplar | 12 | [00 KÜÇÜK KİTAPLAR.md](../upstream/alitekdemir/obsidian-markdown/15 Küçük Kitaplar/00 KÜÇÜK KİTAPLAR.md) | [15-kucuk-kitaplar.md](books/15-kucuk-kitaplar.md) |

## Canonical references

| Kaynak | Birleşik dosya | Bölüm klasörü |
| --- | --- | --- |
| Furkan canonical Asa-yi Musa reference | [Asa-yi Musa.md](../canonical/furkan/asa-yi-musa/Asa-yi Musa.md) | [by_heading](../canonical/furkan/asa-yi-musa/by_heading) |
| Furkan canonical Barla Lahikasi reference | [Barla Lahikasi.md](../canonical/furkan/barla-lahikasi/Barla Lahikasi.md) | [by_heading](../canonical/furkan/barla-lahikasi/by_heading) |
| Furkan canonical Emirdag Lahikasi 1 reference | [Emirdag Lahikasi 1.md](../canonical/furkan/emirdag-lahikasi-1/Emirdag Lahikasi 1.md) | [by_heading](../canonical/furkan/emirdag-lahikasi-1/by_heading) |
| Furkan canonical Emirdag Lahikasi 2 reference | [Emirdag Lahikasi 2.md](../canonical/furkan/emirdag-lahikasi-2/Emirdag Lahikasi 2.md) | [by_heading](../canonical/furkan/emirdag-lahikasi-2/by_heading) |
| Furkan canonical Isaratul-icaz reference | [Isaratul-icaz.md](../canonical/furkan/isaratul-icaz/Isaratul-icaz.md) | [by_heading](../canonical/furkan/isaratul-icaz/by_heading) |
| Furkan canonical Kastamonu Lahikasi reference | [Kastamonu Lahikasi.md](../canonical/furkan/kastamonu-lahikasi/Kastamonu Lahikasi.md) | [by_heading](../canonical/furkan/kastamonu-lahikasi/by_heading) |
| Furkan canonical Kucuk Kitaplar reference | [Kucuk Kitaplar.md](../canonical/furkan/kucuk-kitaplar/Kucuk Kitaplar.md) | [by_heading](../canonical/furkan/kucuk-kitaplar/by_heading) |
| Furkan canonical Lemalar reference | [Lemalar.md](../canonical/furkan/lemalar/Lemalar.md) | [by_heading](../canonical/furkan/lemalar/by_heading) |
| Furkan canonical Mektubat reference | [Mektubat.md](../canonical/furkan/mektubat/Mektubat.md) | [by_heading](../canonical/furkan/mektubat/by_heading) |
| Furkan canonical Mesnevi-i Nuriye reference | [Mesnevi-i Nuriye.md](../canonical/furkan/mesnevi-i-nuriye/Mesnevi-i Nuriye.md) | [by_heading](../canonical/furkan/mesnevi-i-nuriye/by_heading) |
| Furkan canonical Muhakemat reference | [Muhakemat.md](../canonical/furkan/muhakemat/Muhakemat.md) | [by_heading](../canonical/furkan/muhakemat/by_heading) |
| Furkan canonical Sikke-i Tasdik-i Gaybi reference | [Sikke-i Tasdik-i Gaybi.md](../canonical/furkan/sikke-i-tasdik-i-gaybi/Sikke-i Tasdik-i Gaybi.md) | [by_heading](../canonical/furkan/sikke-i-tasdik-i-gaybi/by_heading) |
| Furkan canonical Sozler reference | [Sozler.md](../canonical/furkan/sozler/Sozler.md) | [by_heading](../canonical/furkan/sozler/by_heading) |
| Furkan canonical Sualar reference | [Sualar.md](../canonical/furkan/sualar/Sualar.md) | [by_heading](../canonical/furkan/sualar/by_heading) |
| Furkan canonical Tarihce-i Hayat reference | [Tarihce-i Hayat.md](../canonical/furkan/tarihce-i-hayat/Tarihce-i Hayat.md) | [by_heading](../canonical/furkan/tarihce-i-hayat/by_heading) |

## Generated assets

- `generated/json/catalog.json`: kitap ve bölüm kataloğu
- `generated/json/all-upstream-public-summary.json`: tüm upstream kitaplar için toplu uyum özeti
- `generated/json/books/`: kitap bazlı official scrape ve karşılaştırma verileri
- `reports/comparisons/all-upstream-public-summary.md`: insan-okur toplu özet raporu
- `reports/comparisons/books/`: kitap bazlı karşılaştırma raporları
