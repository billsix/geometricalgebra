# Add left & right contraction (named methods + `<` / `>` operators)

**Created:** 2026-07-22 · **Completed:** 2026-07-22

Promoted Finding 2A of `tasks/reference/galgebra-comparison.md` (the single biggest *operation*
gap). Domain detail lives in `tasks/reference/contraction-and-dot-definitions.md`. All gates green
(295 tests incl. 8 new contraction tests, `ty` src/tests/tools clean, ruff clean, `check-regions`
clean, deterministic; generated-vs-`Gn` parity verified over 200 random cases).

## The definitions

**M.D. Taylor, *An Introduction to Geometric Algebra and Geometric Calculus*, 2021, p. 103.** For
homogeneous parts `A_k` (grade `k`) and `B_m` (grade `m`), summed bilinearly over all parts:

- **Left contraction:** `A_k ⌋ B_m = ⟨A_k B_m⟩_{m−k}`, zero when `m − k < 0`.
- **Right contraction:** `A_k ⌊ B_m = ⟨A_k B_m⟩_{k−m}`, zero when `k − m < 0`.

**galgebra 0.6.0 confirms these exactly** (`galgebra/ga.py`): `_LeftContractFunction._result_grade
= grade2 − grade1` (None→0 if negative); `_RightContractFunction._result_grade = grade1 − grade2`.
galgebra's `Mv.__lt__` / `Mv.__gt__` are the left / right contraction (`galgebra/mv.py`).

## The grade-0 caveat

Taylor's definitions **include grade 0**, and so does galgebra (no `grade==0` guard). The **Hestenes
dot / gacalc `inner_product` EXCLUDES grade 0** (Hestenes 1.21b, implemented as
`if lg > 0 and rg > 0` in `base.inner_product`; galgebra's own `_HestenesDotFunction` returns None
when either grade is 0). So the contractions are not the same operation as `inner_product`, and
they treat scalars differently. Taylor also calls grade 0 part of the *dot* product, conflicting with
Hestenes' "dot undefined for scalars". The docstrings say so and point at
`tasks/archive/2026/07/22/investigate-dot-product-grade-0.md` and
`tasks/reference/contraction-and-dot-definitions.md`.

## What shipped

- **`base.py`**: `left_contraction`/`right_contraction` (bilinear sum over
  `itertools.product(self.grades(), rhs.grades())`, grade `m−k` / `k−m` via `r_vector_part`, which
  already returns zero for a negative grade; **no grade-0 filter**), and `__lt__`/`__gt__`
  delegating to them (parallel to `__xor__` → `wedge`). Docstrings cite Taylor 2021 p.103 + galgebra
  and carry the grade-0 caveat. No `cast` was needed: the `r_vector_part` chain already types as
  `Self`, so `return sum(...)` directly.
- **Generator** (per the maintainer: "add these to the generators too"): the full class `G_n` got
  `bilinear` closed forms for both; the graded types got the **same `product_overload_stubs` +
  `dispatch_method` treatment as `inner_product`/`outer_product`** (precise per-rhs overloads, fast
  closed-form dispatch), plus overloaded, delegating `__lt__`/`__gt__` (mirroring `__xor__`). So
  `Vector2.left_contraction(Bivector2) -> Vector2`, `Vector2 < Vector2 -> Scalar`, etc., are precise
  for `ty`. (The original sketch had left the generator fast path as an optional follow-up.)
- **Tests**: `test_conformance.py::test_left_right_contraction` (parity over `[Gn,G1,G2,G3]`,
  methods + operators, incl. the grade-0 behaviour that distinguishes it from `inner_product`);
  `test_operator_typing.py` static `assert_type` + runtime known-value tests.
- **Docs**: `README` + `CLAUDE.md` operator lists (`<` / `>`); `galgebra-comparison.md` Finding 2A
  marked done; `contraction-and-dot-definitions.md` status updated.

## Decisions

- **Names: `left_contraction`/`right_contraction`** (the maintainer's pick), the gacalc `*_product`
  noun style, over galgebra's `left_contract`/`right_contract`.
- **`__lt__`/`__gt__` return a multivector, not `bool`**, intentionally, matching galgebra. `ty`
  accepts it, and nothing sorts multivectors (dataclass `eq=False`, no `order=`; `<`/`>` had raised
  `TypeError` before), so no comparison semantics were broken.

## Related

- `tasks/reference/contraction-and-dot-definitions.md`: the domain note (definitions + grade-0).
- `tasks/archive/2026/07/22/investigate-dot-product-grade-0.md`: the definitional investigation.
- `tasks/reference/galgebra-comparison.md`: Finding 2A (origin).
