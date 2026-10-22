# Lean: assemble the CrossStandardPosition step-lemmas into a capstone (cross via reduction = canonical)

**Status:** done — 2026-10-22 (William Emerison Six <billsix@gmail.com>). All three forms delivered;
`make lean` green (`[lean] OK`); the previously-stranded step-lemmas are all cited now.
**Priority:** 6 **Difficulty:** 7
**Created:** 2026-10-03 **Updated:** 2026-10-22 (William Emerison Six <billsix@gmail.com>)

## What this was

`proofs/GacalcProofs/CrossStandardPosition.lean` proved all the *steps* of computing the 3D cross
product by reducing two vectors to a standard frame (equivariance of `cross` under the elementary
plane rotations, the `reduceToPlane_*` placements, the in-frame `cross_reduced`) but never assembled
them into a capstone — the step-lemmas were *stranded* (proven, 0 citations). This task wrote the
capstone, and per the standing "Lean + symbolic Python + prose/LaTeX" default, in all three forms.

## Decision (2026-10-22, William Emerison Six <billsix@gmail.com>)

GO, and in ALL THREE FORMS (this overrode the task's original "Lean only" recommendation in Q2):
the Lean capstone (over geometric objects, not free scalars — Q1), a symbolic-Python check, and a
book page citing the Lean theorem by name.

## What was done (commit `23aaee9`)

**Lean** (`proofs/GacalcProofs/CrossStandardPosition.lean`):

- `cross_reduceToPlane_equivariant` — `cross` commutes with the full 3-rotation reduction, composing
  the three elementary equivariances. This consumes the previously-stranded **object-form**
  `cross_rotXY_equivariant` / `cross_rotXZ_equivariant` / `cross_rotYZ_equivariant` (the flagged
  0-citation ones; their `_coord` leaves each already had a citation).
- `rotYZ_inv`, `unreduceToPlane`, `unreduceToPlane_reduceToPlane` — the reduction is invertible.
- `cross_eq_unreduce_cross_reduce` — the round-trip capstone: `cross a b = rotate-back(cross (reduce a)
  (reduce b))`, for any unit angle pairs. The "both routes agree" payoff (sibling of
  `projRotation_eq_sandwich`).
- `cross_via_reduction` (object form) + `cross_via_reduction_of_vectors` (explicit reduction angles):
  with `a` on `e₁` and `b` in-plane, the reduced cross is the pure-`e₃` vector `(0,0,|a|*b₂')`
  (`cross_reduced`); the explicit-angle corollary cites `reduceToPlane_a_on_e1` and
  `reduceToPlane_b_in_plane`. **All six step-lemmas now have ≥1 citation** (re-verified by the
  audit scan). Full `proofs/check.sh` green.

**Symbolic Python**: `book/docs/notebooks/proof-cross.py` — the reduce-both → cross → rotate-back
construction, verified symbolically equal to `gacalc.vectorcalc.cross` (exact `a`, symbolic `b`; the
swing's `sqrt` cancels in the round trip). ty / ruff / annotation checks pass; runs clean.

**Book**: `book/docs/proof-cross.rst` states the capstone, derives the reduction, and cites the Lean
theorems by name; wired into `index.rst` + the companion-notebook toctree. The arc reference doc
`tasks/reference/reduction-to-standard-position.md` updated (cross capstone no longer "not yet
assembled").

## Open questions — both resolved by the decision

1. Objects vs coordinates in the statement → **objects** (`cross_via_reduction` is stated over
   `{a b : G3}` + `IsVector`, angles introduced via `reduceToPlane`, as recommended).
2. Python/notebook companion wanted? → **yes** (the decision required all three forms).

## Verification note (for the maintainer)

`make lean` was run green this session. The book page + notebook were validated piecewise (ruff/ty/
annotations, the notebook executed), but a full `make docs` (Sphinx/TeX) was **not** run here — worth
a `make docs` on the host to confirm `proof-cross.rst` + the notebook render. The new page/notebook
also join the voice-pass queue in `tasks/proof-projection-book-voice-pass.md`.
