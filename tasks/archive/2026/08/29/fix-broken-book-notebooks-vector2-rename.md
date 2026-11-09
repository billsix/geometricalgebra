# Fix 2 broken book notebooks — stale `Vector2`/`Bivector2` imports

**Created:** 2026-08-28 · **Completed:** 2026-08-28
**Source:** found while running the containerized book build as the final gate for
`tasks/archive/2026/08/29/document-composable-function-math-identity.md`

## The bug

Two book notebooks failed to execute during `make docs`, so their rendered pages shipped a Python
traceback instead of their output:

- `book/docs/notebooks/geometric-product.py` — `from gacalc.g2 import Bivector2, Vector2` →
  `ImportError: cannot import name 'Bivector2' from 'gacalc.g2'`
- `book/docs/notebooks/rotate.py` — `from gacalc.g2 import Vector2` → the same for `Vector2`.

`gacalc.g2` exports `Vector` / `Bivector`: the graded types dropped their `2` suffix in 0.0.15 (see
`tasks/reference/design-decisions.md`, "graded-typed module basis constants"), and these two sources
were never updated. The other 12 book notebooks built clean. It shipped silently because myst-nb
renders an execution error as a warning and the build still exits 0.

## What changed

A mechanical rename in exactly those two `.py` sources (the `.ipynb` are jupytext-generated and
gitignored): `Vector2` → `Vector`, `Bivector2` → `Bivector`, at the imports and the `.e_1` / `.e_2` /
`.e_12` uses; nothing else changed. Scope was the rename only; the missing execution gate was split
out to `tasks/archive/2026/08/29/gate-book-notebook-execution-errors.md`, which had to wait for this
fix (turning the gate on first would have failed `make docs` immediately). The `notebooks/` pyright
gate (`tasks/archive/2026/11/04/add-notebook-pyright-gate.md`) is related but does not cover
`book/docs/notebooks/`.

## Verification

- In-process run of both notebook bodies was clean: the geometric-product agreement diff was 0, and
  `plane_rotation(Vector.e_1, Vector.e_2)(pi/2)(Vector.e_1).simplified()` gave `g2.Vector(0, 1)`.
- A full containerized `make docs` rebuild (nested, `--cgroups=disabled`) exited 0 with no
  `book/docs/_build/html/reports/notebooks/` directory at all (myst-nb creates it only on error),
  where the prior build had `geometric-product.err.log` and `rotate.err.log`.
