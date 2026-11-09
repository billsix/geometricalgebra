# Reconcile `CLAUDE.md`'s dot-product rule, and record the unrecorded decisions

**Created:** 2026-11-09 · **Completed:** 2026-11-09
**Source:** `tasks/review/2026/11/08/repo-review.md` §1.1, §2.3

## What changed

- **One dot-product rule.**
  - `CLAUDE.md`'s `vectorcalc` module bullet and its Operators "cross product" line said "dot =
    `scalar_product`". They now say `a.dot(b).scalar_part()` for two vectors, matching the
    2026-11-04 convention.
  - So does `src/gacalc/vectorcalc.py`'s module docstring, which also now points at the archived
    path of the task it cites.
  - The code that followed the old wording now uses `.dot(...).scalar_part()`:
    `notebooks/displayvectorcalc.py` (prose and cell), `tests/test_vectorcalc.py`, and
    `tests/test_rotor_from_vectors.py`.
- **Decisions recorded:**
  - `CLAUDE.md` › "Build vectors from the basis constants" now states its scope: teaching-facing
    code; tests may call the constructor, and product tests keep blade-dict literals.
  - `CLAUDE.md` names `bivector_rotation` among the rotation factories, in the module layout and in
    Operators.
  - `CLAUDE.md`'s alias carve-out adds `displayvectorcalc`'s `i, j, k`.
  - `tasks/reference/python-coding-standard-gacalc.md` gains "Symbolic tests write their vectors
    inline": no shared `sym_vec_*` fixtures, and parametrize only over named variants written out
    inline. That is the reviewer's recommendation, which the maintainer took on 2026-11-09.
  - The same doc gains "Notebooks show values with `display(...)`, never `print`".
  - `README.md` › "Contributing" points at `CHANGELOG.md`. (The README's other changes in this
    batch, its math spacing, belong to `tasks/archive/2026/11/09/book-notation-sweep.md`.)

## Verification

- `tests/test_vectorcalc.py` and `tests/test_rotor_from_vectors.py`, plus `vectorcalc`'s doctests:
  19 passed.
- `notebooks/displayvectorcalc.py` runs.
- `ruff`: clean.
