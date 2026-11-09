# Lean proofs — inverses in 𝒢₂ and 𝒢₃: is there a general formula, and what subset to prove?

**Completed:** 2026-09-29 (William Emerison Six <billsix@gmail.com>)
**Part of:** `tasks/archive/2026/10/04/investigate-lean-proofs-for-ga.md` (the Lean-proofs umbrella)
**Related:** `tasks/archive/2026/09/30/lean-proofs-make-coordinate-free.md` (added
`mul_vec_inverse_self`, the vector case).

## Question

The maintainer asked: is there a single general inverse formula for an arbitrary multivector that we
can state and prove in Lean — and if not, say so — and which subset of cases (vector, versor,
bivector, trivector, …) is worth proving? `A⁻¹` means `A A⁻¹ = A⁻¹ A = 1`.

The Python library used one formula for everything, `A⁻¹ = Ã / |A|²` (`base.py` `inverse`, with
`|A|² = ⟨A Ã⟩`), and its docstring and `CLAUDE.md` "Assessment / known issues" #2 flagged it "not sure
if I'm doing this correctly". Lean had the same `inverse` def for both algebras in `Sandwich.lean`
(`smul (1 / normSq a) (reverse a)`), with `A A⁻¹ = 1` proved only for a vector
(`mul_vec_inverse_self`, `a·a ≠ 0`) and the from-vectors versor (`versorFromVectors_mul_inverse`).

## Findings

- **`Ã/|A|²` is not general.** `A (Ã/|A|²) = A Ã / |A|²`, which is `1` iff `A Ã = |A|² * 1`, i.e. iff
  `A Ã` is a scalar: true for blades and versors, false for a mixed-grade multivector. Confirmed on
  paper.
- **A general formula exists in low dimensions** (Hitzer & Sangwine, "Multivector and multivector
  matrix inverses in real Clifford algebras", 2017), built from the grade involutions (reverse `Ã`,
  grade involution `Â`, Clifford conjugation `Ā`) so that the denominator collapses to a scalar — for
  𝒢₂ of the shape `Ā / (A Ā)`, for 𝒢₃ `(Â Ã Ā) / (A Â Ã Ā)`. These were leads to be derived or checked
  against the source, not copied; that work moved to `tasks/lean-general-multivector-inverse.md`.

## Decision

**Prove the per-grade subset** — what the library actually inverts — and leave the general inverse as
the spun-out follow-on. The alternative raised (prove the correct general inverse even where it
diverges from Python, filing a Python fix) went to that follow-on task.

## What was done

- **Proved in Lean** (`proofs/GacalcProofs/`), all `A A⁻¹ = 1`: vector (`mul_vec_inverse_self`),
  versor (`versorFromVectors_mul_inverse`), **bivector (`mul_biv_inverse_self`)**, **trivector
  (`mul_triv_inverse_self`)** — every grade the library's `inverse` is validly used on, and enough for
  the coordinate-free work. Supporting leaves: `reverse_vec`, `mul_vec_self` (`a a = |a|² * 1`),
  `normSq_reverse_sandwich`.
- **Python:** `base.py` `inverse`'s docstring was tightened to state the supported subset
  (blades/versors) instead of "not sure", and `CLAUDE.md`'s known-issue note was updated. A runtime
  guard against mixed-grade input was left undecided here (cost on the versor hot path, symbolic-zero
  detection, a published-API break).
