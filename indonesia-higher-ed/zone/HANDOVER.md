# Handover prompt: Priority-zone gap mission

Paste everything below the line into a new Claude Code session on repo `zeroappam2day/abu-dhabi-shisha-guide`, branch `claude/indonesia-higher-ed-workbook-srd1xb`.

---

You are continuing a finished research mission. Your job is to close the evidence gaps for the user's **priority-zone list** without changing any existing data or output. Use the mission skill suite in `.claude/skills/` and load each skill at its stage: mission-orchestrator, mission-plan, mission-research-swarm, mission-gatekeeper, mission-deliver. Read `indonesia-higher-ed/README.md` and `indonesia-higher-ed/mission/STATE.md` first.

## The list (scope)
Use the "Beach shortlist" sheet in `indonesia-higher-ed/output/indonesia_higher_ed.xlsx`. Keep only the rows where `Priority zone` ≠ "Outside", which gives **70 places**: Java 57, Bali 7, Lampung 6. The user's working filter is those 70 with `Swimmable sand beach` = "Yes", which is **56 places**. Work on all 70 so the filter can be re-applied after the fixes.

## Zero-risk rules (non-negotiable)
1. **Baseline:** `indonesia-higher-ed/zone/BASELINE.sha256` lists 148 files. Run `sha256sum -c --quiet indonesia-higher-ed/zone/BASELINE.sha256` at the start and end of **every** stage. Any mismatch → stop, `git checkout -- <file>`, and report.
2. **Write only inside `indonesia-higher-ed/zone/`.** Never edit, move, delete or regenerate anything else. Never run `s1_source.py` … `s6_pivot.py` or `build_html.py`, because they rewrite the baseline outputs. Importing `config`, `shortlist` or `build_html` read-only (for example to reuse `build_html.TEMPLATE`) is allowed.
3. **Overlay, never overwrite.** New findings go in new CSVs under `zone/`. The final outputs show each original value unchanged next to its new value, with a `Changed` flag.
4. **Evidence:** every value needs `"<claim> - <URL>"` from a page you actually opened, or it stays `UNVERIFIED`. Never answer from memory. Never put user personal data in queries or request headers.
5. **Git:** commit after each stage to `claude/indonesia-higher-ed-workbook-srd1xb` only. End every commit message with the session's Co-Authored-By and Claude-Session lines. Do not open a PR.
6. **Confidence-gated stop:** if a gate fails or the evidence doesn't support an answer, stop and ask the user one question with options. Otherwise proceed without asking.

## Known gaps in the 70 (baseline commit e34937f)
| Gap | Count | Detail |
|---|---|---|
| Swim "Yes" never opened | 56 | The round-2 agents could not open pages, so citations come from search summaries. Weak yes: Bekasi (mudflat), Mataram, Garut, Sukabumi, Cianjur (rip currents), Blitar, Pemalang, Tanggamus, Gunung Kidul, Karawang (location), Pasuruan (pollution). |
| Swim "Unverified" | 7 | Kab. Cirebon, Demak, Lumajang, Pati, Purworejo, Tabanan, Kota Probolinggo |
| Swim "No", weak | 1 | Gianyar (rests on one general article) |
| Safety not researched | 35 | |
| Safety "No rating" | 12 | Fewer than 2 dated sources |
| Unemployment unverified | 3 | Demak, Garut, Kulon Progo |
| Poverty whole number only | 22 | Decimals truncated (see Notes column) |
| UMK basis = province UMP | 8 | Confirm that no regency UMK 2026 exists |
| No independent spot-check yet | — | For the swim and second-round safety ratings |

## Stages (each ends with a gate written to `zone/gate_zN.txt`; on FAIL, stop)
**Z0 Preflight.**
- Verify the baseline.
- Test that WebSearch works, and that WebFetch opens 3 sample cited URLs. In round 2, WebFetch DNS failed. If it still fails, stop and ask whether summary-only evidence is acceptable.
- Write `zone/zone_config.py` (all parameters: file paths, the safety window 2026-04-15 to 2026-10-15, which matches the existing ratings, and the seed 4001) and `zone/zone_list.csv` (the 70 keys plus their baseline values).
- Budget ledger: about 200 web searches per turn, shared by all agents. Hold 10 back for yourself.
- Gate: 70 rows, keys match the workbook exactly, baseline intact.

**Z1 Swim.**
- Open each cited URL for the 56 Yes and the 1 weak No. Confirm the page states both sand (not pebble, rock or mud) and swimming. If it doesn't, find a replacement URL.
- Research the 7 Unverified (up to 2 searches each).
- Output `zone/swim_v2.csv` with: city, province, swim_v2, beach_name, evidence, checked (opened/summary), changed.
- Gate: 70 rows; no Yes or No without an opened URL.

**Z2 Safety.**
- Research the 35 Not-researched and the 12 No-rating places with the existing method: at least 2 independent local news or police sources dated inside the window, rated High/Medium/Low.
- Output `zone/safety_v2.csv`.
- Gate: 70 rows, values in the existing `SAFETY_VALUES`, and at least 2 dated URLs per rating.

**Z3 Numbers.**
- Unemployment (TPT) for the 3 unverified.
- Decimal poverty (P0 2025) for the 22 truncated.
- For the 8 UMP places, confirm that no UMK 2026 exists.
- Use the mirrors (databoks, goodstats, news); bps.go.id is firewalled.
- Output `zone/numbers_v2.csv`.
- Gate: each new number has a URL, and every truncated value v satisfies v ≤ new < v+1. If one doesn't, flag it; do not overwrite.

**Z4 Spot-check.**
- An independent agent, given no prior answers, re-checks a seeded random 20 of the 70 on swim and safety.
- Gate: swim ≥ 18/20 agree; safety within one band wherever both sides rated.
- On fail: stop and ask.

**Z5 Deliver.**
- `zone/zone_build.py` writes `indonesia-higher-ed/zone/output/priority_zone.xlsx`, which has 70 rows and these columns: the original 18 shortlist columns unchanged, then `Swim (v2)`, `Swim evidence (v2)`, `Safety (v2)`, `Safety evidence (v2)`, `Unemployment % (v2)`, `Poverty % (v2)`, `UMK note (v2)`, `Changed`.
- It also writes `zone/output/priority_zone.html`, built from `build_html.TEMPLATE` with the v2 values plus the same multi-select filters.
- Read both back.
- Final gate: the baseline is intact (`sha256sum -c`), and `git diff e34937f -- indonesia-higher-ed ':!indonesia-higher-ed/zone'` is empty.
- Commit, push, and send the user the HTML. Report the before/after counts per gap in one table, plus the remaining caveats.

## Reply style
Concise and action-first. Give tables, not prose. If a manual step is needed from the user: give the step and a way to verify it, with no preamble.
