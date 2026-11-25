# Make the first `make lean` on a fresh checkout fast

**Status:** go-ahead 2026-11-25, question 1 answered (see Decisions); not started
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
- `tasks/archive/2026/11/25/lean-proofs-remove-extras.md` also touches the proofs; coordinate so the two don't fight.

## Open questions (answered 2026-11-25, see Decisions)

1. Is a cached CI build acceptable, or must a clean build itself be fast? Recommend measuring the split
   and the slow proofs first; caching only hides the cost.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-25)

1. Measure first: split the clean-build time and find the slow proofs before choosing a cache. Caching only hides the cost, so no decision to rely on a cached CI build is made until the measurement is in this doc.

The decision was the maintainer's "go with your suggestions" on the recommendation above.
