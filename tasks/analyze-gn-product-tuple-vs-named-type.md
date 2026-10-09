# Analyze the structure/naming of the Gn geometric product: named type vs. passing tuples

**Status:** in-progress
**Priority:** 5
**Difficulty:** 3
**Started:** 2026-10-09

## BLUF

Analyze how `Gn._geometric_product` is structured and named today — it canonicalizes each concatenated
blade with the recursive helper `decrease_grade`, carrying a `BladeDictionaryEntry(NamedTuple)` of
`(blade, coefficient)`. The maintainer recalls an earlier version that passed **plain tuples** around
and felt it "looked cleaner," and wants the alternatives weighed. Deliverable: a reference doc that
describes the current design, lays out the options (plain tuple / `NamedTuple` [current] / frozen
dataclass / a pair of parallel values / a small typed record), each keeping behaviour identical, with
pros/cons and a recommendation. **Analysis only — no refactor here**; if the recommendation is to
change, it scaffolds a follow-on implementation task (`proposed — needs go-ahead`).

## Context (read first)

- The code: `src/gacalc/gn.py` — `BladeDictionaryEntry(NamedTuple)` (`blade: Blade`,
  `coefficient: Real`, plus `as_multivector()`), the `_geometric_product` method and its nested
  `decrease_grade` recursion (four `match` arms: base `() | (_,)`, annihilate `a == c`, swap+negate
  `a > c`, in-order-insert `a < c`), and the final comprehension that maps `decrease_grade` over every
  pair of blades from the two factors and sums.
- The types: `Blade = tuple[int, ...]`, `BladeReal = dict[Blade, Real]` (`src/gacalc/base.py`).
- The mechanism is now documented for readers in `tasks/reference/gn-multiplication-by-hand.md`
  (the ASCII slide/flip/annihilate account) — the analysis should stay consistent with it.
- Git history: find the pre-named-type version to ground "it looked cleaner" in the actual old code
  (`git log -- src/gacalc/gn.py`, look for the commit that introduced `BladeDictionaryEntry` /
  `NamedTuple`); quote the before/after so the comparison is concrete, not from memory.
- Conventions that bound the options: the project's Python standard (expression/CQS, naming grammar,
  `cls` for type locals) and "an externally-defined name wins" — the interchange primitives
  `from_blade_dict`/`to_blade_dict`/`_geometric_product` are fixed by `MultiVectorBase` and out of
  scope for renaming.

## Goal

Produce `tasks/reference/gn-product-structure-options.md` (a design-rationale reference doc): the
current structure, the alternatives with concrete before/after sketches, the trade-offs (readability,
type precision, immutability, `match`-pattern ergonomics, allocation cost in the hot product loop,
consistency with the rest of the code), and a recommendation. Keep behaviour identical in every option.

## Plan

- [ ] Read `_geometric_product`/`decrease_grade`/`BladeDictionaryEntry` and the git history of the
      tuple→named-type change; quote the old tuple form.
- [ ] Enumerate the options and sketch each against the four `match` arms (does it still pattern-match
      cleanly? `NamedTuple` and tuple both destructure in `match`; a dataclass needs field patterns).
- [ ] Weigh trade-offs; note the hot-loop allocation angle (the product maps over every blade pair).
- [ ] Write the reference doc with a recommendation; if it recommends a change, scaffold the follow-on
      implementation task as `proposed — needs go-ahead`, cross-linked.

## Open questions

None — this is analysis; any change is a separate, go-ahead-gated task.
