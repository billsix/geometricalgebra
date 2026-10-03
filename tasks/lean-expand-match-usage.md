# Sweep the Lean proofs for additional `match` / total-dispatch opportunities

**Status:** done — investigation found nothing to convert (no-op). Archivable.
**Priority:** 7
**Difficulty:** 3
**Created:** 2026-10-03 (William Emerison Six <billsix@gmail.com>, stream-of-consciousness notes:
"I really like match … see if there are more places that you can use match").
**Part of:** the Lean proof initiative, `tasks/investigate-lean-proofs-for-ga.md`.
**See also:** `tasks/reference/lean-ga-proof-architecture.md`; the cross-project convention
"Prefer total dispatch over an open-ended conditional chain" in the shared `CLAUDE.md`; sibling
`tasks/lean-grade-projection-as-basis-combination.md`.

## BLUF

The maintainer likes the `match` style used in `rVectorPart` (`GradeProjection.lean:16/48`, with a
total `| _ => ⟨0,0,0,0⟩` catch-all) and wants a sweep of `proofs/GacalcProofs/*.lean` for other
places a `match` on structure would read better than the current form — chained `if`/`else`,
nested conditionals, or dispatch-on-a-tag. **Scoped by the existing rule**, not blanket: `match`
earns its keep on *structural* patterns with a mandatory-feeling default; a `match` whose every arm
is a boolean guard is an `if/elif` chain in disguise and must NOT be converted. "Done" = a reviewed
list of candidate sites, the clear wins converted, each keeping an explicit/total default, and
`make lean` green + `sorry`-free.

## Context — how to read this cold

This is a readability/idiom pass over the Lean corpus, the Lean analogue of the Python "prefer
total dispatch" convention (which itself carries the caveat: don't convert every two-branch
conditional; `match` is for structural patterns). `rVectorPart` is the model the maintainer likes —
a `match r with | 0 => … | 1 => … | 2 => … | _ => …` that is total by construction.

## Method

1. Grep the source `*.lean` (exclude `.lake/`) for `if … then … else`, nested conditionals, and
   natural-number / grade dispatch that currently uses something other than `match`.
2. For each, judge: is this a **structural** pattern (grade, constructor, index) → good `match`
   candidate; or a **boolean guard** → leave it. Produce the candidate list for review before
   converting (this is a judgment pass, not a mechanical codemod).
3. Convert the clear wins; every converted `match` keeps an explicit, total default (a real arm or a
   commented exhaustive-by-construction note), per the dispatch rule.
4. `make lean` green + `sorry`-free; confirm no proof broke (a `match` change can shift what `simp`
   unfolds).

## Decisions (resolved 2026-10-03, William Emerison Six <billsix@gmail.com>)

1. **Delivery = incremental, review-by-diff.** Convert the clear structural wins one increment at a
   time and leave each change **UNSTAGED**; the maintainer reads the diff and says whether he likes
   it. Only on approval is that increment staged and kept. (Neither "list first" nor "convert all and
   report" — a live diff-review loop.) Each increment must still leave `make lean` green + `sorry`-free.

## Findings (2026-10-03 — sweep complete, empty)

Scanned all `proofs/GacalcProofs/*.lean` (excluding `.lake/`) for term-level `if/then/else`, `ite`,
`dite`, `cond`, and for Nat/grade/constructor case-dispatch defs. Result:

- **Zero** term-level conditionals in proof code — every `if … then` hit was inside a docstring
  comment (`AlgebraLaws.lean:51/107`, `ProjectionRotation.lean:117`, `Rotation3D.lean:25`, etc.).
- The **only** `match` blocks are the two `rVectorPart` defs (`GradeProjection.lean:17,49`) — the
  model the maintainer already likes, each already total (`| _ => …`).
- No other definition enumerates cases in a non-`match` way; nothing warrants conversion.

Conclusion: the codebase already uses `match` wherever structural dispatch occurs, and there are no
`if`/`elif` chains to convert. **No code change, no diff to review.** The forward-looking "prefer
total dispatch / `match` for structural patterns" preference already lives in the shared
cross-project convention; future code should follow it, but there is nothing to retrofit here.

(Not pursued: converting tactic-mode case splits — `rcases`/`cases`/`split` with `·` bullets — into
term-mode `match`. That's a different, riskier refactor than the term-level `match` the notes were
about, and was not requested.)

## Open questions

None — sweep complete, nothing to convert.
