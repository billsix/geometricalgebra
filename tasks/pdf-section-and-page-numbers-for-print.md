# Make the book's cross-references usable in print: section numbers and page numbers in the PDF

**Status:** proposed — needs go-ahead (investigation done; the config changes are known)
**Priority:** 3
**Difficulty:** 2
**Created:** 2026-10-08 (William Emerison Six <billsix@gmail.com>)

## BLUF

The book's internal links (`:ref:`/`:doc:`, 23 uses across `book/docs/*.rst`) work as hyperlinks
in HTML and in the PDF viewer, but a **printed** PDF loses them: the link text carries neither a
section number nor a page number. The maintainer asked (2026-10-08) whether Sphinx can put section
numbers or page numbers in the text. **It can, with two config changes and one toctree option** —
verified against the installed Sphinx 8.2.3 source (`sphinx/writers/latex.py`,
`sphinx/domains/std/__init__.py`). "Done" = a `make docs` PDF where every internal reference reads
like "see Proof: Rotate (Section 2.3, page 41)", and HTML shows the same section numbers.

## What Sphinx offers (verified 2026-10-08)

1. **Page numbers on every cross-reference in the PDF:** `latex_show_pagerefs = True` in
   `book/docs/conf.py`. The LaTeX writer then appends ` (page N)` (via `\hyperpageref`) after each
   `:ref:`/`:doc:` link — `writers/latex.py`, the `visit_reference` branches that check
   `self.config.latex_show_pagerefs`. Default is `False`. HTML is unaffected.
2. **Section numbers in the text (HTML and PDF):** add `:numbered:` to the main toctree in
   `book/docs/index.rst`. Chapters/sections get "1", "1.2", … in both builders, and `:numref:` can
   then name a section by number — `:numref:` on a section target works **without** `numfig`
   (`domains/std/__init__.py`: the `figtype != 'section' and numfig is False` guard skips only
   non-section targets). The rendered text follows `numfig_format["section"]` (default
   `"Section %s"`); a custom template like `"Section %s"` or `"§%s"` is a one-line config.
   - **Caveat — the proof pages:** `proof-rotate.rst`, `proof-rotate-from-a-to-b.rst`,
     `proof-projection.rst` sit in their chapter's own toctree (not `index.rst`'s), so they get
     numbered as subsections of that chapter — which is what we want, but check the depth
     (`:numbered: 2` limits how deep numbers go; `numfig_secnum_depth` controls the figure/equation
     prefix depth).
3. **Figure / table / listing numbers:** `numfig = True` (plus `numfig_format`) numbers figures
   ("Fig. 2.1") and lets `:numref:` reference them. The book's ePiX figures currently have no
   captions and are referenced only by position in the prose; numbering them is optional but is
   the same switch the equation-numbering task needs (`tasks/number-equations-with-labels.md`).
4. **External URLs in print:** `latex_show_urls = "footnote"` prints each external link's URL as
   a footnote in the PDF (default `"no"`: the URL is invisible on paper). Same print concern, same
   file; include it unless the maintainer objects.

## Plan

1. `book/docs/conf.py`: `latex_show_pagerefs = True`, `latex_show_urls = "footnote"`,
   `numfig = True`, and a `numfig_format` with the wording the maintainer wants (decide once:
   "Section %s" vs "§%s"; "Fig. %s"; "Eq. %s" — shared with the equation task).
2. `book/docs/index.rst`: `:numbered:` on the main toctree.
3. Convert the 23 `:ref:`/`:doc:` uses where a number helps the printed reader to
   `:numref:` (or keep `:ref:` and rely on the ` (page N)` suffix — `:ref:` already prints the
   target's title, so most links need nothing more than the page suffix). Rule of thumb: a
   "see the proof in …" link → `:numref:` + page; an inline mention of a chapter by name → leave.
4. `make docs`; read the PDF's cross-references and the HTML's section numbers. Record the chosen
   wording in `tasks/reference/book-and-docs-pipeline.md` (one bullet under the build settings).

## Context

- `book/docs/conf.py` today sets none of `numfig` / `latex_show_pagerefs` / `latex_show_urls`
  (grep 2026-10-08); the toctree in `index.rst` is un-numbered. The LaTeX engine is lualatex
  (`latex_engine = "lualatex"`) — none of the options above depend on the engine.
- modelviewprojection's book (the template this book was modelled on,
  `tasks/reference/book-and-docs-pipeline.md`) sets none of these either, so this is new ground,
  not a port.
- Related: `tasks/number-equations-with-labels.md` (equation numbers share `numfig`/
  `numfig_format`) and `tasks/archive/2026/10/09/line-numbers-in-source-listings.md` (the other print-readability
  item from the same 2026-10-08 list).

## Open questions

None — the wording choices in step 1 are routine; pick "Section %s" / "Fig. %s" / "Eq. %s" unless
told otherwise.
