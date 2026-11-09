# Book: flesh out the rotate chapter, and show the from-to rotation in its notebook

**Status:** proposed — needs go-ahead (approved in session 2026-11-09; in progress)
**Priority:** 5
**Difficulty:** 4
**Created:** 2026-11-09
**Source:** `tasks/review/2026/11/08/repo-review.md` §3.2

## BLUF

`rotate.rst` gives the book's founding definition (rotate from `a`'s direction to `b`'s, not by an
angle) in three paragraphs, and its notebook rotates by an angle while saying "only the directions
set the rotation". Done means the page explains the definition and why it beats an angle, and the
notebook builds the rotation from two vectors with `versor_rotation`.

## Context

- The voice to follow is the modelviewprojection book (`github.com/billsix/modelviewprojection`,
  `book/docs/`): plain declarative sentences, "let's", practical analogies, rhetorical questions.
- The pages the chapter introduces: `proof-rotate` (by an angle) and `proof-rotate-from-a-to-b`
  (from two vectors).
- The factories: `transforms.versor_rotation(from_vector=, to_vector=)`, and
  `transforms.plane_rotation(a, b)(θ)`.

## Plan

- [ ] Rewrite `rotate.rst`: the definition, why not an angle, magnitudes don't matter, the two
  proof pages in order, the coordinate-free sequel.
- [ ] Rewrite `notebooks/rotate.py`: `versor_rotation` carries `a` to `(|a| / |b|) * b`; scaling the
  inputs gives the same rotation; it agrees with `plane_rotation` at the angle from `a` to `b`.
- [ ] Gate: the notebook runs and is ty-clean.

## Open questions

None.
