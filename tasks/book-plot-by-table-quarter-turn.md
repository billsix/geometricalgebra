# Book: plot from a table by turning the output with `e_1 * e_2`

**Status:** ready — decision made, waiting for the go-ahead to execute
**Priority:** 4
**Difficulty:** 4
**Created:** 2026-11-22 (William Emerison Six <billsix@gmail.com>)

## BLUF

As children we plotted a function by filling a table of inputs and outputs and marking the
points. The book already draws that table "along one direction": each input `x * e_1` beside its
output `f(x) * e_1`, both on the same line. Add the next step: take those same vectors, multiply
each output by `e_1 * e_2`, and show that the output turns 90° to point along `e_2`, so that
input plus turned output is the familiar point `(x, f(x))` on graph paper. Say why the product
does that. Done = the page is in the book with its companion notebook and its Lean
theorem, and `make format`, `make check-notebooks`, `make test`, `make docs` and `make lean`
pass.

## The request (2026-11-22, the maintainer's words)

> when we were kids, we learned how to plot by making tables, and plotting them. Find the task
> and section where we did plotting in one direction, I like the work there. Afterwords, show
> how to plot by taking those vectors, and multiplying the function's result by e_1 * e_2, and
> show that it rotates 90 degrees, and why.

## The work the maintainer likes

- **Task:** `tasks/archive/2026/11/19/fill-placeholder-book-notebooks.md` (its `one-dimension`
  row: `f = translate(b) @ uniform_scale(m)`; graph-paper pictures, then each input
  `x * e_1`, `x = −5..5`, beside its output on a parallel number line, stacked so a tilted head
  sees the line). Commit `6d7b69a`, "book: fill the one-dimension notebook and page".
- **Page section:** `book/docs/one-dimension.rst`, "Along one direction".
- **Notebook sections:** `notebooks/one-dimension.py`, "The same function, along one direction"
  (one figure per input, the scale step green, the translate step blue, the output a purple dot)
  and "Turn your head" (all eleven rows stacked; tilt your head to the right and the output dots
  fall on the line `y = m * x + b`).
- **Drawing helpers:** `src/gacalc/epixscene/line_scene.py` (`number_lines_scene`,
  `number_line`, `step`, `tip`, `graph_paper_scene`, `graph_line`).

That section ends by asking the reader to tilt their head. The new section replaces the tilted
head with algebra: the product turns the output, so the reader does not have to.

## Context

- Read first: `CLAUDE.md` ("Book: one name per operation…", "Every piece of math comes in three
  forms", "Math notation for readers", the notebook rules), `tasks/reference/book-outline.md`,
  `tasks/reference/teaching-order-and-dependencies.md` (a construction uses only results taught
  before it; the dependency graph on the book's first page), and
  `tasks/reference/book-notebook-teaching-style.md`.
- What is already taught, and where:
  - `book/docs/geometric-product.rst` introduces `e_1 * e_2`, shows `a * (e_1 * e_2)` turns `a`
    by 90°, and states the two facts `e_1 * (e_1 * e_2) = e_2` and `e_2 * (e_1 * e_2) = -e_1`.
  - `book/docs/vector-addition.rst` (before it) teaches adding one arrow at another's tip.
  - `book/docs/one-dimension.rst` is the third page of Part I and works in 𝒢₁
    (`from gacalc.g1 import …`), where there is no `e_2`. Vectors, addition and the product
    all come later.
- Lean already has the quarter turn as a product: `G2.rot90` and "the quarter turn is a
  product", `rot90 v = v * e_12`, in `proofs/GacalcProofs/StandardPosition2D.lean`.
- Python: `g2.Vector.rotate_90_degrees()` is `v * e_12`.
- If `tasks/spell-out-basis-blades-as-vector-products.md` has run, the page writes the unit
  plane as `e_1 * e_2`, which is the form this section needs anyway.

## The page

A new page, "Plotting a table" (`book/docs/plotting-a-table.rst`, companion
`notebooks/plotting-a-table.py`), right after `geometric-product` in Part I (decision 1).

**1. The table.** For `f(x) = m * x + b` at the notebook's plot values, the table a child
makes: `x`, `f(x)` for `x = −5..5`, computed from `f` itself. Show the table.

**2. The same table as vectors.** Each row is two vectors on one line: the input
`x * e_1` and the output `f(x) * e_1`. This is the "along one direction" picture; reuse it
(one row, then the stack).

**3. Turn the output.** Multiply each output on the right by `e_1 * e_2`:

    f(x) * e_1 * (e_1 * e_2) = f(x) * (e_1 * e_1) * e_2 = f(x) * e_2

because `e_1 * e_1 = 1`. The output now points along `e_2`, a quarter turn counterclockwise
from where it was, and its length `f(x)` has not changed.

**4. Plot.** Put the turned output at the tip of its input (vector addition):

    p(x) = x * e_1 + f(x) * e_1 * (e_1 * e_2) = x * e_1 + f(x) * e_2

Draw it for each row of the table: the input in black along `e_1`, the turned output from its
tip, the purple dot at `p(x)`. The dots are the graph-paper line `y = m * x + b`, the one
"Turn your head" asked the reader to see by tilting.

**5. Why it turns 90°.** Three statements, each shown:

- `e_1 * (e_1 * e_2) = e_2`: the first two factors are the same unit vector and cancel, leaving
  the other basis vector. An arrow along `e_1` leaves along `e_2`.
- The same product sends `e_2` to `-e_1` (`e_2 * e_1 * e_2 = -e_1 * e_2 * e_2 = -e_1`, one
  swap, one sign), so every arrow `v_1 * e_1 + v_2 * e_2` goes to `-v_2 * e_1 + v_1 * e_2`:
  same length, perpendicular (their dot product is `0`), counterclockwise. That is the page's
  `r(v; π/2)` (one name per operation: cite `geometric-product`'s equation, do not rename it).
- Doing it twice gives `-v`: two quarter turns are a half turn, which is why
  `(e_1 * e_2) * (e_1 * e_2) = -1`.

**6. The other side, and the other sign.** `(e_1 * e_2) * e_1 = -e_2`: multiplying on the
left turns the output the other way and draws the graph upside down. One figure, so the reader
sees that the side matters.

**7. A table that is not a line.** The same four steps for `f(x) = x * x` (the parabola a
child plots next), to show nothing depended on `m * x + b`.

**Notebook.** Symbolic first (`f(x_input)`, the product, `p(x)` with symbols `m`, `b`, `x`),
numbers only to draw, live ePiX figures with every argument by keyword, one check shown with
`show_difference`: `p(x)` against `x * e_1 + (m * x + b) * e_2`. The output must be a 𝒢₂ vector
to be multiplied, so the notebook builds `f` over `gacalc.g2` (`translate(b=Scalar(b) * e_1) @
uniform_scale(m=m)`), the same construction as in 𝒢₁.

**Lean.** One theorem beside `rot90` in `StandardPosition2D.lean` (or `G2.lean`): for reals
`x`, `y`, `add (smul x e_1) (mul (smul y e_1) e_12) = add (smul x e_1) (smul y e_2)`, with the
notebook cell carrying the same `twin:` comment. `y` is a genuine scalar here, so it stays one.

**Figures.** A new helper in `src/gacalc/epixscene/line_scene.py` (or `scene2d.py`) for "input
along `e_1`, turned output from its tip", and its entry in `tests/` if the module's helpers are
tested.

## Plan

1. Write the notebook, then the page, then the Lean theorem; add the page to the Part I
   toctree of `book/docs/index.rst` after `geometric-product`.
2. Update `tasks/reference/teaching-order-and-dependencies.md` and the dependency graph
   (`book/docs/proof-dependencies.dot`) with the new node; update
   `tasks/reference/book-outline.md` and `notebooks/README.md`.
3. Add a forward pointer at the end of `book/docs/one-dimension.rst`'s "Along one direction":
   one sentence saying the tilt becomes a multiplication later.
4. Gates: `make format`, `make check-notebooks`, `make test`, `make docs`, `make lean`.

## Decisions

William Emerison Six <billsix@gmail.com>, 2026-11-22, on the agent's recommendation:

1. **A new page right after `geometric-product`**, with a one-sentence forward pointer from
   `one-dimension`. Why: `one-dimension` is the third page and works in 𝒢₁; this needs `e_2`,
   vector addition and the product `e_1 * e_2`, all taught later, and a construction may use
   only what came before it. Rejected: a section at the end of `one-dimension`, which would
   have to introduce `e_2` and the product early.

## History

All on 2026-11-22 (William Emerison Six <billsix@gmail.com>).

1. Asked for; the one-direction work was traced to its task, page section and notebook
   sections, and the new steps were drafted around `f(x) * e_1 * (e_1 * e_2) = f(x) * e_2`.
2. One question went to the maintainer, where it goes. The answer is the Decision above: a new
   page after `geometric-product`.
