# Fix the medium library bugs in `base.py`, `transforms.py` and `frame.py`

**Created:** 2026-11-09 · **Completed:** 2026-11-09
**Source:** `tasks/review/2026/11/08/repo-review.md` §4.2

## What was wrong, and what changed

1. **`MultiVectorBase.__truediv__` by a number** multiplied by `1 / rhs`. So `(1 * e_1) / 3` gave
   `0.333…`, and `/ sympy.Integer(0)` gave `zoo`/`nan`. It now divides coefficient by coefficient:
   int / int becomes an exact `sympy.Rational`, a float stays a float (the docstring's
   `[1.5, 2.0]` example still holds), and a symbolic value stays symbolic. Any zero number raises
   `ZeroDivisionError`. The docstring says so.
2. **`uniform_scale(m)`'s inverse label** was `S_{-m}`. It is now `S_{\frac{1}{m}}`, matching
   `scale_non_uniform`.
3. **`projection_rotation(a, a)`** inverted a zero plane. For parallel vectors it now returns:
   - the identity on vectors when they point the same way (sympy's `is_positive` on `a·b`), as
     `versor_rotation` does;
   - a `ValueError` saying no plane of rotation is defined when they point opposite ways.
     (`versor_rotation` raises `ZeroDivisionError` there.)
4. **`scale_non_uniform`** summed `m * component` over only the given axes, so a missing axis
   became 0. It now starts from the vector and adds `(m − 1)` times each given axis's component, so
   an axis with no factor is unchanged. The docstring has a doctest. The body is a doc region; no
   book page includes it.
5. **`bivector_rotation`** raised `TypeError` for a non-bivector. It now raises `ValueError`, per
   `CLAUDE.md`'s rule, and `tests/test_bivector_rotation.py` was updated to match.
6. **`Frame.to_invertible_function`'s `term_and_coordinate`** named its normal-vector parameter `n`,
   shadowing the dimension `n`. It is now `m`, and the `CLAUDE.md` module-layout bullet says `m`
   too.
7. **The bare `assert value.is_vector()`** in `MultiVectorBase.reject`'s closure and in
   `projection_rotation`'s is now `MultiVectorBase.require_vector(...)`. (The internal `assert`s in
   the homogeneous-product dispatch are invariants, not input checks, and stay.)

**Tests and changelog:**

- **New tests:** `tests/test_transforms.py` (the label; the unchanged axis plus the inverse;
  `a → a` and `a → 3 * a`; opposite vectors; a non-vector operand) and `tests/test_multivector.py`
  (exact int division; zero as an int, a float and a sympy zero). 7 of them fail on the old code.
- **`CHANGELOG.md` `[Unreleased]` › Fixed:** an entry for each behaviour change.

## Verification

- `pytest -m "not slow"`: 762 passed, 2 skipped.
- `ty check --no-respect-ignore-files src` and `ty check tests`: clean. `ruff`: clean.
