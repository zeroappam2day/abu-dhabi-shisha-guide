---
name: mission-brief
description: Stage 0 of a mission-orchestrator run. Turns a mass-research request into an approved brief: the outcome (who, what they do after, how success is measured), deliverable schema, success criteria and tolerances. It uses a one-question-at-a-time reverse interview and flags vague or contradictory points. Use at the start of any research-and-consolidate mission, or when the user says "brief", "scope this" or "ask me what you need".
---

# Mission Brief (O + R)

## 1. Draft the outcome before asking anything
State your draft of:
- **Who:** who uses the output.
- **After:** what they will do or decide with it.
- **Done when:** measurable success criteria.
- **Deliverable:** format, sheets or sections, and exact columns.

## 2. Flag vagueness and contradictions
List every vague term, for example "beach" vs "coastal", or a "city" that may be an administrative unit or a town. Also list every rule that conflicts with another, for example "fewest turns" vs "always stop". Do this in the same message as the draft.

## 3. Reverse interview: one question per turn, decision-changing questions only
Ask a question only if its answer changes the plan. Use AskUserQuestion with 2–4 options, putting the recommended option first. Cover these, skipping any the user has already answered:
1. **Unit of record:** what one row is (institution, stock, recipe…) and its unique key.
2. **Inclusion rule:** the filters, and what is excluded.
3. **Attribute definitions:** strict definitions, edge cases, and what does not count.
4. **Source preferences:** official or required sources, and forbidden ones.
5. **Execution venue:** this session (cloud or local) or the user's machine. Network or credential limits.
6. **Tolerances:** count tolerance against the known total; whether "unknown" values are allowed and how they're labelled; the spot-check size and threshold.
7. **Row policy:** whether rows are ever dropped or deduplicated, or kept and flagged.

Do not try to list every possible failure upfront. The gatekeeper handles the unforeseen ones with confidence-gated stops.

## 4. Approval
Restate the brief as a compact block: outcome, rules, deliverable schema, tolerances and assumptions. Then wait for "go". Write it into `mission/STATE.md` under "Outcome".

## Anti-patterns
- Several questions in one message when the user asked for one at a time.
- Asking something the codebase, data or a cheap probe could answer.
- Starting work before "go".
