# to_matrix: build the matrix from its columns, not by assembling rows

**Created:** 2026-06-11 · **Completed:** 2026-06-12

## Why

`transforms.to_matrix` (from `tasks/archive/2026/06/08/invertiblefunction-to-matrix.md`) already
produced a column-convention homogeneous matrix (column *i* = image of basis vector *i*, translation in
the last column), but built it as a list of **rows**: `linear_cols` were already the probed
basis-vector images, and a `rows` loop transposed them via `coord(linear_cols[i], j)`, then appended a
`[0]*n + [1]` homogeneous row. The maintainer wanted the construction to follow the data — each column
is a probed image — removing the easy-to-get-wrong index transposition. Only the construction changed,
not the convention (column-vector premultiply, translation last).

## What was done

`to_matrix` assembles the matrix from its columns: `sympy.Matrix.hstack(*columns)` for the sympy backend,
`np.column_stack([...])` for numpy, with no rows list and no transpose. After a couple of iterations
with the maintainer, the final form has a `coords(v, bottom)` helper that builds each whole column —
the n coordinates **plus** its bottom entry (`0` for a direction column, `1` for the origin/translation
column) — so the `0/1` lives at the bottom of each column instead of in a separate homogeneous row. The
coordinates are read straight from `v.to_blade_dict()` (the stored coefficient, no product, no
`component`/`scalar_product`), per the maintainer's "just read what it already has".

## Verification

The output was value-identical (the hard constraint): the 9 `to_matrix` tests (translation in the last
column, `diag(m,m,m,1)`, zero translation column for linear, `compose` → product, `inverse` → matrix
inverse, NONLINEAR raises) and the docstring examples passed; the full suite passed; ty and ruff were
clean. The mvp `pyMatrixStack` cross-check was structurally unaffected; re-confirming it on the mvp side
was left optional.
