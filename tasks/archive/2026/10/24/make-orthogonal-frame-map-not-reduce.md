# Rewrite `make_orthogonal_frame` as nil/cons recursion + a map over the tail (not reduce + an accumulator)

## BLUF

Reworked the 2026-10-22 recursive `make_orthogonal_frame` in `src/gacalc/frame.py` from
`reduce` + a hand-threaded accumulator into the textbook Lisp/SICP shape: `match` on the
**nil/cons** split, keep the head vector, **map** the rejection of that head over the tail (a
comprehension), and recurse on the mapped tail. This removed the `functools.reduce`, the `done`
accumulator, and the reversed argument order. A follow-on in the same file replaced
`make_orthogonal_frame_hestenes`'s manual carried-previous-blade generator with
`itertools.pairwise(prefix_blades(...))` (the "adjacent pairs as an iterable" scheme). The new
form is Modified Gram–Schmidt, which equals the old Classical form **exactly** in symbolic
arithmetic, so `tests/test_frame.py` is **unchanged** and still passes. The durable style rule
(map/filter-first, reduce last and name its accumulator) was recorded in a new cross-project
reference doc, `recursive-design.md` — that was the point of the task, not an afterthought.

## Status

**Status:** complete
**Completed:** 2026-10-24 (William Emerison Six <billsix@gmail.com>) — done 2026-10-23, committed
2026-10-24; archived pending the maintainer's squash of the work commit.
Part A (both `frame.py` functions) and Part B (the `recursive-design.md` doc + wiring) are both
done and green; all three decisions are resolved. One implementation surprise (`ty` rejects a bare
`case []`/`case [v, *rest]` list-match as non-exhaustive, forcing a `case _` base) is recorded
below and in `recursive-design.md`.
**Priority:** 3
**Difficulty:** 3
**Created:** 2026-10-23 (William Emerison Six <billsix@gmail.com>)
Follow-up to `tasks/archive/2026/10/22/refactor-orthogonal-frame-recursive-generators.md`
(the rewrite improved here). Part of the frames work — see `tasks/define-frame.md`.
Touched only Python style + a cross-repo convention doc; no public API or math change.

## Context

Two functions in `src/gacalc/frame.py` were in scope: `make_orthogonal_frame` (the
rejection/Gram–Schmidt function — the main rework) and `make_orthogonal_frame_hestenes` (a small
follow-on — express its adjacent-blade pairing as `itertools.pairwise`). The `prefix_blades`
primitive stayed **as-is** — its `itertools.accumulate` is a genuine running-wedge scan/fold,
correct by the very rule this task is about.

The 2026-10-22 rewrite being improved had this shape:

```python
def reject_span(v, prior):
    return functools.reduce(lambda w, p: w.rejected_away_from(p), prior, v)

def orthogonalize(remaining, done):
    match list(remaining):
        case [v]:        return [*done, reject_span(v, done)]
        case [v, *rest]: return orthogonalize(rest, [*done, reject_span(v, done)])
        case _:          return done          # "unreachable"
return orthogonalize(vectors, [])
```

The maintainer raised three critiques; all three were correct:

1. **Reversed argument order.** `reject_span(v, prior)` handed its parameters to
   `functools.reduce(func, prior, v)` in the opposite order, and "the accumulated value" sat as
   the first lambda arg (`w`) but the second helper parameter (`done`) — the reader tracked the
   accumulator in two positions. The redesign deleted both the `reduce` and the accumulator, so
   the inconsistency is gone rather than patched.
2. **Default the accumulator.** `orthogonalize` could have defaulted its accumulator to call
   `orthogonalize(vectors)`, but a literal `done=[]` is the shared-mutable-default footgun (ruff
   **B006**); the safe idiom is a `None` sentinel. The cleaner answer, taken here: the nil/cons +
   map shape needs **no accumulator parameter at all**. (The general rule — when a real
   accumulator is unavoidable, name it `acc`/`accumulator` and never default it to a mutable
   literal — is recorded in `recursive-design.md`.)
3. **Map/comprehension, not reduce.** The natural structure is the sieve: take the head (already
   orthogonal to everything finalized before it), map its rejection over the tail, recurse on the
   mapped tail, cons the head on the front. No `reduce`, no accumulator.

**Why the tests passed unchanged (the thing to be sure of).** The old code was **Classical
Gram–Schmidt** (reject all previously-finalized vectors out of each new vector); the new map
version is **Modified Gram–Schmidt** (reject each finalized head out of every remaining vector,
then recurse). In **exact** arithmetic these are identical: when rejecting a finalized head `w_j`
out of a partially-processed `u`, the terms already removed from `u` lie along `w_1 … w_{j-1}`,
all orthogonal to `w_j`, so the component removed equals `proj(v_k, w_j)` either way. gacalc is
exact (symbolic / rational `Real`), and `tests/test_frame.py` checks exact symbolic orthogonality
and the exact equivalence `c_k == |A_{k-1}|² * w_k` against `make_orthogonal_frame_hestenes`
(unchanged). So every `w_k` is identical and every assertion still holds. Both forms also reject
from a *single* vector at a time, staying within gacalc's grade-1/grade-2 rejection.

The style principle behind the critique — reach for the most specific sequence operation
(map/filter) and drop to a fold only when a running accumulated value is genuinely needed, naming
its accumulator `acc` — and its references (SICP §2.2.3, Norvig & Pitman, Graham's *On Lisp*
§15.2, van Rossum on `reduce`'s demotion) now live in the durable reference doc; see Part B. The
maintainer's own formulation, adopted as the rule: **map and filter first when they fit; reduce
only when actually required; and a reduce's accumulator is named `acc`/`accumulator` in the
conventional position.**

## What was done

### A1. `make_orthogonal_frame` — nil/cons recursion + map over the tail

The `is_frame` guard was kept; the body became:

```python
def orthogonalize(
    remaining: Sequence[MultiVectorBase],
) -> list[MultiVectorBase]:
    match list(remaining):
        case [v, *rest]:
            rest_orthogonal_to_v: list[MultiVectorBase] = [
                w.rejected_away_from(v) for w in rest
            ]
            return [v, *orthogonalize(rest_orthogonal_to_v)]
        case _:  # the empty list -- base case (wildcard, see the type-checker note)
            return []
return orthogonalize(vectors)
```

Point by point: (1) no `functools.reduce` and no lambda `(w, p)` order to reconcile — the
reversal is gone; (2) no accumulator parameter, so nothing to default and no B006 trap; (3) the
per-element work is a comprehension (a map over the tail) and the recursion is the plain nil/cons
cons-on-the-front shape. `import functools` was removed (nothing else in the file used it);
`operator` stayed (used by `prefix_blades`). The docstring's "how it's computed" prose was
reworded from the Classical argument to the progressive/sieve (Modified Gram–Schmidt) mechanism;
the unchanged facts were kept (first vector returned as-is, orthogonal-not-orthonormal, and the
`c_k == |A_{k-1}|² * w_k` equivalence paragraph — the math result is unchanged).

**Type-checker surprise (found at implementation).** `case []` + `case [v, *rest]` is exhaustive
in principle, but gacalc's `ty` does **not** prove a list-pattern match exhaustive — it errors
`invalid-return-type` ("can implicitly return `None`"). So the base case is spelled as the
wildcard **`case _`** (reachable and meaningful — the empty list — not a dead branch), with the
cons case first. This still honors "drop the dead `# unreachable` branch" (decision 2) and the
house total-dispatch rule, and satisfies the checker. Recorded as a lesson in `recursive-design.md`.

### A2. `make_orthogonal_frame_hestenes` — pair the blades with `itertools.pairwise`

The eq-3.2 step (`c_k = reverse(A_{k-1}) · A_k`) pairs each blade with the one before it. The old
`hestenes_vectors` generator did this by manually carrying the previous blade across loop
iterations — the pairwise-adjacent scheme spelled by hand. It became one comprehension:

```python
return [
    (A_k_minus_1.reverse() * A_k).r_vector_part(1)
    for A_k_minus_1, A_k in pairwise(prefix_blades(vectors))
]
```

`pairwise(prefix_blades(...))` yields `(A_0, A_1), (A_1, A_2), …` — the adjacent `(A_{k-1}, A_k)`
pairs, and the single-pass-safe form of `zip(xs, xs[1:])` (`prefix_blades` returns a lazy iterator
that cannot be sliced `[1:]`). `c_1` needs no special case (`A_0 = 1`, `A_1 = v_1`). The nested
`def hestenes_vectors()` and the manual carry are gone; the `# c_k := … (eq 3.2)` comment and the
`c_1` explanation were kept. Imports became `from itertools import accumulate, pairwise`;
`Iterator` stayed (`prefix_blades` still returns one). Behavior is identical, so
`test_prefix_blades_feeds_hestenes` and `test_hestenes_equals_rejection_*` pass unchanged.

## Part B — where the style rule was recorded (cross-repo)

Done across the repos (all mounted this session under `/foo/opt/`):

- **Technique body + references + this `frame.py` worked example → a NEW
  `recursive-design.md`**, canonical in runClaudeInContainer `tasks/reference/`
  (github.com/billsix/runClaudeInContainer), with **byte-identical** copies in runCrushInContainer
  `tasks/reference/` and its baked crush-client set
  (`client/entrypoint/dotfiles/.config/crush/reference/`). A language-agnostic (Lisp/Haskell-rooted)
  guide: structural recursion (shape follows the data), the nil/cons template, map/filter/fold as
  named recursion schemes, accumulator-passing discipline (`acc`), fold direction, the Python
  spellings + no-TCO/recursion-limit caveat, and the before/after of this `frame.py` rework. A
  trigger line was added to the shared cross-project `CLAUDE.md` reference-docs index ("before
  writing or reviewing a non-trivial recursion, or choosing a recursion scheme").
- **Terse Python spelling → `python-coding-standard.md`** (a 3-way byte-identical mirror): the
  existing §"Reduce with `sum`/`math.prod`…" was extended with map/filter-first + name-the-accumulator
  and a pointer to `recursive-design.md`; the idioms line now mentions `itertools.pairwise`. All
  three copies kept in sync.
- **runCrush `container-file-layout.md`** (both the repo and baked copies) gained the
  `recursive-design.md` row in the baked-vs-repo mapping table.
- **NOT** the personal AI file (this is a general coding standard, not identity/authorization) and
  **NOT** gacalc-only (it is cross-project). gacalc's own
  `tasks/reference/conditional-refactoring-rules.md` already cross-references the technique via
  `recursive-design.md`'s "project's own additions doc" note.

## Decisions (all resolved)

1. **Where the recursive/functional-design knowledge lives.** A new dedicated, language-agnostic
   `recursive-design.md` reference doc (not `code-style-conventions.md`, not gacalc-only, not the
   personal file), with the terse Python spelling pointing at it from `python-coding-standard.md`.
   RESOLVED 2026-10-23 (William Emerison Six <billsix@gmail.com>): **yes, bake it into the Crush
   client reference set too**, so the doc has three byte-identical homes in parallel with the
   Python standard. (Done — Part B.)
2. **Drop the dead `case _`.** RESOLVED 2026-10-23 (William Emerison Six <billsix@gmail.com>). The
   old `case _: # unreachable` is gone. Caveat found at implementation: `ty` does not prove a bare
   `case []`/`case [v, *rest]` match exhaustive, so the empty base case is spelled `case _` — still
   reachable and meaningful, not a dead branch (see the type-checker note in A1).
3. **Include the Hestenes pairwise cleanup** (A2). RESOLVED 2026-10-23 (William Emerison Six
   <billsix@gmail.com>): express the adjacent-blade pairing as `itertools.pairwise(prefix_blades(...))`,
   the single-pass-safe `zip`; `prefix_blades` itself unchanged.

## Verification

Behavior-preserving, so the proof is the **existing** `tests/test_frame.py` passing **unchanged**
(it was not edited). Both gates ran green in-container:

- `make test` — 711 passed, including the 20 `test_frame.py` tests (keeps-first, 2D/3D symbolic +
  concrete + numeric mutual orthogonality, raises-on-dependent, and the
  `test_hestenes_equals_rejection_*` equivalence that would catch any change to the `w_k` values)
  and the frame.py doctests via `--doctest-modules`.
- `make format` — `ruff check` + `ruff format` + `ty check` + `check_changelog`, all clean.

No `CHANGELOG` entry (public API unchanged).

## History

The work landed in gacalc as a task-add (this doc) followed by the `frame.py` rework (A1 + A2)
and the task-doc update — the maintainer squashes those to one commit-per-task on their own
schedule. The cross-repo doc work (Part B) landed in its own repos: `recursive-design.md` and the
`CLAUDE.md`/`python-coding-standard.md` wiring in runClaudeInContainer, with byte-identical copies
in runCrushInContainer (its `tasks/reference/` and the baked crush-client set). See each repo's
`git log` for the commits — SHAs are omitted here because this history was still being rewritten
when the doc was archived.
