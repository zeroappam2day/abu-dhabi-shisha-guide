"""Beach shortlist: one row per beach city/regency with safety, wage, unemployment and poverty (evidence-backed)."""
import csv

import config as C

COLS = ["City/Regency", "Province", "Institution count", "Offering S1/D3/D4", "Safety (walking around)",
        "Safety evidence", "UMK 2026 (IDR/month)", "UMK basis", "Average net wage (IDR/month, all ages)",
        "Unemployment rate % (all ages)", "Unemployment period", "Poverty rate %", "Poverty period", "Sources",
        "Notes", "Swimmable sand beach", "Swim beach evidence"]


def _read(path):
    if not path.exists():
        return {}
    with open(path, newline="", encoding="utf-8") as f:
        return {(r["city"], r["province"]): r for r in csv.DictReader(f)}


def _val(value, src):
    """A value counts only if it has a real source URL."""
    return value if value and src.startswith("http") else ""


def build(counts, under, beach):
    """Return (rows, problems). Missing evidence is labelled, never invented."""
    num, saf, swim = _read(C.SHORTLIST_NUMERIC_FILE), _read(C.SHORTLIST_SAFETY_FILE), _read(C.SHORTLIST_SWIM_FILE)
    rows, problems = [], {"no numeric row": []}
    for (city, prov), n in sorted(counts.items()):
        if beach.get((city, prov)) != "yes":
            continue
        m, s = num.get((city, prov)), saf.get((city, prov))
        if m is None:
            problems["no numeric row"].append(city)
            m = {}
        if s is None:  # outside the researched 60 (user decision)
            s = {"safety": C.NOT_RESEARCHED, "evidence": C.NOT_RESEARCHED}
        umk = _val(m.get("umk_2026_idr", ""), m.get("umk_src", ""))
        wage = _val(m.get("avg_wage_idr", ""), m.get("avg_wage_src", ""))
        tpt = _val(m.get("unemployment_pct", ""), m.get("unemployment_src", ""))
        p0 = _val(m.get("poverty_pct", ""), m.get("poverty_src", ""))
        notes = m.get("notes", "")
        w = swim.get((city, prov))
        if w is None:  # not yet researched
            swim_val = swim_ev = C.NOT_RESEARCHED
        else:
            sourced = "http" in w["evidence"] and not w["evidence"].startswith("UNVERIFIED")
            swim_val = C.SWIM_LABELS.get(w["swim_sand_beach"], C.UNVERIFIED) if sourced else C.UNVERIFIED
            swim_ev = f'{w["beach_name"]}: {w["evidence"]}' if w["beach_name"] not in ("", "-") else w["evidence"]
        srcs = "; ".join(dict.fromkeys(u for u in (m.get("poverty_src", ""), m.get("unemployment_src", ""),
                                                     m.get("umk_src", ""), m.get("avg_wage_src", ""))
                                       if u.startswith("http")))
        rows.append([
            city, prov, n, under[(city, prov)],
            s.get("safety") or C.UNVERIFIED, s.get("evidence") or C.UNVERIFIED,
            int(float(umk)) if umk else C.UNVERIFIED,
            "UMP (no regency UMK)" if "UMP" in notes else ("UMK" if umk else C.UNVERIFIED),
            int(float(wage)) if wage else C.NOT_AT_REGENCY,
            float(tpt) if tpt else C.UNVERIFIED, m.get("unemployment_period") or C.UNVERIFIED,
            float(p0) if p0 else C.UNVERIFIED, m.get("poverty_period") or C.UNVERIFIED,
            srcs or C.UNVERIFIED, notes or "-", swim_val, swim_ev or C.UNVERIFIED,
        ])
    return rows, problems
