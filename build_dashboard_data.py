"""data/summary.json'dan dashboard veri dosyalarını üretir (dashboard_data/*.csv).

Kullanım:
    python analyze.py && python build_dashboard_data.py
"""

import csv
import json
import os

S = json.load(open("data/summary.json", encoding="utf-8"))
OUT = "dashboard_data"
os.makedirs(OUT, exist_ok=True)

CAT_TR = {
    "difficulty": "Zorluk", "monetization": "Monetizasyon", "ads": "Oyun içi reklam",
    "rewarded_ads": "Ödüllü reklam", "misleading_ads": "Reklamla uyuşmazlık",
    "lives_energy": "Can / bekleme", "bug_performance": "Bug / performans",
    "content": "İçerik", "events": "Etkinlikler", "social_pvp": "Sosyal / PvP",
    "ux_ui": "Arayüz / UX", "feature_request": "Özellik isteği",
}
COUNTRY_TR = {"us": "ABD", "gb": "Birleşik Krallık", "de": "Almanya", "tr": "Türkiye"}


def write(name, rows, fields):
    with open(os.path.join(OUT, name), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(name, len(rows))


# Oyun KPI'ları
write("games.csv", [
    {"game": g, "company": v["company"], "store_rating": v.get("store_rating"), "store_count": v.get("store_count"),
     "avg_rating": v["avg_rating"], "gap": v.get("gap"), "reviews": v["n"],
     "neg_pct": v["neg_pct"], "churn_pct": v["churn_pct"], "severe_pct": v["severe_pct"]}
    for g, v in S["games"].items()
], ["game", "company", "store_rating", "store_count", "avg_rating", "gap", "reviews",
    "neg_pct", "churn_pct", "severe_pct"])

# Mağaza puanı ve yazılı yorum ortalaması, ülke bazında
write("store_country.csv", [
    {**r, "country_tr": COUNTRY_TR[r["country"]], "row_id": f'{r["game"]}|{r["country"]}'}
    for r in S.get("store_country", [])
], ["row_id", "game", "country", "country_tr", "store_rating", "rating_count", "written_avg"])

# Ağrı matrisi (uzun format)
write("pain.csv", [
    {"game": g, "category": c, "category_tr": CAT_TR[c], "pct": p}
    for g, cats in S["pain"].items() for c, p in cats.items()
], ["game", "category", "category_tr", "pct"])

# Ülke bazında puan
write("country_rating.csv", [
    {"game": g, "country": c, "country_tr": COUNTRY_TR[c], "avg_rating": r}
    for g, cs in S["country_rating"].items() for c, r in cs.items()
], ["game", "country", "country_tr", "avg_rating"])

d = S["deep"]
rm, tb, cbj, wtg = d["royal_match"], d["toon_blast"], d["color_block_jam"], d["word_tiles_go"]

# Royal Match: ülkeye göre reklamla uyuşmazlık payı
write("rm_misleading_country.csv", [
    {"country": c, "country_tr": COUNTRY_TR[c], "pct": p} for c, p in rm["misleading_by_country"].items()
], ["country", "country_tr", "pct"])

# Color Block Jam: çeyrek bazında olumsuz yorum payı
write("cbj_quarter.csv", [
    {"quarter": q, "neg_pct": p} for q, p in cbj["neg_by_quarter"].items()
], ["quarter", "neg_pct"])

# Word Tiles GO: ana sürüme göre "oyun ortasında reklam" anılma oranı
write("wtg_major.csv", [
    {"major": f"{m}.x", "midgame_pct": p, "reviews": wtg["n_by_major"][m]}
    for m, p in wtg["midgame_by_major"].items()
], ["major", "midgame_pct", "reviews"])

# Metin içindeki tekil sayılar (her biri analyze.py'deki bir hesaba karşılık gelir)
v = S["validation"] or {}
facts = [
    ("n_reviews", S["meta"]["n_reviews"], "Analiz edilen yorum"),
    ("store_date", S["meta"].get("store_fetched_at"), "Mağaza puanlarının çekildiği tarih"),
    ("date_max", S["meta"]["date_max"], "Son yorum tarihi"),
    ("parse_ok", S["meta"]["parse_ok"], "Model çıktısı ayrıştırma başarısı (%)"),
    ("rm_ml_pct", rm["misleading_pct"], "Royal Match: reklamla uyuşmazlık şikâyeti (% tüm yorumlar)"),
    ("rm_ml_30", rm["misleading_pct_last30"], "Royal Match: reklamla uyuşmazlık, son 30 gün (%)"),
    ("others_ml_max", rm["misleading_others_max"], "Diğer 3 oyunda en yüksek reklamla uyuşmazlık payı (%)"),
    ("rm_ml_rating", rm["misleading_avg_rating"], "Royal Match: reklamla uyuşmazlık yorumlarının ort. puanı"),
    ("rm_ml_level", rm["misleading_level_median"], "Reklamla uyuşmazlık yorumlarında anılan medyan seviye"),
    ("rm_ml_level_n", rm["misleading_level_n"], "Seviye belirten reklamla uyuşmazlık yorumu sayısı"),
    ("rm_diff_level", rm["difficulty_level_median"], "Royal Match: zorluk şikâyetinde medyan seviye"),
    ("rm_diff_level_n", rm["difficulty_level_n"], "Royal Match: seviye belirten zorluk yorumu sayısı"),
    ("tb_diff_level", tb["difficulty_level_median"], "Toon Blast: zorluk şikâyetinde medyan seviye"),
    ("tb_diff_level_n", tb["difficulty_level_n"], "Toon Blast: seviye belirten zorluk yorumu sayısı"),
    ("tb_veteran", tb["veteran_pct_of_neg"], "Toon Blast: olumsuz yorumlarda 'yıllardır oynuyorum' payı (%)"),
    ("rm_veteran", tb["veteran_pct_of_neg_rm"], "Royal Match: olumsuz yorumlarda 'yıllardır oynuyorum' payı (%)"),
    ("tb_diffmon", tb["diff_and_mon_pct"], "Toon Blast: zorluk + monetizasyon birlikte (%)"),
    ("rm_diffmon", tb["diff_and_mon_pct_rm"], "Royal Match: zorluk + monetizasyon birlikte (%)"),
    ("cbj_timer", cbj["timer_pct_of_neg"], "Color Block Jam: olumsuz yorumlarda süre/zamanlayıcı anılma payı (%)"),
    ("cbj_timer_churn", cbj["timer_churn_pct"], "Color Block Jam: süreden şikâyet edenlerde bırakma sinyali (%)"),
    ("cbj_notimer_churn", cbj["no_timer_churn_pct"], "Color Block Jam: diğerlerinde bırakma sinyali (%)"),
    ("cbj_timer_mislabel", cbj["timer_labelled_bug_or_ux_pct"], "Süre yorumlarının bug/UX diye etiketlenme payı (%)"),
    ("cbj_diff_level", cbj["difficulty_level_median"], "Color Block Jam: zorluk şikâyetinde medyan seviye"),
    ("wtg_ads", wtg["ads_pct"], "Word Tiles GO: reklam şikâyeti (% tüm yorumlar)"),
    ("wtg_ads_45", wtg["ads_pct_in_4_5_star"], "Word Tiles GO: 4-5 yıldızlı yorumlarda reklam anılma payı (%)"),
    ("wtg_mid", wtg["midgame_pct_of_ads"], "Word Tiles GO: reklam şikâyetlerinde 'oyun ortası' payı (%)"),
    ("val_n", v.get("n"), "Doğrulama örneklemi (yorum)"),
    ("val_sent", v.get("sentiment_pct"), "Duygu doğruluğu (%)"),
    ("val_topic", v.get("main_topic_pct"), "Ana konu doğruluğu (%)"),
    ("val_exact", v.get("exact_categories_pct"), "Tam kategori seti doğruluğu (%)"),
]
write("facts.csv", [{"fact_id": k, "value": val, "label": lab} for k, val, lab in facts],
      ["fact_id", "value", "label"])
