"""Shared helpers: gates, stage I/O, name normalization, HTTP clients."""
import csv
import json
import os
import re
import sys
import time

import config as C


def gate(stage, checks):
    """checks: list of (description, passed, detail). Writes a report; exits 1 on any failure."""
    C.DATA.mkdir(exist_ok=True)
    lines = [f"{'PASS' if ok else 'FAIL'}  {desc}  [{detail}]" for desc, ok, detail in checks]
    report = f"Stage {stage} gate\n" + "\n".join(lines) + "\n"
    (C.DATA / f"gate_s{stage}.txt").write_text(report, encoding="utf-8")
    print(report)
    if not all(ok for _, ok, _ in checks):
        sys.exit(f"Stage {stage} gate FAILED. Stop: report the FAIL lines above and decide before continuing.")


def write_rows(name, rows, fields):
    C.DATA.mkdir(exist_ok=True)
    with open(C.DATA / name, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def read_rows(name):
    path = C.DATA / name
    if not path.exists():
        sys.exit(f"{path} missing: run the previous stage first.")
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


class JsonlCache:
    """Append-only key -> JSON cache so long fetches resume after an interruption."""

    def __init__(self, name):
        C.DATA.mkdir(exist_ok=True)
        self.path = C.DATA / name
        self.data = {}
        if self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                rec = json.loads(line)
                self.data[rec["k"]] = rec["v"]

    def __contains__(self, k):
        return k in self.data

    def __getitem__(self, k):
        return self.data[k]

    def put(self, k, v):
        self.data[k] = v
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"k": k, "v": v}, ensure_ascii=False) + "\n")


def squash(s):
    return re.sub(r"\s+", " ", (s or "").strip())


def norm_level(raw):
    key = re.sub(r"[^A-Z0-9]", "", (raw or "").upper())
    return C.LEVEL_ALIASES.get(key, key)


def clean_city(raw):
    s = squash(raw)
    for pattern, repl in C.CITY_PREFIXES:
        if re.match(pattern, s, flags=re.I):
            s = re.sub(pattern, repl, s, count=1, flags=re.I)
            break
    head, _, rest = s.partition(" ")
    if head in ("Kota", "Kabupaten"):
        s = f"{head} {rest.title()}"
    else:
        s = s.title()
    return C.CITY_ALIASES.get(s, s)


def clean_province(raw):
    s = squash(raw)
    for pattern, repl in C.PROVINCE_PREFIXES:
        s = re.sub(pattern, repl, s, count=1, flags=re.I)
    return C.PROVINCE_ALIASES.get(s.lower(), s.title())


def match_key(name):
    """Comparison key for city names across PDDikti and OSM spellings."""
    s = clean_city(name).lower()
    s = re.sub(r"^kabupaten ", "kab ", s)
    return re.sub(r"[^a-z0-9 ]", "", s).strip()


def pddikti_client():
    from pddiktipy import api
    cookie, ua = os.environ.get(C.ENV_CF_CLEARANCE), os.environ.get(C.ENV_USER_AGENT)
    if cookie and ua:
        return api(cf_clearance=cookie, user_agent=ua)
    return api(auto_cookie=True)


def pddikti_get(client, path):
    """Raw GET that raises on any failure (pddiktipy's wrappers swallow errors into None)."""
    time.sleep(C.REQUEST_PAUSE_S)
    try:
        return client.H.response(f"{client.api_link}/{path}")
    except Exception as e:
        sys.exit(f"PDDikti request failed for /{path}: {e}\n"
                 f"If this is a 403, refresh {C.ENV_CF_CLEARANCE} and {C.ENV_USER_AGENT} and re-run; "
                 "cached responses are kept.")


def overpass(query):
    import requests
    for attempt in range(5):
        time.sleep(C.OVERPASS_PAUSE_S * (2 ** attempt if attempt else 1))
        r = requests.post(C.OVERPASS_URL, data={"data": query}, timeout=300)
        if r.status_code == 200:
            return r.json()["elements"]
        if r.status_code not in (429, 502, 503, 504):
            break
    sys.exit(f"Overpass failed ({r.status_code}): {r.text[:300]}")
