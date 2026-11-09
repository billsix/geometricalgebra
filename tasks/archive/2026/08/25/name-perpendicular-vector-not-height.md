# Rename the `height` loop variable to name the *vector*, not its magnitude

**Created:** 2026-08-25 · **Completed:** 2026-08-25

In `content_by_rejection` (`src/gacalc/measure.py`) the loop variable `height` was bound to a
**vector**: `make_orthogonal_frame(vectors)` returns `list[MultiVectorBase]` (`frame.py`), the
orthogonalized (rejected) frame vectors `w_j`, and the scalar height is `height.magnitude()` (`|w_j|`).
The name labelled the vector as the number it isn't.

## What changed

The loop variable was renamed `height` → **`perpendicular_vector`** (the maintainer's choice, William
Emerison Six <billsix@gmail.com>, 2026-08-25), with its type declared on the line above, per the rule
that loop targets can't be annotated inline:

```python
_require_vectors(vectors)
result: Coef = 1
perpendicular_vector: MultiVectorBase
for perpendicular_vector in make_orthogonal_frame(vectors):
    result = result * perpendicular_vector.magnitude()
return result
```

## Scope

- **Single site:** `grep` confirmed it was the only `height` local in `src/`.
- **The docstring math was left as-is:** "product of rejected heights" and `∏|h_j|` are correct (the
  heights are the magnitudes `|h_j|`, and `h_j` is standard notation for the rejected vector, W&T
  p. 146). Rewording the one phrase that arguably conflates the two ("Each height ``h_j`` is ``v_j``
  rejected from the span") was optional and not the point of the task.
- The rule applied is the coding standard's naming grammar (a local is named for what it is) plus the
  typed-loop-target rule.

## Verification

A rename plus one annotation, with no behaviour change: 405 tests green (including the
`content_by_rejection == content` equality tests in `tests/test_measure.py`), ty clean.
