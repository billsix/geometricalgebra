# Show vector `a` as a similar (scaled-up) right triangle in the rotate figures

**Status:** complete
**Completed:** 2026-10-09
**Priority:** 5
**Difficulty:** 4
**Started:** 2026-10-09 (William Emerison Six <billsix@gmail.com>)

## BLUF

Added a new final step to the `proof-rotate` figure sequence — **`rotate9`** — that overlays the unit
right triangle (`cos θ`, `sin θ`) and `a`'s scaled-up **similar** triangle (`r * cos θ`, `r * sin θ`,
hypotenuse the rotated full-length `a`), driving home the high-school "same angles ⇒ similar ⇒
proportional sides" so a reader sees *why* scaling the unit answer by `r` lands on the rotated `a`. The
shared `R` (|a|) was raised to **1.7** across all rotate figures (the maintainer's call) so the two
triangles' labels separate. `make docs` builds clean (HTML + PDF), the new figure included.

## What was done (maintainer decisions, 2026-10-09)

- **A new last step, `rotate9`** (`book/figures/epix/rotate9.py`), added to `book/docs/proof-rotate.rst`
  after the "scale back to length r" step, with a paragraph naming the similar triangles and the `r`
  ratio. (The maintainer didn't want the choice framed by figure filename; a dedicated new step keeps
  the busy last step uncluttered.)
- **`R = 1.7` for the whole sequence** (bumped in `_rotation_scene.py`, with `rotate_goal.py`'s
  `A_LENGTH` kept in sync). Chosen by experiment: at the old `R = 1.25` the labels collided; 1.7
  separates the `sin` legs and keeps `a` from running too far outside the circle. Re-rendered and
  eyeballed `rotate_goal`/`rotate1`/`rotate8`/`rotate9` — nothing clips.
- **Two triangles distinguished by shade, smaller drawn on top, labels matched to lines.** `a`'s
  (big) triangle uses the bold `BLUE`/`GREEN`; the unit (reference) triangle uses lighter shades of the
  same hues (`LIGHT_BLUE`/`LIGHT_GREEN`) drawn on top so it stays visible where the legs overlap. The
  `sin` legs separate naturally; the `cos` legs are collinear (both along `x'`), so they are drawn
  unlabelled and their two labels placed explicitly at well-separated radii, each in its leg's colour.
- **Standardized "label colour matches its line/vector"** — the maintainer's rule, so a reader instantly
  sees which label is which. Documented in `tasks/reference/book-and-docs-pipeline.md` ("ePiX figures")
  and a one-line rule in `CLAUDE.md`'s ePiX section.

## Verification

- `make docs` (full, nested): HTML + PDF both "build succeeded"; `rotate9.{png,pdf}` rendered and
  referenced once in `proof-rotate.html`. All figures re-rendered at `R = 1.7` without error.
- `ruff check` / `ruff format --check` / `check_epix_keywords` clean on `rotate9.py` and the touched
  scene files.

## Open questions

None.
