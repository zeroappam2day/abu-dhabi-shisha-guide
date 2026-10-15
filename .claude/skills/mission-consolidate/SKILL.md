---
name: mission-consolidate
description: Stage 3 of a mission-orchestrator run. Builds the base table with code: download, extract, join on keys, filter, normalize names, flag (never silently drop) duplicates, and reduce to the unique keys that need an attribute. All parameters sit in one config file and every step ends in a gate. Use when combining sources or spreadsheets into one consolidated table.
---

# Consolidate (code-first build)

## Structure (modular and swappable)
```
config.py        all URLs, column maps, tolerances, alias tables, placeholders
common.py        shared helpers: gate(), read/write rows, download(), normalizers
s1_source.py  s2_filter.py  s3_clean.py  s4_attribute.py  s5_deliver.py
test_pipeline.py offline tests on fixtures (including failing-gate tests)
```
Each stage reads the previous stage's CSV and writes its own, so stages can be rerun independently. Downloads are cached in a git-ignored `data/` folder.

## Rules
1. **Join on codes, not names**, wherever a code exists (for example NPSN or a ticker).
2. **Normalize before grouping:**
   - prefixes and casing;
   - aliases for typos and renamed entities, with the year of change noted;
   - a **compact match key** (lower-case, no spaces, punctuation or filler words);
   - **type guards** so similar names of different types never cross-match (Kota X vs Kabupaten X).
3. **Placeholders count as blank:** "Lainnya", "-", "Other", "N/A", "Unknown". Resolve them through a committed research file with evidence and confidence (`<entity>_research.csv`), or label them per the brief.
4. **One value per key:** check that each grouping key maps to exactly one parent (for example, one province per city). A split means a stale or misattributed record; fix it in config with a comment.
5. **Flag, never delete:** duplicates get a flag column. Excluded rows are written to a classified file with the reason.
6. **Join-rate report:** when matching to an external reference (boundaries, tickers), print the unmatched keys **all at once**, then fix them with a single alias pass. Do not iterate one at a time.
7. **Then deduplicate to unique keys** for the attribute stage. Decide the attribute once per key and join it back, never per row.

## Gate (each stage)
- Row count matches the previous stage, or the difference is explained.
- Zero blank or placeholder values in required fields.
- Join rate is 100%, or the misses are listed.
- One parent per key.

Use `mission-gatekeeper` for the gate format and the stop rule.

## Hygiene
- Kill processes by PID, never with `pkill -f <pattern>`, which matches your own shell.
- Do not chain a file edit with a long-running or kill command.
- Filter big binary datasets (OSM PBF) in the C++ layer (pyosmium `with_filter(TagFilter/IdFilter)`), not in Python loops.
