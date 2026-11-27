# The first external source outline: the Pearson geometry textbook

**Status:** done 2026-11-27 — staged; the archive move is owed after the work commit
**Priority:** 4
**Difficulty:** 3
**Created:** 2026-11-27 (William Emerison Six <billsix@gmail.com>)

## What this did

Put the outline of Charles et al., *Geometry: Common Core* (Pearson, 2012) into
`tasks/sources/pearson-geo.toml`, tagged the book pages that already cover one of its entries, and
removed the hand-kept "Where" column from `tasks/reference/high-school-geometry-objects.md`. This
repository is the first user of the external-source-outline convention of
github.com/billsix/runClaudeInContainer (its `tasks/reference/external-source-outlines.md`; the
design and the maintainer's five decisions are in that repository's task
`external-source-outlines-and-coverage-tracking.md`).

The reason: the maintainer reads that textbook for topics to connect to geometric algebra, over
months, and wants to see at any time which of them the book has covered, without keeping a list by
hand.

## What was built

- **The outline, 127 entries:** 12 chapters, their lessons, and the objects the reference doc
  already listed.
  - Chapter and lesson titles are the table of contents the maintainer typed from his own copy
    (`fromPearsonbook.txt`, an untracked file in his checkout, which he had deleted once every
    line of it was confirmed present in the outline), in his lower case,
    with five spellings corrected.
  - Four lessons that the reference doc cites and his table of contents lacks (1-6, 1-7, 1-8, 3-1)
    are entered with a note saying so.
  - Lesson numbers and page numbers come from the public curriculum map the reference doc used. A
    number is given only where the map gives one. A page is where the lesson's exercises begin.
    Every page has `page_verified = false`.
  - Entry IDs are short names (`within-triangles/medians/median`), not lesson numbers, so that a
    corrected number never changes an ID.
- **Tags:** `covers:` comments above the sections of eight book pages
  (`geometry-from-vectors`, `product-from-projection`, `vector-addition`, `reflection`, `rotate`,
  `relative-graph-paper`, `trigonometry`, `orthogonal`), each checked against the page's text.
  Topics a page only names (the circle on `rotate`, the altitude on `projection`, the angle
  bisector, similar polygons) were not tagged; the outline entry carries a note.
- **A task citation:** `tasks/affine-flats-lines-planes-from-points.md` now names the plane and
  intersection entries on a `**Source:**` line, so they report as planned.
- **Docs:** the pointer in `CLAUDE.md`; the reference doc's intro and tables.

## Verification

`python3 <the shared tool> source_coverage.py` from the repo root, 2026-11-27: 127 entries, 30
covered, 2 planned, 95 not addressed, no problem lines; `--cite
pearson-geo/within-triangles/medians/median` printed the citation with lesson 5-4 and page 312
marked unchecked. The book was not rebuilt: the tags are reStructuredText comments, which do not
render.

## Left for the maintainer

- **Page numbers and lesson numbers** need his copy: `/source-coverage pearson-geo
  --unverified-pages` lists the 31 pages. Two titles are flagged in the outline's notes
  ("right angles and trigonometry", "proportions in right triangles").
- **Decisions.** Only the entries the book already covers are marked `want`. Everything else is
  `undecided` until he says.
- **The two prose citations** of the textbook (`book/docs/geometry-from-vectors.rst`,
  `book/docs/product-from-projection.rst`) are still typed by hand. `source_coverage.py --cite`
  prints the wording for an entry; a Sphinx bibliography fed from the outline was not built.
