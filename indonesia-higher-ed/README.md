# Indonesia higher-education workbook

Builds `output/indonesia_higher_ed.xlsx` with two sheets. **Institutions** lists every active institution with at least one active S1, D3 or D4 program, and **Summary** gives the institution count and a real-sea-beach flag per city.
Every stage ends with a gate. A failed gate writes `data/gate_sN.txt`, exits, and the next stage must not be run.

All sources are public downloads. Every stage downloads its own source once into `data/` (git-ignored).

## Sources
| Stage | Source |
|---|---|
| 1 Institutions (NPSN, name, city, province) | Kemdiktisaintek portal, "Perguruan Tinggi.xlsx" (`download/datasets/6`, 2025): 4,303 rows |
| 2 Programs with Jenjang | Kemdiktisaintek portal, "Program Studi.xlsx" (`download/datasets/5`, 2025), joined on NPSN |
| 4 Beaches | OpenStreetMap Indonesia extract (openstreetmap.fr, ~2 GB): named `natural=beach` inside the kabupaten/kota boundary, within 300 m of `natural=coastline`, surface not mud/rock |
| 4 Spot-check | GeoNames `ID.zip` beach points (BCH/BCHS) inside the same boundary (an independent gazetteer) |

**Stage 1 gate tolerance:** set to 3% by user decision. The source has 4,303 rows, which is −2.56% against 4,416.

## Run (in order)
1. Install the dependencies: `pip install -r requirements.txt`
2. Check the code offline: `pytest -q`. It should report 6 passed.
3. Run the stages one at a time, and continue only when the gate prints all PASS:
   ```
   python s1_source.py
   python s2_age_filter.py
   python s3_clean.py
   python s4_beach.py
   python s5_deliver.py
   ```
   Stage 4 downloads the ~2 GB OSM extract and needs about 6 GB of RAM to read it.

## Rules encoded
- **Age filter:** an institution is kept if it has at least one S1, D3 or D4 program. One with no program data fails the gate; it is not guessed.
- **Duplicates:** an exact duplicate is the same name (case-insensitive), city and province. Every copy is flagged `yes` and none is removed.
- **Beach:** sea beaches only, so lake and river beaches do not count. Every `yes` lists the beach name and its OSM URL in `data/s4_cities.csv`.
- **Gate fixes:** if a gate asks for a fix, edit only `config.py`. That means `CITY_ALIASES` or `OSM_RELATION_OVERRIDES`.

## Outputs
- `output/indonesia_higher_ed.xlsx` is the deliverable. It is written only after the Stage 5 gate passes.
- Evidence in `data/`:
  - Gate reports: `gate_s1.txt` to `gate_s5.txt`.
  - Dropped institutions with their reason: `s2_all_classified.csv`.
  - Beach evidence: `s4_cities.csv`.
  - Spot-check results: `s4_spotcheck.csv`.
