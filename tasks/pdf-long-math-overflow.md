# Long math expressions run off the PDF page

**Status:** proposed — needs go-ahead
**Priority:** 3
**Difficulty:** 5
**Created:** 2026-11-20 (William Emerison Six <billsix@gmail.com>)

## BLUF

Some math expressions in the book's PDF are too wide for the page and are cut off at the right
margin. HTML is not affected, since MathJax scrolls. Measure every overflowing expression, sort
each one by where it comes from, and fix each source with the mechanism that fits it (the
strategy is below). Done means a fresh `make docs` PDF has no math past the right margin, and a
check that keeps it that way.

## Context

- The maintainer's ask (2026-11-20, verbatim): *"Take a look at the math expressions that get cut
  off in the PDF because they are too long, and come up with a strategy for fixing that."*
- **First measurement, 2026-11-20**, on `output/gacalc/geometry2.pdf` (built 2026-11-19): running
  `pdftotext -bbox-layout` and counting text lines whose right edge is within 20 pt of the page
  edge gives 80 lines on 29 pages: 69, 82, 130, 165, 210, 219, 220, 224, 226, 229, 336, 366, 367,
  371, 378, 380, 382–385, 387, 390, 394, 395, 417, 434, 448–450. This is a rough proxy. It also
  catches long code lines, and it misses glyphs clipped past the edge. The real list comes from
  LaTeX's `Overfull \hbox` warnings (plan step 1). The page range 366–395 is mostly Part IV, the
  exploration notebooks.
- The LaTeX log is not kept: `entrypoint/docs.sh` copies only the PDFs out of `_build/latex/`.
- **Where wide math comes from (three sources, each needing its own fix):**
  1. **Hand-written `.rst` math** (`.. math::` and `:math:`), which a person can break.
  2. **Notebook Markdown math** (`$$…$$` in a `# %% [markdown]` cell), also hand-written.
  3. **Computed notebook output**: a value's `_repr_latex_` (`blade_latex` in
     `src/gacalc/base.py`), `show_mult` / `show_cancellation` in `src/gacalc/nbdisplay.py`, and
     sympy output. Examples: `MultiVector.symbolic_multivector(n=8, …)`, and a symbolic 𝒢₃ product
     with 8 blades of 8-term coefficients. No one can hand-break these. They are one `$$…$$` line
     in the `text/latex` MIME output.
- Book config: `book/docs/conf.py` (`latex_elements`, lualatex). Pipeline and font notes:
  `tasks/reference/book-and-docs-pipeline.md`, and the Sphinx-book reference doc
  (`sphinx-book-conventions.md`) in github.com/billsix/runClaudeInContainer.

## Strategy

Fix each case at its source, with the least lossy mechanism first:

1. **Measure.** Keep `_build/latex/*.log` (copy it to `output/gacalc/` in `entrypoint/docs.sh`)
   and list every `Overfull \hbox` that is inside math, with its width and source line. Save the
   list in `tasks/adhoc/pdf-long-math-overflow/data/`.
2. **Hand-written math (sources 1 and 2): break it by hand,** using `aligned` / `split` at a
   `=` or before a `+`, one term or step per line. This is the clearest result for a reader. It
   also fits the book's "show each step" style.
3. **Computed output (source 3): break at blade boundaries in the display code.** Teach the
   display helpers (`blade_latex`'s caller, `show_mult`, `show_cancellation`) to print one blade
   per line inside `\begin{aligned}`, used only when the expression is wider than a threshold
   (term or character count). A multivector is a sum of blades, so one blade per line is the
   natural break, and it reads the same in HTML. Within one blade, a coefficient that is still
   too wide breaks before a `+` at monomial boundaries.
4. **Last resort, PDF only:** a LaTeX fallback in `conf.py`'s preamble that shrinks a display
   to `\linewidth` (e.g. `adjustbox` with `max width`). Use it only for what steps 2 and 3 cannot
   reach, because shrunk math gets hard to read when printed.
5. **Keep it fixed:** after `make docs`, a check that fails on any math `Overfull \hbox` wider
   than a small tolerance (as a `tools/` script run by the docs build).

## Plan

1. Strategy step 1 (measure), then sort each hit by source (1, 2 or 3).
2. Source 3 first, since one helper change fixes many pages. Add the threshold, the `aligned`
   output and doctests to `nbdisplay` / the `_repr_latex_` path. Check HTML and PDF.
3. Hand-break the remaining `.rst` and Markdown math.
4. Add the overflow check, and use the fallback only where it is still needed, listing each such
   case in this doc.

## Decisions

(William Emerison Six <billsix@gmail.com>, 2026-11-20.)

1. **The one-blade-per-line layout goes into `_repr_latex_` itself**, behind the width threshold,
   so plain cell outputs and Jupyter get it too, not just `show_mult` / `show_cancellation`.
   Short values keep printing on one line. `_repr_latex_` is on `MultiVectorBase` and also comes
   out of the generated `g*.py`, so check both (generate first, per CLAUDE.md "Code generation").
   Existing doctests and tests that pin the one-line LaTeX must keep passing below the threshold.
   Because a long value's display changes, this needs a `CHANGELOG.md` `[Unreleased]` entry.

## Open questions

None.
