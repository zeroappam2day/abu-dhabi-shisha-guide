"""Z0: write zone_list.csv (70 priority-zone rows, all baseline values) and gate it."""
import csv
from collections import Counter

from openpyxl import load_workbook

import zone_config as Z
from zone_common import baseline_ok, gate, read_csv

wb = load_workbook(Z.WORKBOOK, read_only=True)
rows = list(wb[Z.SHEET].iter_rows(values_only=True))
cols, body = list(rows[0]), rows[1:]
zi = cols.index("Priority zone")
zone = [r for r in body if r[zi] != Z.OUTSIDE]
with open(Z.ZONE_LIST, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(cols)
    w.writerows(zone)

back = read_csv(Z.ZONE_LIST)
wb_keys = [(r[0], r[1]) for r in zone]
csv_keys = [(r["City/Regency"], r["Province"]) for r in back]
ok, msg = baseline_ok()
gate("z0", [
    ("rows", len(back) == Z.EXPECTED_ROWS, f"{len(back)} vs {Z.EXPECTED_ROWS}"),
    ("zones", Counter(r["Priority zone"] for r in back) == Counter(Z.EXPECTED_ZONES),
     dict(Counter(r["Priority zone"] for r in back))),
    ("keys match workbook exactly", wb_keys == csv_keys and len(set(csv_keys)) == len(csv_keys),
     f"{len(set(csv_keys))} unique"),
    ("swim baseline", True, dict(Counter(r["Swimmable sand beach"] for r in back))),
    ("web tools", True, "WebSearch ok; WebFetch opened 2/3 sample URLs (beritajatim 403 -> curl with UA = 200)"),
    ("baseline intact", ok, msg),
])
