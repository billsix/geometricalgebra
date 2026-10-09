# Can impo's `osbook` LaTeX include marked source regions, like Sphinx `literalinclude`?

**What this is:** the answer to the maintainer's 2026-10-08 question — *"can the openstax latex
use source code literals to include regions like sphinx?"* — i.e. can impo's OpenStax `osbook`
LaTeX house style pull a **marked region** of a `.py` file into the typeset book, the way this
book's Sphinx `literalinclude` does, and the way **modelviewprojection's book does throughout**.
**Investigation only** (the maintainer's standing rule for LaTeX/OpenStax/Sphinx-porting
questions): this records the finding and a recommendation; nothing was changed in impo and no
Sphinx→LaTeX conversion was done.

## The pattern being replicated (Sphinx, as modelviewprojection uses it)

`modelviewprojection/book/docs/ch11.rst` (the reference example):

```rst
.. literalinclude:: ../../src/modelviewprojection/demos/demo11.py
   :start-after: doc-region-begin define square
   :end-before: doc-region-end define square
   :linenos:
   :lineno-match:
```

Three things to reproduce: **(1)** a region chosen by a *named marker* in a comment
(`# doc-region-begin <name>` … `# doc-region-end <name>`), not by line number; **(2)** line
numbers (`:linenos:`); **(3)** those numbers equal to the **real source line numbers**
(`:lineno-match:`), so a reader can find the code in the file. gacalc's own book uses the same
directive, and `nb_number_source_lines = True` numbers its notebook cells
(`tasks/archive/2026/10/09/line-numbers-in-source-listings.md`).

## Answer: yes, with the `listings` package — verified by compiling a minimal example

The `listings` package (pure LaTeX, already in the sandbox's TeXLive; `minted` is **not**
installed) does marker-based range includes. Verified to compile and include the right region
(and exclude the rest) with `pdflatex`:

```latex
\usepackage{listings}
\lstset{basicstyle=\ttfamily\small, numbers=left}
...
\lstinputlisting[language=Python, linerange={square-square},
  rangebeginprefix=\#\ doc-region-begin\ ,
  rangeendprefix=\#\ doc-region-end\ ,
  includerangemarker=false, firstnumber=<first source line>]{demo11.py}
```

- `rangebeginprefix` / `rangeendprefix` match `# doc-region-begin ` / `# doc-region-end `; the
  `linerange={name-name}` names the region. `includerangemarker=false` drops the marker lines
  from the output. The included text was exactly the region; lines outside it did not appear.
- **Escaping gotcha (this cost the first attempt):** the `#` and the spaces in the prefix must
  be escaped — `\#\ doc-region-begin\ `, not `{# doc-region-begin }`. With an unescaped prefix
  `listings` silently matches nothing and emits an **empty** listing (the document compiles to
  "No pages of output", not an error).

## The two real gaps vs. Sphinx

1. **`:lineno-match:` has no direct equivalent.** `listings` numbers a region from `1`, or from
   whatever `firstnumber=` you pass; there is no "use the file's own line numbers" switch. To match
   the source you must pass `firstnumber=<the region's first real line>` per include — a number
   that drifts whenever the file above the region changes. A small helper (a script that reads the
   marker's line number and writes the `firstnumber`, or a Lua filter) would be needed to make it
   maintenance-free the way `:lineno-match:` is for free.
2. **The pandoc HTML/EPUB editions.** impo builds PDF **and** pandoc HTML/EPUB. `\lstinputlisting`
   is a LaTeX-only construct; pandoc's LaTeX reader does not expand it into the HTML/EPUB code
   block. So a `listings`-only solution gives the marker-include in the **PDF only**. The
   HTML/EPUB path would need either a preprocessing step that resolves the includes to literal code
   before pandoc runs, or a pandoc filter — the same "resolve includes first" shape Sphinx does
   internally. This is the larger piece of work, not the LaTeX macro.

## impo's current state

impo's `osbook` toolchain (`openstax/tooling/latex/{osbook.cls, osbook-envs.sty, …}`) has **no
code-listing mechanism at all** — no `listings`, no `minted`, no source-include macro. That is
expected: OpenStax math books quote no source code. Adding this is net-new toolchain work, not a
tweak.

## Recommendation (for the maintainer to decide — not done here)

If a LaTeX port of this book (`tasks/port-book-to-osbook-latex.md`, currently parked) is pursued:

- **In impo (toolchain):** add `listings` to `osbook`, define a `\gacalcregion{file}{name}` macro
  wrapping the pattern above, and solve the two gaps — a `firstnumber` helper for line-number
  fidelity, and the pandoc HTML/EPUB include-resolution. File these as impo tasks when the port is
  greenlit.
- **In this repo:** the port task can then quote `src/gacalc/` by marker the way the Sphinx book
  does; this book's sources would need the `# doc-region-begin/end <name>` markers added (many are
  already marked for the doc-region codegen gate — `make check-regions`).

**Bottom line:** the core capability (marker-region include + line numbers in the PDF) is real and
proven; the work that makes it *equivalent* to Sphinx is the `lineno-match` helper and the pandoc
HTML/EPUB path, both of which live in impo.
