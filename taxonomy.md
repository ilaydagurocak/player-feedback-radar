# Yorum Etiket Şeması (v0.2)

Her yorum 1–3 kategori alabilir. Her kategori bir ürün kararına bağlanır;
amaç "oyuncu ne diyor" değil, "PM bununla ne yapar" sorusunu cevaplamak.

| Kategori | Neyi yakalar | Bağlı ürün sorusu / KPI |
|---|---|---|
| `difficulty` | Seviye çok zor/kolay, takılma, "pay-to-win" hissi | Zorluk eğrisi → level churn, D7 retention |
| `ads` | Oyun içi reklam: sık, uzun, atlanamayan, ödeme sonrası reklam | Reklam yoğunluğu ↔ oturum süresi, ad ARPDAU |
| `rewarded_ads` | Ödüllü reklam: daha fazla isteme, günlük limit, ödülün verilmemesi | Rewarded ad engagement, limit ayarı |
| `misleading_ads` | Oyunun reklamlarındaki oyundan farklı olması | UA kreatif ↔ gerçek oyun uyumu, D1 retention |
| `monetization` | Fiyatlar, paketler, pass'ler, harcama baskısı | IAP dönüşüm, paywall konumu |
| `lives_energy` | Can bitmesi, bekleme süreleri | Oturum sayısı, can satın alma oranı |
| `bug_performance` | Çökme, donma, ilerleme kaybı, pil | Crash-free sessions, sürüm kalitesi |
| `content` | Yeni seviye isteği, içerik bitmesi, tekrar; kelime oyunlarında sözlük eksikleri | İçerik tüketim hızı, sözlük kapsamı |
| `events` | Süreli etkinlikler, mini oyunlar, yan modlar: çok/az, adaletsiz, kafa karıştırıcı | Live-ops takvimi, etkinlik katılımı |
| `social_pvp` | Takım, rakip, eşleştirme, bot, hile, sıralama | Sosyal özellik etkileşimi, PvP adaleti |
| `ux_ui` | Arayüz, kontroller, okunabilirlik, tutorial | Onboarding tamamlama, tutorial drop-off |
| `praise` | Genel övgü, eğlenceli, rahatlatıcı | Viral döngü, puan isteme zamanlaması |
| `feature_request` | Somut özellik önerisi | Backlog adayları |

Ek alanlar:
- **sentiment**: `pos` / `neu` / `neg`
- **severity** (sadece olumsuzlar, en az 1): 1 = küçük rahatsızlık, 2 = deneyimi bozuyor, 3 = oyunu bıraktı / bırakmak üzere
- **churn_signal**: yorum oyunu sildiğini/bıraktığını açıkça söylüyor mu (1/0)

## Sürüm notları
- **v0.2**: `misleading_ads`, `rewarded_ads`, `events` eklendi; sözlük sorunları `content` altına alındı.
  Sebep: v0.1 denemesinde "nothing like the ads" yorumları ve ödüllü reklam talepleri yanlış etiketleniyordu.
