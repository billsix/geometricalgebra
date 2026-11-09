# Understand & document gacalc's symbolic equality; expand tests

**Created:** 2026-08-27 · **Completed:** 2026-08-27 (split into a reference doc + a follow-on task)

## Origin

Maintainer idea (2026-08-27 batch): *"Understand sympy equal better, expand on tests, figure out if I can
use how that works."* Created as `symbolic-equality-reference-and-tests.md`, which bundled two halves.

## Outcome — split into a reference doc + a follow-on task

- **Understand half → done.** Documented in **`tasks/reference/symbolic-equality.md`**: how gacalc's
  symbolic equality works (the generated `__eq__` = per-field `structural == OR simplify(sympify(l) −
  sympify(r)) == 0`, emitted by `tools/gen_specialized.py`), its limits (`simplify` is heuristic —
  possible false negatives, never false positives), and the duplicated test helpers (`_same_value`,
  `simplify_equal`). The numeric sibling is `tasks/reference/approximate-float-equality.md`.
- **Expand/use half → follow-on task** `tasks/archive/2026/10/05/consolidate-symbolic-equality-predicate.md`,
  which at the split awaited one API decision: expose a public `MultiVectorBase.symbolically_equal` or
  keep a test-only helper.

This record exists so the split is discoverable; the reference doc holds the durable knowledge.
