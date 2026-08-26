# Use `sum` for the hand-rolled fold loops in tests

**Status:** DONE 2026-08-26 (William Emerison Six <billsix@gmail.com>) — see Outcome.
**Priority:** 5
**Difficulty:** 2

## Outcome (2026-08-26)

Done, 405 tests green, ruff + ty clean (src and tests). Both folds converted:
- `_random_vector` in `test_measure.py` / `test_frame.py` / `test_dot_wedge_projection_split.py` →
  `sum((random.uniform(-5.0, 5.0) * basis_vector for basis_vector in basis), start=Gn.zero())`; the
  `basis_vector: Gn` annotation dropped, the `# noqa: S311` moved onto the genexpr line.
- `test_conformance.py` `vector_sum` → `sum((coeffs[b] * getattr(mod, field_name(b)) for b in
  grade1), start=graded_type(1).zero())`; the now-unused `first` local removed.
- **One extra fix needed:** the `start=graded_type(1).zero()` tripped ty — the nested
  `graded_type` helper was annotated `-> type` (bare), which has no `.zero()`. Tightened it to
  `-> type[MultiVectorBase]` (honest: it returns graded classes, all `MultiVectorBase` subclasses),
  which is also a small typing improvement to the helper.
- `recon` (test_conformance.py) left as-is per plan (assert side effect in the loop body).
- Optional `_random_vector` dedup into a shared helper: **also DONE 2026-08-26** (follow-up) —
  extracted to `tests/_helpers.py` as `random_vector(dim)`, imported by the three test files (`from
  _helpers import random_vector`); ty resolves the sibling import with no `pyproject.toml` change,
  ruff + ty clean, 405 tests green.

## Goal

Apply the new CLAUDE.md convention ("Reduce with `sum` / `math.prod`, not a hand-rolled accumulator
loop") to the **test** code, which is where the sweep on 2026-08-26 found the only remaining
candidates. The library (`src/gacalc/`) already uses `sum`/`math.prod`/`reduce` throughout — no
changes there — and the `frame.py` Gram–Schmidt loops and the `tools/` `+=` list-concatenations are
correctly *not* folds (leave them).

## Do these (genuine pure folds)

### 1. `_random_vector` — the same helper, copy-pasted in three test files

`tests/test_measure.py:53`, `tests/test_frame.py:50`, `tests/test_dot_wedge_projection_split.py:102`
are byte-identical:

```python
def _random_vector(dim: int) -> Gn:
    ...
    basis: list[Gn] = [e_1, e_2, e_3][:dim]
    v: Gn = Gn.zero()
    basis_vector: Gn
    for basis_vector in basis:
        v = v + random.uniform(-5.0, 5.0) * basis_vector  # noqa: S311
    return v
```

→ pure sum fold:

```python
    basis: list[Gn] = [e_1, e_2, e_3][:dim]
    return sum(
        (random.uniform(-5.0, 5.0) * basis_vector for basis_vector in basis),  # noqa: S311
        start=Gn.zero(),
    )
```

- **`start=Gn.zero()`** is required (non-numeric accumuland) and preserves the `-> Gn` type.
- The `basis_vector: Gn` loop-target annotation is **dropped** — a genexpr's loop var is a separate
  scope and can't be annotated (per the CLAUDE.md loop-target rule).
- The `# noqa: S311` moves onto the `random.uniform(...)` line inside the genexpr (verify ruff is
  still clean — the suppression must land on the right physical line).

### 2. `tests/test_conformance.py:326-334` — `vector_sum`

Currently seeds with the first grade-1 element, then folds the rest:

```python
vector_sum: MultiVectorBase = coeffs[first] * getattr(mod, field_name(first))
for b in grade1[1:]:
    vector_sum = vector_sum + coeffs[b] * getattr(mod, field_name(b))
assert type(vector_sum) is graded_type(1)
```

→

```python
vector_sum: MultiVectorBase = sum(
    (coeffs[b] * getattr(mod, field_name(b)) for b in grade1),
    start=graded_type(1).zero(),
)
assert type(vector_sum) is graded_type(1)
```

- **Caveat — the `start` type matters:** line 333 asserts `type(vector_sum) is graded_type(1)`, so
  the identity must be the **graded Vector's** zero. `graded_type(1)` is already in scope (used on
  the next line), so `graded_type(1).zero()` is the right start — **not** `Gn.zero()` or `0`, which
  would change the result type and break the assertion. The current first-element seeding exists
  precisely to avoid naming that zero; the `sum` form names it instead.
- `grade1[1:]` becomes the full `grade1` (the seed folds in as the first term). `first` may become
  unused — drop it if so (ruff will flag `F841`).

## Leave this one (not a pure fold)

- **`tests/test_conformance.py:264-272` (`recon`)** — the loop body also runs an `assert` on each
  coefficient, so it verifies *and* accumulates. Per the convention's "keep the explicit loop if the
  body also has side effects," leave it. (Splitting into an assert-loop + a separate `sum` is a
  refactor, not a fold swap, and isn't worth it here.)

## Optional follow-up (out of scope unless you want it)

`_random_vector` being copy-pasted three times is its own smell — a shared test helper (e.g. in a
`tests/conftest.py` or a small `tests/_helpers.py`) would dedup all three. Separate from the
sum/prod change; note it, decide separately.

## Verify

- `make test` (or `PYTHONPATH=src python -m pytest -q`) green — these are behaviour-preserving; the
  `_random_vector` change keeps `-> Gn`, and the `vector_sum` change keeps `graded_type(1)`.
- `make format` clean — ruff (`S311` noqa still on the right line, no `F841` leftover) + `ty check
  tests`.

## Cross-links

- CLAUDE.md › Coding standard › "Reduce with `sum` / `math.prod`, not a hand-rolled accumulator
  loop" (the convention this applies) — added 2026-08-26.
- Sibling change that motivated the convention: `measure.content_by_rejection` (`math.prod`,
  archived `tasks/archive/2026/08/25/pseudoscalar-coefficient-via-unit-pseudoscalar.md` is adjacent).
