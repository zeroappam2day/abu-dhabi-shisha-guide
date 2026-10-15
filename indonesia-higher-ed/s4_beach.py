"""Stage 4: per unique city, flag a named sea beach (OSM natural=beach) inside its boundary.

Works offline on the OSM Indonesia extract (Overpass is not required).
Beach = named natural=beach, or a named "Pantai ..." tourism attraction/viewpoint/picnic site/beach resort.
Confirmation rule: the beach is named, lies within COASTLINE_MAX_M of natural=coastline
(sea, not lake/river) and its surface is not in EXCLUDED_SURFACES.
Coastal cities with no OSM beach are decided by web verdicts (BEACH_WEB_FILE), because OSM has gaps there.
Spot-check: SPOTCHECK_SIZE seeded-random cities compared with web-verified verdicts (SPOTCHECK_FILE,
one evidence URL per city). GeoNames (99 beach points) and Wikidata (214) were too sparse to serve.
"""
import csv
import json
import random

import config as C
from common import city_type, clean_province, download, gate, match_key, read_rows, write_rows

FEATURES = "osm_features.jsonl"


def extract(pbf):
    """One pass over the extract: admin areas (level 4/5), named beaches, coastline ways -> FEATURES."""
    import osmium
    wkb = osmium.geom.WKBFactory()
    levels = {C.OSM_ADMIN_LEVEL_PROVINCE, C.OSM_ADMIN_LEVEL_CITY}
    fp = (osmium.FileProcessor(str(pbf)).with_locations("sparse_mem_array")
          .with_areas(osmium.filter.TagFilter(("boundary", "administrative"), ("natural", "beach")))
          .with_filter(osmium.filter.TagFilter(("boundary", "administrative"), ("natural", "beach"),
                                               ("natural", "coastline"),
                                               *(("tourism", v) for v in C.BEACH_TOURISM_VALUES),
                                               *(("leisure", v) for v in C.BEACH_LEISURE_VALUES))))
    tmp = C.DATA / (FEATURES + ".part")
    with open(tmp, "w", encoding="utf-8") as out:
        for obj in fp:
            tags = {t.k: t.v for t in obj.tags}
            try:
                if obj.is_area() and tags.get("boundary") == "administrative" and tags.get("admin_level") in levels:
                    rec = {"kind": "admin", "id": obj.orig_id(), "tags": tags, "wkb": wkb.create_multipolygon(obj)}
                elif is_beach(tags):
                    if obj.is_area():
                        geom, osm = wkb.create_multipolygon(obj), ("way" if obj.from_way() else "relation", obj.orig_id())
                    elif obj.is_node():
                        geom, osm = wkb.create_point(obj), ("node", obj.id)
                    else:
                        continue  # the way itself; its area version is handled above
                    rec = {"kind": "beach", "osm": osm, "tags": tags, "wkb": geom}
                elif obj.is_way() and tags.get("natural") == "coastline":
                    rec = {"kind": "coast", "wkb": wkb.create_linestring(obj)}
                else:
                    continue
            except (RuntimeError, osmium.InvalidLocationError):  # broken geometry in OSM: skip, counted in the gate detail
                rec = {"kind": "broken", "tags": tags}
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
        for rec in rebuild_open_boundaries(pbf):
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
    tmp.replace(C.DATA / FEATURES)


def rebuild_open_boundaries(pbf):
    """Approximate polygons for OSM_OPEN_BOUNDARIES: polygonize the member ways, else a concave hull of them."""
    import osmium
    import shapely
    from shapely.geometry import LineString
    rels = {r.id: (dict(r.tags), [m.ref for m in r.members if m.type == "w"])
            for r in osmium.FileProcessor(str(pbf), osmium.osm.RELATION) if r.id in C.OSM_OPEN_BOUNDARIES}
    wanted = {w for _, ways in rels.values() for w in ways}
    fp = (osmium.FileProcessor(str(pbf), osmium.osm.NODE | osmium.osm.WAY).with_locations("sparse_mem_array")
          .with_filter(osmium.filter.EntityFilter(osmium.osm.WAY)).with_filter(osmium.filter.IdFilter(wanted)))
    lines = {w.id: LineString([(n.lon, n.lat) for n in w.nodes if n.location.valid()]) for w in fp}
    for rid, (tags, ways) in rels.items():
        mls = shapely.MultiLineString([lines[w] for w in ways if w in lines and len(lines[w].coords) > 1])
        poly = shapely.union_all(list(shapely.polygonize(list(shapely.unary_union(mls).geoms)).geoms))
        if poly.is_empty:
            poly = shapely.concave_hull(mls, ratio=C.OPEN_BOUNDARY_HULL_RATIO)
        yield {"kind": "admin", "id": rid, "tags": {**tags, "admin_level": C.OSM_OPEN_BOUNDARIES[rid]},
               "approx": True, "wkb": shapely.to_wkb(poly, hex=True)}


def is_beach(tags):
    """Named natural=beach, or a named 'Pantai ...' tourist attraction / viewpoint / picnic site / beach resort."""
    name = tags.get("name", "")
    return bool(name) and (tags.get("natural") == "beach" or (name.lower().startswith(C.BEACH_NAME_PREFIX) and (
        tags.get("tourism") in C.BEACH_TOURISM_VALUES or tags.get("leisure") in C.BEACH_LEISURE_VALUES)))


def load_features():
    import shapely
    path = C.DATA / FEATURES
    if not path.exists():
        extract(download(C.OSM_PBF_URL, "src_indonesia.osm.pbf"))
    feats = {"admin": [], "beach": [], "coast": [], "broken": []}
    for line in path.read_text(encoding="utf-8").splitlines():
        rec = json.loads(line)
        if "wkb" in rec:
            rec["geom"] = shapely.from_wkb(rec.pop("wkb"))
        feats[rec["kind"]].append(rec)
    return feats


def city_areas(admin):
    """[(relation id, match keys, province, polygon, kota/kab type)] for every kabupaten/kota boundary."""
    from shapely import STRtree
    provs = [a for a in admin if a["tags"]["admin_level"] == C.OSM_ADMIN_LEVEL_PROVINCE]
    tree = STRtree([p["geom"] for p in provs])
    out = []
    for a in admin:
        if a["tags"]["admin_level"] != C.OSM_ADMIN_LEVEL_CITY:
            continue
        pt = a["geom"].representative_point()
        hit = [provs[i] for i in tree.query(pt, predicate="within")]
        province = clean_province(hit[0]["tags"].get("name:id") or hit[0]["tags"].get("name", "")) if hit else ""
        names = [n for t in C.OSM_NAME_TAGS for n in a["tags"].get(t, "").split(";") if n.strip()]
        kind = next((city_type(n) for n in [a["tags"].get("official_name", "")] + names if city_type(n)), "")
        out.append((a["id"], {match_key(n) for n in names}, province, a["geom"], kind, a.get("approx", False)))
    return out


def match_area(city, province, areas):
    """Unique boundary for a city: bare-name match, then province, then Kota/Kabupaten type as tiebreaks."""
    override = C.OSM_RELATION_OVERRIDES.get(f"{city}|{province}")
    kind = city_type(city)
    hits = [a for a in areas if (a[0] == override if override else match_key(city) in a[1])
            and not (override is None and a[4] and kind and a[4] != kind)]  # never Kota X <-> Kabupaten X
    if len({a[0] for a in hits}) > 1:
        hits = [a for a in hits if a[2] == province] or hits
    if len({a[0] for a in hits}) > 1:
        hits = [a for a in hits if a[4] == kind] or [a for a in hits if not a[4]]
    return hits[0] if len({a[0] for a in hits}) == 1 else None


def sea_beaches(feats):
    from shapely import STRtree
    coast = STRtree([c["geom"] for c in feats["coast"]])
    reach = C.COASTLINE_MAX_M / C.METERS_PER_DEGREE
    return [b for b in feats["beach"]
            if b["tags"].get("surface", "").lower() not in C.EXCLUDED_SURFACES
            and len(coast.query(b["geom"], predicate="dwithin", distance=reach))]


def read_csv(path):
    if not path.exists():
        return {}
    with open(path, newline="", encoding="utf-8") as f:
        return {(r["city"], r["province"]): r for r in csv.DictReader(f)}


def url_of(evidence):
    return next((t for t in reversed(evidence.split()) if t.startswith("http")), "")


def spot_check(cities):
    """Compare a seeded-random sample with web-verified verdicts recorded in SPOTCHECK_FILE."""
    sample = random.Random(C.SPOTCHECK_SEED).sample(cities, min(C.SPOTCHECK_SIZE, len(cities)))
    web = read_csv(C.SPOTCHECK_FILE)
    for c in sample:
        w = web.get((c["city"], c["province"]), {})
        c.update(web_beach=w.get("web_beach", ""), web_evidence=w.get("evidence", ""),
                 agree="" if not w else ("yes" if w["web_beach"] == c["beach"] else "no"))
    write_rows("s4_spotcheck.csv", sample, list(sample[0]))
    return sample


def main():
    from shapely import STRtree
    rows, feats = read_rows("s3_institutions.csv"), load_features()
    areas = city_areas(feats["admin"])
    beaches = sea_beaches(feats)
    coast = STRtree([c["geom"] for c in feats["coast"]])
    beach_web = read_csv(C.BEACH_WEB_FILE)
    btree = STRtree([b["geom"].representative_point() for b in beaches])
    pairs = sorted({(r["city"], r["province"]) for r in rows})
    cities, unmatched = [], []
    for city, province in pairs:
        if city == C.UNKNOWN_CITY:  # user decision: kept, but no boundary to test
            cities.append({"city": city, "province": province, "osm_relation": "", "beach": "unknown",
                           "beach_names": "", "beach_source": "", "coastal": "", "basis": "no city known",
                           "boundary_note": ""})
            continue
        area = match_area(city, province, areas)
        if area is None:
            unmatched.append(f"{city}|{province}")
            continue
        inside = sorted((beaches[i] for i in btree.query(area[3], predicate="contains")),
                        key=lambda b: b["tags"]["name"])
        coastal = len(coast.query(area[3], predicate="intersects")) > 0
        row = {
            "city": city, "province": province, "osm_relation": area[0], "coastal": "yes" if coastal else "no",
            "beach": "yes" if inside else "no",
            "beach_names": "; ".join(dict.fromkeys(b["tags"]["name"] for b in inside[:C.BEACH_NAMES_LISTED])),
            "beach_source": f"https://www.openstreetmap.org/{inside[0]['osm'][0]}/{inside[0]['osm'][1]}" if inside else "",
            "basis": "osm" if inside else ("osm: no sea coast" if not coastal else "unverified coastal"),
            "boundary_note": "approximate: OSM ring not closed, outline rebuilt" if area[5] else "",
        }
        w = beach_web.get((city, province))
        if not inside and coastal and w and w.get("verified") == "yes":  # OSM has coastal gaps: web decides
            row.update(beach=w["web_beach"], beach_names=w.get("beach_name", ""),
                       beach_source=url_of(w["evidence"]), basis=f"web: {w['evidence']}")
        cities.append(row)

    write_rows("s4_cities.csv", cities, ["city", "province", "osm_relation", "coastal", "beach", "beach_names",
                                         "beach_source", "basis", "boundary_note"])
    stats = (f"{len(areas)} OSM city boundaries, {len(feats['beach'])} named beaches, {len(beaches)} confirmed sea, "
             f"{len(feats['coast'])} coastline ways, {len(feats['broken'])} broken geometries skipped")
    if unmatched:  # no spot-check on an incomplete set
        gate(4, [("100% of cities classified", False,
                  f"{len(unmatched)} of {len(pairs)} unmatched to an OSM boundary "
                  f"(add to CITY_ALIASES or OSM_RELATION_OVERRIDES): {unmatched}; {stats}")])
    unverified = [f"{c['city']}|{c['province']}" for c in cities if c["basis"] == "unverified coastal"]
    yes_missing = [c["city"] for c in cities if c["beach"] == "yes" and not (c["beach_names"] and c["beach_source"])]
    sample = spot_check([c for c in cities if c["osm_relation"]])
    agree = sum(c["agree"] == "yes" for c in sample)
    todo = [f"{c['city']}|{c['province']}" for c in sample if not c["agree"]]
    gate(4, [
        ("100% of cities classified", True,
         f"{len(cities)} cities, {sum(c['beach'] == 'yes' for c in cities)} yes, "
         f"{sum(c['beach'] == 'unknown' for c in cities)} unknown (user-approved '{C.UNKNOWN_CITY}'); {stats}"),
        ("every yes lists a named beach and a source", not yes_missing, f"missing: {yes_missing}"),
        (f"every coastal city without an OSM beach has a web verdict in {C.BEACH_WEB_FILE.name}", not unverified,
         f"{len(unverified)} unverified: {unverified[:30]}; "
         f"{sum(c['basis'].startswith('web') for c in cities)} decided by web"),
        (f"spot-check sample all verified in {C.SPOTCHECK_FILE.name}", not todo, f"not yet verified: {todo}"),
        (f"spot-check vs web: >= {C.SPOTCHECK_MIN_AGREE}/{len(sample)} agree", agree >= C.SPOTCHECK_MIN_AGREE,
         f"{agree} agree; disagreements: {[(c['city'], c['beach'], c['web_beach']) for c in sample if c['agree'] == 'no']}"),
    ])


if __name__ == "__main__":
    main()
