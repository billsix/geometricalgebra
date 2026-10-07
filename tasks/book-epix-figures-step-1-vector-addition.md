# Step 1: ePiX figures for vector addition and subtraction

**Part of:** `tasks/book-epix-figures.md` · **Depends on:** nothing (first step) ·
**Next:** `tasks/book-epix-figures-step-2-projection-2d.md`
**Status:** proposed — needs go-ahead.
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

- [ ] **Refactor first:** move `ORIGIN`, colours, `polar`, `unit_circle_scene` (+ a no-disc variant),
      `vector`, `wedge`, `right_angle_marker`, `leg` into `book/figures/epix/_scene2d.py`; leave
      `BETA`/`THETA`/`R` and the rotation-specific wording in `_rotation_scene.py`, which re-exports the
      helpers so the nine rotation figures keep working unchanged. Re-render all nine; `git diff` of the
      eepic text should be empty (byte-identical — the oracle for a pure refactor).
- [ ] Add a `dashed_vector` (or `line_style`) helper for the translated copy of a vector, and a
      `parallelogram` helper (closed `Path`, light fill).
- [ ] Figures (`book/figures/epix/`): `add1.py` — `a` and `b` from the origin; `add2.py` — `b` moved
      tip-to-tail onto `a`'s head (dashed), `a + b` from the origin; `add3.py` — the parallelogram with
      both orders (commutativity); `sub1.py` — `a − b` drawn from `b`'s head to `a`'s head; `sub2.py` —
      `−b` and `a + (−b)` tip-to-tail, landing on the same point.
- [ ] `vector-addition.rst`: `.. figure:: _static/epix/<name>.*` for each, with alt text; leave
      `.. TODO prose` markers for the maintainer.
- [ ] Verify: `make docs` nested; HTML embeds the PNGs, PDF shows the vector figures; `make format`
      green (`book/figures` is ruff-checked; ty covers `tools/` only).

## Notes / decisions

## Open questions

None yet.
