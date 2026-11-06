# One shared "must be a vector (grade 1)" check, used everywhere gacalc hand-rolls one

**Status:** in progress — questions answered and go-ahead given (William Emerison Six <billsix@gmail.com>, 2026-11-06)
**Priority:** 5
**Difficulty:** 4
**Created:** 2026-11-04 (William Emerison Six <billsix@gmail.com>): "make a task to see if for that
require_vector thing you made, for the dot product task, if there's an existing function/method in the
codebase that checks to ensure a run-time type like being a vector. I believe there is, so we would
likely want to reuse that".
**Merged 2026-11-06:** this doc absorbed `tasks/archive/2026/11/06/consolidate-vector-grade-checks.md` (created 2026-10-22,
the same job asked earlier: "there is some procedure somewhere that ensures the parameters are vectors
… find all references where they do a check like that, and call the procedure instead, if it makes
sense"). That doc's inventory, its decision, and its open questions are folded in below, and it is
archived as superseded (William Emerison Six <billsix@gmail.com>, 2026-11-06).
**Depends on:** `tasks/refactor-frame-to-invertible-function.md`. Do that first. It reshapes
`Frame.to_invertible_function` (where the nested `require_vector` lives), deletes
`measure._max_basis_index`, and adds `MultiVectorBase.implied_minimal_number_of_dimensions()`, which
raises on a non-vector and so is one more site for this task.

## BLUF

gacalc checks "this argument is a vector" in many places, with different messages, different
exception types (`ValueError` / `TypeError`), and some bare `assert`s that disappear under
`python -O`. A raising helper already exists, `measure._require_vectors`, but it is private and its
message names only area/volume/content. Done = one shared raising check in `base.py`, used by every
real-`raise` site and by the public-API `assert` sites the open questions settle on, named in
`CLAUDE.md`. Behaviour is preserved, or any change of exception type is deliberate and in
`CHANGELOG.md`. `make test` and `make format` pass.

## Context (read first)

- **The predicate:** `MultiVectorBase.is_vector() -> bool` (`base.py`) is
  `is_homogeneous_of_grade_r(1)`; "`zero` qualifies". Every check below is built on it.
- **The helper to promote:** `measure._require_vectors(vectors)`. It raises `ValueError` on an empty
  sequence or a non-vector, and its message is hardcoded to "area/volume/content". `measure.area`,
  `volume`, `content` and `signed_*` call it.
- **The sibling to copy:** `MultiVectorBase._require_scalar_plus_bivector(method_name)` (`base.py`), a
  `_require_*` guard that takes a context label so the message names the caller.
- `CLAUDE.md` › "Dot product for vectors, scalar product only where it is meant" tells new code to
  "check with `is_vector()` and raise `ValueError`". The helper this task settles on should be named
  there.
- Line numbers are deliberately not given; locate each site by function name (they shift with every
  edit, and `refactor-frame-to-invertible-function` will move several).

## Inventory (re-grep before starting; this is the 2026-10-22 + 2026-11-04 snapshot)

Discover with `rg -n 'is_vector\(\)' src/gacalc --glob '!g[0-9].py'` and `rg -n 'grade 1' src/gacalc`.
Also look for a grade-generic check (`is_homogeneous_of_grade_r` plus a raise) that would cover vectors
as one case.

### A. Real user-facing `raise` on a non-vector argument — convert

- `measure._require_vectors` — the helper itself; moves to `base.py`.
- `frame.are_linearly_independent` — an inline loop, `ValueError` ("a frame is a set of vectors
  (grade 1)"). Caveat: its **empty** case must stay `return False`, not raise, so it calls the helper
  only after its own empty guard (Open Q1).
- `frame.Frame.to_invertible_function` — the nested `require_vector`, `ValueError`.
- `MultiVectorBase.implied_minimal_number_of_dimensions` — new, added by
  `tasks/refactor-frame-to-invertible-function.md`; raises `ValueError` on a non-vector.
- `vectorcalc.cross` — loops `(a, b)`, `ValueError` ("cross takes vectors (grade 1)").
- `MultiVectorBase.bivector_from_vectors` — raises **`TypeError`**, not `ValueError`, and reports the
  grades (Open Q2). `Gn.bivector_from_vectors` delegates to it, and its docstring also says "TypeError".
- the `transforms` rotation factory that mirrors `bivector_from_vectors`
  (`if not (a.is_vector() and b.is_vector()): raise …`) — same `TypeError` question.

### B. `assert …is_vector()` on public-API parameters — judgment (Open Q3)

Dev-time asserts (`AssertionError`, gone under `python -O`), and some docstrings advertise "Raises:
AssertionError". Converting them is a behaviour change.

- `MultiVectorBase.inner_product` / `outer_product`.
- `MultiVectorBase.versor_from_vectors`.
- the `transforms` factories (`versor_rotation` and its neighbours).

### C. Leave alone

- `MultiVectorBase.reject` / `reflect` inner asserts marked `# TODO - can this be generalized?`, and the
  `transforms` mirror: they mark a known scope limit, not an input guard.
- `nbplotutils.py`'s `assert v1.is_vector() and v2.is_vector()`: a notebook plotting helper.
- The generated `g3.py` `Odd_3` → `Vector` cast check: generated code (never hand-edited) and a
  different check (a narrowing cast, not a parameter guard).

## Decisions

1. **The shared check lives in `base.py`, not `measure.py`** (William Emerison Six
   <billsix@gmail.com>, 2026-10-22). `base` is the lowest shared module: `frame`, `vectorcalc`,
   `transforms` and `measure` all import it, and it imports none of them, so there is no cycle.
2. **Name it in `CLAUDE.md`** (William Emerison Six <billsix@gmail.com>, 2026-11-04: "if there is such a
   method/function, update CLAUDE.md to call it out"), in "Conventions the agent must obey while
   writing code", and point the "Dot product for vectors" bullet at it.
3. **Form (Q1, the agent's recommendation accepted — William Emerison Six <billsix@gmail.com>,
   2026-11-06: "whatever you recommend"):** a static method
   `MultiVectorBase.require_vectors(vectors, context="", require_nonempty=True)` plus a single-value
   `MultiVectorBase.require_vector(value, context)`, both raising `ValueError` with the caller's context
   in the message. `frame.are_linearly_independent` keeps its own empty guard and calls with
   `require_nonempty=False`.
4. **Exception type (Q2): every vector check raises `ValueError`, including `bivector_from_vectors`
   and its `transforms` mirror** (William Emerison Six <billsix@gmail.com>, 2026-11-06: "I don't care
   if we break callers, only me, this project, and modelviewprojection use it - find any uses that
   cause issues, and update them"). Search gacalc and modelviewprojection for code catching
   `TypeError` from these sites (tests' `pytest.raises(TypeError…)`, `except TypeError`) and update
   them. A `CHANGELOG.md` BREAKING entry records the switch.
5. **Public-parameter asserts become real checks (Q3, the agent's recommendation accepted —
   William Emerison Six <billsix@gmail.com>, 2026-11-06):** bucket B (`inner_product`,
   `outer_product`, `versor_from_vectors`, the `transforms` factories) call the shared check, and their
   "Raises: AssertionError" docstrings become `ValueError`. Bucket C (the `# TODO` reject/reflect
   asserts, the notebook helper, generated code) is left alone.

## Plan

1. Re-grep and refresh the inventory above.
2. Add the shared check to `base.py` (form per Open Q1), with a context label so each site keeps a
   message naming the caller. `measure.py` imports it and drops its local copy.
3. Convert bucket A, preserving each site's message via the context label and the frame's empty case.
4. Bucket B per Open Q3; the `TypeError` sites per Open Q2.
5. Call the helper out in `CLAUDE.md` (Decision 2).
6. `CHANGELOG.md` `[Unreleased]` entry if a public name or an exception type changes (a consumer
   catching `TypeError` from `bivector_from_vectors` would be broken by a switch).
7. Gates: `make test` (tests that match on these messages pin the behaviour; check
   `rg -n 'match=' tests` and update any deliberately), `make format`,
   `python tools/check_annotations.py`. No `src/gacalc/g*.py` edits.

## Open questions

None — all three answered 2026-11-06 (Decisions 3–5).

## See also

- `tasks/reference/conditional-refactoring-rules.md` — Rule B (dedup before you restructure).
- `tasks/archive/2026/11/04/frame-dot-instead-of-scalar-product.md` — where the nested `require_vector`
  came from.
