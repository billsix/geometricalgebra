# Make notebook cells display nicely (kill bare-tuple "junk" output) + drop dict literals

**Status:** complete
**Completed:** 2026-06-06
**Started:** 2026-06-06

> **Done (2026-06-06).** `displaygraded.py`: added the `show(*values)` helper (renders each value as
> `Type:  <latex>`), converted **14** bare-tuple cells to `show(...)` — the 13 surveyed plus line 131
> (`kind(i2*i2), i2*i2`) which held a raw multivector and the grep had missed — replaced the bottom
> display loop with `show(a, a * b, a ^ b, r)`, and swapped the `from_blade_dict({...})` literal for
> `3 * e_1 + 4 * e_2` (which made the `G2` import unused, auto-removed by ruff). Swept `displayg2` /
> `displayg3` / `displaymv`: **no** bare-tuple cells (their comma-lines are all function calls). The
> `show` LaTeX string was headless-verified; `format.sh` fully clean (exit 0), `ruff`/`ty` clean, 161
> tests still pass.
>
> Incidental: `format.sh`'s `ruff format` also fixed inline-comment spacing (`zero # x` → `zero  # x`)
> in `displayg2.py` / `displayg3.py` — pre-existing single-space comments in hand-edited cells; kept,
> per the standing "reformatting may run anytime" preference.
>
> Open question resolved by default: `show` renders the **value** for the two-type cells too
> (e.g. `Scalar:  0`) — kept, as it's informative and consistent; no `value=False` flag added.

## Goal

Several notebook cells end in a bare tuple like `kind(a), a.to_blade_dict()` or `kind(u*v), kind(u^v)`.
Jupyter renders the *tuple's* `repr`, so instead of the nice LaTeX from the classes' `_repr_latex_`
override you get `('Vector2', {(1,): 3, (2,): 4})` — and if a raw multivector ever sits in such a
tuple it dumps the full dataclass `__repr__`. Make these print cleanly, and while here, replace a
leftover `from_blade_dict({...})` literal with a basis-vector combination.

## Why

The classes override `_repr_latex_` so a *single* multivector renders as LaTeX in a cell. A tuple
defeats that (tuple repr, not element `_repr_latex_`). The bottom of `displaygraded.py` already shows
the clean pattern and it reads beautifully:

```python
for x in (a, a * b, a ^ b, r):
    display(Math(f"{kind(x)}:\\quad " + x._repr_latex_().strip("$")))
```

## Scope (surveyed 2026-06-06)

- **`notebooks/displaygraded.py` — the locus.** 13 bare-tuple cells: lines 76, 88, 92, 103, 106, 117,
  128, 137, 147, 161, 216, 221, 228. Plus one dict literal at line 249.
- **`displayg2.py` / `displayg3.py` / `displaymv.py`:** the comma-lines there are *function calls*
  (`show_mult(a, b)`, `scale_non_uniform(5, 6)`, …), **not** bare tuples. (The author already split
  `displayg2`'s `zero, one` into separate cells — strategy 1, by hand.) Still: **sweep all three** to
  confirm nothing slipped past the grep heuristic.

## Strategy

### 1. Add a `show(*values)` helper near the top of `displaygraded.py`

Generalize the bottom loop into a reusable helper (place it right after `kind`):

```python
def show(*values):
    """Display each value as 'Type:  <latex>' -- the type is the point of this notebook."""
    for x in values:
        display(Math(f"{kind(x)}:\\quad " + x._repr_latex_().strip("$")))
```

The varargs cover both the single-value and multi-value cases with one tool (so it serves both the
author's option 1 and option 2), and the **type leads every line** — which is exactly this notebook's
thesis ("the operation decides the type").

### 2. Convert the bare-tuple cells to `show(...)`

A strict upgrade: renders the value as LaTeX instead of a raw blade-dict.

| now | becomes | renders as |
| --- | --- | --- |
| `kind(a), a.to_blade_dict()` | `show(a)` | `Vector2:  3𝐞₁+4𝐞₂` |
| `kind(a * b), (a * b).to_blade_dict()` | `show(a * b)` | `Rotor2:  …` |
| `kind(a ^ b), kind(a.inner_product(b))` | `show(a ^ b, a.inner_product(b))` | two rows, each `Type: …` |
| `kind(e_1 * e_2), (e_1 * e_2).to_blade_dict()` | `show(e_1 * e_2)` | one row |
| `kind(e_1 ^ e_2), (e_1 ^ e_2).to_blade_dict()` | `show(e_1 ^ e_2)` | one row |
| `kind(i2 * i2), (i2 * i2).to_blade_dict()` | `show(i2 * i2)` | one row |
| `kind(r), r.to_blade_dict()` | `show(r)` | one row |
| `kind(rotated), rotated.to_blade_dict()` | `show(rotated)` | one row |
| `kind(quarter.plane_of_rotation()), …to_blade_dict()` | `show(quarter.plane_of_rotation())` | one row |
| `kind(R), R.to_blade_dict()  # comment` | `show(R)  # comment` | one row |
| `kind(u * v), kind(u ^ v)` | `show(u * v, u ^ v)` | two rows |
| `kind(biv), kind(biv.dual())` | `show(biv, biv.dual())` | two rows |
| `[(kind((f_1^f_2)*(f_1^f_2)), (...).to_blade_dict())]` | `show((f_1 ^ f_2) * (f_1 ^ f_2))` | one row |

### 3. Why `show` (option 2) over cell-splitting (option 1) *here specifically*

`displaygraded.py`'s whole thesis is "the operation decides the **type**." Pairing the type with the
rendered value in one labeled row *is* the lesson — splitting `kind(a)` and `a` into two cells loses
that adjacency. For a notebook that wasn't about types, plain cell-splitting (option 1) would be the
right call instead; apply that judgement during the sweep of the other notebooks.

### 4. Replace the dict literal

`displaygraded.py:249`: `a == G2.from_blade_dict({(1,): 3, (2,): 4})` → `a == 3 * e_1 + 4 * e_2`
(here `e_1`/`e_2` are already the `Vector2` basis defined at the top).

### 5. Sweep the other three notebooks

Confirm no bare-tuple cells remain in `displayg2.py` / `displayg3.py` / `displaymv.py`. Fix any by the
same rule: **split** if the two values are unrelated single things; **`show()` / `display()`** if a
labeled multi-value genuinely belongs together.

## Plan

- [ ] Add the `show` helper to `displaygraded.py`.
- [ ] Convert the 13 tuple-cells per the table.
- [ ] Replace the `from_blade_dict` literal with `3 * e_1 + 4 * e_2`.
- [ ] Sweep `displayg2` / `displayg3` / `displaymv` for stray bare-tuple cells; fix by the rule.
- [ ] Spot-check headless that `x._repr_latex_().strip("$")` yields sane LaTeX for the value types used
      (the actual `display(Math(...))` needs Jupyter, but the string can be checked).
- [ ] `entrypoint/format.sh` (ruff + ty) clean. Notebooks aren't run by the suite, so no test delta;
      verify the suite is still green anyway (no library change expected).

## Notes / decisions

- Notebook-only; no library / test / generator change.
- The `show` helper is local to `displaygraded.py` (it leans on that notebook's `kind`); if another
  notebook needs the same, define a local copy there rather than importing across notebooks.

## Open questions

- For the pure "which type?" two-value cells (`kind(a^b), kind(a.inner_product(b))`), `show` will also
  render the *values* (e.g. `Scalar:  0`). Confirm that's wanted (it's informative and consistent); if
  the author wants type-only there, `show` could take an optional `value=False` to print just `kind`.
