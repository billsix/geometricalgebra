# show_mult improvements: distribute (expand) + fix column ordering / iteration

> **UPDATE (2026-06-11): the shared `.simplified()` / `.expanded()` primitive is BUILT** —
> `MultiVectorBase._map_coefficients` + `.simplified()` / `.expanded()` in `base.py` (map a
> sympy op over the coefficients via the blade-dict interchange; inherited by `Gn`/`G1`/`G2`/`G3`
> and the graded subtypes). Tested in `tests/test_conformance.py`. This task can now just *use*
> them rather than build the helper.

Status: **DONE** · 2026-06-12
*(Merge of the former `show-mult-expand.md` + `iteration-concepts-and-show-mult-order.md`
— both edit `show_mult`/`nbplotutils` and must be done together.)*

## What was done (2026-06-12)

- **A. Expand** — `show_mult` now renders the **expanded** view of each per-term
  product and the final sum, via the new module function `base.blade_dict_latex(d)`
  (the body of `_repr_latex_`, factored out). `_repr_latex_` keeps simplifying for
  the normal display; `show_mult` calls `blade_dict_latex(x.expanded().to_blade_dict())`
  to *bypass* that simplify so the distribution stays visible. Confirmed: a product
  with coefficient `c*(a+b)` renders `(a c + b c) e₁₂` in `show_mult` but the
  factored `c(a+b) e₁₂` from `_repr_latex_`.
- **B. Ordering** — `_blade_terms` now sorts by `(len(b), b)`; `__iter__`'s sort key
  changed from `(len(b), str(b))` → `(len(b), b)` (line ~200); `blade_dict_latex`
  uses the same key. All three "iterate the parts" notions now agree and stay
  correct at n ≥ 10.
- **Decision on the open question** (named iteration methods vs local fix): took the
  *leaner* path — fixed `_blade_terms` ordering + unified the sort key only; did
  **not** add public `blade_terms()`/`coefficients()` methods. The expand-vs-simplify
  need was met by extracting `blade_dict_latex` (a render helper), not new iteration
  API.
- **Verify:** `ty` + `ruff` clean; full suite **221 passed**; notebooks
  `displayg2`/`displayg3`/`displayrotations` execute headless. (`displaymv` ends in a
  matplotlib animation loop that blocks when run as a bare script — pre-existing,
  empty stderr, unrelated to this change.)

## Goal

Two fixes to `nbplotutils.show_mult(a, b)` (the distributivity walk-through of
`a * b`), plus the iteration cleanup behind one of them:

- **A. Distribute fully** — `sympy.expand` the symbolic coefficients so every
  product is maximally distributed (the whole point of the "multiplication is
  distributive over addition" lesson; no factored/un-distributed products hiding
  in a cell).
- **B. Order the left/right columns correctly** — the columns currently don't read
  in the order the surrounding prose claims, because the term decomposition is
  unsorted.

## Current state (`src/gacalc/nbplotutils.py:624`)

```python
def show_mult(a, b):
    ... display (a)*(b) ...                                  # "We want to evaluate"
    data = list(itertools.product(_blade_terms(a), _blade_terms(b)))
    result = [(left, "*", right, "=", left * right) for left, right in data]
    ... render table ...
    display(Math("$" + (a * b)._repr_latex_() + "$"))        # final sum
```

### B — the ordering bug (code dig, 2026-06-11)

There are **three different "iterate the parts of a multivector" notions**, with
**inconsistent ordering**:

1. `MultiVectorBase.__iter__` (`base.py:191`) — coefficient *values* in blade
   order, key **`(len(b), str(b))`**.
2. `_repr_latex_` / `plot_multivector` (`base.py:736`, `nbplotutils.py:545`) —
   blades sorted by **`(len(b), b)`** (numeric tuple).
3. `_blade_terms` (`nbplotutils.py:612`) — the single-blade multivectors feeding
   `show_mult`'s columns — iterates **`to_blade_dict().items()` with NO sort**
   (dict/insertion order).

So `show_mult`'s columns (from `_blade_terms`, unsorted) don't match the grade
order the prose implies. The two sort keys also disagree (`str(b)` vs `b`) — they
happen to agree for single-digit indices (n < 10) but it's an inconsistency to
remove. Bill's "multiple iter concepts in different contexts" hunch is exactly
this: *coefficient values in order* vs *single-blade terms in order* are distinct
notions that should each be explicit and consistently ordered.

## What to do

### A. Expand
- Add a small helper (map a sympy op over the coefficients), e.g.
  `expanded(mv) = type(mv).from_blade_dict({b: sympy.expand(c) for b, c in mv.to_blade_dict().items()})`,
  and apply it to the **per-term products** and the **final sum** in `show_mult`.
- **Shared primitive:** this `.expanded()` is the sibling of the `.simplified()`
  helper in `tasks/graded-bivector-dual-simplify.md` / `tasks/display-simplify.md`
  — build the coefficient-op helper **once** (decide: a real method on
  `MultiVectorBase`, recommended, vs nbplotutils-local) and reuse across all three.

### B. Ordering / iteration
- **Fix `_blade_terms`** to emit terms in canonical order
  `sorted(..., key=lambda b: (len(b), b))`, so the columns match the description.
- **Unify the sort key** to `(len(b), b)` everywhere (drop the `str(b)` form in
  `__iter__`) so all three notions agree (and stay correct at n >= 10).
- Decide whether to expose the two notions as **named methods** on
  `MultiVectorBase` (e.g. `blade_terms()` for single-blade terms in order;
  `__iter__`/`coefficients()` for values) — the explicit answer to "multiple iter
  concepts" — or just fix `_blade_terms`' ordering locally. (Lean: at least fix the
  ordering; named methods is the bigger cleanup — gauge appetite.)

## Hard constraint

Display/ordering/presentation only — **no change to computed values**. The
conformance suite must stay green; `show_mult` is notebook-only. If `__iter__`'s
sort key changes, verify no numpy `list(v)` consumer relies on the old `str(b)`
order (unchanged for n < 10, but check).

## Open questions

- Expand **both** the per-term products and the final sum? (Bill: "as much as
  possible" → lean both.)
- `sympy.expand` vs `expand_mul`/`expand_trig` — plain `expand` distributes
  products over sums (the distributivity point); confirm it fits the demo
  coefficients.
- Named iteration methods on the base class, or local `_blade_terms` fix only?

## Relationship

- Shares the coefficient-op primitive with `tasks/graded-bivector-dual-simplify.md`
  and `tasks/display-simplify.md` (`.expanded()`/`.simplified()` — same shape).
- The `__iter__`-yields-values design + the `_blade_terms` workaround came from
  `tasks/archive/2026/06/05/specialized-multivectors.md` and
  `tasks/archive/2026/06/06/notebook-display-cells.md`.
