# Consider porting the book from Sphinx to impo's `osbook` LaTeX house style

**Status:** parked — maintainer: "hold off on this for now, low priority" (2026-10-08). Do not
start. Revisit after `tasks/investigate-osbook-latex-source-region-includes.md` reports.
**Priority:** 10
**Difficulty:** 9
**Created:** 2026-10-08 (William Emerison Six <billsix@gmail.com>)

## BLUF

A possible future: write "Geometry 2" in LaTeX using the same `osbook` document class and
pedagogy environments the maintainer built for his OpenStax ports in impo (`openstax/tooling/latex/`),
instead of Sphinx. Attraction: `osbook-envs.sty` already provides the boxed `definition` /
`theorem` / `example` / `tryit` / `keyconcepts` vocabulary that `tasks/reference/openstax-math-pedagogy.md`
§0 recommends this book adopt, plus a print-grade memoir layout and HTML/EPUB editions via pandoc.
Cost: the Sphinx pipeline's three things LaTeX does not give for free — **executed notebooks**
(myst_nb runs `book/docs/notebooks/*.py` and pastes outputs), **source-region includes** with line
numbers (`literalinclude`), and the **autodoc API appendix** (`api.rst`). This task is the place to
collect the feasibility findings; it is not a go-ahead.

## Feasibility map (fill in as the investigations land)

| Sphinx feature in use | LaTeX/`osbook` answer | Status |
|---|---|---|
| `.rst` prose, `:math:` | plain LaTeX — a mechanical port (Sphinx's own `latex` builder output is a starting point, not the product) | known |
| ePiX figures (`book/figures/epix/*.py` → `_static/epix/*.pdf`) | native: the figures are already `elaps`-rendered PDFs; `\includegraphics` | known |
| `literalinclude` by doc-region, `:linenos:` + `:lineno-match:` | **unknown** — `tasks/investigate-osbook-latex-source-region-includes.md` | pending |
| executed notebooks (myst_nb) | `jupyter nbconvert --to latex` per notebook, or run them at build and splice outputs; must also reach pandoc's HTML/EPUB | not investigated |
| `api.rst` autodoc | no equivalent; drop, or generate a LaTeX API appendix from docstrings (sphinx `latex` builder of just `api.rst`?) | not investigated |
| `:ref:`/`:numref:`/`:eq:` numbering | native LaTeX (`\ref`, `\pageref`, `equation`) — strictly better for print | known |
| HTML edition | impo's pandoc templates (`make html`/`make epub` in a book folder) | known, untested on this content |

## Context

- The current pipeline and its decisions: `tasks/reference/book-and-docs-pipeline.md` (why
  lualatex, the Sphinx-in-venv kernel requirement, ePiX rendering).
- The pedagogy case for `osbook`'s environments: `tasks/reference/openstax-math-pedagogy.md`
  (§0 "the LaTeX environment set *is* the pedagogy"; Part II recommendations).
- impo's toolchain contract: impo `openstax/CLAUDE.md` (toolchain MIT, content CC BY; "generated →
  ignore"; every book mounts at `/book`; per-book `Makefile` targets `pdf`/`html`/`epub`).
  A gacalc port would be a **new family** or a `trench`-style native-LaTeX book there — impo's
  `trench/` (native LaTeX restyled via a per-book shim reusing `openstax/tooling/`) is the closer
  template than the CNXML books.
- The print-readability tasks filed the same day (`pdf-section-and-page-numbers-for-print`,
  `number-equations-with-labels`, `line-numbers-in-source-listings`) get most of the print benefit
  **within Sphinx**; if they satisfy, this port may never be needed. Weigh that before unparking.

## Open questions

Deferred until unparked.
