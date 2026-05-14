# AI Answering Policy

Bu klasör, Risale-i Nur metinlerinden AI retrieval için hazırlanmış güvenli katmandır.

## Zorunlu kurallar

1. Cevap üretirken öncelik `ai/passages/*.jsonl` ve `ai/books/*/sections/*.md` dosyaları olmalıdır.
2. Her cevap en az bir açık atıf içermelidir: kitap, bölüm ve mümkünse `chunk_id`.
3. Dinî hüküm veya anlam aktarımı yapılırken önce metnin kendisi, sonra kısa açıklama verilmelidir.
4. Belirsiz durumda sentez yapılmaz; `metinde açık dayanak bulunamadı` denir.
5. Farklı pasajlar birleştirilecekse her pasaj ayrı cite edilmelidir.
6. Bir pasaj tek başına yetersizse aynı bölüm içindeki komşu chunk'lar birlikte okunmalıdır.
7. Kanonik kaynak ile çelişen dış kaynaklara göre cevap verilmez.

## Önerilen retrieval akışı

1. Soru için önce lexical + semantic retrieval yap.
2. En iyi 5-10 chunk içinden aynı bölümde kümelenenleri topla.
3. Gerekirse `previous_chunk_id` ve `next_chunk_id` ile bağlamı genişlet.
4. Cevabı yalnız doğruladığın chunk'lara dayandır.
