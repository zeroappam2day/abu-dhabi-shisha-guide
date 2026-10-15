"""Shared helpers: baseline check, gate writer, zone-list loader."""
import csv
import subprocess
import sys

import zone_config as Z


def baseline_ok():
    r = subprocess.run(["sha256sum", "-c", "--quiet", str(Z.BASELINE)], cwd=Z.ROOT.parent,
                       capture_output=True, text=True)
    return r.returncode == 0, (r.stdout + r.stderr).strip()[:300] or "148 files match"


def gate(stage, checks):
    lines = [f"{'PASS' if ok else 'FAIL'}  {name}  [{detail}]" for name, ok, detail in checks]
    (Z.ZONE / f"gate_{stage}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    if not all(ok for _, ok, _ in checks):
        sys.exit(1)


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def zone_keys():
    return [(r["City/Regency"], r["Province"]) for r in read_csv(Z.ZONE_LIST)]


def merge_outs(pattern, keyed=True):
    """Concatenate agent output CSVs work/<pattern>; return rows keyed by (city, province)."""
    rows = []
    for p in sorted(Z.WORK.glob(pattern)):
        rows += read_csv(p)
    return {(r["city"], r["province"]): r for r in rows} if keyed else rows


def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=header, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def urls(text):
    import re
    return re.findall(r"https?://[^\s;)\"]+", text or "")
