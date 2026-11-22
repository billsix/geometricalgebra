# Book: plot from a table by turning the output with `e_1 * e_2`

**Status:** done 2026-11-22
**Created:** 2026-11-22 (William Emerison Six <billsix@gmail.com>)

## What this did

*One Dimension* draws a function's table "along one direction": each input `x * e_1` beside its
output `f(x) * e_1`. The new page `book/docs/plotting-a-table.rst` (companion
`notebooks/plotting-a-table.py`), placed right after `geometric-product` in Part I, takes the next
step: multiply each output on the right by `e_1 * e_2`, so it turns a quarter turn to
`f(x) * e_2`, and put it at the tip of its input, `p(x) = x * e_1 + f(x) * e_1 * (e_1 * e_2)`. That is
the point `(x, f(x))` a child marks on graph paper, so the tilt of the old page is replaced by the
product. The page says why the product turns a vector (`e_1` goes to `e_2`, `e_2` to `-e_1`, same
length, dot product `0`, twice gives `-v`), what multiplying on the left does (the graph comes out
upside down), and repeats the four steps for `f(x) = x * x`. `one-dimension.rst` ends with a
sentence pointing forward to it.

- **Notebook:** works in 𝒢₂ with symbols `m`, `b`, `x` and the values `m = 1`, `b = 2` for drawing
  (the line `y = x + 2` fits a square figure; `m = 2` made it tall). One shown check:
  `p(x)` against `x * e_1 + (m * x + b) * e_2`.
- **Figures:** four helpers in `src/gacalc/epixscene/line_scene.py`: `plotted_table_scene`
  (graph paper fitted around the points, directions named by the basis vectors), `plot_row`,
  `turn_picture` and `line_through`. No test: the module's other helpers have none.
- **Lean:** `smul_e1_mul_e12`, `plotted_point_eq` (the notebook's `twin:`), `e2_mul_e12`,
  `e12_mul_smul_e1` and `mul_e12_twice`, beside `rot90` in `proofs/GacalcProofs/StandardPosition2D.lean`.
  `y` is a genuine scalar in each, and each takes objects.
- **Docs:** the Part I toctree in `book/docs/index.rst`, `notebooks/README.md`,
  `book/docs/proof-dependencies.dot` (a node after `rotation_as_product`), and the reading order in
  `tasks/reference/teaching-order-and-dependencies.md` and `tasks/reference/book-outline.md`.

## Decisions

William Emerison Six <billsix@gmail.com>, 2026-11-22: a new page right after `geometric-product`,
with a one-sentence forward pointer from `one-dimension`, because `one-dimension` works in 𝒢₁ and
this needs `e_2`, vector addition and the product `e_1 * e_2`, all taught later. Rejected: a
section at the end of `one-dimension`, which would have to introduce `e_2` and the product early.

The unit plane is written as the product `\vec{\mathbf{e}}_1 * \vec{\mathbf{e}}_2` on the new page
and `i: Versor = e_1 * e_2` in the notebook (`I` is flagged by ruff's E741), the form
`tasks/spell-out-basis-blades-as-vector-products.md` settles on.

## Verification

The notebook's cells ran in the container and every figure was rendered and looked at. `make format`,
`make check-notebooks`, `make test` (1407 passed, 3 skipped), `make docs` (exit 0, no overfull
boxes) and `make lean` (exit 0, 1122 declarations on the three standard axioms, up from 1117) passed.
