# Sözler Normalized Summary

İmla, hareke, apostrof, eski-yeni yazım ve benzeri yüzey farkları büyük ölçüde bastırılarak yapılan karşılaştırma özeti.

## Global alignment

| Karşılaştırma | Ortak bölüm | Sıra benzerliği | İçerik örtüşmesi | Jaccard |
| --- | ---: | ---: | ---: | ---: |
| Yerel repo vs official/public | 36 | 0.9739 | 0.9825 | 0.9739 |
| Yerel repo vs Ali Tekdemir | 36 | 0.9734 | 0.9816 | 0.9729 |

## Interpretation

| Sonuç | Yorum |
| --- | --- |
| `0.9825` official içerik örtüşmesi | İmla ve eski yazım farkları ayıklanınca yerel repo, official/public metinle **çok yüksek derecede uyumlu** |
| `0.9816` Ali içerik örtüşmesi | Aynı şekilde Ali mirror ile de **çok yüksek uyumlu** |
| Official ve Ali sonuçları birbirine çok yakın | Kalan farkların ana kaynağı yerel repo varyantı; official ile Ali neredeyse aynı çizgide |

## Where differences still remain

| Bölüm | Official içerik örtüşmesi | Ali içerik örtüşmesi | Kalan farkın ana sebebi |
| --- | ---: | ---: | --- |
| Onuncu Söz | 0.9440 | 0.9437 | Uzun blok akışı, giriş düzeni, ek Besmele/ayet ve segmentasyon farkı |
| Onbeşinci Söz | 0.9413 | 0.9413 | Bölüm başı ayet yerleşimi ve yapı farkı |
| Onbirinci Söz | 0.9338 | 0.9338 | Başta ek ayet/satır ve küçük yapı farkları |
| Dördüncü Söz | 0.9199 | 0.9199 | Kısa ama gerçek kelime farkları (`altun/altin`, `kerre/kere`) |
| Beşinci Söz | 0.9110 | 0.9110 | Kısa yapı + kelime varyantı |
| Onüçüncü Söz | 0.9064 | 0.9061 | Başlangıç ayet bloğu ve akış farkı |
| Ondördüncü Söz | 0.9045 | 0.9045 | Başlangıç ayeti ve bazı çekim/kelime farkları |
| Birinci Söz | 0.9442 | 0.9036 | Yereldeki başlık tekrarları ve Arapça açılış dizgi farkı |

## Practical judgment

1. İmla ve eski yazım farklarını saymazsan, senin hazırladığın metin hem official/public kaynağa hem de Ali Tekdemir mirror’ına **yaklaşık %98 seviyesinde uyumlu**.
2. Kalan farkların çoğu artık “yanlışlık” değil; **bölüm başı ayet ekleri, blok sıralaması, segmentasyon ve az sayıda gerçek kelime tercihi** farkı.
3. Official/public ile Ali karşılaştırması zaten çok yakın olduğu için, yerel repo ile her ikisine karşı kalan farklar büyük ölçüde aynı noktalarda toplanıyor.
