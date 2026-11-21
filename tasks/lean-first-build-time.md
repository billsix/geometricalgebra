# Make the first `make lean` on a fresh checkout fast

**Status:** proposed — needs go-ahead
**Priority:** 6
**Difficulty:** 5
**Created:** 2026-11-21 (William Emerison Six <billsix@gmail.com>), measured while finishing
`tasks/archive/2026/11/21/book-opening-vectors-supersede-geometry-types.md`.

## BLUF

Mathlib is baked into the image, but the project's own proofs are not: on a checkout with an empty
`proofs/.lake/build`, `make lean` compiles the whole proof library, and `proofs/GacalcProofs/G3.lean`
alone took 1725 s (about 29 minutes). CI's tag-only `lean.yml` and any fresh clone pay that every time.
Find where the time goes and cut it. Done = a measured first-build time well under the current one, with
the approach recorded in `tasks/reference/lean-ga-proof-architecture.md`.

## Context

- Read first: `CLAUDE.md` ("make lean"), `tasks/reference/lean-for-gacalc.md`,
  `tasks/reference/lean-ga-proof-architecture.md`, `proofs/check.sh`, `entrypoint/install-lean.sh` and the
  `USE_LEAN` block of the `Dockerfile` (how Mathlib is baked).
- Options to measure: split `G3.lean` (one huge file builds serially; smaller files build in parallel and
  rebuild less); find the slow proofs (`set_option profiler true`, or per-declaration timing) and replace
  heavy `simp`/`ring`/`field_simp` calls; cache the project's `.lake/build` in CI between tag runs.
- `tasks/lean-proofs-remove-extras.md` also touches the proofs; coordinate so the two don't fight.

## Open questions

1. Is a cached CI build acceptable, or must a clean build itself be fast? Recommend measuring the split
   and the slow proofs first; caching only hides the cost.
