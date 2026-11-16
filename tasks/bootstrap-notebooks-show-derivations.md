# Part III notebooks: show each derivation with set values and plots, not `[0, 0]` checks

**Status:** proposed — needs go-ahead (Open questions below block implementation)
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
  more. `CLAUDE.md` ("ePiX in the image") records the 2026-10-06 decision: matplotlib for the
  interactive notebooks, ePiX for the book's static figures. No book notebook uses matplotlib yet.
- **The three-forms rule** (`CLAUDE.md`): every result has a symbolic-Python form, today the
  `[0, 0]` checks. Removing them needs a decision (Open question 1).

## Plan (draft; depends on the Open questions)

1. Write the notebook style into `tasks/reference/book-outline.md`, with one converted notebook as
   the example:
   - a values cell at the top;
   - each derivation step computed from those values and shown;
   - a plot per step;
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

## Open questions

1. **The symbolic checks:** drop the `[0, 0]` checks, or keep them as a short closing section of
   each notebook ("for any values: …")? *(Recommend: keep them, at the end. They are the
   symbolic-Python form the three-forms rule asks for, and `make docs` fails if one breaks.)*
2. **Where the derivation lives:** should each derivation section move out of its `.rst` page into
   the notebook, leaving the page as prose and a link? Or should the page keep its LaTeX derivation
   and the notebook walk through the same steps with numbers and plots? *(Recommend: the page keeps
   the derivation, and the notebook repeats each step with the set values beside a plot. That way
   the PDF reads on its own.)*
3. **The set values:** one shared set across all six steps, such as `a = 3 * e_1 + 1 * e_2`,
   `b = 1 * e_1 + 2 * e_2`, `v = -1 * e_1 + 2 * e_2`, so the steps read as one story? *(Recommend:
   yes, matching the vectors the ePiX figures draw, if those are close to these.)*
4. **Scope:** the six Part III notebooks only, leaving the Part I notebooks (`rotate.py`,
   `product-from-projection.py`, `proof-projection.py`, …) for later? *(Recommend: Part III only;
   they are the ones you quoted.)*
