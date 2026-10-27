# Lean: define the geometric & wedge products as functions, add grade predicates for every type, then narrow ℝ→G2 signatures

**Status:** proposed — needs go-ahead.
**Priority:** 5
**Difficulty:** 6
**Created:** 2026-10-27 (William Emerison Six <billsix@gmail.com>)
**Updated:** 2026-10-27 (William Emerison Six <billsix@gmail.com>)

## BLUF

In the Lean proofs (at least the **2D** layer), the geometric product and the wedge should be
**defined as functions** (with their characterizing property in the comments), not only used inline
in each proof; the grade **predicates** should exist for **every** type the Python code has
(scalar, vector, bivector, trivector, versor, rotor), not just `IsVector`; and once those are in
place, 2D signatures that currently take **reals** should take a **G2 object** where that is the
honest input. (Maintainer's observations, 2026-10-27.) Three linked parts, below.

## Context (cold start)

- Proofs live in `proofs/GacalcProofs/` (`make lean`; see `tasks/reference/lean-ga-proof-architecture.md`
  and `lean-for-gacalc.md`). Relevant files for 2D: `G2.lean`, `Predicates2D.lean`, plus the shared
  `MathlibBridge.lean`, `GradeProjection.lean`. (3D siblings: `G3.lean`, `Predicates3D.lean`.)
- House conventions this task serves (gacalc `CLAUDE.md`): **"objects in, scalars in the body"**
  (a theorem takes the object + a grade predicate, drops to coordinates only inside the proof) and
  **"every piece of math comes in three forms"** (Lean / symbolic Python / prose).
- The maintainer specifically liked the result that the dot product **is the symmetric part** of the
  geometric product (the `dot_is_sym_part`-style lemma) — keep and build on that framing.

## Part 1 — define the products as functions (2D first)

- Give the **geometric product** an actual Lean definition for G2 (it is "perfectly fine to define
  it, and use coordinates in the definition / elsewhere, for all the types"). Other proofs then use
  that definition rather than re-deriving the product inline each time.
- Give the **wedge (outer) product** the same treatment: a function definition, with its
  **anti-commutation** property stated in the comment (the characterizing property — analogous to the
  dot = symmetric-part observation). Testing/justifying the definition with coordinates is fine.
- Keep the symmetric-part / antisymmetric-part decomposition (dot = sym part, wedge = antisym part)
  as the connective tissue.

## Part 2 — grade predicates for every type

Python has `is_vector`/`is_bivector`/`is_scalar`/`is_trivector` and the versor/rotor notions. Lean
currently tests `IsVector` (and `IsBivector`/`IsEvenVersor` in places) but not the full set. Add the
missing predicates — **`IsScalar`, `IsBivector`, `IsTrivector`, `IsVersor`, `IsRotor`** (as the
dimension warrants) — mirroring the Python `is_*` tests, so theorems can take any typed object the
way they already take a vector. Audit the Python `is_*`/graded types and match the set.

## Part 3 — narrow ℝ→G2 signatures (once Parts 1–2 unlock it)

With the product defined and the predicates available, find the places in the **2D** proofs that
currently take **reals** (`(a1 a2 : ℝ)`, etc.) as inputs where the honest input is a **G2 object**
(`{a : G2} (ha : IsVector a)`), and narrow them — the "objects in, scalars in the body" rule. (This
is the Lean-side mirror of the polynomial-tier sweep recorded in `lean-ga-proof-architecture.md`.)

## Open questions

1. **Scope: 2D only, or 2D now + a 3D follow-up?** The maintainer said "at least 2D" — recommend
   land 2D fully, then file a 3D follow-up rather than widening mid-task.
2. For Part 3, the `define-frame`/general-inverse style leaf lemmas that are *inherently* about
   coordinates stay real-taking (per the convention's "genuine scalars stay scalar"); confirm the
   narrowing targets only the ones whose real inputs are really a disguised object.

## Deliverables (per the three-forms rule)

Each new definition/predicate lands with its Lean proof green (`make lean`), and — where it states a
result meant for students — a symbolic-Python check and a book note, per
`tasks/reference/lean-ga-proof-architecture.md` and the gacalc `CLAUDE.md` three-forms default.
