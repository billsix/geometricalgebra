# Make the rotate3 figure the same width as its sibling rotate figures

**Status:** done — 2026-10-08 (gates green)
**Priority:** 6
**Difficulty:** 3
**Created:** 2026-10-08 (William Emerison Six <billsix@gmail.com>)

## What was done (2026-10-08)

- **`book/figures/epix/rotate3.py`** — dropped the widened box override (`lower_left=(-2.7,-1.3)`) back
  to the default `unit_circle_scene()`, and reformatted the long upper-left label
  `(\cos(\beta+\pi/2),\ \sin(\beta+\pi/2))` from a horizontal pair into a **column vector**
  `\begin{bmatrix}\cos(\beta+\pi/2)\\\sin(\beta+\pi/2)\end{bmatrix}` (the book already uses bmatrix
  column vectors in the algebra sections), placed centered above the perpendicular vector's head
  (`offset=(6,16)`, `align=c`) so it clears the vector line. The shorter `(\cos\beta,\sin\beta)` label
  stays horizontal, matching `rotate1`/`rotate2`.
- **Result:** `rotate3` now renders **537×457 px**, matching the siblings (`rotate2` 537, `rotate1`
  564) — was 833 px wide. Verified by render→view + PIL size check; `make format` + `make docs` green.
- **Sibling scan:** `rotate1`/`2`/`4`/`5`/`6` already use the default box (consistent). **`rotate7`
  (645×547) and `rotate8` (681×583) are larger**, but for a different reason — they are also **taller**
  (`upper_right.y = 1.9` / `2.1`) to show the result vector reaching up, and their width comes from the
  inherently-wide *sum* label `r(\cos\theta\,\vec{x'}+\sin\theta\,\vec{y'})` (not a coordinate pair that
  column-stacks cleanly). Left as-is: they're larger by design for the content, and `rotate3` was the
  flagged egregious width outlier. If the maintainer wants `rotate7`/`8` normalized too, that's a
  follow-on (would mean relocating/reformatting the result-sum label).

## BLUF

In `book/docs/proof-rotate.rst`, the figure after "Before we can rotate by :math:`\theta`, we first
need to rotate by 90° … Rotating :math:`(\cos\beta,\sin\beta)` … gives
:math:`(\cos(\beta+\pi/2),\sin(\beta+\pi/2))`" — that's **`rotate3`** — renders **much wider** than the
other rotate figures (`rotate1`/`2`/`4`–`8`). Cause: its labels are long
(:math:`(\cos(\beta+\pi/2),\ \sin(\beta+\pi/2))`), so the figure was given a widened box
(`lower_left=Point(x=-2.7, y=-1.3)` vs the default `-1.6`) to fit them — and since the rendered size
scales with the box width (`unit_circle_scene` sets physical size = box-width × `UNIT_SCALE_IN`), the
image comes out wider. Make it the **same size** as the siblings (which use the default box). **Not
started — this is the spec.**

## What to change

- **`book/figures/epix/rotate3.py`** — bring it back to the default box so its width matches the other
  rotate figures (`rotate2`/`rotate4` just call `unit_circle_scene()` with no box override). That means
  the long labels must no longer dictate the box. Options (maintainer's preference, pick one):
  1. **Short names + a key/legend** — label the two directions with short symbols (e.g. a letter or
     number) and say what each is in the **prose** (`proof-rotate.rst`, right where the figure sits) or
     a small in-figure key, instead of the full `(\cos(\beta+\pi/2), \sin(\beta+\pi/2))` inside the plot.
  2. **Shorten / relocate the labels** so they fit the default box (e.g. stack the coordinate pair,
     move it inside the frame, or abbreviate), keeping the default `unit_circle_scene()` box.
  Either way the goal is: **default box → same rendered width as the other rotate figures**, labels
  still legible.
- **Also scan the other rotate figures for the same issue.** `rotate1` carries a longish label too
  (:math:`r(\cos\beta,\sin\beta)`) — check whether it (or any sibling) also overrides the box and
  widens; if so, apply the same fix so the whole `rotate1`–`rotate8` set renders at one consistent size.

## How to check sizing

`unit_circle_scene(lower_left=…, upper_right=…)` computes `size = (width × UNIT_SCALE_IN) x (height ×
UNIT_SCALE_IN)` (`_scene2d.py`). Same box ⇒ same physical size. Render the set and compare:
`tools/render_epix_figures.py rotate1 rotate2 rotate3 rotate4 rotate5 rotate6 rotate7 rotate8`, then
view the PNGs (their pixel dimensions should match). Use the render→view loop; keep every figure arg
by keyword and typed (`check_epix_keywords` gate).

## Gates

`make docs` green (the page renders, the figure embeds at the consistent width); `make format` green.
Stage by path.

## Related

- `book/figures/epix/rotate3.py` (the wide one) and `_scene2d.py` (`unit_circle_scene`, `UNIT_SCALE_IN`).
- `book/docs/proof-rotate.rst` — the page; if going with option 1, the key/legend prose lives here.
- `tasks/archive/2026/10/08/fix-epix-figure-label-placement.md` — prior label-placement work (same
  render→view discipline).
