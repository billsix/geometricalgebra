# Rewrite `left_contraction`/`right_contraction` like `inner_product`/`outer_product` (nested fn + assert)

**Completed:** 2026-07-23

## Starting point

`inner_product` and `outer_product` in `base.py` were written with a **nested helper over a
homogeneous grade-pair** (`inner_product_of_homogenous_multivectors(lhs, rhs)`, reading
`max_grade()` of each, asserting `is_homogeneous_of_grade_r(...)`, returning
`(lhs * rhs).r_vector_part(...)`) summed over `itertools.product(self.grades(), rhs.grades())`. The
newer contractions were a **flat** sum-comprehension with no nested helper and no assert. The
maintainer's belief: the same homogeneous-grade `assert` applies to the contractions, and they
should share the shape.

## What was done

Both `left_contraction` and `right_contraction` in `base.py` were rewritten to mirror
`inner_product`/`outer_product` exactly: a nested `*_of_homogenous_multivectors(lhs, rhs)` helper
(matching the sibling misspelling) that reads `left_grade`/`right_grade` via `max_grade()`, asserts
each operand `is_homogeneous_of_grade_r(...)`, and returns
`(lhs * rhs).r_vector_part(right_grade - left_grade)` (left) / `(left_grade - right_grade)` (right),
with a comment noting `r_vector_part` of a negative grade is zero. The callers pass
`self.r_vector_part(k)` / `rhs.r_vector_part(m)`, which are homogeneous, so the assert is a genuine
invariant check, as in inner/outer. The bilinear `sum` and the `typing.cast(typing.Self, …)` match
inner/outer too.

**Grade-0 inclusion was preserved**: no `if lg > 0 and rg > 0` filter, per Taylor
(`tasks/reference/contraction-and-dot-definitions.md`). Only the structure was aligned, not the
grade set. Base-only; the generated closed-form contractions were out of scope.

## Verification

ruff clean, ty src clean, full suite 297 passed; runtime identical (pure refactor).

**Generated classes were proven unaffected.** `G1`/`G2`/`G3` and their graded subtypes carry their
own closed-form `left_contraction`/`right_contraction` (`__lt__`/`__gt__`), which the generator
derives by **running** `a.left_contraction(b)` / `a.right_contraction(b)` symbolically at generation
time in `tools/gen_specialized.py`, so the refactored base methods execute inside the generator.
The on-disk `g1/g2/g3.py` (generated from the old base.py) were snapshotted, regenerated with the
new base.py (generator `tools/` unchanged, so base.py was the only variable), and diffed: **all
three byte-identical**. The docstrings copied into the generated methods via `inspect.getdoc` were
untouched. The only tracked change was `src/gacalc/base.py`.
