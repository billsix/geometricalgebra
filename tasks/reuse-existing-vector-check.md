# Reuse an existing runtime vector check instead of `frame.py`'s new `require_vector`

**Status:** proposed — needs go-ahead
**Priority:** 5
**Difficulty:** 3
**Created:** 2026-11-04 (William Emerison Six <billsix@gmail.com>): "make a task to see if for that
require_vector thing you made, for the dot product task, if there's an existing function/method in the
codebase that checks to ensure a run-time type like being a vector. I believe there is, so we would
likely want to reuse that".

## BLUF

The dot-product task (`tasks/archive/2026/11/04/frame-dot-instead-of-scalar-product.md`) added a nested
`require_vector` inside `Frame.to_invertible_function()` (`src/gacalc/frame.py`) that raises
`ValueError` on a non-vector. gacalc already has the predicate `MultiVectorBase.is_vector()`, plus at
least one raising helper of the same shape, `measure._require_vectors`, and several hand-rolled checks
that differ in the exception they raise. Done = one shared raising check, used by `frame.py` and named in `CLAUDE.md`, with this
doc recording which other call sites moved to it and which were left alone, and why.

## Context (read first)

A first `grep` for `is_vector()` in `src/gacalc/` (generated `g*.py` excluded), 2026-11-04:

- **The predicate:** `MultiVectorBase.is_vector() -> bool` (`base.py`), "homogeneous of grade 1; `zero`
  qualifies". Every check below is built on it.
- **Raising helpers and inline checks, three different behaviours:**
  - `measure._require_vectors(vectors)` (`measure.py`): private, takes a sequence, raises
    `ValueError` on an empty sequence or a non-vector. Its message names "area/volume/content", so it
    can't be reused as it stands.
  - `frame.are_linearly_independent` (`frame.py`): an inline loop raising `ValueError` ("a frame is a
    set of vectors (grade 1)").
  - `frame.Frame.to_invertible_function` (`frame.py`): the new nested `require_vector`, raising
    `ValueError`.
  - `MultiVectorBase.bivector_from_vectors` (`base.py`): raises **`TypeError`**, not `ValueError`.
- **Bare `assert`s** (vanish under `python -O`): `base.py` (two pairs in the vector-only methods near
  the cosine/sine helpers; `versor_from_vectors`; two `# TODO - can this be generalized?` sites),
  `transforms.py` (`versor_rotation` and one TODO site), `nbplotutils.py`.
- `CLAUDE.md` › "Dot product for vectors, scalar product only where it is meant" tells new code to
  "check with `is_vector()` and raise `ValueError`". The helper this task settles on should be named
  there.

## Plan

1. **Re-grep, as the source of truth:** `rg -n 'is_vector\(\)' src/gacalc --glob '!g[0-9].py'` and
   `rg -n 'grade 1' src/gacalc`. Also look for a grade-generic check (`is_homogeneous_of_grade_r` plus a
   raise) that would cover vectors as one case. List every site in this doc.
2. **Pick the shared check.** Most likely a public or module-level helper (`require_vector(value)` /
   `require_vectors(values, context)`) in `base.py`, beside `is_vector`, raising `ValueError` with the
   caller's name in the message. That would replace `measure._require_vectors`, the
   `are_linearly_independent` loop, and `frame.py`'s nested helper. Record the name, the signature and
   where it lives, with the reason.
3. **Convert `frame.py` and `measure.py`** to it. The messages may change wording; check the tests that
   match on them (`rg -n 'match=' tests`).
4. **Decide the other sites** (the open questions): the `TypeError` in `bivector_from_vectors`, and the
   bare `assert`s.
5. **Call the check out in `CLAUDE.md`** (William Emerison Six <billsix@gmail.com>, 2026-11-04: "if
   there is such a method/function, update CLAUDE.md to call it out"). Name the shared helper (and the
   predicate `is_vector()` it wraps) in `CLAUDE.md` › "Conventions the agent must obey while writing
   code", so new code reaches for it instead of writing another check. The "Dot product for vectors"
   bullet, which says "check with `is_vector()` and raise `ValueError`", should point at it too. Add a
   `CHANGELOG.md` `[Unreleased]` entry if the exception type or a public name changes.
6. **Gates:** `make test`, `make format`, `python tools/check_annotations.py`.

## Open questions

1. **Scope:** only the `ValueError` sites (`frame.py` + `measure.py`), or also the bare `assert`s? The
   asserts would become `ValueError`s that hold under `python -O`. Recommended: also the asserts, since
   they stop guarding anything under `-O`.
2. **`bivector_from_vectors`'s `TypeError`:** switch it to `ValueError` to match the rest? That is a
   breaking change for a released method, so it would get a changelog entry. Recommended: leave it
   `TypeError` in this task and note the inconsistency, since changing a public exception type deserves
   its own decision.
