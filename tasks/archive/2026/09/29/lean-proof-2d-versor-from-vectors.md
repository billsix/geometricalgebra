# Lean proof — the half-angle versor-from-two-vectors technique, shown in 2D

**Part of:** `tasks/investigate-lean-proofs-for-ga.md` (the Lean-proofs umbrella)
**Status:** DONE 2026-09-29 (William Emerison Six <billsix@gmail.com>)
**Priority:** 7 · **Difficulty:** 4

## BLUF

Showed the maintainer's angle-free, versor-from-two-vectors rotation technique in **𝒢₂**, the
pedagogical warm-up for the 3D sandwich — the *same* construction in the simplest algebra. Landed in
`proofs/GacalcProofs/Versor2D.lean` + `Sandwich.lean`, `make lean` green.

## What landed

- **`Versor2D.lean`:** `dot`/`mag`/`bisector`/`versorFromVectors` for 𝒢₂, `mag_sq_vec`, and the
  identity `versor_mul_from_eq_bisector` (`R·a = |a|·h`) + the companion `from_mul_versor_eq_bisector`
  (`b·R = |b|·h`).
- **`Sandwich.lean` (G2):** `normSq`/`inverse`/`sandwich`/`evenVersor`, the isometry
  (`sandwich_preserves_dot`/`_normSq_vec` — preserves dot, length, angles), `versorFromVectors_mul_reverse`
  (`R R̃ = |R|²·1`), and the capstone **`sandwich_carries_from_to`**: `R a R⁻¹ = (|a|/|b|)·b` — the
  versor built from `a, b` carries `a` to `b`, angle-free.

## The 2D-vs-3D point (delivered)

In 𝒢₂ the plane of rotation is the whole space — no orthogonal complement, so the sandwich is purely
the rotation. In 𝒢₃ (`Rotation3D.lean` + `Sandwich.lean`) the *identical* construction acts in the
`a∧b` plane and additionally fixes the orthogonal axis (`sandwich_fixes_orthogonal`) and keeps in-plane
vectors in-plane (`sandwich_plane_invariant`). So the 2D and 3D `sandwich_carries_from_to` proofs are
structurally identical; 3D only adds "which plane, leave the orthogonal complement fixed."

## Resolved

- **Open Q1 (carries `a` to a positive multiple of `b` vs. unit-normalized `a ↦ b`):** proved the
  **scalar-multiple** form `R a R⁻¹ = (|a|/|b|)·b` — matches the scale-invariant `R v R⁻¹`, no unit
  hypothesis (just `|b| ≠ 0`, `|R|² ≠ 0`).
