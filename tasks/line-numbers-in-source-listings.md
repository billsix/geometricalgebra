# Show line numbers in the book's source listings (HTML and PDF), as modelviewprojection does

**Status:** proposed — needs go-ahead
**Priority:** 4
**Difficulty:** 1
**Created:** 2026-10-08 (William Emerison Six <billsix@gmail.com>)

## BLUF

The maintainer wants every code listing in the book to show line numbers, in both the HTML and
the PDF, the way the *Model View Projection* book does (2026-10-08). "Done" = notebook code
cells and any `literalinclude`/`code-block` in `book/docs/` render with line numbers in
`make docs`'s HTML and PDF.

## Context — where code appears in this book, and the switch for each

Unlike modelviewprojection, this book has **no `literalinclude` yet** (grep 2026-10-08): its
code reaches the page through two routes, each with its own line-number switch.

1. **Executed notebook cells** (`book/docs/notebooks/*.py`, rendered by myst_nb) — the main
   route. myst_nb has a config flag **`nb_number_source_lines = True`** (`myst_nb/core/config.py`
   field `number_source_lines`, myst_nb 1.4.0 in the sandbox; default `False`) that sets `linenos`
   on every code cell's literal block. Sphinx's LaTeX writer honours `linenos` on literal blocks
   (`sphinx/writers/latex.py`, `visit_literal_block`), so the PDF gets them too — one line in
   `book/docs/conf.py`.
2. **Source quoted from the library** — none today, but the book will quote `src/gacalc/` through
   the doc-region markers (`# doc-region-begin <name>` / `# doc-region-end <name>`, see
   `tasks/reference/code-generator-architecture.md` §6) exactly as modelviewprojection does. The
   mvp pattern to copy verbatim (`modelviewprojection/book/docs/ch13.rst`):

   ```rst
   .. literalinclude:: ../../src/gacalc/transforms.py
      :language: python
      :start-after: doc-region-begin translate signature
      :end-before: doc-region-end translate signature
      :linenos:
      :lineno-match:
      :caption: src/gacalc/transforms.py
   ```

   `:linenos:` turns numbers on; **`:lineno-match:` makes them the file's real line numbers** (not
   1-based per excerpt), which is what makes a printed listing navigable back to the source. Record
   this as the house pattern in `tasks/reference/book-and-docs-pipeline.md` so every future include
   carries both options.
3. **Hand-written `.. code-block::`** — none today; when one appears it takes `:linenos:` directly.

The `api.rst` autodoc pages show signatures and docstrings, not source, so they are out of scope
(the `sphinx.ext.viewcode` "[source]" links already show numbered source in HTML).

## Plan

1. `book/docs/conf.py`: `nb_number_source_lines = True` (next to the other `nb_*` settings).
2. `tasks/reference/book-and-docs-pipeline.md`: add the `literalinclude` house pattern above
   (with `:linenos:` + `:lineno-match:`) under a "Quoting library source" bullet.
3. `make docs`; confirm numbers in a notebook page in both HTML and the PDF (the first
   notebook with real code is `book/docs/notebooks/proof-projection.py`).

Caveat for step 3: in the PDF, long numbered lines wrap under the number gutter; if a cell line
exceeds the text width, shorten the cell rather than fighting `fancyvrb`.

## Related

- `tasks/mark-basis-constants-for-doc-regions.md` — the generator-side marker gap that would let
  the book (and mvp) quote the basis constants with the same pattern.
- `tasks/pdf-section-and-page-numbers-for-print.md`, `tasks/number-equations-with-labels.md` —
  the other print-readability items from the same list.

## Open questions

None.
