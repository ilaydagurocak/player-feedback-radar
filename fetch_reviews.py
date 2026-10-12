"""App Store yorumlarını Apple'ın herkese açık RSS akışından çeker.

Kullanım:
    pip install requests
    python fetch_reviews.py

Çıktı: data/reviews.csv

Biriktirme modu: Apple akışı her ülke için yalnızca en son ~500 yorumu verir.
Script mevcut data/reviews.csv dosyasını okur, yeni yorumları EKLER, eskileri
silmez. Haftada bir çalıştırırsan veri seti zamanla büyür ve sürüm öncesi/sonrası
analiz mümkün olur. Her satırın "first_seen" alanı yorumun ilk kez çekildiği günü,
data/fetch_log.csv ise her çalıştırmanın özetini tutar.

KVKK notu: Kullanıcı adları (author) hiç kaydedilmez. Yorum kimliği yalnızca
tekrarları ayıklamak için tek yönlü hash'lenerek saklanır.
Ham veriyi GitHub'a yükleme (data/ klasörü .gitignore'da).
"""

import csv
import hashlib
import os
import time
from datetime import datetime, timezone

import requests

from apps import APPS, COUNTRIES

FEED_URL = (
    "https://itunes.apple.com/{country}/rss/customerreviews/"
    "page={page}/id={app_id}/sortby=mostrecent/json"
)
MAX_PAGES = 10          # Apple akışı en fazla ~10 sayfa (≈500 yorum) verir
SLEEP_SECONDS = 1.5     # nazik ol: istekler arasında bekle
OUT_PATH = os.path.join("data", "reviews.csv")
LOG_PATH = os.path.join("data", "fetch_log.csv")

FIELDS = ["review_hash", "app_key", "app_name", "company", "cluster", "country",
          "date", "rating", "version", "title", "text", "first_seen"]
LOG_FIELDS = ["fetched_at", "app_key", "country", "fetched", "new"]


def _label(entry, key):
    value = entry.get(key, {})
    return value.get("label", "") if isinstance(value, dict) else ""


def fetch_app_country(app, country):
    rows = []
    for page in range(1, MAX_PAGES + 1):
        url = FEED_URL.format(country=country, page=page, app_id=app["app_id"])
        try:
            resp = requests.get(url, timeout=20)
        except requests.RequestException as exc:
            print(f"  ! {country} sayfa {page}: bağlantı hatası ({exc})")
            break
        if resp.status_code != 200:
            print(f"  ! {country} sayfa {page}: HTTP {resp.status_code}")
            break

        entries = resp.json().get("feed", {}).get("entry", [])
        if isinstance(entries, dict):      # tek kayıt varsa liste değil sözlük döner
            entries = [entries]
        reviews = [e for e in entries if "im:rating" in e]
        if not reviews:
            break

        for e in reviews:
            raw_id = _label(e, "id")
            rows.append({
                "review_hash": hashlib.sha256(raw_id.encode()).hexdigest()[:16],
                "app_key": app["key"],
                "app_name": app["name"],
                "company": app["company"],
                "cluster": app["cluster"],
                "country": country,
                "date": _label(e, "updated"),
                "rating": _label(e, "im:rating"),
                "version": _label(e, "im:version"),
                "title": _label(e, "title"),
                "text": _label(e, "content"),
            })
        time.sleep(SLEEP_SECONDS)
    return rows


def load_existing():
    """Önceki çalıştırmalardan kalan yorumları okur (yoksa boş liste)."""
    if not os.path.exists(OUT_PATH):
        return []
    with open(OUT_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:  # eski formatta first_seen yoksa boş bırak
        r.setdefault("first_seen", "")
    return rows


def main():
    os.makedirs("data", exist_ok=True)
    now = datetime.now(timezone.utc)
    today = now.date().isoformat()

    all_rows = load_existing()
    seen = {r["review_hash"] for r in all_rows}
    print(f"Mevcut veri: {len(all_rows)} yorum\n")

    log_rows = []
    for app in APPS:
        for country in COUNTRIES:
            rows = fetch_app_country(app, country)
            new = [r for r in rows if r["review_hash"] not in seen]
            for r in new:
                r["first_seen"] = today
            seen.update(r["review_hash"] for r in new)
            all_rows.extend(new)
            log_rows.append({"fetched_at": now.isoformat(timespec="seconds"),
                             "app_key": app["key"], "country": country,
                             "fetched": len(rows), "new": len(new)})
            print(f"{app['name']:<16} {country}: {len(rows):>3} çekildi, {len(new):>3} yeni")

    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(all_rows)

    write_header = not os.path.exists(LOG_PATH)
    with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LOG_FIELDS)
        if write_header:
            writer.writeheader()
        writer.writerows(log_rows)

    total_new = sum(r["new"] for r in log_rows)
    print(f"\n{total_new} yeni yorum eklendi. Toplam {len(all_rows)} yorum -> {OUT_PATH}")


if __name__ == "__main__":
    main()
