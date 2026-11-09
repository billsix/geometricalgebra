# Rename the book from "Plotting On Crappy Graph Paper" to "Geometry 2"

**Created:** 2026-08-16 · **Completed:** 2026-08-23

Renamed the Sphinx book to **"Geometry 2"**, framed like the Algebra 1 / Algebra 2 progression a
student already knows (the maintainer, 2026-08-16), so the title says "this is the next course after
the geometry you took."

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-08-23)

- **The old name was dropped entirely** (option (a)). The alternative, keeping "Plotting On Crappy
  Graph Paper" as a subtitle because it carried the book's conceit (relative/tilted graph paper,
  canonical form over decimals), had been recommended and was declined.
- **No extra front matter** (e.g. a "sequel to the geometry course" line) was added.

## What changed

- `book/docs/conf.py`: `project = "Geometry 2"`. It was the only title-bearing setting (no
  `html_title`/`latex_documents`/`html_short_title`), so the LaTeX title derives from it.
- `book/docs/index.rst`: H1 "Geometry 2" with the underline shrunk to 10 `=` (a mismatched underline
  breaks the rst build).
- Live references updated: CLAUDE.md's `make docs` bullet, `tasks/reference/book-and-docs-pipeline.md`,
  `tasks/reference/book-outline.md`, `tasks/reference/openstax-math-pedagogy.md`, and
  `tasks/archive/2026/09/26/docstrings-for-sphinx.md` (not in the original grep list, but it named the
  title). The pun on the old title in `openstax-math-pedagogy.md` was reworded to "For a book built
  around relative graph paper, this gap is the opportunity." rather than substituted.
  `tasks/archive/2026/08/16/prove-blade-square-sign-equals-pseudoscalar-squared.md` no longer named the
  title, so it needed nothing.
- Left alone: `tasks/archive/2026/08/02/sphinx-book-pipeline.md` (the historical record of the name at
  build time), and the many "relative graph paper" mentions in notebooks and chapters (the pedagogical
  concept, not the title). `README.md` never mentioned the title.

## Verification

`make docs` was not run (containerized and heavy; nbsphinx executes the notebooks). The one
build-breaking risk, the rst underline, was checked by length match instead.
