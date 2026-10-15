---
name: mission-deliver
description: Stage 6 of a mission-orchestrator run. Builds the final artifact (xlsx, csv, document or page) exactly to the brief's schema, verifies it by reading it back, saves it under its final name only after the gate passes, commits the evidence, and writes the final report of results, decisions and caveats. Use when a mission's data is verified and ready to ship.
---

# Deliver

## 1. Build to the schema
- Columns and sheets exactly as in the brief, with nothing extra. Evidence lives in companion files, not in the deliverable, unless the brief asks for it.
- For xlsx, load the `xlsx` skill if formatting matters. Add a header row, freeze panes and autofilter.
- Write to `<name>.unverified.<ext>`, then rename to the final name **only after the read-back gate passes**. A partial artifact must never carry the final name.

## 2. Read-back gate
Reopen the file and check:
- row counts against the previous stage;
- totals and sums across sheets;
- no empty cells;
- the value domains (for example, the flag is only in {yes, no, unknown}).

## 3. Persist and share
- Commit the artifact, the gate logs and the evidence files. Force-add them if `data/` or `output/` is git-ignored. Push to the designated branch.
- Send the file to the user (SendUserFile, set to attach), or publish it if the brief says it is for others.

## 4. Final report
Write it in this order:
1. **Result:** the numbers for each sheet.
2. **Gates:** a one-line table per stage.
3. **Sources and method:** one line each.
4. **Decisions:** every user decision and every logged auto-decision.
5. **Caveats:** unknown rows, weak-evidence verdicts, approximations, schema mismatches with the source (for example, old province names).
6. **Where the evidence lives:** the paths.

Disclose any mistakes that affected the user, such as data sent externally.

Keep it compact and end when complete.
