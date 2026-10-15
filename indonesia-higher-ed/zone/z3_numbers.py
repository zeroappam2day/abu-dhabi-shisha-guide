"""Z3: merge numeric agent output into numbers_v2.csv, flag out-of-range poverty, gate."""
import zone_config as Z
from zone_common import baseline_ok, gate, read_csv, urls, write_csv

rows = read_csv(Z.WORK / "numbers_out.csv")
inp = [l.split(" | ") for l in (Z.WORK / "numbers_in.txt").read_text(encoding="utf-8").splitlines() if l]
for r in rows:
    r["flag"] = ""
    if r["metric"] == "poverty" and r["verified"] == "yes":
        v, new = float(r["baseline"].split()[0]), float(r["value_v2"])
        if not (v <= new < v + 1):
            r["flag"] = f"out of range: baseline {v} vs new {new}; not applied"
    r["apply"] = "yes" if r["verified"] == "yes" and not r["flag"] else "no"
write_csv(Z.NUMBERS_V2, ["metric", "city", "province", "baseline", "value_v2", "period", "evidence", "verified", "flag", "apply"], rows)

keys_in = [(m, c, p) for m, c, p, *_ in inp]
keys_out = [(r["metric"], r["city"], r["province"]) for r in rows]
no_url = [r["city"] for r in rows if r["verified"] == "yes" and (not urls(r["evidence"]) or r["evidence"].startswith("UNVERIFIED"))]
ok, msg = baseline_ok()
gate("z3", [
    ("rows = input lines, keys exact", keys_in == keys_out, f"{len(rows)} vs {len(inp)}"),
    ("every new number has URL", not no_url, f"bad={no_url}"),
    ("poverty range check", True, f"flagged={[r['city'] for r in rows if r['flag']]}"),
    ("applied", True, f"{sum(r['apply']=='yes' for r in rows)}/{len(rows)}"),
    ("baseline intact", ok, msg),
])
