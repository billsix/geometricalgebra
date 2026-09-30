# Lean proofs — the GENERAL multivector inverse for 𝒢₂ and 𝒢₃

**Part of:** `tasks/investigate-lean-proofs-for-ga.md` (the Lean-proofs umbrella)
**Grew out of:** `tasks/archive/2026/09/30/lean-inverses-g2-g3.md` (the investigation; the per-blade subset is done there).

**Status:** proposed — needs go-ahead (2026-09-29, William Emerison Six <billsix@gmail.com>)
**Priority:** 7
**Difficulty:** 7

## BLUF

Add (and prove) a **general multivector inverse** for 𝒢₂ and 𝒢₃ — one that inverts *any* invertible
element, not just a blade or versor. The current formula `A⁻¹ = Ã/|A|²` (Python `base.py:inverse`, Lean
`Sandwich.lean:inverse`) is a correct inverse **only when `A Ã` is a scalar** (blades + versors); for a
mixed-grade multivector it silently returns a wrong answer. The per-blade cases (vector, versor, bivector,
trivector) are already proved in Lean and suffice for the coordinate-free work — this task is the stretch
goal of the *general* case, deferred until wanted. "Done" = the general closed form derived/verified and a
`A A⁻¹ = 1` proof for a general element in each algebra, plus the Python reconciliation decided.

## Context (cold-start)

- **Why the current formula isn't general:** `A (Ã/|A|²) = A Ã / |A|²`, which is `1` only if `A Ã = |A|²·1`
  — i.e. `A Ã` has no non-scalar part. Holds for blades and versors, not general mixed-grade `A`.
- **The general low-dim closed form (verify against the source):** Hitzer & Sangwine, "Multivector and
  multivector matrix inverses in real Clifford algebras" (2017). Built from the grade involutions —
  reverse `Ã`, grade involution `Â`, Clifford conjugation `Ā` — chosen so the denominator collapses to a
  scalar. Leads to confirm, not copy:
  - 𝒢₂: `A⁻¹ = Ā / (A Ā)`, denominator scalar.
  - 𝒢₃: `A⁻¹ = (Â Ã Ā) / (A Â Ã Ā)` (three involutions), denominator scalar.
  The codebase has `reverse`; **grade involution and Clifford conjugation would need adding** (Python and
  Lean) — cheap (per-grade sign flips), but they are new primitives.
- **Already done (the subset, do NOT redo here):** Lean `A A⁻¹ = 1` for vector (`mul_vec_inverse_self`),
  versor (`versorFromVectors_mul_inverse`), bivector (`mul_biv_inverse_self`), trivector
  (`mul_triv_inverse_self`) — all in `proofs/GacalcProofs/`.

## Plan (when picked up)

1. Verify the Hitzer–Sangwine forms for 𝒢₂/𝒢₃ against the source; write the exact formula.
2. Add the missing involutions (grade involution, Clifford conjugation) to Lean (and Python if the general
   inverse ships there) as per-grade sign-flip defs, with the small identities they need.
3. Prove `A A⁻¹ = 1` (and `A⁻¹ A = 1`) for a *general* `A : G2` / `A : G3` (the denominator-is-scalar step
   is the crux; likely pure `ring` once the involution product is unfolded).
4. **Python reconciliation** (this is open question 2 from `archive/2026/09/30/lean-inverses-g2-g3.md`, relevant only here):
   decide whether Python's `inverse` adopts the general formula (diverging from today's `Ã/|A|²`) or keeps
   the subset formula with the guard. If it changes, it is a **breaking change** to a published library —
   changelog entry + version bump (maintainer publishes).

## Open questions

1. Do we want the general inverse in **Python too**, or Lean-only (the machine-checked statement) with
   Python staying on the guarded subset formula? (Rec: Lean first — prove it's right — then decide Python.)
