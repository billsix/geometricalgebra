# Speed up the three slow 𝒢₃ proofs in `ProjectionRotation3D.lean`

**Status:** proposed — optional, needs go-ahead **Priority:** 8 **Difficulty:** 6
**Created:** 2026-11-25 (William Emerison Six <billsix@gmail.com>)
**Source:** `tasks/archive/2026/11/25/lean-first-build-time.md` (the measurement).

## BLUF

A clean `make lean` build takes 2 min 42 s on 24 cores, and 119 s of that is `proofs/GacalcProofs/ProjectionRotation3D.lean`, because three theorems end in a large `field_simp`. Done = each of the three elaborates in well under its current time (a few seconds), with `lake build --wfail` and the axioms gate still green.

## Context

- Read first: `tasks/reference/lean-for-gacalc.md` ("Build time (measured 2026-11-25)"), `tasks/reference/lean-ga-proof-architecture.md`.
- The three theorems and their elaboration times (2026-11-25): `inplane_perp_reject` about 147 s, `versor_mul_project_eq` about 44 s, `versor_mul_reject_comm` about 39 s. Each has `set_option maxHeartbeats 8000000` and an `obtain ⟨a1, …, rfl⟩` coordinate unfolding, then `field_simp [hn]; ring`.
- Profile with `lake env lean -Dtrace.profiler=true -Dtrace.profiler.threshold=4000 GacalcProofs/ProjectionRotation3D.lean`.
- Tried and rejected: `generalize` of the normalized denominator `N` before `field_simp`; the identity needs `N`'s definition, so the polynomial goal is false with `N` free.
- Options: a structural proof from the in-plane facts (`project_perp_reject`, a vector in the plane of `f∧t` stays in it after `* f * t`); or avoid `field_simp` by writing the goal as `N⁻¹ * polynomial` and closing it with `linear_combination` against `N * N⁻¹ = 1`, with the quotient computed by a polynomial division in sympy.
