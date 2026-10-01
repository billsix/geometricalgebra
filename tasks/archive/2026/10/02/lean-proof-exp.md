# Lean proof — exponential map (`exp`)

**Part of:** `tasks/investigate-lean-proofs-for-ga.md`
**From:** `tasks/archive/2026/10/01/lean-coverage-gap-audit.md` (the coverage-map gap audit)

**Status:** DONE 2026-10-02 — `proofs/GacalcProofs/Exp.lean` (G2 + G3): `expBivector`/`expBivector12`
(the closed form `cos θ·1 + sin θ·e₁₂` for the unit-plane bivector `θ·e₁₂`, `(e₁₂)² = −1`); proved
`*_eq_evenVersor` (exp = the even versor, so the rotor/sandwich layer applies) and `normSq_* = 1`
(**exp of a bivector is a unit versor — a rotor**, via `cos²+sin²=1`). `make lean` green, sorry-free.
**General case now proved too (2026-10-02):** `expBivectorGeneral p q r = cos|B|·1 + (sin|B|/|B|)·B`
for any nonzero 𝒢₃ bivector `B = p·e₁₂ + q·e₁₃ + r·e₂₃` (every 𝒢₃ bivector is simple, so this is the
full case), with `normSq_expBivectorGeneral = 1` (`|B|² = p²+q²+r²`). Fully done.
**Priority:** 7
**Difficulty:** 6

## BLUF

Prove, from scratch in Lean, gacalc's exponential map `exp` (`base.py:1842`): for a negative-square
blade `A` (a bivector, or the 𝒢₃ pseudoscalar, `A² < 0`), `exp(A) = cos|A| + sin|A|·Â` and **the exp
of a bivector is a rotor** (a unit even versor). No Lean theorem covers it. "Done" = the closed-form
identity + the "result is a unit versor" theorem (2D + 3D bivector cases), `make lean` green.

## Approach

gacalc does **not** use a power series — `exp` is the closed form `cos|A| + sin|A|·Â` for `A² < 0`
(the vector/positive-square hyperbolic branch is rejected with `ValueError`, so Lean need only cover
the negative-square case). Define `exp` on a bivector of `G2`/`G3` by that closed form and prove:
(a) it is a unit versor (`normSq (exp A) = 1`) — the rotor property — using `Â² = −1` (the unit
bivector squares to −1, cf. `I_sq`/`e_12_sq`) and `cos²+sin² = 1` (`cos_sq_add_sin_sq`, already in
`Trig.lean`); and (b) it agrees with the `evenVersor s c` form so the whole sandwich/rotation layer
applies by instantiation (via `versorFromVectors_eq_evenVersor`-style bridging). The transcendental
`cos`/`sin` are Mathlib's; the GA content is the `Â² = −1` reduction. Keep nondegeneracy as
`normSq ≠ 0` per convention. See `tasks/reference/unit-bivector-and-rotors.md` and `design-decisions.md`
for the exp semantics.

See the coverage map in `tasks/reference/lean-ga-proof-architecture.md`.
