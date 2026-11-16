# Live ePiX figures in the book's notebooks get the same light background as prebuilt ones

**Status:** proposed — needs go-ahead (all questions answered); depends on epix-mirror
`tasks/figure-background.md` being merged and pushed
**Priority:** 4
**Difficulty:** 3
**Created:** 2026-11-16 (William Emerison Six <billsix@gmail.com>)
**Related:** `tasks/archive/2026/11/16/bootstrap-notebooks-show-derivations.md` (made the Part III
live figures); github.com/billsix/epix-mirror `tasks/archive/2026/11/16/figure-fit-to-points.md`

## BLUF

The maintainer (2026-11-16): the figures the Part III notebooks draw live should have a
non-transparent background, like the prebuilt ePiX figures do. Done means:
- every live ePiX figure in the book's notebooks has an opaque `#f2f2f2` background in the
  notebook and in the built HTML: the six `bootstrap-*.py` notebooks, and `frame-qr-2d.py` /
  `frame-qr-3d.py`, which have the same problem;
- the rule is written into `CLAUDE.md` and the reference docs;
- the gates pass.

## Context

- **Prebuilt figures** (`book/figures/epix/*.py`, rendered by `tools/render_epix_figures.py` at
  `make docs`): ghostscript's `pngalpha` device leaves the PNG transparent, so the tool flattens
  every PNG with ImageMagick onto `DEFAULT_BACKGROUND = "#f2f2f2"`. A figure can override that with
  a module-level `BACKGROUND`. The tool's comment says why: a transparent figure reads badly on a
  dark-mode HTML page. `#f2f2f2` matches the disc fill `epix.white(0.95)`
  (`book/figures/epix/_scene2d.py` `BACKGROUND`).
- **Live figures** (drawn in a notebook cell inside `epix.figure()`; helpers
  `book/figures/epix/_bootstrap_live.py` `scene_around` and `_frame_scene.py`
  `scene_2d`/`scene_3d`) never go through that tool. The cell's output is the `_Pending` object
  that `epix.figure()` yields. Jupyter displays it through `_repr_png_`, and myst-nb puts that PNG
  in the HTML and the PDF. epix-mirror's `python/epix/render.py` rasterizes with
  `gs -sDEVICE=pngalpha`, so the PNG is transparent, and nothing flattens it.
- **Where the rules are written today:** `CLAUDE.md` ("ePiX in the image": the live-figure
  sentence); `tasks/reference/book-and-docs-pipeline.md` ("ePiX figures", the prebuilt vs live
  paths); `tasks/reference/book-outline.md` ("Structural conventions", the notebook style).

## Plan

1. After epix-mirror `tasks/figure-background.md` is merged and pushed: bump `EPIX_COMMIT` and run
   `make image`.
2. Pass `background=` in `scene_around`, `scene_2d` and `scene_3d`, using `#f2f2f2`, the same
   constant the prebuilt path uses, from one shared place.
3. Rerun the eight notebooks and check each figure's PNG has no transparent pixels. One way: an
   ImageMagick `identify -format %[opaque]`, or a PIL alpha-channel check. Then `make docs`, and
   look at the HTML notebook pages.
4. Documentation:
   - **`CLAUDE.md`:** one sentence that every ePiX figure, prebuilt or live, has the opaque
     `#f2f2f2` background;
   - **`book-and-docs-pipeline.md`:** the live path's mechanism;
   - **`book-outline.md`:** a line in the notebook style.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-16)

1. **In epix-mirror.** `epix.figure` / `figure_around` / `render` gain an optional
   `background="#rrggbb"`. The default stays transparent, so existing output doesn't change. The
   epix-mirror half is github.com/billsix/epix-mirror `tasks/figure-background.md`; this task is
   the geometricalgebra half: bump `EPIX_COMMIT`, then pass the background from the scene helpers.
2. **`#f2f2f2`**, the prebuilt figures' `DEFAULT_BACKGROUND` and the disc fill. Use one shared
   constant: the helpers import it instead of repeating the literal.
3. **The frame-QR notebooks too.** `_frame_scene.py` `scene_2d` / `scene_3d` get the same
   background as `_bootstrap_live.py` `scene_around`.

## Open questions

None. The task is ready to start on your go-ahead. It depends on the epix-mirror half being merged
and pushed, because `EPIX_COMMIT` is fetched from GitHub.
