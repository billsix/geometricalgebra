# Show line numbers on every code listing in the book

**Status:** complete
**Completed:** 2026-10-09
**Priority:** 4
**Difficulty:** 1
**Created:** 2026-10-08 (William Emerison Six <billsix@gmail.com>)

## BLUF

The maintainer wanted every code listing in the book to show line numbers in HTML and PDF, the
way *Model View Projection* does. One `conf.py` setting does it for the notebook code cells (the
only code listings the book has today); the `literalinclude` house pattern for quoting library
source is documented for when it is first used.

## What was done

- `book/docs/conf.py`: `nb_number_source_lines = True` (next to the other `nb_*` settings), so
  myst_nb numbers every notebook code cell in HTML and the LaTeX/PDF.
- `tasks/reference/book-and-docs-pipeline.md` › "Book notebooks": a "Code listings carry line
  numbers" bullet — the setting, and the `literalinclude` pattern (`:linenos:` **and**
  `:lineno-match:` so printed numbers equal the real `src/` line numbers) for quoting library
  source later. There are **no** `literalinclude`/`code-block` directives in `book/docs/*.rst`
  yet, so that half is forward-looking.

The PDF caveat (a long numbered line wraps under the number gutter — shorten the cell rather than
fight `fancyvrb`) is recorded in the same bullet.

## Gate

`make docs` green; the rendered notebook pages carry line-number markup in the HTML, and the PDF
shows numbered cells. (`proof-projection.html` had 71 line-number markers after the change, 0 before.)

## Open questions

None.
