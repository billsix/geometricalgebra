# Consolidate the symbolic-equality predicate; expand symbolic tests

**Status:** blocked
**Priority:** 6
**Difficulty:** 3
**Started:** 2026-08-27 (William Emerison Six <billsix@gmail.com>)
**Blocked on:** one small API decision (Q1 below). The reference-doc half is DONE
(`tasks/reference/symbolic-equality.md`); this is the actionable follow-on.
**Recheck:** Q1 is answered (maintainer-gated; `/recheck-blocked` surfaces it).

## Goal

Maintainer's idea, verbatim: *"Understand sympy equal better, expand on tests, figure out if I can use
how that works."* The **understand** half is done — `tasks/reference/symbolic-equality.md` documents how
gacalc's symbolic equality works (the generated `__eq__` = per-field `structural == OR simplify(sympify(l)
− sympify(r)) == 0`, its limits, and the duplicated test helpers). This task is the **use/expand** half:
consolidate the duplicated helpers into one public predicate and grow the symbolic tests.

## Context (from the reference doc — verified)

- The `simplify(a − b) == 0` logic lives in the generated `__eq__` (`tools/gen_specialized.py:873-923`)
  and is **re-implemented ad hoc** in tests: `_same_value` (`tests/test_conformance.py:401`),
  `simplify_equal` (`tests/test_graded.py:381`), plus inline one-offs (`tests/test_conformance.py:87`,
  `tests/test_measure.py:139-140`). No public `MultiVectorBase.symbolically_equal` exists.
- Numeric equality (`isclose`, `base.py:1207`) is the separate, already-documented sibling
  (`approximate-float-equality.md`).

## Plan (draft — after Q1)

- [ ] Add a public predicate (e.g. `MultiVectorBase.symbolically_equal(other)`) that does the blade-dict
      `simplify(a − b) == 0` comparison in one place (`src/gacalc/base.py`).
- [ ] Replace `_same_value` / `simplify_equal` / the inline idioms in tests with it.
- [ ] Expand symbolic-equality tests (the `simplify`-can't-prove-it false-negative cases from the
      reference doc's "Limits" are good targets to pin behavior).
- [ ] `ruff` + `ty check src tests` + full suite green.

## Open questions

1. **Expose it how?** A public `MultiVectorBase.symbolically_equal(other)` method (recommended — one home,
   used by both tests and callers), or keep it a test-only helper consolidated in `tests/`? And should it
   return a plain `bool` (matching `_same_value`) — i.e. is a False on a `simplify`-can't-prove case
   acceptable, or do you want it to raise/flag "undecided" separately? *(Recommend: a `bool` method on
   `MultiVectorBase`, documented to be conservative — a `False` may mean "not proven equal," per the
   reference doc's Limits.)*
