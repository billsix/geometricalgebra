# Verify dot/wedge as the projection/rejection geometric products

**Status:** in-progress
**Priority:** 4
**Difficulty:** 2
**Started:** 2026-08-03

## Goal

Confirm — symbolically in gacalc and, ideally, with a written proof suitable for the
book — that for two vectors $a, b$, splitting $a$ into its projection $a_\parallel =
\operatorname{proj}_b(a)$ and rejection $a_\perp = \operatorname{rej}_b(a)$ gives:

- $a_\parallel\, b = a \cdot b$ — the geometric product of the projection with $b$ is the
  **dot product** (the wedge term vanishes because $a_\parallel \parallel b$).
- $a_\perp\, b = a \wedge b$ — the geometric product of the rejection with $b$ is the
  **wedge product** (the dot term vanishes because $a_\perp \perp b$).

This is the "prove-it-once, then use it as a black box" kind of result the GA book wants
to make legible: the geometric product decomposes cleanly along the parallel/perpendicular
split of one vector relative to the other.

## Plan

- [ ] Verify $a_\parallel\, b = a \cdot b$ symbolically in gacalc (general 2D/3D vectors).
- [ ] Verify $a_\perp\, b = a \wedge b$ symbolically in gacalc.
- [ ] Sanity-check that $a_\parallel + a_\perp = a$ and that $a_\parallel\,b + a_\perp\,b$
      reconstitutes the full geometric product $ab = a\cdot b + a\wedge b$.
- [ ] Write up the short proof (parallel ⇒ zero wedge; perpendicular ⇒ zero dot) for the book.

## Notes / decisions

- Origin: Bill's ask (2026-08-03) while scoping the OpenStax-pedagogy reference doc. Serves
  as a concrete example of the multi-level / black-box concern that motivated that survey.

## Open questions
