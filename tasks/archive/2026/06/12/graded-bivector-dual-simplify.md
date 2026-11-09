# Graded types: make bivector * dual simplify (cancellation) — at least in the notebook

**Created:** 2026-06-11 · **Completed:** 2026-06-12

## Symptom (the maintainer, 2026-06-11)

For the graded subtypes, a bivector times its dual should cancel terms, but the displayed result showed
uncancelled symbolic coefficients. The graded subtypes deliberately do not eager-simplify (lazy policy:
simplify only on equality, unlike `Gn`, which simplifies in `__post_init__`), so a product such as
`Bivector3 * Bivector3.dual()` kept raw per-blade coefficients (`a*b - b*a` left as is). (`dual` of a
`Bivector3` narrows to `Vector3`, and `Bivector3 * Vector3` with support `{1,3}` then widened to `G3` —
see `tasks/archive/2026/09/05/model-odd-graded-type.md`.) The maintainer wanted to ensure the result
*can* be simplified and that the notebook shows the cancellation, even by an explicit call.

## What was done

1. **The simplify path.** The shared primitive was built first (2026-06-11):
   `MultiVectorBase._map_coefficients` + `.simplified()` / `.expanded()` in `base.py`, mapping a sympy
   op over the coefficients via the blade-dict interchange, inherited by `Gn`/`G1`/`G2`/`G3` and the
   graded subtypes, tested in `tests/test_conformance.py`. It was made a real method rather than a
   notebook-local helper, being small, broadly useful, and the same shape the display work and the
   show_mult `expanded()` idea needed (the separate `show-mult-expand` task doc no longer exists).
   Then `tasks/archive/2026/06/12/display-simplify.md` made `_repr_latex_` render the simplified view
   for every representation, so a bivector × its dual displays cancelled with no explicit call.
2. **Symbolic confirmation and a teaching cell.** `B · B.dual() = |B|² I` (a trivector) was confirmed;
   for a general bivector the closed form is already clean (`(a²+b²+c²) e₁₂₃`), so the simplification
   matters when coefficients reduce. A cell was added to `notebooks/displaygraded.py`: the unit
   bivector `B = cos(t) * (e₁∧e₂) + sin(t) * (e₁∧e₃)`, whose `B · B.dual()` stores
   `(cos²(t)+sin²(t)) * e₁₂₃` but displays as `e₁₂₃`. `import sympy` was added; the notebook ran
   headless (exit 0) and ruff was clean.

Scope decision: the helper plus the one notebook cell were done here, and display-wide simplification
was left to its own task (`display-simplify`, which then did it).
