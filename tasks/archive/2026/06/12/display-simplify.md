# Display simplification for G1/G2/G3

**Created:** 2026-06-04 · **Completed:** 2026-06-12

## Background

The specialized-multivector work (`tasks/archive/2026/06/03/specialized-multivectors.md`) set the
coefficient policy "symbolic, but lazy simplify": `Gn` eager-simplifies, `G1`/`G2`/`G3` simplify
lazily, and its Decision 1 said the specialized classes should simplify on display as well as on
equality. Equality had been done (their `__eq__` simplifies the per-blade difference), but display had
not: `G1`/`G2`/`G3` inherited `_repr_latex_` from `base.py`, which rendered the raw coefficients — not
wrong, but not always in lowest terms.

## What was done

`AbstractMultiVector._repr_latex_` in `base.py` (inherited by every representation, so no
regeneration) renders the **simplified** view: it reads `self.simplified().to_blade_dict()` instead of
`self.to_blade_dict()`. The lazy classes (G1/G2/G3 and the graded subtypes) display coefficients in
lowest terms (`sin²+cos² → 1`, a bivector times its dual whose terms cancel) while the stored fields stay
lazy. The zero check became `not d` (an empty simplified blade-dict means the value simplified to zero).
On `Gn`, which already eager-simplifies, it is a cheap no-op.

It used the shared primitive built on 2026-06-11: `MultiVectorBase._map_coefficients` +
`.simplified()` / `.expanded()` in `base.py`, which map a sympy op over the coefficients via the
blade-dict interchange, are inherited by every representation, and are tested in
`tests/test_conformance.py`.

Test: `test_repr_latex_shows_simplified` (stored stays raw, displayed is simplified). The full suite
passed (221), ty and ruff clean.

## Decisions

- **A `.simplified()` helper as well as display:** the helper already existed; display uses it.
- **`__repr__` not simplified.** It stays the raw dataclass repr (`Vector2(coeff_e_1=…, …)`), the honest
  stored state for debugging; `_repr_latex_` is the user-facing render. The alternatives sketched first
  — a generated `_repr_latex_` override on G1/G2/G3, or a class-flag hook in the ABC — were unnecessary
  once the base method could call `.simplified()`.
- **Cost accepted:** display is not hot; one simplify pass per shown value.

This covered the display half of `tasks/archive/2026/06/12/graded-bivector-dual-simplify.md`: a
bivector × dual renders cancelled in any notebook cell without an explicit `.simplified()` call.
