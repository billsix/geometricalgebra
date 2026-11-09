# Rewrite `make_orthogonal_frame` / `make_orthogonal_frame_hestenes` recursively, and make the Hestenes one generator-driven

**Created:** 2026-10-22 (William Emerison Six <billsix@gmail.com>) · **Completed:** 2026-10-22
**Part of:** the frames work — `tasks/define-frame.md` (the functions were added in its Phase 1)

Both orthogonalizations in `src/gacalc/frame.py` were rewritten as a **behavior-preserving teaching
refactor**. `make_orthogonal_frame` became a nested recursive helper with an **accumulator**,
dispatching with `match` on **one vector vs. multiple**; `make_orthogonal_frame_hestenes` became two
**self-referential generators** — one carrying the running prefix wedge `A_k = A_{k-1} ∧ v_k`, one
pairing consecutive blades into `c_k = reverse(A_{k-1}) * A_k`. Public signatures and the
`list[MultiVectorBase]` return were unchanged. The refactor touched only Python style; it did not
depend on the then-parked `Frame`-class representation decision or the Lean frame coverage
(`tasks/lean-frame-coverage.md`).

## Constraints the rewrite kept

- The two functions are a deliberate teaching pair computing the *same* orthogonal directions two ways
  (equal up to a positive scalar per vector, `c_k == |A_{k-1}|² * w_k`); both are public and both stay
  (`tasks/define-frame.md`, 2026-08-23). Only *how each is written* changed.
- `match` + total dispatch with a mandatory-feeling `case _` (`CLAUDE.md` › "Prefer `match` / total
  dispatch"), and **Rule E** of `tasks/reference/conditional-refactoring-rules.md`: a named nested
  function reads the enclosing scope but takes its accumulator as a parameter and returns.
- Hestenes variable naming (`tasks/reference/hestenes-variable-notation.md`): `A`/`A_k` for blades,
  `v`/`w` for vectors, `c_k` for the Hestenes output; every binding annotated.
- The `is_frame` guard stays at the top of each function (`ValueError` on a dependent set); only the
  orthogonalization body changed.

## What was done

- **`make_orthogonal_frame`** (rejection / Gram–Schmidt): a nested `reject_span(v, prior)` rejects `v`
  off each already-orthogonal vector with a `functools.reduce` over `rejected_away_from` (pairwise
  rejection equals rejecting the whole span because the prior vectors are mutually orthogonal), and a
  nested recursive `orthogonalize(remaining, done)` matches `[v]` (base case) / `[v, *rest]` (recurse
  with the accumulator) / `case _` (empty, unreachable because `is_frame` rules out `[]`).
- **`make_orthogonal_frame_hestenes`**: the `prefix_blades` generator seeds `A_0 = type(v).one()` and
  yields `A_k = A_{k-1} ∧ v_k` (H&S eq 3.1); the `hestenes_vectors` generator carries the previous blade
  (named `A_k_minus_1`, per the maintainer) and yields `(reverse(A_{k-1}) * A_k).r_vector_part(1)` (H&S
  eq 3.2). The docstrings' cross-referencing prose and `See also` were kept; only the "how it's
  computed" sentences changed.
- Two side benefits, described in the new docstring: the generator form **subsumes the old `k == 1`
  special case** (`A_1 = 1 ∧ v_1 = v_1`, so `c_1 = v_1` falls out, a pedagogical contrast with the
  rejection form's explicit `match`), and it builds each blade once — **O(k) wedges instead of O(k²)**,
  since the old code rebuilt both blades per step via `outer_product_of_vectors(*vectors[:k])`. Seeding
  from `one()` also avoids `outer_product_of_vectors`' no-initializer `reduce`, which raises on empty
  input.

## Decision (William Emerison Six <billsix@gmail.com>, 2026-10-22)

The maintainer's request was "a function taking in the subscripts to calculate the wedge, maybe a
self-referential generator, and then the function a self-referential generator as well." The agent's
reading — the **state-carrying loop generator** (inner one carries the running wedge, outer one carries
the previous blade) — was confirmed; a recursive `yield from` form was **not** used.

## Verification

`tests/test_frame.py` was left unedited, so the proof is the existing tests passing: all 16 frame tests
(including `test_hestenes_equals_rejection_*` in 2D/3D, symbolic and numeric, and the single-vector /
first-vector-unchanged / dependent-raises cases) plus the `frame.py` doctests pass; `ruff` /
`ruff format` / `ty` clean. No `CHANGELOG` entry — the public API is unchanged.
