# `nbplotutils.sine`: correct for graded vectors, and only in the plane

**Status:** proposed — needs go-ahead (approved in session 2026-11-09; in progress)
**Priority:** 3
**Difficulty:** 2
**Created:** 2026-11-09
**Source:** `tasks/review/2026/11/08/repo-review.md` §4.2

## BLUF

`nbplotutils.sine` returns 0 for graded vectors, and 0 for perpendicular vectors off the e₁e₂ plane.
It also uses `abs(v1 * v2)` against the recorded `|a| * |b|` decision, and a bare `assert`. Done
means it is the signed sine of two 𝒢₂ vectors, built on `measure.signed_area`; it raises for vectors
it can't sign; and it is tested.

## Context

- **The bug.** `type(v1).from_blade_dict({(1, 2): 1})` on a graded `Vector` silently drops the
  bivector (the graded "exp() trap" in `tasks/reference/blade-dict-interchange.md`), so the 90° turn
  is zero.
- **The callers:** `_draw_labelled_triangle` and `draw_ndc` (the triangle-label angles).
- **The rules:** `CLAUDE.md`'s `require_vector` rule, and the archived "keep `|a| * |b|`, never
  `abs(b * a)`" decision (`tasks/archive/2026/06/27/wedge-magnitude-sin-notebook.md`).

## Plan

- [ ] `sine(v1, v2) = signed_area(v1, v2) / (|v1| * |v2|)`, after `require_vectors` and the zero
  check. `signed_area` raises for vectors not in a 2D space.
- [ ] Tests: `Gn`, `g2.Vector` and `g2.G` give `sine(e_1, e_2) = 1` and `sine(e_2, e_1) = −1`; a 𝒢₃
  vector raises.

## Open questions

None.
