# A shared `require_frame` guard, used everywhere a frame is required

**Status:** in progress (2026-11-09)
**Priority:** 5
**Difficulty:** 2
**Created:** 2026-11-09
**Source:** conversation, 2026-11-09 (William Emerison Six <billsix@gmail.com>: "you know how there
is a standard is_vector or are_vectors check, that throws an exception? can you make a similar one
for frames, and then always use it instead of custom checks?")

## BLUF

"Must be a vector" has one shared guard, `MultiVectorBase.require_vector`/`require_vectors`, which
raises `ValueError` naming the caller. "Must be a frame" has none: four functions in
`src/gacalc/frame.py` each hand-write `if not is_frame(vectors): raise ValueError(...)` with their
own copy of the message. Done means a `require_frame(vectors, context)` guard exists next to
`is_frame`, with a doctest. Every frame-requiring function calls it, no hand-rolled
`if not is_frame(...): raise` is left in `src/`, and `CLAUDE.md` names the guard beside
`require_vector`.

## Context

Read first:
- `src/gacalc/base.py` › `MultiVectorBase.require_vector` and `require_vectors`, the model. They are
  static methods taking `(value(s), context)`. The message reads `"<context> takes a vector (grade
  1); got a non-vector: …"`. They raise rather than assert, so they still guard under `python -O`,
  and each has an Examples doctest showing both the pass and the raise.
- `src/gacalc/frame.py` › `are_linearly_independent` and `is_frame`. `is_frame` is a pass-through to
  `are_linearly_independent`, which already calls
  `MultiVectorBase.require_vectors(vectors, "a frame")`. So a non-vector or an empty sequence already
  raises (with "a frame" as the context), and only *dependence* returns `False`.
- `CLAUDE.md` › "Coding standard (Python)" › "Check 'must be a vector' with the shared guard", the
  rule this extends.

**The four hand-written checks** (`git grep -n "if not is_frame" -- src`):

| Function (`src/gacalc/frame.py`) | Message today |
|---|---|
| `make_orthogonal_frame` | `make_orthogonal_frame requires a frame (linearly independent vectors: a_1 ∧ … ∧ a_k ≠ 0); the given vectors are dependent` |
| `make_orthogonal_frame_hestenes` | the same, naming `make_orthogonal_frame_hestenes` |
| `make_orthogonal_frame_hestenes_inverse` | the same, naming `make_orthogonal_frame_hestenes_inverse` |
| `reciprocal_frame` | the same, naming `reciprocal_frame`, with `a_n` in place of `a_k` |

**Callers covered without an edit:** `Frame.__post_init__` and `measure.content_by_rejection` both go
through `make_orthogonal_frame`, so they pick up the guard from it. Their docstrings' `Raises:`
lines stay true.

Nothing outside `src/` hand-checks a frame (`git grep` over `notebooks/`, `book/docs/notebooks/`
and `tools/` finds no `is_frame`). No test matches the message text (`git grep "requires a frame"
-- tests` is empty), so rewording it breaks no `pytest.raises(match=...)`.

**Where the guard lives:** in `frame.py`, as a module function beside `is_frame`, not as a static
method on `MultiVectorBase`. `frame.py` imports `base.py`, so `base.py` can't call `is_frame`
without an import cycle. And frames are free functions over `MultiVectorBase` by design
(`tasks/reference/design-decisions.md` › "Frames … are representation-agnostic free functions").
Its signature mirrors `require_vectors` plus `is_frame`'s tolerance flag:
`require_frame(vectors: Sequence[MultiVectorBase], context: str, float_close_to_zero: bool = False)
-> None`.

**The message:** keep today's wording with the caller as `<context>`, and use `a_k` throughout:
`"<context> requires a frame (linearly independent vectors: a_1 ∧ … ∧ a_k ≠ 0); the given vectors
are dependent"`. `reciprocal_frame`'s message then says `a_k` instead of `a_n`.

**Changelog:** the exception type and trigger are unchanged, and one message changes from `a_n` to
`a_k`. A new public helper (`require_frame`) is an **Added** entry in `CHANGELOG.md` `[Unreleased]`.

## Plan

- [ ] Add `require_frame` to `src/gacalc/frame.py`, right after `is_frame`. Give it a Google-style
  docstring (Args, Raises) and an Examples doctest showing a pass, a dependent set raising (with
  `+ELLIPSIS`), and that a non-vector raises through `require_vectors`. `book/docs/api.rst` documents
  `gacalc.frame` with `automodule :members:`, so a public `require_frame` appears there with no edit.
- [ ] Replace the four `if not is_frame(vectors): raise ValueError(...)` blocks with
  `require_frame(vectors, "<function name>")`. Leave each function's `Raises:` docstring as it is.
- [ ] Add a test in `tests/test_frame.py`. It is parametrized over the four functions and checks
  that each raises `ValueError` matching `"<name> requires a frame"` on a dependent set
  (`[1 * e_1, 2 * e_1]`). That pins the shared message.
- [ ] `CLAUDE.md` › "Check 'must be a vector' with the shared guard": add `require_frame(vectors,
  context)` (`frame.py`) as the guard for "must be a frame". Never hand-roll an `if not is_frame`
  raise.
- [ ] `CHANGELOG.md` `[Unreleased]` › Added: `require_frame`.
- [ ] Gates: `make test`, `make format` (ruff + ty).

## Decisions

1. `require_frame` is public, like `is_frame` and `require_vector`/`require_vectors` (William
   Emerison Six <billsix@gmail.com>, 2026-11-09: "yes public").
2. Done in the committed batch on branch `gn-frozendict-and-frame-tuple`, before
   `tasks/frame-derived-orthogonal-set-and-tuple-field.md`, whose plan names this task as its first
   step. The maintainer authorized the Frame task and was away. Doing its prerequisite first is
   the agent's ordering call, logged here (2026-11-09).
3. `require_frame` first calls `MultiVectorBase.require_vectors(vectors, context)`, so an empty
   sequence or a non-vector member raises with the caller named (`"<context> needs at least one
   vector"`), the same as every other vector-taking function. Before this change, an empty
   sequence reached the "the given vectors are dependent" message. The exception type is unchanged
   (agent's call, 2026-11-09).

## Open questions

None.
