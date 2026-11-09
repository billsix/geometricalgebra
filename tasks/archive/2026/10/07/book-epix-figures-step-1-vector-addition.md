# Step 1: ePiX figures for vector addition and subtraction

**Created:** 2026-10-07 (William Emerison Six <billsix@gmail.com>) · **Completed:** 2026-10-07 (overnight autonomous run)
**Part of:** `tasks/archive/2026/10/07/book-epix-figures.md` · **Next:** `tasks/archive/2026/10/07/book-epix-figures-step-2-projection-2d.md`

Figures for `book/docs/vector-addition.rst` in the rotation sequence's style: vector **addition**
(tip-to-tail and the parallelogram) and **subtraction** (`a − b` as the vector from `b`'s head to
`a`'s head, and as `a + (−b)`), 2D only. The page and its notebook were placeholders before this step;
the outline is `tasks/reference/book-outline.md` ("Vector addition — pictures, in 2D only to start").

## What was done

- **Refactor first:** moved `ORIGIN`, colours, `polar`, `unit_circle_scene` (now with a
  `disc: bool = True` toggle), `vector`, `wedge`, `right_angle_marker`, `leg` into
  `book/figures/epix/_scene2d.py`; `_rotation_scene.py` keeps `BETA`/`THETA`/`R` and re-exports the
  helpers. All nine rotation figures were re-rendered; their eepic was **byte-identical** before vs
  after (oracle PASS).
- Added `dashed_vector` (via `epix.dashed()` + an `epix.line_style(style="-")` reset) and
  `parallelogram` (closed `Path`, light fill) to `_scene2d.py`.
- Figures (`book/figures/epix/`): `add1` (a, b from origin), `add2` (b tip-to-tail onto a's head,
  dashed; a+b), `add3` (parallelogram, commutativity), `sub1` (a−b from b's head to a's head, green),
  `sub2` (−b and a+(−b) tip-to-tail, landing on a−b). Shared vectors live in `_addition_scene.py`.
- `vector-addition.rst` got a `.. figure::` for each, with alt text; `.. TODO prose` markers were left
  for the maintainer's narrative.

## Decisions

- The addition figures use `unit_circle_scene(disc=False)` (axes, no circle — addition needs no unit
  circle). The `disc=True` default path is byte-identical to the old helper, which is why the rotation
  oracle passes.
- `check_epix_keywords.py`'s KNOWN table was extended for `dashed_vector`, `parallelogram`,
  `line_style`, and `unit_circle_scene`'s new `disc` parameter.
- A pre-existing warning, not from this step (`proof-projection.rst:60: Title underline too short`),
  was left for step 2, which owns that page and fixed it.

## Verification

Figures rendered; the Sphinx HTML build succeeded and embedded all five PNGs; the `make format` gate
was green (ruff + ty + `check_epix_keywords`). The full html+PDF build ran at the end of step 3.
