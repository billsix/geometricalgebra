# Replace the borrowed composition figure with modelviewprojection's rotate + translate sequence

**Created:** 2026-11-20 (William Emerison Six <billsix@gmail.com>) · **Completed:** 2026-11-20

The maintainer's ask (2026-11-20, verbatim): *"For the plot that you took from model view
projection, regarding composed coordinate systems, you did it for like the screen space to NDC
transformation. That's not the one I want. I want the stuff that's like rotate and translate."*
*Relative Graph Paper* (from `c205abe`) composed a translate with a uniform scale, the shape of
modelviewprojection's screen/NDC sequence. It now composes a rotation with a translate, the
sequence modelviewprojection uses to place a paddle.

## What the source showed

modelviewprojection's `src/modelviewprojection/notebooksrc/plot2d.py`
(github.com/billsix/modelviewprojection) has four `compose_intermediate_fns` sequences: "Composed
functions, read bottom up" (`[rotate(pi/4), translate(b=2.0 * e_1)]`), "read top down" (the same
with `relative_basis=True`), and two screen sequences (`translate`, `scale_non_uniform(4, 3)`,
`scale_non_uniform(0.5, 0.5)`, `translate`, drawn with `draw_screen`). The first two are the wanted
ones.

## Decisions

(William Emerison Six <billsix@gmail.com>, 2026-11-20.)

1. Confirmed: the unwanted figure was the translate + uniform-scale sequence on *Relative Graph
   Paper*; the wanted one is the rotate-then-translate sequence above.
2. The rotate + translate sequence goes on *Relative Graph Paper*, replacing the translate + scale
   one, and *Rotation Is Turning the Graph Paper* is reconciled with it, so the sequence is not shown
   twice.
3. *Relative Graph Paper* moves after rotation. The teaching-order rule
   (`tasks/reference/teaching-order-and-dependencies.md`) forbids a rotation before `rotate`.

## Judgment calls made while doing it

- **The page sits after `rotation-graph-paper`**, not right after `rotate`: decision 3 asked for
  "after `rotate`", and putting it after the turned-graph-paper picture keeps that picture first.
  The order is now `vectors-as-number-lines`, `vector-addition`, `rotate`, `geometric-product`,
  `rotation-graph-paper`, `relative-graph-paper`, `projection`.
- **"How we write coordinates" moved to `vectors-as-number-lines.rst`.** That section introduces
  the `a_1 * e₁ + a_2 * e₂` notation that `vector-addition` and `rotate` use. Moving it with the
  page would have broken the teaching order. It stayed where it was taught, on the page just
  before, which already ends by saying two number lines make graph paper.
- **`translate` is cited from `vector-addition`,** which defines it.
- **`rotation-graph-paper` lost its "Turning, then sliding" section and its companion notebook.**
  `notebooks/rotation-graph-paper.py` was the rotate + translate sequence (`T_b ∘ R`, with
  `standardposition.rotation_from_to(e₁, e₁ + e₂)`, a 45° turn); its cells became the new
  `notebooks/relative-graph-paper.py`, which `git rm`'d the old file. The page keeps the
  `graphpaper1`–`graphpaper5` pictures and ends with a pointer to the next page.

## What changed

`book/docs/index.rst` (order), `book/docs/relative-graph-paper.rst` (rewritten for `T_b ∘ R`),
`book/docs/rotation-graph-paper.rst`, `book/docs/vectors-as-number-lines.rst`,
`notebooks/relative-graph-paper.py` (rewritten: coordinates relative to a sheet, then `R` and
`T_b`, both readings drawn with `paper_scene`/`carried_paper`, the two end-function checks and the
inverse round trip with `show_difference`, and the swapped order `R ∘ T_b`), `notebooks/README.md`,
`src/gacalc/epixscene/paper_scene.py` (docstring), `tasks/reference/book-outline.md`,
`tasks/reference/teaching-order-and-dependencies.md`, `tasks/reference/book-and-docs-pipeline.md`.

## Verification

The new notebook executed in the image (`jupytext --execute`), with clean ruff, ruff format and
ty. Its checks show the numbered cancellation of `b₁ + (√2/2) * x − (√2/2) * y` (and the `e₂` line)
and `x − x`, `y − y` for the inverse. The figures show the slid sheet, then the turn about its own
origin. The full book build (`entrypoint/docs.sh` in the image) exited 0: the page is §2.12, after
*Rotation Is Turning the Graph Paper*, and the only new warning came from a stale, gitignored
`book/docs/notebooks/rotation-graph-paper.ipynb` that `docs.sh` had converted earlier and does not
delete (removed by hand). The PDF text showed `vectors-as-number-lines.py` still calling it "the
next chapter"; that sentence now points forward to it.
