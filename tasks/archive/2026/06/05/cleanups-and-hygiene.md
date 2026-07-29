# Cleanups & repo hygiene (backlog)

Status: **complete** · proposed 2026-06-04 · worked + finished 2026-06-05
**Completed:** 2026-06-05

Non-correctness cleanups identified during the assessment (see `CLAUDE.md`). Low risk; grouped for
one review.

## Progress (2026-06-05)

- **#1 doctests** — the broken `modelviewprojection`/`Vector2D` doctests were already gone (the
  `transforms.py` refactor rewrote them to valid lambda examples). Repo has **no CI**, but
  `--doctest-modules` is now **ENABLED** in `pytest.ini` so the doctests run as part of local pytest
  (see Resolved decisions).
- **#2 typos / cosmetics** — DONE: `excuted`→`executed` and `sortedBladeDictionyEntriy`→
  `sorted_blade_dictionary_entry` in `gn.py`; `_repr_latex_` no longer round-trips through
  `sympy.sympify(str(x))` (now `sympy.latex(x)` directly — verified byte-identical output for numeric
  and symbolic coeffs). The `"Note invertible"` message and malformed `\frac` were already fixed in
  the refactor.
- **#3 `.gitignore`** — DONE: added `__pycache__/`, `*.py[cod]`, `.pytest_cache/`, `.ruff_cache/`,
  egg-info, build/dist, `.ipynb_checkpoints/`. (None were tracked; nothing committed affected.)
- **#4 vendored Emacs tree** — **DECISION: keep it vendored** (author wants a reproducible Emacs
  env). Recorded in `CLAUDE.md` (Module layout + known-issue 7) and memory as **off-limits** — never
  read/edit/format/gitignore it. Whole-repo tooling churn (`ruff format .` hit 27 vendored files last
  task) is now **fixed** by excluding `entrypoint/` from ruff (see Resolved decisions).

Verified after edits: `bash entrypoint/format.sh` (ruff + ty clean) and `python -m pytest -q`
(124 passed: 118 tests + 6 doctests).

## Resolved decisions (2026-06-05)

- **Doctests: ENABLED.** `pytest.ini` now sets `testpaths = src tests` (so collection never walks
  `entrypoint/` or `notebooks/`) and `addopts = --doctest-modules
  --ignore=src/geometricalgebra/nbplotutils.py` (that module imports a matplotlib GUI backend that
  fails headless and has no doctests). Bare `python -m pytest` → **124 passed**.
- **format.sh: emacs tree excluded via config.** Added `extend-exclude = ["entrypoint"]` to
  `pyproject.toml [tool.ruff]` — both `ruff check` and `ruff format` (and editor integrations) skip
  the vendored tree no matter how invoked — a CLI flag covers only one entry point (note: `ruff format` does
  **not** accept `--extend-exclude` on the CLI, only `ruff check` does). `format.sh` stays plain
  `ruff check . --fix` / `ruff format` with a pointer comment. Confirmed it no longer touches any
  `entrypoint/` file.

## Known remaining (out of scope, pre-existing)

- `ruff check .` reports one `E402` in `notebooks/displaymv.py:471` — a mid-cell import, idiomatic for
  a jupytext notebook, flagged before this work too. Left as-is; revisit only if we add per-file
  ignores for notebooks.

## 1. Fix / rewrite the `InvertibleFunction` doctests (`gn.py`)

The docstrings on `InvertibleFunction`, `inverse`, `compose`, `compose_intermediate_fns`,
`compose_intermediate_fns_and_fn` import from **`modelviewprojection.mathutils`** (a different
package) and show `Vector2D`/`Vector1D` return values that don't exist here. They're copy-pasted from
the author's book project. They'd fail under `--doctest-modules` (not currently enabled, so they
silently rot). **Options:** rewrite the examples against this package's real API (e.g. `Gn`/`G2`
values), or delete the misleading example blocks. Decide whether to also enable doctests in CI.
(`TODO.org` lists "add docstrings" as undone.)

## 2. Typos / cosmetics (`gn.py`, others)

- Malformed LaTeX `S_{{\\\frac...}}` (triple backslash) in `scale_non_uniform_2d`.
- `"Note invertible.  Scaling factors cannot be zero."` → "Not invertible." (also `uniform_scale`
  says it correctly — make consistent).
- Spelling: `excuted` ("This code should never be able to be excuted"), and the camelCase +
  misspelled local `sortedBladeDictionyEntriy` in `decrease_grade`.
- `_repr_latex_` round-trips coefficients through `sympy.sympify(str(x))` (fragile string round-trip;
  consider using the sympy object directly).

## 3. `.gitignore`

- `src/geometricalgebra/__pycache__/` shows up in `git status` — add `__pycache__/` (and `*.pyc`) to
  `.gitignore`. The existing `.gitignore` only covers Emacs artifacts.

## 4. (Optional, larger) Vendored Emacs tree

`entrypoint/dotfiles/.emacs.d/elpa/` is a large vendored package tree that dwarfs the actual source.
Decide whether to keep it committed (it's part of the container dev setup) or gitignore/slim it.
Bigger decision — listed for awareness, not urgent.

## Open questions

- Rewrite vs. delete the broken doctests (#1)? Enable `--doctest-modules` afterward?
- Do the typo/gitignore fixes (#2, #3) now as a quick sweep?
