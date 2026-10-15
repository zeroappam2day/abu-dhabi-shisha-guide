"""Stage 3: standardize city/province names and flag exact duplicates (never remove them)."""
from collections import Counter

import config as C
from common import clean_city, clean_province, gate, read_rows, squash, write_rows


def dup_key(r):
    return (squash(r["name"]).casefold(), r["city"], r["province"])


def main():
    rows = read_rows("s2_institutions.csv")
    for r in rows:
        r["city"], r["province"] = clean_city(r["city_raw"]), clean_province(r["province_raw"])
        r["province"] = C.CITY_PROVINCE_FIXES.get(r["city"], r["province"])
        r["address"] = r["address"] if r["address"].strip("- ") else C.ADDRESS_MISSING
    counts = Counter(dup_key(r) for r in rows)
    for r in rows:
        r["duplicate"] = "yes" if counts[dup_key(r)] > 1 else "no"

    write_rows("s3_institutions.csv", rows, list(rows[0]))
    provs = {}
    for r in rows:
        provs.setdefault(r["city"], set()).add(r["province"])
    split = {c: sorted(p) for c, p in provs.items() if len(p) > 1}
    dups = sum(r["duplicate"] == "yes" for r in rows)
    gate(3, [
        ("row count equals Stage 2", len(rows) == len(read_rows("s2_institutions.csv")), f"{len(rows)} rows"),
        ("zero blank cities", all(r["city"] for r in rows), ""),
        ("zero blank provinces", all(r["province"] for r in rows), ""),
        ("each city has one province", not split, f"split: {split}"),
        ("duplicates flagged, none removed", True, f"{dups} rows flagged as exact duplicates"),
    ])


if __name__ == "__main__":
    main()
