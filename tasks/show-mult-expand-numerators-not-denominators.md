# show_mult: expand numerators but not denominators

**Status:** proposed — needs go-ahead (investigation). 2026-06-14, Bill.

## Why

`nbplotutils.show_mult` currently runs `.expanded()` on each coefficient before
rendering (so the term-by-term product table and the final sum show *fully
expanded* coefficients). That reads well for polynomial coefficients, but for
products with rational coefficients — e.g. the rotor cross-product derivation,
whose coefficients carry `1/‖a‖` and `1/c` (radical) denominators — expanding the
**denominator** distributes/denests it into something less readable. Bill wants
the **numerator expanded but the denominator left factored**.

## Where it is

`src/gacalc/nbplotutils.py`, `show_mult(a, b)` (~line 650):

```python
df_latex = df.map(
    lambda x: blade_dict_latex(x.expanded().to_blade_dict())
              if hasattr(x, "expanded") else x
)
...
display(Math("$" + blade_dict_latex((a * b).expanded().to_blade_dict()) + "$"))
```

The `.expanded()` is the `MultiVectorBase` coefficient-view helper in `base.py`
(alongside `.simplified()`), which maps `sympy.expand` over every coefficient via
`_map_coefficients`.

## Idea to investigate

Per-coefficient "expand the numerator, keep the denominator":

```python
import sympy
def _expand_numer(c):
    n, d = sympy.fraction(sympy.together(c))   # split into num / den
    return sympy.expand(n) / d                  # expand only the numerator
```

Options for wiring it in:
1. A new coefficient-view helper on `MultiVectorBase`, e.g. `expanded_numerators()`
   (mirrors `expanded()` / `simplified()`, via `_map_coefficients(_expand_numer)`),
   and have `show_mult` use it instead of `.expanded()`.
2. Or keep it local to `nbplotutils` if it's only a display concern.

## Open questions / things to check

- `together` then `expand(num)/den`: does it behave for purely-polynomial
  coefficients (no denominator) — should be a no-op-ish expand? Confirm.
- Radical denominators (`sqrt(a_x**2+a_y**2+a_z**2)`): does `fraction(together(...))`
  keep the radical in the denominator rather than rationalizing it? Verify it does
  NOT call `radsimp`/denest.
- Mixed sign / common-denominator behaviour across a blade's terms — is the
  result still legible, or does `together` over-combine?
- Should the final summed product (`(a*b)` line) use the same numerator-only
  expansion for consistency? (Probably yes.)
- Decide helper name + whether it belongs on the ABC (option 1) or in nbplotutils
  (option 2). If on the ABC, add a docstring + a small test like the other
  coefficient-view helpers.

## Verify

A notebook cell (e.g. the rotor cross-product `show_mult` steps in
`modelviewprojection`'s `notebooksrc/crossproduct.py`) renders with expanded
numerators and intact `1/‖a‖`-style denominators; a unit test on a hand-built
multivector with a rational coefficient confirms numerator expanded / denominator
untouched.
