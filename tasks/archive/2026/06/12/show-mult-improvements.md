# show_mult improvements: distribute (expand) + fix column ordering / iteration

**Created:** 2026-06-11 · **Completed:** 2026-06-12

This merged two former task docs, `show-mult-expand` and `iteration-concepts-and-show-mult-order`
(neither exists any more), because both edited `show_mult` / `nbplotutils` and had to be done together.
`nbplotutils.show_mult(a, b)` is the notebook walk-through of the distributivity of `a * b`. The hard
constraint: presentation only, no change to computed values; the conformance suite had to stay green.

## A. Expand

`show_mult` renders the **expanded** view of each per-term product and of the final sum (the maintainer:
"as much as possible", so both). It uses the shared coefficient-op primitive built on 2026-06-11 —
`MultiVectorBase._map_coefficients` + `.simplified()` / `.expanded()` in `base.py`, inherited by every
representation and tested in `tests/test_conformance.py` — the same primitive used by
`tasks/archive/2026/06/12/graded-bivector-dual-simplify.md` and
`tasks/archive/2026/06/12/display-simplify.md`. Plain `sympy.expand` was used, since it distributes
products over sums, which is the lesson.

Because `_repr_latex_` now simplifies for normal display, the body of `_repr_latex_` was factored out
into a module function `base.blade_dict_latex(d)`, and `show_mult` calls
`blade_dict_latex(x.expanded().to_blade_dict())` to bypass the simplify and keep the distribution
visible. Confirmed: a coefficient `c*(a+b)` renders as `(a c + b c) e₁₂` in `show_mult` but as the
factored `c(a+b) e₁₂` from `_repr_latex_`.

## B. Ordering

The code dig (2026-06-11) found three "iterate the parts of a multivector" notions ordered
inconsistently: `MultiVectorBase.__iter__` (coefficient values, key `(len(b), str(b))`);
`_repr_latex_` / `plot_multivector` (key `(len(b), b)`); and `_blade_terms` (the single-blade terms
feeding `show_mult`'s columns, **unsorted** dict order). So the columns did not read in the order the
prose claimed, and the two sort keys disagreed for indices ≥ 10. That was the maintainer's "multiple
iter concepts in different contexts" hunch.

The fix: `_blade_terms` sorts by `(len(b), b)`, `__iter__`'s key changed from `(len(b), str(b))` to
`(len(b), b)`, and `blade_dict_latex` uses the same key, so all three agree and stay correct at n ≥ 10.
(For n < 10 the order of `list(v)` was unchanged.)

**Decision:** the leaner path. Only the ordering was fixed and the key unified; public `blade_terms()` /
`coefficients()` methods on the base class were not added. The expand-vs-simplify need was met by the
render helper, not new iteration API.

## Verification

`ty` and `ruff` clean; full suite passed (221); notebooks `displayg2` / `displayg3` / `displayrotations`
executed headless. `displaymv` ends in a matplotlib animation loop that blocks when run as a bare script
— pre-existing and unrelated (empty stderr).

The `__iter__`-yields-values design and the `_blade_terms` workaround came from
`tasks/archive/2026/06/03/specialized-multivectors.md` and
`tasks/archive/2026/06/06/notebook-display-cells.md`.
