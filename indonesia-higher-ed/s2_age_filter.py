"""Stage 2: keep institutions with at least one active S1, D3 or D4 program."""
import config as C
from common import JsonlCache, gate, norm_level, pddikti_client, pddikti_get, read_rows, squash, write_rows
from s1_source import first_list


def classify(levels):
    if not levels:
        return "no-data"
    if levels & C.KEEP_LEVELS:
        return "keep"
    return "postgrad-only" if levels <= C.POSTGRAD_LEVELS else "non-degree"


def active_levels(programs):
    return {norm_level(p.get("jenjang_prodi")) for p in programs
            if squash(p.get("status_prodi")).lower() in C.KEEP_PRODI_STATUS}


def main():
    rows, cache, client = read_rows("s1_institutions.csv"), JsonlCache("cache_prodi.jsonl"), None
    for i, r in enumerate(rows, 1):
        levels, used = set(), ""
        for sem in C.SEMESTERS:
            key = f"{r['pt_id']}|{sem}"
            if key not in cache:
                client = client or pddikti_client()
                cache.put(key, first_list(pddikti_get(client, f"pt/prodi/{client.H.parse(r['pt_id'])}/{sem}")) or [])
                print(f"prodi {i}/{len(rows)}", end="\r")
            levels, used = active_levels(cache[key]), sem
            if levels:
                break
        r["levels"], r["semester"], r["age_class"] = " ".join(sorted(levels)), used, classify(levels)

    write_rows("s2_all_classified.csv", rows, list(rows[0]))
    kept = [r for r in rows if r["age_class"] == "keep"]
    write_rows("s2_institutions.csv", kept, list(rows[0]))
    by = {c: [r["name"] for r in rows if r["age_class"] == c] for c in ("postgrad-only", "non-degree", "no-data")}
    print(f"kept {len(kept)} of {len(rows)}; dropped postgrad-only {len(by['postgrad-only'])}, "
          f"non-degree {len(by['non-degree'])}")
    gate(2, [
        ("zero postgraduate-only remain", not any(r["age_class"] == "postgrad-only" for r in kept), ""),
        ("zero non-degree remain", not any(r["age_class"] == "non-degree" for r in kept), ""),
        ("every institution classified from program data (none unknown)", not by["no-data"],
         f"{len(by['no-data'])} with no active programs in {C.SEMESTERS}: {by['no-data'][:20]}"),
    ])


if __name__ == "__main__":
    main()
