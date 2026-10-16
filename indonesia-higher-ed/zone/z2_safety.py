"""Z2: merge safety agent outputs with carried-forward ratings into safety_v2.csv (70 rows) and gate."""
import re
from collections import Counter

import zone_config as Z
from zone_common import baseline_ok, gate, merge_outs, read_csv, urls, write_csv

import sys
sys.path.insert(0, str(Z.ROOT))
import config as C  # read-only import, for SAFETY_VALUES

lo, hi = Z.SAFETY_WINDOW


def dated_in_window(ev):
    return [d for d in re.findall(r"\((\d{4}-\d{2}(?:-\d{2})?)", ev) if lo[:len(d)] <= d <= hi[:len(d)]]


base = read_csv(Z.ZONE_LIST)
got = merge_outs("safety_out_*.csv")
retry = {k: r for k, r in merge_outs("safety_retry_out_*.csv").items() if r["safety_v2"] in ("High", "Medium", "Low")}
got.update(retry)
out = []
for b in base:
    k = (b["City/Regency"], b["Province"])
    old = b["Safety (walking around)"]
    if k in got:
        r = got[k]
        val, ev, src = r["safety_v2"], r["evidence"], "researched (zone)"
        if k in Z.SAFETY_OVERRIDES and k not in retry:
            val, why = Z.SAFETY_OVERRIDES[k]
            ev = f"UNVERIFIED (reviewer: {why}): {ev}"
    else:
        val, ev, src = old, b["Safety evidence"], "baseline (carried)"
    out.append({"city": k[0], "province": k[1], "safety_v2": val, "evidence": ev, "source": src,
                "n_dated": len(dated_in_window(ev)), "changed": "yes" if val != old else "no", "baseline": old})
write_csv(Z.SAFETY_V2, ["city", "province", "safety_v2", "evidence", "source", "n_dated", "changed", "baseline"], out)

new_rated = [r for r in out if r["source"].startswith("researched") and r["safety_v2"] in ("High", "Medium", "Low")]
weak_new = [r["city"] for r in new_rated if r["n_dated"] < Z.SAFETY_MIN_SOURCES or len(set(urls(r["evidence"]))) < 2]
carried = [r for r in out if r["source"].startswith("baseline") and r["safety_v2"] in ("High", "Medium", "Low")]
weak_carried = [r["city"] for r in carried if r["n_dated"] < Z.SAFETY_MIN_SOURCES]
todo = [b for b in base if b["Safety (walking around)"] in (C.NOT_RESEARCHED, C.NO_SAFETY_RATING)]
ok, msg = baseline_ok()
gate("z2", [
    ("rows", len(out) == Z.EXPECTED_ROWS, f"{len(out)}"),
    ("researched set = 47 gaps", set(got) == {(b['City/Regency'], b['Province']) for b in todo}, f"{len(got)} vs {len(todo)}"),
    ("values in SAFETY_VALUES", all(r["safety_v2"] in C.SAFETY_VALUES for r in out), dict(Counter(r["safety_v2"] for r in out))),
    (">=2 dated in-window URLs per new rating", not weak_new, f"{len(new_rated)} new ratings; weak={weak_new}"),
    ("info: carried ratings with <2 machine-readable dates", True, f"{len(weak_carried)}/{len(carried)}: {weak_carried}"),
    ("baseline intact", ok, msg),
])
