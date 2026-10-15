# Indonesia higher-education workbook

Builds `output/indonesia_higher_ed.xlsx` with two sheets. **Institutions** lists every active institution with at least one active S1, D3 or D4 program, and **Summary** gives the institution count and a real-sea-beach flag per city.
Every stage ends with a gate. A failed gate writes `data/gate_sN.txt`, exits, and the next stage must not be run.

Run it on a machine with open internet. The cloud workspace blocks PDDikti, Overpass and GeoNames.

## Sources
| Stage | Source |
|---|---|
| 1 Institutions (name, city, province, status) | PDDikti API `v2/pt/search/filter` + `pt/detail` via `pddiktipy` |
| 2 Programs with Jenjang | PDDikti `pt/prodi/{id}/{semester}` (semesters in `config.SEMESTERS`) |
| 4 Beaches | OpenStreetMap Overpass: named `natural=beach` inside the kabupaten/kota boundary, within 300 m of `natural=coastline`, surface not mud/rock |
| 4 Spot-check | GeoNames `ID.zip` beach points (BCH/BCHS) inside the same boundary (an independent gazetteer) |

## Run (in order)
1. Install Python 3.11+ and the dependencies:
   `pip install -r requirements.txt`
2. Check the code offline: `pytest -q`. It should report 6 passed.
3. Open https://pddikti.kemdiktisaintek.go.id in Chrome and wait until the page loads, which passes the Cloudflare check.
4. Press F12 and copy these two values:
   - **Application → Cookies →** the `cf_clearance` value.
   - **Console →** run `navigator.userAgent` and copy the result.
5. Set them in the terminal you will use for the run:
   - Windows PowerShell: `$env:PDDIKTI_CF_CLEARANCE="..."; $env:PDDIKTI_UA="..."`
   - Ubuntu: `export PDDIKTI_CF_CLEARANCE="..." PDDIKTI_UA="..."`
6. Run the stages one at a time, and continue only when the gate prints all PASS:
   ```
   python s1_source.py
   python s2_age_filter.py
   python s3_clean.py
   python s4_beach.py
   python s5_deliver.py
   ```
   If a stage stops with a 403, repeat steps 3–5 and re-run that same stage. Responses are cached in `data/`, so a re-run resumes where it stopped.

## Rules encoded
- **Status:** only `status_pt = Aktif` counts toward Stage 1. The status breakdown is printed in the gate.
- **Age filter:** an institution is kept if it has at least one active S1, D3 or D4 program. One with no program data in any listed semester fails the gate; it is not guessed.
- **Duplicates:** an exact duplicate is the same name (case-insensitive), city and province. Every copy is flagged `yes` and none is removed.
- **Beach:** sea beaches only, so lake and river beaches do not count. Every `yes` lists the beach name and its OSM URL in `data/s4_cities.csv`.
- **Gate fixes:** if a gate asks for a fix, edit only `config.py`. That means `CITY_ALIASES`, `OSM_RELATION_OVERRIDES` or `SEMESTERS`.

## Outputs
- `output/indonesia_higher_ed.xlsx` is the deliverable. It is written only after the Stage 5 gate passes.
- Evidence in `data/`:
  - Gate reports: `gate_s1.txt` to `gate_s5.txt`.
  - Dropped institutions with their reason: `s2_all_classified.csv`.
  - Beach evidence: `s4_cities.csv`.
  - Spot-check results: `s4_spotcheck.csv`.
