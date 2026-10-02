# Lean proof — exponential map (`exp`)

**Part of:** `tasks/investigate-lean-proofs-for-ga.md`
**From:** `tasks/archive/2026/10/01/lean-coverage-gap-audit.md` (the coverage-map gap audit)

**Status:** DONE 2026-10-02. **Priority:** 7 **Difficulty:** 6

## Summary

gacalc's exponential map `exp` (`base.py:1842`) — the closed form `cos|A| + sin|A|·Â` for a
negative-square blade (`A² < 0`; the positive-square hyperbolic branch is rejected), not a power series —
had no Lean theorem. `proofs/GacalcProofs/Exp.lean` (G2 + G3) proved that the exp of a bivector is a
rotor: `expBivector`/`expBivector12` (the unit-plane form `cos θ·1 + sin θ·e₁₂`, `(e₁₂)² = −1`) with
`*_eq_evenVersor` (exp = the even versor, so the whole sandwich/rotation layer applies by instantiation)
and `normSq_* = 1` (unit versor, via `cos²+sin² = 1`); and the general
`expBivectorGeneral p q r = cos|B|·1 + (sin|B|/|B|)·B` for any nonzero 𝒢₃ bivector
`B = p·e₁₂ + q·e₁₃ + r·e₂₃` — every 𝒢₃ bivector is simple, so this is the full bivector case — with
`normSq_expBivectorGeneral = 1` (`|B|² = p²+q²+r²`). `make lean` green, sorry-free. The transcendental
`cos`/`sin` are Mathlib's; the GA content is the `Â² = −1` reduction (cf. `I_sq`, `cos_sq_add_sin_sq`).

Coverage map: `tasks/reference/lean-ga-proof-architecture.md`;
semantics: `tasks/reference/unit-bivector-and-rotors.md`, `design-decisions.md`.
