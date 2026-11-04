# Frame / QR book notebooks (2D and 3D) with live-rendered ePiX figures

**Status:** blocked
**Blocked on:** the ePiX global-state reset (github.com/billsix/epix-mirror
`tasks/reset-global-state-between-figures.md`) being implemented **and pushed** to epix-mirror's
`github` remote.
**Recheck:** `git -C <epix-mirror checkout> fetch github && git -C <epix-mirror checkout> grep -n
reset_state github/master -- python/epix/figure.py`. Cleared when `figure()` calls `reset_state()` on
`github/master`; also confirm that task is archived (done).
**Priority:** 7 (blocked)
**Difficulty:** 5
**Created:** 2026-11-04 (William Emerison Six <billsix@gmail.com>). Split out of
`tasks/archive/2026/11/04/frame-class-orthonormal-invertible-function.md` (its former Phase 3) at the maintainer's request:
"make the notebook stuff a follow up task for when the epix work is done and pushed. when it is, verify
it on the gacalc side, pull from the correct version, etc".

## BLUF

Two book notebooks, 2D and 3D, that compute a `Frame` with gacalc + sympy and draw the geometry with
ePiX **live in the notebook**: each figure cell renders inline, with no prebuilt images. Live rendering
needs ePiX to reset its global state per figure, which is the upstream fix this task waits on. Done =
gacalc's `EPIX_COMMIT` pinned to the pushed fix, the multi-figure behaviour verified in gacalc's image,
both notebooks executing in `make docs` with every figure correct, and the gates green.

## Context (read first)

- `tasks/reference/frames-qr-and-reciprocal-frames.md`: the math the figures illustrate.
- `src/gacalc/frame.py` `Frame`: holds the **orthogonal** `w_j` and coefficients
  `(w_j · v_i) / |w_j|²` (unit diagonal). `orthonormal_vectors()` gives the `u_j`.
- `tasks/reference/book-and-docs-pipeline.md` "ePiX figures": keyword arguments everywhere
  (`tools/check_epix_keywords.py`), a label's colour matches its vector, and the shared scene helpers
  `book/figures/epix/_scene2d.py` / `_scene3d.py`. The existing **prebuilt** pipeline
  (`tools/render_epix_figures.py`, one process per figure) stays for the other pages. This task does not
  use it.
- **Why live rendering needs the upstream fix (measured 2026-11-04 in gacalc's image).** Two
  `epix.figure()` blocks in one process: the second inherits the first figure's pen, line style, fill,
  label style, color palette and camera. Its eepic was byte-identical to the first figure's. Resetting
  pen/line style/fill/labels by hand made the drawing match a fresh process, but the palette (and the
  camera, untested) cannot be reset from Python today.
- gacalc pins ePiX in one place: the Dockerfile's `ARG EPIX_COMMIT` (installed by
  `entrypoint/install-epix.sh`). It was `ebf3ca6…` on 2026-11-04.

## Plan

1. **Pull the fixed ePiX.** Take the epix-mirror commit on `github/master` that contains the reset;
   check `git -C <epix-mirror> log --oneline github/master`, and pin the full SHA, not a branch. Set
   `EPIX_COMMIT` to it, then `make image` (nested: the full image, because `USE_EPIX=1` and
   `BUILD_DOCS=1` are needed).
2. **Verify on the gacalc side, before writing any notebook**, in the rebuilt image:
   - two figures in one process (the 2026-11-04 red/dashed repro, in the epix-mirror task): the second
     figure's eepic equals the same figure drawn alone in a fresh process, **including** the palette
     lines;
   - a 3D figure after a 2D one: the camera is reset;
   - `tools/render_epix_figures.py` still renders every existing book figure, and `make docs` still
     builds (the pin bump must not change other pages).
   If any check fails, stop and report. The fix belongs in epix-mirror, not in a gacalc workaround.
3. **Notebooks** `book/docs/notebooks/frame-qr-2d.py` and `frame-qr-3d.py`, plus a stub page
   `book/docs/frames-qr.rst` with a toctree entry in `index.rst`. Prose is deferred (CLAUDE.md
   three-forms rule, overridden for the `Frame` work); a `TODO prose` comment marks it, as
   `projection-rejection-3d.rst` does. Each notebook runs the symbolic computation with gacalc + sympy,
   then draws from the computed (concrete) vectors:
   - **The frame and its orthogonalization:** oblique `v_1, v_2(, v_3)`; the rejection `w_2` (`w_3`)
     with a right-angle mark; the unit `u`'s.
   - **The coefficients as shadows:** `w_j · v_i / |w_j|²` (and `u_j · v_i`) as projection lengths,
     with the zeros above the diagonal visible.
   - **Volume:** the parallelogram (2D) or parallelepiped (3D) as base × height(s), with
     `|w_1| * |w_2| (* |w_3|) = |v_1 ∧ … ∧ v_n|`.
   - **The forward map:** the unit square (cube) → the frame's parallelogram (parallelepiped),
     `e_i ↦ v_i`.
   - **f = Q ∘ R:** the square → R (shear + scale, keeping `e_1`'s line) → Q (rotate onto the u's).
   - **The inverse:** a vector `y`, its shadows on the w's, and the back-substitution steps recovering
     `x_n`, then `x_{n-1}`, and so on.
   - **The reciprocal frame:** `vⁿ = w_n / |w_n|²` against the frame; the full set once
     `tasks/reciprocal-frame-hestenes.md` is done.
   Notebook helpers that both notebooks share go in `book/figures/epix/_frame_scene.py` (reusing
   `_scene2d` / `_scene3d`). The notebooks add that directory to `sys.path`, and `ty` needs it in
   `pyproject.toml [tool.ty.environment] extra-paths`.
4. **Gates:** `make format` (ruff, `ty check book/docs/notebooks`, `check_epix_keywords.py`),
   `python tools/check_annotations.py` (every binding typed), and `make docs`
   (`nb_execution_raise_on_error = True`, so a failing cell fails the build). Look at every rendered
   figure in the HTML output.
5. Update `tasks/reference/book-and-docs-pipeline.md` with the live-rendered notebook path (alongside
   the prebuilt one) and the `EPIX_COMMIT` bump. Write a `CHANGELOG.md` entry only if the book is
   changelogged.

## Open questions

None yet. Re-raise if step 2 finds something.
