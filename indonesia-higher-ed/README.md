# Indonesia higher-education workbook

Builds `output/indonesia_higher_ed.xlsx` with two sheets:
- **Institutions:** name, city, province, beach, duplicate.
- **Summary:** city, province, institution count, beach.

It covers every institution with at least one S1, D3 or D4 program. Every stage ends with a gate. If a gate fails, the stage writes `data/gate_sN.txt` and exits, and the workbook is not produced.

## Sources and method
| Stage | Source / rule |
|---|---|
| 1 Institutions | Kemdiktisaintek open-data portal, "Perguruan Tinggi.xlsx" (`download/datasets/6`, 2025), 4,303 rows. 36 rows with city "Lainnya" (meaning "other") are resolved from `city_research.csv`, which records evidence and confidence for each. |
| 2 Age filter | "Program Studi.xlsx" (`download/datasets/5`), joined on NPSN. An institution is kept if it has any S1, D3 or D4 program. |
| 3 Clean | City and province prefixes are normalized. `CITY_ALIASES` maps typos and renamed regencies to current official names. Exact duplicates (same name, city and province) are flagged and never removed. |
| 4 Beach | The OpenStreetMap Indonesia extract supplies kabupaten/kota boundaries. A city is "yes" if its boundary contains a named `natural=beach`, or a named "Pantai …" tourist attraction, viewpoint, picnic site or beach resort, within 300 m of the coastline and not mud or rock. OSM has gaps on the coast, so coastal cities with no OSM beach are decided by web-verified verdicts in `beach_web.csv`, each with a URL. |
| 4 Spot-check | 20 seeded-random cities are compared with independent web verdicts in `spotcheck_web.csv`. At least 19 must agree. |
| 5 Deliver | Two sheets, read back and checked. The file is renamed to its final name only after the gate passes. |

## Recorded decisions
- **Stage 1 tolerance:** 3% instead of 2% (user decision). The source has 4,303 rows, which is −2.56% against 4,416. The PDDikti API was unreachable because Cloudflare blocks it.
- **Unknown cities:** 5 institutions in DKI Jakarta have no city in any official or web source. They are kept as `Jakarta (City Unknown)` with beach `unknown` (user decision).
- **Sea beaches only:** lake and river beaches do not count.
- **Provinces:** the source's 34-province scheme is kept, so Papua's 2022 split is not applied. Kota Tarakan is set to Kalimantan Utara.
- **Rokan Hilir:** its OSM boundary ring is not closed, so the outline is rebuilt and flagged as approximate.
- **Second source:** GeoNames (99 beach points) and Wikidata (214 beaches) proved too sparse to serve as the spot-check source, so web verification is used instead.

## Run (in order)
1. Install the dependencies: `pip install -r requirements.txt`
2. Check the code offline: `pytest -q`
3. Run the stages one at a time, and continue only when every gate line prints PASS:
   ```
   python s1_source.py
   python s2_age_filter.py
   python s3_clean.py
   python s4_beach.py
   python s5_deliver.py
   ```
   Stage 4 downloads the ~2 GB OSM extract on its first run and needs about 6 GB of RAM.

## Outputs
- `output/indonesia_higher_ed.xlsx` is the deliverable.
- Evidence in `data/`:
  - Gate reports: `gate_s1.txt` to `gate_s5.txt`.
  - Dropped institutions with their reason: `s2_all_classified.csv`.
  - Beach evidence per city, including its basis (OSM or web): `s4_cities.csv`.
  - Spot-check results: `s4_spotcheck.csv`.
