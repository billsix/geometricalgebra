# Lean proof — the 3D sandwich rotates correctly in its plane (matrix-free)

**Part of:** `tasks/investigate-lean-proofs-for-ga.md` (the Lean-proofs umbrella)
**Status:** DONE 2026-09-29 (William Emerison Six <billsix@gmail.com>) — matrix-free reframing
**Priority:** 6 · **Difficulty:** 7

## BLUF

Proved, for the actual a→b rotation `R = versorFromVectors a b` in 𝒢₃, the maintainer's three goals —
**matrix-free, no angle computed**: (1) it rotates in the plane defined by a→b; (2) it rotates the
*oriented* angle correctly; (3) components perpendicular to the plane are unchanged. Landed in
`proofs/GacalcProofs/RotateComponents.lean` + `Sandwich.lean`, `make lean` green.

## What landed (the three goals)

For `R = versorFromVectors a b`:

- **Goal 1 — rotates in the a→b plane.** `sandwich_carries_from_to` (`R a R⁻¹ = (|a|/|b|)·b`, a↦b) +
  `plane_eq_wedge` (the plane is `a∧b`) + `rotation_fixes_plane_bivector` (`sandwich R (b∧a) = b∧a` —
  the plane, oriented, is invariant).
- **Goal 2 — rotates the oriented angle correctly.** The sandwich is an **oriented isometry**:
  `rotation_preserves_dot` (`(R u R⁻¹)·(R v R⁻¹) = u·v`, angle magnitude) + `rotation_fixes_plane_bivector`
  (orientation preserved — a rotation, not a reflection). With `sandwich_carries_from_to` (a↦b), an
  oriented isometry carrying a to b is exactly the rotation by the oriented angle from a to b.
- **Goal 3 — perpendicular components unchanged.** `rotation_fixes_normal` — the axis `b×a = dual(b∧a)`
  (⊥ both a and b) is fixed.

Supporting (in `Sandwich.lean`): `sandwich_add`/`sandwich_smul` (linearity), `sandwich_ahat` (â↦b̂),
`versorFromVectors_eq_evenVersor` (the a→b versor is an even versor — the bridge that lets the general
`evenVersor` isometry/fixed-bivector/fixed-normal results apply to the actual rotation),
`sandwich_fixes_own_bivector` (a rotation fixes its own plane bivector), `sandwich_fixes_own_normal`
(a rotation fixes the normal to its plane).

## Decisions / notes

- **Matrix-free reframing (maintainer, 2026-09-29):** the goal is the three geometric properties above,
  NOT a rotation matrix. This made the double-angle "second column" and the `{â, r̂}` rotation-matrix
  theorem **unnecessary** — dropped. The Stage-1 `sandwich_ahat` (â↦b̂) is kept as the concrete
  "carries the frame vector," but the full 2×2 matrix / `c²+s²=1` route was not needed.
- **Frame/orientation decisions (kept for context):** orthonormal `{â, r̂}`, `sin θ ≥ 0` oriented by
  `a∧b`. In the matrix-free formulation these live implicitly in `rotation_fixes_plane_bivector`
  (orientation `a∧b`) rather than in explicit `sin`/`cos` symbols.
- Possible future strengthening (not needed for the goals): the sandwich preserves the wedge of two
  in-plane vectors (a sharper "oriented angle between any two vectors is preserved"); the plane
  bivector being fixed already gives the orientation content.
