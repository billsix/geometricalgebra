# Display simplification for G1/G2/G3

Status: **not started** · proposed 2026-06-04 · needs a go/no-go

## Background

In the specialized-multivector work (see `tasks/archive/specialized-multivectors.md`) the coefficient
policy was "symbolic, but lazy simplify": `Gn` eager-simplifies; `G1`/`G2`/`G3` simplify lazily.
Decision 1 said the specialized classes should "simplify **on display**" as well as on equality.

We implemented lazy simplify on **equality** (their `__eq__` simplifies the per-blade difference),
but **display was never done**: `G1`/`G2`/`G3` inherit `AbstractMultiVector._repr_latex_` (in
`base.py`), which renders the raw, lazily-unsimplified coefficients. (sympy still auto-simplifies
trivially, so it's not wrong — just potentially not in lowest terms.)

## The decision

Do we want specialized values to fully `sympy.simplify` their coefficients when displayed
(`_repr_latex_`, and maybe `__repr__`)?

## Sketch if yes

- Override `_repr_latex_` on `G1`/`G2`/`G3` (generated) to render a simplified view — e.g. build a
  blade-dict with `sympy.simplify` applied, then reuse the base rendering logic. Keep the stored
  fields untouched (still lazy); only the displayed form is simplified.
- Alternatively, give the ABC `_repr_latex_` a small hook (e.g. simplify `to_blade_dict()` values
  before formatting) controlled by a class flag, so only the specialized classes opt in.

## Open questions

- Display only, or also a `.simplified()` helper returning a new fully-simplified instance?
- Is the extra simplify cost acceptable on display (display is not hot, so almost certainly yes)?
