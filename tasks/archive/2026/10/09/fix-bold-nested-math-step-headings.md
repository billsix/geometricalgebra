# Fix the two bold step headings that print their `:math:` source literally

**Status:** complete
**Completed:** 2026-10-09
**Priority:** 3
**Difficulty:** 1
**Created:** 2026-10-09 (William Emerison Six <billsix@gmail.com>)

## BLUF

Two run-in step headings in `book/docs/proof-rotate-from-a-to-b.rst` wrapped a `:math:` role
inside `**bold**`. reStructuredText does not nest inline markup, so the reader saw the literal
``:math:`\vec{a}``` in the HTML and PDF instead of a typeset vector. Both headings now split the
bold *around* each role (the pattern `proof-projection.rst` already used), words unchanged, and
the rendered book shows the math.

## What was done

Two lines in `book/docs/proof-rotate-from-a-to-b.rst`, markup only:

- "The plan: three rotations" / step 1:
  `**Step 1 — swing :math:`\vec{a}` onto the x-axis.**` → `**Step 1 — swing** :math:`\vec{a}`
  **onto the x-axis.**`
- step 2 (two roles): `**Step 2 — in standard position, rotate :math:`\vec{e}_1` onto
  :math:`\vec{b}'`.**` → `**Step 2 — in standard position, rotate** :math:`\vec{e}_1` **onto**
  :math:`\vec{b}'`.` (the sentence-final period is left plain, since no word follows the last
  role to carry the bold).

This is the split `proof-projection.rst` lines ~164/170 (`**First, swing the** :math:`xy`
**shadow onto the x-axis.**`) already used, confirmed correct there earlier this session.

## Gate

`make docs` green; the rendered `output/gacalc/html/proof-rotate-from-a-to-b.html` shows **0**
literal `:math:`/`\vec{...}` role strings (it showed 2 before), and the PDF typesets the two
vectors. No other page changed.

## Open questions

None.
