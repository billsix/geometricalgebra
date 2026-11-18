# Lean proofs — the GENERAL multivector inverse for 𝒢₂ and 𝒢₃

**Completed:** 2026-11-18 (William Emerison Six <billsix@gmail.com>; authorized batch
`ready-tasks-batch-2026-11-18`)
**Part of:** the Lean-proofs program (map: `tasks/reference/lean-ga-proof-architecture.md`)
**Grew out of:** `tasks/archive/2026/09/30/lean-inverses-g2-g3.md`
**Priority:** 7
**Difficulty:** 7

## Outcome

`proofs/GacalcProofs/GeneralInverse.lean` inverts every invertible element of 𝒢₂ and 𝒢₃, after
Hitzer & Sangwine (2017).

- **New sign flips:** `gradeInvolution` (`Â`, odd grades negated) and `cliffordConjugate` (`Ā`,
  grades 1 and 2 negated), with `cliffordConjugate_eq_reverse_gradeInvolution` in each algebra.
- **𝒢₂:** `A * Ā` is a scalar (`mul_cliffordConjugate`, `cliffordConjugate_mul`), so
  `generalInverse a = Ā / (A * Ā)`. On a vector it equals the existing `inverse`, which is `Ã / |A|²`
  (`generalInverse_eq_inverse_of_isVector`).
- **𝒢₃:** `N = A * Ā` has only scalar and pseudoscalar parts (`conjProduct_grades`), equals `Ā * A`,
  and commutes with `A` (`gradeInvolution_conjProduct_comm`). `N * N̂ = N₀² + N₁₂₃²` is a scalar
  (`conjProduct_mul_gradeInvolution`), so `generalInverse a = Ā * N̂ / (N * N̂)`.
- **Both algebras:** `mul_generalInverse` and `generalInverse_mul` hold whenever the scalar
  denominator is nonzero. The proofs are structural: `mul_assoc` and `smul` rewrites over four `ring`
  facts.

Before the proof, the forms were checked with gacalc on fully symbolic multivectors:
- `A * Ā` is grade 0 in 𝒢₂ and grades {0, 3} in 𝒢₃;
- `Ā * A = A * Ā`;
- `N * N̂` is grade 0.

**Python** keeps the guarded `Ã / |A|²` (decision 1). Its docstring and the `RuntimeError` message
now point at the Lean file instead of this task. So do `CLAUDE.md` known issue 2 and the reference
doc's inventory and coverage map. Whether Python adopts the general form is open. Adopting it would
change `inverse` for mixed-grade input from raising to returning a value; that would get a changelog
entry, but would not break existing callers.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-18)

1. Lean first; Python keeps the guarded blade/versor formula, and Python's adoption is decided after
   the proof.

## Not done

- No 𝒢₃ vector corollary like 𝒢₂'s. There, `N = −|a|²` and the inverse is `a * |a|² / |a|⁴`; it
  agrees with `inverse` but needs a case split at zero.
- No Python twin, since the general inverse is not implemented in Python.

## Verification

- `lake build GacalcProofs.GeneralInverse` passed.
- `proofs/check.sh` passed: full build, no `sorry`/`admit`, and the axioms gate (1104 declarations,
  only `propext`/`Classical.choice`/`Quot.sound`).
- ruff was clean on `base.py`.
