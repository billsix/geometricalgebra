# Promote symbolic unit tests to Lean theorems (pick the worthy ones)

**Status:** DONE (cheap high-value items) 2026-09-30 — items 1/2/3/5 proven; 4/6 deferred
**Priority:** 7
**Difficulty:** 4
**Created:** 2026-09-30 **Updated:** 2026-09-30 (William Emerison Six <billsix@gmail.com>)

## Outcome (2026-09-30) — items 1, 2, 3, 5 proven; 4, 6 deferred

Executed the cheap high-value gap items (my Q1/Q2 recommendation) directly as Lean proofs, all
gate-verified `sorry`-free:

- **Item 2 (cross product)** — new `proofs/GacalcProofs/Cross.lean`: `cross a b := (a∧b) I₃⁻¹`,
  `cross_vec` (coordinate formula), `cross_anticomm_vec`, `cross_perp_left`/`cross_perp_right`.
- **Item 5 (3D vector dual = perpendicular bivector)** — `Cross.lean` `dual_vec`
  (`(x,y,z)* = −z e₁₂ + y e₁₃ − x e₂₃`).
- **Item 1 (scalar triple = signed volume)** — `Cross.lean` `signedVolume := (a∧b∧c).c123` and
  `dot_cross_eq_signedVolume` (`a·(b×c) = signedVolume = det[a,b,c]`).
- **Item 3 (sandwich grade-preserving for a general even versor)** — `Sandwich.lean`
  `sandwich_evenVersor_vec_isVector` (`IsVector (R v R⁻¹)`; grade-3 part vanishes).

Commits `3f53e7b` (Cross.lean), `2883077` (grade preservation). Inventory updated in
`tasks/reference/lean-ga-proof-architecture.md`.

**Deferred (bigger, my Q1 recommendation to hold):** item 4 (Gram–Schmidt / frame theory — no
frame theory in Lean at all; belongs with `tasks/define-frame.md`) and item 6 (content-two-ways —
needs `area`/`content` defs in Lean; the Gram-determinant half is already `lagrange_3d`). Left as
their own future work, not this pass.

## BLUF

Go through gacalc's **symbolic** unit tests (the ones that assert an algebraic identity over
sympy-symbol multivectors, i.e. a law that holds for *all* values), decide which deserve to be
added as **Lean** theorems, and produce that shortlist as the deliverable. Many identities are
**already** proven in Lean; the value here is closing the *gap* — universal laws asserted only in
Python. "Done" for THIS task = a reviewed shortlist (identity → target `.lean` file → build-on
lemma), each item either spun into its own `lean-proof-*` task or folded into the umbrella
`tasks/investigate-lean-proofs-for-ga.md`. It is **not** authorization to write the proofs.

## Context (read first)

- Lean lives under `proofs/GacalcProofs/*.lean`, gated by `make lean` (`proofs/check.sh`;
  green as of 2026-09-30). Orientation: `tasks/reference/lean-for-gacalc.md`; architecture +
  inventory: `tasks/reference/lean-ga-proof-architecture.md`.
- Symbolic-test infrastructure: the shipped fixtures are `sym_vec2_1/2`, `sym_vec3_1/2`,
  `sym_vec_plane` at `src/gacalc/gn.py:285-299`; most tests declare fresh `sympy.symbols(...)`
  inline. Symbolic equality is asserted three ways (generated `__eq__`; per-blade
  `simplify(a-b)==0` helpers `_same_value` `tests/test_conformance.py:420`, `simplify_equal`
  `tests/test_graded.py:390`; and direct `sympy.simplify/expand`). See
  `tasks/reference/symbolic-equality.md`.
- **Not the same as** `tasks/consolidate-symbolic-equality-predicate.md` (blocked) — that
  consolidates the duplicated equality helpers; this is about Lean coverage. No overlap.

## The gap — universal identities asserted in Python but NOT yet in Lean

Best candidates (each cites the Python test; none has a named Lean theorem today):

1. **Scalar triple product = signed volume** — `tests/test_vectorcalc.py:76-92`
   (`a·(b×c) = signed_volume(a,b,c)`); and **signed_volume = 3×3 determinant** —
   `tests/test_measure.py:121-123`. Needs `cross`/`dual`-based triple + a determinant statement
   in Lean (target: a new `Measure.lean` or extend `Projection.lean`'s `dual` lemmas).
2. **Cross-product coordinate formula & anticommutativity** — `tests/test_vectorcalc.py:64-73`.
   Derivable from the existing `dual` + wedge (`dual_wedge_perp_*`, `Projection.lean:46/51`); no
   Lean `cross` yet.
3. **Sandwich is grade-preserving for a general even versor** (grade-3 part vanishes) —
   `tests/test_odd3.py:100-118`. Distinct from the isometry lemmas already in `Sandwich.lean`.
4. **Gram–Schmidt orthogonality** (`tests/test_frame.py:106-113`, `:134-149`) and **Hestenes
   cₖ = |A_{k−1}|²·wₖ** (`tests/test_frame.py:221-233`). No frame theory exists in Lean at all
   — the biggest new area; consider whether it's worth it (see `tasks/define-frame.md`).
5. **3D vector dual = perpendicular bivector** — `tests/test_multivector.py:185-192`. Only the
   2D `dual_vec` (`G2.lean:200`) is named; the 3D case is not.
6. **content-two-ways = determinant** — `tests/test_measure.py:126-141`. (The 3D Gram-determinant
   case IS already `lagrange_3d`/`lagrange_property` in `Lagrange.lean`/`Trig.lean` — so only the
   content/rejection *equivalence* is new.)

## Already covered in Lean (low value — do NOT re-target)

The `ab = a·b + a∧b` split (2D+3D), projection/rejection split + `reject_perp`, the Lagrange
identity, `I²=−1` / `eᵢⱼ²=−1`, reverse involution, associativity/distributivity, the
plane-rotation cos/sin form, sandwich preserves dot+length+wedge, `R R̃=|R|²`, `cos²+sin²=1`.
Full mapping (test → Lean theorem) is in the survey that produced this task; regenerate it by
re-reading `proofs/GacalcProofs/*.lean` if it goes stale.

## Poor Lean candidates (skip)

Predicate/behaviour tests, not math laws: `test_same_type_eq_fast_path_stays_simplify_aware`
(`test_graded.py:320`), `test_symbolic_magnitude_stays_symbolic` (`test_numeric_magnitude.py:56`),
and code-equivalence/oracle tests like `test_generated_closed_form_matches_definition`
(`test_vectorcalc.py:109`).

## Open questions

1. **Cutoff:** do all six gap-items become Lean tasks, or only the cheap high-value ones (1, 2,
   5)? Frame theory (4) is a large new area — in scope or defer to `tasks/define-frame.md`?
2. **Bookkeeping:** one new `lean-proof-*` task per accepted item, or one "close the symbolic-test
   gap" task tracked under the umbrella `tasks/investigate-lean-proofs-for-ga.md`? My lean: cheap
   ones (cross/triple/3D-dual) as a single task; frame theory as its own.
3. **Naming caution to carry into any proof task:** in Lean `dot` = scalar part = gacalc's
   `scalar_product`; gacalc's `dot`/`inner_product` are distinct graded notions
   (`lean-ga-proof-architecture.md` §"Hestenes projection" documents this — reuse its wording).
