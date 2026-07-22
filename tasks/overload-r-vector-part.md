# Precise `r_vector_part` via `Literal[grade]` overloads (drop the `Scalar(0)` cast)

**Status:** proposed — needs go-ahead. Created 2026-07-22. (Follow-up spun from
`overloads-and-drop-cast-on-product-primitives`, which cleaned the *product* arms; this does the
same for the one remaining graded op that has an argument to overload on.)

## Goal

Give the generated `r_vector_part(r)` precise return types and drop its unsound `Scalar(0)` cast —
using the **same `@typing.overload` technique as the products**, just keyed on an *int literal*
(`r: Literal[<grade>]`) instead of an operand *type*.

## What's there now (verified in `g2.py`)

`r_vector_part(self, r: int) -> typing.Self` — an `if r == <grade>:` branch per grade the type
carries (each returning that grade's part), then a fallback `return typing.cast(typing.Self,
Scalar(coeff_scalar=cast(Coef, 0)))` for absent grades. E.g. `Vector2.r_vector_part`: `if r == 1:
return Vector2(...)` (present, concrete since Vector2 is `@final`), else `cast(Self, Scalar(0))`.
The absent-grade fallback is the unsound cast (a `Scalar` asserted to be a `Vector2`).

## Plan (sketch — mirrors the product overloads)

1. **Emit `@typing.overload` per grade** `0..DIMENSION`, mapping `r: Literal[<grade>]` to the
   resolved grade-`r`-part type: the graded type covering that grade's blades **if the class has
   it** (`Vector2.r_vector_part(Literal[1]) -> Vector2`; `Rotor2.r_vector_part(Literal[0]) ->
   Scalar`, `Literal[2] -> Bivector2`), else `-> Scalar` (absent grade → `Scalar(0)`). The
   generator already computes these branches (`rvp_body`), so the per-grade type is in hand.
2. **Impl `-> MultiVectorBase`** (like the products), then **drop the `Scalar(0)` cast** — return
   `Scalar(coeff_scalar=0)` directly (sound: `Scalar <: MultiVectorBase`). The present-grade
   branches already build the concrete type with no cast (post-finalize).
3. Optionally a `MultiVectorBase` catch-all overload for a non-literal `r: int`.
4. Regenerate; `ty` clean; `reveal_type(v.r_vector_part(1))` precise; suite/regions/determinism.

## Notes

- Same soundness/typing story as `tasks/reference/generated-product-typing.md`; no base change
  needed (overloads are additive over `base.r_vector_part(self, r) -> Self`).
- **`even_part`/`odd_part` can't use this** — they take no argument, so there's no `Literal` key;
  they need a base retype (see `retype-even-odd-part-off-self.md`).
