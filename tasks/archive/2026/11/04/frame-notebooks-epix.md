# Frame / QR book notebooks (2D and 3D) with live-rendered ePiX figures — done-record

**Completed:** 2026-11-04. Requested by William Emerison Six <billsix@gmail.com>, split out of
`tasks/archive/2026/11/04/frame-class-orthonormal-invertible-function.md` (its former Phase 3): "make the
notebook stuff a follow up task for when the epix work is done and pushed. when it is, verify it on the
gacalc side, pull from the correct version, etc". The per-step peel figures were added at the
maintainer's request ("graphically show what's happening at each step"). Implemented by the agent.

## What was built

- **The ePiX pin.** The Dockerfile's `EPIX_COMMIT` moved from `ebf3ca6…` to
  `275adefe5ced0abdba30a5efd443955c8370fb48`, the epix-mirror merge that added the per-figure reset
  (github.com/billsix/epix-mirror `tasks/archive/2026/11/04/reset-global-state-between-figures.md`). It
  was confirmed as `master` on epix-mirror's `github` remote (`git ls-remote`), and the image build
  logged `epix-mirror at 275adef…`.
- **Two notebooks**, `book/docs/notebooks/frame-qr-2d.py` (11 figures) and `frame-qr-3d.py` (9 figures),
  under a new page `book/docs/frames-qr.rst` (toctree entry after `projection-rejection-3d` in
  `index.rst`; prose deferred behind a `TODO prose` comment, as on `projection-rejection-3d.rst`). Each
  section computes with gacalc's `Frame` and then draws in its own cell, live, from the numbers just
  computed:
  - 2D: the frame and its orthogonal and unit sets; the coefficient table as a shadow (`4/5 * w_1`);
    area as `|w_1| * |w_2|`; the forward map (unit square → parallelogram); `R` (shear and scale) and
    then `Q ∘ R`; the peel in four figures (setup, read `x_2`, remove `x_2 * v_2`, read `x_1`); the
    symbolic round trip; the last reciprocal vector.
  - 3D: the frame and orthogonal set; volume as base times height; the forward map (unit cube →
    parallelepiped); the peel (setup, read `x_3`, slide into the plane, the 2D peel inside the plane,
    the result); the symbolic round trip; the last reciprocal vector.
- **`book/figures/epix/_frame_scene.py`**, the drawing helpers both notebooks share (`scene_2d`,
  `scene_3d`, `point`, `arrow`, `dashed_arrow`, `note`, `patch`, `box_edges`, `right_angle`, the role
  colours). Documented in `tasks/reference/book-and-docs-pipeline.md` ("ePiX figures").
- **Config:** `pyproject.toml` adds `book/figures/epix` to ty's `extra-paths` and exempts
  `book/docs/notebooks/frame-qr-*.py` from E402 (each notebook puts that directory on `sys.path` before
  importing `_frame_scene`), both with the reason at the site.
- **Docs:** `book-and-docs-pipeline.md` describes the live-rendered path beside the prebuilt one, drops
  the stale "libepix keeps global drawing state with no reset" claim, and adds the black-tint fill
  gotcha. `CLAUDE.md`'s ePiX bullet names the live path and the pin it needs.

## Decisions

1. **A second frame for the QR figures.** The reference doc's worked frame (`v_1 = 2 * e_1`,
   `v_2 = 1 * e_1 + 3 * e_2`) has `u_i = e_i`, so its `Q` is the identity and a `Q ∘ R` figure would show
   nothing. The orthogonalization, coefficient, area, forward-map and QR figures use the oblique frame
   `v_1 = 2 * e_1 + 1 * e_2`, `v_2 = 1 * e_1 + 2 * e_2`. The peel figures keep the worked frame, so they
   match `tasks/reference/frames-qr-and-reciprocal-frames.md` number for number.
2. **No `Q ∘ R` figure in 3D.** The plan described it only for the square; the 3D frame
   (`v_1 = 2 * e_1`, `v_2 = 1 * e_1 + 2 * e_2`, `v_3 = 1 * e_1 + 1 * e_2 + 2 * e_3`, `y = v_1 + v_2 + v_3`)
   has orthogonal set `2 * e_i`, chosen so the plane of `v_1, v_2` is the `e_1 e_2` plane and each peel
   step reads plainly.
3. **Unlabelled axes.** In these figures `x` and `y` name vectors (the coordinates and the target), so
   axis labels would put two different `y`s on one figure. The axes are drawn light and unlabelled, and
   each notebook's intro says so.
4. **Camera `(5, -10, 7)`**, not `_scene3d`'s `(9, -6, 5)`. From the old camera the x and y axes projected
   almost parallel and the plane of `v_1, v_2` read as a sliver. The choice and the bounding box came
   from ePiX's perspective formula (`src/lens.cc`, `Perspective::operator()`) applied to the figures'
   points, not from trial renders.
5. **The notebooks don't `import epix`.** ty cannot resolve the editable-installed package, so
   `_frame_scene` re-exports `LabelPos` and holds every colour, including the cube-edge gray.
6. **No license header** on the new notebooks and helper, matching every other `book/docs/notebooks/`
   file and the CC0 `book/figures/epix/` helpers.
7. **No `CHANGELOG.md` entry:** the changelog covers the library, and book pages aren't changelogged.

## Verification (2026-11-04, the rebuilt image `b294e77bfbc7`)

- **Reset, checked on the gacalc side before any notebook** (a one-shot script, `tasks/adhoc/frame-notebooks-epix/verify_epix_reset.py`, removed at archive):
  a plain figure drawn after a red, dashed one that also moved the camera, and a 3D figure drawn after
  the same, each equal the same figure drawn in a fresh process. Both PASS.
- `tools/render_epix_figures.py`: every existing book figure rendered, none failed.
- Both notebooks executed under Jupyter (`jupyter nbconvert --execute`): 11 and 9 inline PNGs, and every
  printed check `True`, including `R` upper-triangular, `Q` a rotation, and both symbolic round trips.
- Every figure was inspected as PNG (a one-shot dump script, removed at archive), and the
  overlaps and clipping found were fixed.
- `make format` (ruff, ty over `src`/`tests`/`tools`/`book/docs/notebooks`, the changelog guard,
  `check_epix_keywords`): exit 0. `tools/check_annotations.py`: nothing in the new files.
- `make docs`: exit 0, no warning naming the new pages. The HTML pages carry 11 and 9 images; the PDF has
  them as chapter 23, and a rendered PDF page showed the figures intact.
- `make test` (its own `podman run` line): **717 passed** in 283 s.

## Follow-ups

- **Optional:** some code lines near 88 columns wrap in the PDF listings (e.g.
  `with scene_2d(lower_left=PEEL_LOWER_LEFT, upper_right=PEEL_UPPER_RIGHT) as fig_step_1:`). The
  pipeline doc's advice is to shorten the cell; it is cosmetic and was left.
- The full reciprocal frame figure waits on `tasks/reciprocal-frame-hestenes.md` (on hold); only the
  last reciprocal vector is drawn.
