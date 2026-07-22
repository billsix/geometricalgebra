# Contraction & dot-product definitions (Taylor, Hestenes, galgebra) — and the grade-0 wrinkle

**Reference document** — durable domain notes on the inner-product family (dot, left/right
contraction, scalar product) and how the sources differ on **grade 0**. Consult before touching or
extending gacalc's inner products. Not a task. Created 2026-07-22 (from reading Taylor 2021 p. 103,
Hestenes & Sobczyk, and galgebra 0.6.0 source). Related: `galgebra-comparison.md` (Finding 2A),
`tasks/add-left-right-contraction.md`, `tasks/investigate-dot-product-grade-0.md`.

## The operations, by which grade of the geometric product they keep

For homogeneous parts `A_k` (grade `k`) and `B_m` (grade `m`), each product keeps one grade of the
geometric product `A_k B_m` and sums bilinearly over all homogeneous parts:

| operation | grade kept | zero when | grade 0 in the loop? |
|---|---|---|---|
| outer / wedge `∧` | `k + m` | `k + m > n` | **yes** (`base.outer_product`) |
| Hestenes inner / dot `·` | `|k − m|` | — | **no** — excluded (`base.inner_product`, `if lg>0 and rg>0`) |
| **left contraction `⌋`** | `m − k` | `m − k < 0` | **yes** |
| **right contraction `⌊`** | `k − m` | `k − m < 0` | **yes** |
| scalar product `∗` | `0` | `k ≠ m` | (grade-0 result by definition) |

## Sources

- **M.D. Taylor, *An Introduction to Geometric Algebra and Geometric Calculus*, 2021, p. 103** —
  defines left contraction as the grade-`(m−k)` part and right contraction as the grade-`(k−m)`
  part (m = right grade, k = left grade), and **includes grade 0** in the source-component loop.
- **Hestenes & Sobczyk, *Clifford Algebra to Geometric Calculus*** — the inner/dot product
  (eq. 1.21) is `⟨A_k B_m⟩_{|k−m|}` but **not defined for grade 0** (a scalar has no inner product).
  This is the convention gacalc's `inner_product`/`dot` follow today.
- **galgebra 0.6.0** (`galgebra/ga.py`) — encodes all of these as `_SingleGradeProductFunction`
  subclasses differing only in `_result_grade(grade1, grade2)`:
  - `_HestenesDotFunction`: `if grade1 == 0 or grade2 == 0: return None` else `abs(g1−g2)` — **grade 0 excluded**.
  - `_LeftContractFunction`: `g2 − g1`, `None` if `< 0` — **grade 0 included**.
  - `_RightContractFunction`: `g1 − g2`, `None` if `< 0` — **grade 0 included**.
  - `_WedgeProductFunction`: `g1 + g2`, `None` if `> n`.
  - `_ScalarProductFunction`: `0`.
  galgebra's operators (`galgebra/mv.py`): `Mv.__lt__` = `<` = left contraction; `Mv.__gt__` = `>` =
  right contraction (both delegate to `Ga.left_contract` / `Ga.right_contract`).

## The grade-0 wrinkle (the thing to keep straight)

**The contractions and the Hestenes dot treat scalars differently, on purpose.** Taylor and galgebra
**agree** the contractions include grade 0; Hestenes (and gacalc's `inner_product`) exclude it from
the plain dot. So once gacalc has contractions, `a.inner_product(s)` (scalar `s`) and
`a.left_contraction(s)` will **not** match — that's expected, not a bug.

A separate, softer discrepancy: Taylor reportedly also calls grade 0 part of the plain *dot*
product, which conflicts with Hestenes ("dot undefined for scalars"). gacalc keeps the Hestenes
convention for `inner_product`. Whether that plain-dot difference matters (or wants a second,
grade-0-including "dot") is **open** — tracked in `tasks/investigate-dot-product-grade-0.md`. It does
**not** block implementing the contractions (their grade-0 behaviour is unambiguous across sources).

## gacalc status

- Has: `outer_product`/`wedge`/`^`, `inner_product`/`dot` (Hestenes, grade-0-excluded),
  `scalar_product`, and (2026-07-22) **`left_contraction`/`right_contraction` + the `<` / `>`
  operators** — on `MultiVectorBase` (the general path) and with generated closed-form fast paths +
  precise `@overload` typing on the specialized classes (`Vector2.left_contraction(Bivector2) ->
  Vector2`, `Vector2 < Vector2 -> Scalar`, etc.). Grade `m−k` (left) / `k−m` (right), grade 0
  included; the impl is `base.left_contraction`/`right_contraction`, a bilinear sum with **no**
  grade-0 filter (contrast `inner_product`'s `if lg>0 and rg>0`).
- Open: the plain-dot grade-0 question (`tasks/investigate-dot-product-grade-0.md`).
