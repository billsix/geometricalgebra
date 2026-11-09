# Umbrella: ePiX figures for the book's vector-addition, projection and 3D-projection sections

**Created:** 2026-10-07 (William Emerison Six <billsix@gmail.com>: "make a umbrella task for the following …") · **Completed:** 2026-10-07 (overnight autonomous run)

Extended what the rotation sequence established — book figures authored in **Python with the `epix`
package** (`book/figures/epix/*.py`, a shared scene helper, rendered by `make docs` to PDF for LaTeX and a
dark-mode-safe PNG for HTML) — to three more sections of "Geometry 2": **vector addition and
subtraction**, **projection and rejection in 2D** (the result *and* the precalculus derivation), and
**projection and rejection in 3D** onto the three coordinate planes. The pattern copied was
`book/figures/epix/rotate_goal.py`, `rotate1.py`–`rotate8.py` and `_rotation_scene.py`, rendered by
`tools/render_epix_figures.py` and described in `tasks/reference/book-and-docs-pipeline.md` ("ePiX
figures"); the image integration and rotation port are recorded in
`tasks/archive/2026/10/07/epix-plot-integration.md`. Outline: `tasks/reference/book-outline.md`.

## Steps

1. `tasks/archive/2026/10/07/book-epix-figures-step-1-vector-addition.md` — addition + subtraction
   figures (2D); promoted the generic 2D helpers out of `_rotation_scene.py` into a shared `_scene2d.py`.
2. `tasks/archive/2026/10/07/book-epix-figures-step-2-projection-2d.md` — projection + rejection: the
   result, then the rotate-to-standard-position derivation (filled `proof-projection.rst`'s TODO figures).
3. `tasks/archive/2026/10/07/book-epix-figures-step-3-projection-3d.md` — projection + rejection in 3D
   onto the `e_12`, `e_23`, `e_31` planes; the first 3D figures, a new `_scene3d.py`.

All three were done 2026-10-07; the full html+PDF build was clean and the gate green.

## Cross-step conventions

- Same as the rotation sequence: one `.py` per figure, percent-format, module-level `fig`,
  `BACKGROUND = "#f2f2f2"` for the HTML PNG, LaTeX labels matching the prose (`\vec{a}`, `\vec{b}`),
  colours: black vectors, purple angles, blue/green for the two legs/components.
- Figures illustrate; the prose on each page is the maintainer's to write (the steps added figures,
  minimal captions/alt text, and `.. TODO prose` markers).

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-10-07)

- Projection figures reuse the rotation sequence's `a` (length 1.25 at 66°), with `b` at 20°, length 1.
- The third plane is labelled `e_31` (cyclic) in the figures, with a one-line page note that gacalc
  spells the blade `e_13 = -e_31`.
- 3D: one figure per plane showing projection *and* rejection, plus an overview with all three planes.
- `proof-projection.rst` got the **2D** derivation figures in step 2; the 3D "one plane at a time"
  pictures wait for the maintainer's 2D-then-3D restructuring of that page.
- Every argument by keyword, every binding typed; `tools/check_epix_keywords.py` is a `make format`
  gate step, and every new helper or epix call goes in its table.
