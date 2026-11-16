# Live ePiX figures in the book's notebooks get the same light background as prebuilt ones

**Status:** proposed — needs go-ahead (Open questions below block implementation)
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

## Plan (draft; depends on Q1)

1. Make live figures opaque by the mechanism chosen in Q1.
2. Apply it in `scene_around`, `scene_2d` and `scene_3d`, using `#f2f2f2`, the same constant the
   prebuilt path uses, from one shared place.
3. Rerun the eight notebooks and check each figure's PNG has no transparent pixels. One way: an
   ImageMagick `identify -format %[opaque]`, or a PIL alpha-channel check. Then `make docs`, and
   look at the HTML notebook pages.
4. Documentation:
   - **`CLAUDE.md`:** one sentence that every ePiX figure, prebuilt or live, has the opaque
     `#f2f2f2` background;
   - **`book-and-docs-pipeline.md`:** the live path's mechanism;
   - **`book-outline.md`:** a line in the notebook style.

## Open questions

1. **Where the background is applied.** Either:
   - **(a)** in epix-mirror: an optional `background="#rrggbb"` on `epix.figure` /
     `figure_around` / `render`, which rasterizes or flattens onto that colour. The default stays
     transparent, so existing output doesn't change. That needs a companion epix-mirror task and
     an `EPIX_COMMIT` bump, the same workflow as `figure-fit-to-points`.
   - **(b)** here only: the scene helpers flatten the PNG after the `with` block, with ImageMagick
     or PIL, on the `_Pending` object.

   *(Recommend (a). Every live epix user gets it, the helpers stay drawing-only, and it matches
   your rule that epix-side gaps get fixed in epix-mirror. (b) works today without a pin bump.)*
2. **Colour:** `#f2f2f2` for live figures too, matching the prebuilt ones and the disc fill?
   *(Recommend yes.)*
3. **Scope:** fix the frame-QR notebooks' live figures in the same task? *(Recommend yes. They are
   the same mechanism and the same problem.)*
