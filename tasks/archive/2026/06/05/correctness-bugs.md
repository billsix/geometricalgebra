# Correctness bug fixes (backlog)

**Created:** 2026-06-04 · **Completed:** 2026-06-05

Three correctness issues found in the initial assessment (see `CLAUDE.md` "Assessment") were all
fixed and committed by the maintainer outside the container.

## What changed

1. **`reject`/`reflect` sequence handling (`base.py`).** Both called `cls.outer_product(*sequence)`,
   but `outer_product` is an instance method `(self, rhs)`, so it only worked by luck for exactly two
   elements. They now use `cls.outer_product_of_vectors(*sequence)`, as `project` already did.
   1-element-sequence regressions were added to `test_project_and_reject` and `test_reflect` (a
   1-element sequence used to raise `TypeError`).
2. **`__rmul__` negation (`base.py`).** The `case _:` fall-through returned
   `-self._geometric_product(lhs)`, which is wrong because the geometric product is not
   anticommutative. It was dead code (scalars hit earlier arms; MV*MV goes through `__mul__`), so it
   now returns `NotImplemented`, and any other left operand raises a clean `TypeError`. Nothing in
   the suite relied on it.
3. **Test copy-paste (`tests/test_multivector.py`).** `i15` in `test_multivector_unit_pseudoscalar`
   was built with `unit_pseudoscalar(14)`; it now uses `15`, so the grade-15 case is exercised (the
   assertion still holds: the 𝒢₁₅ pseudoscalar squares to −1).

## Found, out of scope

Fixing #1 showed that `reject`/`reflect` only implemented vector and bivector blades: a 3-element
span reduces to a trivector and fell through to `raise Exception("TODO - implement project for
...")`. Grade-3+ rejection/reflection was left as a separate gap.

## Verification

ruff clean, `ty check src` clean (including `NotImplemented`), full suite 124 passed.
