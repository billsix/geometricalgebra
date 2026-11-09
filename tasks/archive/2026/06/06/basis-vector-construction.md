# Build multivectors from basis vectors, not blade-dict literals

**Created:** 2026-06-06 · **Completed:** 2026-06-06

Blade-dict literals such as `gn({(1,): 1, (2,): 2, (3,): 3})` were replaced, where it helped, by
linear combinations of the basis vectors (`1 * gn.e_1 + 2 * gn.e_2 + 3 * gn.e_3`). This reads like
the mathematics, matches how `displaygraded.py` / `displayg2.py` already build values, and for the
typed classes goes through `__rmul__`/`__add__`, sidestepping the `numbers.Real` field-annotation
friction that bare constructors hit. Generated code was out of scope: its `from_blade_dict` bodies
are the interchange primitive, and `gn.py`/`g*.py` define the `e_*` constants through it.

## Decisions

- **Module-qualified style** (confirmed by the maintainer): `import geometricalgebra.gn as gn`, then
  `gn.e_1`, so a file does not import a pile of names.
- **Blades** are built with the wedge, always parenthesized because `^` binds loosely in Python:
  `(gn.e_1 ^ gn.e_2)`. `gn` exports only vector constants `e_1 … e_10` plus `zero`/`one`; scalars
  are `k * gn.one`.
- **Scope: `tests/test_graded.py` only**, the primary, high-value target. Left as dict literals, by
  the per-case judgement the task called for:
  - `tests/test_multivector.py` — its `MultiVector({...})` values are expectations in
    geometric-product tests; building them from basis vectors uses the product (the wedge routes
    through it in the ABC), which would make the ground truth circular.
  - `tools/bench.py` and the dense/generated dicts in `tests/test_conformance.py`
    (`{b: base+i+1 for b in blades(n)}`, `{(i,): i for i in range(1, n+1)}`) read worse as basis
    combinations; the few trivial `Gn.from_blade_dict({(1,): 1})` spots there were already clear.

## What changed

In `tests/test_graded.py` the local `def gn(d)` dict→`Gn` helper was replaced by the module import,
and every `gn({...})` expected value became a basis combination (`3 * gn.e_1 + 4 * gn.e_2`). The
expectations stayed general `Gn` values, so the cross-representation `typed == Gn` check is kept.

## Verification

`ty` and `ruff` clean on tests; 141 tests pass.
