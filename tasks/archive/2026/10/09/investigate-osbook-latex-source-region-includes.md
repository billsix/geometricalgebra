# Investigation: can OpenStax/`osbook` LaTeX include marked source regions like Sphinx?

**Status:** complete
**Completed:** 2026-10-09
**Priority:** 8
**Difficulty:** 3
**Created:** 2026-10-08 (William Emerison Six <billsix@gmail.com>)

## BLUF

Investigated the maintainer's question — can impo's `osbook` LaTeX pull a *marked* source region
into the book the way this book's (and modelviewprojection's) Sphinx `literalinclude` does
(`:start-after:`/`:end-before:` + `:linenos:` + `:lineno-match:`)? **Answer: yes for the PDF**, via
the pure-LaTeX `listings` package (verified by compiling a minimal example here); the two pieces
that make it *equivalent* to Sphinx — real source line numbers (`:lineno-match:`) and the pandoc
HTML/EPUB editions — are impo toolchain work. **Investigation only: nothing was changed in impo and
no Sphinx→LaTeX conversion was done.** Full findings, the verified example, the gaps, and the
recommendation: `tasks/reference/osbook-latex-source-includes.md`.

## What was done

- Studied the reference pattern in `modelviewprojection/book/docs/ch11.rst` (`literalinclude` with
  `doc-region-begin`/`-end` markers, `:linenos:`, `:lineno-match:`) — the maintainer flagged MVP as
  the one to study for line-number/marker includes.
- Confirmed impo's `osbook` toolchain has **no** code-listing mechanism (no `listings`/`minted`) —
  expected for a math-book toolchain.
- **Verified** the `listings` marker-range include by compiling a minimal `\lstinputlisting` with
  `rangebeginprefix`/`rangeendprefix`: it selected exactly the marked region and excluded the rest.
  Found the escaping gotcha (`\#\ doc-region-begin\ `, not `{# …}`, or the listing is silently
  empty) and that `:lineno-match:` has no direct equivalent (needs a per-include `firstnumber`).
- Wrote the reference doc with the answer, the example, the two gaps (`lineno-match` fidelity;
  `\lstinputlisting` is LaTeX-only so the pandoc HTML/EPUB path needs include-resolution), and the
  recommended follow-ups (impo toolchain work; the parked `tasks/port-book-to-osbook-latex.md`).

## Open questions

None. (The decision whether to pursue the LaTeX port stays the maintainer's, in the port task.)
