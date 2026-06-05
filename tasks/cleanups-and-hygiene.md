# Cleanups & repo hygiene (backlog)

Status: **mostly done** · proposed 2026-06-04 · worked 2026-06-05 · two items pending decision

Non-correctness cleanups identified during the assessment (see `CLAUDE.md`). Low risk; grouped for
one review.

## Progress (2026-06-05)

- **#1 doctests** — the broken `modelviewprojection`/`Vector2D` doctests were already gone (the
  `transforms.py` refactor rewrote them to valid lambda examples). Nothing to fix. Repo has **no CI**;
  remaining *option* is enabling `--doctest-modules` in `pytest.ini` so doctests actually run locally
  — **not done, awaiting decision.**
- **#2 typos / cosmetics** — DONE: `excuted`→`executed` and `sortedBladeDictionyEntriy`→
  `sorted_blade_dictionary_entry` in `gn.py`; `_repr_latex_` no longer round-trips through
  `sympy.sympify(str(x))` (now `sympy.latex(x)` directly — verified byte-identical output for numeric
  and symbolic coeffs). The `"Note invertible"` message and malformed `\frac` were already fixed in
  the refactor.
- **#3 `.gitignore`** — DONE: added `__pycache__/`, `*.py[cod]`, `.pytest_cache/`, `.ruff_cache/`,
  egg-info, build/dist, `.ipynb_checkpoints/`. (None were tracked; nothing committed affected.)
- **#4 vendored Emacs tree** — **DECISION: keep it vendored** (author wants a reproducible Emacs
  env). Recorded in `CLAUDE.md` (Module layout + known-issue 7) and memory as **off-limits** — never
  read/edit/format/gitignore it. Remaining: whole-repo tooling still churns it (`ruff format .` hit
  27 vendored files last task). Concrete fix = scope `format.sh` to `src tools tests` — **not done,
  awaiting go-ahead** (it's the author's dev script).

Verified after edits: `ruff check src tools tests`, `ty check src`, `python -m pytest -q` (118 passed).

## Pending decisions

- Enable `--doctest-modules` in `pytest.ini`? (no CI; runs doctests as part of local pytest)
- Scope `entrypoint/format.sh` to `src tools tests` so it stops reformatting vendored Emacs +
  notebook files?

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
