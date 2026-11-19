# gacalc ships a `py.typed` marker

**Status:** proposed — needs go-ahead
**Priority:** 4
**Difficulty:** 1
**Created:** 2026-11-19 (William Emerison Six <billsix@gmail.com>)

## BLUF

gacalc's code is fully annotated, and its generated `g*.py` carry precise `@typing.overload`
signatures, but the package does not say so: there is no `src/gacalc/py.typed`. Without that PEP 561
marker, mypy ignores gacalc's annotations in a consumer, and pyright falls back to inferring types
from the source. Add the marker and ship it in the sdist and wheel. Done means `make dist`'s wheel
contains `gacalc/py.typed`, and a consumer's type checker uses gacalc's own annotations.

## Context

- Found 2026-11-19 while separating out the ePiX type problem
  (`tasks/archive/2026/11/19/notebooks-one-directory.md`). The shared rule is runClaudeInContainer's
  `tasks/python-packages-ship-type-information.md` (github.com/billsix/runClaudeInContainer), which
  adds "a package others install ships `py.typed`" to the shared Python standard.
- Packaging is setuptools with the `src/` layout. `pyproject.toml` already has a
  `[tool.setuptools.package-data]` table, with `"gacalc.gl"` listing the shaders. `setup.py`'s
  `build_py` hook generates the `g*.py` before the copy.
- The consumer that imports gacalc is github.com/billsix/modelviewprojection (its `pgzero_gl`
  shim subclasses `gacalc.g2.Vector`).
- `gacalc.epixscene` imports ePiX, which has no types (geometricalgebra's
  `tasks/epix-type-stubs-for-pyright.md`). The marker is still right for that subpackage: its own
  annotations are complete, and only the ePiX-derived names stay unknown to a consumer.

## Plan

1. Add an empty `src/gacalc/py.typed`, and `"gacalc" = ["py.typed"]` to
   `[tool.setuptools.package-data]`.
2. `make dist`, then `unzip -l dist/gacalc-*.whl | grep py.typed` and
   `tar tzf dist/gacalc-*.tar.gz | grep py.typed`.
3. Consumer check: in a scratch venv with the built wheel installed, a file
   `from gacalc.g2 import e_1; reveal_type(3 * e_1)` reports `Vector` under mypy (which needs the
   marker) and pyright.
4. A `CHANGELOG.md` `[Unreleased]` entry (a consumer's type checker starts reading gacalc's
   annotations, which can surface new errors in their code). Gates: `make format`, `make test`.
