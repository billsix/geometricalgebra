# Replace the borrowed composition figure with modelviewprojection's rotate + translate sequence

**Status:** proposed — needs go-ahead
**Priority:** 3
**Difficulty:** 3
**Created:** 2026-11-20 (William Emerison Six <billsix@gmail.com>)

## BLUF

For the composed-coordinate-system plots borrowed from modelviewprojection
(github.com/billsix/modelviewprojection), the book took the wrong sequence: the one modelled on
the screen-space/NDC transformation (translates and scales). The maintainer wants the rotate-and-
translate sequence instead. Research which plot is which, confirm the right one with the
maintainer, and replace it. Done means the page shows modelviewprojection's rotate + translate
sequence read both ways, and `make docs` passes.

## Context

- The maintainer's ask (2026-11-20, verbatim): *"For the plot that you took from model view
  projection, regarding composed coordinate systems, you did it for like the screen space to NDC
  transformation. That's not the one I want. I want the stuff that's like rotate and translate.
  Make a task to research that, confirm that you found the correct thing, and replace it."*
- **modelviewprojection's source (read 2026-11-20):** `src/modelviewprojection/notebooksrc/plot2d.py`
  in that repo has four `compose_intermediate_fns` sequences:
  1. "Composed functions, read bottom up": `[rotate(pi/4), translate(b=2.0 * e_1)]`, draws the
     basis, the x/y lines, an isosceles triangle and the unit circle through each step.
  2. "Composed functions, read top down": `[rotate(pi/4), translate(b=1.0 * e_1)]` with
     `relative_basis=True`.
  3. and 4. The screen sequence: `translate(-0.5 e_1 - 0.5 e_2)`, `scale_non_uniform(4, 3)`,
     `scale_non_uniform(0.5, 0.5)`, `translate(e_1 + e_2)`, drawn with `draw_screen`, with
     `relative_basis=False` and `True`.
  Sequences 1 and 2 are the "rotate and translate" ones the maintainer means (to be confirmed).
- **What gacalc's book has now:** commit `c205abe` ("book: fill relative-graph-paper, add the
  rotation-graph-paper notebook", 2026-11-19).
  - `notebooks/relative-graph-paper.py` + `book/docs/relative-graph-paper.rst`: `T_b ∘ S_m`
    (translate + uniform scale), read right to left and left to right. This is the screen/NDC-
    style sequence, the likely target of the complaint.
  - `notebooks/rotation-graph-paper.py` + `book/docs/rotation-graph-paper.rst`: `T_b ∘ R` (turn
    45°, then slide), both readings. It already resembles sequences 1 and 2, but it sits after the
    rotate chapter (decision 2 of `tasks/archive/2026/11/19/fill-placeholder-book-notebooks.md`),
    because rotation is not yet introduced at *Relative Graph Paper*.
  - Figures: `book/figures/epix/_paper_scene.py` draws the carried graph paper.
- Book order and placement: `tasks/reference/book-outline.md`.

## Plan

1. Confirm with the maintainer which page holds the unwanted figure and that sequences 1 and 2 of
   modelviewprojection's `plot2d.py` are the wanted ones (questions 1 and 2).
2. Port the wanted sequence in gacalc's style (ePiX via `_paper_scene.py`, symbolic first,
   numbers only to draw, the translate's `b` by keyword), including what modelviewprojection's
   version draws that ours does not (the isosceles triangle carried through each step, the
   standard sheet kept underneath in the bottom-up reading).
3. Remove the replaced translate + scale sequence, its figures, and the prose that describes it;
   update `relative-graph-paper.rst`'s "Two ways to read a composition".
4. `make docs`; look at both readings in HTML and PDF.

## Decisions

(William Emerison Six <billsix@gmail.com>, 2026-11-20.)

1. **Confirmed:** the unwanted figure is the translate + uniform-scale sequence on *Relative Graph
   Paper* (`notebooks/relative-graph-paper.py`). The wanted one is modelviewprojection's "Composed
   functions, read bottom up / read top down" (`rotate(pi/4)`, then `translate`). Plan step 1 is
   done.
2. **The rotate + translate sequence goes on *Relative Graph Paper*,** replacing the translate +
   scale one. *Rotation Is Turning the Graph Paper* then has to be reconciled with it, so the two
   pages do not show the same sequence twice.

3. **Move *Relative Graph Paper* after `rotate`,** and fold *Rotation Is Turning the Graph Paper*'s
   `T_b ∘ R` content into it, so one page carries the sequence. The reason: `book/docs/index.rst`
   orders the pages `relative-graph-paper`, then `rotate`, then `rotation-graph-paper`, and the
   teaching-order rule (`tasks/reference/teaching-order-and-dependencies.md`) forbids using
   rotation before `rotate`. The work this adds to the plan: reorder `index.rst`; update the
   dependency graph on the book's first page and `tasks/reference/book-outline.md`; fix every
   cross-reference to the two pages (`:doc:` links, including `relative-graph-paper.rst`'s link to
   `rotation-graph-paper`); and either retire *Rotation Is Turning the Graph Paper* (its notebook,
   page and toctree entry) or keep only what does not duplicate the moved page (e.g. the
   `y = x^2` parabola on the rotated frame). Decide that per section while merging, and record it
   here.

## Open questions

None.
