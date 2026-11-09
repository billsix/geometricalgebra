# Book: broken cross-references and author-facing notes

**Status:** proposed — needs go-ahead (approved in session 2026-11-09; in progress)
**Priority:** 3
**Difficulty:** 2
**Created:** 2026-11-09
**Source:** `tasks/review/2026/11/08/repo-review.md` §3.2, §3.5

## BLUF

Fix the book's cross-references to content the cited page doesn't contain, remove author notes from
reader-facing text, and mark every agent-written page as a draft, since none has had the
maintainer's voice pass (the maintainer, 2026-11-09). Some of these are settled by the restructure
(`tasks/book-restructure-parts.md`); this task does the rest.

## Context

From review §3.2/§3.5:

- **Cross-references:**
  - `blade-square-sign` claims `geometric-product` showed that `e₁₂` squares to −1;
  - `rotation-from-vectors` claims `geometric-product` gave the dot + wedge split;
  - `proof-cross` cites `projection-rejection-3d` for the 3D reduction;
  - `proof-rotate-from-a-to-b` cites `projection` for the standard-position move.
- **Author notes:**
  - `index.rst`'s "This is the skeleton";
  - `proof-projection`'s "As promised in the outline";
  - `relative-graph-paper`'s "Placeholder" line above drafted content;
  - `projection-rejection-3d`'s stale TODO.
- **Draft marking:** only 4 pages carried the "agent-drafted" note.

## Plan

- [ ] Make each cross-reference true: add `e₁₂ * e₁₂ = −1` to `geometric-product`, and point the
  others at the page that has the content.
- [ ] Remove or hide the author notes.
- [ ] Add the Draft note to every agent-written page.
- [ ] Gate: the RST parses (docutils); `make docs` needs the full image.

## Open questions

None.
