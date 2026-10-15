---
name: mission-gatekeeper
description: Gate and verification rules for a mission-orchestrator run. Defines the PASS/FAIL gate format, the confidence-gated stop rule (proceed when evidence supports the answer, stop and ask when it does not), placeholder and join-rate checks, and the independent seeded spot-check. Use at the end of every mission stage, and whenever deciding whether to proceed or ask the user.
---

# Gatekeeper

## Gate format
Every stage ends by calling `gate(stage, [(check, passed, detail)])`. It prints and saves `PASS|FAIL  check  [numbers + examples]` and exits non-zero on any FAIL. Nothing downstream runs after a FAIL.

## Standard checks (pick the ones that apply)
- Count against the known total, within the brief's tolerance. Report the signed percentage and which total was used.
- No blank **or placeholder** values in required fields.
- Row count equals the previous stage's, or the difference is explained.
- Join rate is 100%, listing every miss.
- One parent per key.
- Every positive verdict carries a named value and a source URL.
- Every residue item has a verified verdict.
- Spot-check agreement ≥ threshold.
- Deliverable read-back: row counts and sums match, and there are no empty cells.

## Confidence-gated stop rule
**Proceed and log** in STATE.md under "Decisions" when all of these hold:
- the fix is mechanical and has a single correct answer (a typo alias, an official rename with a source, a documented OSM error);
- the evidence comes from an official source or ≥2 independent sources;
- it stays inside a tolerance the user already approved.

**Stop and ask** when any of these holds:
- a tolerance is exceeded (count, threshold, or share unverified);
- several plausible answers exist and the choice changes the output (labels for unlocatable rows, two conflicting sources);
- only one weak source supports a verdict that affects ≥1% of rows;
- the method itself failed a sample test (low recall), so the plan must change and costs change with it.

Each stop puts **all** open issues into one message, using AskUserQuestion with the recommended option first. Include the measured numbers and the cost of each option.

## Independent spot-check
- Use a seeded random sample of N items (default 20; threshold from the brief, default ≥19).
- After the method changes, draw a **fresh seed** and record both seeds.
- The verifier is independent of the classifier: a different source, or a separate agent that receives no prior verdicts.
- Exclude user-approved "unknown" items from the sample and report them separately.
- Report the agreement, every disagreement, and the basis mix of the sample (for example, 14 from OSM, 6 from web).

## Honesty
- A gate that passes on a technicality, such as placeholders counted as filled, is a defect. Fix the check.
- Never mark a row verified without evidence, and never weaken a gate silently. Changing a tolerance needs the user's approval.
