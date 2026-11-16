# epix-mirror: a figure that fits its points, then use it in the live notebooks

**Status:** proposed — needs go-ahead; the epix-mirror half needs that repo mounted
**Priority:** 6
**Difficulty:** 3
**Created:** 2026-11-16 (William Emerison Six <billsix@gmail.com>)
**Related:** `tasks/bootstrap-notebooks-show-derivations.md` (where the gap showed up)

## BLUF

`epix.figure()` (github.com/billsix/epix-mirror, `python/epix/figure.py`) takes fixed bounds and a
fixed size: `figure(lower_left, upper_right, size, dpi=150)`. A notebook that draws live from
vectors a reader can change needs a figure that fits whatever points it is given. Done means:
- epix-mirror's Python layer has such a function;
- geometricalgebra's `Dockerfile` pins an `EPIX_COMMIT` that includes it;
- the local workaround `scene_around` in `book/figures/epix/_bootstrap_live.py` is replaced by the
  new function;
- the frame-QR notebooks' hand-tuned bounds are considered for the same change.

## Context

- **The workaround in geometricalgebra:** `book/figures/epix/_bootstrap_live.py` `scene_around`
  (added 2026-11-16 for the Part III notebooks). It works as follows:
  - it takes the points a figure must show, plus the origin;
  - it adds a margin of 18% of the larger extent;
  - it computes `lower_left` / `upper_right`;
  - it sets `size` to a fixed width of 3.4 in, with the height chosen to keep the two scales
    equal;
  - it then calls `epix.figure(...)` and draws light axes.
  The fitting logic isn't specific to the book, and every live-drawing notebook needs it.
- **The other caller:** `book/figures/epix/_frame_scene.py` `scene_2d` / `scene_3d`. These take
  explicit bounds, and `book/docs/notebooks/frame-qr-2d.py` / `frame-qr-3d.py` hand-pick them per
  figure. They would also stop fitting if a reader changed the frame.
- **Where epix-mirror is pinned:** the `EPIX_COMMIT` build arg in geometricalgebra's
  `Dockerfile`, installed by `entrypoint/install-epix.sh` (`CLAUDE.md`, "ePiX in the image"). Bumping
  it needs `make image`.

## Plan (draft)

1. **epix-mirror:** add a fitting figure to `python/epix/figure.py`, for example
   `figure_around(points, width, margin=0.18, dpi=150)` or an optional `points=` mode of `figure`.
   It should handle 2D and 3D points (3D through the camera's projection, if epix exposes it) and
   keep the axes' scales equal. Write a doctest or a sample, and a changelog entry if epix-mirror
   keeps one.
2. **geometricalgebra:** bump `EPIX_COMMIT`, run `make image`, and replace `scene_around`'s body
   with the new call. It keeps drawing its light axes. Then rerun the six `bootstrap-*.py`
   notebooks and `make docs`, and check that the figures are unchanged or better.
3. Decide whether `frame-qr-*.py` should switch too (Open question 2).

## Open questions

1. **API shape:** a separate `epix.figure_around(points, width)`, or `epix.figure(points=...,
   width=...)` as a second mode of the existing function? *(Recommend: a separate function. It
   leaves `figure`'s signature alone, and every existing figure stays byte-identical.)*
2. **Frame-QR notebooks:** switch them to the fitting figure in the same change, or leave their
   hand-tuned bounds? *(Recommend: leave them. Their figures are tuned and their frames aren't
   meant to be edited by readers yet.)*
3. **Mounting:** epix-mirror isn't mounted in this sandbox (2026-11-16). Should the epix-mirror
   half be done in a session where it is mounted, or will you make that change yourself?
   *(Recommend: mount it and let the agent do both halves.)*
