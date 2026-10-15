"""Stage 4: per unique city, flag a named sea beach (OSM natural=beach) inside its boundary.

Confirmation rule: the beach is named, lies within COASTLINE_MAX_M of natural=coastline
(sea, not lake/river) and its surface is not in EXCLUDED_SURFACES.
Spot-check: SPOTCHECK_SIZE seeded-random cities re-classified from GeoNames (BCH/BCHS points
inside the same OSM boundary polygon), an independent gazetteer.
"""
import csv
import io
import json
import random
import zipfile

import config as C
from common import JsonlCache, clean_province, gate, match_key, overpass, read_rows, write_rows

ADMIN_QUERY = f"""[out:json][timeout:900];
area["ISO3166-1"="ID"]["admin_level"="2"]->.id;
rel(area.id)["boundary"="administrative"]["admin_level"="{C.OSM_ADMIN_LEVEL_PROVINCE}"]->.provs;
foreach.provs->.p(
  .p out tags;
  .p map_to_area->.pa;
  rel(area.pa)["boundary"="administrative"]["admin_level"="{C.OSM_ADMIN_LEVEL_CITY}"];
  out tags;
);"""

BEACH_QUERY = """[out:json][timeout:300];
area(id:{area})->.a;
nwr["natural"="beach"]["name"](area.a)->.b;
way["natural"="coastline"](around.b:{m})->.c;
nwr.b(around.c:{m});
out tags center;"""


def osm_cities():
    """[(relation id, set of match keys, province)] for every kabupaten/kota relation."""
    path = C.DATA / "osm_admin.json"
    if not path.exists():
        path.write_text(json.dumps(overpass(ADMIN_QUERY)), encoding="utf-8")
    out, province = [], ""
    for el in json.loads(path.read_text(encoding="utf-8")):
        tags = el.get("tags", {})
        if tags.get("admin_level") == C.OSM_ADMIN_LEVEL_PROVINCE:
            province = clean_province(tags.get("name:id") or tags.get("name", ""))
            continue
        names = {n for t in C.OSM_NAME_TAGS for n in tags.get(t, "").split(";") if n.strip()}
        out.append((el["id"], {match_key(n) for n in names}, province))
    return out


def match_relation(city, province, osm):
    override = C.OSM_RELATION_OVERRIDES.get(f"{city}|{province}")
    if override:
        return override
    hits = [(rid, prov) for rid, keys, prov in osm if match_key(city) in keys]
    ids = {rid for rid, _ in hits}
    if len(ids) > 1:
        ids = {rid for rid, prov in hits if prov == province}
    return ids.pop() if len(ids) == 1 else None


def sea_beaches(rel_id, cache):
    key = str(rel_id)
    if key not in cache:
        cache.put(key, overpass(BEACH_QUERY.format(area=3600000000 + int(rel_id), m=C.COASTLINE_MAX_M)))
    good = [e for e in cache[key] if e.get("tags", {}).get("surface", "").lower() not in C.EXCLUDED_SURFACES]
    return sorted(good, key=lambda e: e["tags"]["name"])


def boundary_polygon(rel_id):
    from shapely.geometry import LineString
    from shapely.ops import polygonize, unary_union
    rel = overpass(f"[out:json][timeout:300];rel({rel_id});out geom;")[0]
    rings = {"outer": [], "inner": []}
    for m in rel["members"]:
        if m["type"] == "way" and m.get("geometry"):
            line = LineString([(p["lon"], p["lat"]) for p in m["geometry"]])
            rings["inner" if m.get("role") == "inner" else "outer"].append(line)
    poly = unary_union(list(polygonize(unary_union(rings["outer"]))))
    if rings["inner"]:
        poly = poly.difference(unary_union(list(polygonize(unary_union(rings["inner"])))))
    return poly


def geonames_beaches():
    import requests
    path = C.DATA / "geonames_ID.zip"
    if not path.exists():
        r = requests.get(C.GEONAMES_URL, timeout=300)
        r.raise_for_status()
        path.write_bytes(r.content)
    with zipfile.ZipFile(path) as z, z.open("ID.txt") as f:
        rows = csv.reader(io.TextIOWrapper(f, encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE)
        return [(row[1], float(row[5]), float(row[4])) for row in rows if row[7] in C.GEONAMES_BEACH_CODES]


def spot_check(cities):
    from shapely.geometry import Point
    from shapely.prepared import prep
    points = geonames_beaches()
    sample = random.Random(C.SPOTCHECK_SEED).sample(cities, min(C.SPOTCHECK_SIZE, len(cities)))
    for c in sample:
        poly = prep(boundary_polygon(c["osm_relation"]))
        names = sorted({n for n, lon, lat in points if poly.contains(Point(lon, lat))})
        c2 = "yes" if names else "no"
        c.update(geonames_beach=c2, geonames_names="; ".join(names[:C.BEACH_NAMES_LISTED]),
                 agree="yes" if c2 == c["beach"] else "no")
    write_rows("s4_spotcheck.csv", sample, list(sample[0]))
    return sample


def main():
    rows, osm, cache = read_rows("s3_institutions.csv"), osm_cities(), JsonlCache("cache_beach.jsonl")
    pairs = sorted({(r["city"], r["province"]) for r in rows})
    cities, unmatched = [], []
    for i, (city, province) in enumerate(pairs, 1):
        rel = match_relation(city, province, osm)
        if rel is None:
            unmatched.append(f"{city}|{province}")
            continue
        beaches = sea_beaches(rel, cache)
        cities.append({
            "city": city, "province": province, "osm_relation": rel,
            "beach": "yes" if beaches else "no",
            "beach_names": "; ".join(b["tags"]["name"] for b in beaches[:C.BEACH_NAMES_LISTED]),
            "beach_source": f"https://www.openstreetmap.org/{beaches[0]['type']}/{beaches[0]['id']}" if beaches else "",
        })
        print(f"city {i}/{len(pairs)}", end="\r")

    write_rows("s4_cities.csv", cities, ["city", "province", "osm_relation", "beach", "beach_names", "beach_source"])
    if unmatched:  # no spot-check on an incomplete set
        gate(4, [("100% of cities classified", False,
                  f"{len(unmatched)} of {len(pairs)} unmatched to an OSM boundary "
                  f"(add to CITY_ALIASES or OSM_RELATION_OVERRIDES): {unmatched}")])
    yes_missing = [c["city"] for c in cities if c["beach"] == "yes" and not (c["beach_names"] and c["beach_source"])]
    sample = spot_check(cities)
    agree = sum(c["agree"] == "yes" for c in sample)
    gate(4, [
        ("100% of cities classified", True,
         f"{len(cities)} cities, {sum(c['beach'] == 'yes' for c in cities)} yes"),
        ("every yes lists a named beach and a source", not yes_missing, f"missing: {yes_missing}"),
        (f"spot-check vs GeoNames: >= {C.SPOTCHECK_MIN_AGREE}/{len(sample)} agree", agree >= C.SPOTCHECK_MIN_AGREE,
         f"{agree} agree; disagreements: {[(c['city'], c['beach'], c['geonames_beach']) for c in sample if c['agree'] == 'no']}"),
    ])


if __name__ == "__main__":
    main()
