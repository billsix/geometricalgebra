# Scaffold the book's placeholder documents (.rst chapters + notebook stubs)

**Status:** proposed — **deferred; blocked on Bill's detailed review of
`tasks/reference/book-outline.md`.** Do not start until Bill has reviewed the outline
and firmed up the structure.
**Priority:** 5
**Difficulty:** 2
**Created:** 2026-08-02

## Goal

Once the book outline (`tasks/reference/book-outline.md`) is reviewed and its structure
firmed up, scaffold the **empty placeholder documents** in `book/docs/` that mirror it —
blank `.rst` chapters/sections (plus notebook stubs) wired into the Sphinx toctree — so
any section can be drafted **out of order** (per the outline's "write out of order; use
placeholders" convention). This is the book's skeleton of files; prose/graphs/notebooks
fill in later.

## Why deferred (Bill, 2026-08-02)

Bill wants to review the outline in more detail before we commit to a file layout;
scaffolding now would create files for a structure he may still reorder.

## When unblocked

- Mirror the outline's **Part I (A–I)** and **Part II** structure; one blank `.rst` per
  section, added to `index.rst`'s toctree.
- Follow the outline's media conventions: **proofs → separate `.rst`**, **coordinate
  calculations → notebook stubs** (`notebooksrc/` percent-format, per
  `book-and-docs-pipeline.md`), main docs for the coordinate-free *uses*.
- Hoist any "important early" content into its own `.rst` linked early (per the
  outline's convention).
- Keep the build green: empty placeholders must still build HTML + PDF (`make docs`).

## Related

- `tasks/reference/book-outline.md` — the structure this scaffolds (the blocker).
- `tasks/reference/book-and-docs-pipeline.md` — how the book builds.
