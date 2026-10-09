# Verify the rotated `a` vector is drawn at the same length as the original `a` in the rotate figures

**Status:** in-progress
**Priority:** 4
**Difficulty:** 2
**Started:** 2026-10-09

## BLUF

The maintainer wants a check that the rotate figures place the **rotated** `a` at the **same length**
as the original `a` — it looked, at first glance, like the rotated point might carry values derived by
eye from the maintainer's original hand-made SVG rather than computed. Verify by reading the ePiX
figure Python, confirming both the original and the rotated vectors use the **same radius constant**
(a rotation preserves length). Deliverable: a confirmation (with the exact lines) that the lengths
match — or, if any figure places the rotated point at a different/eyeballed radius, a fix so it uses
the original's radius. Also check git history for whether an SVG-derived magic coordinate was ever used.

## Context (read first)

The figures are ePiX Python under `book/figures/epix/`, rendered by `tools/render_epix_figures.py`
(see `CLAUDE.md` › "ePiX in the image" and `tasks/reference/book-and-docs-pipeline.md`). `polar(radius,
angle)` places a point; a length-preserving rotation keeps `radius` and changes only `angle`.

Early reading (verify each; this is most of the task):

- **`rotate_goal.py`** draws both: `a = polar(radius=A_LENGTH, angle=A_ANGLE)` and
  `rotated_a = polar(radius=A_LENGTH, angle=A_ANGLE + THETA)` — same `A_LENGTH`, so equal length by
  construction. `THETA = math.radians(66)`.
- **`rotate1.py` … `rotate8.py`** import `R`/`BETA`/`THETA` from `_rotation_scene.py`;
  `rotate1` has `a = polar(radius=R, angle=BETA)` and `rotate8` has
  `result = polar(radius=R, angle=BETA + THETA)` — same `R`.
- **`_rotate_ab_scene.py`** (the a→b figures): `A = polar(radius=A_LENGTH, …)` and
  `RESULT = polar(radius=A_LENGTH, …)` — same `A_LENGTH`.

So the quick read says every rotated vector reuses the original's radius constant (lengths equal). The
maintainer's "derived from my SVG" worry is about the *angle/length constants* possibly being eyeballed
— but as long as original and rotated share the radius, the **length-equality** the maintainer asked
about holds regardless of the constant's value.

## Goal

Confirm, with the exact `polar(...)` lines from every rotate figure and the shared scene modules, that
the rotated `a` uses the same radius as the original `a` (so the drawn lengths are equal). If any figure
violates this (an eyeballed/hardcoded rotated coordinate), change it to `polar(radius=<original radius>,
angle=<rotated angle>)`. Check `git log`/`git show` on the figure files and any removed SVG for whether
an SVG-derived value was once used. Re-render if anything changes (`make docs` / the epix step) and
confirm the figures still build.

## Plan

- [ ] Read every `book/figures/epix/rotate*.py` and the shared `_rotation_scene.py` /
      `_rotate_ab_scene.py`; tabulate each original-vs-rotated `polar` radius.
- [ ] Confirm equality (or find and fix a mismatch).
- [ ] `git log`/`git show` the figure files + any `.svg` the maintainer removed, to address the
      "derived from the SVG" recollection.
- [ ] If anything changed, re-render the epix figures and confirm the build.

## Open questions

None — the intent is clear (rotated length must equal original length); verify, and fix only if a
figure violates it.
