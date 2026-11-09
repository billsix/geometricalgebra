# Make notebook cells display nicely (kill bare-tuple "junk" output) + drop dict literals

**Created:** 2026-06-06 · **Completed:** 2026-06-06

Several notebook cells ended in a bare tuple such as `kind(a), a.to_blade_dict()`. Jupyter renders
the tuple's `repr`, not each element's `_repr_latex_`, so a cell showed
`('Vector2', {(1,): 3, (2,): 4})`, or a full dataclass `__repr__` if a raw multivector sat in the
tuple. These cells were made to render cleanly, and a leftover `from_blade_dict({...})` literal was
replaced by a basis combination. Notebook-only; no library, test, or generator change.

## Decisions

- **A `show(*values)` helper rather than splitting cells.** `show` renders each value as
  `Type:  <latex>`, generalizing the display loop at the bottom of `displaygraded.py`. That
  notebook's thesis is "the operation decides the type", so keeping the type and the rendered value
  in one labeled row is the lesson; splitting `kind(a)` and `a` into two cells would lose it. For a
  notebook not about types, plain cell-splitting would be right, and that rule (split unrelated
  single values; `show()`/`display()` for a labeled group that belongs together) was applied in the
  sweep.
- `show` is local to `displaygraded.py` (it relies on that notebook's `kind`); another notebook that
  needs it defines its own copy rather than importing across notebooks.
- For the two-type cells (e.g. `kind(a ^ b), kind(a.inner_product(b))`), `show` also renders the
  values (`Scalar:  0`). This was kept by default as informative and consistent; no `value=False`
  flag was added.

## What changed

- `notebooks/displaygraded.py`: added `show` right after `kind`; converted **14** bare-tuple cells to
  `show(...)` (the 13 surveyed plus `kind(i2*i2), i2*i2`, which held a raw multivector and which the
  grep had missed), e.g. `kind(a), a.to_blade_dict()` → `show(a)` and `kind(u * v), kind(u ^ v)` →
  `show(u * v, u ^ v)`; replaced the bottom display loop with `show(a, a * b, a ^ b, r)`; and swapped
  `a == G2.from_blade_dict({(1,): 3, (2,): 4})` for `a == 3 * e_1 + 4 * e_2` (ruff then removed the
  unused `G2` import).
- `displayg2` / `displayg3` / `displaymv` were swept: no bare-tuple cells (their comma lines are
  function calls such as `show_mult(a, b)`; the author had already split `displayg2`'s `zero, one`
  by hand).
- Incidentally, `format.sh`'s `ruff format` fixed pre-existing single-space inline comments
  (`zero # x` → `zero  # x`) in `displayg2.py`/`displayg3.py`; kept, per the standing
  "reformatting may run anytime" preference.

## Verification

The `show` LaTeX string (`x._repr_latex_().strip("$")`) was checked headless (the `display(Math(...))`
call itself needs Jupyter); `format.sh` exit 0, ruff/ty clean; 161 tests still pass.
