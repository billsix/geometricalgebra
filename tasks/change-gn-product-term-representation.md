# Change the Gn product's term representation (option C: a type-aliased tuple)

**Status:** proposed — needs go-ahead (a taste call; see the analysis)
**Priority:** 7
**Difficulty:** 3
**Created:** 2026-10-09 (William Emerison Six <billsix@gmail.com>)

## BLUF

Optional, behaviour-identical refactor spun off from the analysis
`tasks/reference/gn-product-structure-options.md`. If the maintainer prefers the old "cleaner" tuple
feel over the current `BladeDictionaryEntry(NamedTuple)`, replace it with **option C**: a type alias
`BladeTerm = tuple[Blade, Real]`, positional return in `decrease_grade`, and `as_multivector` moved to a
small free function. This recovers the terse recursion while keeping a named (non-opaque) return type.
**Do not start without the maintainer's pick** — the analysis recommends either keeping the NamedTuple
(no work) or this; both are correct, so it is the maintainer's taste call, not a defect fix.

## Context

- Analysis + options table + before/after: `tasks/reference/gn-product-structure-options.md`.
- Current code: `Gn._geometric_product` / `decrease_grade` / `BladeDictionaryEntry` in `src/gacalc/gn.py`.
- The old tuple form is `git show ca31ce5:src/geometricalgebra/multivector.py`.

## Plan (if greenlit for option C)

- [ ] Add `BladeTerm = tuple[Blade, Real]` (near `Blade`/`BladeReal` in `base.py`, or local to `gn.py`).
- [ ] Rewrite `decrease_grade` to take/return `BladeTerm` positionally; drop `BladeDictionaryEntry`.
- [ ] Move `as_multivector` to a free helper `term_to_multivector(term: BladeTerm) -> Gn` (or inline).
- [ ] Verify: container `make test` (697) + `make format` green; `make check-generated` unaffected
      (this is `Gn`-only, the generator doesn't use `BladeDictionaryEntry`). Confirm with a REPL that a
      few products are byte-identical to before.

## Open questions

1. Keep the current `NamedTuple`, or switch to option C (type-aliased tuple)? The analysis recommends
   either; this task implements C. **Your call** — answer before any code.
