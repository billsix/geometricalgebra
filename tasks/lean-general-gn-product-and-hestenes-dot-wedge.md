# Lean — a dimension-agnostic `Gn`-style product, and Hestenes-style dot/wedge (future)

**Relates to:** the Lean-proofs program (umbrella archived: `tasks/archive/2026/10/04/investigate-lean-proofs-for-ga.md`) and the
per-component algebras `proofs/GacalcProofs/G2.lean`, `G3.lean`.

**Status:** proposed — **deliberately deferred** (do NOT start now). The maintainer prefers the
current per-component approach (explicit `G2`/`G3` coordinate structs) for now — it makes the algebra
concrete and is **desirable for his learning**. This task is a *later* exploration of a more general
formulation, once the component proofs have served their teaching purpose.
**Priority:** 9
**Difficulty:** 8

## BLUF

Explore whether, in Lean, we can (1) define the geometric **product the way gacalc's oracle `Gn`
does** — dimension-agnostically, as a blade→coefficient map with the product computed by the
blade-multiplication rule **for any number of dimensions** `n`, rather than a separate hand-written
component formula per dimension (`G2`, `G3`, …); and (2) then define **dot and wedge the way Hestenes
does** — as the graded parts of that geometric product (for vectors, `a·b = ½(ab+ba)`,
`a∧b = ½(ab−ba)`; in general the grade projections `⟨AB⟩_{|r−s|}` / `⟨AB⟩_{r+s}`) — rather than
per-component. "Done" (when eventually taken up) = a general `Gn` in Lean with the product + Hestenes
dot/wedge, **proved consistent with the per-component `G2`/`G3`** (a bridge lemma each way).

## Context — read first

- **Why not now (the point):** the component approach is pedagogically valuable — writing the explicit
  8-coefficient `G3.mul` (transcribed from `Gn`) makes every blade product visible, which the
  maintainer wants while learning. The general version *hides* that behind an abstraction, so it comes
  after, not instead.
- **What "like `Gn`" means:** gacalc's `Gn` (`src/gacalc/gn.py`) stores a multivector as a `dict` from
  a canonical blade (a sorted tuple of basis indices) to a coefficient, and multiplies by the
  blade-product rule (concatenate, sort with a sign per transposition, cancel `eᵢeᵢ = 1`). A Lean
  analogue could model a multivector as `Blade →₀ ℝ` (`Finsupp`) — or an inductive/`Finset`-indexed
  blade type — with `mul` defined by that rule, parametric in `n`.
- **What "Hestenes dot/wedge" means:** define the inner and outer products as *derived* from the
  geometric product via grade projection (Hestenes & Sobczyk), not as separate coordinate formulas —
  the from-rotation `dot = symmetric part` / `wedge = antisymmetric part` already proved in 2D
  (`G2.dot_is_sym_part`/`wedge_is_antisym_part`) is the vector case; generalize it.
- **Standalone-policy note:** this stays *from-scratch* (a blade-`Finsupp` model of our own), separate
  from depending on Mathlib's `CliffordAlgebra` — though comparing to / mapping onto `CliffordAlgebra`
  for an equivalence check would be welcome (as elsewhere, Mathlib for the *equivalence* direction).

## Added scope (2026-10-04): the general-n pseudoscalar sign

`tasks/archive/2026/10/04/lean-proof-pseudoscalar-square-sign.md` (archived) covers n = 1, 2, 3; the general statement
`Iₙ² = (−1)^(n(n−1)/2)` belongs here, once a dimension-general blade model exists. What is already known:

- The Python closed form `base.pseudoscalar_squared_sign(r)` replaced a body that squared the unit
  pseudoscalar through the `Gn` oracle (commits `45dcdc9` → `3a98012`); `tests/test_pseudoscalar_square_sign.py`
  gates the two equal for a range of `r`, and `tests/test_conformance.py` checks each generated algebra's
  `unit_pseudoscalar_squared` against `Gn`. So a *computed* general-n check exists in Python.
- The *written* general proof is `tasks/reference/pseudoscalar-square-sign.md`: count the adjacent swaps
  needed to reverse `e₁…eₙ` (the triangular number `n(n−1)/2`), or the one-liner via `reverse`.
- In Lean the natural statement is on the blade model this task picks: a basis blade is a sorted index
  list (or `Finset (Fin n)`), the product of blades is the merged list with the sign of the sorting
  permutation, and `Iₙ² ` is the sign of reversing `[0, …, n−1]`, i.e. `(−1)^(n(n−1)/2)` by induction on
  `n` (`Iₙ₊₁ = Iₙ eₙ`, and moving `eₙ` through `Iₙ` costs `n` swaps). Mathlib's `CliffordAlgebra` is the
  reference for the general statement but is not the standalone route this corpus uses.

## Open questions

1. Representation for the general `Gn`: `Blade →₀ ℝ` (`Finsupp`, closest to gacalc's dict) vs an
   inductive blade type vs a `Fin n`-indexed construction — which keeps the product proofs tractable
   (the sign-per-transposition rule is the hard part to formalize cleanly)?
2. Is `ring`-style automation still usable once the product is a `Finsupp` sum, or do the proofs become
   `Finsupp`/`Finset` inductions (a big step up in difficulty from the current one-line `ext <;> ring`)?
3. Scope of the consistency bridge: prove `G2`/`G3` `≃` the `n=2`/`n=3` instances of the general `Gn`
   (product-preserving), so the concrete proofs and the general one corroborate each other.
