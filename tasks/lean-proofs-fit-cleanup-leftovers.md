# Lean proofs: finish what the fit cleanup left

**Status:** proposed — needs go-ahead (filed 2026-11-23)
**Priority:** 7
**Difficulty:** 5
**Created:** 2026-11-23 (William Emerison Six <billsix@gmail.com>)
**Source:** the archived `tasks/archive/2026/11/23/lean-proofs-fit-cleanup.md` (phase 5, and phase 7's "Not done")

## BLUF

Five small items from the Lean fit cleanup were left on purpose. None is a correctness problem: each makes
a proof or a statement closer to the house style ("objects in, scalars only in the body", one proof per fact,
every result cited from the book). Done = each item is done or declined with a reason, `make lean` passes, and
`tasks/reference/lean-ga-proof-architecture.md` still describes the files.

## Context

Read first: `tasks/reference/lean-ga-proof-architecture.md` ("Coordinates only when needed", "Structural proofs
over brute `ring`", "Build discipline"). A full `lake build` takes about 20 minutes; edit one module at a time
with `lake env lean proofs/GacalcProofs/<File>.lean` from `proofs/`.

## Items

1. **Three coordinate leaves of `ProjectionRotation3D.lean`.** `inplane_perp_reject`, `versor_mul_project_eq` and
   `versor_mul_reject_comm` still compute on coordinates with `field_simp; ring`. They mention `f` and `t`
   themselves, not just the plane, so they do not generalize to an arbitrary bivector the way `project_perp_reject`
   did. Try a structural proof (the in-plane product `P f t` is in the plane because the plane bivector is `f ∧ t`)
   and keep the coordinate body only if the structural one needs the unavailable `IsBivector`-closure lemmas.
2. **`hrn` (`|R|² ≠ 0`) in `projRotation_eq_sandwich`.** It follows from the nondegenerate plane, but the closed
   form `normSq_versorFromVectors` lives in `Rotor.lean`, which imports `ProjectionRotation3D.lean`. Move
   `normSq_versorFromVectors_eq`/`normSq_versorFromVectors` (𝒢₃) upstream, derive `hrn`, and drop `hr` from the
   `Rotor` theorems that carry it.
3. **`Bootstrap2D` against `RotateFromTo2D`.** `Bootstrap2D`'s `mul_proj_eq_dot`, `mul_reject_eq_wedge` and neighbours
   restate part of what `RotateFromTo2D` and `Projection2D` already give; decide which file owns each and delete the
   duplicate, citing the survivor from `book/docs/bootstrap-*.rst`.
4. **`G2.lean`'s late sections.** `G1` and the early `G2` follow the teaching order; the duals and reverse sections of
   `G2.lean` were not regrouped against `G3.lean` and `tasks/reference/algebra-teaching-order.md`.
5. **The Python `exp` docstring and the generator.** `MultiVectorBase.exp`'s docstring states that `exp(−(θ/2)*i)` is the
   rotor but does not name the Lean theorem `rotor_eq_expBivector`; add the citation where the docstring is generated
   (`tools/gen_specialized.py`'s custom-docs table), then `make generate`, `make check-generated`, `make check-regions`.

## Open questions

None.
