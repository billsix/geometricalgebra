# Cleanups & repo hygiene (backlog)

**Created:** 2026-06-04 · **Completed:** 2026-06-05

Four low-risk, non-correctness cleanups identified during the initial assessment (see `CLAUDE.md`)
were done as one sweep.

## What changed

1. **`InvertibleFunction` doctests (`gn.py`).** The broken doctests copied from the author's book
   project (importing `modelviewprojection.mathutils`, showing `Vector2D`/`Vector1D`) were already
   gone: the `transforms.py` refactor had rewritten them as valid lambda examples. Doctests were then
   **enabled**: `pytest.ini` sets `testpaths = src tests` (collection never walks `entrypoint/` or
   `notebooks/`) and `addopts = --doctest-modules --ignore=src/geometricalgebra/nbplotutils.py`
   (that module imports a matplotlib GUI backend that fails headless and has no doctests). The repo
   had no CI then, so this ran in local pytest.
2. **Typos / cosmetics.** `excuted` → `executed` and `sortedBladeDictionyEntriy` →
   `sorted_blade_dictionary_entry` in `gn.py`; `_repr_latex_` stopped round-tripping through
   `sympy.sympify(str(x))` and uses `sympy.latex(x)` directly (output verified byte-identical for
   numeric and symbolic coefficients). The `"Note invertible"` message and the malformed `\frac` in
   `scale_non_uniform_2d` had already been fixed by the refactor.
3. **`.gitignore`.** Added `__pycache__/`, `*.py[cod]`, `.pytest_cache/`, `.ruff_cache/`, egg-info,
   build/dist, `.ipynb_checkpoints/` (none were tracked).
4. **Vendored Emacs tree — decision: keep it vendored** (the author wants a reproducible Emacs
   environment). Recorded in `CLAUDE.md` as off-limits: never read, edit, format, or gitignore it.
   The whole-repo tooling churn (`ruff format .` had touched 27 vendored files) was fixed by adding
   `extend-exclude = ["entrypoint"]` to `pyproject.toml [tool.ruff]`, so both `ruff check` and
   `ruff format` (and editor integrations) skip it however invoked. A CLI flag was rejected because
   it covers one entry point only, and `ruff format` does not accept `--extend-exclude`. `format.sh`
   stayed plain `ruff check . --fix` / `ruff format` with a pointer comment.

Left as-is: one pre-existing `E402` in `notebooks/displaymv.py:471`, a mid-cell import that is
idiomatic in a jupytext notebook.

## Verification

`bash entrypoint/format.sh` (ruff + ty clean) and `python -m pytest -q`: 124 passed (118 tests +
6 doctests); `format.sh` confirmed to touch no `entrypoint/` file.
