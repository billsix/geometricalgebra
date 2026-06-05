# Cleanups & repo hygiene (backlog)

Status: **not started** · proposed 2026-06-04 · needs go-ahead per item

Non-correctness cleanups identified during the assessment (see `CLAUDE.md`). Low risk; grouped for
one review.

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
