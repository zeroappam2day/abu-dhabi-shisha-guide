"""Z4: compare independent spot-check (work/spot_out_*.csv) with swim_v2/safety_v2; write spotcheck_v2.csv and gate."""
import zone_config as Z
from zone_common import baseline_ok, gate, merge_outs, read_csv, write_csv

BAND = {"Low": 0, "Medium": 1, "High": 2}
swim = {(r["city"], r["province"]): r["swim_v2"] for r in read_csv(Z.SWIM_V2)}
safe = {(r["city"], r["province"]): r["safety_v2"] for r in read_csv(Z.SAFETY_V2)}
sample = [tuple(l.split(" | ")) for l in (Z.WORK / "spot_in.txt").read_text(encoding="utf-8").splitlines() if l]
spot = merge_outs("spot_out_*.csv")
rows = []
for k in sample:
    s = spot[k]
    a, b = safe[k], s["safety"]
    both = a in BAND and b in BAND
    rows.append({"city": k[0], "province": k[1], "swim_v2": swim[k], "swim_spot": s["swim"],
                 "swim_agree": "yes" if swim[k] == s["swim"] else "no",
                 "safety_v2": a, "safety_spot": b, "both_rated": "yes" if both else "no",
                 "safety_within_one": ("yes" if abs(BAND[a] - BAND[b]) <= 1 else "no") if both else "n/a",
                 "swim_evidence_spot": s["swim_evidence"], "safety_evidence_spot": s["safety_evidence"]})
write_csv(Z.SPOT_V2, list(rows[0]), rows)
agree = sum(r["swim_agree"] == "yes" for r in rows)
both = [r for r in rows if r["both_rated"] == "yes"]
bad_s = [r["city"] for r in both if r["safety_within_one"] == "no"]
ok, msg = baseline_ok()
gate("z4", [
    ("sample", len(rows) == Z.SPOT_SIZE and set(spot) == set(sample), f"{len(rows)} seed {Z.SPOT_SEED}"),
    (f"swim agree >= {Z.SPOT_SWIM_MIN_AGREE}/{Z.SPOT_SIZE}", agree >= Z.SPOT_SWIM_MIN_AGREE,
     f"{agree}/20; disagree={[(r['city'], r['swim_v2'], r['swim_spot']) for r in rows if r['swim_agree'] == 'no']}"),
    ("safety within one band where both rated", not bad_s, f"{len(both)} both rated; exact {sum(r['safety_v2'] == r['safety_spot'] for r in both)}; bad={bad_s}"),
    ("info: safety coverage mismatch", True, [(r["city"], r["safety_v2"][:9], r["safety_spot"][:9]) for r in rows if r["both_rated"] == "no" and r["safety_v2"] != r["safety_spot"]]),
    ("baseline intact", ok, msg),
])
