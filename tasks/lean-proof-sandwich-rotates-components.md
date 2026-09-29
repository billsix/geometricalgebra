# Lean proof — the 3D sandwich rotates in-plane components correctly (sin/cos from dot & wedge)

**Part of:** `tasks/investigate-lean-proofs-for-ga.md` (the Lean-proofs umbrella)
**Depends on:** the completed 3D versor sandwich — `proofs/GacalcProofs/Sandwich.lean`
(`sandwich_carries_from_to`, `sandwich_preserves_dot`, `sandwich_fixes_orthogonal`,
`sandwich_plane_invariant`), `Rotation3D.lean`, `Projection.lean` (`plane_eq_wedge`, `reject_perp`),
and `Lagrange.lean` (`lagrange_3d`: `|a|²|b|² = (a·b)² + |a∧b|²`).
**Extends:** the maintainer's request (2026-09-29) — go beyond "`R` carries `a` to `b`" to "the sandwich
rotates an arbitrary in-plane vector by the correct angle, with sin/cos taken from `a·b` and `a∧b`,
never computing the angle."

**Status:** proposed — needs go-ahead (open questions below) (2026-09-29, William Emerison Six <billsix@gmail.com>)
**Priority:** 6
**Difficulty:** 7

## BLUF

Prove that the from-vectors versor sandwich `R v R⁻¹` **rotates a general in-plane vector correctly**:
for a vector `v = s₁·â + s₂·r̂` written in the orthonormal frame of the rotation plane
(`â = a/|a|`, `r̂ = (b − proj_a b)/|b − proj_a b|`), `sandwich R v = (s₁c − s₂s)·â + (s₁s + s₂c)·r̂`,
where `c = cos θ = (a·b)/(|a||b|)` and `s = sin θ = |a∧b|/(|a||b|)` come straight from the **dot and
wedge** of `a` and `b` — **the angle θ is never computed**. `c² + s² = 1` is a corollary of the
already-proved `lagrange_3d`. This is the full "reduce-to-2D" statement: the 3D sandwich restricted to
its plane IS the 2D rotation matrix, with entries from the invariant dot/wedge. "Done" = that equation
proved in `G3`, `make lean` green.

## Context / the math (research 2026-09-29)

- The plane is `a ∧ b`; `{a, r}` with `r = b − proj_a b` is an *orthogonal* frame of it (`reject_perp`),
  and `a (b − proj_a b) = a ∧ b` (`plane_eq_wedge`). Normalize to `{â, r̂}`.
- **sin/cos without the angle.** `cos θ = (a·b)/(|a||b|)`; `sin θ = |a∧b|/(|a||b|)`. `lagrange_3d`
  gives `(a·b)² + |a∧b|² = |a|²|b|²`, i.e. `c² + s² = 1` — no arctan, no trig functions, just the dot
  and the wedge magnitude. The frame orientation (`r̂` = `+90°` image of `â`) makes `sin θ ≥ 0`, and
  `b̂ = c·â + s·r̂` (that is `sandwich_carries_from_to` for the basis vector `â`).
- **Method.** The sandwich is linear (`R(·)R⁻¹` distributes over `+` and pulls out scalars — from
  `AlgebraLaws`), so it suffices to compute `sandwich R â` and `sandwich R r̂` and combine:
  `sandwich R â = c·â + s·r̂` (= `b̂`, from `sandwich_carries_from_to`), and
  `sandwich R r̂ = −s·â + c·r̂` (the perpendicular in-plane image). Then
  `sandwich R (s₁â + s₂r̂) = (s₁c − s₂s)â + (s₁s + s₂c)r̂`.

## Plan (pending the open-question answers)

- [ ] Define `c`, `s` from `a·b` and `|a∧b|` (dot + wedge), and prove `c² + s² = 1` from `lagrange_3d`.
- [ ] `sandwich R r̂ = −s·â + c·r̂` (the perpendicular basis image) — the new piece beyond
      `sandwich_carries_from_to` (which gives `sandwich R â = b̂ = c·â + s·r̂`).
- [ ] Linearity of the sandwich (`sandwich R (add u v) = add (sandwich R u)(sandwich R v)`,
      `sandwich R (smul k v) = smul k (sandwich R v)`) — from `mul_add`/`add_mul`/`smul_mul`/`mul_smul`.
- [ ] The main theorem: `sandwich R (s₁â + s₂r̂) = (s₁c − s₂s)â + (s₁s + s₂c)r̂`.
- [ ] (Optional, Q3) the rotation-matrix corollary: orthogonal, det 1.
- [ ] `make lean` green; `proofs/README.md` updated.

## Open questions (maintainer)

1. **Frame — orthonormal `{â, r̂}` or the raw `{a, r}`?** The clean cos/sin rotation matrix only exists
    in the orthonormal frame (raw `{a, r}` carries scale factors since `|a| ≠ |r|`). (Rec: orthonormal
    `{â, r̂}` — accept the `√` from normalization; that is where sin/cos live.)
2. **Sign of sin** — orient by `a∧b` so `r̂` is the `+90°` image of `â` and `sin θ ≥ 0`? (Rec: yes;
    `r = b − proj_a b` already points to `b`'s side.)
3. **What "correctly" asserts** — the explicit rotated-vector equation (Rec), and/or the
    orthogonal/det-1 rotation-matrix corollary with `c²+s²=1` from `lagrange_3d` (Rec: the equation
    first; the matrix facts as a short corollary).
