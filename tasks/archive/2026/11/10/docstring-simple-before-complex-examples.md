# Every example shows a simple case first, then the general one

**Created:** 2026-11-10 (William Emerison Six <billsix@gmail.com>) · **Done:** 2026-11-10

The maintainer's request: keep the existing examples (arbitrary and symbolic vectors) and put simple
ones in front, so a student gets a quick feel for the operation. For `project`: onto `e_1`, then onto
`3 * e_1`, showing that the length of the onto-vector does not matter. Scope decision (William Emerison
Six <billsix@gmail.com>, 2026-11-10): hand-written docstrings and generator-emitted docstrings;
`tests/` and the notebooks unchanged.

Done by three fresh subagents on disjoint files, with no git access, reviewed and committed one step
per file group:

- **`src/gacalc/base.py`:** 73 public methods and operators, insert-only (925 lines). Skipped: the
  abstract/interchange plumbing, `basis_vector` (its only example would break "use the constant"), and
  methods whose examples were already simple. `__lt__`/`__gt__` examples are parenthesized, because
  Python chains `<` with `==`.
- **The other hand-written modules:** 41 callables in `transforms.py`, `functions.py`, `gn.py`,
  `frame.py`, `measure.py`, `standardposition.py` (`vectorcalc.cross` already led with simple ones).
  Six existing examples that called `translate`/`uniform_scale` positionally were changed to `b=`/`m=`
  (the protected-name keyword rule).
- **The generator** (`tools/gen_specialized.py`): the existing example-bearing `CUSTOM_METHOD_DOCS`
  entries got simple cases first, and the ~105 entries that rendered no example (so they hid the base
  docstrings' new examples) got one. New helper `_by_dimension`, unit-blade callables for
  `*|__eq__`/`*|__rsub__`, and documented `rel_tol`/`abs_tol` on `isclose`. **A false claim fixed on the
  way:** `versor|dual` said the dual of a versor is even, which is true in 𝒢₂ only; in 𝒢₃ it is an
  `Odd_3`, which the code already returned. Mechanism: `tasks/reference/generated-docstrings.md`.
- Earlier the same day, the guards, the rotation factories and `to_matrix` got simple-first doctests
  in their own tasks.
- **Inventory:** `tasks/adhoc/docstring-simple-before-complex-examples/inventory.py` (141 public
  callables, 72 with no doctest at the start); a one-shot, removed at archive.
- **Not done:** seven existing generated doctest lines in g2/g3 exceed 88 columns; left as they are,
  since the generated modules are not under the line-length gate.
- **Gate (host):** ruff + ty clean; generator deterministic (two runs byte-identical);
  `pytest -m "not slow"` 1184 passed (up from 821 at the start of the batch).
