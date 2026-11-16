# Re-evaluate the 2D quarter turn under the base-case and one-name rules

**Status:** proposed — needs go-ahead (Open questions below block implementation)
**Priority:** 5
**Difficulty:** 4
**Created:** 2026-11-16 (William Emerison Six <billsix@gmail.com>)
**Related:** `tasks/bootstrap-dot-wedge-from-proj-rej.md` (applied the same rules to projection and
rejection); `tasks/bare-2d-bootstrap-pages.md` (the Part III pages)

## BLUF

The maintainer's request (2026-11-16): re-evaluate whether rotation by 90° in 2D should follow the
approach just applied to projection. That approach is: one name for the operation, the base case
stated first under that name, and every version a labelled equation that each use cites. The
maintainer's first thought is yes, because the quarter turn can also be shown to be a product
with `e₁ * e₂` (`e₁₂`, the pseudoscalar `I₂`, the unit bivector `i`). Done means a decision on
each open question, followed by the page, notebook and Lean changes it implies.

## Context

- **The rules being applied** are in `tasks/reference/book-outline.md` ("Pedagogical principles":
  one name per operation; a base case keeps the operation's name) and
  `tasks/reference/reduction-to-standard-position.md` ("Base case, then general case"), whose table
  already lists the quarter turn as the base case of 2D rotation.
- **The quarter turn's versions as of 2026-11-16:**
  - *Coordinates:* `r(v; π/2) = (−v₂, v₁)`. Part III Step 1 (`book/docs/bootstrap-rotation.rst`,
    inside `eq-bootstrap-rotation`), Part I `proof-rotate.rst` and `geometric-product.rst` all
    state it in the same equation as the general `r(v; θ)`. Lean: `rot90`
    (`proofs/GacalcProofs/StandardPosition2D.lean`), documented as "a coordinate swap rather than
    a product with `e₁₂`". Python: `g2.Vector.rotate_90_degrees()`.
  - *Product:* `v * e₁₂`. `geometric-product.rst` introduces `e₁₂` as the thing that "turns `a`
    90°" when multiplied on the right. The Python docstring says `rotate_90_degrees = v * e_12`.
    Part III Step 5 uses `e₁₂ * a = −r(a; π/2)`, Step 6 has `â * b̂ = cos(θ) + sin(θ) * e₁₂`, and
    Lean's `Exp.lean` has `exp(θ * e₁₂) = cos(θ) + sin(θ) * e₁₂`.
  - **No Lean theorem found that `rot90 v = mul v e_12`** for a vector `v`. grep for `rot90_eq`
    and `rot90 … mul` found nothing; confirm before adding one.
- **Ordering constraint.** In Part III the product doesn't exist until Step 4. So the coordinate
  form has to be the base case in Step 1, and `v * e₁₂` can only appear later as a second version
  of `r(v; π/2)`, exactly as Step 5's `(b · a) * a⁻¹` is a later version of `proj_a(b)`.
- **Step 1's order, as noted in `tasks/bootstrap-dot-wedge-from-proj-rej.md`:** Step 1 reads
  `r(v; π/2)` off the general angle-addition derivation instead of stating it first, and the two
  share the `eq-bootstrap-rotation` label.

## Plan (draft; depends on the Open questions)

1. **Step 1:** state `r(v; π/2) = (−v₂, v₁)` first, with its own label (for example
   `eq-bootstrap-quarter-turn`). Justify it directly (from `cos(β + π/2)`, `sin(β + π/2)`, or as
   the turn that swaps the axes), then build `r(v; θ)` on it, citing that label.
2. **The product version:** where the product exists (Step 4 or later), state
   `r(v; π/2) = v * e₁₂` as a labelled second version and cite whichever version each later use
   relies on (Step 5's `e₁₂ * a = −r(a; π/2)`, Step 6).
3. **Lean:** add `rot90_eq_mul_e12` (`IsVector v → rot90 v = mul v e_12`) and cite it. Update
   `rot90`'s doc comment, which today contrasts the swap with the product instead of relating them.
4. **Notebooks:** a symbolic check of `v * e₁₂ = (−v₂, v₁)` in the Step 1 or Step 4 notebook.
5. **Reference docs:** extend the base-case table row for 2D rotation with the product version.
6. **Gates:** `make lean`, `make format`, `make docs`, and a look at the changed PDF pages.

## Open questions

1. **Scope:** Part III only, or also Part I's `proof-rotate.rst` and `geometric-product.rst`,
   which state the quarter turn in the same equation as the general rotation? *(Recommend: Part
   III only, matching the projection task.)*
2. **Name of the pseudoscalar in the product version:** write `v * e₁₂` (the basis-blade name
   Part III already uses), or introduce `I₂` / `i` at that point? *(Recommend: `e₁₂`, with a
   one-line remark that it is the unit bivector, also called `i`. Part III doesn't use `I₂`
   anywhere yet.)*
3. **Where the product version appears:** in Step 4 next to the product's definition, or at its
   first use in Step 5? *(Recommend: Step 4, since `e₁₂` is introduced there.)*
