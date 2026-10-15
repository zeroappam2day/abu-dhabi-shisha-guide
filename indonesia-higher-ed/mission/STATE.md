# Mission: append safety, wage, unemployment, poverty to the 260 beach places
Stage: 6 Deliver (done)   Updated: 2026-10-15

## Outcome (from brief)
- For: user comparing beach places for students aged 17-25. Deliverable: new "Beach shortlist" sheet, 260 rows.
- Columns: Safety (High/Medium/Low/Insufficient evidence) + evidence; UMK 2026; average net wage (if published per regency);
  open unemployment rate (TPT, all ages, Aug 2025); poverty rate (P0, Mar 2025); source and year for each.
- Done when: every row has each value with source + year, or is marked unverified / "not published at regency level";
  spot-check of 20 rows: numeric 19/20 exact; safety 19/20 within one band.

## Process note
- Turn 1 ran stages 2-4 without loading mission-source-scout / mission-research-swarm / mission-gatekeeper; budget safety factor was skipped (190/200 planned). Corrected from turn 2: skills loaded per stage, swarm maths and prompt template applied.

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

| 9 | Fill | Numeric merged (shortlist_numeric.csv): UMK 260/260 (128 UMP), poverty 254/260 (69 whole-number, decimals truncated), TPT 246/260 (period as published "Desember 2025"), avg wage 0/260 (not published at regency level) | batches 0-5 + pilot |
| 10 | Fill | Safety batch 0 (20 largest): 6 Medium, 5 Low, 9 Insufficient; evidence is local news/police (forums not indexed) | safety_result_0.csv |

| 11 | Fill | Safety stopped at 60 researched places; 200 "Not researched" | user |
| 12 | Verify | Spot-check seed 3001: numeric 20/20; safety 9/20 (5/5 where both rated, within one band; rest coverage) | shortlist_spotcheck.csv |
| 13 | Verify | Adopt verifier's ratings for 10 places it rated; "Insufficient evidence" relabelled "No rating: <2 dated sources found" | user |

## Budget ledger
| Stage | Planned searches | Planned turns | Actual |
|---|---|---|---|
| Probe pilot (1 province, numeric + safety) | ~25 | this turn | |
| Numeric, 34 provinces (~5 agents) | ~150 | 1 | |
| Safety, 260 places at <=2 searches each | ~520 | 3 | |
| Spot-check, 20 places | ~40 | with last batch | |
| Actual this turn | numeric 6x25 + safety 36 = ~186 searches | 1 turn | on plan |
| Remaining (re-planned with mission-research-swarm budget maths: floor(190/(2x1.5)) = 63 items/turn) | safety 240 places + gaps 19 + spot-check 20 | 5 turns | |
| Turn 2 | safety batches 1-2 (40) + numeric gaps (19); ~149 planned | 1 | running |

## Open issues
- (none yet)
