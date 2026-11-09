# Book: broken cross-references and author-facing notes

**Created:** 2026-11-09 · **Completed:** 2026-11-09
**Source:** `tasks/review/2026/11/08/repo-review.md` §3.2, §3.5

## What changed

- **The cross-references.** Each now cites a page that has the content.
  - `blade-square-sign`'s "In geometric-product you met … `e₁₂` squares to −1" is now true:
    `geometric-product` states it (in `tasks/archive/2026/11/09/book-restructure-parts.md`'s commit).
  - `rotation-from-vectors` cites `product-from-projection` for the dot + wedge split, and
    `proof-cross` cites `proof-projection-3d` for the 3D reduction (both in the restructure's
    commit).
  - `proof-rotate-from-a-to-b`'s "the same move does the work later in projection" now cites
    `proof-projection`.
- **The author notes:**
  - `index.rst`'s "This is the skeleton" (restructure commit);
  - `proof-projection`'s "As promised in the outline" (restructure commit);
  - `relative-graph-paper`'s visible "Placeholder — content to come" line, now a hidden `TODO prose`
    comment above the drafted subsection;
  - `projection-rejection-3d`'s stale TODO, which waited on a restructure that is done. It now
    points at `proof-projection-3d` (restructure commit, since that file moved there).
- **Draft notes.** No page has had the maintainer's voice pass (the maintainer, 2026-11-09), so every
  agent-written page with prose now opens with ".. note:: Draft. The prose is agent-drafted; the
  maintainer's voice pass is pending." 11 pages gained the note; 6 already had it (`rotate`,
  `geometric-product`, `proof-projection`, `proof-cross` and `projection-rejection-3d` gained it in
  the restructure's or the rotate chapter's commits, which carry those files). The placeholder pages
  and `api`/`index` have no prose to mark.

**Notation edits carried here.** `proof-rotate-from-a-to-b.rst` and `rotation-graph-paper.rst` also
carry the batch's notation edits (`tasks/archive/2026/11/09/book-notation-sweep.md`) on the same
lines.

## Verification

- The scratch HTML build described in the restructure's done-record: no undefined documents or
  labels.
- `grep -L "Draft\."` over `book/docs/*.rst` lists only the placeholder pages and `api`/`index`.
