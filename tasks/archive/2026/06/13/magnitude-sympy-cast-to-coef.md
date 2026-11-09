# Why is multiplying magnitudes cast to a sympy expression instead of Coef?

**Created:** 2026-06-13 · **Completed:** 2026-06-13

## The question

The maintainer asked why something was cast to a sympy expression when it was just multiplying
magnitudes together, rather than staying a plain `Coef` (`int | float | sympy.Expr`, `base.py`), and
suspected a workaround from when casting to `Coef` did not work. The candidates found:

- `magnitude()` returned `sympy.sqrt(self.magnitude_squared())`, and `sympy.sqrt` always returns a
  `sympy.Expr`, so `abs(a) * abs(b)` (in `rotor_from_vectors`, and `cosine()`) was always sympy.
- `mag_sq = sympy.sympify(self.magnitude_squared())` in `inverse()` was deliberate: its comment said
  that for the specialized representations the value "silently degrades to a float — sympify keeps it
  exact (Rational)". That exactness was the original reason for the cast, and the cleanup had to keep
  it.

## Outcome

Resolved in two parts:

- **Functional**, through `tasks/archive/2026/06/13/magnitude-numeric-for-numeric-input.md`:
  `magnitude()` and `inverse()` keep `float` input numeric, so multiplying magnitudes no longer produces
  sympy for numeric input, while `int` stays exact (`Rational`) and symbolic stays symbolic. The
  `sympify` in `inverse()` was replaced by that numeric/exact split, which keeps the exactness the cast
  had protected.
- **Cosmetic**, here: the rotor scalar was built via `from_sympy_expr(scale)`, a constructor whose name
  looked like a sympy cast but which is just `from_blade_dict({(): s})`. It was renamed
  **`from_sympy_expr` → `from_coef`** (definition and callers in `base.py`, and the `_coerce` template
  in `tools/gen_specialized.py`) and the `g*.py` were regenerated.

The magnitude-product question of `tasks/archive/2026/06/27/geometric-product-magnitude-proof.md`
(`abs(from*to)` instead of `abs(from)*abs(to)`) overlapped and was handled in that task.

## Verification

The full suite passed (225, incl. doctests); the generator output was byte-deterministic; no
`from_sympy_expr` remained anywhere.
