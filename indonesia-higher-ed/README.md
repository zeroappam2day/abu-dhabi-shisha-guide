# Indonesia higher-education workbook

Builds `output/indonesia_higher_ed.xlsx` with four sheets:
- **Institutions:** NPSN, name, type, ownership, address, city/regency, province, levels offered, offers S1/D3/D4, typical student age, beach, duplicate, city source.
- **Summary:** city/regency, province, institution count, beach, number offering S1/D3/D4.
- **Beach shortlist:** one row per beach city/regency (260): safety (walking around) with evidence, UMK 2026, average net wage, unemployment rate, poverty rate, each with period and source URLs.
- **Pivot:** a real, refreshable Excel pivot table. Rows are province, then city; columns are beach; values are the count of institutions; filters are type and offers S1/D3/D4.

It covers every registered higher-education institution: all six types (Universitas, Institut, Sekolah Tinggi, Politeknik, Akademi and Akademi Komunitas), 4,303 rows. Nothing is dropped by age. The "Offers S1/D3/D4" and "Typical student age" columns let you filter instead (user decision; set `AGE_FILTER = True` in config to drop instead). Every stage ends with a gate. If a gate fails, the stage writes `data/gate_sN.txt` and exits, and the workbook is not produced.

## Sources and method
| Stage | Source / rule |
|---|---|
| 1 Institutions | Kemdiktisaintek open-data portal, "Perguruan Tinggi.xlsx" (`download/datasets/6`, 2025), 4,303 rows. 36 rows with city "Lainnya" (meaning "other") are resolved from `city_research.csv`, which records evidence and confidence for each. |
| 2 Levels | "Program Studi.xlsx" (`download/datasets/5`), joined on NPSN. Records the levels each institution offers, whether it offers S1/D3/D4, and a typical student age (S1/D4 18-22, D3 18-21, D2 18-20, D1 18-19, postgraduate 23+). These are typical study ages, not measured: the source has no age data. |
| 3 Clean | City and province prefixes are normalized. `CITY_ALIASES` maps typos and renamed regencies to current official names. Exact duplicates (same name, city and province) are flagged and never removed. |
| 4 Beach | The OpenStreetMap Indonesia extract supplies kabupaten/kota boundaries. A city is "yes" if its boundary contains a named `natural=beach`, or a named "Pantai …" tourist attraction, viewpoint, picnic site or beach resort, within 300 m of the coastline and not mud or rock. OSM has gaps on the coast, so coastal cities with no OSM beach are decided by web-verified verdicts in `beach_web.csv`, each with a URL. |
| 4 Spot-check | 20 seeded-random cities are compared with independent web verdicts in `spotcheck_web.csv`. At least 19 must agree. |
| 5 Deliver | Institutions and Summary sheets, read back and checked. The file is renamed to its final name only after the gate passes. Missing addresses read "Not published in source". |
| 6 Pivot | Headless LibreOffice adds the pivot table. The gate checks that the pivot object exists, that its grand total equals the institution count, and that the Institutions sheet is unchanged. |

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
   python s6_pivot.py
   ```
   Stage 6 needs LibreOffice (`soffice`) to build the pivot table.
   Stage 4 downloads the ~2 GB OSM extract on its first run and needs about 6 GB of RAM.

## Outputs
- `output/indonesia_higher_ed.xlsx` is the deliverable.
- Evidence in `data/`:
  - Gate reports: `gate_s1.txt` to `gate_s6.txt`.
  - Dropped institutions with their reason: `s2_all_classified.csv`.
  - Beach evidence per city, including its basis (OSM or web): `s4_cities.csv`.
  - Spot-check results: `s4_spotcheck.csv`.

## Level of the beach test
"City/Regency" is the kabupaten/kota, Indonesia's second-level administrative unit. A kabupaten (regency) is made up of towns and villages, so institutions in towns and villages are included under their regency. The beach flag is tested per city/regency (user decision). A town-level test was declined because the source gives the town (kecamatan) for only 1,097 of the 4,303 institutions.

## Beach shortlist metrics (web-researched)
| Column | Source / rule | Coverage |
|---|---|---|
| UMK 2026 | Governor decrees via news/GoodStats; where a regency sets none, the province UMP (labelled "UMP") | 260/260 (128 UMP) |
| Average net wage | BPS publishes it only nationally/provincially | "Not published at regency level" for all 260 |
| Unemployment rate | BPS TPT, all ages, 2025, via Databoks/GoodStats mirrors (bps.go.id is firewalled); period as published ("Desember 2025") | 251/260; 9 "Unverified" |
| Poverty rate | BPS P0 2025 via mirrors; 69 values exist only as whole numbers from provincial lists (decimals truncated, labelled in Notes) | 258/260; 2 "Unverified" |
| Swimmable sand beach | Yes = a named sea beach inside the city/regency with sand (not pebble, rock, coral rubble or mud) and a source describing swimming; No = only non-sand shores or swimming banned; evidence in `shortlist_swim.csv` | 120 largest researched (90 Yes, 6 No, 24 Unverified); 140 "Not researched" |
| Priority zone | User's priority area by province: Java (Banten, DKI Jakarta, Jawa Barat, Jawa Tengah, DI Yogyakarta, Jawa Timur), Bali, Lampung; others "Outside" (`config.PRIORITY_ZONES`) | 70 of 260 in zone |
| Safety | High/Medium/Low from >=2 independent local news, police or forum sources dated 15 Apr - 15 Oct 2026; forum-only evidence failed its pilot (0/5) | 60 largest places researched; 200 "Not researched" (user decision); 25 of the 60 "No rating: <2 dated sources found" |

**Spot-checks** (seed 3001, independent agents given no prior values): numeric 20/20 rows agree (poverty 17/17, unemployment 19/19, UMK 19/19 where both found a value). Safety 9/20: all 5 places both sides rated agree within one band; 11 disagreements were "insufficient" vs a rating found with deeper search. The verifier's evidence-backed ratings were adopted for 10 of them (user decision); record in `shortlist_spotcheck.csv`.

**Caveats:** wage and unemployment are all-ages regency figures, not 17-25-specific (user decision: regency-level data only). The safety scale is news-based, so it cannot show "High" (none found).
