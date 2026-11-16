# How the book's notebooks teach — the cell-by-cell lesson style

**Reference document.** How the maintainer wants the book's notebooks (`book/docs/notebooks/*.py`)
to read: what a notebook is for, how its cells are shaped, what to copy from the best existing
example, and what to avoid. Update in place; never archive. Created 2026-11-16 (William Emerison Six
<billsix@gmail.com>).

**Scope against the sibling docs.** `tasks/reference/book-outline.md` owns the *structure* of a
companion notebook ("Structural conventions": one values cell, live ePiX figures, one check per
cell, a "For all vectors" symbolic section). This doc owns the *teaching voice and cell design*
inside that structure. The notation rules (explicit `*`, parentheses for application, named angles)
are in `CLAUDE.md` ("Math notation for readers"). The sweep that brings the existing book notebooks
to this standard is `tasks/book-notebooks-teaching-style-sweep.md`; the backfill of a notebook for
every proof is `tasks/proof-notebooks-student-math-notation-style.md`. The `show_mult` tables were
added in `tasks/archive/2026/11/16/book-notebooks-show-mult-tables.md`.

## What a notebook is

The maintainer's description (2026-11-16): the notebooks use sympy, but what they show the reader, a
student who does not know the subject, is the *math*, rendered as LaTeX. There are many cells, and
they are ordered to walk the student through the material.

Put another way: **a notebook is a guided lab.** Each idea is stated in plain words, tied to algebra
the student already knows, written as a chain of equalities with a reason on each line, and then
confirmed by a short sympy cell whose rendered LaTeX output is the evidence. Python is the engine;
the student reads math.

## The model: the first part of `notebooks/displaymv.py`

The sections of `notebooks/displaymv.py` from "How multiplication works in G_n" through "A longer
example — and why grouping is about to matter" are the model to copy. (The rest of that notebook is
not; see "Known gaps in the model" below.) What they do, as rules:

1. **Start from algebra the student already knows.** Before any new rule, the notebook recalls
   multiplying `(x + 2)(x + 3)` out term by term, collecting `2x + 3y + 5x`, and the imaginary unit.
   Each new rule is then presented as a small change to that familiar algebra ("the *same* idea,
   with just a couple of new rules for the letters"). Note the quotation of the student's prior
   notation is exempt from the explicit-`*` rule (`CLAUDE.md`).
2. **One idea per cell: state it, then confirm it.** A Markdown cell states one rule in plain words
   ("an arrow times itself is 1"); the next code cell is one line (`e_1 * e_1`) whose output is the
   evidence. Many small cells, each answering exactly one claim, beat one cell that does several
   things.
3. **Two levels of formality, the second labelled.** After the informal rules comes "The same
   rules, written as math", marked as optional ("a little more formal"), restating them as (R1),
   (R2) and the sort-with-a-sign / cancel-repeats procedure. A student can skip it and lose nothing.
4. **Hand reductions as justified chains.** A worked reduction is written as a chain of equalities,
   each line carrying its reason (`— (R1) on the middle pair`, `— regroup (associativity)`,
   `— scalars to the front`). The code cell that follows computes the same product, so the chain
   and the computation agree in front of the student.
5. **Raise the question the student should be asking, from their own step.** After the hand
   reduction, the notebook notices that it *re-grouped* the factors ("Were we *allowed* to do
   that?"), then answers by computing three different groupings, and only then names the property
   (associativity) and says why it is not obvious when order matters. The motivation comes from
   something the student just did, not from a definition.
6. **Numbers before symbols.** `3 * e_1 + 4 * e_2` (Pythagoras: `v * v` is `25`) comes before the
   symbolic `sym_vec2_1`. A concrete case the student can check by hand earns the general one.
7. **Make the distribution visible with `show_mult`.** `show_mult(a, b)` (`src/gacalc/nbdisplay.py`)
   prints the product to evaluate, a table of every term of `a` times every term of `b`, and the
   sum. It is the multiply-everything-by-everything grid from rule 1, so the student sees where
   each term of the answer came from instead of receiving a simplified result. For a property such
   as associativity, show both sides' tables, then one cell with the difference (`0`).
8. **Point the curious at the implementation.** One sentence names where the code does the same
   steps (`decrease_grade` in `src/gacalc/gn.py`), for the reader who wants it.

## What to avoid

Each of these is in `notebooks/displaymv.py` as of 2026-11-16 and should not be copied:

- **The narrative must not stop.** Every code cell has a Markdown lead-in or sits under one that
  covers it. A run of bare cells (dot, wedge, projections onto coordinate planes, grade parts, duals,
  transforms) with no prose is a scratchpad, and it happens exactly where the material gets harder.
- **One notebook, one subject.** A notebook titled for multiplication should not drift into a
  grams-to-moles conversion, transforms and graph paper. A second subject is a second notebook.
- **Write the prose math as LaTeX too, not only the output.** Explanations in backticked code
  (`` `e_1*e_1 = 1` ``) make the student match a monospace `e_12` in the text to a typeset blade in
  the output. Write Markdown math as `$e_1 * e_1 = 1$` (MathJax), with the `CLAUDE.md` notation
  rules, so text and output look the same. `book/docs/notebooks/frame-qr-2d.py` already does this.
- **Say what a table or check shows.** The associativity tables in `displaymv.py` have no lead-in,
  so the student must infer that two groupings are being compared. Say it, and say what the result
  means: with general symbolic multivectors, a zero difference is a proof for every element of the
  algebra, not an example. Call it a proof when it is one.
- **No developer noise the student can see.** No `# pyright: ignore[...]` trailers on teaching
  cells, no comments about typing workarounds (`typing.cast` for `dual()`, why a `Callable` is
  `[..., Any]`). Restructure the cell, or move that code out of the student's path. Teaching code
  follows the `CLAUDE.md` coding conventions too (symbolic coefficients through the scalar
  constructor, basis constants, explicit unit coefficients).
- **Ask before answering.** A comment such as `# -> 1 (Rule 1)` gives the result before the cell
  runs. Prefer a prompt in the Markdown ("Before running the next cell, predict the result") and
  let the output answer it.
- **Size tables to be read.** A 72-row `show_mult` table (an 8-term vector times a 9-term one) can
  make the point that the method scales, but only with a sentence saying so; otherwise it is a wall
  of output. Prefer two- or three-term factors for tables a student reads row by row.
- **No pointers to nothing.** "See the associativity section / task" names nothing. Cite the file:
  the proof is `tasks/reference/geometric-product-associativity.md` and its book page, once there is
  one.

## Mechanics (learned in the 2026-11-16 sweep)

From `tasks/archive/2026/11/16/book-notebooks-teaching-style-sweep.md`:

- **Keep each inline `$…$` on one line.** A formula split across two comment lines is fragile in
  the Markdown parser; put a long one on its own line as display math (`$$…$$`).
- **Math in `$…$`, code in backticks.** A name the reader types (`versor_rotation`,
  `Vector.rotate(θ)`, a Lean theorem, a file path) stays in backticks; a formula becomes LaTeX.
- **A check is a subtraction that shows $0$.** `(left - right).simplified()` reduces to $0$ even
  for trigonometric identities, so `symbolically_equal(...)`, `==` and `assert` are not needed in
  a notebook. When the left side is symbolic, one check covers every value, and a list of
  per-point differences adds nothing.
- **A table of numbers is shown as `sympy.Matrix`**, which renders as a LaTeX matrix
  (`proof-reciprocal-frame.py`'s Kronecker-delta tables).
- **A cell whose helper displays a figure and also returns it** (`plot_multivector`) binds the
  result to a name, so Jupyter does not show the figure twice; a stray trailing expression to
  suppress it is noise.
- **`show_mult`'s tables need `nb_render_markdown_format = "myst"`** in `book/docs/conf.py`; see
  `tasks/reference/book-and-docs-pipeline.md`.
- **Read the check cells without a book build:** from the notebook's directory,
  `PYTHONPATH=<repo>/src python <repo>/tools/run_notebook_cells.py <notebook>.py` runs it cell by
  cell and prints each code cell's last value (the ePiX notebooks need the image).

## Checklist for a new or revised book notebook

- The page's structure follows `tasks/reference/book-outline.md` ("Structural conventions").
- It opens from something the student knows, and says what the notebook will show.
- Every code cell has a Markdown lead-in; each pair states one idea and confirms it.
- Prose math is LaTeX, following the notation rules in `CLAUDE.md`.
- Hand reductions are chains with a reason per line, followed by the cell that computes them.
- Concrete values come before symbols; the symbolic section says when its result is a proof.
- Products whose expansion is the point are shown with `show_mult`, with a lead-in.
- No developer comments, pyright trailers or typing workarounds in the student's view.
- One subject per notebook.

## Known gaps in the model

`notebooks/displaymv.py` itself is a demo notebook under `notebooks/`, not a book notebook, and
after the model sections it becomes a scratchpad with the problems listed under "What to avoid".
Bringing it up to this standard is `tasks/displaymv-teaching-style.md`. `show_mult` lives in the
display-only `gacalc.nbdisplay` (sympy and IPython, no matplotlib), so the book's ePiX-drawn
notebooks import it from there; `gacalc.nbplotutils` re-exports it for the demo notebooks.
