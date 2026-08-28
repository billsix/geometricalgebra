# Understand & document gacalc's symbolic equality; expand tests

**Status:** DONE / split 2026-08-27 (William Emerison Six <billsix@gmail.com>). Archived lean record.

## Origin

Maintainer idea (2026-08-27 batch): *"Understand sympy equal better, expand on tests, figure out if I can
use how that works."* Created as `symbolic-equality-reference-and-tests.md`, which bundled two halves.

## Outcome — split into a reference doc + a follow-on task

- **Understand half → DONE.** Documented in **`tasks/reference/symbolic-equality.md`**: how gacalc's
  symbolic equality works (the generated `__eq__` = per-field `structural == OR simplify(sympify(l) −
  sympify(r)) == 0`, `tools/gen_specialized.py:873-923`), its limits (`simplify` is heuristic — possible
  false negatives, never false positives), and the duplicated test helpers (`_same_value`,
  `simplify_equal`). The numeric sibling is `approximate-float-equality.md`.
- **Expand/use half → follow-on task** `tasks/consolidate-symbolic-equality-predicate.md` (blocked on one
  small API decision: expose a public `MultiVectorBase.symbolically_equal` vs a test-only helper).

This record exists so the split is discoverable; the reference doc holds the durable knowledge and the
follow-on task carries the remaining work.
