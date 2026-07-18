# Build vectors from basis blades, not positional constructors

**Status:** teaching-facing portion **DONE** (2026-07-18). Remaining sites
(mvp `tests/` 38, `mvpvisualization/` 33, `cayley/` 5) are deliberately left:
library and test audiences, and `tests/` arguably *should* exercise the
positional constructor since it is public API (Bill, 2026-07-18).
**Created:** 2026-07-18
**Requested by:** Bill, 2026-07-18 — "I don't expect to see stuff like this, with
explicit constructors. `compose([translate(b=Vector1(b)), uniform_scale(m=m)])`. The
`Vector1` could be made by multiplying by `e_1`, correct? that's what I want"

## Yes — verified

`Vector1(b)` and `b * Vector1.e_1` produce an identical value **of the same type**:

```
Vector1(b)      = Vector1(coeff_e_1=5.0)
b * Vector1.e_1 = Vector1(coeff_e_1=5.0)
equal: True | same type: True
```

Same in higher dimensions:

```
Vector2(3.0, 4.0)                  == 3.0 * Vector2.e_1 + 4.0 * Vector2.e_2   # True
```

## Why the basis form is better here

This is a **geometric-algebra teaching library**, and the two spellings say different
things to a reader:

- `Vector2(3, 4)` says "a pair of numbers in a box" — the coordinate tuple is primary and
  the basis is invisible.
- `3 * e_1 + 4 * e_2` says "three of *this* direction plus four of *that* one" — which is
  what a vector **is** in the algebra being taught, and it makes the basis blades the
  reader has just met do visible work.

It also scales to the rest of the algebra without a new spelling: a bivector is
`5 * Bivector2.e_12`, a rotor is `scalar + bivector`. There is no `Bivector2(5)`-shaped
habit to unlearn later.

`Vector1(b)` is the worst case of the positional form: a one-element constructor whose
argument order carries no information at all, sitting inside `translate(b=Vector1(b))`
where `b` now means two different things in one line.

## Scope (measured 2026-07-18)

| repo / area | `Vector[123](...)` sites |
|---|---|
| gacalc `src/` | 56 |
| gacalc `tests/` | 25 |
| mvp `assignments/` | **39** |
| mvp `tests/` | 38 |
| mvp `mvpvisualization/` | 33 |
| mvp `notebooksrc/` | **14** |
| mvp `cayley/` | 5 |
| mvp `demos/` | 0 |

~210 sites. Two corrections to that table once it was looked at properly:

- **gacalc `src/` is really 0.** The 56 were all in the *generated* `g1/g2/g3.py`, which
  must never be hand-edited (fix the generator, not the output).
- **mvp `assignments/` is really one file** — all 65 are in `assignments/demo02/vec1.py`.

## DONE: `notebooksrc/plot2d.py` (14 sites, 2026-07-18)

Converted, including the line Bill quoted. `translate(b=Vector1(5))` is now
`translate(b=5 * Vector1.e_1)`; `Vector2(5, 6)` is `5 * Vector2.e_1 + 6 * Vector2.e_2`.
Edge cases verified equal-and-same-type at runtime: a **zero component is dropped**
(`Vector2(2.0, 0.0)` -> `2.0 * Vector2.e_1`, still a `Vector2`) and **negatives subtract**
(`Vector2(-0.5, -0.5)` -> `-0.5 * Vector2.e_1 - 0.5 * Vector2.e_2`). Notebook re-run
headless, three figures render as before.

## OUT OF SCOPE: `assignments/demo02/vec1.py` (Bill, 2026-07-18)

**Do not convert this file.** Its 65 sites are the whole of the remaining count, and
Bill's ruling was explicit: *"you are correct that it was part of a lesson, please don't
do the blind update, perhaps it's unnecessary."*

The file is a 1-D vector notebook whose doc-regions are excerpted into the book with
titles like "adding vectors" / "subtracting vectors" / "multiplying scalar by a vector":

```python
# doc-region-begin adding vectors
Vector1(1.0) + Vector1(3.0)
# doc-region-end adding vectors
```

The lesson there is the **arithmetic**, not the basis. Rewriting it as
`1.0 * Vector1.e_1 + 3.0 * Vector1.e_1` puts the thing being taught behind a second
concept the student has not met yet. **The general rule stands, but a chapter that is
teaching the constructor is exactly where it does not apply** — and that is worth
remembering as the pattern generalizes: check what the surrounding chapter is teaching
before converting book-excerpted code.

## Open questions

- **How far does this go?** Library internals and tests are a different audience.
  Constructing 38 test fixtures as `3*e_1 + 4*e_2` is more typing for no pedagogical
  gain, and `tests/` arguably *should* exercise the constructor since it is public API.
  Suggested scope: **notebooks, assignments, demos, and docstrings** — the same
  teaching-facing boundary already settled for `m`/`b`.
- **Is the positional constructor still supported?** Nothing here proposes removing it;
  it is the natural output of `from_blade_dict` and of generated code. This is a
  *style* preference for hand-written teaching code, not a deprecation. Say so
  explicitly in whichever `CLAUDE.md` records it, or someone will try to delete
  `__init__`.
- **Does the book's prose show the constructor form?** Check `book/docs/*.rst` — if a
  chapter's text says "make a vector with `Vector2(3, 4)`", the prose and the code must
  change together.

## Interaction with the coding standard

Both repos already carry a rule that basis blades have canonical names and should be
referenced directly (gacalc's "no local aliases for values that have a direct name" —
`Vector2.e_1`, `Bivector2.e_12`). **This task is the constructive counterpart of that
rule**, and belongs beside it in `CLAUDE.md`: don't alias a basis blade, *and* build
values out of basis blades rather than positional coordinates.

## Gates

Both repos green (`make format`, full suite). For the teaching-facing areas the suite is
not enough — execute the notebooks (`MPLBACKEND=Agg`) and the assignments (Xvfb), since
they are scripts rather than imported modules.
