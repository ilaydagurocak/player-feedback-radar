"""Verinin genel resmini çıkarır: oyun başına yorum sayısı, puanlar, ülke farkları.

Kullanım:
    pip install pandas
    python explore.py
"""

import pandas as pd

df = pd.read_csv("data/reviews.csv")
df["date"] = pd.to_datetime(df["date"], utc=True, errors="coerce")
df["words"] = df["text"].fillna("").str.split().str.len()

print("=== Oyun bazında özet ===")
summary = df.groupby("app_name").agg(
    yorum=("rating", "size"),
    ort_puan=("rating", "mean"),
    olumsuz_oran=("rating", lambda s: (s <= 2).mean()),
    medyan_kelime=("words", "median"),
)
print(summary.round(2).to_string())

print("\n=== Ülke bazında ortalama puan ===")
print(df.pivot_table(index="app_name", columns="country",
                     values="rating", aggfunc="mean").round(2).to_string())

print("\n=== Puan dağılımı (yorum sayısı) ===")
print(df.pivot_table(index="app_name", columns="rating", values="review_hash",
                     aggfunc="count", fill_value=0).to_string())

print("\n=== Zaman kapsamı (oyun x ülke) ===")
cov = df.groupby(["app_name", "country"])["date"].agg(["min", "max", "count"])
cov["min"], cov["max"] = cov["min"].dt.date, cov["max"].dt.date
print(cov.to_string())

cut = df["date"].max() - pd.Timedelta(days=90)
recent = df[df["date"] >= cut]
print("\n=== Son 90 gün ===")
print(recent.groupby("app_name").agg(
    yorum=("rating", "size"),
    ort_puan=("rating", "mean"),
    olumsuz_oran=("rating", lambda s: (s <= 2).mean()),
).round(2).to_string())
