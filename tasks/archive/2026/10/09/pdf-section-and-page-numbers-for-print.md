# Make the book's cross-references usable in print: section numbers and page numbers in the PDF

**Status:** complete
**Completed:** 2026-10-09
**Priority:** 3
**Difficulty:** 2
**Created:** 2026-10-08 **Updated:** 2026-10-09 (William Emerison Six <billsix@gmail.com>)

## BLUF

A printed PDF can't follow a hyperlink, so the maintainer asked (2026-10-08) whether Sphinx can put
section numbers or page numbers in the text. Done: `index.rst`'s toctree is now `:numbered:` (every
chapter/section carries a number in headings, the TOC, and `:numref:`, in HTML and PDF), and
`conf.py` sets `latex_show_pagerefs = True` so every `:ref:`/`:doc:` cross-reference in the PDF reads
"<Title> (page N)", plus `latex_show_urls = "footnote"` for external URLs. The `:numbered:` switch
also upgraded the companion equation numbers from running `(3)` to per-chapter `(10.1)`. Verified
with a full nested `make docs` (HTML + PDF both succeed, no undefined references).

## What was done

- **`book/docs/index.rst`:** added `:numbered:` to the main toctree. Chapters/sections (and the proof
  pages nested in their chapters' toctrees) now number in both builders.
- **`book/docs/conf.py`:** `latex_show_pagerefs = True` (PDF appends `(page N)` via `\autopageref` to
  every cross-reference) and `latex_show_urls = "footnote"` (external URLs become footnotes in print).
  `numfig`/`math_numfig`/`numfig_secnum_depth` were already set by the equation-numbering task; no
  `numfig_format` override — the defaults ("Section %s", "Fig. %s", equation `({number})`) are the
  TeX-style wording the maintainer wanted.
- **`tasks/reference/book-and-docs-pipeline.md`:** a "Numbering & print-readability" bullet under
  "conf.py essentials" records the settings and the label-only-when-cited rule.

## Verification

- Full nested `make docs` (`entrypoint/docs.sh` against the existing image): HTML + PDF both
  "build succeeded"; "Book built". No undefined references in the final LaTeX pass.
- HTML: section numbers render in headings (`<span class="section-number">`); equation numbers are
  now per-chapter (`(10.1)`/`(10.2)` on `proof-rotate`, chapter 10).
- PDF `.tex`: cross-references render as `…{Proof: Rotate}}}} (\autopageref*{…proof-rotate::doc})`
  → "Proof: Rotate (page N)"; four external URLs became footnotes.

## Scope note — section numbers IN the reference text

The automatic config gives: numbered sections everywhere, and every PDF cross-reference carrying a
page number. A reference now reads "Proof: Rotate (page 41)", and its target is a numbered section
"10.1 Proof: Rotate". The aspirational "(Section 2.3, page 41)" *inline in each reference's text*
would additionally need per-link `:numref:` against section labels — `:numref:` does not work on a
`:doc:` (whole-page) target, so it would mean adding section labels and rewording the 23 links. That
is voice-sensitive prose surgery, and the task's own plan marked it selective ("where a number
helps"), so it is **left for the maintainer's voice pass**, not done mechanically here. The core ask
— section numbers and page numbers present in the printed text — is delivered.

## Open questions

None.
