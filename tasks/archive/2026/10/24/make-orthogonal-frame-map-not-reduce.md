# Rewrite `make_orthogonal_frame` as nil/cons recursion + a map over the tail (not reduce + an accumulator)

**Created:** 2026-10-23 · **Completed:** 2026-10-24 (William Emerison Six <billsix@gmail.com>)
**Part of:** the frames work, `tasks/define-frame.md`. Follow-up to
`tasks/archive/2026/10/22/refactor-orthogonal-frame-recursive-generators.md` (the rewrite improved
here).

The 2026-10-22 recursive `make_orthogonal_frame` in `src/gacalc/frame.py` was reworked from
`reduce` + a hand-threaded accumulator into the textbook Lisp/SICP shape: `match` on the nil/cons
split, keep the head vector, map the rejection of that head over the tail (a comprehension), and
recurse on the mapped tail. A follow-on in the same file replaced `make_orthogonal_frame_hestenes`'s
manual carried-previous-blade generator with `itertools.pairwise(prefix_blades(...))`. Only Python
style and a cross-repo convention doc changed; no public API or math change. `prefix_blades` stayed
as-is: its `itertools.accumulate` is a genuine running-wedge fold.

## The critique

The 2026-10-22 form was `orthogonalize(remaining, done)` recursing with `[*done, reject_span(v, done)]`,
where `reject_span(v, prior) = functools.reduce(lambda w, p: w.rejected_away_from(p), prior, v)`, plus
a `case _: return done  # "unreachable"` branch. The maintainer raised three critiques; all three were
correct:

1. **Reversed argument order.** `reject_span(v, prior)` passed its parameters to `reduce(func, prior, v)`
   in the opposite order, and the accumulated value was the first lambda arg (`w`) but the second
   helper parameter (`done`). The redesign deleted both the `reduce` and the accumulator.
2. **Default the accumulator.** A literal `done=[]` default is the shared-mutable-default footgun (ruff
   B006; the safe idiom is a `None` sentinel). The nil/cons + map shape needs no accumulator at all.
3. **Map/comprehension, not reduce.** The natural structure is the sieve: take the head, map its
   rejection over the tail, recurse on the mapped tail, cons the head on the front.

The maintainer's formulation, adopted as the rule: **map and filter first when they fit; reduce only
when actually required; and a reduce's accumulator is named `acc`/`accumulator` in the conventional
position.**

## What changed

**A1. `make_orthogonal_frame`.** The `is_frame` guard was kept; the body became a nested
`orthogonalize(remaining)` whose `match list(remaining)` has `case [v, *rest]:` returning
`[v, *orthogonalize([w.rejected_away_from(v) for w in rest])]` (via a named
`rest_orthogonal_to_v` list) and `case _:` returning `[]`. `import functools` was removed. The
docstring's "how it's computed" prose was reworded from the Classical argument to the sieve (Modified
Gram–Schmidt) mechanism; the unchanged facts (first vector returned as-is, orthogonal-not-orthonormal,
the `c_k == |A_{k-1}|² * w_k` equivalence) were kept.

**Type-checker surprise.** `case []` + `case [v, *rest]` is exhaustive in principle, but `ty` does not
prove a list-pattern match exhaustive (it reports `invalid-return-type`, "can implicitly return
`None`"). So the empty base case is the wildcard `case _`, reachable and meaningful, with the cons case
first. Recorded as a lesson in `recursive-design.md`.

**A2. `make_orthogonal_frame_hestenes`.** The eq-3.2 step pairs each blade with the one before it; the
old `hestenes_vectors` generator carried the previous blade by hand. It became one comprehension,
`[(A_k_minus_1.reverse() * A_k).r_vector_part(1) for A_k_minus_1, A_k in pairwise(prefix_blades(vectors))]`.
`pairwise` is the single-pass-safe form of `zip(xs, xs[1:])` (`prefix_blades` returns a lazy iterator
that cannot be sliced). `c_1` needs no special case (`A_0 = 1`). Imports became
`from itertools import accumulate, pairwise`.

## Why the tests passed unchanged

The old code was Classical Gram–Schmidt (reject all finalized vectors out of each new one); the new
one is Modified Gram–Schmidt (reject each finalized head out of every remaining vector). In exact
arithmetic they are identical: when rejecting `w_j` from a partially processed `u`, the terms already
removed lie along `w_1 … w_{j-1}`, all orthogonal to `w_j`, so the removed component equals
`proj(v_k, w_j)` either way. gacalc is exact, and `tests/test_frame.py` checks exact symbolic
orthogonality and `c_k == |A_{k-1}|² * w_k` against the Hestenes form, so every `w_k` is identical.
Both forms reject from a single vector at a time, within gacalc's grade-1/grade-2 rejection.

## Where the style rule was recorded (cross-repo)

In the repos github.com/billsix/runClaudeInContainer and github.com/billsix/runCrushInContainer:

- A new language-agnostic `recursive-design.md`, canonical in runClaudeInContainer
  `tasks/reference/`, with byte-identical copies in runCrushInContainer `tasks/reference/` and its baked
  crush-client set (`client/entrypoint/dotfiles/.config/crush/reference/`): structural recursion, the
  nil/cons template, map/filter/fold as named schemes, accumulator discipline (`acc`), fold direction,
  the Python spellings + no-TCO caveat, and this `frame.py` before/after. References: SICP §2.2.3,
  Norvig & Pitman, Graham's *On Lisp* §15.2, van Rossum on `reduce`'s demotion. A trigger line was
  added to the shared cross-project `CLAUDE.md` reference-docs index.
- `python-coding-standard.md` (3-way byte-identical mirror): the "Reduce with `sum`/`math.prod`"
  section gained map/filter-first + name-the-accumulator and a pointer to `recursive-design.md`; the
  idioms line mentions `itertools.pairwise`.
- runCrushInContainer `container-file-layout.md` (repo and baked copies) gained the
  `recursive-design.md` row.
- Not the personal AI file (a general coding standard, not identity) and not gacalc-only. gacalc's
  `tasks/reference/conditional-refactoring-rules.md` already cross-references the technique.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-10-23)

1. **Where the knowledge lives:** a new dedicated `recursive-design.md` (not
   `code-style-conventions.md`, not gacalc-only, not the personal file), also baked into the Crush
   client reference set, so it has three byte-identical homes like the Python standard.
2. **Drop the dead `# unreachable` branch.** Done; the `case _` that remains is the real empty base
   case (see the type-checker note).
3. **Include the Hestenes pairwise cleanup** (A2), with `prefix_blades` unchanged.

## Verification

`tests/test_frame.py` was not edited and passed. In-container: `make test` — 711 passed, including
the 20 `test_frame.py` tests (2D/3D symbolic + concrete + numeric orthogonality, raises-on-dependent,
the `test_hestenes_equals_rejection_*` equivalence) and the `frame.py` doctests; `make format` (ruff
check + format, `ty check`, `check_changelog`) clean. No `CHANGELOG` entry (public API unchanged).
SHAs were omitted because the history was still being squashed when the doc was archived.
