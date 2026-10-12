# Player Feedback Radar

Türk mobil oyun stüdyolarının oyunlarına gelen App Store yorumlarını açık kaynak bir dil modeliyle
etiketleyip bulguları **ürün önerilerine** dönüştüren bağımsız bir portföy çalışması.

**[▶ Canlı dashboard](https://ilaydagurocak.github.io/player-feedback-radar/dashboard.html)**

> Bağımsız bir portföy çalışmasıdır; adı geçen şirketlerle herhangi bir bağlantısı yoktur.

## Öne çıkan bulgular (5.404 yorum, Ekim 2026)

| Oyun | Stüdyo | En büyük ürün riski |
|---|---|---|
| Royal Match | Dream Games | Yorumların %15,7'si "oyun reklamdaki gibi değil" diyor (diğer oyunlarda ≤ %2,9); son 30 günde %19,6. Şikâyet edenler oyunun başındaki oyuncular. |
| Toon Blast | Peak | "Para harcamadan geçilmiyor" hissi erken: zorluk şikâyetinde medyan seviye 300 (Royal Match: 1050). Olumsuz yorumların %9,1'i "yıllardır oynuyorum" diyen sadık oyunculardan. |
| Word Tiles GO | Gulliver's Games | Yorumların %47,2'si reklamdan şikâyet; 4–5 yıldız verenlerin bile %23,5'i reklamdan söz ediyor. Asıl sorun maç ortası reklamlar. |
| Color Block Jam | Rollic | Olumsuz yorumların %27,4'ü süre sınırından şikâyet; bu oyuncularda bırakma sinyali %21,4 (diğerlerinde %15,4). |

Her oyun için 3 öneri ve ölçülecek KPI'lar dashboard'da.

### Mağaza puanı ≠ yazılı yorumlar

| Oyun | Mağaza puanı* | Yazılı yorum ort. | Fark |
|---|---|---|---|
| Royal Match | 4,68 | 3,01 | −1,67 |
| Toon Blast | 4,71 | 3,44 | −1,27 |
| Word Tiles GO | 4,74 | 3,08 | −1,66 |
| Color Block Jam | 4,56 | 2,25 | −2,31 |

\* 4 ülke, puan sayısına göre ağırlıklı (12 Ekim 2026, `fetch_store_ratings.py`).
Mağaza puanı çoğunlukla oyun içi puanlama penceresinden gelen hızlı yıldızlardan oluşur; yorum yazan oyuncu ise
genelde bir sorun yaşamıştır. Bu analiz oyunun kalitesini değil, **memnun olmayan oyuncunun neden memnun olmadığını** ölçer.

## Yöntem

1. **Veri** — `fetch_reviews.py`: Apple'ın herkese açık yorum akışından 4 oyun × 4 ülke (ABD, Birleşik Krallık, Almanya, Türkiye).
2. **Etiketleme** — `label_colab.ipynb`: Qwen2.5-7B-Instruct (4-bit, Colab T4, ücretsiz). `taxonomy.md`'deki 13 kategori + duygu + şiddet + bırakma sinyali.
   Prompt dört sürümde iyileştirildi (v0.1 → v0.4: şema genişletme, çözülmüş örnekler, GPU belleği için kısa prompt).
3. **Doğrulama** — 80 yorumluk dengeli örneklem elle kontrol edildi (`data/validation_v0.4.csv`):
   duygu %97,5 · ana konu %97,5 · kategori seti birebir %82,5.
4. **Analiz** — `analyze.py` → `data/summary.json`. Model etiketlerine ek olarak anahtar kelime işaretleri
   (seviye numarası, zamanlayıcı, "yıllardır oynuyorum") ile çapraz kontrol.
5. **Dashboard** — `build_dashboard_data.py` → `dashboard_data/`, `build_standalone.py` → `dashboard.html`. Her sayı bir veri dosyasındaki satıra bağlı; `dashboard.html` çift tıklayınca internetsiz açılır.

### Öğrenilenler
- 3B model kısa övgüleri "arayüz", reklamla uyuşmazlık şikâyetlerini "bug" sanıyordu; 7B + çözülmüş örneklerle ana konu doğruluğu %97,5'e çıktı.
- Şemada **zamanlayıcı** kategorisi yoktu; model Color Block Jam'deki süre şikâyetlerinin %55,8'ini bug/UX diye etiketledi.
  Anahtar kelime kontrolü bunu yakaladı → v0.5'te `timer` kategorisi eklenecek.

### Sınırlar
- Yazılı yorumlar memnuniyetsiz oyunculara doğru kayar; sonuçlar mağaza puanını temsil etmez.
- Apple akışı ülke başına son ~500 yorumu verir; oyunların zaman pencereleri farklıdır.
- Seviye medyanları az sayıda yoruma dayanır (n=13–116). Word Tiles GO örneklemi küçük (199 yorum).

## Çalıştırma

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python fetch_reviews.py          # -> data/reviews.csv (yeni yorumları ekler)
python fetch_store_ratings.py    # -> data/store_ratings.csv (mağaza puanları)
# Etiketleme: label_colab.ipynb'yi Colab'da çalıştır -> labels_v0.4.csv'yi data/ altına koy
python analyze.py                # -> data/summary.json
python build_dashboard_data.py   # -> dashboard_data/*.csv
python build_standalone.py       # -> dashboard.html (tarayıcıda çevrimdışı açılır)
```

Apple akışı ülke başına yalnızca son ~500 yorumu verdiği için `fetch_reviews.py`'yi haftada bir çalıştırmak
veri setini zamanla büyütür. Yeni oyun eklemek için `apps.py`'ye bir satır eklemek yeterli.

## Veri ve gizlilik

- Kullanıcı adları hiç saklanmaz; yorum kimlikleri hash'lenir.
- Ham yorumlar repoya konmaz (`data/` gitignore'da). Yalnızca kod ve toplu bulgular paylaşılır.

## Yol haritası

1. Veri toplama ✅
2. Etiketleme + doğrulama ✅
3. Bulgular + dashboard ✅
4. v0.5: `timer` kategorisi, sürüm notları ↔ yorum eşleştirmesi
5. Oyun başına 1 sayfalık insight raporu (başvurulara eklemek için)
