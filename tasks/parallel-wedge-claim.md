# The `A ∧ B = 0 ⟺ A ∥ B` claim: prove the converse, or reword it

**Status:** proposed — needs go-ahead (blocked on open question 1)
**Priority:** 3
**Difficulty:** 1 if reworded; ~5 if the converse is proved
**Created:** 2026-11-08
**Source:** `tasks/review/2026/11/08/repo-review.md` §7.1, §2.2

## BLUF

Three places say Lean machine-checks the equivalence `A ∧ B = 0 ⟺ A ∥ B`:

- the `is_parallel_to` docstring;
- `CLAUDE.md` › "Assessment / known issues" item 2;
- a `CHANGELOG.md` `[Unreleased]` › Fixed entry.

Lean proves only one direction. Done means those claims match what is proved: either the converse
is proved in Lean, or the three claims are reworded to the direction that is proved.

## Context

**What is proved.** `proofs/GacalcProofs/Predicates3D.lean` proves `wedge_parallel_smul`: for a
vector `a` and a real `k`, `a ∧ (k·a) = 0`, i.e. parallel ⟹ wedge zero. Its header (:11) says: "The
converse (`a ∧ b = 0 ⟹ b = k·a` for `a ≠ 0`) is not yet stated here."

**Where the claim is made** (re-checked 2026-11-08):

- `src/gacalc/base.py`, `is_parallel_to` docstring: "The equivalence ``A ∧ B = 0 ⟺ A ∥ B`` is
  machine-checked in ``proofs/GacalcProofs/Predicates3D.lean``."
- `CLAUDE.md` › "Assessment / known issues" item 2: "now uses the wedge-zero test `A ∧ B = 0`,
  machine-checked in `proofs/GacalcProofs/Predicates3D.lean`."
- `CHANGELOG.md` `[Unreleased]` › Fixed, the `is_parallel_to` entry, says the same.

**What the converse would take.** In 𝒢₃ with `a ≠ 0`, `a ∧ b = 0` gives three equations,
`a₁ * b₂ = a₂ * b₁` and so on, and the converse is that they force `b = k * a`. This is the standard
proof:

- pick a nonzero component of `a`, say `a₁`;
- set `k = b₁ / a₁`;
- each other component follows from one of the three equations.

In Lean that is a `by_cases` on which component is nonzero, then `field_simp` and `linarith` or
`linear_combination`. The house style is "Coordinates only when needed": objects in, coordinates in
the body (`CLAUDE.md`), so the statement is about `{a b : G3} (ha : IsVector a) (hb : IsVector b)
(h0 : a ≠ 0)`. A 2D twin in `Predicates2D.lean` would be the same argument with two components.
The new theorem must pass `proofs/check.sh`, including the axioms gate added by
`tasks/archive/2026/11/08/lean-check-sh-axioms-gate.md`.

## Plan

Depends on open question 1.

- **If (a) prove:**
  - [ ] State and prove `parallel_of_wedge_eq_zero` (3D, and 2D) in object form.
  - [ ] Add the `⟺` corollary that combines it with `wedge_parallel_smul`.
  - [ ] Update `Predicates3D.lean`'s header.
  - [ ] Check that the three claims now name the right theorems.
  - [ ] Gate: `bash proofs/check.sh`.
- **If (b) reword:**
  - [ ] Change the three claims to "the direction parallel ⟹ `A ∧ B = 0` is machine-checked
    (`wedge_parallel_smul`); the converse is not yet proved".
  - [ ] Gate: `ruff`/doctests unaffected.

## Open questions

1. **(a) prove the converse** (`a ∧ b = 0` and `a ≠ 0` ⟹ `b = k * a`, in 3D and 2D, ~D5) so the three
   `⟺` claims become true; or **(b) reword** the three claims to the one direction Lean proves (~D1)?
   Recommendation: (a). The library's predicate rests on this equivalence, and the proof is a
   standard case split.
