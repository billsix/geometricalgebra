# How the book's notebooks teach — the cell-by-cell lesson style

**Reference document.** How the maintainer wants the book's notebooks (`book/docs/notebooks/*.py`)
to read: what a notebook is for, how its cells are shaped, what to copy from the best existing
example, and what to avoid. Update in place; never archive. Created 2026-11-16 (William Emerison Six
<billsix@gmail.com>).

**It covers every notebook**: the book's (`book/docs/notebooks/*.py`) and the demo notebooks under
`notebooks/` alike (William Emerison Six <billsix@gmail.com>, 2026-11-18). Rules that only fit a
book notebook say so (rule 6, "Symbolic notebooks"). Why the two sets still differ in tooling
and figure library, and how to unify them, is `tasks/unify-demo-and-book-notebooks.md` (parked
until the maintainer starts it).

**Scope against the sibling docs.** `tasks/reference/book-outline.md` owns the *structure* of a
companion notebook ("Structural conventions": one values cell, live ePiX figures, one check per
cell, a "For all vectors" symbolic section). This doc owns the *teaching voice and cell design*
inside that structure. The notation rules (explicit `*`, parentheses for application, named angles)
are in `CLAUDE.md` ("Math notation for readers"). The existing book notebooks were brought to this
standard in `tasks/archive/2026/11/16/book-notebooks-teaching-style-sweep.md`; the backfill of a notebook for
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

## The model: the opening of `notebooks/displaymv.py`

The sections of `notebooks/displaymv.py` from "How multiplication works in G_n" through "A longer
example, and why grouping is about to matter" are the model to copy. (The whole notebook now meets
this standard; see "History of the model" below.) What they do, as rules:

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
6. **Numbers before symbols** (the demo notebooks). `3 * e_1 + 4 * e_2` (Pythagoras: `v * v` is
   `25`) comes before the symbolic `sym_vec2_1`. A concrete case the student can check by hand
   earns the general one. Book notebooks instead stay symbolic throughout and show the numbers
   in the figures and the "At the plot values:" cells ("Symbolic notebooks" below).
7. **Make the distribution visible with `show_mult`.** `show_mult(a, b)` (`src/gacalc/nbdisplay.py`)
   prints the product to evaluate, a table of every term of `a` times every term of `b`, and the
   sum. It is the multiply-everything-by-everything grid from rule 1, so the student sees where
   each term of the answer came from instead of receiving a simplified result. For a property such
   as associativity, show both sides' tables, then one cell with the difference (`0`).
8. **Point the curious at the implementation.** One sentence names where the code does the same
   steps (`decrease_grade` in `src/gacalc/gn.py`), for the reader who wants it.

**What else the maintainer likes in it** (studied 2026-11-18, confirmed by William Emerison Six
<billsix@gmail.com>; `tasks/archive/2026/11/18/notebooks-like-displaymv.md`):

9. **Sentences run across cells.** "The plain-number part is the dot product," → output → "and
   the plane part is the wedge:" → output. The prose reads as one sentence, and each output lands
   where its clause ends. A lead-in ending in a comma or colon is the usual sign.
10. **Plain names before jargon.** "Arrows", "plain-number part", "piece of plane" come first;
    "scalar", "bivector", "grade" follow, or wait for the optional formal layer.
11. **Headings are questions or claims, not topics**: "Where do the plain numbers go? Scalars
    first.", "Does grouping matter? A proof that it does not", rather than "Associativity".
12. **The recipe grows one step at a time.** Each section adds exactly one move to a procedure the
    student already holds (three rules, then "putting the rules together", then "scalars first").
13. **Prediction prompts, a handful per notebook**: "Predict the result before running the cell",
    only where a student can genuinely predict (a square, a swap, a length from a Pythagorean
    triple), not on every cell.
14. **It ends in a proof.** With general symbolic elements, a law is shown for every element, not by
    example, and the notebook says so. When the law's cancellation is readable, show it with
    `show_cancellation` (`src/gacalc/nbdisplay.py`). Above a few dozen terms a side, show the zero
    difference and say why the table is skipped.
15. **Zero developer noise**: no `pyright: ignore` trailers, no typing workarounds in sight, short
    cells, mostly one expression. A cell's bare last expression needs no comment: `pyrightconfig.json`
    turns `reportUnusedExpression` off for `notebooks/` and `book/docs/notebooks/`.

## What to avoid

Each of these was in `notebooks/displaymv.py` before 2026-11-16 and should not be copied:

- **The narrative must not stop.** Every code cell has a Markdown lead-in or sits under one that
  covers it. A run of bare cells (dot, wedge, projections onto coordinate planes, grade parts, duals,
  transforms) with no prose is a scratchpad, and it happens exactly where the material gets harder.
- **One notebook, one subject.** A notebook titled for multiplication should not drift into a
  grams-to-moles conversion, transforms and graph paper. A second subject is a second notebook.
- **Write the prose math as LaTeX too, not only the output.** Explanations in backticked code
  (`` `e_1*e_1 = 1` ``) make the student match a monospace `e_12` in the text to a typeset blade in
  the output. Write Markdown math as `$\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_1 = 1$` (MathJax),
  with the `CLAUDE.md` notation rules, so text and output look the same: a vector is
  `\vec{\mathbf{a}}`, a unit vector `\hat{\mathbf{a}}`, a basis vector `\vec{\mathbf{e}}_1`, a
  bivector `\mathbf{e}_{12}`, as `blade_latex` (`src/gacalc/base.py`) writes them; scalars and
  coordinates stay plain. A long inline span may pass 88 columns (`pyproject.toml` exempts the
  book's notebooks and figure scripts from E501); wrap the paragraph around it.
  `tools/check_notebook_prose_width.py [--fix]` checks that (a `make format` step).
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
- **A check is both sides, then a subtraction that shows $0$.** Show the first formula in its own
  cell, the second in the next, then `(left - right).simplified()`, which reduces to $0$ even for
  trigonometric identities; `symbolically_equal(...)`, `==` and `assert` show nothing and are not
  used. With symbolic coordinates one check covers every value, and a list of per-point
  differences adds nothing.
- **One displayed value per cell.** A tuple as a cell's last expression, `(cos, sin)`, does not
  render as math; end the cell on `cos` and put `sin` in the next cell (William Emerison Six
  <billsix@gmail.com>, 2026-11-17).
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

## Symbolic notebooks (the `proof-projection.py` model, 2026-11-17)

Set by William Emerison Six <billsix@gmail.com> while revising
`book/docs/notebooks/proof-projection.py`, then applied to every content notebook in
`tasks/archive/2026/11/17/book-notebooks-symbolic-proof-style.md`:

- **Symbolic the whole time.** Every step uses symbolic coordinates, so each output is a formula.
  Numbers live in one plot-values cell, `values: list[tuple[sympy.Symbol, Real]] = [(a_1, 1), …]`
  (a list of pairs: `ty` rejects a `dict` passed to `subs`), and reach only the figures, through
  `gacalc.nbdisplay.at_values(value, values)`: `point(coordinates=list(at_values(v, values)))`.
- **"At the plot values:" only for what a figure draws.** A drawn step's formula is followed by a
  cell with it at the plot values; a substituted value that nothing draws or uses has no purpose.
- **A `show_mult` table comes twice: at the plot values, then symbolic.** The one exception to
  "numbers only in the figures" (William Emerison Six <billsix@gmail.com>, 2026-11-17). Each row of
  the plot-values table is short enough to check by hand, and the symbolic table after it shows the
  same rows for every vector. Lead in with "First at the plot values:" and "Then with every
  coordinate a symbol:", and build the plot-values table from the symbolic factors:
  `show_mult(at_values(a, values), at_values(b, values))`. Every table follows this except
  `rotation-from-vectors.py`'s `a_hat * b_hat`, whose point is the angle-difference identities,
  which numbers would hide.
- **Numbers in figure labels are computed, never typed:** a notebook-local
  `tex(value) = sympy.latex(at_values(value, values))` fills the label, so it stays right when the
  values change (`frame-qr-2d.py`, `frame-qr-3d.py`).
- **Rotations are the taught ones** (`Vector.rotate`, `standardposition.rotation_from_to` with
  `inverse(R)`, `standardposition.in_plane` for a coordinate plane in 𝒢₃), never a local function
  taking a cosine and a sine, and every construction uses only results taught before it:
  `tasks/reference/teaching-order-and-dependencies.md`.
- **Where arrows meet tip to tip, draw the result first and its parts after**, so the parts' heads
  sit on top (`tasks/archive/2026/11/17/arrowheads-past-their-points.md`).
- **When symbolic is too slow or unreadable, keep numbers and say why in the notebook.** The cases
  today: the 3D frames in `proof-reciprocal-frame.py` and `frame-qr-3d.py` (nine symbolic
  coordinates make each check take minutes), and the second term-by-term table of
  `bootstrap-rotation-from-product.py`'s sandwich, `(R * v) * R⁻¹`, which is shown only at the plot
  values (symbolically it is thousands of characters of nested roots).
- **Watch for double simplification.** Simplifying an already simplified result can merge
  `sqrt(x) * sqrt(y)` into one square root of an expanded product that sympy cannot split again
  (`proof-projection-3d.py` builds its rejection part from coefficients for this reason).

## Checklist for a new or revised notebook

- The page's structure follows `tasks/reference/book-outline.md` ("Structural conventions").
- It opens from something the student knows, and says what the notebook will show.
- Every code cell has a Markdown lead-in; each pair states one idea and confirms it.
- Prose math is LaTeX, following the notation rules in `CLAUDE.md`; vectors and blades are typeset
  as the output typesets them (`\vec{\mathbf{a}}`, `\vec{\mathbf{e}}_1`, `\mathbf{e}_{12}`).
- Hand reductions are chains with a reason per line, followed by the cell that computes them.
- Every step is symbolic; numbers appear only in the plot-values cell, the figures and the
  plot-values `show_mult` tables.
- Each check shows both sides before the difference; each cell displays one value.
- Every construction uses only earlier results, and rotations are the taught ones.
- Products whose expansion is the point are shown with `show_mult`, with a lead-in: at the plot
  values first, then symbolic.
- No developer comments, pyright trailers or typing workarounds in the student's view.
- One subject per notebook; a short, labelled aside (like `displaymv.py`'s units-as-arrows) is
  fine.
- Headings are questions or claims; plain names come before jargon; sentences may run across
  cells.
- A handful of prediction prompts, where a student can genuinely predict.
- Where the subject has a law, the notebook proves it with general symbolic elements, and shows
  the cancellation when it is readable.

## History of the model

`notebooks/displaymv.py` is a demo notebook under `notebooks/`, not a book notebook.
On 2026-11-18 the other demo notebooks were brought to it: `displayg2.py` and `displayg3.py` were
split into one-subject notebooks (`displayg2areas.py`, `displayg2transforms.py`,
`displayg3measures.py`) and rewritten, the rest got Markdown lead-ins for every code cell, the
bold-arrow notation, and no `pyright: ignore` trailers. The notebooks were also exempted from
E501 and added to `tools/check_notebook_prose_width.py`. Until
2026-11-16 its second half was a scratchpad with the problems listed under "What to avoid"; it was
brought to this standard, and its transforms and graph paper moved to
`notebooks/displaytransforms.py`, in `tasks/archive/2026/11/16/displaymv-teaching-style.md`.
`show_mult` lives in the display-only `gacalc.nbdisplay` (sympy and IPython, no matplotlib), so the
book's ePiX-drawn notebooks import it from there; `gacalc.nbplotutils` re-exports it for the demo
notebooks.
