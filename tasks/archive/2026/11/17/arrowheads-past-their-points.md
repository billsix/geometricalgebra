# ePiX arrowheads poke past the point they should end at

**Created:** 2026-11-17 (William Emerison Six <billsix@gmail.com>)
**Done:** 2026-11-17
**Related:** `tasks/archive/2026/11/17/book-notebooks-symbolic-proof-style.md` (the notebooks whose figures showed it);
github.com/billsix/epix-mirror `tasks/archive/2026/11/17/arrowheads-end-on-their-points.md` (the fix)

## What was wrong

In the book's ePiX figures an arrow's visible tip ran past the point it was drawn to, so arrows that
met at a point crossed. The maintainer saw it in `book/docs/notebooks/proof-projection.py`'s last
figure, where the projection and the rejection add up to $a$ and their arrowheads went through each
other.

Measured on a 600 dpi probe (arrows drawn to a red reference line): the eepic put the head polygon's
tip exactly on the point, and the rendered tip overshot by 2.0 pt at pen width 0.8 pt, 4.4 pt at
1.6 pt and 6.3 pt at 2.4 pt. ePiX stroked the head's outline with the line pen, and at the narrow tip
(half-angle about 10°) the stroke's miter reaches $(w/2)/\sin(\text{half-angle}) \approx 2.8 w$ past
the corner; the shaft also ran to the tip, with round caps.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-17)

1. **Fix it in epix-mirror** (the head set back by the miter length, the shaft stopped under the head),
   rather than compensating in the book's helpers.
2. **Where two arrows share a tip, the parts go on top**: draw the result first, then its parts.
   `proof-projection.py` already draws $a$ before the projection and rejection; the rule is carried
   into `tasks/archive/2026/11/17/book-notebooks-symbolic-proof-style.md` (rule 5) for the other notebooks.

The other options weighed: compensating in `book/figures/epix/_frame_scene.py` `arrow()` by pulling
the tip back, or drawing the shaft and head separately there. Both needed a points-to-figure-units
conversion per scene type and fixed only the book's figures.

## What changed here

- `Dockerfile` `EPIX_COMMIT` moved from `8cb788a…` to `8fe7ff3…`, epix-mirror's fix commit (an
  ancestor of its pushed `master`, merge `fcfca67`).
- `tasks/reference/book-and-docs-pipeline.md` records the new minimum pin, and its citation of
  epix-mirror's figure-fit task now points at that task's archived path.

## Verification

- epix-mirror's own probe: after the fix every tip lands within 0.3 pt short of its point; its port
  harness and smoke gate pass (details in its done-record).
- The image rebuilt with the new pin (`make image`, nested, 4 min 15 s; the build log shows
  "epix-mirror at 8fe7ff3…").
- `proof-projection.py`'s four figures re-rendered: the rejection's head ends on $a$'s tip and the
  projection's head where the rejection starts, with no crossing.
- `make docs` (HTML and PDF) with the new pin builds clean apart from the pre-existing `frame.py`
  "more than one target found for cross-reference 'InvertibleFunction'" warning. The same warning
  from the new `standardposition.rotation_from_to` docstring was fixed by naming
  `gacalc.functions.InvertibleFunction` in its `Returns:` line.
