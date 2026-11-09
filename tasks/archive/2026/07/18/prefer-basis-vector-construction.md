# Build vectors from basis blades, not positional constructors

**Created:** 2026-07-18 · **Completed:** 2026-07-18

Requested by the maintainer, 2026-07-18: "I don't expect to see stuff like this, with explicit
constructors. `compose([translate(b=Vector1(b)), uniform_scale(m=m)])`. The `Vector1` could be made by
multiplying by `e_1`, correct? that's what I want". The teaching-facing portion was converted; the
library and test sites were deliberately left (see Scope).

## Verified equivalent

`Vector1(b)` and `b * Vector1.e_1` produce an identical value **of the same type**
(`Vector1(coeff_e_1=5.0)` both ways); likewise `Vector2(3.0, 4.0) == 3.0 * Vector2.e_1 + 4.0 * Vector2.e_2`.

## Why the basis form is better here

In a teaching library the two spellings say different things. `Vector2(3, 4)` says "a pair of numbers
in a box"; `3 * e_1 + 4 * e_2` says "three of this direction plus four of that one", which is what a
vector **is** in the algebra being taught, and it puts the basis blades the reader has just met to
work. It scales without a new spelling (a bivector is `5 * Bivector2.e_12`, a rotor is
`scalar + bivector`). `Vector1(b)` was the worst case: a one-element constructor inside
`translate(b=Vector1(b))`, where `b` meant two things in one line.

This is the constructive counterpart of the existing "no local aliases for values with a direct name"
rule (`Vector2.e_1`, `Bivector2.e_12`), and was recorded beside it in `CLAUDE.md`. It is a **style
preference for hand-written teaching code, not a deprecation**: the positional constructor stays
supported (it is the natural output of `from_blade_dict` and of generated code), which the record says
so that nobody deletes `__init__`.

## Scope (measured 2026-07-18)

`Vector[123](...)` sites: gacalc `src/` 56, gacalc `tests/` 25, mvp `assignments/` 39, mvp `tests/` 38,
mvp `mvpvisualization/` 33, mvp `notebooksrc/` 14, mvp `cayley/` 5, mvp `demos/` 0 (~210). Two
corrections on a closer look: gacalc `src/` was really 0 (all 56 were in the generated, never
hand-edited `g1/g2/g3.py`), and mvp `assignments/` was really one file (all 65 sites in
`assignments/demo02/vec1.py`).

**Decision (William Emerison Six <billsix@gmail.com>, 2026-07-18):** the boundary is teaching-facing
code (notebooks, assignments, demos, docstrings), the same boundary already settled for `m`/`b`. mvp
`tests/` (38), `mvpvisualization/` (33) and `cayley/` (5) were left: library and test audiences, and
`tests/` arguably should exercise the positional constructor since it is public API.

## What was done

- **`notebooksrc/plot2d.py` (14 sites)** was converted, including the line the maintainer quoted:
  `translate(b=Vector1(5))` became `translate(b=5 * Vector1.e_1)`; `Vector2(5, 6)` became
  `5 * Vector2.e_1 + 6 * Vector2.e_2`. Edge cases were verified equal and same-type at runtime: a
  **zero component is dropped** (`Vector2(2.0, 0.0)` → `2.0 * Vector2.e_1`, still a `Vector2`) and
  **negatives subtract** (`Vector2(-0.5, -0.5)` → `-0.5 * Vector2.e_1 - 0.5 * Vector2.e_2`). The
  notebook was re-run headless and its three figures rendered as before.
- **`assignments/demo02/vec1.py` was deliberately not converted** (the maintainer, 2026-07-18: "you are
  correct that it was part of a lesson, please don't do the blind update, perhaps it's unnecessary").
  It is a 1-D vector notebook whose doc-regions ("adding vectors", "subtracting vectors", "multiplying
  scalar by a vector") are excerpted into the book; the lesson there is the arithmetic, and
  `1.0 * Vector1.e_1 + 3.0 * Vector1.e_1` would put it behind a concept the student has not met.
  **The general lesson: check what the surrounding chapter teaches before converting book-excerpted
  code.**
- Whether the book's `book/docs/*.rst` prose shows the constructor form (prose and code must change
  together) was raised and left unchecked in this task.

## Verification

Both repos green (`make format`, full suite). The notebooks were executed with `MPLBACKEND=Agg`, since
they are scripts the suite does not import.
