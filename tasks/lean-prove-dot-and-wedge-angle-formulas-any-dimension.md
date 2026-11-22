# Prove `a · b = |a| * |b| * cos(θ)` and `|a ∧ b| = |a| * |b| * sin(θ)`, in any dimension

**Status:** proposed — do not start; the maintainer said "make a task for it, but don't start
it yet" (William Emerison Six <billsix@gmail.com>, 2026-11-22)
**Priority:** 7
**Difficulty:** 6
**Created:** 2026-11-22 (William Emerison Six <billsix@gmail.com>)

## BLUF

In the Lean proofs the cosine and sine of the angle between two vectors are *defined* as
`dot a b / (|a| * |b|)` and `|a ∧ b| / (|a| * |b|)`, following Hestenes, so the two formulas in
the title hold by definition. The maintainer wants them proved: give the angle a meaning that
does not mention the dot or the wedge, then derive both formulas, for vectors of any dimension
`n`. Done = the theorems are in `proofs/GacalcProofs/`, the existing 𝒢₂ and 𝒢₃ definitions are
shown to be their `n = 2, 3` cases, a notebook checks them symbolically, a book page states
them, and `make lean`, `make test` and `make docs` pass.

## The request (2026-11-22, the maintainer's words)

> is there a task for making proofs for gn? like the dot product for vectors being
> |a||b| cos(theta) and |wedge product| = |a||b|sin(theta)? how would you even go about
> representing arbitrary dimension vectors?

> so I defined them that way because of the hestenes book, but if we can prove it, I'd like to.
> make a task for it, but don't start it yet

## Context

- Read first: `tasks/reference/lean-ga-proof-architecture.md` (rules, and program decision 4:
  everything from scratch, Mathlib only as an equivalence bridge), `tasks/reference/lean-for-gacalc.md`,
  `tasks/reference/reduction-to-standard-position.md` (rotate to a standard frame, do the easy
  case, rotate back), `CLAUDE.md` "Every piece of math comes in three forms" and "Presenting
  to students: prefer sine/cosine over dot/wedge".
- What exists today:
  - `proofs/GacalcProofs/Trig.lean`: `cos_between`, `sin_between` (the definitions above, in
    𝒢₂ and 𝒢₃), `cos² + sin² = 1` (`cos_sq_add_sin_sq`, from `lagrange_property`), and both
    preserved by the versor sandwich.
  - `proofs/GacalcProofs/Rotation2D.lean`: the one place an angle is independent of the
    products. `uvec α = cos(α) * e₁ + sin(α) * e₂`, and `uvec_mul_uvec`, `uvec_dot`,
    `uvec_wedge`: two unit vectors at angles `α`, `β` multiply to
    `cos(β − α) + sin(β − α) * e₁₂`. `TrigEquiv.lean` ties that to `cos_between` / `sin_between`
    (`cos_between_uvec`, `sin_between_uvec`). So in the plane, for unit vectors given by their
    angles, the formulas are already proved and not merely defined.
  - `proofs/GacalcProofs/MathlibBridge.lean`: Cauchy–Schwarz, `abs_dot_le_magnitude_mul`,
    through Mathlib's `inner`.
  - `proofs/GacalcProofs/StandardPosition.lean` / `StandardPosition2D.lean`: `alignSP`, which
    rotates a vector onto `e₁` with elementary plane rotations that preserve the dot
    (`rotXY_preserves_dot`, `rotXZ_preserves_dot`).
  - The book defines cosine and sine the same independent way in
    `book/docs/bootstrap-rotation-from-projection.rst`, `eq-bootstrap-from-projection-cos-sin`:
    the projection and rejection of `b` against `a` are the legs of a right triangle with
    hypotenuse `b`.
- There is no dimension-general object in Lean. The deferred
  `tasks/lean-general-gn-product-and-hestenes-dot-wedge.md` would build all of 𝒢ₙ (every grade,
  the product, the sign rule). This task needs far less and does not depend on it.
- Python side: `Gn` (`src/gacalc/gn.py`) works in any dimension, so a notebook can check the
  formulas symbolically for `n = 4` and `5`.

## How to represent a vector of any dimension

A vector is a function from indices to reals, `a : Fin n → ℝ`, with `n` a parameter of each
theorem. From scratch, with finite sums:

- length squared: `∑ i, a i * a i`; `magnitude` its square root;
- dot: `∑ i, a i * b i`;
- the wedge of two vectors: its coefficient on the plane `(i, j)`, `i < j`, is
  `a i * b j − a j * b i`, and its squared magnitude is the sum of those squared over `i < j`.

Only the grade-2 part of 𝒢ₙ that two vectors can produce is modelled; no general product. At
`n = 2` and `3` these sums are the existing `G2`/`G3` `dot`, `wedge` and `normSq`, shown by a
bridge lemma each (`Fin.sum_univ_two`, `Fin.sum_univ_three`).

## What "the angle" means, so that there is something to prove

The formulas are only theorems if `θ` is defined without them. The proposed definition is the
book's and the schoolroom's: **the angle of a right triangle**.

For nonzero `a` and `b`, split `b` into a part along `a` and a part across it. With
`â = a / |a|`:

    b = x * â + r,      r perpendicular to a,      y = |r|

Then `x`, `y` are the legs and `|b|` the hypotenuse, `x² + y² = |b|²` (Pythagoras), so there is
exactly one `θ` in `[0, π]` with `cos(θ) = x / |b|` and `sin(θ) = y / |b|`: adjacent over
hypotenuse, opposite over hypotenuse.

Stated without the dot product, "perpendicular" is the Pythagorean condition
`|u + w|² = |u|² + |w|²`, and the split is characterized by it. The theorems, in order:

1. **Perpendicular, two ways.** `|u + w|² = |u|² + |w|²  ⟺  ∑ i, u i * w i = 0`. This is where
   the dot product first appears, as a consequence.
2. **The split exists and is unique.** For `a ≠ 0` there is exactly one `x` with `b − x * â`
   perpendicular to `a`.
3. **The dot formula.** `∑ i, a i * b i = |a| * x = |a| * |b| * cos(θ)`.
4. **Lagrange in `n` dimensions.** `|a|² * |b|² = (a · b)² + |a ∧ b|²`, by finite-sum algebra.
5. **The wedge formula.** `|a ∧ b| = |a| * y = |a| * |b| * sin(θ)` (the wedge sees only the
   rejection, then 4, or directly).
6. **Corollaries.** Cauchy–Schwarz from 4, with no Mathlib `inner`; `θ = 0` or `π` exactly
   when the vectors are parallel; `θ = π/2` exactly when `a · b = 0`.
7. **Bridges.** At `n = 2`, `3` the new `cos`/`sin` equal `Trig.cos_between` /
   `sin_between`; and in the plane `θ` is `|β − α|` folded into `[0, π]` for `uvec α`,
   `uvec β`, tying the triangle's angle to the turning angle of `Rotation2D`.

After this, `cos_between` and `sin_between` keep their Hestenes definitions; what changes is
that a theorem says they are the cosine and sine of the triangle's angle.

## Phases

1. **𝒢₃ first, with what exists.** State and prove items 2, 3 and 5 for `G3` vectors using the
   present `proj`/`reject` and `lagrange_property`. This tests the definitions of `θ` and of
   "perpendicular" on familiar ground before any finite sums.
2. **The `Fin n → ℝ` model:** the definitions above and item 1.
3. **Items 2 to 6 in `n` dimensions.**
4. **Item 7, the bridges.**
5. **Symbolic Python:** a notebook that builds two symbolic vectors in `Gn` for `n = 4` and
   `5`, forms the split, and shows both formulas with `show_difference`; each cell tagged with
   its Lean twin.
6. **The book:** a page (Part II or a proof page) that states the triangle definition and the
   two formulas, cites the Lean theorems, and points back to
   `bootstrap-rotation-from-projection` for the plane.
7. Docs: the inventory and coverage map of `tasks/reference/lean-ga-proof-architecture.md`,
   `proofs/README.md`, `tasks/reference/teaching-order-and-dependencies.md`.

## Risks and things to settle when it starts

- **The sums.** Items 1 to 4 are `Finset.sum` manipulations (`Finset.sum_mul`,
  `Finset.mul_sum`, splitting a double sum into `i < j`, `i = j`, `i > j`), not one-line
  `ext <;> ring` proofs. Lagrange in `n` dimensions is the hardest; Mathlib has it as an
  identity on sums, which under program decision 4 is a check, not the proof.
- **Square roots and the zero vector.** Keep the statements squared where possible, as the
  corpus does, and carry `a ≠ 0`, `b ≠ 0` where `θ` is mentioned (Lean's `x / 0 = 0` would
  otherwise make `cos(θ) = 0` a junk claim).
- **`θ` as a real number.** `Real.arccos (x / |b|)` gives `θ` in `[0, π]`; `sin(θ) = y / |b|`
  then needs `y ≥ 0` and Pythagoras (`Real.sin_arccos`).
- **Signed angle.** In the plane the wedge has a sign and `θ` can be signed; in `n ≥ 3`
  dimensions only `|a ∧ b|` and `θ ∈ [0, π]` make sense. The title's absolute value is that.

## Open questions

1. **The definition of the angle:** (a) the right triangle of the split, as above, the book's
   own route; (b) rotate to standard position (`a` onto `e₁`, `b` into the `e₁ e₂` plane as
   `|b| * (cos(θ) * e₁ + sin(θ) * e₂)`) and read `θ` there, which reuses the `alignSP` theme
   but needs an `n`-dimensional chain of plane rotations; or (c) the law of cosines on the
   triangle with sides `|a|`, `|b|`, `|a − b|`. I recommend (a): it is what the book already
   teaches, it needs no rotations in `n` dimensions, and (c) follows from it as a corollary.
2. **Where "perpendicular" comes from:** (a) the Pythagorean condition, with `dot = 0` proved
   equivalent (item 1), or (b) take `dot = 0` as the definition and accept that the split then
   uses the dot. I recommend (a); with (b) the dot formula is closer to a restatement.

## History

All on 2026-11-22 (William Emerison Six <billsix@gmail.com>).

1. The maintainer asked whether a task existed for 𝒢ₙ proofs of the two angle formulas, and how
   a vector of any dimension would be represented. The answer: the deferred general-𝒢ₙ task
   does not cover them, and in 𝒢₂/𝒢₃ they hold by definition.
2. The maintainer said the definitions follow Hestenes, that a proof is wanted if one can be
   had, and to write the task without starting it. The two open questions are for when it
   starts.
