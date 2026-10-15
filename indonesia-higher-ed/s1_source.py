"""Stage 1: list every institution (name, city, province) from the Kemdiktisaintek portal."""
import csv
from collections import Counter

import config as C
from common import download, gate, read_xlsx, write_rows


def main():
    rows = read_xlsx(download(C.PT_URL, "src_perguruan_tinggi.xlsx"), C.PT_COLS)
    with open(C.CITY_RESEARCH, newline="", encoding="utf-8") as f:
        research = {r["npsn"]: r for r in csv.DictReader(f)}
    for r in rows:
        r["city_source"] = "official"
        if r["city_raw"].lower() in C.PLACEHOLDER_CITIES:
            found = research.get(r["npsn"], {})
            r["city_raw"] = found.get("city", "")
            r["province_raw"] = found.get("province") or r["province_raw"]
            r["city_source"] = f"research ({found.get('confidence', 'none')}): {found.get('evidence', '')}"
    write_rows("s1_institutions.csv", rows, [*C.PT_COLS, "city_source"])
    n = len(rows)
    diff = (n - C.OFFICIAL_TOTAL) / C.OFFICIAL_TOTAL
    blank = [r["name"] or r["npsn"] for r in rows if not r["city_raw"]]
    repeated = [k for k, v in Counter(r["npsn"] for r in rows).items() if v > 1]
    gate(1, [
        (f"rows within {C.COUNT_TOLERANCE:.0%} of {C.OFFICIAL_TOTAL_LABEL}", abs(diff) <= C.COUNT_TOLERANCE,
         f"{n} rows from {C.PT_URL}, diff {diff:+.2%}; vs 4,621 homepage: {(n - 4621) / 4621:+.2%}"),
        ("no blank city (placeholders like 'Lainnya' count as blank)", not blank,
         f"{len(blank)} blank: {blank[:20]}; {sum(r['city_source'] != 'official' for r in rows)} cities from {C.CITY_RESEARCH.name}"),
        ("no blank name or province", all(r["name"] and r["province_raw"] for r in rows), ""),
        ("NPSN codes unique (join key for Stage 2)", not repeated, f"repeated: {repeated[:20]}"),
    ])


if __name__ == "__main__":
    main()
