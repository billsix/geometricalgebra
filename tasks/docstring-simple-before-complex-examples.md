# Every example shows a simple case first, then the general one

**Status:** proposed — open questions below
**Priority:** 4
**Difficulty:** 6
**Created:** 2026-11-10 (William Emerison Six <billsix@gmail.com>)
**Branch:** `sp-rotations-guards-enums-examples`

## BLUF

Keep the existing doctests/examples/tests (arbitrary and symbolic vectors), and **add simple ones in
front** so a student gets a quick intuitive feel before the general case. The maintainer's example:
`project` — first project onto a natural basis vector (`e_1`), then onto a scalar multiple of it
(`3 * e_1`) to show the **length of the onto-vector does not matter, only its direction**, then the
existing symbolic arbitrary-vector cases. Each operation's simple examples should make its one key
property visible (reject is perpendicular, reflect flips one component, a rotation keeps length,
wedge of parallel vectors is zero, …). Done means: every public operation in the hand-written modules
has at least one simple, basis-vector example ahead of its general ones, the same for the generated
classes' docstrings (via the generator), and the gate is green.

## Context (read first)

- Conventions for examples: project `CLAUDE.md` ("Build vectors from the basis constants, and write
  every unit coefficient explicitly", "Use the predefined basis constant").
- Doctests are the default unit test (`--doctest-modules`); generated docstrings come from
  `tools/gen_specialized.py` (never edit `g*.py`).
- Scope (docstrings only, or also `tests/` and `notebooks/`) is pending question.

## Plan

1. Inventory public operations per module (`base.py`, `transforms.py`, `frame.py`, `measure.py`,
   `vectorcalc.py`, `standardposition.py`, `functions.py`, generator templates); note which lack a
   simple example.
2. Per operation, choose the property the simple example shows; write it; one module per commit.
3. Regenerate; `make test` + `make type-check`.
