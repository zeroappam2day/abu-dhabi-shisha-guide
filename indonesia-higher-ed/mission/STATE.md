# Mission: append safety, wage, unemployment, poverty to the 260 beach places
Stage: 4 Fill residue (numeric: all provinces; safety: batch 0 of ~13)   Updated: 2026-10-15

## Outcome (from brief)
- For: user comparing beach places for students aged 17-25. Deliverable: new "Beach shortlist" sheet, 260 rows.
- Columns: Safety (High/Medium/Low/Insufficient evidence) + evidence; UMK 2026; average net wage (if published per regency);
  open unemployment rate (TPT, all ages, Aug 2025); poverty rate (P0, Mar 2025); source and year for each.
- Done when: every row has each value with source + year, or is marked unverified / "not published at regency level";
  spot-check of 20 rows: numeric 19/20 exact; safety 19/20 within one band.

## Decisions
| # | Stage | Decision | Basis |
|---|---|---|---|
| 1 | Brief | Shortlist = 260 beach places | user |
| 2 | Brief | City/regency-level data only (not age-specific) | user |
| 3 | Brief | Safety from forum comments, last 6 months, needs >=2 independent comments, else "Insufficient evidence" | user |
| 4 | Brief | Salary = UMK 2026 + BPS average wage where published | user |
| 5 | Plan | BPS (incl. API) blocked by firewall; WebFetch cannot resolve .go.id; Reddit 403; numeric metrics via news/Databoks/provincial portals | preflight |

| 6 | Probe | Safety pilot forum-only: 0/5 places had >=2 dated comments -> method failed sample test | pilot_safety.csv |
| 7 | Probe | Safety method changed to forum OR local news/police reports, >=2 independent sources, same window and bands | user |
| 8 | Probe | Numeric pilot (Sulsel, 11 searches): UMK 16/16, TPT 15/16, P0 14/16 decimals; rounded values / as-published periods recorded with label | pilot_numeric.csv; user |

## Budget ledger
| Stage | Planned searches | Planned turns | Actual |
|---|---|---|---|
| Probe pilot (1 province, numeric + safety) | ~25 | this turn | |
| Numeric, 34 provinces (~5 agents) | ~150 | 1 | |
| Safety, 260 places at <=2 searches each | ~520 | 3 | |
| Spot-check, 20 places | ~40 | with last batch | |

## Open issues
- (none yet)
