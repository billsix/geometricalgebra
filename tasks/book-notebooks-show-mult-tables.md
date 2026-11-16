# Add `show_mult` distribution tables to the book notebooks

**Status:** proposed — needs go-ahead (open questions below)
**Priority:** 5
**Difficulty:** 4
**Started:** 2026-11-16 (William Emerison Six <billsix@gmail.com>)

## BLUF

The `notebooks/display*.py` notebooks show a geometric product as a table: every term of the left
factor times every term of the right, then the sum. The book notebooks in `book/docs/notebooks/`
never do; they print only the simplified product, or a difference that is zero. Add `show_mult`
tables to the book notebooks at the products where seeing the term-by-term distribution helps the
reader. Done means: each chosen cell renders its table in the built HTML, the book build and the
test gate pass, and the open questions below are answered and recorded.

## Context

- **The helper:** `show_mult(a, b)` in `src/gacalc/nbplotutils.py`. It prints "We want to
  evaluate", the product in LaTeX, a pandas `to_markdown` table (Left Component, `*`, Right
  Component, `=`, Product, one row per pair of blade terms, from `_blade_terms`), then "Summing
  all the products up, we get" and the total. Numerators are expanded and denominators left
  factored (`_expand_numerators_dict`). History: `tasks/archive/2026/06/12/show-mult-improvements.md`,
  `tasks/archive/2026/06/15/show-mult-expand-numerators-not-denominators.md`.
- **Where it is used now:** `notebooks/displaymv.py` (including the associativity comparison,
  `show_mult(G2_1 * G2_2, G2_3)` against `show_mult(G2_1, G2_2 * G2_3)`), `notebooks/displayg2.py`,
  `notebooks/displayg3.py`, `notebooks/displayrotations.py`. No file under `book/` calls it.
- **It works on the book's graded types.** Checked 2026-11-16 in the sandbox (not the gate):
  `show_mult(2*e_1 + 1*e_2, 1*e_1 + 2*e_2)` with `gacalc.g2` vectors runs and displays all six
  parts. It has not yet been run inside a myst-nb book build.
- **Cost of the import:** `gacalc.nbplotutils` imports matplotlib, pandas and numpy at module
  level. The book notebooks draw with ePiX (`book/figures/epix/_bootstrap_live.py`) and currently
  do not import matplotlib at all. `pandas` is in the `notebooks` extra in `pyproject.toml`;
  `tabulate` (which `to_markdown` needs) is only a transitive pin in `constraints.txt`.
- **Candidate cells** (found by grep for products in `book/docs/notebooks/*.py`; to be confirmed
  in step 1):
  - `bootstrap-product.py`: `a * b`, and `a * projection` / `a * rejection` (dot and wedge as `a`
    times projection and rejection), concrete and symbolic.
  - `bootstrap-rotation-from-product.py`: `a_hat * b_hat`, `v * unit_product`, the sandwich
    `R * v * R⁻¹` (two tables, like `notebooks/displayrotations.py`).
  - `bootstrap-projection-from-product.py`: `b * a`, `b.wedge(a) * a⁻¹`.
  - `product-from-projection.py`: `b * a`.
  - `geometric-product.py`: `a * R`, and the "Rotation is distributive" cell
    `(a + b) * R` against `a * R + b * R`.
  - `levels-of-abstraction.py`: `a * b`.

## Plan

1. Survey the candidate cells above and pick the ones to table (per open question 1). Record the
   list here.
2. Settle the import (open question 3). If `show_mult` moves to a lighter module, keep
   `gacalc.nbplotutils.show_mult` working for the `notebooks/` callers.
3. Add the `show_mult` cells next to the existing product cells, each with a one-line Markdown
   lead-in saying what the table shows. Keep the existing simplified-product and zero-difference
   cells, since those carry the result.
4. Build the book (`make docs` or whatever the repo's `CLAUDE.md` names) and check that the tables
   render in the HTML (myst-nb renders `IPython.display.Markdown` tables). Run the test gate.

## Open questions

1. Which products get a table: every product in the candidate list, or only the first appearance
   of each kind (vector × vector, vector × rotor, sandwich)? Recommended: first appearance of each
   kind, so a page carries one or two tables, not six.
2. Concrete or symbolic factors? The bootstrap notebooks set concrete vectors first and repeat the
   checks with symbols at the end, as the companion-notebook rule in `CLAUDE.md` ("Book: one name
   per operation …") and `tasks/reference/book-outline.md` ("Pedagogical principles") require.
   Recommended: table the concrete product (small numbers, short rows), and table the symbolic
   product once per notebook, in its final section.
3. Is pulling matplotlib/pandas into the book notebooks through `gacalc.nbplotutils` acceptable, or
   should `show_mult` move to a module without the plotting imports? Recommended: move it to a
   small display-only module and re-export it from `nbplotutils`.
