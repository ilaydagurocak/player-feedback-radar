"""Analiz edilecek oyunlar ve ülkeler.

Yeni bir oyun eklemek için APPS listesine bir satır eklemen yeterli.
App Store ID'si, oyunun App Store linkindeki "id" sonrasındaki sayıdır.
"""

APPS = [
    # Küme 1: Match / blast puzzle (rakip analizi)
    {"key": "royal_match", "name": "Royal Match", "company": "Dream Games",
     "app_id": "1482155847", "cluster": "match_puzzle"},
    {"key": "toon_blast", "name": "Toon Blast", "company": "Peak",
     "app_id": "1176027022", "cluster": "match_puzzle"},

    # Küme 2: Kelime oyunları
    {"key": "word_tiles_go", "name": "Word Tiles GO", "company": "Gulliver's Games",
     "app_id": "6737275844", "cluster": "word"},
    # Benchmark rakip — ID'sini ekleyince açılır (ör. bir PvP kelime oyunu)
    # {"key": "benchmark_word", "name": "...", "company": "...", "app_id": "...", "cluster": "word"},

    # Küme 3: Casual / hybrid-casual
    {"key": "color_block_jam", "name": "Color Block Jam", "company": "Rollic",
     "app_id": "6504332779", "cluster": "casual"},
]

# Ülke karşılaştırması için App Store mağaza kodları
COUNTRIES = ["us", "gb", "de", "tr"]
