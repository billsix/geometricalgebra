# Fill the five remaining placeholder book notebooks

**Status:** done (2026-11-19)
**Created:** 2026-11-19 (William Emerison Six <billsix@gmail.com>)
**Related:** `tasks/archive/2026/11/19/fill-placeholder-book-notebooks.md` (filled the first five
and scaffolded this task); `tasks/archive/2026/11/19/notebook-dot-wedge-projection-demo.md` (since done; it then
records that the book has both its halves)

## What this did

Five book notebooks were still the jupytext stub whose only code cell was `1 + 1`. After this task
no book notebook is a stub (`grep -l '^1 + 1$' book/docs/notebooks/*.py` finds nothing).

| Page | Notebook | Outcome |
| --- | --- | --- |
| `hook` | `hook.py` | Dropped from the toctree and deleted (decision 1) |
| `canonical-form` | `canonical-form.py` | Exact against decimal with sympy: the stored `√2` squared, `0.1 + 0.2`, one canonical form per answer, the cracker example ordered to stay whole, the stored decimal of `5/6` as an exact fraction, a decimal only on request |
| `vectors-as-number-lines` | `vectors-as-number-lines.py` | Any nonzero `v` makes a number line `t * v`; `coordinate_along` reads a point's number; `3 * v` reads 3, 3/2 and −3 on the lines of `v`, `2 * v` and `−v` (`t / s` in general) |
| `projection` | `projection.py` | Decision 2: `proj_a(b)` and `rej_a(b)` drawn and added back to `b`; `a * proj_a(b)` is a plain number, `a * rej_a(b)` a multiple of `e12`, together `a * b`; swapping roles keeps the number and flips the area |
| `projection-rejection-3d` | `projection-rejection-3d.py` | Projection onto the three coordinate planes and onto any plane `p ∧ q`; the 3D product split `a * proj_a(b) = a · b`, `a * rej_a(b) = a ∧ b` |

Each page that kept its notebook got a drafted section or Draft prose. `canonical-form.rst` and
`vectors-as-number-lines.rst` were written in full, still marked for the maintainer's voice pass.
`book/figures/epix/_line_scene.py` gained `slanted_number_line`, a number line along any vector,
with an `offset` for setting two lines side by side. `tasks/reference/book-and-docs-pipeline.md`
lists it.

## Decisions

- **1 (maintainer, 2026-11-19): drop `hook.py`.** Nothing has been taught on the book's first page,
  so it carries no companion notebook.
- **2 (maintainer, 2026-11-19): fill `projection.py` with the dot/wedge projection demo**, in the
  left-multiplied form the maintainer chose on 2026-11-16 (`a · b = a * proj_a(b)`,
  `a ∧ b = a * rej_a(b)`). The `projection` page comes before `product-from-projection`, which names
  the dot and the wedge, so the notebook calls the pieces "a plain number" and "a piece of plane"
  and names them only by forward reference.
- `projection-rejection-3d.py` also carries the 3D product split, which is the remaining work of the
  blocked `tasks/archive/2026/11/19/notebook-dot-wedge-projection-demo.md`. That task's Q1, whether the demo notebook
  `notebooks/displayg3.py` should also carry the cells, is left to the maintainer; the task records
  the progress.
- `canonical-form` comes before vectors are taught, so it uses plain sympy numbers and no gacalc.
  Multiplying the stored decimal of `5/6` by 12 happens to round back to `10.0`; the notebook says
  so and shows the stored fraction instead of hunting for numbers whose rounding fails.

## Verification

Each notebook was executed in the `gacalc` image and every check came out 0; every figure was
viewed. `ruff`, `ty check book/docs/notebooks`, `tools/check_notebook_prose_width.py`,
`tools/check_epix_keywords.py` and `tools/check_annotations.py` were clean. The full `make format`
and the book build (`docs.sh`) ran at the end and passed. The build's only new warning was
`hook.ipynb` "not included in any toctree": a stale, gitignored `.ipynb` left by an earlier build in
the working tree, deleted by hand. A fresh checkout never has it.
