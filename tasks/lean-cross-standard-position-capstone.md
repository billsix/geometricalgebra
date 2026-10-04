# Lean: assemble the CrossStandardPosition step-lemmas into a capstone (cross via reduction = canonical)

## BLUF

`proofs/GacalcProofs/CrossStandardPosition.lean` proves all the *steps* of computing the 3D cross
product by reducing two vectors to a standard frame — `cross` is equivariant under the elementary
plane rotations (`cross_rotXY/XZ/YZ_equivariant`), the reduction lands `a` on `e₁` and `b` in the
`e₁e₂` plane (`reduceToPlane_a_on_e1`, `reduceToPlane_b_in_plane`), and in that frame the cross is a
pure `e₃` vector (`cross_reduced`) — but it **never assembles them into a capstone theorem**. Those
step-lemmas are currently *stranded* (proven, 0 citations). This task writes the capstone: prove the
general cross product equals the value obtained by reducing to the standard frame, computing there,
and rotating back — i.e. **cross-via-reduction = canonical `cross`** — closing the cross arc the same
way `StandardPosition.lean` caps the project/reject arc. "Done" = a capstone theorem that cites the
stranded step-lemmas (so they are no longer stranded) and `make lean` is green.

**Status:** proposed — needs go-ahead. **Priority:** 6. **Difficulty:** 7.
**Created:** 2026-10-03 (William Emerison Six <billsix@gmail.com>). Surfaced by the dead-code audit
(`tasks/lean-proofs-dead-code-audit.md`): those step-lemmas are *proven-but-not-assembled*, not dead.
**See also:** `tasks/reference/reduction-to-standard-position.md` (the arc; its "full bootstrap arc"
section names the cross product as the one step whose equality is not yet assembled — this task);
`tasks/reference/lean-ga-proof-architecture.md`.

## Context — read these first (cold start)

- **The theme** (`reduction-to-standard-position.md`): an operation is additionally defined by
  rotating the figure to a standard frame with **elementary plane rotations** (NOT versors — that's
  the non-circular point), doing the easy version there, and rotating back. The canonical
  Hestenes-form definition stays primary; the reduction form is a cross-checking pedagogical
  duplicate. The hand-written derivation is `multivariate-math/proofs/crossproduct.tex`
  (github.com/billsix/multivariate-math), which this Lean arc mirrors.
- **The analogous CAPPED arc** to mirror: `proofs/GacalcProofs/StandardPosition.lean` caps the
  project/reject/geometric-product arc — `rotate_b_to_e1` / `rotate_b_to_e1_magnitude`,
  `mul_eq_proj_dot_add_reject_wedge`, and above all `projectSP_eq_proj` (align → keep the x-component
  → unalign, proved equal to `proj` via `proj_onto_x_axis`, `alignSP_self`, equivariance, and the
  `rot*_inv` inverses). Model the cross capstone on how that assembles the align-to-`e₁` rotations +
  the reduced-frame computation.
- **What already exists in `CrossStandardPosition.lean`** (the ingredients; cited counts from the
  2026-10-03 audit):
  - rotation algebra: `rotYZ_smul/_sub/_preserves_dot`, `rotXY_vec`/`rotXZ_vec`/`rotYZ_vec` (used).
  - **stranded steps (0 citations — to be consumed by the capstone):** `rotYZ_fixes_e1` (`:63`),
    `vecReject_rotXZ_equivariant`/`_rotYZ_equivariant` (`:77`,`:82`),
    `cross_rotXY_equivariant`/`_rotXZ_`/`_rotYZ_` (`:94`,`:109`,`:124`),
    `reduceToPlane_a_on_e1` (`:167`), `reduceToPlane_b_in_plane` (`:180`),
    `vecReject_reduced` (`:205`), `cross_reduced` (`:213`).

## What to prove (the capstone)

A theorem stating that the general cross product is recovered by the reduction route: reduce `a`, `b`
to the standard frame via the composed elementary rotations, apply `cross_reduced` there, and rotate
back by the inverse rotations — and that this equals the canonical `cross a b`. Follow the shape of
`StandardPosition.lean`'s project/reject capstone. The `cross_rot*_equivariant` lemmas are exactly the
"rotating back commutes with cross" ingredient; `reduceToPlane_*` place the operands; `cross_reduced`
is the easy in-frame value. State it over vectors/`IsVector` objects where practical (per
`CLAUDE.md` "use coordinates only when needed"), dropping to the coordinate step-lemmas via the usual
bridge.

## How to verify

`make lean` green (`proofs/check.sh`: `lake build` + no `sorry`/`admit`), and the previously-stranded
step-lemmas above now show ≥1 citation (re-run the audit scan). If the Python `vectorcalc.cross`
grows a matching "standard-position" pedagogical note or variant, cross-link it — but that is
optional and out of scope here (this task is the Lean capstone only).

## Open questions

1. State the capstone purely over objects (`{a b : G3}` + `IsVector`), or in coordinates to match the
   existing coordinate step-lemmas it assembles? My recommendation: coordinates for the capstone
   statement (it must thread the explicit `(cos, sin)` of the reduction rotations, which are
   coordinate data), consistent with how `StandardPosition.lean`'s capstone is stated.
2. Is a Python/notebook companion wanted (a `cross` "reduction" cross-check, mirroring `project_sp`),
   or is the Lean capstone sufficient? My recommendation: Lean only for now; file a separate task if a
   Python duplicate is desired.
