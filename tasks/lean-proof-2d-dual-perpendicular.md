# Lean proof — the dual of a vector is perpendicular to it (2D)

**Part of:** `tasks/investigate-lean-proofs-for-ga.md`
**Depends on:** nothing new — the existing `proofs/GacalcProofs/G2.lean` already has everything
(`mul`, `e_12`, `inner_product`/dot). **Doable now** (no `G3` needed).
**Related:** `tasks/lean-proof-projection.md` — the 3D "dual of a bivector ⊥ the plane" step is the
3D analogue; this 2D case is its warm-up. Also the 𝒢₂ quarter turn (`g2.rotate_90_degrees`, `v * e_12`).

**Status:** proposed — ready (small, self-contained; no prerequisites)
**Priority:** 6
**Difficulty:** 2

## BLUF

Prove in 𝒢₂ that the **dual of a vector is perpendicular to that vector**: for `v` a grade-1 vector,
`dual(v) · v = 0`, where `dual(v) = v · I₂⁻¹` (equivalently `v * I₂`, up to sign; `I₂ = e₁e₂`). "Done"
= the lemma proved in `proofs/GacalcProofs/G2.lean` (or a small `Dual.lean`), `make lean` green,
matching gacalc's `dual` convention (`base.py:1217`).

## Context — read first

- In 2D the dual of a vector is again a **vector** (grade 1) — it is the 90° rotation of `v`
  (`v * e_12`, the quarter turn). Concretely, for `v = x·e₁ + y·e₂`:
  `v * e₁₂ = x(e₁e₁₂) + y(e₂e₁₂) = x·e₂ − y·e₁ = (−y)·e₁ + x·e₂`, and
  `(v * e₁₂) · v = (−y)(x) + (x)(y) = 0`. So the dual is perpendicular. (`I₂⁻¹ = −I₂` since `I₂² = −1`,
  so `v · I₂⁻¹` is the same line up to sign — still perpendicular.)
- Contrast with 3D, where the dual of a *vector* is a *bivector* and the dual of a *bivector* is a
  vector (the plane normal) — that 3D case lives in `tasks/lean-proof-projection.md`. This 2D lemma is
  the grade-1↔grade-1 warm-up.
- Read `tasks/reference/lean-for-gacalc.md`; the G2 build style (basis blades as genuine `G2` elements)
  is in `proofs/GacalcProofs/G2.lean`.

## Plan

- [ ] Define `dual (v : G2) : G2` matching gacalc (`v · I₂⁻¹`, or `mul v e_12` with the sign noted) —
      or state the lemma directly on `mul v e_12`.
- [ ] Prove `(dual v) · v = 0` for a grade-1 `v = G2.vec x y` — expand `mul`/dot; `ring` closes it
      (no trig, no Pythagorean identity needed — it's a polynomial identity `−xy + xy = 0`).
- [ ] (Optional) note the tie to `versor`/the quarter turn: `dual(v)` is `v` rotated 90°.
- [ ] `make lean` green; mention in `proofs/README.md`.

## Open questions

1. Match gacalc's exact `dual` sign/normalization (`v · I₂⁻¹` vs `v · I₂`) — pin from `base.py:1217`
   when implementing; the perpendicularity holds either way, so this only fixes the statement's form.
