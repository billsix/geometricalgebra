# Migrate unit tests into doctests where they read well

**Status:** proposed — needs go-ahead (the investigation/criteria can start now; the actual migration is the bulk).
**Priority:** 5
**Difficulty:** 4
**Created:** 2026-10-27 (William Emerison Six <billsix@gmail.com>)
**Updated:** 2026-10-27 (William Emerison Six <billsix@gmail.com>)

## BLUF

Push as many of the `tests/` unit tests as reasonable **into doctests** in the library source
(`src/`), so an example lives next to the code it documents and runs as part of `make test`.
"Done" = the tests that read naturally as a `>>> expr` → result example have been moved into the
relevant module/function docstrings; the ones that should **stay** pytest (see criteria) are listed
with a one-line reason each; `make test` is green and still exercises every migrated case.

**The wiring already exists — this task is migration, not plumbing.** `pytest.ini` already sets
`testpaths = src tests tools` and `addopts = --doctest-modules`, so any `>>>` example in `src`
(and `tools`) is already collected and run by `make test`. ~31 test files under `tests/` and
10 source files already carry `>>>` examples. So a doctest you add to `src/` runs automatically;
nothing new needs to be hooked up.

## Context (cold start)

- Repo: github.com/billsix/geometricalgebra (gacalc). Python library + Sphinx book.
- Test gate: `make test` → container → `pytest` (see `Makefile:272`). Collection is governed by
  `pytest.ini` (`testpaths = src tests tools`, `addopts = --doctest-modules`).
- So doctests in `src`/`tools` already count. The question is purely *which `tests/` cases move
  into docstrings*, and where.

## Criteria — what becomes a doctest vs stays pytest

Default: **a test becomes a doctest** if it is a short, deterministic `input → expected output`
that also documents the function (exactly the kind of example a reader of the docstring wants).

**Keep as pytest** (list each kept file/case with its reason) when the test:
- would need a **debugger to understand** the code under test (the user noted none are known in
  gacalc today — confirm during the pass);
- relies on **fixtures, parametrization, or `pytest.raises`/`approx`** machinery that a doctest
  can't express cleanly;
- is a **slow / symbolic / randomized** check (gacalc already has such tests) where putting the
  output in a docstring would be noisy or non-reproducible;
- asserts something **not meant to appear in user-facing docs** (internal invariants, regression
  guards for a specific bug).

## Plan

1. Inventory `tests/` (≈31 files): for each test, classify migrate / keep, with a reason for keeps.
2. Migrate the "migrate" set into the docstring of the function/class/module it exercises; keep
   each example minimal and deterministic (watch NumPy scalar-repr and sympy ordering — the kind
   of thing that silently breaks doctests).
3. Delete the now-redundant pytest cases (don't leave both).
4. `make test` green; confirm the migrated examples actually ran (doctest count went up, pytest
   count went down by the same cases).

## Notes

- Part of a cross-repo "doctests by default" initiative. The convention write-up for runClaude /
  runCrush / the personal dotfiles overlay is tracked separately in **runClaudeInContainer**
  (`tasks/document-doctests-by-default.md`) and is to be done **after** the per-project migrations.
