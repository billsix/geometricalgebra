# Lean proof — the 3D sandwich rotates in-plane components correctly (sin/cos from dot & wedge)

**Part of:** `tasks/investigate-lean-proofs-for-ga.md` (the Lean-proofs umbrella)
**Depends on:** the completed 3D versor sandwich — `proofs/GacalcProofs/Sandwich.lean`
(`sandwich_carries_from_to`, `sandwich_preserves_dot`, `sandwich_fixes_orthogonal`,
`sandwich_plane_invariant`), `Rotation3D.lean`, `Projection.lean` (`plane_eq_wedge`, `reject_perp`),
and `Lagrange.lean` (`lagrange_3d`: `|a|²|b|² = (a·b)² + |a∧b|²`).
**Extends:** the maintainer's request (2026-09-29) — go beyond "`R` carries `a` to `b`" to "the sandwich
rotates an arbitrary in-plane vector by the correct angle, with sin/cos taken from `a·b` and `a∧b`,
never computing the angle."

**Status:** in-progress — decisions made (2026-09-29): orthonormal `{â, r̂}`, `sin θ ≥ 0` oriented by
`a∧b`, prove the explicit rotated-vector equation with `c²+s²=1` a corollary of `lagrange_3d`. **Stage 1
landed** (`RotateComponents.lean`, `make lean` green): sandwich linearity (`sandwich_add`/`sandwich_smul`
in `Sandwich.lean`) + **`sandwich_ahat`** (`â ↦ b̂`, the first column). Stages 2–3 remain — see the two
obstacles below.
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

## Plan / progress

- [x] **Stage 1 (landed 2026-09-29):** sandwich linearity (`sandwich_add`, `sandwich_smul`) and
      **`sandwich_ahat`** (`sandwich R â = b̂`, the first column). Since `b̂ = cos θ·â + sin θ·r̂`, this
      already exhibits `â`'s image with plane components `(cos θ, sin θ)`.
- [ ] **Stage 2 — `c² + s² = 1` and the decomposition `b̂ = c·â + s·r̂`.** Obstacle: needs the
      **magnitude of derived vectors** — `mag(b − proj_a b)` (not a `vec` literal, so `mag_sq_vec`
      doesn't apply) and, for the "sin from the wedge" form, the **bivector magnitude** `|a∧b|` (where
      `dot B B < 0`, so `mag = √(dot ..)` is the wrong sign). Fix: add a small layer — `mag_sq` for a
      general grade-1 vector (`(mag v)² = dot v v` given `dot v v ≥ 0`), and a bivector norm
      `bmag B = √(B.c12² + B.c13² + B.c23²)`, then `|a∧b| = |a|·|r|` (from `lagrange_3d`) ties `s = |r|/|b|`
      to `s = |a∧b|/(|a||b|)`. With those, `c²+s² = ((a·b)²+|a∧b|²)/(|a|²|b|²) = 1` by `lagrange_3d`.
- [ ] **Stage 3 — the second column `sandwich R r̂ = −s·â + c·r̂` and the full theorem.** The deep part:
      `r̂` is `â` turned `+90°`, so its image is `b̂` turned `+90°` — equivalently `sandwich R b̂ =
      sandwich (R²) â` (via `sandwich_comp`, already proved), which brings in the **double angle**
      `cos 2θ = 2c²−1`, `sin 2θ = 2cs`. From `sandwich R b̂ = cos2θ·â + sin2θ·r̂` and `r̂ = (b̂ − c·â)/s`
      (linearity), `sandwich R r̂ = −s·â + c·r̂` falls out. Then the main theorem
      `sandwich R (s₁â + s₂r̂) = (s₁c − s₂s)â + (s₁s + s₂c)r̂` is linearity + collecting.
      Alternative route (avoids the explicit double angle): prove `sandwich` preserves the **wedge**
      (orientation-preserving, like `sandwich_preserves_dot`) and pin `sandwich R r̂` by
      unit + ⊥ b̂ + in-plane + orientation — but that needs a 2D "these four facts determine the vector"
      lemma. The double-angle route is more direct.
- [ ] (Optional, Q3) the rotation-matrix corollary: orthogonal, det 1 (from `c²+s²=1`).
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
