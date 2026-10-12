"""App Store mağaza puanlarını (yıldız ortalaması ve puan sayısı) Apple'ın herkese açık
arama servisinden çeker.

Kullanım:
    python fetch_store_ratings.py

Çıktı: data/store_ratings.csv (her çalıştırma yeni satırlar EKLER; tarih damgalıdır)

Not: Mağaza puanı, yorum yazmadan verilen yıldızları da içerir. Bu yüzden yazılı
yorumların ortalamasından genellikle belirgin şekilde yüksektir.
"""

import csv
import os
import time
from datetime import datetime, timezone

import requests

from apps import APPS, COUNTRIES

LOOKUP_URL = "https://itunes.apple.com/lookup"
OUT_PATH = os.path.join("data", "store_ratings.csv")
FIELDS = ["fetched_at", "app_key", "app_name", "country", "store_rating", "rating_count",
          "current_version_rating", "current_version_count", "version", "version_date"]


def parse(result):
    """Apple'ın lookup cevabındaki ilk sonuçtan ilgili alanları alır."""
    return {
        "store_rating": result.get("averageUserRating"),
        "rating_count": result.get("userRatingCount"),
        "current_version_rating": result.get("averageUserRatingForCurrentVersion"),
        "current_version_count": result.get("userRatingCountForCurrentVersion"),
        "version": result.get("version"),
        "version_date": (result.get("currentVersionReleaseDate") or "")[:10],
    }


def main():
    os.makedirs("data", exist_ok=True)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows = []
    for app in APPS:
        for country in COUNTRIES:
            try:
                resp = requests.get(LOOKUP_URL, params={"id": app["app_id"], "country": country}, timeout=20)
                results = resp.json().get("results", []) if resp.status_code == 200 else []
            except (requests.RequestException, ValueError) as exc:
                print(f"  ! {app['name']} {country}: {exc}")
                results = []
            if not results:
                print(f"{app['name']:<16} {country}: sonuç yok")
                continue
            row = {"fetched_at": now, "app_key": app["key"], "app_name": app["name"],
                   "country": country, **parse(results[0])}
            rows.append(row)
            r, n = row["store_rating"], row["rating_count"]
            print(f"{app['name']:<16} {country}: {r if r is not None else '-':>5} yıldız, "
                  f"{n if n is not None else '-':>10} puan")
            time.sleep(0.5)

    write_header = not os.path.exists(OUT_PATH)
    with open(OUT_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if write_header:
            writer.writeheader()
        writer.writerows(rows)
    print(f"\n{len(rows)} satır -> {OUT_PATH}")


if __name__ == "__main__":
    main()
