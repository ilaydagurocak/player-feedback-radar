"""Etiketli yorumlardan bulguları hesaplar ve dashboard için data/summary.json üretir.

Kullanım:
    python analyze.py                       # varsayılan: data/labels_v0.4.csv
    python analyze.py data/labels_v0.5.csv  # başka bir etiket sürümü

Tüm sayılar bu script'ten gelir; dashboard ve rapordaki her rakam buradan izlenebilir.
"""

import json
import re
import sys

import numpy as np
import pandas as pd

LABELS = sys.argv[1] if len(sys.argv) > 1 else "data/labels_v0.4.csv"
GAMES = ["Royal Match", "Toon Blast", "Word Tiles GO", "Color Block Jam"]
CATS = ["difficulty", "monetization", "ads", "rewarded_ads", "misleading_ads",
        "lives_energy", "bug_performance", "content", "events", "social_pvp",
        "ux_ui", "feature_request", "praise"]

# Anahtar kelime işaretleri (model etiketlerinden bağımsız ikinci bir kontrol)
KW = {
    "timer": r"timer|time limit|süre|zeitlich|zeitdruck|zeitlimit|seconds|saniye|minute|dakika|clock",
    "midgame_ad": r"middle|mid game|mid-game|midgame|during (?:a |the )?(?:game|match|round)|in game|interrupt",
    "veteran": r"for years|years now|\d+ years|seit jahren|jahrelang|yıllardır|\d+ yıl|since (?:the )?(?:start|beginning)|used to love|früher",
    "save_the_king": r"save the king|saving the king|rescu\w* the king|kralı kurtar|kral\w* kurtar|könig rett",
}
LEVEL_RE = re.compile(r"(?:level|lvl|seviye|bölüm|bolum|stufe|niveau)\s*#?\s*(\d[\d,\.]*\s*k?)", re.I)


def level_of(text):
    m = LEVEL_RE.search(str(text))
    if not m:
        return np.nan
    s = m.group(1).replace(",", "").replace(".", "").strip().lower()
    try:
        return float(s[:-1].strip()) * 1000 if s.endswith("k") else float(s)
    except ValueError:
        return np.nan


def pct(x):
    return round(float(x) * 100, 1)


def main():
    reviews = pd.read_csv("data/reviews.csv")
    labels = pd.read_csv(LABELS)
    df = reviews.merge(labels, on="review_hash", how="inner")
    df["date"] = pd.to_datetime(df["date"], utc=True)
    df["cats"] = df["categories"].fillna("").str.split("|")
    for c in CATS:
        df[c] = df["cats"].apply(lambda xs, c=c: c in xs)
    df["neg"] = df["sentiment"].eq("neg")
    low = df["text"].fillna("").str.lower()
    for k, p in KW.items():
        df[k] = low.str.contains(p, regex=True)
    df["level"] = df["text"].apply(level_of)

    last = df["date"].max()
    cut30 = last - pd.Timedelta(days=30)
    out = {"meta": {
        "labels_file": LABELS,
        "model": str(labels["model"].iloc[0]),
        "n_reviews": int(len(df)),
        "date_min": str(df["date"].min().date()),
        "date_max": str(last.date()),
        "parse_ok": pct(labels["parse_ok"].mean()),
    }}

    # 1) Oyun başına KPI'lar
    games = {}
    for g in GAMES:
        s = df[df.app_name == g]
        games[g] = {
            "company": s["company"].iloc[0],
            "n": int(len(s)),
            "avg_rating": round(float(s["rating"].mean()), 2),
            "neg_pct": pct(s["neg"].mean()),
            "churn_pct": pct(s["churn_signal"].mean()),
            "severe_pct": pct((s["severity"] == 3).mean()),
            "countries": {c: int(n) for c, n in s.groupby("country").size().items()},
            "date_min": str(s["date"].min().date()),
        }
    # 1b) Mağaza puanı (yıldız-only değerlendirmeler dahil) — fetch_store_ratings.py çıktısı
    try:
        st = pd.read_csv("data/store_ratings.csv")
        st = st[st["fetched_at"] == st["fetched_at"].max()]
        out["meta"]["store_fetched_at"] = str(st["fetched_at"].iloc[0])[:10]
        store_country = []
        for g in GAMES:
            s = st[st["app_name"] == g]
            if s.empty:
                continue
            # 4 ülkenin puan sayısına göre ağırlıklı ortalaması
            w = (s["store_rating"] * s["rating_count"]).sum() / s["rating_count"].sum()
            games[g]["store_rating"] = round(float(w), 2)
            games[g]["store_count"] = int(s["rating_count"].sum())
            games[g]["gap"] = round(float(w) - games[g]["avg_rating"], 2)
            written = df[df.app_name == g].groupby("country")["rating"].agg(["mean", "size"])
            for _, r in s.iterrows():
                if r["country"] in written.index and written.loc[r["country"], "size"] >= 30:
                    store_country.append({
                        "game": g, "country": r["country"],
                        "store_rating": round(float(r["store_rating"]), 2),
                        "rating_count": int(r["rating_count"]),
                        "written_avg": round(float(written.loc[r["country"], "mean"]), 2),
                    })
        out["store_country"] = store_country
    except FileNotFoundError:
        out["store_country"] = []
    out["games"] = games

    # 2) Ağrı matrisi: kategori içeren OLUMSUZ yorumların tüm yorumlara oranı (%)
    pain, pain30 = {}, {}
    for g in GAMES:
        s = df[df.app_name == g]
        s30 = s[s["date"] >= cut30]
        pain[g] = {c: pct((s[c] & s["neg"]).mean()) for c in CATS if c != "praise"}
        pain30[g] = {c: pct((s30[c] & s30["neg"]).mean()) if len(s30) else None
                     for c in CATS if c != "praise"}
        pain30[g]["_n"] = int(len(s30))
    out["pain"] = pain
    out["pain_last30"] = pain30

    # 3) Kategoriye göre oyunu bırakma sinyali (tüm oyunlar)
    base = df["churn_signal"].mean()
    out["churn_by_cat"] = sorted(
        [{"cat": c, "n": int(df[c].sum()), "churn_pct": pct(df.loc[df[c], "churn_signal"].mean()),
          "lift": round(float(df.loc[df[c], "churn_signal"].mean() / base), 2)}
         for c in CATS if df[c].sum() >= 40],
        key=lambda r: -r["churn_pct"])
    out["churn_base_pct"] = pct(base)

    # 4) Oyuna özel derin bulgular
    rm = df[df.app_name == "Royal Match"]
    tb = df[df.app_name == "Toon Blast"]
    cbj = df[df.app_name == "Color Block Jam"]
    wtg = df[df.app_name == "Word Tiles GO"]
    others_ml = {g: pain[g]["misleading_ads"] for g in GAMES if g != "Royal Match"}
    rm_ml = rm[rm["misleading_ads"]]
    out["deep"] = {
        "royal_match": {
            "misleading_pct": pain["Royal Match"]["misleading_ads"],
            "misleading_pct_last30": pain30["Royal Match"]["misleading_ads"],
            "misleading_others_max": max(others_ml.values()),
            "misleading_by_country": {c: pct(v) for c, v in rm.groupby("country")["misleading_ads"].mean().items()},
            "misleading_avg_rating": round(float(rm_ml["rating"].mean()), 2),
            "misleading_mentions_save_king_pct": pct(rm_ml["save_the_king"].mean()),
            "misleading_level_median": float(rm_ml["level"].median()),
            "misleading_level_n": int(rm_ml["level"].notna().sum()),
            "difficulty_level_median": float(rm[rm["difficulty"]]["level"].median()),
            "difficulty_level_n": int(rm[rm["difficulty"]]["level"].notna().sum()),
        },
        "toon_blast": {
            "difficulty_level_median": float(tb[tb["difficulty"]]["level"].median()),
            "difficulty_level_n": int(tb[tb["difficulty"]]["level"].notna().sum()),
            "veteran_pct_of_neg": pct(tb[tb["neg"]]["veteran"].mean()),
            "veteran_pct_of_neg_rm": pct(rm[rm["neg"]]["veteran"].mean()),
            "diff_and_mon_pct": pct((tb["difficulty"] & tb["monetization"]).mean()),
            "diff_and_mon_pct_rm": pct((rm["difficulty"] & rm["monetization"]).mean()),
        },
        "color_block_jam": {
            "timer_pct_of_neg": pct(cbj[cbj["neg"]]["timer"].mean()),
            "timer_churn_pct": pct(cbj[cbj["timer"]]["churn_signal"].mean()),
            "no_timer_churn_pct": pct(cbj[~cbj["timer"]]["churn_signal"].mean()),
            "timer_labelled_bug_or_ux_pct": pct((cbj[cbj["timer"]]["bug_performance"] | cbj[cbj["timer"]]["ux_ui"]).mean()),
            "difficulty_level_median": float(cbj[cbj["difficulty"]]["level"].median()),
            "difficulty_level_n": int(cbj[cbj["difficulty"]]["level"].notna().sum()),
            "neg_by_quarter": {str(k): pct(v) for k, v in
                               cbj.groupby(cbj["date"].dt.tz_localize(None).dt.to_period("Q"))["neg"].mean().items()
                               if (cbj["date"].dt.tz_localize(None).dt.to_period("Q") == k).sum() >= 30},
        },
        "word_tiles_go": {
            "ads_pct": pain["Word Tiles GO"]["ads"],
            "ads_pct_in_4_5_star": pct(wtg[wtg["rating"] >= 4]["ads"].mean()),
            "midgame_pct_of_ads": pct(wtg[wtg["ads"]]["midgame_ad"].mean()),
            "midgame_by_major": {k: pct(v) for k, v in
                                 wtg.assign(major=wtg["version"].astype(str).str.split(".").str[0])
                                 .query("major != '0'").groupby("major")["midgame_ad"].mean().items()},
            "n_by_major": {k: int(v) for k, v in
                           wtg.assign(major=wtg["version"].astype(str).str.split(".").str[0])
                           .query("major != '0'").groupby("major").size().items()},
        },
    }

    # 5) Ülke farkları (ortalama puan)
    out["country_rating"] = {g: {c: round(float(v), 2) for c, v in df[df.app_name == g].groupby("country")["rating"].mean().items()
                                 if (df[(df.app_name == g)]["country"] == c).sum() >= 30}
                             for g in GAMES}

    # 6) Doğrulama
    try:
        v = pd.read_csv("data/validation_v0.4.csv")
        out["validation"] = {"n": int(len(v)),
                             "exact_categories_pct": pct((v["category_judgement"] == "correct").mean()),
                             "main_topic_pct": pct(v["main_topic_correct"].mean()),
                             "sentiment_pct": pct(v["sentiment_correct"].mean())}
    except FileNotFoundError:
        out["validation"] = None

    with open("data/summary.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps(out["deep"], ensure_ascii=False, indent=1))
    print("validation:", out["validation"])
    print("-> data/summary.json")


if __name__ == "__main__":
    main()
