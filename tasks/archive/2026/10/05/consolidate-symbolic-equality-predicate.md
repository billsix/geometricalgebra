# Consolidate the symbolic-equality predicate; expand symbolic tests

**Status:** done 2026-10-05 (Q1 (a), Q2 (a) decided by the maintainer; 695 tests, format/ty green); archived 2026-10-05
**Priority:** 6
**Difficulty:** 3
**Started:** 2026-08-27 (William Emerison Six <billsix@gmail.com>)
**Blocked on:** two small API decisions (Q1–Q2 below). The reference-doc half is DONE
(`tasks/reference/symbolic-equality.md`); this is the actionable follow-on.
**Recheck:** Q1 and Q2 are answered (maintainer-gated; `/recheck-blocked` surfaces it).


**Update 2026-09-09 (does not unblock this task; Q1–Q2 are still open):** the per-coefficient rule now
lives in one place — `base._coef_eq` in `src/gacalc/base.py`, added by
`tasks/archive/2026/09/09/fast-numeric-equality.md`. The generated `__eq__` calls it from both its
same-type and blade-dict paths. Whatever this task decides for Q1, the public predicate should
delegate to `_coef_eq` per blade rather than re-implement `simplify(a − b) == 0`; that removes the
"which of the three copies is canonical" part of the problem, leaving the API questions untouched.

## Goal

Maintainer's idea, verbatim: *"Understand sympy equal better, expand on tests, figure out if I can use
how that works."* The **understand** half is done — `tasks/reference/symbolic-equality.md` documents how
gacalc's symbolic equality works (the generated `__eq__` = per-field `structural == OR simplify(sympify(l)
− sympify(r)) == 0`, its limits, and the duplicated test helpers). This task is the **use/expand** half:
consolidate the duplicated helpers into one public predicate and grow the symbolic tests.

## Context (from the reference doc — verified)

- The `simplify(a − b) == 0` logic lives in the generated `__eq__` (`tools/gen_specialized.py` ›
  `eq_method()`, whose `field_equal` helper emits `_coef_eq(...)` per field) and is **re-implemented
  ad hoc** in tests: `_same_value()` (`tests/test_conformance.py`), `simplify_equal()`
  (`tests/test_graded.py`), plus inline one-offs (`scalar_eq()` in `tests/test_conformance.py`; the
  `content` assertions in `tests/test_measure.py` ›
  `test_content_two_ways_both_give_the_determinant_symbolic`). No public
  `MultiVectorBase.symbolically_equal` exists (re-verified 2026-10-04).
- Numeric equality (`MultiVectorBase.isclose` in `src/gacalc/base.py`) is the separate,
  already-documented sibling (`tasks/reference/approximate-float-equality.md`).

## Plan (draft — after Q1)

- [ ] Add a public predicate (e.g. `MultiVectorBase.symbolically_equal(other)`) that does the blade-dict
      `simplify(a − b) == 0` comparison in one place (`src/gacalc/base.py`).
- [ ] Replace `_same_value` / `simplify_equal` / the inline idioms in tests with it.
- [ ] Expand symbolic-equality tests (the `simplify`-can't-prove-it false-negative cases from the
      reference doc's "Limits" are good targets to pin behavior).
- [ ] `ruff` + `ty check src tests` + full suite green.

## Open questions

1. **Expose it how?** (a) a public `MultiVectorBase.symbolically_equal(other)` method (recommended —
   one home, used by both tests and callers), or (b) a test-only helper consolidated in `tests/`?
2. **Return type?** (a) a plain `bool` (matching `_same_value`; recommended — documented to be
   conservative, a `False` may mean "not proven equal," per the reference doc's Limits), or (b)
   raise/flag "undecided" separately when `simplify` can't prove it?

## Decisions and work record (2026-10-05)

- **Q1 → (a) a public method** `MultiVectorBase.symbolically_equal(other, *, subs=None)`; **Q2 → (a) a
  plain `bool`**, conservative (`False` = not proven equal). Decided by the maintainer 2026-10-05.
- Implementation (`src/gacalc/base.py`): blade-dict-wise over the union of present blades, so any two
  representations compare; per blade it delegates to `_coef_eq` (the generated `__eq__`'s rule — exact for
  plain numbers, `simplify`-backed when a side is symbolic). With `subs` (type
  `gacalc.base.SymbolicSubstitution = Mapping[sympy.Basic | complex, sympy.Expr | complex]`) it applies the
  substitution to each blade's difference before `simplify` — the "hand sympy the relation" recipe from
  the rotor work (`{s**2: 1 - c**2}`), which is why the parameter exists.
- The three hand-rolled copies were removed and their call sites rewritten to the method:
  `test_conformance._same_value` (3 sites), `test_graded.simplify_equal` (2), and
  `test_rotor_from_vectors._simplify_equal` (10). Scalar-level one-offs (`scalar_eq`, the `content`
  assertions in `test_measure.py`) compare `Coef`s, not multivectors, and stay.
- New `tests/test_symbolic_equality.py` pins: structurally-different-but-equal forms, unequal values and
  a blade present on one side only, exact numeric comparison, cross-representation (`Gn` vs `g2`), and the
  substitution path (`sqrt(4c⁴ + 4s²c²)` vs `2c`: `False` without the relation, `True` with it).
- Docs: `symbolic-equality.md` "The public predicate" section replaces the "currently duplicated" one;
  README and `CLAUDE.md` one-liners; `CHANGELOG` Added.
