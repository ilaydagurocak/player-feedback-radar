"""dashboard_data/ içeriğinden tek dosyalık, çevrimdışı açılan dashboard.html üretir.

Kullanım:
    python analyze.py && python build_dashboard_data.py && python build_standalone.py
    open dashboard.html        # Windows: start dashboard.html

d3 kütüphanesi vendor/d3.min.js'ten sayfaya gömülür; internet gerekmez.
"""

import csv
import json
import os

SRC = "dashboard_data"
DATASETS = ["games", "pain", "country_rating", "rm_misleading_country",
            "cbj_quarter", "wtg_major", "facts"]

page = open(os.path.join(SRC, "index.html"), encoding="utf-8").read()
data = {n: list(csv.DictReader(open(os.path.join(SRC, f"{n}.csv"), encoding="utf-8")))
        for n in DATASETS}
d3 = open(os.path.join("vendor", "d3.min.js"), encoding="utf-8").read()

# Yayındaki dashboard'un sağladığı tema değişkenleri (açık ve koyu tema)
TOKENS = """
:root {
  --color-fg: #1f1e1d; --color-fg-muted: #6b6a66; --color-bg: #faf9f5; --color-panel: #ffffff;
  --color-border-line: #e5e3dc; --color-ok: #2f7d4f; --color-warn: #a86a12; --color-bad: #c0392b;
  --cds-chart-grid: #ecebe6; --cds-chart-axis: #c9c7bf; --cds-chart-muted: #b9b6ad;
  --cds-chart-status-critical: #c8553d; --cds-surface-popover: #ffffff; --cds-border: #e5e3dc;
  --cds-shadow-popover: 0 4px 16px rgba(0,0,0,.08); --cds-text-secondary: #6b6a66;
  --font-anthropic-sans: ui-sans-serif, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --font-anthropic-serif: ui-serif, Georgia, "Times New Roman", serif;
  --cds-font-size-caption: 12px; --cds-font-size-body: 14px; --cds-font-size-heading: 16px; --cds-font-size-title: 26px;
  --cds-font-weight-medium: 600;
  --cds-gap-xs: 4px; --cds-gap-sm: 8px; --cds-gap-md: 16px; --cds-gap-lg: 24px; --cds-gap-xl: 36px;
  --cds-pad-xs: 4px; --cds-pad-sm: 8px; --cds-pad-md: 12px; --cds-pad-lg: 20px;
  --cds-radius: 10px; --cds-dur-slow: .3s;
}
@media (prefers-color-scheme: dark) {
  :root {
    --color-fg: #ecebe6; --color-fg-muted: #a3a19a; --color-bg: #1c1b19; --color-panel: #252422;
    --color-border-line: #3a3935; --cds-chart-grid: #33322e; --cds-chart-axis: #55534d; --cds-chart-muted: #6f6c64;
    --cds-chart-status-critical: #e07a5f; --cds-surface-popover: #2c2b28; --cds-border: #3a3935;
    --cds-text-secondary: #a3a19a;
  }
}
html, body { margin: 0; background: var(--color-bg); color: var(--color-fg); }
#dash-root { padding: 28px 16px 48px; }
"""

# Yayındaki sayfanın kullandığı küçük "dash" arayüzünün çevrimdışı karşılığı
SHIM = """
window.dash = (function () {
  const DATA = %s;
  const subs = [];
  return {
    data(id) { return id in DATA ? {status: 'ok', data: DATA[id], columns: Object.keys(DATA[id][0] || {})}
                                 : {status: 'missing', data: []}; },
    onData(fn) { subs.push(fn); fn(); },
    setLink(name) { try { history.replaceState(null, '', '#' + name); } catch (e) {} },
    _redraw() { subs.forEach(f => f()); },
  };
})();
let _t; window.addEventListener('resize', () => { clearTimeout(_t); _t = setTimeout(() => dash._redraw(), 150); });
""" % json.dumps(data, ensure_ascii=False)

html = f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Player Feedback Radar</title>
<style>{TOKENS}</style>
<script>{d3}</script>
<script>{SHIM}</script>
</head>
<body>
<div id="dash-root">
{page}
</div>
</body>
</html>
"""
open("dashboard.html", "w", encoding="utf-8").write(html)
print(f"dashboard.html ({len(html.encode()) // 1024} KB)")
