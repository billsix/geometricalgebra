# Book: GFDL headers on the remaining pages, `api.rst` coverage, the "deformed graph paper" wording

**Status:** proposed — needs go-ahead
**Priority:** 6
**Difficulty:** 2
**Created:** 2026-11-09
**Source:** tasks/review/2026/11/08/repo-review.md §3.6

## BLUF

Finish the book's smaller §3.6 items. Done means:
- every `book/docs/*.rst` page carries the GFDL-1.3 header;
- `api.rst` documents `gacalc.standardposition` and `gacalc.nbplotutils`;
- `rotation-graph-paper.rst` no longer calls a rotation "deformed";
- `make docs` builds with no new warnings.

## Context

Read first: `tasks/reference/book-and-docs-pipeline.md` and `tasks/reference/book-outline.md`. Re-checked
2026-11-09:

- **Licence headers:** 12 of the 32 `.rst` pages carry the GFDL text (`grep -li "free documentation"
  book/docs/*.rst`); 20 don't. Copy the header from a page that has it. The book-wide pass was first
  proposed in `tasks/archive/2026/08/03/port-rotation-explanation-from-mvp.md` and never tracked.
- **`api.rst`** documents neither `gacalc.standardposition` (cited by `proof-projection`) nor
  `gacalc.nbplotutils`. The generated `g1`–`g5` are absent too, probably on purpose; leave them out
  unless `book-and-docs-pipeline.md` says otherwise.
- **`book/docs/rotation-graph-paper.rst:65`** says "a rotation is **deformed graph paper**", but a
  rotation is rigid. Choose a word such as "turned" in the maintainer's voice (model:
  github.com/billsix/modelviewprojection's RST). The page's sentence-case title also differs from every
  other page's Title Case.
- Already fixed, so dropped: `proof-cross` now hangs off `projection-rejection-3d.rst`'s toctree.

## Plan

- [ ] Add the header to the 20 pages, then check `grep -Li "free documentation" book/docs/*.rst`
  prints nothing.
- [ ] Add the two modules to `api.rst`.
- [ ] Reword "deformed" and title-case the heading. Check for cross-references to the old title.
- [ ] `make docs`, comparing its warnings with the previous build's.

## Open questions

None.
