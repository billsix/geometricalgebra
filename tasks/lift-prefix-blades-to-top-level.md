# Lift `prefix_blades` to a top-level reusable function (accumulate form)

**Status:** proposed — needs go-ahead (ready to execute; a focused refactor, no new math).
**Priority:** 6 **Difficulty:** 3
**Created:** 2026-10-23 (William Emerison Six <billsix@gmail.com>). Requested: lift the prefix-wedge
helper to module scope so other code (e.g. a reciprocal frame) can reuse it, and write it with
`itertools.accumulate`.

## BLUF

`src/gacalc/frame.py` already computes the **prefix outer products** `A_0 := 1`,
`A_k := A_{k-1} ∧ v_k` (Hestenes & Sobczyk p. 27, eq 3.1) — but only as a **nested closure**
`prefix_blades()` buried inside `make_orthogonal_frame_hestenes` (`frame.py:180`). Lift it to a
**top-level, public, representation-agnostic free function** in `frame.py`, rewrite its body in the
`itertools.accumulate` form the maintainer supplied, and rewire `make_orthogonal_frame_hestenes` to
call it. "Done" = the function is module-level and exported, the Hestenes orthogonalization uses it
and produces byte/symbolically identical output, a direct unit test covers it, and `make test` +
`make format` (ruff + ty) are green. This is a pure extraction — **no behavior change, no new math**.

## Context (read first)

- **Current code:** `src/gacalc/frame.py:180-189`, the nested generator inside
  `make_orthogonal_frame_hestenes` (`frame.py:143`):

  ```python
  def prefix_blades() -> Iterator[MultiVectorBase]:
      # A_0 := 1, then A_k := A_{k-1} ∧ v_k (eq 3.1) ...
      A: MultiVectorBase = type(vectors[0]).one()
      yield A  # A_0 = 1
      v: MultiVectorBase
      for v in vectors:
          A = A ^ v  # A_k = A_{k-1} ∧ v_k
          yield A
  ```

  It yields `A_0 = 1` (the scalar one, in the operands' own representation), then `A_1 = v_1`,
  `A_2 = v_1 ∧ v_2`, … The one consumer (`hestenes_vectors`, `frame.py:191`) reads `A_{k-1}` and
  `A_k` pairwise for eq 3.2 `c_k := reverse(A_{k-1}) · A_k`.
- **The maintainer's requested form** (adapt the pasted pseudocode to gacalc — `one` is a **method**,
  `^` is `operator.xor` = the outer/wedge product):

  ```python
  return accumulate(chain([type(vectors[0]).one()], vectors), operator.xor)
  ```

  Equivalent and cleaner: `accumulate(vectors, operator.xor, initial=type(vectors[0]).one())`
  (the `initial=` keyword, Python ≥ 3.8 — avoids the `chain`). Either yields `A_0, A_1, …, A_k`,
  matching the current semantics exactly.
- **Style the module already follows** (`frame.py` docstring, lines 14-27): representation-agnostic
  **free functions** over `MultiVectorBase` (work on `Gn` and the graded `Vector_n` alike); no
  `Frame` class. Capital `A` for a general multivector/blade is correct per the Hestenes variable
  convention (gacalc CLAUDE.md). Keep the eq-3.1 teaching comment and the O(k)-not-O(k²) note.
- **Imports to add** to `frame.py`: `operator`, and `accumulate`/`chain` from `itertools`
  (currently it imports only `functools`, `collections.abc`, `numpy`, `MultiVectorBase`).
- **Not generated code** — `frame.py` is hand-written, so this shows up as an ordinary `src/` diff
  (unlike the generator). No `make check-generated` / `make check-regions` impact.

## Plan

1. Add a module-level `def prefix_blades(vectors: Sequence[MultiVectorBase]) -> Iterator[MultiVectorBase]:`
   to `frame.py`, docstringed (H&S p. 27 eq 3.1; "yields `A_0 = 1` then each prefix wedge"), body =
   the `accumulate(..., initial=...)` form. Keep it lazy (returns an iterator).
2. Replace the nested `prefix_blades()` in `make_orthogonal_frame_hestenes` with a call to the new
   top-level function; `hestenes_vectors` is otherwise unchanged.
3. Export it (it's public — no leading underscore; add to the module's public surface the same way
   the other frame functions are exposed — confirm whether `frame.py`/`transforms.py` use an
   `__all__` and match that).
4. Add a direct unit test in `tests/test_frame.py`: for a 2D and 3D frame, `list(prefix_blades(vs))`
   equals `[one, v1, v1∧v2, …]` (symbolic equality), and that `make_orthogonal_frame_hestenes` output
   is unchanged (the existing equivalence tests already guard this — confirm they still pass).

## Decisions / open questions

1. **`initial=` vs `chain`** — recommend `accumulate(vectors, operator.xor, initial=type(vectors[0]).one())`
   (no `chain`, reads as "seed with 1, fold with ∧"). OK?
2. **Empty-`vectors` behavior.** The current nested version is only reached after an `is_frame` guard,
   so it never sees an empty sequence; a *public* function must define it. The pasted pseudocode
   returned `iter([one])` — but with no vectors there is no `type(vectors[0])` to pick a representation
   from. Recommend: **raise `ValueError` on empty input** (consistent with the frame functions, which
   require a nonempty linearly independent set), rather than inventing a representation. OK, or do you
   want it to yield a bare scalar `1` for `[]`?
3. **Name/location.** Keep the name `prefix_blades` and put it in `frame.py`? It is a frame/blade
   primitive and `frame.py` is its only current consumer, so that is the natural home; the alternative
   is a more general home (`base.py` as a `MultiVectorBase` staticmethod, or `measure.py`) if you
   expect non-frame consumers. Recommend `frame.py` top-level.
4. **Reciprocal frame (the motivating future consumer).** There is **no reciprocal-frame function in
   the repo today** (grep: only "reciprocal" in `inverse` docstrings). The reciprocal frame `{e^k}`
   (H&S p. 27-28) is built from complementary wedge products and the pseudoscalar, for which these
   prefix blades (and their suffix mirror) are a natural building block. That would be **new math**, so
   by the "every result in three forms" rule (Lean + symbolic Python + prose) it should be its **own
   task** when you want it — not folded in here. **Shall I file a `proposed` `reciprocal-frame` task
   cross-linked to this one?** (Default: no, until you confirm the design.)

## Verify

- `make test` — `tests/test_frame.py` (incl. the new direct test) + the Hestenes/rejection
  equivalence tests, which prove behavior is unchanged.
- `make format` — ruff + `ty check` clean (the new function fully annotated).
- Lean (`make lean`) is unaffected (no proof depends on this helper).

## Pointers

- `src/gacalc/frame.py` — the module; `make_orthogonal_frame_hestenes` (eqs 3.1-3.2) is the consumer.
- `tasks/define-frame.md` — the broader frame-API task (priority was lowered while frames are parked).
- `tasks/reference/content-area-volume.md` — `measure.py`'s free-function-over-`MultiVectorBase` style,
  the sibling pattern.
