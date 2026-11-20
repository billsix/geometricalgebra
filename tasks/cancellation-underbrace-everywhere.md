# Show every "these terms cancel" check with numbered underbraces

**Status:** proposed — needs go-ahead
**Priority:** 3
**Difficulty:** 4
**Created:** 2026-11-20 (William Emerison Six <billsix@gmail.com>)

## BLUF

The maintainer likes how `notebooks/displaymv.py` shows a cancellation: each pair of cancelling
terms is marked with an `\underbrace{…}_{k}` carrying the same number `k`, so a reader can match
the pairs on screen, or on a printout cross them off one at a time. Find every other place in the
book (notebooks and `.rst` pages) that shows or checks that something cancels, and rewrite it to
use the same numbered-underbrace display. Done means a worklog of every site, each one converted
or opted out with a written reason, and `make docs` passing.

## Context

- **What the liked display is (identified 2026-11-20):** `gacalc.nbdisplay.show_cancellation(left,
  right, left_name, right_name)` in `src/gacalc/nbdisplay.py`. It shows both sides expanded, then
  one line per blade from `cancellation_latex(left, right)` (same file), which expands each
  coefficient into monomials and marks each monomial of `left` that also appears in `right` with
  `\underbrace{…}_{k}`, the same `k` on both copies. Whatever does not cancel is left unmarked and
  the line ends with the residual (`0` for an identity).
- **Current users (3):** `notebooks/displaymv.py` (the associativity check, `# twin:
  GacalcProofs.G2.mul_assoc`), `notebooks/displayg2.py`, `notebooks/displayproofs.py`.
- **Candidate sites found by a first grep (2026-11-20), not yet classified:**
  - Notebooks mentioning "cancel": `defining-g2.py`, `displayg2areas.py`, `displayg3.py`,
    `displaygraded.py`, `displayrotations.py`, `reflection.py`, `reflection-3d.py`,
    `rotation-from-vectors.py` (plus the three users above, which may have further
    un-braced cancellations, e.g. `displaymv.py`'s "the like terms add to 1 and every plane part
    cancels" near its `B^{-1} * B` cell).
  - Notebooks with difference-is-zero style checks (`simplify(`, `== 0`, `.expand()`), which may
    show a bare `0` instead of the cancellation: `bootstrap-rotation-from-projection.py`,
    `frame-qr-2d.py`, `frame-qr-3d.py`, `product-from-projection.py`,
    `proof-reciprocal-frame.py`, `dual-3d.py`, `levels-of-abstraction.py`,
    `vectors-as-number-lines.py`, and others in the same grep.
  - `.rst` pages mentioning "cancel": `book/docs/blade-square-sign.rst` (ASCII `\__/` brackets
    under `e1 e1` pairs — the same idea drawn by hand), `proof-rotate.rst`,
    `proof-rotate-from-a-to-b.rst`, `reflection.rst`, `rotation-from-vectors.rst`.
- `show_cancellation` works on two `MultiVectorBase` values. An `.rst` page has no live Python, so
  there the equivalent is hand-written `:math:` with `\underbrace{…}_{k}`, or a call in the page's
  companion notebook.
- Notebook style: `tasks/reference/book-notebook-teaching-style.md`. Notebooks are jupytext
  percent-format `.py` under `notebooks/`.

## Plan

1. Discover: save the grep as `tasks/adhoc/cancellation-underbrace-everywhere/discover.sh` (cancel /
   cancels / cancelling, `simplify(`, `== 0`, `- … ==`, `\__/`) over `notebooks/*.py` and
   `book/docs/*.rst`; log hits to `tasks/adhoc/cancellation-underbrace-everywhere/data/`.
2. Classify each hit: (a) a two-sided identity check on multivectors → `show_cancellation`;
   (b) a scalar/sympy cancellation (e.g. "the `r`'s cancel") → `\underbrace` in LaTeX, possibly a
   small helper if several sites need it; (c) a blade-word cancellation like `e1 e1 = 1` in
   `blade-square-sign.rst` → see question 1; (d) prose "cancel" that shows no terms → leave.
3. Convert, one page at a time; `make docs`; check the rendered pages and the PDF (underbraces and
   numbers must stay legible when printed).

## Decisions

(William Emerison Six <billsix@gmail.com>, 2026-11-20.)

1. **`blade-square-sign.rst`'s ASCII `\__/` brackets become numbered `\underbrace`s**, with the
   rule (Rule 1, Rule 2) kept as text beside each line. The page's note that a `*` would misalign
   the sliding columns (CLAUDE.md, "Math notation for readers") must be revisited when the diagrams
   leave ASCII.
2. **Scalar cancellations that are not a left-vs-right identity get the same numbered
   `\underbrace`** on each cancelling factor (e.g. `proof-rotate.rst`'s "the `r`'s cancel"), so
   every cancellation in the book reads alike.

## Open questions

None.
