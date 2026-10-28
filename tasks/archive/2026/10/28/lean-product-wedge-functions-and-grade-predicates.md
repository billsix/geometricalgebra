# Lean: products as functions, grade predicates for every type, narrow ℝ→G2 (2D)

**Status:** done — 2026-10-28 (2D scope, per the "2D now, 3D later" go-ahead). `make lean` green
(8958 jobs; completeness gate OK). 3D parity is the follow-up `tasks/archive/2026/10/28/lean-grade-predicates-3d.md`.
**Priority:** 5
**Difficulty:** 6
**Created:** 2026-10-27 (William Emerison Six <billsix@gmail.com>)
**Updated:** 2026-10-28 (William Emerison Six <billsix@gmail.com>)

> **Later move (file-structure task, 2026-10-28):** `dot`/`wedge` and their lemmas were subsequently
> relocated into `G2.lean` (`tasks/archive/2026/10/28/study-and-reorder-lean-file-structure.md`). The `Projection2D.lean`
> / `Versor2D.lean` locations cited below — including "where `wedge` currently lives" — were correct at
> the time of this task; `isBivector_wedge_of_isVector` and `wedge_isVector_isBivector_eq_zero` now live
> in `G2.lean`.

## BLUF

Three-part task on the 2D Lean proofs: (1) the geometric & wedge products should be **functions** with
their characterizing properties; (2) grade **predicates** should exist for every 2D type; (3) 2D proofs
taking **reals** that are really a G2 object should be narrowed. On inspection, (1) and (3) were already
satisfied; the genuine delta was (2), the missing grade-pure predicates `IsScalar` and `IsBivector`.
Those were added with bridges, recognizers, and grade-of-result lemmas, and verified with `make lean`.
Durable record: `tasks/reference/lean-ga-proof-architecture.md` → "The 2D grade-pure predicate set".

## What each part turned out to need

**Part 1 — products as functions: already done.** `G2.mul` (`G2.lean`), `G2.wedge`
(`Projection2D.lean`), `G2.dot` (`Versor2D.lean` = `(mul a b).s`) and `reverse` are all defined
functions; the characterizing properties already existed in object form — `dot_is_sym_part` /
`wedge_is_antisym_part` (dot = symmetric part, wedge = antisymmetric part; `G2.lean`), `wedge_antisymm`
/ `wedge_self_vec` (`Projection2D.lean`), and the split `mul_eq_dot_add_wedge`. No code change; the
"use the definition, don't re-derive inline" structure was already in place.

**Part 2 — grade predicates for every 2D type: the real work.** Added to `G2.lean`, mirroring the
existing `IsVector` (grade 1) and its `eq_vec_of_isVector` bridge / `isVector_vec` recognizer:

- `IsScalar` (grade 0) + `eq_smul_one_of_isScalar` (object → `s*1`) + `isScalar_one`.
- `IsBivector` (grade 2, the pseudoscalar's grade) + `eq_smul_e12_of_isBivector` (object → `c*e₁₂`) +
  `isBivector_e12` + `isBivector_I` (the pseudoscalar `I` *is* `e₁₂`).
- Grade-of-result lemmas so the predicates aren't dead API: `isScalar_mul_self_of_isVector` — `a a` is a
  scalar (`G2.lean`); `isBivector_wedge_of_isVector` — `a∧b` is a bivector (`Projection2D.lean`, where
  `wedge` currently lives).
- Refactored `vec_wedge_I_eq_zero` into a corollary of the new object-form
  `wedge_isVector_isBivector_eq_zero` (a vector ∧ a bivector = 0 in 2D), discharged by `isVector_vec` +
  `isBivector_I` — its signature is unchanged, so `reject_from_I_eq_zero` is unaffected.

Decisions (mirroring Python's `is_*` in `base.py`, and "don't add speculative dead code"):
- The 2D set is complete: `IsScalar`/`IsVector`/`IsBivector` are grades 0/1/2. **No grade-3 `IsTrivector`
  in 2D.** `IsEvenVersor`/`IsRotor` (`Sandwich.lean`) already cover the versor/rotor notions, and Python
  has **no** `is_versor`/`is_rotor` predicate (versor/rotor are generated *types*, not `Gn` predicates),
  so **no bare `IsVersor`** was added — a `IsEvenVersor ∨ IsVector` disjunction nothing consumes would be
  speculative.
- Three-forms rule: the Python side already has `is_scalar`/`is_bivector` (the `a∧b`-is-a-bivector fact is
  in `is_bivector`'s docstring example), so the symbolic-Python form exists; these are mirror predicates,
  not a headline student result, so no new book page was warranted (the three-forms default is "new work
  when asked," not a backfill).

**Part 3 — narrow ℝ→G2 signatures: already complete for 2D.** Audited every ℝ-taking 2D theorem; each
remaining one is either a genuine scalar parameter (angles `θ`/`φ`, `cos`/`sin` as `c`/`s`, a scalar
multiple `k`, a magnitude `m`) or a coordinate leaf whose RHS is coordinate arithmetic (the
`_coord`-suffixed ones, `vec_mul`, `dot_vec`, `normSq_vec`, `dual_vec`, …) — both of which "Coordinates
only when needed" explicitly keeps. The disguised-object theorems were lifted in the 2026-10-04
polynomial-tier sweep and the 2026-10-20 follow-up (`lean-ga-proof-architecture.md`). No edits.

## Files touched

- `proofs/GacalcProofs/G2.lean` — `IsScalar`/`IsBivector` + bridges + recognizers +
  `isScalar_mul_self_of_isVector`.
- `proofs/GacalcProofs/Projection2D.lean` — `isBivector_wedge_of_isVector`,
  `wedge_isVector_isBivector_eq_zero`, `vec_wedge_I_eq_zero` as a corollary.
- `tasks/reference/lean-ga-proof-architecture.md` — the durable "2D grade-pure predicate set" note.

## Follow-up

- `tasks/archive/2026/10/28/lean-grade-predicates-3d.md` — add `IsScalar` + grade-of-result lemmas to `G3` (3D parity).
