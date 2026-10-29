# Inline the single-use `rest_orthogonal_to_v` in `make_orthogonal_frame`

**Status:** proposed — needs go-ahead
**Priority:** 5  (readability)
**Difficulty:** 2  (one local variable, one function)
**Created:** 2026-10-29 (William Emerison Six <billsix@gmail.com>)

## BLUF

In `make_orthogonal_frame`'s inner `orthogonalize` recursion (`src/gacalc/frame.py`), the `[v, *rest]`
case binds a local `rest_orthogonal_to_v` and then uses it **once**, immediately, as the argument to
the recursive call. A single-use variable defined and consumed on the very next line should be
inlined and used as a value. Inline it. Behavior unchanged; `test_frame.py` (17 tests) stays green.

## Context (cold-start)

- File: `src/gacalc/frame.py`, `make_orthogonal_frame` → inner `orthogonalize`, `case [v, *rest]:`
  ```python
  rest_orthogonal_to_v: list[MultiVectorBase] = [w.rejected_away_from(v) for w in rest]
  return [v, *orthogonalize(rest_orthogonal_to_v)]
  ```
- This function's recursion *shape* and comments were already reworked in the 2026-10-27 task
  `tasks/archive/2026/10/27/orthogonal-frame-recursion-structure-and-comment.md`; that task did **not**
  inline this variable. This is the follow-on refinement.

## Proposed change

```python
return [v, *orthogonalize([w.rejected_away_from(v) for w in rest])]
```

**Discretion note (an exception to weigh):** the name `rest_orthogonal_to_v` documents what the
comprehension produces. If, on reading it inline, the maintainer finds the recursive call less clear
without the name, keeping it is the sanctioned exception. Default is to inline.

## Verification

- `make test` — `test_frame.py` 17 passed (and the full suite green).
- `make format` — ruff + ty clean.

## Follow-on (AFTER the code change is accepted)

Update the **Python coding standard** reference doc in **both** `runClaudeInContainer` and
`runCrushInContainer` (canonical `tasks/reference/python-coding-standard.md` + byte-identical mirror):
a **single-use local variable, defined and then used immediately**, should by default be **inlined and
used as a value**. Exceptions are allowed when the name genuinely serves a purpose (documents a
non-obvious intermediate, or is reused) — use discretion, but default to inlining. (This complements
the existing "inline-once" / expression-vs-mutate guidance; confirm the exact section at that point.)
