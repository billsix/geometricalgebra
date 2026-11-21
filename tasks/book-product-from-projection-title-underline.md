# Fix the short title underline in product-from-projection.rst

**Status:** proposed — needs go-ahead
**Priority:** 3
**Difficulty:** 1
**Created:** 2026-11-21 (William Emerison Six <billsix@gmail.com>), seen in `make docs` while finishing
`tasks/archive/2026/11/21/book-opening-vectors-supersede-geometry-types.md`.

## BLUF

`make docs` warns "Title underline too short" at `book/docs/product-from-projection.rst:27`: the heading
``Where :math:`\vec{\mathbf{a}}` lands`` is 31 characters of source and its `---` underline is 27.
Lengthen the underline to the source length. Done = `make docs` no longer prints that warning (check the
other headings with a `:math:` role while there).
