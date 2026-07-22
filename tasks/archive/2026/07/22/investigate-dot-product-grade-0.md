# Investigate the grade-0 discrepancy in dot-product / contraction definitions

**Status:** resolved
**Completed:** 2026-07-22
Created 2026-07-22. Spun off from `add-left-right-contraction.md`; findings live in
`tasks/reference/contraction-and-dot-definitions.md`.

## Resolution

The investigation was carried out as part of implementing the contractions (by reading galgebra
0.6.0 source), and its conclusions are recorded in
`tasks/reference/contraction-and-dot-definitions.md`:

1. **Contraction grade-0 behaviour is unambiguous** — Taylor p.103 and galgebra agree the
   contractions **include** grade 0. galgebra makes it explicit in code: its
   `_LeftContractFunction`/`_RightContractFunction` have no grade-0 guard, whereas
   `_HestenesDotFunction` does (`if grade1==0 or grade2==0: return None`). Implemented exactly so.
2. **gacalc's stance is decided and shipped** — `inner_product` stays the Hestenes dot
   (grade-0-excluded); the contractions include grade 0. Both conventions coexist, matching galgebra.
3. **No separate grade-0-including "dot" op** — galgebra has none and nothing needs one; the
   contractions cover the grade-0-inclusive case.

**One residual, deliberately not pursued (needs Taylor's text, which the author has and the agent
does not):** whether Taylor calls grade 0 part of the *plain dot* product (not just the
contractions). galgebra keeps the plain dot grade-0-*excluded* (Hestenes), and gacalc follows
Hestenes for `inner_product`, so this is a Taylor-vs-Hestenes textual curiosity that changes **no
gacalc code**. Archived as resolved on that basis.

---

## Original investigation notes (below, for reference)

## The question

Different sources disagree on whether **grade 0 (scalars)** participates in the dot/contraction
family, and gacalc currently commits to only one convention. Is that right, and does it need to
change once contractions exist?

## What we know so far (from reading three sources)

- **Hestenes & Sobczyk** (gacalc's reference): the inner/dot product is **not defined for grade 0**
  — gacalc's `base.inner_product` implements this as `if lg > 0 and rg > 0` (skips any grade-0
  operand). Equation 1.21b.
- **M.D. Taylor, *An Introduction to Geometric Algebra and Geometric Calculus*, 2021, p. 103**:
  Bill's reading — Taylor **includes grade 0** in the looping of source components, and states grade
  0 is part of the *dot* product too. This conflicts with Hestenes for the plain dot product.
- **galgebra 0.6.0** (`galgebra/ga.py`) makes the split explicit in code:
  - `_HestenesDotFunction._result_grade`: `if grade1 == 0 or grade2 == 0: return None` → **excludes 0**.
  - `_LeftContractFunction` / `_RightContractFunction`: `grade2 − grade1` / `grade1 − grade2`, **no
    grade-0 guard** → **include 0**.
  - i.e. galgebra keeps *two different* operations: a Hestenes dot (grade-0-excluded) and the
    contractions (grade-0-included).

## The open points to resolve

1. Confirm Bill's reading of Taylor p. 103 verbatim (does Taylor really put grade 0 in the plain
   *dot* product, or only in the *contractions*? galgebra treats the dot and the contractions
   differently on exactly this point).
2. Decide gacalc's stance: keep `inner_product` = Hestenes-dot (grade-0-excluded, unchanged), and
   make the **contractions grade-0-included** (matching Taylor + galgebra). This is almost certainly
   right (it's what galgebra does), but the naming/teaching story should be explicit so a reader
   isn't surprised that `a.inner_product(scalar)` and `a.left_contraction(scalar)` differ.
3. Whether to add a Taylor-style "dot that includes grade 0" as a *separate* named op, or leave the
   grade-0-included behaviour available only via the contractions. (Likely: no separate op — the
   contractions cover it; revisit only if the book work needs the symmetric grade-0 dot.)

## Not blocking

`add-left-right-contraction.md` can proceed regardless: contractions include grade 0 under **both**
Taylor and galgebra, so that behaviour is unambiguous. This task is about the *plain dot* wrinkle
and how loudly gacalc documents the two conventions coexisting.

## Relationships

- `tasks/reference/contraction-and-dot-definitions.md` — where the resolved understanding lives.
- `tasks/add-left-right-contraction.md` — the feature whose docstrings flag this.
