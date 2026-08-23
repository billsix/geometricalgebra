# Rename the book from "Plotting On Crappy Graph Paper" to "Geometry 2"

**Status:** complete
**Completed:** 2026-08-23 (William Emerison Six <billsix@gmail.com>). Renamed to "Geometry 2";
old name dropped entirely (Q1 → option (a), Bill's call 2026-08-23). Q2 (extra front-matter) skipped.
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

- [x] Change `conf.py` `project` to "Geometry 2" (line 9; it was the only title-bearing setting —
      no `html_title`/`latex_documents`/`html_short_title`, so the LaTeX title derives from `project`).
- [x] Change `index.rst` H1 to "Geometry 2" and shrink the underline to 10 `=` (verified title==underline).
- [x] Update the live references: `CLAUDE.md:660`, `tasks/reference/book-and-docs-pipeline.md:3`,
      `tasks/reference/book-outline.md:1`, `tasks/reference/openstax-math-pedagogy.md:1,442`, and
      `tasks/docstrings-for-sphinx.md:21` (this last one was not in the original grep list but named the
      title). Reworded the pun at `openstax-math-pedagogy.md:408` to "For a book built around relative
      graph paper, this gap is the opportunity." — keeps the point (the book's conceit is graph paper)
      without the dead title-joke. `prove-blade-square-sign-…md:65` no longer names the title (drifted);
      nothing to change there. Left `tasks/archive/2026/08/02/sphinx-book-pipeline.md` historical.
      Left the many *"relative graph paper"* mentions in notebooks/chapters alone — that's the
      pedagogical concept, not the title.
- [ ] Rebuild verify with `make docs` NOT run (containerized/heavy; nbsphinx executes notebooks). The
      one build-breaking risk — the rst underline — was verified by length match instead. Worth a
      `make docs` sanity pass next time the book is built anyway.

## Open questions

1. **Keep the old evocative name as a subtitle?** "Plotting On Crappy Graph Paper" carried the book's
   whole conceit (relative/tilted graph paper, canonical-form-over-decimals). Options: (a) drop it
   entirely — clean, "Geometry 2" only; (b) keep it as a **subtitle/tagline** — `Geometry 2` as the
   title with "Plotting on Crappy Graph Paper" underneath, so the hook survives. Recommend **(b)** — the
   old name is doing pedagogical work the new one doesn't. Needs Bill's call.
2. **Any front-matter beyond the title?** e.g. a one-line description in `conf.py`/`index.rst` that
   should now mention "the sequel to the geometry course" framing. Minor; do only if Bill wants it.
