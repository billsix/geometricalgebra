# OpenStax math pedagogy survey (for the GA book)

**Status:** complete — deliverable at `tasks/reference/openstax-math-pedagogy.md`
**Completed:** 2026-08-03
**Priority:** 3
**Difficulty:** 5
**Started:** 2026-08-03

## Goal

Read the LaTeX-converted source of four OpenStax math books — Prealgebra (`prealgebra-2e`),
Algebra (`osbooks-algebra-1`), Precalculus (`precalculus-2e`), Calculus 1
(`calculus-volume-1`) — and characterize their pedagogy: how they explain new ideas, the
anatomy of worked examples, how exercises are structured/ordered, how much repetition and
spaced review they use, and how they signal "this result is now settled — use it as a tool."
Deliverable is a large reference doc with many transcribed examples, both **descriptive**
(what OpenStax does) and **applied** (how to bring it into the GA book), grounded in the
geometricalgebra Python code and the book's aim: a high-school-level "Geometry 2" that
students print out and draw on. Central design concern: GA layers levels of abstraction
(dot, wedge, geometric product, projection/rejection, rotors); students fixate on the
mechanics of each instead of black-boxing a proven result and climbing to the next level.

Deliverable: `tasks/reference/openstax-math-pedagogy.md` (reference doc, not archived).

## Plan

- [x] Locate repos; confirm all four on `latex` branch under /foo/opt/openstax.
- [x] Crack conversion: `cnxml2tex/convert.py` is pure-Python (needs only lxml) — runs
      in-sandbox, no TeXLive container needed.
- [x] Convert college-algebra bundle (contains precalculus-2e).
- [x] Convert prealgebra + calculus bundles. All four now in LaTeX:
      prealgebra-2e (75 modules), algebra-1 (976 sections), precalculus-2e (87),
      calculus-volume-1 (55).
- [x] Per-book read (5 subagents): explanation style, worked-example anatomy, exercise
      structure/ordering, repetition/spaced-review, "settled result" signaling — verbatim
      examples with anchors. All five reports gathered.
- [x] Read geometricalgebra Python (the book's current approach) for the applied section.
- [x] Synthesize the reference doc: descriptive findings + applied recommendations +
      print-and-draw worksheet ideas + the multi-level/black-box treatment.
- [x] Cross-link to [[verify-dot-wedge-as-projection-rejection-products]] as the worked
      archetype of the black-box climb (see §10.3 and §11 of the reference doc).

## Notes / decisions

- Converter emits `latex/<collection>.tex` masters that \input `latex/sections/mNNNNN.tex`.
  Read the per-section files; the master gives reading order.
- "Unknown/fallback elements" (inline:span/label/space) in converter output are cosmetic,
  not blockers for reading pedagogy.
- Scope call: "algebra" = HS `osbooks-algebra-1`, matching Bill's Algebra 1/Algebra 2 framing.

## Open questions
