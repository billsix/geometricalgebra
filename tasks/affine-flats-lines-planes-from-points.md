# Affine lines/planes from points (calc-3 style), not origin-oriented

**Status:** blocked
**Priority:** 7
**Difficulty:** 7
**Started:** 2026-08-27 (William Emerison Six <billsix@gmail.com>)
**Blocked on:** maintainer answers the Open questions below — chiefly full PGA/CGA substrate vs a
lightweight pedagogical representation. **This is the most under-specified bullet and potentially the
largest (architectural).**
**Recheck:** the Open questions below are answered (maintainer-gated; `/recheck-blocked` surfaces it).

## Goal

Maintainer's idea, verbatim: *"Take descriptions of lines, planes in calc 3, and make them into
geometric objects. These ones don't have to be oriented around the origin. Make examples in graded
notebook. Should be able to take 2 points to create a line, which can be extrapolated via a method on
it, or by a description in standard form. Same thing for a plane, 3 points define it, make a function
that can then transform 2d into 3d, or take the standard plane form to create the plane."*

Model **affine** (offset, not origin-through) lines and planes as geometric objects: 2 points → line,
3 points → plane, with standard-form ↔ object conversion, and graded-notebook examples.

## Context (investigation 2026-08-27)

- **Scope flag — this is likely large/architectural.** `tasks/reference/galgebra-comparison.md:30,33,35,
  107-131` records that non-origin lines/planes/points + meet/join/incidence need a **projective (PGA)**
  or **conformal (CGA)** model, which needs mixed/degenerate metric signatures — listed as gap row #7
  (signatures, "large, architectural") gating row #9 (meet/join/incidence). gacalc today is **Euclidean
  origin-through-subspaces only**.
- A **lightweight interim** exists as an alternative: store an offset point + a direction/normal blade
  in plain 𝒢ₙ, without a full projective model — much smaller, enough for calc-3 pedagogy.
- **Collision risk with the projections bullet:** keep this (affine/offset flats) distinct from the
  "projections line→line / plane→plane" work in `generalize-reject-reflect-higher-grade.md`, which is
  about origin-through subspaces.

## Plan (draft — depends entirely on Q1)

- If **pedagogical interim**: a point + direction/normal blade representation in 𝒢ₙ; constructors from
  2 points (line) / 3 points (plane); standard-form ↔ object; graded-notebook examples.
- If **full PGA/CGA**: this becomes the metric-signatures architectural project (galgebra-comparison #7).

## Open questions

1. **Full model or interim?** Do you want the full **PGA/CGA** affine-geometry substrate (large, gated on
   metric signatures per galgebra-comparison #7), or a **pedagogical** calc-3 representation (point +
   direction/normal blade) that skips conformal machinery? *(Recommend: pedagogical interim first.)*
2. **"Transform 2d into 3d"** — what does this mean: an embedding of 2D into 3D, or a homogeneous lift?
3. Confirm this is distinct from the origin-through-subspace projections work (bullet 3 /
   `generalize-reject-reflect-higher-grade.md`).
