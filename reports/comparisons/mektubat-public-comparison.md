# Mektubat Public Comparison Report

- Kaynak aynası: `sources/official-markdown-mirror/obsidian-markdown/02 Mektubat/`
- Public kaynak: resmi Hizmet Vakfı `Mektubat` sayfaları
- Public index: https://risaleinur.hizmetvakfi.org/mektubat/
- Yöntem: resmi site menüsündeki tüm `Mektubat` bağlantıları scrape edilip bölüm bazlı normalize token karşılaştırması yapıldı

## Summary

- Public tarafta bulunan bölüm sayısı: **39**
- Ortak bölüm sayısı: **39**
- Genel sıra-duyarlı benzerlik: **0.9956**
- Genel içerik örtüşmesi: **0.9947**
- Toplam farklı token: **870**
- Yalnız upstream'de bulunan bölümler: **0**
- Yalnız public tarafta bulunan bölümler: **0**
- En büyük fark bloğu: **On Dokuzuncu Mektup** (486 farklı token, benzerlik 0.9915)

## Coverage gaps

## Lowest-similarity overlapping sections

| Bölüm | Sıra benzerliği | İçerik örtüşmesi | Fark tokenı | Upstream | Public |
| --- | ---: | ---: | ---: | --- | --- |
| Hakikat Çekirdekleri | 0.9551 | 0.9553 | 140 | `sources/official-markdown-mirror/obsidian-markdown/02 Mektubat/35 Hakikat Çekirdekleri.md` | [public](https://risaleinur.hizmetvakfi.org/hakikat-cekirdekleri/) |
| On Dokuzuncu Mektup | 0.9915 | 0.9891 | 486 | `sources/official-markdown-mirror/obsidian-markdown/02 Mektubat/19 On Dokuzuncu Mektup.md` | [public](https://risaleinur.hizmetvakfi.org/on-dokuzuncu-mektup/) |
| Fihriste-i Mektubat | 0.9933 | 0.9924 | 66 | `sources/official-markdown-mirror/obsidian-markdown/02 Mektubat/37 Fihriste-i Mektubat.md` | [public](https://risaleinur.hizmetvakfi.org/fihriste-i-mektubat/) |
| Dördüncü Mektup | 0.9933 | 0.9905 | 5 | `sources/official-markdown-mirror/obsidian-markdown/02 Mektubat/04 Dördüncü Mektup.md` | [public](https://risaleinur.hizmetvakfi.org/dorduncu-mektup/) |
| On Üçüncü Mektup | 0.9949 | 0.9933 | 8 | `sources/official-markdown-mirror/obsidian-markdown/02 Mektubat/13 On Üçüncü Mektup.md` | [public](https://risaleinur.hizmetvakfi.org/on-ucuncu-mektup/) |
| Birinci Mektup | 0.9951 | 0.9960 | 13 | `sources/official-markdown-mirror/obsidian-markdown/02 Mektubat/01 Birinci Mektup.md` | [public](https://risaleinur.hizmetvakfi.org/birinci-mektup/) |
| Yirmi Birinci Mektup | 0.9962 | 0.9949 | 4 | `sources/official-markdown-mirror/obsidian-markdown/02 Mektubat/21 Yirmi Birinci Mektup.md` | [public](https://risaleinur.hizmetvakfi.org/yirmi-birinci-mektup/) |
| Beşinci Mektup | 0.9962 | 0.9925 | 3 | `sources/official-markdown-mirror/obsidian-markdown/02 Mektubat/05 Beşinci Mektup.md` | [public](https://risaleinur.hizmetvakfi.org/besinci-mektup/) |
| Altıncı Mektup | 0.9976 | 0.9968 | 2 | `sources/official-markdown-mirror/obsidian-markdown/02 Mektubat/06 Altıncı Mektup.md` | [public](https://risaleinur.hizmetvakfi.org/altinci-mektup/) |
| Yirmi Altıncı Mektup | 0.9977 | 0.9973 | 32 | `sources/official-markdown-mirror/obsidian-markdown/02 Mektubat/26 Yirmi Altıncı Mektup.md` | [public](https://risaleinur.hizmetvakfi.org/yirmi-altinci-mektup/) |

## Representative divergence snippets

### Hakikat Çekirdekleri

- Sıra benzerliği: **0.9551** · İçerik örtüşmesi: **0.9553** · Fark tokenı: **140** · Public: https://risaleinur.hizmetvakfi.org/hakikat-cekirdekleri/

1. `replace`
   - Upstream: 1.
   - Public: 1-
2. `replace`
   - Upstream: 2.
   - Public: 2-
3. `replace`
   - Upstream: 3.
   - Public: 3-

### On Dokuzuncu Mektup

- Sıra benzerliği: **0.9915** · İçerik örtüşmesi: **0.9891** · Fark tokenı: **486** · Public: https://risaleinur.hizmetvakfi.org/on-dokuzuncu-mektup/

1. `replace`
   - Upstream: Birincisi
   - Public: Birincisi:
2. `replace`
   - Upstream: İkincisi
   - Public: İkincisi:
3. `replace`
   - Upstream: Üçüncüsü
   - Public: Üçüncüsü:

### Fihriste-i Mektubat

- Sıra benzerliği: **0.9933** · İçerik örtüşmesi: **0.9924** · Fark tokenı: **66** · Public: https://risaleinur.hizmetvakfi.org/fihriste-i-mektubat/

1. `replace`
   - Upstream: MEKTUP
   - Public: MEKTUP:
2. `replace`
   - Upstream: MEKTUP
   - Public: MEKTUP:
3. `replace`
   - Upstream: MEKTUP
   - Public: MEKTUP:

### Dördüncü Mektup

- Sıra benzerliği: **0.9933** · İçerik örtüşmesi: **0.9905** · Fark tokenı: **5** · Public: https://risaleinur.hizmetvakfi.org/dorduncu-mektup/

1. `replace`
   - Upstream: [^hâşiye1]
   - Public: (Hâşiye [1] )
2. `replace`
   - Upstream: [^hâşiye1]:
   - Public: [1] Hâşiye:

### On Üçüncü Mektup

- Sıra benzerliği: **0.9949** · İçerik örtüşmesi: **0.9933** · Fark tokenı: **8** · Public: https://risaleinur.hizmetvakfi.org/on-ucuncu-mektup/

1. `replace`
   - Upstream: ‌ اَلْحَمْدُ
   - Public: ‌اَلْحَمْدُ
2. `replace`
   - Upstream: حَالٍ ‌
   - Public: حَالٍ‌
3. `replace`
   - Upstream: ‌ اَعُوذُ
   - Public: ‌اَعُوذُ

## Notes

- `Sıra benzerliği`, token dizilerinin sırasını da dikkate alır; başlık/ara başlık yer değişimleri ve uzun blok kaymaları bu metriği sert düşürebilir.
- `İçerik örtüşmesi`, token çoklu-küme kesişimine bakar; aynı malzemenin farklı akış veya imla ile verildiği durumları daha doğru yansıtır.
- Karşılaştırmada frontmatter, sayfa işaretleri ve markdown ayraçları temizlendi; anlamlı metin gövdesi token bazında ölçüldü.
- Upstream birleştirilmiş çıktı `generated/text/upstream-mektubat-merged.md` dosyasına yazıldı.
- Ayrıntılı veri `generated/json/mektubat-public-comparison.json` içinde tutulur; scrape çıktısı `generated/json/official-mektubat-scrape.json` dosyasına yazılır.
