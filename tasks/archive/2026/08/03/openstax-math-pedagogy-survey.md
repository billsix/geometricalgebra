# OpenStax math pedagogy survey (for the GA book)

**Created:** 2026-08-03 · **Completed:** 2026-08-03

Read the LaTeX-converted source of four OpenStax math books (Prealgebra `prealgebra-2e`, Algebra
`osbooks-algebra-1`, Precalculus `precalculus-2e`, Calculus 1 `calculus-volume-1`) and
characterized their pedagogy: how they explain new ideas, the anatomy of worked examples, how
exercises are structured and ordered, how much repetition and spaced review they use, and how they
signal "this result is now settled — use it as a tool." The concern behind it: GA layers levels of
abstraction (dot, wedge, geometric product, projection/rejection, rotors), and students fixate on
the mechanics of each instead of black-boxing a proven result and climbing to the next level.

**Deliverable:** `tasks/reference/openstax-math-pedagogy.md` (a reference doc, descriptive and
applied, with many transcribed examples), grounded in the gacalc Python code and the book's aim: a
high-school-level "Geometry 2" that students print out and draw on.

## What was done

- Used the four OpenStax book repos' `latex` branches (local clones; no container path is
  recorded here).
- The converter `cnxml2tex/convert.py` turned out to be pure Python (needs only lxml), so it ran
  in the sandbox with no TeX Live container.
- Converted all three bundles (college-algebra, which contains precalculus-2e; prealgebra;
  calculus): prealgebra-2e 75 modules, algebra-1 976 sections, precalculus-2e 87,
  calculus-volume-1 55.
- Five parallel readers each covered one book/aspect (explanation style, worked-example anatomy,
  exercise structure/ordering, repetition/spaced review, settled-result signaling), quoting
  verbatim examples with anchors.
- Read the gacalc Python (the book's then-current approach) for the applied section.
- Wrote the reference doc: descriptive findings, applied recommendations, print-and-draw worksheet
  ideas, and the multi-level/black-box treatment. It cross-links
  `tasks/archive/2026/08/03/verify-dot-wedge-as-projection-rejection-products.md` as the worked
  archetype of the black-box climb (§10.3 and §11 of the reference doc).

## Notes and decisions

- The converter emits `latex/<collection>.tex` masters that `\input` `latex/sections/mNNNNN.tex`;
  the per-section files were read, using the master for reading order.
- "Unknown/fallback elements" (inline:span/label/space) in the converter output were cosmetic, not
  blockers for reading pedagogy.
- Scope call: "algebra" meant the high-school `osbooks-algebra-1`, matching the maintainer's
  Algebra 1 / Algebra 2 framing.
