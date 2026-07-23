# Rewrite `left_contraction`/`right_contraction` like `inner_product`/`outer_product` (nested fn + assert)

**Status:** complete
**Completed:** 2026-07-23

## Done

Both `left_contraction` (`base.py:415`) and `right_contraction` (`:439`) now mirror
`inner_product`/`outer_product` exactly: a nested `*_of_homogenous_multivectors(lhs, rhs)`
helper (matching the sibling misspelling) that reads `left_grade`/`right_grade` via
`max_grade()`, asserts each operand `is_homogeneous_of_grade_r(...)`, and returns
`(lhs * rhs).r_vector_part(right_grade - left_grade)` (left) / `(left_grade - right_grade)`
(right) — with a comment noting `r_vector_part` of a negative grade is zero. The bilinear
`sum` over `itertools.product(self.grades(), rhs.grades())` and the `typing.cast(typing.Self, …)`
match inner/outer too. **Grade-0 inclusion preserved** — no `if lg > 0 and rg > 0` filter, per
Taylor (see `tasks/reference/contraction-and-dot-definitions.md`). Base-only; the generated
closed-form contractions were out of scope and untouched. Gates: ruff clean, ty src clean,
full suite 297 passed. Runtime identical (pure refactor).

### Generated classes verified unaffected

`G1`/`G2`/`G3` (and their graded subtypes) **do** carry their own closed-form
`left_contraction`/`right_contraction` (`__lt__`/`__gt__`), and the generator *derives* them by
**running** `a.left_contraction(b)` / `a.right_contraction(b)` symbolically at generation time
(`tools/gen_specialized.py:1889`, `:2213`), so the refactored base methods execute inside the
generator. Because the refactor is behavior-preserving — and the `left_/right_contraction`
docstrings (copied to the generated methods via `inspect.getdoc`) were not touched — the emitted
code doesn't move. **Proven, not assumed:** snapshotted the on-disk `g1/g2/g3.py` (generated from
the *old* base.py), regenerated with the *new* base.py (generator `tools/` unchanged this turn, so
base.py was the only variable), and diffed — **all three byte-identical**. The only change that
lands is `M src/gacalc/base.py`; the generated `.py` are gitignored artifacts and show nothing in
`git diff`.

## Original task


## Goal

`inner_product` and `outer_product` (`base.py:334`, `:367`) are written with a **nested helper over a
homogeneous grade-pair** plus **homogeneity `assert`s**:

```python
def inner_product_of_homogenous_multivectors(lhs, rhs) -> MultiVectorBase:
    left_grade = lhs.max_grade()
    right_grade = rhs.max_grade()
    assert lhs.is_homogeneous_of_grade_r(left_grade)
    assert rhs.is_homogeneous_of_grade_r(right_grade)
    return (lhs * rhs).r_vector_part(abs(left_grade - right_grade))
inner = sum([inner_product_of_homogenous_multivectors(self.r_vector_part(lg), rhs.r_vector_part(rg))
             for lg, rg in itertools.product(self.grades(), rhs.grades()) if lg > 0 and rg > 0], ...)
```

The two newer contractions `left_contraction`/`right_contraction` (`base.py:415`, `:439`) are instead
a **flat** sum-comprehension with **no nested helper and no assert**:

```python
return sum([(self.r_vector_part(k) * rhs.r_vector_part(m)).r_vector_part(m - k)
            for k, m in itertools.product(self.grades(), rhs.grades())], start=type(self).zero())
```

**Bill's belief:** the same homogeneous-grade `assert` applies to the contractions too, and they
should be written in the same shape. See if they can be — a nested
`contraction_of_homogeneous_multivectors(lhs, rhs)` with the `is_homogeneous_of_grade_r` asserts, then
the same grade-pair sum.

## Investigate / do

- Extract a nested helper in each contraction that takes a homogeneous `lhs`/`rhs`, asserts each is
  homogeneous of its `max_grade()`, and returns `(lhs * rhs).r_vector_part(m - k)` (left) /
  `.r_vector_part(k - m)` (right).
- Confirm the asserts hold (the callers already pass `self.r_vector_part(k)` / `rhs.r_vector_part(m)`,
  which *are* homogeneous — so the assert is a genuine invariant check, exactly like inner/outer).
- Note the **grade-0 difference from `inner_product`**: contractions **include** grade 0 (no
  `if lg > 0 and rg > 0` filter — Taylor, see the docstrings + `tasks/reference/contraction-and-dot-definitions.md`).
  Preserve that; only the *structure* (nested fn + assert) is being aligned, not the grade set.

## Verify

Pure refactor — runtime unchanged. `ty`/ruff clean; the contraction suites
(`tests/test_operator_typing.py`, `tests/test_graded.py`, conformance) stay green.

## Relationships

- `tasks/reference/contraction-and-dot-definitions.md` (the contraction vs dot definitions + grade-0
  inclusion).
- The pattern source: `inner_product`/`outer_product` in `base.py`.
