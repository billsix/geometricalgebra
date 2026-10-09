# Verify the rotated `a` vector is drawn at the same length as the original `a` in the rotate figures

**Status:** complete
**Completed:** 2026-10-09
**Priority:** 4
**Difficulty:** 2
**Started:** 2026-10-09

## BLUF

**Verified correct — no fix needed.** Every rotate figure draws the rotated `a` with the **same radius
constant** as the original `a`, so the two are equal length by construction. The rotated point has
always been *computed* (`polar(radius=<original length>, angle=<rotated angle>)`), never an eyeballed
coordinate derived from the maintainer's hand-made SVG — true back to the first ePiX commit. The
original SVGs were removed when the Python figures replaced them, but the Python never inherited a
magic rotated-coordinate.

## What was checked

Read every `book/figures/epix/rotate*.py` and the shared scene modules; tabulated each
original-vs-rotated `polar` radius:

| figure | original | rotated | same radius? |
|---|---|---|---|
| `rotate_goal.py` | `a = polar(radius=A_LENGTH=1.25, angle=A_ANGLE)` | `rotated_a = polar(radius=A_LENGTH=1.25, angle=A_ANGLE+THETA)` | ✓ |
| `rotate1.py` / `rotate8.py` | `a = polar(radius=R=1.25, angle=BETA)` | `result = polar(radius=R=1.25, angle=BETA+THETA)` | ✓ |
| `_rotate_ab_scene.py` | `A = polar(radius=A_LENGTH=1.1, angle=A_ANGLE)` | `RESULT = polar(radius=A_LENGTH=1.1, angle=B_ANGLE)` | ✓ |

- The `radius=1` points in `rotate3`–`rotate7` are the **unit-circle intermediate steps** (the rotated
  *direction* before re-lengthening); `rotate8`'s `result` is where it is scaled back to `R`. Correct.
- The only hardcoded radii (`rotate7.py:87` `radius=1.45`, `rotate8.py:89` `radius=R + 0.2`) are
  **label positions**, not vector endpoints.
- A length-preserving rotation changes only `angle`, not `radius` — which is exactly what the code does.

## The "derived from my SVG" recollection — resolved by git history

- `git log --follow book/figures/epix/rotate_goal.py`: created in `dcc4ba3` (ePiX front-end + first
  figures), ported in `90ee212` ("Port the eight proof figures … remove the SVGs"). The rotate proof
  itself was ported from modelviewprojection (`6f67a3d`).
- In the **first** version (`dcc4ba3`), `rotated_a = polar(A_LENGTH, A_ANGLE + THETA)` — already the
  same `A_LENGTH` as `a = polar(A_LENGTH, A_ANGLE)`. So no SVG-measured coordinate was ever used for
  the rotated point; it has always been computed from the original's length.
- The maintainer's hand-made SVGs existed and were deliberately removed (`90ee212`) when the ePiX
  Python figures replaced them; the layout constants (`A_LENGTH`, `A_ANGLE=66°`, `THETA=66°`) may have
  been chosen to echo that SVG's look, but they are cosmetic and do not affect length-equality.

## Verification

Read-only — no figure changed, so no re-render was needed. The conclusion is a direct read of the
`polar(...)` calls plus `git show dcc4ba3:…` on the first version.

## Open questions

None.
