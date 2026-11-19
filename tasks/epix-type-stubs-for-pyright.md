# Let pyright check the live-figure notebooks once ePiX ships type information

**Status:** blocked
**Priority:** 7
**Difficulty:** 3
**Created:** 2026-11-19 (William Emerison Six <billsix@gmail.com>)
**Blocked on:** epix-mirror's `tasks/ship-python-type-information.md` being done, committed and
pushed to github.com/billsix/epix-mirror (a `_epix.pyi` stub and `py.typed` in `python/epix/`).
**Recheck:** `git -C <epix-mirror checkout> fetch github && git -C <epix-mirror checkout> cat-file
-e github/master:python/epix/py.typed && git -C <epix-mirror checkout> cat-file -e
github/master:python/epix/_epix.pyi`; both succeed = cleared (then bump `EPIX_COMMIT` to that
commit).

## BLUF

pyright skips the 31 notebooks that draw live ePiX figures (the `exclude` list in
`pyrightconfig.json`), and ty allows `epix` to be unresolved (`pyproject.toml`,
`[tool.ty.analysis] allowed-unresolved-imports`). Once epix ships type information, make it
visible to both checkers and remove both. Done means `make check-notebooks` covers every notebook
with zero errors and `make format` passes without the ty allowance.

## Context

- Why pyright skips them (measured 2026-11-19, during
  `tasks/archive/2026/11/19/notebooks-one-directory.md`): ePiX has no stub or `py.typed`, and the image installs it
  editable through a setuptools import hook that static checkers cannot follow. Every name the
  notebooks import from `gacalc.epixscene` that comes from ePiX (`Point`, `PendingFigure`,
  `LabelPos`, `Color`) was reported, 91 errors in all.
- The lean CI image (`MINIMAL_IMAGE=1`) has no ePiX at all. Stubs inside the epix package only help
  in an image that builds ePiX. epix-mirror's task asks (its Q2) whether a stub-only package is
  wanted for this.
- Three errors pyright reported in `notebooks/frame-qr-2d.py` are about sympy, not ePiX:
  `table[1, 0]` and `sympy.Matrix(...)[:2, :2]` are typed as `MatrixElement | list`. They need
  narrowing (see `tasks/reference/pyright-sympy-coefficient-typing.md`) once the notebook is
  checked.

## Decision (William Emerison Six <billsix@gmail.com>, 2026-11-19)

Once epix-mirror ships the stubs, drop the pyright `exclude` list rather than keep any part of it.
The one caveat is CI's lean image, which has no ePiX: step 3 decides how it gets the types, and
the excludes go only when the CI notebooks job passes without them.

## Plan

1. Bump `EPIX_COMMIT` to the epix-mirror commit that ships the stubs, and make the editable install
   visible to static checkers (`--config-settings editable_mode=compat` in
   `entrypoint/install-epix.sh`, or a non-editable install).
2. Remove the `exclude` list from `pyrightconfig.json` and `allowed-unresolved-imports` from
   `pyproject.toml`; fix what pyright and ty then report (the sympy narrowing above included).
3. Decide how CI's lean image gets the types (a stub-only package, or a CI notebooks job that
   builds ePiX), following epix-mirror's answer.
4. Gates: `make check-notebooks`, `make format`.
