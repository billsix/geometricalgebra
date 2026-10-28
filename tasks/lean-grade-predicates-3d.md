# Lean: bring the 3D grade-pure predicate set to parity with 2D

**Status:** done — 2026-10-28. `make lean` green (8958 jobs; completeness gate OK). `G3.IsScalar` +
bridge + recognizers + the `a²`-is-scalar grade-of-result lemma added; wedge/wedge3 grade lemmas
deliberately skipped (no consumer).
**Priority:** 6
**Difficulty:** 5
**Created:** 2026-10-28 (William Emerison Six <billsix@gmail.com>)
**Updated:** 2026-10-28 (William Emerison Six <billsix@gmail.com>)

## BLUF

The 3D follow-up agreed when the 2D grade-predicate work landed. `G3.lean` had
`IsVector`/`IsBivector`/`IsTrivector` (+ `IsEvenVersor`/`IsRotor` in `Sandwich.lean`) but **no
`IsScalar`** and none of the grade-of-result lemmas 𝒢₂ gained. Added `IsScalar` to `G3` with its bridge
and recognizers, plus `isScalar_mul_self_of_isVector` (`a a` is a scalar), mirroring the 2D set.
`make lean` green.

## What was added (`proofs/GacalcProofs/G3.lean`)

In the grade-structure-predicates section (after the `IsVector` cluster, before `IsBivector`):

- `IsScalar (a : G3) : Prop` — `a.c1 = 0 ∧ a.c2 = 0 ∧ a.c3 = 0 ∧ a.c12 = 0 ∧ a.c13 = 0 ∧ a.c23 = 0 ∧
  a.c123 = 0` (only `s` nonzero).
- `eq_scalar_of_isScalar {a} (ha : IsScalar a) : a = scalar a.s` — the bridge.
- `isScalar_scalar (a : ℝ) : IsScalar (scalar a)` and `isScalar_one : IsScalar one` — recognizers.

In the object-form-facts section (after `mul_vec_self`):

- `isScalar_mul_self_of_isVector {a} (ha : IsVector a) : IsScalar (mul a a)` — the grade-of-result
  lemma (`a²` is a scalar), the 3D twin of `G2.isScalar_mul_self_of_isVector`.

## Decisions

- **Open question (scope): resolved to `IsScalar` + `a²`-is-scalar only.** The wedge/wedge3
  grade-of-result lemmas (`isBivector_wedge_of_isVector`, `isTrivector_wedge3_of_isVector`) were
  **skipped**: a tree-wide grep found **no 3D consumer** (the 2D `isBivector_wedge_of_isVector` existed
  to serve the 2D-only `v ∧ I = 0`, grade 1+2 = dim; 3D has no analogue), so adding them would be the
  speculative dead pred+lemma pairs the 2D judgment warns against.
- **Naming follows G3's own pattern, not 2D's.** G3's other grade bridges use the grade *constructor*
  (`eq_bivector_of_isBivector` → `bivector …`, `eq_trivector_of_isTrivector` → `trivector …`), and G3
  *has* a `scalar` constructor (G2 does not), so the bridge is `eq_scalar_of_isScalar : a = scalar a.s`
  and the recognizer `isScalar_scalar` — rather than 2D's `eq_smul_one_of_isScalar`/`smul a.s one`
  form. `isScalar_one` is kept as the handy "`1` is a scalar" recognizer (mirrors 2D).
- No book page: the predicate mirrors existing Python `is_scalar`; the three-forms rule is "new work
  when asked", not a backfill.

## Files touched

- `proofs/GacalcProofs/G3.lean` — the `IsScalar` cluster + `isScalar_mul_self_of_isVector` (additive).
- `tasks/reference/lean-ga-proof-architecture.md` — the "2D grade-pure predicate set" note updated:
  3D parity is now done.

See also: `tasks/reference/lean-ga-proof-architecture.md` → "The 2D grade-pure predicate set".
