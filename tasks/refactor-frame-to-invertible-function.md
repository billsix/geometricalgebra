# Refactor `Frame.to_invertible_function`: inline single-use locals, narrow scopes, name the implied dimension

**Status:** proposed — open questions below block implementation.
**Priority:** 3
**Difficulty:** 3
**Created:** 2026-11-06 (William Emerison Six <billsix@gmail.com>)

## BLUF

`Frame.to_invertible_function` (`src/gacalc/frame.py`) works, but it does not read the way the
maintainer wants. It binds names that are used only once, spells "the smallest dimension a vector needs"
as an opaque nested `max`, and declares `pairs` and `peel` far wider than where they are used. This task
reshapes it with no change in behaviour. Then, as the last step, it writes the rules learned here into
the shared cross-project standards in github.com/billsix/runClaudeInContainer and
github.com/billsix/runCrushInContainer. Done = the method is refactored, a named public
implied-dimension method replaces all three copies of the dimension-inference logic, `make test` and
`make format` pass, a `CHANGELOG.md` `[Unreleased]` entry exists, and the shared docs are updated in
both sandbox repos. The maintainer has said more issues with this method will follow; add them under
"Later issues" when they arrive.

## Context

- **The code:** `Frame.to_invertible_function` in `src/gacalc/frame.py` (`def to_invertible_function`).
  It has a long docstring (the peel derivation and a doctest), then the body: compute `k` and `n`, raise if
  `k != n`, build `pairs`, then the nested helpers `require_vector`, `forward`, `peel`, `backward`.
  Math background: `tasks/reference/frames-qr-and-reciprocal-frames.md` ("The peel inverse, step by
  step").
- **The governing shared rule today:** "Inline a value used exactly once — unless the name documents an
  otherwise-opaque expression" in the `python-coding-standard.md` reference doc
  (github.com/billsix/runClaudeInContainer `tasks/reference/`, byte-identical mirror in
  runCrushInContainer). Its "documents an opaque expression" exception is exactly what the maintainer
  rejects here (see Decisions). Read it, plus "What earns an extraction", before editing.
- **The dimension-inference logic exists in three places:**
  1. `frame.py`, this method: `getattr(cls, "DIMENSION", None)`, else
     `max(max(blade) for v in … for blade in v.to_blade_dict() if blade)`. That `max` has no `default=`,
     so it would raise on all-zero input. A frame cannot hold a zero vector, so this never fires.
  2. `measure.py`: the private helper `_max_basis_index(vectors)` (`default=0`), used by
     `signed_content` with the same `DIMENSION`-else pattern.
  3. `vectorcalc.py` `cross`: imports `measure._max_basis_index` across modules (a private name) and
     calls it twice.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-06)

1. **A local that is bound once and used once is inlined, even when the name was there for
   readability.** The reader of a declaration scans ahead to see how far it is used. A one-use binding
   wastes that scan, and the waste grows with the length of the method. Instead, put a **comment above
   the inlined subexpression** that quotes or describes it and **gives it its name in the comment**. A
   local used two or more times stays a local.
2. **A declaration goes where it is used, not earlier.** `pairs` is built many lines before its only
   use, inside `backward`.
3. **A helper used by only one function is nested inside that function.** `peel` is used only by
   `backward`, so it moves inside `backward` unless there is a real reason not to. Analysis for the
   maintainer: the only cost is that a nested `def` creates a new function object on each `backward`
   call, which is microseconds next to the sympy and multivector work in each peel step. Recursion
   through the closure cell works the same. There is no performance or correctness reason to keep it at
   the outer level.
4. **The `n` ternary is replaced by a named method.** The `max(max(blade) …)` idea ("the highest
   basis index this vector uses, i.e. the smallest coordinate space that holds it") is extracted into
   `base.py`, `gn.py`, or the generated classes. The working name is `implied_minimal_number_of_dimensions`.
   The method checks that its input is a vector.

## Plan

1. Settle the open questions.
2. Add the implied-dimension method (home and name per Q1–Q2), with a doctest and a non-vector
   `ValueError`. Route `measure.signed_content` and `vectorcalc.cross` through it and delete
   `measure._max_basis_index` (per Q3). Add a `CHANGELOG.md` `[Unreleased]` "Added" entry for the new
   public method.
3. Refactor `to_invertible_function`:
   - Use `self.vectors` directly in place of the `frame_vectors` alias (CLAUDE.md: "No local aliases").
   - Inline `cls` and `dimension`. They disappear once the method from step 2 computes `n`.
   - Keep `k` and `n`, which are each used twice (the `if` and the error message).
   - Move `peel` inside `backward`. Inline `pairs` into the `peel(...)` call there, with a comment naming
     it ("pairs: each orthogonal vector `w_i` with the frame vector `v_i` it came from, in frame order").
   - Inline `x_last` into the recursive call only if it is used once. It is used **twice** (in
     `y - x_last * v` and in the returned list), so it stays.
   - Keep `require_vector` at its current level: both `forward` and `backward` use it.
4. Gates: `make test`, `make format` (ruff + ty), `python tools/check_annotations.py` (no new rows).
5. **Last item: extract the knowledge.** Update the shared docs (location per Q4) in
   github.com/billsix/runClaudeInContainer and mirror the change byte-identically into
   github.com/billsix/runCrushInContainer:
   - Rewrite the inline-once rule: drop the "documents an opaque expression" exception, and replace it
     with "inline it, with a comment above that names the subexpression". Name the cost it avoids (the
     reader's scan for the extent of a declaration).
   - Add "declare at the point of use" and "nest a helper inside its only caller".
   - Replace the gacalc worked examples with this refactor (before/after) in
     `tasks/reference/python-coding-standard-gacalc.md`.
   - Stage both repos by path.

## Open questions

1. **Home and shape of the implied-dimension method.** Recommendation: an **instance method on
   `MultiVectorBase`** (`base.py`), `v.implied_minimal_number_of_dimensions() -> int`. It raises
   `ValueError` on a non-vector, returns the highest basis index in `v`, and returns 0 for the zero
   vector. Callers with several vectors take `max(...)` over them. As a base method it works for `Gn` and
   every generated class with nothing to generate. Alternative: a free function over a sequence, as
   `_max_basis_index` is today.
2. **The name.** You said "some name like" `implied_minimal_number_of_dimensions`. Recommendation: keep
   it as you wrote it. Alternative: something shorter, e.g. `minimal_dimension`.
3. **Should the `DIMENSION`-else-max decision move into a helper too?** The pattern "a fixed type's
   `DIMENSION`, else the implied dimension" appears in `frame.py`, `measure.py`, and (in another form) in
   `vectorcalc.py`. Recommendation: no. Extract only the per-vector method you asked for, and let each
   caller keep its short `DIMENSION` check, because `vectorcalc` uses the two halves differently.
4. **Where in the shared layer the rules go.** Recommendation: the full rule with examples goes in
   `python-coding-standard.md` and the language-agnostic `code-style-conventions.md`, plus **one terse
   line** in the shared `CLAUDE.md` (runClaudeInContainer `entrypoint/dotfiles/.claude/CLAUDE.md` and
   the runCrush twin), under "What earns pulling code into its own function". It is a portable rule,
   not a personal one, so not the personal overlay.

## Later issues

(The maintainer has more issues with this method; record them here as they arrive.)
