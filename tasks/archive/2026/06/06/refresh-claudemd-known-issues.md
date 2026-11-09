# Refresh CLAUDE.md to match the current code (stale "Known issues" + nits)

**Created:** 2026-06-06 · **Completed:** 2026-06-06

`CLAUDE.md`'s "Assessment / known issues" section and a few other spots described bugs already fixed
in the code, overstating the open-issue count (two stale entries were correctness warnings) and
contradicting itself. It was brought back in sync with `base.py` / `gn.py` / `transforms.py` /
`pytest.ini` as of 2026-06-06. This was a documentation pass; the only code edit was one typo fix.

## Findings (verified against the working tree, 2026-06-06)

Numbers are from the then-current "Open issues" list.

- **#2 — `InvertibleFunction` doctests "would fail under `--doctest-modules` (not enabled)": stale.**
  `pytest.ini` set `addopts = --doctest-modules --ignore=…/nbplotutils.py` and
  `testpaths = src tests`; the `transforms.py` doctests import from `geometricalgebra.transforms`
  with plain lambdas; `pytest -q` gave 141 passed including doctests. The "(not enabled)" also
  contradicted `CLAUDE.md`'s own module-layout line.
- **#3 — `reject`/`reflect` sequence handling: fixed** (`case [*sequence]:` +
  `outer_product_of_vectors`).
- **#4 — `__rmul__` negation: fixed** (the fall-through returns `NotImplemented`, with a comment).
- **#8 — typo/fragility cluster: all fixed but one.** `excuted` / `sortedBladeDictionyEntriy`, the
  malformed `\\frac`, the `_repr_latex_` `sympify(str(x))` round-trip, and the `i15` /
  `unit_pseudoscalar(14)` test bug were gone. The survivor was the `inverse` docstring's "Note sure
  if I'm doing it correctly" (should be "Not sure").
- **Still open and accurate:** #5 fixed Euclidean signature; #6 self-flagged uncertainty in
  `inverse` / `is_parallel_to` / `component`; the open half of #7 (`format.sh` walks the whole repo).
- **Other inaccuracies:** the Architecture → Transforms subsection and a future-directions mention
  put `InvertibleFunction` "in `gn.py`" (it lives in `transforms.py`, re-exported from `gn.py`, as
  the module-layout section already said); the dev workflow mentioned only `pythonpath = src`; the
  section header still said "(updated 2026-06-04)".

## What changed

- `CLAUDE.md`: removed #2, #3 and #4 and cut #8 down to the residual typo; pointed the
  `InvertibleFunction` mentions at `transforms.py` (re-exported from `gn.py`); added `testpaths` and
  `--doctest-modules` to the dev workflow, with the `nbplotutils` ignore and its reason (it imports a
  GUI backend that fails headless), since a broken doctest now fails the suite; bumped the header
  date. Edits were surgical, keeping the file's voice and structure.
- `base.py`: the `inverse` docstring's "Note sure" became "Not sure", keeping the self-flag.
- Done in the same sitting as `tasks/archive/2026/06/06/document-rotor-methods.md`, which added
  content to nearby sections of the same file.

## Verification

`python -m pytest -q` (141) and `entrypoint/format.sh` (ruff + ty) clean after the `base.py`
docstring touch.
