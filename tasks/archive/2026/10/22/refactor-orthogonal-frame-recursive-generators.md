# Rewrite `make_orthogonal_frame` / `make_orthogonal_frame_hestenes` recursively, and make the Hestenes one generator-driven

## BLUF

Rewrite both orthogonalizations in `src/gacalc/frame.py` as a **behavior-preserving teaching
refactor**: a nested recursive helper with an **accumulator**, dispatching with `match` on
**one vector vs. multiple**. For `make_orthogonal_frame_hestenes` go further — express the prefix
wedge `A_k = v_1 ∧ … ∧ v_k` as a **self-referential generator** that carries the running wedge
(`A_k = A_{k-1} ∧ v_k`), and make the orthogonal-vector producer a **self-referential generator**
too (`c_k = reverse(A_{k-1}) * A_k`, pairing consecutive blades from that stream). "Done" = the
public return (a `list[MultiVectorBase]`) is unchanged, all ~16 `tests/test_frame.py` tests plus
the docstring doctests still pass, and `make format` (ruff + ty) is clean.

## Status

**Status:** DONE 2026-10-22 — both functions rewritten in `src/gacalc/frame.py` as designed
(`make_orthogonal_frame`: nested recursive `orthogonalize` + `reject_span`, `match` on one-vs-many;
`make_orthogonal_frame_hestenes`: the `prefix_blades` running-wedge generator + the
`hestenes_vectors` generator, with the previous blade named `A_k_minus_1` per the maintainer). The
16 `tests/test_frame.py` tests + frame.py doctests pass; `ruff` / `ruff format` / `ty` clean. Public
signatures and `list[MultiVectorBase]` return unchanged. Work STAGED; archive is its own commit
after the maintainer's work commit.
**Priority:** 6
**Difficulty:** 4
**Created:** 2026-10-22 (William Emerison Six <billsix@gmail.com>)
Part of the frames work — see `tasks/define-frame.md` (the functions were added in its Phase 1).
This touches only Python style; it does not depend on the parked `Frame`-class representation
decision or the parked Lean frame coverage (`tasks/lean-frame-coverage.md`).

## Context (cold-start orientation)

- **The two functions live in `src/gacalc/frame.py`** (`make_orthogonal_frame` at line ~85,
  `make_orthogonal_frame_hestenes` at ~130). Read that file and the H&S p. 27 reference in its
  module docstring first.
- **They are a deliberate teaching pair** computing the *same* orthogonal directions two ways
  (proven equal up to a positive scalar per vector, `c_k == |A_{k-1}|² * w_k`). Both are PUBLIC and
  both STAY — neither replaces the other (`tasks/define-frame.md`, 2026-08-23). This refactor
  changes *how each is written*, not that both exist.
- **Project conventions that bind this refactor:**
  - `match` + total dispatch for structural case analysis, always with a mandatory-feeling default
    (`case _`) — `CLAUDE.md` › "Prefer `match` / total dispatch", and the worked examples in
    `tasks/reference/conditional-refactoring-rules.md` (esp. **Rule E**: a named *nested* function
    that **reads** the enclosing scope but **returns** rather than mutating it).
  - Hestenes variable-naming (`tasks/reference/hestenes-variable-notation.md`): `A`/`A_k` for the
    blades (CAPITAL Latin — general/graded multivector), `v`/`w` for vectors (lowercase Latin),
    `c_k` for the Hestenes output. Keep these.
  - Every local/binding annotated; LGPL-2.1-only header already present — don't disturb it.
- **Primitives available** (verified in `src/gacalc/base.py`): `type(v).one()` (A₀ = 1, a classmethod
  at base.py:320), `type(v).zero()`, `A ^ v` (wedge), `A.reverse()`, `A * B` (geometric product),
  `A.r_vector_part(1)` (grade-1 narrowing, drops identically-zero widened terms),
  `v.rejected_away_from(prior)`. Note `outer_product_of_vectors(*…)` is a `functools.reduce` with
  **no initializer**, so it raises on empty input — the running-wedge generator seeded from `one()`
  avoids that edge entirely.
- **The `is_frame` guard stays at the top of each function** (raises `ValueError` on a dependent
  set); only the orthogonalization body is rewritten.

## Proposed design

### 1. `make_orthogonal_frame` (rejection / Gram–Schmidt): recursion + accumulator + match

Keep the `is_frame` guard, then dispatch with a nested recursive helper carrying the
already-orthogonalized prefix as the accumulator. Dispatch on **one vs. multiple**:

```python
def make_orthogonal_frame(
    vectors: Sequence[MultiVectorBase],
) -> list[MultiVectorBase]:
    if not is_frame(vectors):
        raise ValueError(...)  # unchanged

    def reject_span(v: MultiVectorBase, prior: list[MultiVectorBase]) -> MultiVectorBase:
        # reject v off each already-orthogonal vector (pairwise == rejecting the whole span,
        # because the prior vectors are mutually orthogonal — the existing docstring argument)
        return functools.reduce(lambda w, p: w.rejected_away_from(p), prior, v)

    def orthogonalize(
        remaining: Sequence[MultiVectorBase], done: list[MultiVectorBase]
    ) -> list[MultiVectorBase]:
        match list(remaining):
            case [v]:                       # one vector left — base case
                return [*done, reject_span(v, done)]
            case [v, *rest]:                # multiple — recurse with the accumulator
                return orthogonalize(rest, [*done, reject_span(v, done)])
            case _:                         # empty — unreachable (is_frame rules out [])
                return done

    return orthogonalize(vectors, [])
```

The nested helpers **read** the enclosing scope but take their accumulator as a parameter and
**return** (Rule E). The `case _` names the empty case explicitly even though `is_frame` makes it
unreachable.

### 2. `make_orthogonal_frame_hestenes`: the two self-referential generators

This is the part the maintainer described as "a function taking in the subscripts to calculate the
wedge, maybe a self-referential generator, and then the function a self-referential generator as
well." My reading, concretely (**confirm — see the open question**):

```python
def make_orthogonal_frame_hestenes(
    vectors: Sequence[MultiVectorBase],
) -> list[MultiVectorBase]:
    if not is_frame(vectors):
        raise ValueError(...)  # unchanged

    def prefix_blades() -> Iterator[MultiVectorBase]:
        # A_0 := 1, then A_k := A_{k-1} ∧ v_k  (H&S eq 3.1) — self-referential:
        # each blade is built from the one yielded before it, carried in A.
        A: MultiVectorBase = type(vectors[0]).one()
        yield A                              # A_0 = 1
        v: MultiVectorBase
        for v in vectors:
            A = A ^ v                        # A_k = A_{k-1} ∧ v_k
            yield A

    def hestenes_vectors() -> Iterator[MultiVectorBase]:
        # c_k := reverse(A_{k-1}) * A_k  (H&S eq 3.2) — self-referential: carries the
        # previous blade across iterations and pairs it with the current one.
        blades: Iterator[MultiVectorBase] = prefix_blades()
        A_prev: MultiVectorBase = next(blades)       # A_0
        A_k: MultiVectorBase
        for A_k in blades:                           # A_1, A_2, …
            yield (A_prev.reverse() * A_k).r_vector_part(1)
            A_prev = A_k

    return list(hestenes_vectors())
```

Two wins beyond style, worth noting in the new docstring:

- **The one-vs-multiple split disappears for free.** The current code special-cases `k == 1`
  (`c_1 = v_1`); the generator produces it automatically — `A_0 = 1`, `A_1 = 1 ∧ v_1 = v_1`, and
  `c_1 = reverse(1) * A_1 = v_1`. So the generator form *subsumes* the base case, where the
  rejection form (part 1) still carries an explicit `match`. That contrast is itself pedagogical.
- **It is O(k) wedges, not O(k²).** The current code rebuilds `A_{k-1}` and `A_k` from scratch each
  step via `outer_product_of_vectors(*vectors[:k])`; carrying the running wedge builds each blade
  once. (Behavior is identical — this is a side benefit, not the goal.)

Keep the cross-referencing docstrings (the equivalence prose, the `See also`) — update only the
"how it's computed" sentences to describe the generators.

## Verification gate

Behavior-preserving, so the proof is the existing tests passing unchanged — do **not** edit
`tests/test_frame.py`:

1. `make test` green (the ~16 frame tests, incl. `test_hestenes_equals_rejection_*` in 2D/3D,
   symbolic and numeric, and the single-vector / first-vector-unchanged / dependent-raises cases;
   plus `--doctest-modules` on the rewritten docstrings).
2. `make format` clean — `ruff check`, `ruff format`, `ty check` (annotate every new binding;
   `Iterator` from `collections.abc`).
3. Spot-confirm by eye that the public signatures and return type (`list[MultiVectorBase]`) are
   untouched.

Stage `src/gacalc/frame.py` when green; this task then archives per the lifecycle (its own commit
after the work commit). No `CHANGELOG` entry — the public API is unchanged.

## Open questions

1. **RESOLVED 2026-10-22 (William Emerison Six <billsix@gmail.com>): the state-carrying loop
   generator** — exactly the part-2 sketch. The inner generator carries the running wedge forward
   (`A_0 = 1`, then `A_k = A_{k-1} ∧ v_k`) and the outer one carries the previous blade to pair
   consecutive blades (`c_k = reverse(A_{k-1}) * A_k`); **not** a recursive `yield from` form. No
   other open questions — the design is settled; implement part 2 as written.
