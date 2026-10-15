# Templates

## mission/STATE.md
```markdown
# Mission: <one line>
Stage: <0-6 name>   Updated: <ISO time>

## Outcome (from brief)
- For: <who>  |  Deliverable: <format, columns>  |  Done when: <success criteria>

## Decisions (append-only)
| # | Stage | Decision | Basis (evidence / user) |

## Budget ledger
| Stage | Planned calls | Planned searches | Planned tokens | Actual | Note |

## Open issues (batch into the next stop)
- <issue> — <why confidence is low> — <options>
```

## Gate log line (printed and saved by every gate)
`PASS|FAIL  <check>  [<numbers and examples>]`, with one line per check, saved to `mission/gates/gate_<stage>.txt`.

## Evidence CSV contract (all research output)
```
key_1,...,key_n,verdict,value,evidence,verified
```
- `evidence` is `"<specific claim> - <URL actually seen>"`.
- `verified` is `yes` only if a URL is present and the claim was read from that source (not from memory).
- If there is no source, `evidence` starts with `UNVERIFIED` and `verified` is `no`. Unverified rows are never shipped as verified.

## Research-agent prompt (fill in the <...> fields)
```
Read <input file> (one "<key> | <key2>" per line). For EACH line decide <question> using web search
(load WebSearch via ToolSearch "select:WebSearch" if needed). Budget: at most <k> searches per item;
never answer from memory.

Definition (strict): yes = <...>. no = <...>. Exclusions: <...>. Disambiguation: <...>.

Write with the Write tool to <output file>, header exactly: <header>.
Copy the keys EXACTLY. evidence = "<claim> - <URL>" double-quoted, with no line breaks.
If no web evidence was found: start evidence with UNVERIFIED.
Reply only with the row count and up to 5 lines on genuinely uncertain items.
```
Never include user personal data in queries or request headers.
