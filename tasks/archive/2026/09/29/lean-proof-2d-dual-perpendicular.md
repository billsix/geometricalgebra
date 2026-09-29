# Lean proof — the dual of a vector is perpendicular to it (2D) [DONE]

**Part of:** `tasks/investigate-lean-proofs-for-ga.md`
**Status:** DONE 2026-09-29 (`make lean` green). Archived.

## What was done

Proved in 𝒢₂ (`proofs/GacalcProofs/G2.lean`) that the dual of a vector is perpendicular to it:

- `I_inv = ⟨0,0,0,-1⟩ = −e₁₂` — the inverse unit pseudoscalar (`I₂² = −1`, so `I₂⁻¹ = −I₂`), with
  `I_mul_I_inv : mul I I_inv = one` confirming it.
- `dual a := mul a I_inv` — the dual `A · I₂⁻¹`, matching gacalc's `dual` (base.py:1217).
- `dual_vec : dual (vec x y) = vec y (-x)` — the dual of a vector is the −90° rotation.
- `dual_vec_perp : (mul (dual (vec x y)) (vec x y)).s = 0` — the perpendicularity result: the dot of
  `dual v` and `v` (the scalar part of their geometric product, per `dot_eq_coord_sum`) is zero, since
  `dual(v) = (y, −x)` gives `xy − xy = 0`. One-line `simp` + `ring`; no trig, no Pythagorean identity.

Verified by `make lean`. No adhoc scripts (direct edits in `G2.lean`); noted in `proofs/README.md`.

## Why it mattered

The grade-1 ↔ grade-1 warm-up for the 3D "dual of a bivector ⊥ the plane" step in
`tasks/lean-proof-projection.md`. gacalc's `dual` convention (`A · I⁻¹`) was matched exactly, so this
doubles as a small second-oracle check of that operation in 2D.
