# Check the geometry survey's lesson page numbers against the real textbook

**Status:** blocked
**Priority:** 8 (blocked)
**Difficulty:** 1
**Created:** 2026-11-21 (William Emerison Six <billsix@gmail.com>), from
`tasks/archive/2026/11/21/book-opening-vectors-supersede-geometry-types.md`.
**Blocked on:** the maintainer's copy of Pearson *Geometry: Common Core* (2012).
**Recheck:** the maintainer has the book at hand; "cleared" = `/source-coverage pearson-geo --unverified-pages` shows no rows.

## BLUF

`tasks/reference/high-school-geometry-objects.md` cites each lesson of the textbook with a page number.
The numbers came from a school's public curriculum map that names neither the book nor the edition (its
13-chapter outline matches the book); they are where each lesson's exercises begin. Check them, and the
ISBN, against the maintainer's copy, and correct the survey. Done = the survey's page numbers and edition
note are confirmed or corrected.

**Since 2026-11-27 the same numbers are also in `tasks/sources/pearson-geo.toml`**, the textbook's
outline, one `page` per lesson with `page_verified = false`. `/source-coverage pearson-geo
--unverified-pages` lists the 31 of them. When the maintainer reads a page from his copy, correct
`page` (the outline's pages are where a lesson's exercises begin; replace each with the lesson's
first page and drop the file banner's note once all are), set `page_verified = true`, and fix the
survey's "(lesson, exercises p.)" cell to match. Also to confirm from the copy, flagged in the
outline's `note` fields: the lesson numbers (given only where the curriculum map gave one), the
four lessons his typed table of contents lacked (1-6, 1-7, 1-8, 3-1), and two titles ("right
angles and trigonometry", "proportions in right triangles"). Entry IDs never change with these
corrections.
