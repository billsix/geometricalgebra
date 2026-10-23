# Rewrite `make_orthogonal_frame` as nil/cons recursion + a map over the tail (not reduce + an accumulator)

## BLUF

The 2026-10-22 recursive rewrite of `make_orthogonal_frame` in `src/gacalc/frame.py` is
*correct* but not in the best functional style. Rework it into the textbook Lisp/SICP shape:
`match` on the **nil/cons** split (`[]` vs `[v, *rest]`), keep the head vector, **map** the
rejection of that head over the tail (a comprehension), and recurse on the mapped tail —
removing the `functools.reduce`, the hand-threaded `done` accumulator, and the reversed
argument order. This is Modified Gram–Schmidt, which equals the current Classical form
**exactly** in symbolic arithmetic, so **`tests/test_frame.py` stays byte-for-byte unchanged**
and still passes; `make format` (ruff + ty) stays clean. A small follow-on in the same file:
replace `make_orthogonal_frame_hestenes`'s manual carried-previous-blade generator with
`itertools.pairwise(prefix_blades(...))` — the named "adjacent pairs as an iterable" scheme (the
single-pass-safe form of `zip(xs, xs[1:])`). "Done" also includes recording the
underlying map/filter-over-reduce style rule in the right place (see Part B + Open question 1)
— **the maintainer cares about this; it is the point of the task, not an afterthought.**

## Status

**Status:** proposed — needs go-ahead (open questions below block implementation)
**Priority:** 3
**Difficulty:** 3
**Created:** 2026-10-23 (William Emerison Six <billsix@gmail.com>)
Follow-up to `tasks/archive/2026/10/22/refactor-orthogonal-frame-recursive-generators.md`
(the rewrite being improved here). Part of the frames work — see `tasks/define-frame.md`.
Touches only Python style + a cross-repo convention doc; no public API or math changes.

## Context (cold-start orientation)

- **Two functions** in `src/gacalc/frame.py` are in scope (read that file first):
  `make_orthogonal_frame` (~line 121, the rejection/Gram–Schmidt function — the main rework) and
  `make_orthogonal_frame_hestenes` (~line 178, a small follow-on: express its adjacent-blade
  pairing as `itertools.pairwise` — see Part A2). The `prefix_blades` primitive (~line 88) stays
  **as-is** — its `itertools.accumulate` is a genuine running-wedge scan/fold, correct by the very
  rule this task is about.
- **Current shape** (the thing to improve):
  ```python
  def reject_span(v, prior):
      return functools.reduce(lambda w, p: w.rejected_away_from(p), prior, v)

  def orthogonalize(remaining, done):
      match list(remaining):
          case [v]:            return [*done, reject_span(v, done)]
          case [v, *rest]:     return orthogonalize(rest, [*done, reject_span(v, done)])
          case _:              return done   # "unreachable"

  return orthogonalize(vectors, [])
  ```
- **The maintainer's three critiques, and my verdict (I agree with all three):**
  1. **Reversed argument order — agree.** `reject_span` declares parameters `(v, prior)` but
     hands them to `functools.reduce(func, prior, v)` in the opposite order (iterable `prior`,
     then initial value `v`). Separately, "the accumulated value" sits as the **first** lambda
     arg (`w`) inside the `reduce` but as the **second** parameter (`done`) of `orthogonalize`
     — so the reader tracks the accumulator in two different positions. The redesign deletes
     both the `reduce` and the accumulator, so the inconsistency disappears rather than being
     patched.
  2. **Default the accumulator — agree in spirit, better to remove it.** Yes, `orthogonalize`
     could default its accumulator so the call is just `orthogonalize(vectors)`. But a literal
     `done: list[...] = []` is the classic shared-mutable-default footgun (ruff **B006**); the
     safe idiom is a `None` sentinel (`done=None` then `done = done or []`). The cleaner answer
     is the one the redesign takes: the nil/cons + map shape needs **no accumulator parameter
     at all**, so there is nothing to default. (Worth stating the general rule anyway, Part B:
     when a real accumulator is unavoidable, name it `acc`/`accumulator` and never default it
     to a mutable literal.)
  3. **Map/comprehension, not reduce — strongly agree.** The natural structure is the "sieve":
     take the head (already orthogonal to everything finalized before it), **map** its
     rejection over the tail, recurse on the mapped tail, and cons the head on the front. No
     `reduce`, no accumulator, and the `[]` base case becomes a **real, reachable** case
     instead of a `case _` labelled "unreachable."

- **Why the tests still pass (the one thing to be sure of).** The current code is **Classical
  Gram–Schmidt** (for each new vector, reject out all previously-finalized vectors). The
  maintainer's map version is **Modified Gram–Schmidt** (take each finalized head, reject it
  out of every remaining vector, recurse). In **exact** arithmetic these produce **identical**
  results: when rejecting the finalized head `w_j` out of a partially-processed `u`, the terms
  already removed from `u` lie along `w_1 … w_{j-1}`, which are all orthogonal to `w_j`, so the
  component removed is exactly `proj(v_k, w_j)` either way. gacalc is exact (symbolic / rational
  `Real`), and `tests/test_frame.py` checks exact symbolic orthogonality and the exact
  equivalence `c_k == |A_{k-1}|² * w_k` against `make_orthogonal_frame_hestenes` (unchanged). So
  `w_k` is identical and every assertion still holds. (Both forms also still reject from a
  *single* vector at a time, so they stay within gacalc's grade-1/grade-2 rejection.)

## Theory and references (the style principle behind the critique)

**Reach for the most specific sequence operation that does the job; drop to a general fold only
when the computation genuinely needs the running accumulated value.** A 1:1 transform is a
**map** (or a comprehension); a selection is a **filter**; a true reduction — each step needs
the value accumulated so far — is a **reduce/fold**, and then its accumulator is named for what
it holds (`acc`/`accumulator`) and kept in the conventional position. Structural list recursion
is the **nil/cons** split: a base case for `[]` and a recursive case for `[head, *tail]` that
does the per-element work by **mapping over the tail**, not by threading a hand-rolled
accumulator through an extra parameter.

The maintainer's own formulation, adopted here: **map and filter are the first choice when they
fit; reduce only when it is actually required; and a reduce's accumulator argument is named
`acc`/`accumulator`** (never a bare `w`/`x` whose role the reader must reconstruct).

This is long-standing Lisp/functional guidance, not a personal quirk:

- **SICP §2.2.3, "Sequences as Conventional Interfaces"** (Abelson & Sussman). map/filter/
  accumulate are a *signal-flow pipeline* of independent stages (enumerate → filter → map →
  accumulate), each with exactly one job. Primary-source reads (verified today): a direct
  recursion "fail[s] to exhibit this signal-flow structure" because the stages are "tangled
  together in the recursion," and expressing structures through the conventional sequence
  operations "localized the data-structure dependencies … to a small number of sequence
  operations." The lesson: prefer the named stage (map/filter/accumulate) that makes the one
  job explicit over a recursion that hides it.
  <https://sicp.sourceacademy.org/chapters/2.2.3.html>
- **Norvig & Pitman, "Tutorial on Good Lisp Programming Style"** (1993). Maxims include **be
  explicit, be specific, be concise, be consistent, be conventional.** "Be specific" = use the
  most specific operator that expresses the intent (a `map` says "transform each," a bare
  `reduce` does not); "be conventional" = name and shape things the way a reader expects (the
  accumulator). (Maxims from today's search; full slides:
  <https://www.cs.umd.edu/~nau/cmsc421/norvig-lisp-style.pdf> — note the cert was flaky, use a
  mirror.)
- **Paul Graham, *On Lisp*** — ch. 5 (functional programming) and **§15.2 "Recursion on
  Cdrs."** The canonical list recursion is the nil/cons shape (handle the `car`, recurse on the
  `cdr`); `mapcar` is the idiom for a 1:1 transform over a list. Our redesign is exactly
  "process the head, map over the cdr, recurse."
  <https://redirect.cs.umbc.edu/courses/331/resources/lisp/onLisp/15macrosReturningFunctions.pdf>
- **Guido van Rossum, "The fate of reduce() in Python 3000"** (2005). `reduce` was demoted from
  a builtin to `functools` because in practice it was "used almost only to implement `sum()`"
  or to "write unreadable code"; `map`/`filter` were kept and comprehensions preferred, and a
  plain `for` loop is usually more readable than a `reduce`. This is the Python-specific echo of
  the same principle (reduce is the tool of last resort). (Secondary source — his original post
  quoted at <https://blog.finxter.com/about-guidos-fate-of-reduce-in-python-3000/>; corroborated
  by Real Python <https://realpython.com/python-reduce-function/>.)

**Where a genuine fold *is* right** (so the rule is not "never reduce"): `prefix_blades` in the
same file legitimately uses `itertools.accumulate` — a running wedge where each blade depends on
the previous accumulation is a true scan/fold, and the builtin names it. The guidance is to
prefer map/filter *when they fit*, not to purge every fold.

## Proposed design

### A1. `make_orthogonal_frame` — nil/cons recursion + map over the tail

Keep the `is_frame` guard unchanged; replace the body:

```python
def make_orthogonal_frame(
    vectors: Sequence[MultiVectorBase],
) -> list[MultiVectorBase]:
    """...docstring updated to describe the sieve (progressive rejection)..."""
    if not is_frame(vectors):
        raise ValueError(...)  # unchanged

    def orthogonalize(
        remaining: Sequence[MultiVectorBase],
    ) -> list[MultiVectorBase]:
        match list(remaining):
            case []:  # base case -- empty tail
                return []
            case [v, *rest]:
                # v is already orthogonal to every vector finalized before it (each
                # earlier head was rejected out of it on the way down), so keep it and
                # reject it out of each remaining vector, then recurse on that tail.
                rest_orthogonal_to_v: list[MultiVectorBase] = [
                    w.rejected_away_from(v) for w in rest
                ]
                return [v, *orthogonalize(rest_orthogonal_to_v)]

    return orthogonalize(vectors)
```

What this fixes, point by point:
- **(1)** No `functools.reduce`, no lambda with a `(w, p)` arg order to reconcile against the
  helper's parameters — the reversal is gone.
- **(2)** No accumulator parameter, so nothing to default (and no B006 mutable-default trap).
- **(3)** The per-element work is a **comprehension** (`[w.rejected_away_from(v) for w in rest]`)
  — a map over the tail — and the recursion is the plain nil/cons cons-on-the-front shape. The
  `[]` case is now reachable and meaningful; the `case _: # unreachable` is gone.

Also update the docstring's "how it's computed" prose: it currently argues the Classical form
("each subsequent vector has the span of the ones before it rejected out … rejecting them one
at a time equals rejecting the whole span"). Reword to the progressive/sieve mechanism
(Modified Gram–Schmidt: each finalized head is rejected out of all the vectors after it), and
**keep** the unchanged facts: first vector returned as-is, result is orthogonal-not-orthonormal,
and the equivalence-to-`make_orthogonal_frame_hestenes` paragraph (`c_k == |A_{k-1}|² * w_k`,
still true — the math result is unchanged). `functools` and `operator` imports: `operator` is
still used by `prefix_blades`; `functools` becomes unused here — **remove the `import functools`
only if nothing else in the file uses it** (grep first).

### A2. `make_orthogonal_frame_hestenes` — pair the blades with `itertools.pairwise`

The eq-3.2 step pairs each blade with the one before it (`c_k = reverse(A_{k-1}) · A_k`). The
current `hestenes_vectors` generator does this by **manually carrying the previous blade** across
loop iterations (`A_k_minus_1 = next(blades)`, then reassign inside the loop). That carried-state
loop *is* the pairwise-adjacent recursion scheme spelled out by hand — `itertools.pairwise` is its
name. Replace the whole generator with one comprehension over the pairs:

```python
return [
    (A_k_minus_1.reverse() * A_k).r_vector_part(1)
    for A_k_minus_1, A_k in itertools.pairwise(prefix_blades(vectors))
]
```

`itertools.pairwise(iterable)` yields `(A_0, A_1), (A_1, A_2), …` — exactly the adjacent
`(A_{k-1}, A_k)` pairs, and it is the **single-pass-safe** form of the `zip(xs, xs[1:])` idiom:
`prefix_blades` returns a lazy iterator, which cannot be sliced `[1:]`, so `pairwise` (which tees
one iterator internally) is the right tool rather than materializing a list to `zip`. This drops
the nested `def hestenes_vectors()` generator and the manual carry; keep the `# c_k := … (eq 3.2)`
comment and the `c_1` explanation on the comprehension. Add `import itertools` (and drop the now
possibly-unused `Iterator` import from `collections.abc` **iff** nothing else in the file needs it
— grep; `prefix_blades` still returns an `Iterator`, so it is very likely still needed). Behavior
is identical, so `test_prefix_blades_feeds_hestenes` and the `test_hestenes_equals_rejection_*`
tests pass unchanged.

## Part B — where to record the style rule (cross-repo; see Open question 1)

My recommendation (the maintainer decides in Open question 1):

- **Canonical rule → `python-coding-standard.md`**, extending the existing §"Reduce with `sum` /
  `math.prod`, not a hand-rolled accumulator loop" (it already owns "don't hand-roll accumulators"
  and mentions `functools.reduce`). Add: *prefer map/filter/comprehension first; use
  `functools.reduce` only for a genuine associative fold the builtins don't cover, and then name
  its accumulator `acc`/`accumulator` in the conventional first position.* Tighten the idioms-line
  "comprehensions over trivial map/filter+loop" to point at it.
  **This doc is a THREE-way byte-identical mirror** (verified 2026-10-23; the doc's own banner lists
  them) — edit the canonical, then re-copy over the other two so all three stay byte-identical
  (banner included):
  1. `runClaudeInContainer/tasks/reference/python-coding-standard.md` (canonical;
     github.com/billsix/runClaudeInContainer)
  2. `runCrushInContainer/tasks/reference/python-coding-standard.md`
  3. `runCrushInContainer/client/entrypoint/dotfiles/.config/crush/reference/python-coding-standard.md`
     (the baked crush-client copy — how a project developed *with Crush* gets the standard)
  **All three are mounted this session (both sandboxes are under `/foo/opt/`), so this sync is
  doable now — not an owed follow-up.**
- **Technique body + references + this `frame.py` worked example → a NEW
  `tasks/reference/recursive-design.md`** (canonical in runClaudeInContainer; direction set
  2026-10-23 — see Open question 1). A language-agnostic (Lisp/Haskell-rooted) guide: structural
  recursion (shape follows the data), the nil/cons template, **map/filter/fold as named recursion
  schemes** (prefer the matching scheme; hand-roll recursion only when none fits), the
  accumulator-passing discipline (`acc`, and when it is actually warranted), fold direction, and
  the **Python no-TCO / recursion-limit caveat** (iterate when deep; structural recursion when the
  structure is bounded). This **supersedes** the earlier idea of putting the rationale into
  `code-style-conventions.md`. Add a trigger line to the shared cross-project `CLAUDE.md`
  reference-docs index ("before writing or reviewing a non-trivial recursion, or choosing a
  recursion scheme") — and that CLAUDE.md line has a baked crush mirror to sync. Whether the new
  doc itself is baked into the crush client set is Open question 1.
- **gacalc `tasks/reference/conditional-refactoring-rules.md`** gets this case as a worked example
  (or a pointer to `recursive-design.md`) — it already collects gacalc's
  conditional/structural-refactor examples, and this `make_orthogonal_frame` before/after is a
  clean one.
- **NOT** the personal AI file (`ai-coding-conventions.personal.md`) — this is a general coding
  standard, not identity / project-mapping / standing-authorization. **NOT** gacalc-only — it is
  cross-project.

## Verification gate

Behavior-preserving, so the proof is the **existing** tests passing **unchanged** — do **not**
edit `tests/test_frame.py`:

1. `make test` green — the ~16 frame tests, especially `test_orthogonal_frame_*` (keeps-first,
   2D/3D symbolic + concrete + numeric mutual orthogonality, raises-on-dependent) and the
   `test_hestenes_equals_rejection_*` equivalence tests (these are the ones that would catch any
   accidental change to the `w_k` values), plus the frame.py doctests via `--doctest-modules`.
   The Hestenes-side change (Part A2) is covered by `test_prefix_blades_feeds_hestenes` and the
   same `test_hestenes_equals_rejection_*` tests — all unchanged.
2. `make format` clean — `ruff check` (watch B006 if any accumulator survives; it should not),
   `ruff format`, `ty check`. Annotate every new binding (`rest_orthogonal_to_v: list[...]`).
3. Spot-confirm by eye: both public signatures and the `list[MultiVectorBase]` returns unchanged;
   `import itertools` added (Part A2); `import functools` removed iff now unused, and the
   `Iterator` import kept iff `prefix_blades` (or anything else) still needs it — `operator` and
   `accumulate` stay (used by `prefix_blades`).

Stage `src/gacalc/frame.py` when green; the doc edits in Part B stage within their own repos
(runClaudeInContainer + runCrushInContainer — both mounted under `/foo/opt/`, so the mirror syncs
happen in the same work). No `CHANGELOG` entry (public API unchanged). Archive per the lifecycle
(own commit after the work commit).

## Open questions

1. **Where should the recursive/functional-design knowledge live?** DIRECTION SET in discussion
   2026-10-23 (William Emerison Six <billsix@gmail.com>): **a new dedicated, language-agnostic
   `recursive-design.md` reference doc** — the positive body of technique (structural recursion =
   shape follows the data; the nil/cons template; map/filter/fold *as* named recursion schemes,
   prefer the matching scheme and hand-roll only when none fits; accumulator-passing style and
   when it is actually warranted, named `acc`; fold direction; the Python no-TCO / recursion-limit
   caveat → iterate when deep, structural recursion when bounded). References + the `frame.py`
   before/after as the worked example. The **Python spelling** stays terse in
   `python-coding-standard.md` (comprehension-first; `reduce` last and name its accumulator) and
   **points at** `recursive-design.md`; that new doc replaces the earlier
   "rationale-in-code-style-conventions.md" idea (this is technique, not just
   rationale-behind-a-terse-rule). Canonical copy in runClaudeInContainer
   `tasks/reference/recursive-design.md`, trigger-indexed in the shared cross-project `CLAUDE.md`
   ("before writing or reviewing a non-trivial recursion, or choosing a recursion scheme"); worked
   example also pointed at from gacalc's `conditional-refactoring-rules.md`; **not** the personal
   AI file, **not** gacalc-only. The Python standard is a 3-way byte-identical mirror (sync all
   three copies). **Still open — your call:** does `recursive-design.md` also get **baked into the
   Crush client reference set** like the other design docs
   (`client/entrypoint/dotfiles/.config/crush/reference/`)? I lean **yes** (a Crush-developed
   project benefits identically). Yes/no?
2. **RESOLVED 2026-10-23 (William Emerison Six <billsix@gmail.com>): drop the `case _`.** The
   redesign's `case []` + `case [v, *rest]` is the exhaustive nil/cons split (no silent
   fall-through hole), so no dead default branch is added.
3. **RESOLVED 2026-10-23 (William Emerison Six <billsix@gmail.com>): include the Hestenes
   pairwise cleanup** (Part A2) — express the adjacent-blade pairing as
   `itertools.pairwise(prefix_blades(...))`, the "pairings as an iterable" form the maintainer
   asked for (the single-pass-safe `zip`). `prefix_blades` itself stays unchanged (its
   `accumulate` is a genuine scan).
