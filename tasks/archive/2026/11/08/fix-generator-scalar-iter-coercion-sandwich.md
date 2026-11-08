# Fix three generator bugs: `Scalar.__iter__`, full `G` with a graded operand, inexact `sandwich`

**Created:** 2026-11-08 · **Completed:** 2026-11-08
**Source:** `tasks/review/2026/11/08/repo-review.md` §5.1

## What was wrong

Three bugs in `tools/gen_specialized.py`, present in every generated `g1`–`g3`:

1. **`Scalar.__iter__` yielded the `Scalar` itself, and nothing when it was zero.**
   `list(Scalar.from_real(3))` gave `[Scalar(3)]`, and `list(Scalar.from_real(0))` gave `[]`. The
   scalar's `__iter__` was hand-built; every other type uses `iter_method`.
2. **The full class `G` sent a graded operand of its own algebra to the slow `Gn`.**
   - `G.e_1 * Vector.e_1` and `G.e_1 + Vector.e_1` returned `Gn`.
   - The cause: the full-class `bilinear` (products) and `linear` (`__add__`/`__sub__`) emitters
     guarded with `if not isinstance(rhs, G): <Gn fallback>`.
3. **The closed-form `Versor.sandwich` turned integer input into floats.**
   - sympy's CSE reciprocal `Pow(|R|², −1)` was printed as `1/(…)`, which is float division in
     Python.
   - `(1 + 1*Versor.e_12).sandwich(1*e_1)` gave `Vector(0.0, -1.0)`.
   - Every `1/expr` in the generated code was such a reciprocal (1 in g2, 4 in g3, all in `sandwich`).

## What changed

- **`Scalar.__iter__`** is emitted with `iter_method([()])`, so it yields `coeff_scalar`.
- **`widen_same_algebra_rhs(n, full_name)`** is a new emitter. It produces
  `if isinstance(rhs, (Scalar, Vector, …)): rhs = G.from_blade_dict(rhs.to_blade_dict())`, placed
  ahead of the `Gn` guard in `bilinear` and `linear`. `Gn` and foreign operands still take the `Gn`
  path, which `test_mixing_with_gn_coerces_to_gn` pins.
- **`gacalc.base._reciprocal(x)`** is a new shared helper, imported by the generated modules like
  `_coerce`:
  - an `int` becomes an exact `sympy.Rational`, and integer 0 raises `ZeroDivisionError`;
  - a float or symbolic value is returned as `1 / x`;
  - it has doctests.

  **`ReciprocalToCall`** rewrites every `1 / x` that `expr_to_ast` produces into `_reciprocal(x)`.
  (g1 has no reciprocal, so the generator's ruff pass drops the unused import there.)
- **Regression tests**, each confirmed to fail on the old generator (8 failed):
  - `tests/test_graded.py::test_scalar_iteration_yields_its_coefficient` (g1–g3);
  - `tests/test_conformance.py::test_full_class_with_a_graded_operand_stays_the_full_class` (g1–g3,
    for `*`/`+`/`-`);
  - `tests/test_sandwich_grades.py::test_versor_sandwich_keeps_integer_input_exact` (g2/g3).
- **`CHANGELOG.md` `[Unreleased]` › Fixed:** an entry for each bug.

## Verification

- `pytest -m "not slow"` on the sandbox Python: 805 passed, 2 skipped.
- **Determinism:** regenerated twice, and `cmp` found g1–g3 identical.
- `tools/check_doc_regions.py`: OK.
- **`ty` on the generated g1–g3 + `base.py`:** 121 diagnostics, the same count as on the old
  generator, so no new ones. That pre-existing count is the gap tracked by
  `tasks/test-all-dims-ty-gate.md`.
- `ruff check`/`ruff format`: clean.
