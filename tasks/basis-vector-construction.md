# Build multivectors from basis vectors, not blade-dict literals

**Status:** proposed — needs go-ahead
**Started:** 2026-06-06

## Goal

Across the codebase (and especially the tests), replace `from_blade_dict` / `gn({...})`-style dict
literals such as

```python
gn({(1,): 1, (2,): 2, (3,): 3})
gn({(): 2, (1, 2): 3})
```

with readable **linear combinations of the standard basis vectors**, e.g.

```python
1 * gn.e_1 + 2 * gn.e_2 + 3 * gn.e_3
2 * gn.one + 3 * (gn.e_1 * gn.e_2)
```

Per the user, prefer the **module-qualified** form (`gn.e_1`, `g2.e_1`, …) so a file doesn't have to
import a pile of names into its namespace — `import geometricalgebra.gn as gn` then `gn.e_1`.

## Why

Reads like the mathematics, matches how `displaygraded.py` / `displayg2.py` already build values, and
(for the typed classes) goes through `__rmul__`/`__add__`, which sidesteps the `numbers.Real`
field-annotation friction that bare constructors trip.

## Scope / where to change

- **Primary: the tests.** `tests/test_graded.py` (expected values still use `gn({...})`),
  `tests/test_conformance.py`, `tests/test_multivector.py`.
- **`tools/bench.py`** sample inputs, where it doesn't obscure intent.
- **Notebooks**, if any remaining dict literals read worse than a basis combination.
- **Do NOT touch generated code** (`g1/g2/g3.py`, `scalar.py`) — their `from_blade_dict` bodies are
  the interchange primitive and are emitted by the generator. And `gn.py`/`g*.py` *define* the
  `e_*` constants via `from_blade_dict`, which obviously can't be rewritten in terms of themselves.

## Notes / considerations

- **Basis coverage:** `gn` exports vector constants `e_1 … e_10` plus `zero`/`one`, but **not** named
  blade constants like `e_12`. Build higher blades as products: bivector `gn.e_1 * gn.e_2`, trivector
  `gn.e_1 * gn.e_2 * gn.e_3`, scalar `k * gn.one`. (The specialized modules `g2`/`g3` *do* export
  `e_12` etc., so within those a named constant is available.)
- **Geometric vs. wedge for blades:** for orthogonal basis vectors `e_i * e_j == e_i ^ e_j`, so the
  product is fine for constructing a basis blade; use `^` if you want to be explicit that it's a
  blade.
- **Mild circularity:** building an *expected* value via the geometric product uses the very
  operation some tests exercise. It's fine for simple vector/scalar expectations, but for a test
  whose subject *is* the product, keep the expected side as a basis combination that doesn't depend
  on the product under test (or leave a dict literal there) — judgement per case.
- **Equality still works** across representations via the simplify-aware `__eq__` (e.g. a `Vector2`
  built from `g2.e_1`/`g2.e_2` compares equal to a `gn(...)` or `Gn`-built value).
- Keep `ty check tests` + ruff clean; re-run the suite (currently 135 tests).

## Open questions

- Confirm the **module-qualified** style (`import geometricalgebra.gn as gn`; `gn.e_1`) as the
  convention, vs. importing the names.
- How far to take it — all three test files + bench, or start with `test_graded.py` and `bench.py`?
- Any spots where a dict literal is genuinely clearer (e.g. a dense full multivector with all 2ⁿ
  coefficients) and should be left as-is?
