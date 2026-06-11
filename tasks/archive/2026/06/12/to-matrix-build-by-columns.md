# to_matrix: build the matrix from its columns, not by assembling rows

Status: **DONE 2026-06-12** · proposed 2026-06-11 (Bill)

> **Done.** `to_matrix` (`transforms.py`) now assembles the matrix from its
> **columns** — `sympy.Matrix.hstack(*columns)` (sympy) / `np.column_stack([...])`
> (numpy), no `rows`-list + transpose. Final form (after a couple of Bill
> iterations): a `coords(v, bottom)` helper builds each whole column — the n
> coordinates **plus** its bottom entry (`0` for a unit-direction column, `1` for
> the origin/translation column) — so the `0/1` lives at the bottom of each column,
> not in a separate homogeneous row. The coordinates are read **straight from
> `v.to_blade_dict()`** (the stored coefficient — no product, no
> `component`/`scalar_product`), per Bill's "just read what it already has". Same
> column-vector convention, value-identical output (9 to_matrix tests + docstring
> examples; full suite green; ty + ruff clean). mvp `pyMatrixStack` cross-check
> structurally unaffected — re-confirm on the mvp side if desired.

## Goal

`transforms.to_matrix` already produces a **column-convention** homogeneous matrix
(column *i* = image of basis vector *i*; translation in the last column). But the
*construction* assembles a list of **rows** and transposes the per-column data into
them. Bill wants it **built from columns directly** — matching how the data is
naturally organized (each column *is* a probed basis-vector image), which is
clearer and removes the index-transposition that's easy to get wrong.

## Current state (`src/gacalc/transforms.py:576`)

```python
f0 = fn(cls.zero())                                  # translation (image of origin)
linear_cols = [fn(cls.basis_vector(i + 1)) - f0 for i in range(n)]   # the columns!

def coord(v, j):
    return v.component(cls.basis_vector(j + 1))

rows = []
for j in range(n):                                   # assembles ROWS...
    rows.append([coord(linear_cols[i], j) for i in range(n)] + [coord(f0, j)])
rows.append([0] * n + [1])                           # homogeneous last row
... sympy.Matrix(rows) / np.array(rows) ...
```

Note `linear_cols` are *already the columns* (basis-vector images); the `rows`
loop just transposes them via `coord(linear_cols[i], j)` = element (row *j*,
col *i*). That transposition is the part Bill wants gone.

## What to do (sketch)

Build each column vector and stack them horizontally — keeping the **exact same
output** (column convention, translation last, homogeneous row):

```python
# each linear column: the basis image's coords + 0 in the homogeneous row
cols = [[coord(lc, j) for j in range(n)] + [0] for lc in linear_cols]
trans_col = [coord(f0, j) for j in range(n)] + [1]
columns = cols + [trans_col]                         # n linear cols + translation col
# sympy: Matrix.hstack(*[Matrix(c) for c in columns]); numpy: np.array(columns).T
```

- **sympy backend:** `sympy.Matrix.hstack(*[sympy.Matrix(c) for c in columns])`.
- **numpy backend:** `np.array(columns, dtype=np.float32).T` (build columns, then
  transpose once — or `np.column_stack`).

## Hard constraint

**Output must be byte/value-identical** to the current implementation — `to_matrix`
has tests (translation-in-last-column, `diag(m,m,m,1)`, zero-translation-column for
linear, `compose → product`, `inverse → matrix inverse`, NONLINEAR-raises; and the
mvp cross-check against `pyMatrixStack`). Run the suite; the matrices must match.

## Open questions

- Confirm Bill means the **construction** (build columns vs assemble rows), not a
  change of *convention* (the output is already column-vector/premultiply with
  translation in the last column — that stays).
- Whether to add a tiny `column(v)` helper for readability.

## Relationship

- Touches `transforms.to_matrix` (landed in
  `tasks/archive/2026/06/08/invertiblefunction-to-matrix.md`); consumed by mvp's
  `mathutils`/`pyMatrixStack` — keep the cross-check green.
