"""Stage 2: classify every institution by the levels it offers (Kemdiktisaintek program list); filter only if AGE_FILTER."""
from collections import defaultdict

import config as C
from common import download, gate, norm_level, read_rows, read_xlsx, write_rows


def classify(levels):
    if not levels:
        return "no-data"
    if levels & C.KEEP_LEVELS:
        return "keep"
    return "postgrad-only" if levels <= C.POSTGRAD_LEVELS else "non-degree"


def typical_age(levels):
    under = next((band for lvl, band in C.AGE_BANDS if lvl in levels), "")
    post = C.POSTGRAD_AGE if levels & C.POSTGRAD_LEVELS else ""
    return "; ".join(x for x in (under, f"{post} (postgraduate)" if post and under else post) if x)


def main():
    rows = read_rows("s1_institutions.csv")
    levels = defaultdict(set)
    for p in read_xlsx(download(C.PRODI_URL, "src_program_studi.xlsx"), C.PRODI_COLS):
        levels[p["npsn"]].add(norm_level(p["level"]))
    for r in rows:
        lv = levels.get(r["npsn"], set())
        r["levels"], r["age_class"] = " ".join(sorted(lv)), classify(lv)
        r["offers_undergrad"] = "yes" if lv & C.KEEP_LEVELS else "no"
        r["typical_age"] = typical_age(lv)

    write_rows("s2_all_classified.csv", rows, list(rows[0]))
    kept = [r for r in rows if r["age_class"] == "keep" or not C.AGE_FILTER]
    write_rows("s2_institutions.csv", kept, list(rows[0]))
    by = {c: [r["name"] for r in rows if r["age_class"] == c] for c in ("postgrad-only", "non-degree", "no-data")}
    gate(2, [
        ("age rule applied as configured", C.AGE_FILTER or len(kept) == len(rows),
         f"AGE_FILTER={C.AGE_FILTER}; postgrad-only {len(by['postgrad-only'])}, non-degree {len(by['non-degree'])} "
         f"({'dropped' if C.AGE_FILTER else 'kept, flagged Offers S1/D3/D4 = no'})"),
        ("every row has a typical age", all(r["typical_age"] for r in kept), ""),
        ("every institution classified from program data (none unknown)", not by["no-data"],
         f"{len(by['no-data'])} with no programs: {by['no-data'][:20]}"),
        ("kept count", True, f"{len(kept)} of {len(rows)}"),
    ])


if __name__ == "__main__":
    main()
