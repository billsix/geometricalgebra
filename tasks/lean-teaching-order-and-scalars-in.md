# Lean: the G2/G3 laws in teaching order, and the "scalars in" theorems

**Status:** proposed — needs go-ahead (approved in session 2026-11-09; in progress)
**Priority:** 6
**Difficulty:** 6
**Created:** 2026-11-09
**Source:** `tasks/review/2026/11/08/repo-review.md` §7.2
**Related:** `tasks/push-delicate-coordinate-core-tier.md` (the `_coord` tier) and
`tasks/lean-proofs-remove-extras.md` (unused tactics). Both are kept separate.

## BLUF

Put the G2/G3 algebra laws in the order `tasks/reference/algebra-teaching-order.md` prescribes, with
every law in its algebra's file. Then restate, over `IsVector` objects, the theorems that take free
coordinates and build `vec …` inside, wherever `CLAUDE.md` › "Coordinates only when needed" doesn't
allow that shape. Done means `bash proofs/check.sh` passes, there are no new warnings, and each
flagged theorem is either restated or listed with the reason it stays.

## Plan

- [ ] Laws: addition first (commutative, associative, identity, inverse), then the product
  (associative, identity, zero, distributive last), then the scalar laws. Add `G2.zero`; move
  `G2.sub_mul` and `G3.zero_mul`/`add_zero`/`zero_add` into their algebras; put G3's `dot` in its
  product section.
- [ ] Restate the inverted theorems with consumers updated; classify the rest.
- [ ] Gate: `bash proofs/check.sh`; warnings compared before and after.

## Open questions

None.
