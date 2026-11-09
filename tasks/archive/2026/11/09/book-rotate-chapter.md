# Book: flesh out the rotate chapter, and show the from-to rotation in its notebook

**Created:** 2026-11-09 · **Completed:** 2026-11-09
**Source:** `tasks/review/2026/11/08/repo-review.md` §3.2

## What changed

- **`book/docs/rotate.rst`** is written in the modelviewprojection book's voice (plain declarative
  sentences, "let's", an everyday analogy, a rhetorical question). It now:
  - opens with the from-to definition and the `rotate-ab-goal` figure;
  - explains why the book doesn't start from an angle ("thirty degrees from where, and turning which
    way?", turning your head from where you're looking to where something is);
  - says magnitudes don't matter (`2 * a` toward `5 * b` is the same rotation);
  - walks the two proof pages in order: `proof-rotate`, with the `rotate-goal` figure, then
    `proof-rotate-from-a-to-b`;
  - points at the coordinate-free sequel (`geometric-product`, `rotation-from-vectors`).

  It keeps the Draft note: no page has had the maintainer's voice pass.
- **`book/docs/notebooks/rotate.py`** builds the rotation from two vectors with
  `versor_rotation(from_vector=a, to_vector=b)`. It checks that:
  - it carries `a` to `(|a| / |b|) * b`;
  - `versor_rotation(2 * a, 5 * b)` moves `e_1` to the same place;
  - `plane_rotation(e_1, e_2)` at the angle from `a` to `b` agrees (computed only to check, "a
    property, not something to solve for").

  It used to rotate by an angle while saying "only the directions set the rotation".

## Verification

The notebook runs as a script, `ty` and `ruff` are clean, and the scratch HTML build has no warnings
for the page.
