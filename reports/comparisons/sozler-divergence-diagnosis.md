# Sözler Divergence Diagnosis

## Compared sources

| Kaynak | Tür | Yol / URL | Not |
| --- | --- | --- | --- |
| Yerel repo metni | Yerel kanonik kaynak | `canonical/furkan/sozler/Sozler.md` ve `canonical/furkan/sozler/by_heading/` | Mevcut çalışma metni; kapak, sayfa işaretleri ve başlık bazlı ayrım içeriyor |
| Resmi public metin | Scrape edilen otoritatif web kaynağı | `https://risaleinur.hizmetvakfi.org/sozler-2/` | Hizmet Vakfı / DİB asıl nüsha zinciri |
| Ali Tekdemir mirror | Public GitHub mirror | `upstream/alitekdemir/obsidian-markdown/01 Sözler/` | Resmi metnin Markdown aynası; scrape doğrulaması için kullanıldı |

## Trust decision

| Karar alanı | Hüküm |
| --- | --- |
| Otoritatif baz metin | **Resmi Hizmet Vakfı public metni** |
| Scrape güvenilir mi? | **Evet.** Resmi site ile Ali Tekdemir mirror arasında 36 ortak bölümde ortalama **0.9948** sıra benzerliği var |
| Yerel repo tamamen yanlış mı? | **Hayır.** Büyük ölçüde aynı metin ailesi; farkların çoğu edisyon, imla, yapı ve kapsam farkı |
| “Doğru” tercih hangisi? | **DİB/Hizmet Vakfı asıl nüsha hedefleniyorsa official/public metin doğru referans**; yerel repo ise eski baskı/edisyon şahidi olarak değerli |

## Global result

| Ölçü | Sonuç |
| --- | ---: |
| Official public bölüm sayısı | 36 |
| Yerel + public ortak bölüm | 36 |
| Genel sıra-duyarlı benzerlik | 0.8997 |
| Genel içerik örtüşmesi | 0.9537 |
| Yerelde olup public tarafta olmayan bölüm | 2 |

## Why the differences happen

| Fark tipi | Yerel repo görünümü | Official/public görünümü | Neden |
| --- | --- | --- | --- |
| Korpus kapsamı | `Kapak ve Giriş`, `Anglikan Kilisesine Cevab` var | Sözler menüsünde yok | **Editoryal kapsam farkı**; official Sözler seti bu iki parçayı ayrı/harici tutuyor |
| Frontmatter / repo aparatı | YAML frontmatter, `slug`, `start_page`, `end_page` var | Yok | **Repo üretim katmanı farkı**; metinsel ihtilaf değil |
| Sayfa yapısı | `[Page N]` işaretleri ve bölümleme korunmuş | Web akışı içinde verilmiş | **Baskı dizgisi vs web sunumu farkı** |
| İmla | `kıymetdar`, `Kur'anın`, `İHTAR:` gibi | `kıymettar`, `Kur’an’ın`, `İhtar:` gibi | **Edisyon / modernizasyon farkı** |
| Arapça dizgi | Daha sade Unicode biçimi | Daha yoğun hareke / tipografik form | **Arapça imla ve dizgi standardı farkı** |
| Başlık yerleşimi | Bölüm başı ve ara başlıklar repo mantığıyla sabit | Web’de bazı başlıklar/ayetler farklı akışta | **Yapısal akış farkı** |
| Büyük blok kaymaları | Özellikle `Onuncu Söz`te sıra skoru düşüyor | Aynı malzeme farklı blok akışıyla geliyor | **Uzun bölüm içi yeniden akış / segmentasyon farkı** |

## Section diagnosis table

| Bölüm | Sıra benzerliği | İçerik örtüşmesi | Ana sebep | Doğru / tercih |
| --- | ---: | ---: | --- | --- |
| Onuncu Söz | 0.2649 | 0.8288 | Uzun blokların akışı, başlık yerleşimi, editoryal segmentasyon | **Official/public tercih edilmeli**; yerel metin büyük ölçüde aynı içerik ailesinde |
| Onikinci Söz | 0.7768 | 0.7826 | Başta ek Besmele/ayet satırı, imla farkları | **Official/public tercih edilmeli** |
| Ondördüncü Söz | 0.7921 | 0.7843 | Başlangıç ayeti + modern imla + başlık biçimi | **Official/public tercih edilmeli** |
| Birinci Söz | 0.8027 | 0.7987 | Arapça yazım, başlık yerleşimi, tipografik normalizasyon | **Her iki metin de aynı çekirdeği taşıyor**; DİB hedefinde official üstün |
| Onüçüncü Söz | 0.8141 | 0.8125 | Bölüm içi akış ve imla farkları | **Official/public tercih edilmeli** |
| Onbirinci Söz | 0.8378 | 0.8274 | İmla + yapı + küçük editoryal farklar | **Official/public tercih edilmeli** |
| Onbeşinci Söz | 0.8451 | 0.8654 | İmla + bazı blok/başlık yer farkları | **Official/public tercih edilmeli** |
| Beşinci Söz | 0.8306 | 0.8188 | Özellikle Arapça dizgi ve küçük imla ayrımı | **İki metin çok yakın** |
| Yedinci Söz | 0.8124 | 0.8202 | Arapça form, `kıymetdar/kıymettar` tipi farklar | **İki metin çok yakın** |
| Konferans | 0.9997 | 0.9996 | Anlamlı fark yok | **Pratikte aynı** |

## Concrete examples

| Alan | Yerel repo | Official/public | Tanı | Hüküm |
| --- | --- | --- | --- | --- |
| Birinci Söz açılışı | `الرَّحِيمِ وَبِهِ نَسْتَعِينُ` | `الرَّحٖيمِ وَ بِهٖ نَسْتَعٖينُ` | Arapça dizgi / hareke yoğunluğu farkı | **Official/public asıl nüsha standardına daha yakın** |
| Yedinci Söz | `kıymetdar` | `kıymettar` | İmla/edisyon farkı | **Official/public tercih** |
| Ondördüncü Söz | Yerelde ayet satırı daha sade/başlıkla birleşik | Official’da ayet açık biçimde başta | Web/DİB redaksiyonu | **Official/public tercih** |
| Onuncu Söz | Aynı konu başlıkları var ama blok akışı farklı | Aynı malzeme daha farklı dizilimle verilmiş | Yapısal yeniden akış | **Official/public baz alınmalı; yerel tamamen farklı metin değil** |
| Kapak ve Giriş | Var | Yok | Sözler çekirdek metni dışında bırakılmış | **Yanlış değil; kapsam farkı** |
| Anglikan Kilisesine Cevab | Var | Yok | Official Sözler menüsüne dahil edilmemiş | **Yanlış değil; kapsam farkı** |

## Final judgment

1. **Scrape edilen official/public metin güvenilir ve kullanılabilir.**
2. **Ali Tekdemir mirror, official kaynağı çok yüksek doğrulukla yansıtıyor**; yani public scrape sonucu tesadüfi değil.
3. **Yerel repo metni çoğu yerde aynı içerik ailesine ait**, ancak:
   - eski baskı/edisyon izleri taşıyor,
   - repo/frontmatter/page apparatus içeriyor,
   - bazı bölümlerde daha eski imla ve dizgi biçimini koruyor,
   - official Sözler kümesinde olmayan iki ek parça içeriyor.
4. Bu yüzden **“DİB/Hizmet Vakfı asıl nüsha açısından doğru baz” = official/public metin**.
5. **Yerel repo “yanlış metin” değil; ama farklı edisyon mantığıyla korunmuş bir varyant.**
