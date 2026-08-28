# Fix 2 broken book notebooks — stale `Vector2`/`Bivector2` imports

**Status:** DONE 2026-08-28 — rename applied to both notebook sources; verified. Ready to archive.
In-process run of both notebook bodies is clean (geometric-product agreement diff = 0; rotate e_1→e_2),
and a full containerized `make docs` rebuild (nested, `--cgroups=disabled`) exits 0 with **no**
`reports/notebooks/` dir at all (myst-nb creates it only on error) — i.e. zero notebook exceptions,
where the prior build had `geometric-product.err.log` + `rotate.err.log`.
**Priority:** 4
**Difficulty:** 2
**Created:** 2026-08-28 (William Emerison Six <billsix@gmail.com>) — found while running the containerized
book build as the final gate for [[document-composable-function-math-identity]].

## The bug

Two **book** notebooks fail to execute during `make docs`, so their rendered pages ship a Python
traceback instead of the intended output:

- `book/docs/notebooks/geometric-product.py` — `from gacalc.g2 import Bivector2, Vector2`
  → `ImportError: cannot import name 'Bivector2' from 'gacalc.g2'`
- `book/docs/notebooks/rotate.py` — `from gacalc.g2 import Vector2`
  → `ImportError: cannot import name 'Vector2' from 'gacalc.g2'`

`gacalc.g2` exports **`Vector` / `Bivector`**, not `Vector2` / `Bivector2` — the graded types were
renamed (the `2`-suffix was dropped; see `tasks/reference/design-decisions.md` "graded-typed module
basis constants", 0.0.15). These two notebook sources were never updated. The other 12 book notebooks
build clean.

**Why it shipped silently:** myst-nb renders an execution error into the page as a *warning* and the
build still exits 0 (`make docs` succeeded with these two failing). So nothing gates book-notebook
execution — this is a real gate gap, see "Also flag" below.

## The fix (verified 2026-08-28)

Mechanical rename in exactly those two files: `Vector2` → `Vector`, `Bivector2` → `Bivector`
(the `.e_1` / `.e_2` / `.e_12` attributes and everything else are unchanged). Confirmed to resolve and
run:

```
Vector.e_1 = g2.Vector(coeff_e_1=1, coeff_e_2=0)
Bivector.e_12 = g2.Bivector(coeff_e_12=1)
plane_rotation(Vector.e_1, Vector.e_2)(pi/2)(Vector.e_1).simplified() = g2.Vector(0, 1)   # correct
```

Sites to change (all in `book/docs/notebooks/`):
- `geometric-product.py`: line 19 import; `Vector2.e_1`/`Vector2.e_2` (l.24, l.37), `Bivector2.e_12`
  (l.27, l.31).
- `rotate.py`: line 19 import; `Vector2.e_1`/`Vector2.e_2` (l.23, l.26).

**Verify after:** re-run `make docs` (nested, `--cgroups=disabled`) and confirm
`book/docs/_build/html/reports/notebooks/` has **no** `geometric-product.err.log` / `rotate.err.log`
(currently both are present). The `.ipynb` are generated from these `.py` via jupytext and are
gitignored — edit the `.py` sources only.

## The gate gap this exposed → its own task

The reason this drift shipped silently — the book build does **not** fail when a notebook errors
(myst-nb renders the traceback as a warning; `make docs` still exits 0) — is now tracked separately as
[[gate-book-notebook-execution-errors]]. That gate task depends on **this** fix landing first (turning
the gate on while these two notebooks are still broken would make `make docs` fail immediately). So:
this task is purely the two-file rename; the gate is out of scope here.

## Cross-links

- [[document-composable-function-math-identity]] — the task whose book-build gate surfaced this.
- [[add-notebook-pyright-gate]] — the `notebooks/` (not `book/docs/notebooks/`) pyright gate; related
  but does not cover these files.
- `tasks/reference/design-decisions.md` — the `Vector2`→`Vector` graded-type rename that these
  notebooks missed.

## Open questions

(none — scope settled: two-file rename only; the execution gate is
[[gate-book-notebook-execution-errors]], to be done after this.)
