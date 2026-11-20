# The last three PDF overflows: 3D terms wider than their space

**Status:** ready — decisions recorded
**Priority:** 5
**Difficulty:** 3
**Created:** 2026-11-20 (William Emerison Six <billsix@gmail.com>)

## BLUF

After `tasks/archive/2026/11/20/pdf-long-math-overflow.md`, the book's PDF still cuts off three
places, all where a *single term* is wider than the space it sits in, which no line break between
terms can fix: two `show_mult` product tables in `notebooks/displaymv.py` and one radical in
`notebooks/displayg3measures.py`. Change what those cells show so each term fits, then make
`tools/check_math_overflow.py` a failing gate. Done means the check reports 0 equations and tables
over 10pt on a fresh `make docs`, and `entrypoint/docs.sh` fails the build if one comes back.

## Context

- **How to see them:** `make docs`; its last lines are `tools/check_math_overflow.py`'s report
  (also `python tools/check_math_overflow.py` on the host after a build; the log is at
  `output/gacalc/geometry2.log`). On 2026-11-20 it listed 73 boxes: 36 rows of each table and one
  equation.
- **The tables** (`notebooks/displaymv.py`):
  - "A bivector times its inverse": `show_mult(B.inverse(), B)` for `B = sym_vec3_1 ∧ sym_vec3_2`.
  - "A bivector and its dual": `show_mult(B, B.dual(3))` and `show_mult(B, B.dual(3).inverse())`.

  Each term of `B⁻¹` carries the denominator `|B|² = (e₁f₂ − e₂f₁)² + (e₁f₃ − e₃f₁)² + (e₂f₃ − e₃f₂)²`
  (about 70 visible characters). A table cell is a third of the page (`nbdisplay.TABLE_CELL_WIDTH`,
  24), so each row overflows by 100–160pt. `base.term_tokens` only splits a fraction's
  *numerator*, so the long denominator stays whole.
- **The radical** (`notebooks/displayg3measures.py`, the `show_difference` of
  `|a| * |b| * sin(θ)` against `(a ∧ b).magnitude()`, about line 200): one `\sqrt{…}` of a long 3D
  sum, 29pt over.
- How line breaking works, and why it cannot split a single term: `tasks/reference/book-and-docs-pipeline.md`
  ("Notebook output in the PDF"); `gacalc.base.latex_broken` / `term_tokens`.
- The shrink-to-fit fallback (LaTeX `adjustbox` on every display) was rejected in the parent
  task: it makes all printed math smaller to rescue three places.

## Plan

1. Tables: show `|B|²` by a name. Proposed: before the tables, a cell defines a symbol for it
   (e.g. `B_sq = sympy.Symbol("|B|^2", positive=True)`), and the tables run on `B.inverse()` with
   `|B|²` substituted, so each term is `(e₁f₂ − e₂f₁) / |B|²` and the reader sees the structure
   (the plane parts cancel, the like terms add to `|B|² / |B|² = 1`). A Markdown line ties the
   name to its expansion. The same substitution may tidy `B.dual(3).inverse()`.
2. Radical: show the two sides by name too (the square of each side, or `|a ∧ b|`), keeping the
   numbered cancellation of the squares inside the margin.
3. `make docs`; the check reports 0; look at the three places in the PDF.
4. Make the check a gate: in `entrypoint/docs.sh`, drop the `|| echo …` so a nonzero exit fails
   the build, and say so in `CLAUDE.md` (`make docs` bullet) and the pipeline reference doc.

## Decisions

William Emerison Six <billsix@gmail.com>, 2026-11-20:

1. The tables show `|B|²` as a named symbol (plan step 1), not the full expansion in a changed
   layout. Reason: each term gets shorter, and the reader sees why the terms cancel.
2. Once the count is 0, `make docs` fails on a new overflow (plan step 4), rather than only
   reporting it. Reason: a long new value is caught when it is added, not in print.
