---
name: mission-source-scout
description: Stage 2 of a mission-orchestrator run, and callable whenever a new source is considered. Finds candidate sources (official portals, datasets, APIs, extracts, gazetteers) and tests each on a ~10–20 item sample for reachability, schema, completeness, coverage and recall, before any code or research depends on it. Use before adopting any data source or second source.
---

# Source Scout

No source is used at scale until it passes a sample test. Most rework comes from skipping this step.

## 1. Find candidates (cheap first)
1. Sources the user named or required.
2. Official portals. **List the whole catalogue.** Datasets are often addressable as `/download/datasets/{id}`; loop the IDs and read only the headers (filename, size). This takes about 2 minutes and finds files a homepage hides.
3. Open structured data (OSM extracts, government APIs, Wikidata).
4. Community mirrors (GitHub). Check how fresh they are.

## 2. Test each candidate on a sample (one batched command where possible)
| Check | How | Fails if |
|---|---|---|
| Reachable | HTTP status from this environment; note any Cloudflare/JS wall | 403 challenge, timeout, needs a browser |
| Schema | Read the header and 10 rows | Required fields missing |
| Completeness | Row count against the known total; blank and placeholder share ("Lainnya", "-", "Other", "N/A") | Outside tolerance |
| Freshness | Publication date or last-modified | Older than the brief allows |
| Coverage / recall | For an attribute source: run 10–20 items with a known answer (from your knowledge or a web check) and compute the hit rate | Recall < 90% means the residue goes to `mission-research-swarm`, sized by the miss rate |
| Join key | Share of rows that join to the base table on the key | < 99% → normalization is needed (`mission-consolidate`) |

## 3. Record the decision
For each source, write to STATE.md:
- adopt or reject;
- the measured numbers;
- the expected residue.

A second source for spot-checks must be independent of the first and have coverage at least equal to it. Count its records before adopting it.

## Anti-patterns
- Adopting a gazetteer without counting its records (GeoNames had 99 beach points for all of Indonesia).
- Assuming that tag-based data (OSM) is complete for subjective categories.
- Fetching full datasets to inspect a schema.
