# Number the book's displayed equations, LaTeX-style, and reference them by number

**Status:** proposed — needs go-ahead
**Priority:** 4
**Difficulty:** 2
**Created:** 2026-10-08 (William Emerison Six <billsix@gmail.com>)

## BLUF

The maintainer wants displayed equations to carry numbers "like happens in TeX" (2026-10-08) —
`(2.3)` in the margin, referenced as "by (2.3)" from the prose. Today the book has 18
`.. math::` directives across five pages and **zero** `:label:`s, so nothing is numbered and
nothing can be referenced. "Done" = every displayed equation a proof later refers to has a
`:label:` and is cited with `:eq:`; the numbering is per-chapter (`(2.3)`) in both HTML and PDF;
`make docs` is green with no "undefined label" warnings.

## How Sphinx numbers equations (verified against Sphinx 8.2.3, 2026-10-08)

- A `.. math::` block with `:label: name` is numbered in both builders and `:eq:\`name\`` renders
  the number as a link, `(3)` by default (`sphinx/domains/math.py`: `math_eqref_format`, default
  `"({number})"`).
- `math_number_all = True` numbers **every** displayed equation, labelled or not — this is the
  "like TeX" behaviour (`equation` environment numbers everything). Recommended, so the reader can
  point at any line; add `:label:` only to the ones cited.
- Per-chapter numbers `(2.3)` instead of running `(7)`: `numfig = True` **and** `math_numfig = True`
  (the latter is the default; it only takes effect with `numfig`). The chapter prefix depth is
  `numfig_secnum_depth` (default 1 = chapter). This is the same `numfig` switch
  `tasks/pdf-section-and-page-numbers-for-print.md` turns on — do these two tasks together or
  in sequence.
- Notebook pages (myst_nb, `book/docs/notebooks/*.py`) use `$$ … $$` dollar-math; MyST labels
  them as `$$ … $$ (label)` and `myst_dmath_allow_labels` is on by default (`conf.py` enables
  `dollarmath`), so the same numbering reaches the executed notebooks.

## Current state

| File | `.. math::` blocks | labels |
|---|---|---|
| `book/docs/proof-rotate-from-a-to-b.rst` | 6 | 0 |
| `book/docs/blade-square-sign.rst` | 4 | 0 |
| `book/docs/geometric-product.rst` | 3 | 0 |
| `book/docs/proof-projection.rst` | 3 | 0 |
| `book/docs/proof-rotate.rst` | 2 | 0 |

Several of these are multi-line `align`-style derivations (the `proof-rotate.rst` chain of `&=`
steps). In LaTeX an `align` numbers every line; decide per block whether the whole derivation
gets one number (wrap as a single equation, or `:nowrap:` with an explicit `\begin{align*}` and a
`\tag`) or each line gets its own.

## Plan

1. `book/docs/conf.py`: `math_number_all = True`, `numfig = True` (if not already from the
   page-numbers task), `math_eqref_format = "Eq. ({number})"` or plain `"({number})"` —
   maintainer's taste; TeX convention is plain `(2.3)`.
2. Walk the 18 blocks: give a `:label:` to each equation the prose refers back to (the rotation
   formula `\vec{r}(\vec{a}; \theta)` in `proof-rotate.rst` is cited from `geometric-product.rst`,
   `proof-rotate-from-a-to-b.rst` and `proof-projection.rst` — the obvious first label). Label
   names: `eq-<page>-<what>`, e.g. `eq-rotate-formula`.
3. Replace the prose's "the formula above" / "the chapter-ending formula of Proof: Rotate" with
   `:eq:` references where a number is clearer than a name.
4. `make docs`; check the HTML (MathJax renders the numbers at the right margin) and the PDF.
   Note the convention (label naming, when to label) in `tasks/reference/book-outline.md` ›
   "Notation & prose conventions for proof pages".

## Open questions

None.
