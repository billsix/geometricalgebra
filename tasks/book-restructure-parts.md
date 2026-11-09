# Book: restructure into Part I (the plane) and Part II (space), with a second route to the product

**Status:** proposed — needs go-ahead (approved in session 2026-11-09; in progress)
**Priority:** 4
**Difficulty:** 4
**Created:** 2026-11-09
**Source:** `tasks/review/2026/11/08/repo-review.md` §3.2, §1.2, and its open questions 1–4

## BLUF

The maintainer answered the review's book questions (William Emerison Six <billsix@gmail.com>,
2026-11-09):

1. (b): add a chapter that builds the geometric product from projection and rejection, "as long as
   you can get it to work";
2. move `blade-square-sign` and `levels-of-abstraction` after `defining-g2`;
3. move Part I's 3D material to Part II and split `index.rst`;
4. no page has had a voice pass ("you can word it however you like, read modelviewprojection
   restructuredtext for my voice").

Done means the toctree, the pages and `tasks/reference/book-outline.md` match those answers. The new
chapter must exist in all three forms (Lean, symbolic Python, prose), and every moved notebook must
still run.

## Context

`book/docs/index.rst` is one flat toctree. The narrative problems are in review §3.2:

- `proof-projection` promises "much later" to build the product from projection, but no chapter
  does;
- `levels-of-abstraction` and `blade-square-sign` sit inside the spine;
- 3D material appears in Part I (`proof-projection`'s 3D section, `levels-of-abstraction`'s 𝒢₃
  cells, `blade-square-sign`'s grades 3–5).

The proof-page conventions are in `tasks/reference/book-outline.md`, and the three-forms rule is in
`CLAUDE.md`.

## Plan

- [ ] The new chapter `product-from-projection`: `b * a = |b| * (x + y * e₁₂)`, with `(x, y)`
  where `a` lands when `b` is rotated onto the x-axis. Prove it in Lean
  (`G2.mul_eq_magnitude_smul_alignSP`); check it in a symbolic notebook; write the page, citing both.
- [ ] Reword `geometric-product` as the first of the two routes, and `proof-projection`'s promise and
  payoff to point at the new chapter. Move `rotation-from-vectors` under the new chapter.
- [ ] Split `index.rst` into "Part I — The plane" and "Part II — Space" (plus "Reference"). Move
  `blade-square-sign` (whole) to Part II, and `levels-of-abstraction` to after `defining-g2`.
- [ ] Move `proof-projection`'s 3D section and notebook cells to a new Part II proof page,
  `proof-projection-3d`. Move `levels-of-abstraction`'s 𝒢₃ cells to the `three-dimensions`
  notebook, and make the remaining cells exact (no decimals).
- [ ] Refresh `book-outline.md`: status, current order, the decisions, the file lists.
- [ ] Gate: every changed notebook runs and is ty-clean; `bash proofs/check.sh`; the RST parses.

## Open questions

None.
