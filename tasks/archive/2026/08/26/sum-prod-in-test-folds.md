# Use `sum` for the hand-rolled fold loops in tests

**Created:** 2026-08-26 · **Completed:** 2026-08-26

## Goal

The `CLAUDE.md` convention "Reduce with `sum` / `math.prod`, not a hand-rolled accumulator loop"
(added 2026-08-26, motivated by `measure.content_by_rejection`'s `math.prod`) was applied to the test
code, where the 2026-08-26 sweep found the only remaining candidates. `src/gacalc/` already used
`sum`/`math.prod`/`reduce`; the `frame.py` Gram–Schmidt loops and the `tools/` `+=` list
concatenations are not folds and were left alone.

## What changed

- **`_random_vector`** — byte-identical in `tests/test_measure.py`, `tests/test_frame.py` and
  `tests/test_dot_wedge_projection_split.py` — became
  `sum((random.uniform(-5.0, 5.0) * basis_vector for basis_vector in basis), start=Gn.zero())`.
  `start=Gn.zero()` is required (non-numeric accumuland) and keeps `-> Gn`; the `basis_vector: Gn`
  loop-target annotation was dropped (a genexpr's loop variable can't be annotated); the
  `# noqa: S311` moved onto the genexpr line.
- **`tests/test_conformance.py` `vector_sum`** — previously seeded with the first grade-1 element —
  became `sum((coeffs[b] * getattr(mod, field_name(b)) for b in grade1), start=graded_type(1).zero())`,
  and the unused `first` local was removed. The start had to be the graded `Vector`'s zero (not
  `Gn.zero()` or `0`) because the next line asserts `type(vector_sum) is graded_type(1)`.
- **One extra fix:** that `start` tripped ty because the nested `graded_type` helper was annotated
  bare `-> type` (no `.zero()`); it was tightened to `-> type[MultiVectorBase]`.
- **Left as a loop:** `recon` in `test_conformance.py`, whose body also asserts each coefficient
  (verify-and-accumulate is not a pure fold; splitting it was not worth it).
- **Dedup follow-up (also done 2026-08-26):** `_random_vector` was extracted to `tests/_helpers.py` as
  `random_vector(dim)` and imported by the three files (`from _helpers import random_vector`); ty
  resolved the sibling import with no `pyproject.toml` change.

## Verification

405 tests green; ruff + ty clean on src and tests (after both the fold change and the dedup).
