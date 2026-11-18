# Live ePiX figures in the book's notebooks get the same light background as prebuilt ones

**Completed:** 2026-11-18 (William Emerison Six <billsix@gmail.com>)
**Priority:** 4
**Difficulty:** 3
**Created:** 2026-11-16 (William Emerison Six <billsix@gmail.com>)
**Related:** github.com/billsix/epix-mirror `tasks/archive/2026/11/18/figure-background.md` (the ePiX
half); `tasks/archive/2026/11/16/bootstrap-notebooks-show-derivations.md` (made the Part III live
figures)

## Outcome

Every ePiX figure the book's notebooks draw live now has the opaque `#f2f2f2` background that the
prebuilt figures already had, so none shows as a transparent sheet on a dark-mode page.

- **epix-mirror** gained `epix.figure(…, background="#rrggbb")`, which flattens the PNG with
  ImageMagick, and the same option on `figure_around` / `render` / `Figure`. The default stays
  transparent. It was merged and pushed as `797b944`.
- **`Dockerfile`:** `EPIX_COMMIT` was bumped to `797b9442…`.
- **Scene helpers:** `scene_2d` / `scene_3d` (`book/figures/epix/_frame_scene.py`) and
  `scene_around` (`_bootstrap_live.py`) pass `background=BACKGROUND`. The constant is imported from
  `_scene2d.py`, whose `BACKGROUND` is the disc fill and the colour of the render tool's
  `DEFAULT_BACKGROUND`, so the literal is not repeated. Its comment now covers both paths.
- **Docs:**
  - `CLAUDE.md` ("ePiX in the image"): every ePiX figure, prebuilt or live, has the opaque
    background.
  - `tasks/reference/book-and-docs-pipeline.md`: the live path's mechanism and the pin.
  - `tasks/reference/book-outline.md`: the notebook-style line.

## Decisions (William Emerison Six <billsix@gmail.com>)

1. The option lives in epix-mirror, defaulting to transparent (2026-11-16).
2. `#f2f2f2`, one shared constant (2026-11-16).
3. The frame-QR notebooks are included (2026-11-16).
4. The mechanism is to flatten with ImageMagick (2026-11-18).

## Verification

- `make image` rebuilt from the ePiX layer.
- `tasks/adhoc/live-epix-figure-background/check_opaque.py` (one-shot, deleted at archive) executed
  the eight notebooks in the container with jupytext + nbconvert. All 33 figure PNGs are opaque with
  an `F2F2F2` corner:

  | Notebook | Figures |
  | --- | --- |
  | `bootstrap-product` | 2 |
  | `bootstrap-projection` | 4 |
  | `bootstrap-projection-from-product` | 1 |
  | `bootstrap-rotation` | 2 |
  | `bootstrap-rotation-from-product` | 2 |
  | `bootstrap-rotation-from-projection` | 2 |
  | `frame-qr-2d` | 11 |
  | `frame-qr-3d` | 9 |

  One `frame-qr-2d` figure was viewed.
- ruff and `tools/check_epix_keywords.py` were clean on the helpers.
- `make docs` passed (HTML + PDF).
  - Every PNG the HTML pages reference is opaque: 111 images, 63 of them notebook outputs.
  - `output/gacalc/html/_images/` also holds 219 transparent PNGs that no page references. They are
    left over from earlier builds, because the output directory is not cleaned.
  - The build's warnings predate this change: four short title underlines, a duplicate
    `InvertibleFunction` cross-reference target, and the kernel's TCP notices.
