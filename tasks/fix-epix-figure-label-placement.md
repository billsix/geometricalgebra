# Fix label placement / overlap in the ePiX book figures

**Status:** proposed — needs go-ahead
**Priority:** 5
**Difficulty:** 4
**Created:** 2026-10-08 (William Emerison Six <billsix@gmail.com>)

## BLUF

Several of the book's ePiX-generated figures have **labels that overlap each other or sit in the
wrong place** — not cleanly beside the item they name. Worst offenders: `proj3` draws the equation
`a = proj_b a + rej_b a` **along the blue projection segment**, so it reads as the projection's label
instead of describing `a`; the three 3D figures (`proj3d-e12`/`-e23`/`-e31`) crowd the proj/rej/axis
labels, with `proj3d-e31` overlapping the proj and rej labels outright; and `proj2`/`sp5` collide the
`b` label with the `proj_b a` label near `b`'s head. Fix is **label placement only** — adjust each
figure's label anchor/offset/alignment (no geometry or scene changes), re-render, and **visually
re-check every figure** until each label sits beside its item with no overlap. "Done" = all 25 figures
viewed and clean, `make docs` green (HTML + PDF, figures embed), `make format` green (incl. the
`check_epix_keywords` gate).

## Context — how the figures and labels work (read first)

- **Sources:** `book/figures/epix/<name>.py` (one per figure), with shared helpers
  `book/figures/epix/_scene2d.py`, `_scene3d.py`, and the per-topic `_projection_scene.py` /
  `_rotation_scene.py` / `_addition_scene.py` (fixed vectors, box extents).
- **Rendering:** `tools/render_epix_figures.py` runs each figure in a **fresh interpreter** (libepix
  keeps global state) and writes `book/docs/_static/epix/<name>.{pdf,png}` (gitignored build
  artifacts). It takes optional figure NAMEs and `--dpi N`. `make docs` invokes it via
  `entrypoint/docs.sh`; needs the full image (`USE_EPIX=1`, the default).
- **Fast view loop (use this — don't run full Sphinx each iteration):** render just the figures you
  touched and view the PNGs directly, e.g. in the image:
  `python tools/render_epix_figures.py proj3 sp5 proj3d_e31` → open
  `book/docs/_static/epix/proj3.png` etc. (the Read tool shows PNGs). Run it the same way the gate
  does — the target's own `podman run` line against the existing image, **not** a `: image` make
  target that rebuilds nested.
- **Label API (the thing to adjust):** `epix.label(at=<Point>, offset=<Point, in PIXELS>, text=...,
  align=epix.LabelPos.{l|r|c|t|...})`. Helpers: `vector(head=, text=, offset=, align=)` /
  `vector3(...)` label at the vector **head**; `_labeled_segment` labels at a segment **midpoint**.
  **There is no automatic collision avoidance** — every position is a hand-tuned `(at, offset, align)`.
  For 3D, points are genuine 3D and the camera (`frame_scene`) projects them, so a label's screen
  position depends on the camera; `project_onto(plane)` returns the in-plane projection point used as
  an anchor.
- **Conventions to preserve:** every argument passed **by keyword** and every binding **typed**
  (`tools/check_epix_keywords.py`, a `make format` step — see `tasks/reference/book-and-docs-pipeline.md`
  and CLAUDE.md "ePiX"); the default angle symbol is `θ` (`tasks/reference/book-outline.md`); HTML PNGs
  are flattened onto a `BACKGROUND` fill for dark mode — **do not disturb** the scene, colors, or
  background, only move labels.

## The defects found (2026-10-08 visual audit) — the checklist to fix

Verified by viewing the rendered PNGs. Fix each, then re-render + re-view to confirm.

1. **`proj3` (the `a = proj + rej` figure) — maintainer's explicit example.** The equation
   `$\vec a = \mathrm{proj}_{\vec b}\,\vec a + \mathrm{rej}_{\vec b}\,\vec a$` is `epix.label`'d at the
   projection segment's midpoint (`offset=(0,-12)`), so it sits on the **blue projection** line and
   reads as its label. **Re-anchor it to `\vec a`** (the vector the equation is about) — e.g. above /
   upper-left of the `a` head, clear of the blue segment — or to open space inside the triangle.
2. **`proj2`** — `\vec b` (labeled at `B`, `offset=(6,-6)`) overlaps `proj_{\vec b}\,\vec a` (proj
   midpoint, `offset=(2,-11)`) near `b`'s head. Separate them (move `\vec b` further out, or the proj
   label down-left).
3. **`sp5`** — same `\vec b` ↔ `proj_{\vec b}\,\vec a` collision near the proj point / `b` head.
4. **`sp4`** — minor: `a'_x` (blue) and `\vec b'` crowd just below the x-axis; nudge apart.
5. **`proj3d-e12`** — the green `rej` label floats mid-plane, close to the `y`-axis label; crowded and
   not beside its segment. Reposition beside the green rejection segment. **Also verify the `rej`
   subscript renders fully as `e_{12}`** (it looked clipped/ambiguous in the render — confirm the text
   string and that overlap isn't hiding the `2`).
6. **`proj3d-e23`** — `proj_{e23}\,\vec a`, `rej_{e23}\,\vec a`, and `\vec a` cluster in the upper-right;
   the trailing `\vec a` of the multi-part labels runs into the segments. Spread them.
7. **`proj3d-e31` (worst)** — the proj and rej lines are nearly collinear, so `proj_{e31}\,\vec a` and
   `rej_{e31}\,\vec a` **overlap each other** and sit on the vectors. Separate them (e.g. proj below /
   rej above, each pushed perpendicular to the segment) so both read.
8. **Re-scan all 25.** `add1`–`3`, `sub1`–`2`, `rotate1`–`8`, `rotate-goal`, `proj1`, `sp1`–`3` looked
   clean in the audit, but confirm each after any shared-helper change. (`add3`'s `\vec a+\vec b` label
   just grazes the corner dot — a minor nudge is optional.)

## Plan

1. **Stand up the fast loop** (render-subset → view PNG), per Context. Confirm you can render one
   figure and view it before touching anything.
2. **Audit all 25** by viewing each rendered PNG; append anything missed to the checklist above.
3. **Fix placement per figure** — adjust `(at, offset, align)` only. For `proj3`, re-anchor the
   equation to `\vec a`. For the 3D crowding, offset each label perpendicular to its segment and push
   proj/rej to opposite sides. Keep every call keyword-only and every binding typed.
4. **(Optional, only if it pays for itself)** if the same "offset a label perpendicular to its
   segment, away from the other label" pattern recurs, add a small shared helper to `_scene2d.py` /
   `_scene3d.py` (e.g. `segment_label(..., side=...)`) rather than re-tuning pixels per figure. Don't
   over-engineer — per-figure offsets are fine if the count is small.
5. **Re-render + re-view** every changed figure; iterate until each label is beside its item and
   nothing overlaps. Check both the PNG (HTML) and, for at least the fixed ones, the PDF vector output
   (the camera/scale differ slightly).
6. **Gates + stage.** `make docs` green (HTML + PDF, pages embed the figures, 0 notebook errors);
   `make format` green (ruff + `check_epix_keywords` + types). Stage the changed `book/figures/epix/*.py`
   (and any helper) by path.

## Open questions

1. Shared perpendicular-offset label helper vs. per-figure pixel tuning — executor's judgment (plan
   step 4); lean per-figure unless the 3D cases clearly share one pattern.

## Related

- `tasks/reference/book-and-docs-pipeline.md` — the ePiX figure pipeline + keyword/type gate.
- `tasks/reference/book-outline.md` — figure/notation conventions (θ default, from→to naming).
- `tasks/archive/2026/10/07/book-epix-figures*.md` — the umbrella/steps that created these figures.
