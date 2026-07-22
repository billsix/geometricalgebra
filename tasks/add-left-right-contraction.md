# Add left & right contraction (named methods + `<` / `>` operators)

**Status:** proposed — needs go-ahead (spec only; implementation deliberately deferred — see note).
Created 2026-07-22. Promotes Finding 2A of `tasks/reference/galgebra-comparison.md` (the single
biggest *operation* gap). Domain detail lives in `tasks/reference/contraction-and-dot-definitions.md`.

> **Not yet implemented** — Bill was mid history-rewrite/push when this was written, so no tracked
> source was touched (a `git reset --hard` would discard uncommitted edits). Implement after the push.

## Goal

Add the **left contraction** `A ⌋ B` and **right contraction** `A ⌊ B` as first-class named
methods, and overload `<` / `>` to call them — mirroring how `^` / `wedge` / `outer_product` relate,
and matching **galgebra** (`Mv.__lt__` = left contraction `<`, `Mv.__gt__` = right contraction `>`,
`galgebra/mv.py:852,872`).

## The definitions (cite these in the docstrings)

**M.D. Taylor, *An Introduction to Geometric Algebra and Geometric Calculus*, 2021, p. 103.** For
homogeneous parts `A_k` (grade `k`, left) and `B_m` (grade `m`, right):

- **Left contraction:** `A_k ⌋ B_m = ⟨A_k B_m⟩_{m−k}` — the grade-`(m−k)` part of the geometric
  product; zero when `m − k < 0`.
- **Right contraction:** `A_k ⌊ B_m = ⟨A_k B_m⟩_{k−m}` — the grade-`(k−m)` part; zero when
  `k − m < 0`.

Summed bilinearly over all homogeneous parts of `A` and `B`.

**galgebra 0.6.0 confirms these exactly** (`galgebra/ga.py`): `_LeftContractFunction._result_grade
= grade2 − grade1` (None→0 if negative); `_RightContractFunction._result_grade = grade1 − grade2`.
Neither special-cases grade 0.

## The grade-0 caveat (must be in the docstrings + flagged for investigation)

Taylor's definitions **include grade 0** in the source-component loop, and so does galgebra
(its contraction `_result_grade` has no `grade==0` guard). But the **Hestenes dot / gacalc
`inner_product` EXCLUDES grade 0** — Hestenes 1.21b, implemented as `if lg > 0 and rg > 0` in
`base.inner_product`, and galgebra's own `_HestenesDotFunction._result_grade` literally does
`if grade1 == 0 or grade2 == 0: return None`. So the contractions are **not** the same operation as
gacalc's existing `inner_product`, and they treat scalars differently. The docstrings must:
- cite Taylor p. 103 and note galgebra agrees;
- state plainly that the contractions **include grade 0**, unlike the Hestenes dot (`inner_product`),
  which does not — and that Taylor also calls grade 0 part of the *dot* product, conflicting with
  Hestenes' "dot undefined for scalars";
- say **this discrepancy may warrant further investigation** → see
  `tasks/investigate-dot-product-grade-0.md` and
  `tasks/reference/contraction-and-dot-definitions.md`.

## Plan (sketch)

1. **`base.py` (`MultiVectorBase`)** — add `left_contraction`/`right_contraction`, structured exactly
   like `inner_product`/`outer_product` (a `_of_homogeneous` inner helper using `max_grade()` +
   `r_vector_part(m − k)` / `r_vector_part(k − m)`; `r_vector_part` of a negative grade already
   returns zero, so no explicit sign guard needed). **Do NOT filter grade 0** (unlike
   `inner_product`) — loop over `itertools.product(self.grades(), rhs.grades())` with no `>0` guard.
   Names: `left_contraction`/`right_contraction` (noun form, matching `outer_product`); reconsider
   vs galgebra's `left_contract` if Bill prefers.
2. **Operators on `base.py`** — `__lt__` → `left_contraction`, `__gt__` → `right_contraction`
   (parallel to `__xor__` → `wedge`). Docstring the operator form (`a < b == a.left_contraction(b)`).
   Verify nothing relied on `<`/`>` for multivectors (dataclass `eq=False`, no `order=` → they
   currently raise `TypeError`, so this is safe — confirm at implementation time).
3. **Generated classes** — they inherit the base methods/operators for free (MVP). A **closed-form
   fast path + precise `@overload` typing** in the generator is an *optional follow-up* (perf is
   opportunistic; fast paths only in generated classes — see memory). Not required for correctness.
4. **Docstrings** — Taylor p. 103 reference + the grade-0 caveat above, on both methods.
5. **Tests** — a `test_contraction.py`: symmetry/known-value checks (e.g. for vectors `a ⌋ b ==
   a · b`; `a ⌋ B` for a bivector; contraction asymmetry: `bivector ⌋ vector == 0`), across
   `[Gn, G1, G2, G3]` (conformance-style), incl. the grade-0 behaviour that distinguishes it from
   `inner_product`.
6. **Docs** — update `tasks/reference/galgebra-comparison.md` Finding 2A / the table row (mark
   contractions as done, cross-link) and `README`/`CLAUDE.md` operator list (`<` / `>`).
7. Regenerate; `ty`/ruff/pytest/`check-regions`/determinism all green.

## Open question

1. Method names: `left_contraction`/`right_contraction` (gacalc `*_product` noun style, my rec) vs
   galgebra's `left_contract`/`right_contract`?

## Relationships

- `tasks/reference/contraction-and-dot-definitions.md` — the domain note (definitions + grade-0).
- `tasks/investigate-dot-product-grade-0.md` — the deferred definitional investigation.
- `tasks/reference/galgebra-comparison.md` — Finding 2A (origin).
