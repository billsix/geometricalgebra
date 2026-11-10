# A shared `require_frame` guard, used everywhere a frame is required

**Done:** 2026-11-09
**Priority:** 5
**Difficulty:** 2
**Source:** conversation, 2026-11-09 (William Emerison Six <billsix@gmail.com>: "you know how there
is a standard is_vector or are_vectors check, that throws an exception? can you make a similar one
for frames, and then always use it instead of custom checks?")

## Summary

"Must be a frame" now has one shared guard, like "must be a vector"
(`MultiVectorBase.require_vector`/`require_vectors`). The new guard is
`require_frame(vectors, context, float_close_to_zero=False)` in `src/gacalc/frame.py`, right after
`is_frame`. It calls `MultiVectorBase.require_vectors(vectors, context)` and then raises
`ValueError("<context> requires a frame (linearly independent vectors: a_1 ∧ … ∧ a_k ≠ 0); the
given vectors are dependent")` when `is_frame` is false. Its doctest shows a pass, a dependent set
raising, and a non-vector raising.

## What changed

- **The four hand-written checks were replaced** with `require_frame(vectors, "<function name>")`:
  `make_orthogonal_frame`, `make_orthogonal_frame_hestenes`,
  `make_orthogonal_frame_hestenes_inverse` and `reciprocal_frame`. Their `Raises:` docstrings
  were left as they were, since each still raises `ValueError`. `reciprocal_frame`'s message now
  says `a_k`, not `a_n`.
- **Callers covered with no edit:** `Frame.__post_init__` and `measure.content_by_rejection` both
  go through `make_orthogonal_frame`. No `if not is_frame(...): raise` is left in `src/`.
- **`tests/test_frame.py`:**
  - `test_frame_functions_share_the_require_frame_message` is parametrized over the four
    functions and pins `"^<name> requires a frame"` on `[1 * e_1, 2 * e_1]`;
  - `test_require_frame_names_the_caller_for_an_empty_set` covers the empty case.
- **`CLAUDE.md`** › "Check 'must be a vector' with the shared guard" names `require_frame` as the
  guard for "must be a frame".
- **`CHANGELOG.md`** `[Unreleased]` › Added has the `require_frame` entry. `book/docs/api.rst`
  documents `gacalc.frame` with `automodule :members:`, so the new function appears in the book
  with no edit there.
- **Gates:** `make test` (781 passed, 2 skipped) and `make format`, both passing. The first
  `make format` failed in `ty`: the test read `__name__` off a `Callable`. It now takes
  explicit `(name, function)` pairs.

## Decisions

1. `require_frame` is public, like `is_frame` and `require_vector`/`require_vectors` (William
   Emerison Six <billsix@gmail.com>, 2026-11-09: "yes public").
2. It was done in the committed batch on branch `gn-frozendict-and-frame-tuple`, before
   `tasks/archive/2026/11/09/frame-derived-orthogonal-set-and-tuple-field.md`, whose plan named this task as its
   first step. The maintainer had authorized the Frame task and was away, so the order was the
   agent's call (2026-11-09).
3. `require_frame` calls `require_vectors` first, so an empty sequence or a non-vector member
   raises with the caller named (`"<context> needs at least one vector"`), the same as every other
   vector-taking function. Before this, an empty sequence got the "the given vectors are
   dependent" message. The exception type did not change (agent's call, 2026-11-09).
4. It lives in `frame.py`, not as a static method on `MultiVectorBase`. `base.py` can't import
   `is_frame` without an import cycle, and frames are representation-agnostic free functions by
   design (`tasks/reference/design-decisions.md`).
