# Options and mode parameters are enums, not strings

**Status:** proposed — open questions below
**Priority:** 4
**Difficulty:** 4
**Created:** 2026-11-10 (William Emerison Six <billsix@gmail.com>)
**Branch:** `sp-rotations-guards-enums-examples`

## BLUF

Every parameter that selects an option by string becomes an `enum.Enum`. Known today:
`Frame.to_invertible_function(inverse_method="reciprocal" | "peel")` (`src/gacalc/frame.py`) and
`to_matrix(..., backend="numpy")` / `ComposableFunction.to_matrix(backend=...)`
(`src/gacalc/transforms.py`, `src/gacalc/functions.py`); the sweep finds the rest (`nbplotutils.py`,
`tools/`, notebooks). Dispatch on the enum with a `match` and a `case _` default (house rule: total
dispatch). Then add the rule to the shared Python standard (tracked separately in
github.com/billsix/runClaudeInContainer `tasks/python-options-as-enums-standard.md` and its
runCrushInContainer mirror). Done means: no string-valued option parameters remain, doctests show the
enum, CHANGELOG lists the breaking change, version bumped (pre-1.0: `0.1.0`), gate green.

## Context (read first)

- gacalc is published (CHANGELOG, `pyproject.toml` version `0.0.20`), so this breaks callers →
  breaking-change entry + minor bump per the versioning rules.
- Discovery: `rg -n 'Literal\[' src tools` plus `rg -n ': str = "' src tools`, then read each hit
  (most `str` params are labels/titles, not options).

## Plan

1. Discover + log to `tasks/adhoc/options-as-enums/data/`.
2. Per option, define the enum next to the function that uses it (exported); convert; doctests.
3. CHANGELOG + version; gate.
