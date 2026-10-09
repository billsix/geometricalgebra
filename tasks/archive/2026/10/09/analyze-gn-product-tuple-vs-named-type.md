# Analyze the structure/naming of the Gn geometric product: named type vs. passing tuples

**Status:** complete
**Completed:** 2026-10-09
**Priority:** 5
**Difficulty:** 3
**Started:** 2026-10-09

## BLUF

Analyzed how `Gn._geometric_product` carries a `(blade, coefficient)` term through its `decrease_grade`
canonicalization, compared the current `BladeDictionaryEntry(NamedTuple)` against the earlier plain
tuple form the maintainer recalls as "cleaner" and two other options, all behaviour-identical. Findings,
the concrete before/after from git history, the options table, and a recommendation are in
`tasks/reference/gn-product-structure-options.md`. Outcome: it is a **taste call**, not a defect —
either keep the NamedTuple (no work) or adopt option C (a type-aliased tuple) to recover the terse
recursion with a readable return type. **The maintainer chose to keep the `NamedTuple` as is
(2026-10-09)**; option C was declined and its scaffolded task removed. The decision is recorded in
`tasks/reference/gn-product-structure-options.md`.

## What was found

- **Current (named record):** `BladeDictionaryEntry(NamedTuple)` (`blade`, `coefficient`,
  `as_multivector()`); `decrease_grade` takes/returns it; the four `match` arms read
  `basis_blade.blade` / `.coefficient` and reconstruct the record at each recursive call.
- **The maintainer's recollection is accurate.** Git history shows the oscillation: `ca31ce5`
  ("use tuple instead, directly", in `src/geometricalgebra/multivector.py`) passed the blade and
  coefficient as **two positional values** and returned a bare `(blade, magnitude)` 2-tuple, with terse
  recursive calls and a `sorted_rest, new_mag = decrease_grade(...)` destructure; `18e1536`
  ("extracted type") later introduced the named record.
- **Where each wins:** the tuple form's advantage is the terse recursive calls / return-destructure
  (the bulk of the function); the NamedTuple's advantage is self-documenting field access in the arms
  and a home for `as_multivector()`. The tuple era's one real weakness was the opaque return
  annotation `tuple[tuple[int, …], Real]`.
- **Not a performance question:** the product maps `decrease_grade` over every blade pair, but a
  NamedTuple, a plain tuple, and a slotted frozen dataclass allocate comparably.

## Recommendation (in the reference doc)

Either keep the `NamedTuple` (field names earn their keep; no work) or adopt **option C** — a type alias
`BladeTerm = tuple[Blade, Real]`, positional return, `as_multivector` as a free helper — which recovers
the old terseness while naming the return type. Options A (bare tuple, opaque annotation) and D (frozen
dataclass, heavier for no gain) are not recommended. The pick is the maintainer's taste.

## Open questions

None. The one decision — keep the NamedTuple or switch to option C — was answered by the maintainer
(2026-10-09): **keep the NamedTuple**. See `tasks/reference/gn-product-structure-options.md`.
