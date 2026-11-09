# Investigate the grade-0 discrepancy in dot-product / contraction definitions

**Created:** 2026-07-22 · **Completed:** 2026-07-22 (resolved)

Spun off from `tasks/archive/2026/07/22/add-left-right-contraction.md`; findings live in
`tasks/reference/contraction-and-dot-definitions.md`.

## The question

Sources disagree on whether **grade 0 (scalars)** participates in the dot/contraction family, and
gacalc committed to only one convention. Was that right, and did it need to change once
contractions existed?

## What the three sources say

- **Hestenes & Sobczyk** (gacalc's reference, eq. 1.21b): the inner/dot product is **not defined
  for grade 0**; `base.inner_product` implements this as `if lg > 0 and rg > 0`.
- **M.D. Taylor, *An Introduction to Geometric Algebra and Geometric Calculus*, 2021, p. 103**, on
  the maintainer's reading: Taylor **includes grade 0** in the looping of source components, and
  states grade 0 is part of the *dot* product too, conflicting with Hestenes for the plain dot.
- **galgebra 0.6.0** (`galgebra/ga.py`) keeps two different operations:
  `_HestenesDotFunction._result_grade` returns None if either grade is 0 (**excludes 0**), while
  `_LeftContractFunction` / `_RightContractFunction` (`grade2 − grade1` / `grade1 − grade2`) have
  **no grade-0 guard** (**include 0**).

## Resolution

The investigation was carried out while implementing the contractions (by reading galgebra 0.6.0
source); the contraction work was never blocked on it, since contractions include grade 0 under
both Taylor and galgebra.

1. **Contraction grade-0 behaviour is unambiguous**: Taylor p.103 and galgebra agree the
   contractions **include** grade 0. Implemented exactly so.
2. **gacalc's stance was decided and shipped**: `inner_product` stays the Hestenes dot
   (grade-0-excluded); the contractions include grade 0. Both conventions coexist, matching
   galgebra, and the docstrings say so explicitly so a reader isn't surprised that
   `a.inner_product(scalar)` and `a.left_contraction(scalar)` differ.
3. **No separate grade-0-including "dot" op**: galgebra has none and nothing needs one; the
   contractions cover the grade-0-inclusive case.

**One residual was deliberately not pursued** (it needs Taylor's text, which the maintainer has and
the agent did not): whether Taylor calls grade 0 part of the *plain dot* product, not just the
contractions. galgebra keeps the plain dot grade-0-excluded (Hestenes), and gacalc follows Hestenes
for `inner_product`, so this is a Taylor-vs-Hestenes textual curiosity that changes no gacalc code.
It was archived as resolved on that basis.

## Related

- `tasks/reference/contraction-and-dot-definitions.md`: the resolved understanding.
- `tasks/archive/2026/07/22/add-left-right-contraction.md`: the feature whose docstrings flag this.
