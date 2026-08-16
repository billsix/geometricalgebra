# Rename the book from "Plotting On Crappy Graph Paper" to "Geometry 2"

**Status:** proposed — needs go-ahead. Created 2026-08-16 (William Emerison Six <billsix@gmail.com>).
**Priority:** 4
**Difficulty:** 2

## Goal

Rename the Sphinx book from **"Plotting On Crappy Graph Paper"** to **"Geometry 2"** — framed like
the Algebra 1 / Algebra 2 progression a student already knows (Bill, 2026-08-16), so the title itself
says "this is the next course after the geometry you took."

## Where the title lives (grepped 2026-08-16)

**Authoritative — the book's own title (must change):**

- `book/docs/conf.py:9` — `project = "Plotting On Crappy Graph Paper"`. This flows into the HTML site
  title and the PDF title page. **Check the rest of `conf.py`** too — `html_title`, `latex_documents`
  tuples, and any `author`/`html_short_title` that may embed the title (verify before editing; grep
  found only `project`, but the LaTeX title is often derived).
- `book/docs/index.rst:1` — the landing-page H1 `Plotting On Crappy Graph Paper` and its `====`
  underline. **The underline length must be updated to match the new, shorter title** ("Geometry 2"
  is 10 chars) or the rst build errors.

**References to the title (update the live ones; leave archives historical):**

- `CLAUDE.md:624` — the `make docs` bullet names the book.
- `tasks/reference/book-outline.md` — the doc's own H1 title + body references throughout.
- `tasks/reference/book-and-docs-pipeline.md:3` — names the book.
- `tasks/reference/openstax-math-pedagogy.md:1, 408, 442` — names the book (line 408 even puns on the
  "graph paper" title — reword, don't just substitute, since the joke dies with the rename).
- `tasks/prove-blade-square-sign-equals-pseudoscalar-squared.md:65` — names the book (Book chapter
  section).
- `tasks/archive/2026/08/02/sphinx-book-pipeline.md:9` — **archived; leave as-is** (historical record
  of what it was named when built), unless Bill wants a note.

`README.md` does **not** mention the title (grep clean) — nothing to change there.

## Plan

- [ ] Change `conf.py` `project` (and any other title-bearing setting found there) to "Geometry 2".
- [ ] Change `index.rst` H1 **and fix the underline length**.
- [ ] Update the live references above (CLAUDE.md, the three `tasks/reference/` docs, the active task
      doc); reword the graph-paper pun in `openstax-math-pedagogy.md:408` rather than blind-substitute.
- [ ] Rebuild to verify: `make docs` (container) — or a host `sphinx-build` with notebooks disabled —
      and confirm the new title shows in the HTML header and the rst still builds warning-free for the
      landing page.

## Open questions

1. **Keep the old evocative name as a subtitle?** "Plotting On Crappy Graph Paper" carried the book's
   whole conceit (relative/tilted graph paper, canonical-form-over-decimals). Options: (a) drop it
   entirely — clean, "Geometry 2" only; (b) keep it as a **subtitle/tagline** — `Geometry 2` as the
   title with "Plotting on Crappy Graph Paper" underneath, so the hook survives. Recommend **(b)** — the
   old name is doing pedagogical work the new one doesn't. Needs Bill's call.
2. **Any front-matter beyond the title?** e.g. a one-line description in `conf.py`/`index.rst` that
   should now mention "the sequel to the geometry course" framing. Minor; do only if Bill wants it.
