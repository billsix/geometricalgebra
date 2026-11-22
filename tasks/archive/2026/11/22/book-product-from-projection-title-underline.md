# Fix the short title underline in product-from-projection.rst

**Status:** done 2026-11-22
**Created:** 2026-11-21 (William Emerison Six <billsix@gmail.com>), seen in `make docs` while finishing
`tasks/archive/2026/11/21/book-opening-vectors-supersede-geometry-types.md`.

## What this did

`make docs` warned "Title underline too short" at the heading `Where :math:`\\vec{\\mathbf{a}}` lands` in
`book/docs/product-from-projection.rst`. The underline was 27 characters against a 36-character source line
(docutils counts the source, roles included). Three other headings with a `:math:` role had the same
fault, so all four underlines now match their heading source length:

- `book/docs/product-from-projection.rst`: "Where a lands"
- `book/docs/proof-projection.rst`: "Rotating b onto the x-axis"
- `book/docs/bootstrap-rotation-from-projection.rst`: "The first triangle" and "The second triangle"

## Verification

A scan of every `book/docs/*.rst` for an underline shorter than its heading source found exactly those
four. `make docs` then built HTML and PDF (exit 0) with no underline warning in its log.
