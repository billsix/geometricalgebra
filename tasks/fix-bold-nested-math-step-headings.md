# Fix the two bold step headings that print their `:math:` source literally

**Status:** proposed — needs go-ahead (filed 2026-10-09 on the maintainer's ask, "make a task to fix it")
**Priority:** 3
**Difficulty:** 1
**Created:** 2026-10-09 (William Emerison Six <billsix@gmail.com>)

## BLUF

Two run-in step headings in `book/docs/proof-rotate-from-a-to-b.rst` put an inline `:math:` role
inside `**bold**`. reStructuredText does not nest inline markup, so the reader sees the literal text
``:math:`\vec{a}``` in both the HTML and the PDF instead of a typeset vector. "Done" = both headings
render their math, written the way the projection page already does it (bold split around the
role), and `make docs` is green.

## Context

- **The two broken sites** (found 2026-10-09 while reading the PDF for
  `tasks/coordinate-subscripts-indices-not-xyz.md`; the rendering predates that work):
  - `book/docs/proof-rotate-from-a-to-b.rst` line ~50:
    ``**Step 1 — swing :math:`\vec{a}` onto the x-axis.**``
  - `book/docs/proof-rotate-from-a-to-b.rst` line ~76:
    ``**Step 2 — in standard position, rotate :math:`\vec{e}_1` onto :math:`\vec{b}'`.**``
  (Find them again with ``grep -nE '\*\*[^*]*:math:`[^*]*\*\*' book/docs/*.rst`` — the discovery
  that found exactly these two.) In the built HTML the literal survives verbatim
  (`output/gacalc/html/proof-rotate-from-a-to-b.html`, 2 hits); in the generated LaTeX it appears as
  ``:math:`vec\{a\}``` inside `\sphinxstylestrong{…}`.
- **Why:** docutils inline markup cannot contain other inline markup
  (https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#inline-markup-recognition-rules
  — "inline markup cannot be nested"). The `**…**` wins, and the role text inside is just characters.
- **The fix model is already in the book:** `book/docs/proof-projection.rst` lines ~164 and ~170
  write the same kind of heading as bold *around* the role — ``**First, swing the** :math:`xy`
  **shadow onto the x-axis.**`` — and render correctly (0 literal hits in its HTML). Apply the same
  split to the two sites: ``**Step 1 — swing** :math:`\vec{a}` **onto the x-axis.**`` and
  ``**Step 2 — in standard position, rotate** :math:`\vec{e}_1` **onto** :math:`\vec{b}'`.
  **(period inside the last bold)**.
- **Conventions in play:** `tasks/reference/book-outline.md` › "Notation & prose conventions for
  proof pages" (the page's symbols are `\vec{a}`, `\vec{b}`, `\vec{e}_1`; coordinates are `a_1`).
  The page is in the maintainer's voice — change only the markup, not the words.
- **Gate:** `make docs` (nested: `make -o image docs` against the existing image; see
  `tasks/reference/nested-run-and-gates.md`), then re-run the grep above (0 hits) and grep the HTML
  for `:math:` (0 hits).

## Goal

Make the two "Step N" headings on the rotate-from-a-to-b proof page typeset their vectors instead of
printing the raw `:math:` role, by splitting the bold around the role exactly as the projection page
does, without changing any wording.

## Plan

- [ ] Rewrite the two headings with the bold split around each `:math:` role.
- [ ] `make docs`; confirm the grep over `book/docs/*.rst` and over the page's HTML both return 0.
- [ ] Read the page in the PDF once (the two headings sit on the page after "The plan: three rotations").

## Notes / decisions

- Priority 3: a visible defect on a finished, reader-facing proof page; nothing depends on it, but
  it is the kind of thing a reader notices first. Difficulty 1: two lines, a known-good pattern on a
  sibling page, one gate run.

## Open questions

None.
