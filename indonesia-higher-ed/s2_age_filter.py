"""Stage 2: keep institutions with at least one S1, D3 or D4 program (Kemdiktisaintek program list)."""
from collections import defaultdict

import config as C
from common import download, gate, norm_level, read_rows, read_xlsx, write_rows


def classify(levels):
    if not levels:
        return "no-data"
    if levels & C.KEEP_LEVELS:
        return "keep"
    return "postgrad-only" if levels <= C.POSTGRAD_LEVELS else "non-degree"


def main():
    rows = read_rows("s1_institutions.csv")
    levels = defaultdict(set)
    for p in read_xlsx(download(C.PRODI_URL, "src_program_studi.xlsx"), C.PRODI_COLS):
        levels[p["npsn"]].add(norm_level(p["level"]))
    for r in rows:
        lv = levels.get(r["npsn"], set())
        r["levels"], r["age_class"] = " ".join(sorted(lv)), classify(lv)

    write_rows("s2_all_classified.csv", rows, list(rows[0]))
    kept = [r for r in rows if r["age_class"] == "keep"]
    write_rows("s2_institutions.csv", kept, list(rows[0]))
    by = {c: [r["name"] for r in rows if r["age_class"] == c] for c in ("postgrad-only", "non-degree", "no-data")}
    gate(2, [
        ("zero postgraduate-only remain", not any(r["age_class"] == "postgrad-only" for r in kept),
         f"dropped {len(by['postgrad-only'])}: {by['postgrad-only'][:20]}"),
        ("zero non-degree remain", not any(r["age_class"] == "non-degree" for r in kept),
         f"dropped {len(by['non-degree'])}: {by['non-degree'][:20]}"),
        ("every institution classified from program data (none unknown)", not by["no-data"],
         f"{len(by['no-data'])} with no programs: {by['no-data'][:20]}"),
        ("kept count", True, f"{len(kept)} of {len(rows)}"),
    ])


if __name__ == "__main__":
    main()
