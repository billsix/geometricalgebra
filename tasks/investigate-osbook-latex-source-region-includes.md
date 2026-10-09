# Investigate: can the OpenStax-port LaTeX toolchain (impo's `osbook`) include source-code regions the way Sphinx's `literalinclude` does?

**Status:** proposed — needs go-ahead (an investigation; its recommendation feeds
`tasks/port-book-to-osbook-latex.md`, which is parked)
**Priority:** 8
**Difficulty:** 3
**Created:** 2026-10-08 (William Emerison Six <billsix@gmail.com>)

## BLUF

The maintainer's question (2026-10-08): *"can the openstax latex use source code literals to
include regions like sphinx?"* — i.e. can impo's `osbook` LaTeX house style pull a marked region
of a `.py` file into the typeset book, as this book's Sphinx `literalinclude` does with
`:start-after: doc-region-begin <name>` / `:end-before: doc-region-end <name>` (the pattern
modelviewprojection's book uses throughout). **Purpose:** decide whether a LaTeX port of this book
(`tasks/port-book-to-osbook-latex.md`) could keep quoting `src/gacalc/` by marker, with real line
numbers, in PDF *and* in impo's pandoc-built HTML/EPUB editions. **Deliverable:** a short reference
doc (`tasks/reference/osbook-latex-source-includes.md`) with the answer, a working minimal example,
and the recommended follow-up tasks (in impo for toolchain work, here for the port).

## What is already known (read 2026-10-08, no build run)

- **impo's toolchain today has no region-include at all.** `openstax/tooling/latex/osbook-envs.sty`
  defines `oscode` — an `\obeylines` + `\ttfamily` environment whose *content is emitted by the
  CNXML→LaTeX converter* (`convert.py`) from `<code>` blocks; it is not verbatim and reads no files.
  Grep of `openstax/tooling/` for `listings`, `minted`, `lstinputlisting`, `inputminted`,
  `catchfile`, `linerange`, `doc-region`: nothing. The class (`osbook.cls`: memoir, lualatex,
  fontspec) loads neither `listings` nor `minted`.
- **The CNXML books never needed it** — OpenStax content has no external source files. This book
  would be the first consumer, so it is a toolchain *addition*, owned by impo.
- **The marker convention to support** is gacalc's doc-region one (`tasks/reference/code-generator-architecture.md`
  §6): `# doc-region-begin <name>` … `# doc-region-end <name>`, names prefix-free per file, checked
  by `tools/check_doc_regions.py`.

## Candidates to evaluate (in order)

1. **`listings` with text-marker ranges.** `\lstinputlisting[linerange={<begin>-<end>}, rangeprefix=…,
   rangesuffix=…, includerangemarker=false]{file}` selects between two *marker strings* rather than
   numeric lines — the closest thing to `start-after`/`end-before`. Check: can `rangeprefix`/
   `rangebeginprefix` be set to `\#\ doc-region-begin\ ` and the end form to `\#\ doc-region-end\ `
   so the marker is literally `<name>`; does `numbers=left` with `firstnumber=` give the **file's
   line numbers** (Sphinx's `:lineno-match:`) or restart at 1 — if it restarts, listings cannot
   match `lineno-match` on its own. Also: Unicode in source under lualatex (`listings` +
   `fontspec` + `extendedchars` has known rough edges; gacalc docstrings carry `𝒢ₙ`, `√`).
2. **`minted` (Pygments).** `\inputminted[firstline=,lastline=]{python}{file}` is numeric-only;
   marker support would need a tiny **preprocessor** that resolves `<name>` → line numbers and
   emits a `.tex` snippet (`firstnumber=` set to the real first line, so line numbers match the
   file). That preprocessor is ~40 lines of Python, fits impo's "generated → ignore" model, and
   gives the same highlighting as the Sphinx HTML. Needs `pygmentize` + `-shell-escape` in the
   build image.
3. **A Lua pre-pass under lualatex** (`\directlua` reads the file, finds markers, writes a
   temp file for `lstinputlisting`). Powerful but the most bespoke; only if 1 and 2 both fail.

**The HTML/EPUB editions are the real risk.** impo builds those with **pandoc from the LaTeX**
(`openstax/tooling/` pandoc templates; `make html`/`make epub` per book). pandoc does not execute
`\lstinputlisting`/`\inputminted`; it either drops them or needs a filter. So any candidate must
also answer "how does the same include reach the web edition" — likely the preprocessor route (2),
emitting a plain `verbatim`/`lstlisting` block that pandoc *does* understand, is the one that
works in all three outputs. Test all three (`pdf`, `html`, `epub`) in the minimal example.

## Method

1. In a scratch book folder under impo (or a scratch `.tex` using `osbook.cls` directly in the
   `openstax/tooling` image — `make shell` there), write a 1-page document that includes the
   `translate signature` and `translate body` regions of this repo's `src/gacalc/transforms.py`
   by each candidate; build PDF, then HTML and EPUB through impo's pandoc path.
2. Record per candidate: markers honoured? real line numbers? lualatex Unicode OK? web editions
   OK? image deps added?
3. Write the reference doc here (`tasks/reference/osbook-latex-source-includes.md`) with the
   verdict and the minimal example; propose the follow-ups: (a) in **impo** — add the chosen
   mechanism to `openstax/tooling/` (its own task there, since the toolchain is impo's and MIT);
   (b) here — fold the verdict into `tasks/port-book-to-osbook-latex.md`'s feasibility section.
   Per the reference-doc rule, scaffold (a) as a `proposed — needs go-ahead` task in impo when
   this one archives, so the recommendation is not stranded.

## Context pointers

- impo repo (the maintainer's OpenStax LaTeX port carrier, sibling of github.com/billsix/imps):
  `openstax/CLAUDE.md` (family contract), `openstax/tooling/latex/{osbook.cls, osbook-envs.sty,
  osbook-defer.sty}`, `tasks/reference/tooling/converters.md`, `tasks/reference/tooling/cross-references.md`.
- This repo: `tasks/reference/openstax-math-pedagogy.md` (why `osbook`'s environments appeal to
  this book), `tasks/reference/book-and-docs-pipeline.md` (the Sphinx pipeline being compared),
  `tasks/archive/2026/10/09/line-numbers-in-source-listings.md` (the `:linenos:` + `:lineno-match:` pattern the LaTeX
  side must match).

## Open questions

None for the investigation itself.
