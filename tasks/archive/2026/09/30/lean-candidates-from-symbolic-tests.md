# Promote symbolic unit tests to Lean theorems (pick the worthy ones)

**Created:** 2026-09-30 · **Completed:** 2026-09-30 (William Emerison Six <billsix@gmail.com>)
**Part of:** `tasks/archive/2026/10/04/investigate-lean-proofs-for-ga.md` (the Lean-proofs umbrella)

## Goal

gacalc's symbolic unit tests (identities asserted over sympy-symbol multivectors, i.e. laws for all
values) were surveyed to find universal laws asserted only in Python and not yet in Lean
(`proofs/GacalcProofs/*.lean`, gated by `make lean`). The task was scoped as a shortlist; the cheap
high-value items were then proved directly. Distinct from
`tasks/archive/2026/10/05/consolidate-symbolic-equality-predicate.md`, which consolidated the
duplicated equality helpers; no overlap.

## The gap found (each cited by its Python test)

1. Scalar triple product = signed volume = 3×3 determinant (`tests/test_vectorcalc.py`,
   `tests/test_measure.py`).
2. Cross-product coordinate formula and anticommutativity (`tests/test_vectorcalc.py`); Lean had no
   `cross`.
3. The sandwich is grade-preserving for a general even versor (grade-3 part vanishes,
   `tests/test_odd3.py`) — distinct from the isometry lemmas already in `Sandwich.lean`.
4. Gram–Schmidt orthogonality and Hestenes `cₖ = |A_{k−1}|² * wₖ` (`tests/test_frame.py`); Lean had no
   frame theory.
5. 3D vector dual = perpendicular bivector (`tests/test_multivector.py`); only the 2D `dual_vec` existed.
6. content-two-ways = determinant (`tests/test_measure.py`); the Gram-determinant half was already
   `lagrange_3d` / `lagrange_property`, so only the content/rejection equivalence was new.

Already covered in Lean, not re-targeted: `ab = a·b + a∧b` (2D+3D), the projection/rejection split
and `reject_perp`, the Lagrange identity, `I² = −1` / `eᵢⱼ² = −1`, reverse involution,
associativity/distributivity, the plane-rotation cos/sin form, sandwich preserves dot + length + wedge,
`R R̃ = |R|²`, `cos² + sin² = 1`. Skipped as poor candidates (behaviour or code-equivalence tests, not
math laws): `test_same_type_eq_fast_path_stays_simplify_aware`, `test_symbolic_magnitude_stays_symbolic`,
`test_generated_closed_form_matches_definition`.

## Decisions

- **Cutoff:** prove the cheap high-value items (1, 2, 3, 5) in this pass; defer the larger ones
  (4 and 6).
- **Bookkeeping:** the cheap items were done as one pass under this task rather than one task each.
- **Naming caution carried into the proofs:** in Lean `dot` is the scalar part, i.e. gacalc's
  `scalar_product`; gacalc's `dot` / `inner_product` are distinct graded notions
  (`tasks/reference/lean-ga-proof-architecture.md` §"Hestenes projection").

## What was proved (`sorry`-free, gate-verified)

- **Item 2** — new `proofs/GacalcProofs/Cross.lean`: `cross a b := (a∧b) I₃⁻¹`, `cross_vec`
  (coordinate formula), `cross_anticomm_vec`, `cross_perp_left` / `cross_perp_right`.
- **Item 5** — `Cross.lean` `dual_vec` (`(x,y,z)* = −z e₁₂ + y e₁₃ − x e₂₃`).
- **Item 1** — `Cross.lean` `signedVolume := (a∧b∧c).c123` and `dot_cross_eq_signedVolume`
  (`a·(b×c) = signedVolume = det[a,b,c]`).
- **Item 3** — `Sandwich.lean` `sandwich_evenVersor_vec_isVector` (`IsVector (R v R⁻¹)`).

The step commits were squashed into `3f6e933`. The inventory in
`tasks/reference/lean-ga-proof-architecture.md` was updated.

**Deferred:** item 4 (frame theory, a large new area belonging with `tasks/define-frame.md`) and item 6
(needs `area` / `content` definitions in Lean).
