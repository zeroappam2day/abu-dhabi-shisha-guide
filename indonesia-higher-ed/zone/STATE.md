# Mission: close evidence gaps for the 70 priority-zone places (overlay only)
Stage: Z5 Deliver (done)   Updated: 2026-10-15

## Outcome
- Deliverable: zone/output/priority_zone.xlsx + .html (70 rows; original 18 columns unchanged + v2 columns + Changed).
- Done when: gates z0-z5 PASS; baseline (148 files) intact; no diff outside zone/ vs e34937f.

## Decisions
| # | Stage | Decision | Basis |
|---|---|---|---|
| 1 | Z0 | Branch claude/indonesia-higher-ed-workbook-srd1xb (user-named; the session's default branch had no mission files) | user |
| 2 | Z0 | WebFetch works (DNS fixed). Sites that return 403 to WebFetch are opened with curl plus a browser UA; both count as "opened" | preflight |
| 3 | Z0 | All 7 swim "No" rows (not only Gianyar) need an opened URL, because the Z1 gate covers every Yes/No | Z1 gate text |
| 4 | Z0 | Mission state is kept in zone/STATE.md; mission/STATE.md is baseline and read-only | rule 2 |

| 5 | Z1 | Kota Serang No->Unverified (one beach only); reviewer override in zone_config | definition |
| 6 | Z2 | Safety bands inferred from 23 existing ratings (no written definition in repo) | baseline data |
| 7 | Z2 | Situbondo Medium->No rating (both sources = same press conference) | independence rule |
| 8 | Z2 | Separate police accounts in one outlet (detik) count as independent | agent prompt rule |

| 9 | Z2 | User chose retry of 39 unrated via news tag/search pages; 33 rated, 6 remain No rating | user |
| 10 | Z4 | Spot-check seed 4001: swim 18/20, safety 12/12 within one band (9 exact) | spotcheck_v2.csv |

## Budget ledger (200 searches/turn shared, 10 reserved)
| Stage | Items | Planned searches | Note |
|---|---|---|---|
| Z1 swim | 63 reopen + 7 research | ~40 (replacements) + 14 | URL opens are fetches, not searches |
| Z2 safety | 47 | ~94-140 | 2-3 per place |
| Z3 numbers | 33 | ~40 | |
| Z4 spot-check | 20 | ~40-60 | next turn if over cap |

## Actuals (turn 1)
Searches ~167/200: swim 46, safety 88, numbers 32, preflight 1.

Turn 2: ~140 searches (safety retry ~24 + direct page fetches; spot-check 54).

## Open issues
- Resolved: safety recall (retry lifted 8/47 to 41/47). rri.co.id still unreachable.
