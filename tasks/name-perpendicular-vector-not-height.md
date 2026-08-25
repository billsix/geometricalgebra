# Rename the `height` loop variable to name the *vector*, not its magnitude

**Status:** proposed — needs go-ahead. Created 2026-08-25 (William Emerison Six <billsix@gmail.com>)
**Priority:** 4
**Difficulty:** 1

## Goal

In `content_by_rejection` (`src/gacalc/measure.py:116`) the loop variable is named `height`,
but it is bound to a **vector**, not a scalar height:

```python
_require_vectors(vectors)
result: Coef = 1
for height in make_orthogonal_frame(vectors):
    result = result * height.magnitude()
return result
```

`make_orthogonal_frame(vectors)` returns `list[MultiVectorBase]` (`frame.py:82-84`) — the
orthogonalized (rejected) frame vectors `w_j`. The *scalar height* is `height.magnitude()`
(`|w_j|`), so the local holds the perpendicular **vector** and `height` mislabels it as the
number it isn't. Rename the local to name the vector; its `.magnitude()` is the height.

## Change

Rename the loop variable and — per the house rule "loop/unpack targets can't be annotated
inline, declare the type on the line above" — add its type:

```python
_require_vectors(vectors)
result: Coef = 1
perpendicular_vector: MultiVectorBase
for perpendicular_vector in make_orthogonal_frame(vectors):
    result = result * perpendicular_vector.magnitude()
return result
```

**Name choice — `perpendicular_vector` (DECIDED 2026-08-25, Bill).** (`MultiVectorBase` is
already imported in `measure.py`.)

## Scope / what NOT to touch

- **Single site.** `grep` confirms `measure.py:116` is the only `height` local in `src/` — no
  sibling occurrences to sweep.
- **Leave the docstring math as-is.** In the prose, "product of rejected heights" and `∏|h_j|`
  are correct: the *heights* are the magnitudes `|h_j|`, and `h_j` is standard notation for the
  rejected vector (W&T p. 146). This task renames the **code local** only. The one prose phrase
  that arguably conflates — "Each height ``h_j`` is ``v_j`` rejected from the span" (`measure.py:93`)
  — is optional to reword ("Each rejected vector ``h_j`` is …"); decide when doing the rename, but
  it is not the point of the task.

## Verify

- `make format` clean (ruff + `ty check src`) — a rename + one annotation, no behaviour change.
- `make test` green (the `content_by_rejection` == `content` equality tests in
  `tests/test_measure.py` still pass — value is unchanged).

## Cross-links

- `src/gacalc/measure.py:89` — `content_by_rejection` (the function).
- `src/gacalc/frame.py:82` — `make_orthogonal_frame` → `list[MultiVectorBase]`.
- Coding standard (`CLAUDE.md` › Coding standard › Naming grammar): "nouns for values … a local
  bound to X is named for what it is"; typed loop targets get a declared type on the line above.
