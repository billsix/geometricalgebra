# Long math expressions ran off the PDF page

**Created:** 2026-11-20 (William Emerison Six <billsix@gmail.com>) · **Completed:** 2026-11-20

The maintainer's ask (2026-11-20, verbatim): *"Take a look at the math expressions that get cut
off in the PDF because they are too long, and come up with a strategy for fixing that."* LaTeX
does not wrap display math, so a long computed value, cancellation line or product table ran past
the right margin and was cut off in print. HTML was not affected (MathJax scrolls).

## Decision

(William Emerison Six <billsix@gmail.com>, 2026-11-20.) The one-blade-per-line layout went into
`_repr_latex_` itself, behind a width threshold, so plain cell outputs and Jupyter get it too;
short values keep printing on one line. It is in `CHANGELOG.md` `[Unreleased]` (a long value's
`_repr_latex_` text changed).

## What was measured

`tools/check_math_overflow.py` (new) reads `book/docs/_build/latex/geometry2.log` and `.tex`, sorts
each `Overfull \hbox` into equation, table or text, and lists the equations and tables more than
10pt too wide. Before the work: **234**, all but one from computed notebook output: 136 product
tables (`show_mult`), about 50 values, 51 cancellation lines (the new `show_difference` lines made
some of those). The one hand-written case was `geometric-product.rst`, whose multi-line
`.. math::` blocks had no `\\`, so LaTeX set each on one line.

## What changed

- **`src/gacalc/base.py`:** `LATEX_LINE_WIDTH` (60 visible characters) and the helpers
  `latex_visible_length` (characters a LaTeX string shows: commands, braces, `_`, `^` not
  counted), `latex_rows` (whole tokens into rows), `latex_broken` (one line, or an `aligned` block
  of rows with the later rows indented), `term_tokens` / `signed_term_latex`. `blade_dict_latex`
  (so `_repr_latex_`) takes a `width` argument. A value that fits is rendered exactly as before.
  A longer one breaks between the monomials of each coefficient and between blades. A single term
  wider than a row whose numerator is a sum is written `\frac{1}{D} * (n_1 + n_2 + …)`, so the
  numerator can break.
- **`src/gacalc/nbdisplay.py`:** the cancellation lines break their left terms, right terms and
  residual (the residual term by term too). `show_mult`'s "We want to evaluate" line breaks. The
  product table has three columns (`Left Component | * Right Component | = Product`, the
  operators in the cells, `_with_operator`) instead of five. Sphinx's tabulary gave each column
  a fifth of the page, two of them to `*` and `=`. Its cells break past `TABLE_CELL_WIDTH` (24).
- **`book/docs/geometric-product.rst`:** both equations got `&` and `\\`.
- **`entrypoint/docs.sh`** runs `tools/check_math_overflow.py` after `make latexpdf` as a report
  (the build still succeeds) and copies `geometry2.log` to `output/gacalc/`.
  `tasks/reference/book-and-docs-pipeline.md` ("Notebook output in the PDF") records the mechanism.

## Result, and what is still too wide

Four builds measured it: 234, then 85 (line breaking), 89 (three-column tables, fraction split;
the tables' rows were still too wide), then **73**: one equation and the rows of two tables. All
three are single terms wider than the space they are in, which no break between terms can fix:

- `displaymv.py`, "A bivector times its inverse" and "A bivector and its dual" (36 overfull rows
  each, about 100–160pt): the product table's terms carry the 3D denominator
  `(e₁f₂ − e₂f₁)² + (e₁f₃ − e₃f₁)² + (e₂f₃ − e₃f₂)²`, about 70 characters, inside a third of the
  page.
- One 29pt equation: a `\sqrt{…}` of a long 3D expression (a magnitude in `displayg3measures.py`).

Fixing those means changing what the notebooks show (a name for `|B|²`, say), not how gacalc
breaks lines; that is a content decision left to the maintainer, and `check_math_overflow.py`
lists them after every build. Shrinking display math to the page width in LaTeX (the strategy's
last resort, `adjustbox`) was not added: the remaining cases are table rows and one radical, and
shrinking every display to fit would make the printed math hard to read.

## Verification

`format.sh` (ruff, ty) clean; `pytest -m "not slow"` 1404 passed (the new helpers' doctests
included); the last book build exited 0, no new Sphinx warnings, 0 `<Figure size` lines; page 416
(`displaymv.py`'s associativity check) shows both sides and the numbered cancellation broken into
rows inside the margin.
