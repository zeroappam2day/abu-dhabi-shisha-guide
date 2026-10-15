"""Stage 1: list every institution (name, city, province) from PDDikti."""
from collections import Counter

import config as C
from common import JsonlCache, gate, pddikti_client, pddikti_get, squash, write_rows

ID_KEYS = ("id_sp", "id", "id_pt")


def first_list(obj):
    """The first list of dicts inside a response, whatever the wrapper."""
    if isinstance(obj, list) and (not obj or isinstance(obj[0], dict)):
        return obj
    if isinstance(obj, dict):
        for v in obj.values():
            found = first_list(v)
            if found is not None:
                return found
    return None


def unwrap(obj):
    if isinstance(obj, dict) and "data" in obj and isinstance(obj["data"], (dict, list)):
        obj = obj["data"]
    return obj[0] if isinstance(obj, list) and obj else obj


def list_ids(client):
    pages, ids, offset = JsonlCache("cache_pt_pages.jsonl"), [], 0
    while True:
        key = str(offset)
        if key not in pages:
            pages.put(key, pddikti_get(client, f"v2/pt/search/filter?limit={C.LIST_PAGE_SIZE}&offset={offset}"))
        items = first_list(pages[key]) or []
        if not items:
            return ids
        id_key = next((k for k in ID_KEYS if k in items[0]), None)
        if id_key is None:
            raise SystemExit(f"No id field in list response; keys seen: {sorted(items[0])}")
        new = [it[id_key] for it in items]
        if offset and new[0] in ids:
            raise SystemExit("List endpoint ignores offset (page repeated); cannot enumerate.")
        ids += new
        offset += C.LIST_PAGE_SIZE
        print(f"listed {len(ids)}", end="\r")


def main():
    client = pddikti_client()
    count = unwrap(pddikti_get(client, "pt/count"))
    live_total = count.get("jumlah") if isinstance(count, dict) else count

    details, rows = JsonlCache("cache_pt_detail.jsonl"), []
    ids = list_ids(client)
    for i, pt_id in enumerate(ids, 1):
        if pt_id not in details:
            details.put(pt_id, unwrap(pddikti_get(client, f"pt/detail/{client.H.parse(pt_id)}")))
            print(f"detail {i}/{len(ids)}", end="\r")
        d = details[pt_id] or {}
        rows.append({
            "pt_id": pt_id, "kode_pt": squash(d.get("kode_pt")), "name": squash(d.get("nama_pt")),
            "city_raw": squash(d.get("kab_kota_pt")), "province_raw": squash(d.get("provinsi_pt")),
            "status": squash(d.get("status_pt")),
        })

    statuses = Counter(r["status"].lower() for r in rows)
    kept = [r for r in rows if r["status"].lower() in C.KEEP_PT_STATUS]
    write_rows("s1_institutions.csv", kept, list(kept[0]) if kept else ["pt_id"])
    n, blank = len(kept), [r["name"] or r["pt_id"] for r in kept if not r["city_raw"]]
    diff = abs(n - C.OFFICIAL_TOTAL) / C.OFFICIAL_TOTAL
    gate(1, [
        (f"rows within {C.COUNT_TOLERANCE:.0%} of {C.OFFICIAL_TOTAL_LABEL}", diff <= C.COUNT_TOLERANCE,
         f"listed {len(rows)}, status counts {dict(statuses)}, kept {n} with status in {sorted(C.KEEP_PT_STATUS)}, "
         f"diff {diff:.2%}, live /pt/count = {live_total}"),
        ("no blank city", not blank, f"{len(blank)} blank: {blank[:20]}"),
        ("no blank name", all(r["name"] for r in kept), ""),
    ])


if __name__ == "__main__":
    main()
