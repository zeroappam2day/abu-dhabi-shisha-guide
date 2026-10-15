"""Z1: merge swim agent outputs into swim_v2.csv (70 rows) and gate."""
from collections import Counter

import zone_config as Z
from zone_common import baseline_ok, gate, merge_outs, read_csv, urls, write_csv

base = read_csv(Z.ZONE_LIST)
got = merge_outs("swim_out_*.csv")
out = []
for b in base:
    k = (b["City/Regency"], b["Province"])
    r = got.get(k, {"swim_v2": "Unverified", "beach_name": "-", "evidence": "UNVERIFIED: no agent row", "checked": "none"})
    out.append({"city": k[0], "province": k[1], "swim_v2": r["swim_v2"], "beach_name": r["beach_name"],
                "evidence": r["evidence"], "checked": r["checked"],
                "changed": "yes" if r["swim_v2"] != b["Swimmable sand beach"] else "no",
                "baseline": b["Swimmable sand beach"]})
write_csv(Z.SWIM_V2, ["city", "province", "swim_v2", "beach_name", "evidence", "checked", "changed", "baseline"], out)

decided = [r for r in out if r["swim_v2"] in ("Yes", "No")]
bad = [r["city"] for r in decided if r["checked"] != "opened" or not urls(r["evidence"]) or r["evidence"].startswith("UNVERIFIED")]
ok, msg = baseline_ok()
gate("z1", [
    ("rows", len(out) == Z.EXPECTED_ROWS and len(got) == Z.EXPECTED_ROWS, f"{len(out)} out, {len(got)} agent rows"),
    ("agent keys match", set(got) == {(b['City/Regency'], b['Province']) for b in base}, f"extra={set(got)-{(b['City/Regency'], b['Province']) for b in base}}"),
    ("values valid", all(r["swim_v2"] in {"Yes", "No", "Unverified"} and r["checked"] in Z.CHECKED_VALUES for r in out), ""),
    ("every Yes/No has opened URL", not bad, f"{len(decided)} decided; bad={bad[:5]}"),
    ("counts", True, f"v2 {dict(Counter(r['swim_v2'] for r in out))}; changed {sum(r['changed']=='yes' for r in out)}"),
    ("baseline intact", ok, msg),
])
