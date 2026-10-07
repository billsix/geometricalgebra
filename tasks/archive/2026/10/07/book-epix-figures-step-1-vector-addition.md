# Step 1: ePiX figures for vector addition and subtraction

**Part of:** `tasks/archive/2026/10/07/book-epix-figures.md` · **Depends on:** nothing (first step) ·
**Next:** `tasks/archive/2026/10/07/book-epix-figures-step-2-projection-2d.md`
**Status:** DONE 2026-10-07 (overnight autonomous run) — figures render, page wired, gate green.
**Priority:** 4
**Difficulty:** 3
**Created:** 2026-10-07 (William Emerison Six <billsix@gmail.com>)

## BLUF

Figures for `book/docs/vector-addition.rst` in the rotation sequence's style: vector **addition**
(tip-to-tail and the parallelogram) and **subtraction** (`a − b` as the vector from `b`'s head to
`a`'s head, and as `a + (−b)`), 2D only, on the same gray-disc-and-axes scene. Along the way the
generic 2D helpers move out of `_rotation_scene.py` into a shared `_scene2d.py` so this and the later
steps don't copy them. Done = the figures render via `make docs`, the page references them, both
outputs checked.

## Context

- Pattern: `book/figures/epix/rotate*.py` + `_rotation_scene.py`; pipeline doc:
  `tasks/reference/book-and-docs-pipeline.md` ("ePiX figures"). The page is a placeholder today
  (`vector-addition.rst`: "Vector addition, in pictures, in 2D"; notebook `notebooks/vector-addition.py`
  is `1 + 1`). Outline: `tasks/reference/book-outline.md` ("Vector addition — pictures, in 2D only to
  start").
- The disc is "only for scale" in the rotation figures; here it may be dropped (addition doesn't need a
  unit circle) — keep the axes. `unit_circle_scene` should grow a `disc: bool = True` parameter, or the
  shared module offers `axes_scene` and `unit_circle_scene` both.

## Plan

- [x] **Refactor first:** moved `ORIGIN`, colours, `polar`, `unit_circle_scene` (now with a
      `disc: bool = True` toggle), `vector`, `wedge`, `right_angle_marker`, `leg` into
      `book/figures/epix/_scene2d.py`; `_rotation_scene.py` keeps `BETA`/`THETA`/`R` and re-exports the
      helpers. Re-rendered all nine rotation figures; eepic **byte-identical** before vs after (oracle
      PASS).
- [x] Added `dashed_vector` (via `epix.dashed()` + `epix.line_style(style="-")` reset) and
      `parallelogram` (closed `Path`, light fill) to `_scene2d.py`.
- [x] Figures (`book/figures/epix/`): `add1` (a, b from origin), `add2` (b tip-to-tail onto a's head,
      dashed; a+b), `add3` (parallelogram, commutativity), `sub1` (a−b from b's head to a's head, green),
      `sub2` (−b and a+(−b) tip-to-tail, landing on a−b). Shared vectors in `_addition_scene.py`.
- [x] `vector-addition.rst`: `.. figure::` for each with alt text; `.. TODO prose` markers left for the
      maintainer's narrative.
- [x] Verified: figures render; Sphinx HTML build succeeds and embeds all five PNGs; `make format` gate
      green (ruff + ty + `check_epix_keywords`). Full html+PDF build runs at the end of step 3.

## Notes / decisions

- `unit_circle_scene(disc=False)` is used by the addition figures (axes, no circle). The `disc=True`
  default path is byte-identical to the old helper, which is why the rotation oracle passes.
- `check_epix_keywords.py` KNOWN table extended for `dashed_vector`, `parallelogram`, `line_style`, and
  `unit_circle_scene`'s new `disc` parameter.
- Pre-existing warning noticed, NOT from this step: `proof-projection.rst:60: Title underline too short`
  — that is step 2's page; fixed there.

## Open questions

None.
