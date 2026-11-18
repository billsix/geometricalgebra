# Investigate: generate percent-formatted Python proof notebooks from Lean proofs

**Completed:** 2026-11-18 (William Emerison Six <billsix@gmail.com>; authorized batch
`ready-tasks-batch-2026-11-18`)
**Part of:** `tasks/proof-notebooks-student-math-notation-style.md` (the proof-notebook umbrella)
**Priority:** 7
**Difficulty:** 7

## Outcome

The answer is go, in the "checked by Lean" form: the notebook does the symbolic expansion and cites
the Lean theorem that certifies it. Nothing is generated from Lean's steps, because a `ring` proof
has none. The finding is in `tasks/reference/lean-python-notebook-workflow.md`, under
"Showing the cancellation" and "Why 'checked by Lean'".

Built:
- **`gacalc.nbdisplay.show_cancellation(left, right, left_name, right_name)`**, with the doctested
  `cancellation_latex` it displays. It shows both sides expanded, then one line per blade, with each
  cancelling pair of monomials marked `\underbrace{…}_{k}` with a shared `k` and the residual at the
  end. This answers the maintainer's 2026-09-30 complaint that the associativity demo "just shows 0".
- **The prototype, `notebooks/displayproofs.py`, on distributivity:** three general symbolic 𝒢₂
  multivectors, `show_mult` of `a * (b + c)`, `a * b` and `a * c`, then `show_cancellation` (8
  numbered pairs per blade, residual 0). It is tagged `twin: GacalcProofs.G2.mul_add`.
- **`notebooks/displaymv.py`'s associativity proof** now ends with `show_cancellation` (16 pairs per
  blade) instead of a bare difference. It is tagged `twin: GacalcProofs.G2.mul_assoc`.
- The matching `-- twin:` comments are in `proofs/GacalcProofs/G2.lean`.
- `CHANGELOG.md` (Added) and `CLAUDE.md` (the `nbdisplay` and demo-notebook lines) are updated.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-18)

1. Checked by Lean, not transcribed (no `calc` re-proofs, no extractor).
2. The first prototype is distributivity.

## Not done

- The Lean tracing options were not spiked. Decision 1 made them moot, and `ring` decides by
  normalizing both sides to one polynomial form in a single reflection step, so there is no rewrite
  chain to print.
- No generator task was scaffolded, since nothing is generated. Applying `show_cancellation` to more
  laws and to the book's proof notebooks is the umbrella task's backlog.

## Verification

- The `nbdisplay` doctests passed (6).
- Both notebooks ran headless (Agg). The associativity cancellation was checked programmatically:
  every line ends `= 0`, with 32 underbraces per blade.
- ruff and `ty check` were clean on the module and notebooks.
- `lake build GacalcProofs.G2` passed with the tags.
