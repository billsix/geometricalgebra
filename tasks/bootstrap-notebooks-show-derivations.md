# Part III notebooks: show each derivation with set values and plots, not `[0, 0]` checks

**Status:** proposed — needs go-ahead (all questions answered)
**Priority:** 4
**Difficulty:** 5
**Created:** 2026-11-16 (William Emerison Six <billsix@gmail.com>)
**Related:** `tasks/bare-2d-bootstrap-pages.md` (the six Part III pages and notebooks; open);
`tasks/archive/2026/11/16/bootstrap-dot-wedge-from-proj-rej.md` (the latest edits to them)

## BLUF

The Part III companion notebooks ("Step N, … — calculations") check each result by subtracting
the two sides and printing `[0, 0]`. The maintainer (2026-11-16) wants each derivation shown as a
notebook instead, **with plots**. The values are set in the book build. A reader running the
notebook can change them and replot. Done means the six Part III notebooks work that way, are
rendered in the book with their set values and plots, and that the style is written down in
`tasks/reference/book-outline.md` for new notebooks.

## Context

### What the maintainer said (2026-11-16, in order)

1. Pointing at the Part III work: "that's the kind of stuff I was looking to have evaluated in the
   book, the parts that show the math derivation", done instead of what an earlier task did, which
   "subtracted stuff to make sure they equal zero".
2. "they weren't necessarily notebooks, they may have been rst".
3. The example of what is **not** wanted, the intro of
   `book/docs/notebooks/bootstrap-projection.py`: "Step 2, projection from rotation —
   calculations … Each check prints [0, 0] when it holds."
4. "those sections should be notebooks, and should have plots. the user should be able to change
   values and replot if they run it as a notebook, but in the book, we have values set".

### What exists (2026-11-16)

- **Six notebooks**, `book/docs/notebooks/bootstrap-*.py` (jupytext percent format), each in its
  page's toctree and executed by myst-nb at `make docs` (`book/docs/conf.py`:
  `nb_execution_raise_on_error = True`, 600 s timeout). All are symbolic: `sympy` symbols for
  every coordinate, a `zeros()` helper, and cells ending `zeros(lhs - rhs)  # -> [0, 0]` (between
  6 and 9 such checks per notebook, 94–180 lines each). None plots anything.
- **The derivations themselves** are in the `.rst` pages (`book/docs/bootstrap-*.rst`) as
  `.. math::` blocks, with ePiX figures rendered at build time (`book/figures/epix/boot_*.py`).
- **Plotting for notebooks:** `src/gacalc/nbplotutils.py` (matplotlib) has `create_graphs`,
  `create_basis`, `create_unit_circle`, `plot_multivector`, `draw_right_triangle`, `show_mult` and
  more. The book's notebooks don't use it: per the Decisions below, Part III plots with ePiX, as
  `frame-qr-*.py` already does.
- **The three-forms rule** (`CLAUDE.md`): every result has a symbolic-Python form, today the
  `[0, 0]` checks. Removing them needs a decision (Open question 1).

## Plan (draft; depends on the Open questions)

1. Write the notebook style into `tasks/reference/book-outline.md`, with one converted notebook as
   the example:
   - a values cell at the top;
   - each derivation step computed from those values and shown;
   - a plot per step;
   - checks beside what they check, one subtraction and one result per cell;
   - "change the values and rerun" said once.
2. Convert Step 2 first (`bootstrap-projection.py`) as the pilot, and get the maintainer's review
   of the rendered page before doing the rest.
3. Convert Steps 1 and 3–6, one commit each.
4. Gates: `make format` (ty over the notebooks), `tools/check_annotations.py`, `make docs`. Then
   look at each rendered notebook page in the HTML and PDF, plots included.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-16)

- **The plots are ePiX**, drawn live in the notebook's cells, not matplotlib. The precedent is
  `book/docs/notebooks/frame-qr-*.py`, which draws through `book/figures/epix/_frame_scene.py`.
  It relies on `epix.figure()` resetting ePiX's global state for each figure (`CLAUDE.md`, "ePiX
  in the image"). Part III's scene helpers are in `book/figures/epix/_bootstrap_scene.py`. The
  figure rules apply: every argument by keyword (`tools/check_epix_keywords.py`, which also checks
  the book notebooks), every binding typed, and each label in the colour of what it labels.

- **Checks sit beside what they check, one result per cell** (answered Q1). There is no closing
  section of symbolic checks. Where a step needs checking, a cell subtracts the two sides, using
  the values just plotted or symbolic values, and shows a single result. Several things to check
  means several cells, never one cell printing a list of results.
- **The page keeps its LaTeX derivation** (answered Q2). The notebook repeats each step with the
  set values beside an ePiX plot, so the PDF reads on its own.
- **One shared set of values across all six steps** (answered Q3, left to the implementer). Pick
  vectors that match what the Part III ePiX figures already draw
  (`book/figures/epix/_bootstrap_scene.py`). Put them in the first code cell, which says once that
  a reader can change them and rerun.
- **Scope: the six Part III notebooks only** (answered Q4). The Part I notebooks are left for
  later.

## Open questions

None. The task is ready to start on your go-ahead.
