# Add arrow heads to the vectors in the ePiX figures

**Status:** in-progress
**Priority:** 5
**Difficulty:** 2
**Started:** 2026-10-09 (William Emerison Six <billsix@gmail.com>)

## BLUF

The book's ePiX figures draw a vector as a plain segment with a dot at the tip (`_scene2d.py`'s
`vector()` / `dashed_vector()` use `epix.line` + `epix.dot`), so a vector doesn't visually read as a
directed arrow. Give every such vector a small but **visible** arrow head, using `epix.arrow` (already
used for the axes), so vectors look like vectors. Small change, one place (the shared helpers), then
re-render.

## Context (read first)

- `book/figures/epix/_scene2d.py`: `vector(head, text, offset, align)` draws `epix.line(tail=ORIGIN,
  head=head)` then `epix.dot(at=head)`; `dashed_vector(tail, head, …)` does the dashed equivalent. The
  **axes** already use `epix.arrow(tail=…, head=…, scale=1)` (in `unit_circle_scene`), so `epix.arrow`
  is available and its look is set.
- `book/figures/epix/_scene3d.py`: `vector3(...)` is the 3D vector helper (also check it uses an arrow;
  the 3D axes use `epix.arrow`).
- Rendering: `tools/render_epix_figures.py` (`make docs`); conventions in
  `tasks/reference/book-and-docs-pipeline.md` ("ePiX figures"): every arg by keyword, every binding
  typed, label colour matches its line.

## Goal

`vector()` (and `dashed_vector()`, and the 3D `vector3()` if it lacks one) draw an arrow head at the
head — small but clearly visible — in place of (or in addition to) the tip dot. The arrow head matches
the line's colour (the label-colour standard's spirit). Re-render all figures and confirm `make docs`
builds, vectors now reading as arrows.

## Plan

- [ ] In `_scene2d.py`, switch `vector()`/`dashed_vector()` to `epix.arrow` for the shaft+head (keep or
      drop the tip dot — decide by eye); match the arrow's pen colour to the vector.
- [ ] Check `_scene3d.py`'s `vector3()` and give it an arrow head too if it uses a plain line.
- [ ] Re-render (`make docs` / the epix step); eyeball a few figures (`rotate-goal`, `add*`, `proj*`,
      `rotate9`) to confirm the heads are visible and not oversized.
- [ ] `make docs` green; `ruff`/`check_epix_keywords` clean.

## Open questions

None — the intent is clear (visible arrow heads on vectors). Head size and keep-the-dot-or-not are
small by-eye calls made during the work.
