# magnitude() should return a Python number for numeric input (don't poison numeric pipelines)

**Status:** proposed — not started
**Created:** 2026-06-13

## Goal

`MultiVectorBase.magnitude()` is `sympy.sqrt(magnitude_squared())` (`base.py:229`),
so it returns a **sympy expression even when every coefficient is a plain Python
number**. That sympy-ness propagates through the rotor path
(`rotor_from_vectors` uses `|from||to|`; `rotate`/`sandwich`), so rotating a
*numeric* vector yields **sympy** coefficients. Downstream numeric consumers then
break — concretely, modelviewprojection's GL matrices become numpy
**`dtype=object`** and `np.linalg.inv` throws (see `[[mvpviz-focus-failure]]` in
the mvp repo).

Make `magnitude()` (and the rotor path that depends on it) return a **Python
float** when the input is numeric, while preserving full **symbolic** behavior when
coefficients are sympy. Numeric in → numeric out; symbolic in → symbolic out.

## Evidence

Against gacalc 0.0.3 (the released/pinned version): `abs(Vector3(1.0,0.0,0.0))`
and `rotate`/`rotate_z` of a numeric `Vector3` return coefficients of sympy type
(`Float`, `Float`, `Zero`), not Python `float`. mvp's `to_matrix` then builds a
`dtype=object` array and `np.linalg.inv` raises
`UFuncTypeError: Cannot cast ... dtype('O') to dtype('float64')`.

## Plan

- [ ] **Reproduce in gacalc.** Confirm `magnitude()` / `abs()` of an all-numeric
      multivector returns a sympy `Float`, and that `rotor_from_vectors` /
      `rotate` / `sandwich` of numeric vectors carry sympy through to the result.
- [ ] **Decide the approach.** Likely a numeric fast-path in `magnitude()`: if all
      coefficients are Python numbers (`int`/`float`), use `math.sqrt` and return a
      `float`; otherwise `sympy.sqrt`. Keep `Coef = int | float | sympy.Expr`
      honest (a number stays a number). Verify the same numeric-preservation holds
      across the even-grade product / `normalize` used by the rotor.
- [ ] **Trace the whole rotor path.** `rotor_from_vectors` (`base.py:686`),
      `sandwich` (`base.py:755`), `normalize` (`base.py:242`) — ensure numeric in
      stays numeric end-to-end (no sympy reintroduced by an intermediate).
- [ ] **Respect codegen + doctests.** Specialized reps (`g2`/`g3`) are generated —
      change the generator/source and regenerate, don't hand-edit; keep
      `--doctest-modules` examples valid.
- [ ] **Add tests.** Assert `type(abs(numeric_vector)) is float` (and the rotated
      vector's coefficients are Python floats), alongside the existing symbolic
      tests so symbolic mode is proven unaffected.

## Notes / decisions

- **mvp keeps its own float-coercion even after this lands.** This gacalc fix
  stops *surprising* sympy leakage and helps every consumer, but mvp must still
  coerce to `float` at its numpy/GL boundary (numpy/OpenGL need `float64`; gacalc
  may legitimately return sympy in symbolic mode). The two are complementary; the
  mvp guard is not made redundant. (Mirrored in `[[mvpviz-focus-failure]]`.)
- Closely related to `[[magnitude-sympy-cast-to-coef]]` (same `magnitude` path,
  the `sympify`/`Coef` question) and `[[geometric-product-magnitude-proof]]` (the
  rotor magnitude) — consider doing them together; this one is the
  consumer-driven motivation.
- gacalc deliberately runs symbolic via sympy and `Gn` eager-simplifies — the fix
  must not weaken symbolic mode.

## Open questions

- Numeric fast-path inside `magnitude()` only, or a broader "stay numeric for
  numeric coefficients" pass across the magnitude/rotor/normalize chain?
- Treat `sympy.Float`/`sympy.Integer` (numeric sympy) as "numeric" and downcast to
  Python float, or only bare Python numbers?
