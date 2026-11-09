# Reconcile `CLAUDE.md`'s dot-product rule, and record the unrecorded decisions

**Status:** proposed — needs go-ahead (approved in session 2026-11-09; in progress)
**Priority:** 3
**Difficulty:** 2
**Created:** 2026-11-09
**Source:** `tasks/review/2026/11/08/repo-review.md` §1.1, §2.3

## BLUF

`CLAUDE.md` says both "write `a.dot(b).scalar_part()` for vectors" (2026-11-04) and "dot =
`scalar_product`" (two older bullets), and some code follows the older wording. Several decisions
still in force are recorded nowhere. Done means one dot-product rule throughout, the code following
it, and each decision written where a reader looks for it.

## Context

- **The dot-product contradiction:**
  - the rule is `CLAUDE.md` › "Conventions" (2026-11-04);
  - the old wording is in the `vectorcalc` module bullet, the Operators "cross product" line, and
    `src/gacalc/vectorcalc.py`'s module docstring;
  - code using `scalar_product` for two vectors: `notebooks/displayvectorcalc.py`,
    `tests/test_vectorcalc.py`, `tests/test_rotor_from_vectors.py`.
- **Decisions to record** (review §2.3):
  - the scope of "build vectors from basis constants" (teaching-facing code; tests may use the
    constructor);
  - `bivector_rotation` among the rotation factories;
  - the `displayvectorcalc` `i, j, k` alias;
  - "symbolic tests write their vectors inline" (and how that sits with the `FRAMES` parametrize;
    the maintainer took the reviewer's recommendation, 2026-11-09);
  - "notebooks use `display`, not `print`";
  - a `CHANGELOG.md` pointer in the README.

## Plan

- [ ] Make the two old `CLAUDE.md` bullets and `vectorcalc.py`'s docstring say
  `a.dot(b).scalar_part()`; change the three code sites.
- [ ] Add the scope clause, the factory, and the alias carve-out to `CLAUDE.md`. Add the inline-tests
  and `display` sections to `tasks/reference/python-coding-standard-gacalc.md`. Add the README
  pointer.
- [ ] Gate: `pytest` on the touched tests, the notebook runs, `ruff`, `ty`.

## Open questions

None.
