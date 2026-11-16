# Add `show_mult` distribution tables to the book notebooks

**Completed:** 2026-11-16 (William Emerison Six <billsix@gmail.com>; done by Claude on the
`book-notebooks-teaching-style` branch)

## What was done

The book notebooks in `book/docs/notebooks/` now show the term-by-term expansion of the products
whose expansion is the point of the page, with `show_mult(a, b)`: the product to evaluate, a table
of every term of `a` times every term of `b`, and the sum. Each table has a one-line Markdown
lead-in saying what to read in it. The existing simplified-product and zero-difference cells were
kept. The teaching standard behind it is `tasks/reference/book-notebook-teaching-style.md`.

- **`show_mult` moved to `src/gacalc/nbdisplay.py`**, a display-only module (sympy and IPython, no
  matplotlib or pandas), so the book's ePiX-drawn notebooks can import it. `gacalc.nbplotutils`
  re-exports it, so `notebooks/display*.py` are unchanged. The table is now built as Markdown text by
  `product_table_markdown(a, b)` (doctested) instead of through pandas `to_markdown`, which removed
  the module's dependence on pandas and its transitive `tabulate`. `api.rst`, `CLAUDE.md`'s module
  list and `CHANGELOG.md` `[Unreleased]` name the new module.
- **The book's PDF build exposed a `show_mult` bug:** it wrapped `_repr_latex_()` output (which
  carries `$$` delimiters) in more `$`, and Sphinx puts `Math` output inside an `equation`
  environment, so lualatex stopped with "Missing } inserted". `show_mult` now strips the delimiters
  (`_math_body`) before handing LaTeX to `Math`, and writes the product with an explicit `*`.
- **The tables did not render at first.** myst-nb renders a notebook's `text/markdown` output as
  CommonMark by default, which has no tables, so both HTML and PDF showed raw `| … |` lines (the
  pandas-built table would have done the same). `book/docs/conf.py` now sets
  `nb_render_markdown_format = "myst"`, which renders those outputs with the MyST parser and the
  configured `dollarmath` extension.
- **Tables added (14 in 8 notebooks):**

  | Notebook | Concrete values | Symbolic |
  |---|---|---|
  | `bootstrap-product.py` | `a * b` (new section "The same product, term by term") | `a_symbolic * b_symbolic` |
  | `bootstrap-projection-from-product.py` | `b * a`; `(b ∧ a) * a⁻¹` | `b_symbolic * a_symbolic` |
  | `bootstrap-rotation-from-product.py` | `v * unit_product`; the sandwich as `R * v`, then `(R * v) * R⁻¹` | `v_symbolic * unit_product` |
  | `geometric-product.py` | — | `a * R` |
  | `levels-of-abstraction.py` | — | `a * b` |
  | `product-from-projection.py` | — | `b * a` |
  | `rotation-from-vectors.py` | — | `a_hat * b_hat` (the angle-difference identities) |
  | `three-dimensions.py` | — | `p * q` (nine rows in 𝒢₃) |

## Judgment calls

- **"First product of each kind" was read per notebook, and only where the expansion is the page's
  point.** `bootstrap-rotation-from-product.py` does not table `a_hat * b_hat` (vector × vector is
  `bootstrap-product.py`'s subject, and the normalized coordinates carry `√5`); it tables the
  rotation products instead. The quarter turn `b * e_12` in `bootstrap-product.py` got no table,
  to keep that page at two.
- **The Part I notebooks set no concrete values** (they are fully symbolic), so they got one
  symbolic table each rather than "concrete, then symbolic".
- **The symbolic table in `bootstrap-rotation-from-product.py` keeps the concrete rotor**
  (`v_symbolic * unit_product`), as the notebook's own symbolic sandwich check does, so each row is
  short and the result reads as a combination of `v_1` and `v_2`.
- The edits were made by `tasks/adhoc/book-notebooks-show-mult-tables/insert_tables.py` (anchor
  must occur once; idempotent, proven by a second run with no diff).

## Verification

- `ruff check`, `ruff format --check` and `ty check` over `book/docs/notebooks` and `src/gacalc`
  clean; the `nbdisplay` doctests and `tests/test_nbplotutils.py` pass.
- Every edited notebook ran to completion (the ePiX ones inside the `gacalc` image).
- The book built (HTML and PDF) inside the image, the tables rendered as tables in both.
- `entrypoint/format.sh` in the image passed; `pytest -m "not slow"` in the image: 1364 passed.
