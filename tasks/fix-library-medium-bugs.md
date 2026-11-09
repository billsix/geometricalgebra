# Fix the medium library bugs in `base.py`, `transforms.py` and `frame.py`

**Status:** proposed — needs go-ahead (approved in session 2026-11-09; in progress)
**Priority:** 3
**Difficulty:** 4
**Created:** 2026-11-09
**Source:** `tasks/review/2026/11/08/repo-review.md` §4.2

## BLUF

Done means each bug below has a regression test (or doctest) that fails on the old code, and the
suite is green:

1. `A / k` for an int `k` gives floats, and `A / sympy.Integer(0)` gives `zoo`/`nan` instead of
   `ZeroDivisionError`.
2. `uniform_scale(m)`'s inverse is labelled `S_{-m}`.
3. `projection_rotation(a, a)` raises `ZeroDivisionError`, while `versor_rotation(a, a)` is the
   identity.
4. `scale_non_uniform` with fewer factors than the dimension zeroes the missing axes.
5. `bivector_rotation` raises `TypeError` for a wrong grade (`CLAUDE.md` reserves `TypeError` for
   `isinstance` checks).
6. In `frame.py`, a helper's vector parameter named `n` shadows the dimension `n`.
7. Bare `assert` vector checks remain in `base.py` and `transforms.py`. (The one in
   `nbplotutils.sine` is `tasks/fix-nbplotutils-sine.md`'s.)

## Context

Each finding was re-checked by running it (review §4.2). The rules are `CLAUDE.md`'s
`magnitude`/`inverse` "int stays exact" rule and the `require_vector` rule. `gacalc.base._reciprocal`
(added 2026-11-08) is the shared exact reciprocal.

## Plan

- [ ] Fix each one, with a doctest or a test.
- [ ] `CHANGELOG.md` `[Unreleased]` › Fixed entries for the behaviour changes (1, 3, 4, 5).
- [ ] Gate: `pytest -m "not slow"`, `ruff`, `ty` (with the generated modules).

## Open questions

None.
