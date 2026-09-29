# Lean proof — the half-angle versor-from-two-vectors technique, shown in 2D

**Part of:** `tasks/investigate-lean-proofs-for-ga.md` (the Lean-proofs umbrella)
**Depends on:** `proofs/GacalcProofs/G2.lean` (the from-scratch 𝒢₂; done) and the 3D angle-free
versor already landed in `proofs/GacalcProofs/Rotation3D.lean` (`mag`/`bisector`/`versorFromVectors`/
`versor_mul_from_eq_bisector`) — this is the 2D transcription of that same technique.
**Related:** `tasks/lean-proof-rotation-from-scratch.md` (holds the 3D sandwich and the reduce-to-2D
plan; 𝒢₂ already has the *angle-parameterized* `sandwich_versor`).

**Status:** in-progress — the identity + the 𝒢₂ sandwich isometry landed 2026-09-29
(`proofs/GacalcProofs/Versor2D.lean`, `Sandwich.lean`, `make lean` green); the from-vectors
"carries a to b" capstone remains (same short chain as the 3D case).
**Priority:** 7
**Difficulty:** 4

## BLUF

Show the maintainer's **angle-free, versor-from-two-vectors** rotation technique in **𝒢₂**, as a
pedagogical warm-up. It is **not necessary** in 2D — 𝒢₂ already has the angle-parameterized
`sandwich_versor` (`R = cos(θ/2)·1 − sin(θ/2)·e₁₂`, proved to rotate by θ) — but proving the *same*
construction the 3D case uses (build `R = b·a + |a||b|` straight from two vectors, no trig; `R·a`
recovers the bisector; the sandwich `R v R⁻¹` carries `a` to `b`) makes the technique legible in the
simplest setting first. Then in 3D we see the identical construction, which *additionally* leaves
components orthogonal to the plane of rotation unchanged — so 2D isolates "the rotation itself" and
3D adds only "and the orthogonal complement is fixed." "Done" = the 𝒢₂ analogues of the 3D lemmas,
`make lean` green, with the 2D-vs-3D correspondence written in the module docstring.

## Context — read first

- **The 3D version is already landed and is the template** (`proofs/GacalcProofs/Rotation3D.lean`,
  2026-09-29): `bisector fromV toV = |to|·from + |from|·to` (the half-angle *vector* `h`),
  `versorFromVectors fromV toV = to·from + |from||to|` (the half-angle *versor* `R`), and
  **`versor_mul_from_eq_bisector`**: `R·a = |a|·h`. The only analytic fact is `mag_sq_vec` (`|a|²=a·a`
  via `Real.sq_sqrt`); everything else is `ring`. Transcribe these to 𝒢₂ — the 𝒢₂ struct + product
  are in `proofs/GacalcProofs/G2.lean`.
- **The gacalc source** (`base.py` `versor_from_vectors`) is dimension-agnostic — `R = to·from +
  |from||to|`, `h = |to|·from + |from|·to` — so the 2D and 3D constructions are literally the same
  formula; only the algebra (𝒢₂ vs 𝒢₃) differs.
- **Terminology:** versor, not rotor (un-normalized; applied by the scale-invariant `R v R⁻¹`).

## The 2D-vs-3D pedagogical point (why this task exists)

- In **𝒢₂** the plane of rotation is the *whole space* — every vector is in-plane, so there is **no
  orthogonal complement** and nothing is "left fixed." The sandwich is *purely* the rotation. This is
  the cleanest place to see `R·a = |a|·h` and `R v R⁻¹ : a ↦ (scaled) b`.
- In **𝒢₃** the *same* `R = b·a + |a||b|` acts in the `a∧b` plane and, additionally, **fixes any
  component along the normal `dual(a∧b)`** (it commutes with the plane bivector). So the 3D story is
  "the 2D rotation, embedded in a plane, with the orthogonal complement untouched."
- Landing 2D first means the 3D sandwich reads as a *recognition* ("same construction") rather than a
  new idea — matching the maintainer's intent (2026-09-29).

## Plan

- [x] **𝒢₂ `dot`/`mag`/`bisector`/`versorFromVectors`** (2026-09-29, `Versor2D.lean`).
- [x] **`mag_sq_vec` (2D)** — `|a|² = a₁² + a₂²` via `Real.sq_sqrt` (`Versor2D.lean`).
- [x] **`versor_mul_from_eq_bisector` (2D)** — `R·a = |a|·h` (`Versor2D.lean`), same proof shape as 3D.
- [x] **The 𝒢₂ sandwich is an isometry** (`Sandwich.lean`, 2026-09-29): `normSq`/`inverse`/`sandwich` +
      `evenVersor` (the even subalgebra ≅ ℂ), and `sandwich_preserves_dot` / `sandwich_preserves_normSq_vec`
      — a general even versor with `|R|²≠0` preserves dot, length, and angles. (This is the "it's a
      rotation" content; in 2D the whole space is the plane, so there is nothing orthogonal to fix.)
- [ ] **The from-vectors "carries a to b" capstone** — `R a R⁻¹ = (|a|/|b|)·b` in 𝒢₂, the same short
      chain documented in `tasks/lean-proof-rotation-from-scratch.md` (needs `smul_smul`,
      `versorFromVectors_mul_reverse`, `versorFromVectors_mul_inverse`, then `R a = |a|h`, `b R = |b|h`).
      Do the 3D capstone first (or together) — the 𝒢₂ and 𝒢₃ proofs are structurally identical.
- [x] Module docstring states the 2D-vs-3D correspondence; `proofs/README.md` updated.
- [x] `make lean` green (for what's landed).

## Open questions

1. State the 2D sandwich as "carries `a` to a *positive scalar multiple* of `b`" (avoids needing
    `|a|=|b|`), or normalize inputs to unit vectors for a cleaner `a ↦ b`? (Recommend the scalar-multiple
    form — it matches the scale-invariant `R v R⁻¹` and needs no unit hypothesis.)
