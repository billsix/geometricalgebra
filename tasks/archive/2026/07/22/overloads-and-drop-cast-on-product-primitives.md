# Overloads on `_geometric_product`, and drop the unsound Self cast in the product arms

**Created:** 2026-07-21 · **Completed:** 2026-07-22

The maintainer's batch items 7 and 8, merged. All gates green (283 tests, `ty` src/tests/tools
clean, ruff clean, `check-regions` clean, deterministic; runtime product values unchanged).

## Starting point

`__mul__`/`__xor__`/`outer_product`/`inner_product` had `@typing.overload`s
(`tasks/reference/generated-product-typing.md`), but the internal primitive **`_geometric_product`
did not**: it returned `-> typing.Self` and each arm did `typing.cast(typing.Self, Rotor2(...))`,
an unsound cast (a `Rotor2` asserted to be a `Vector2`). `outer_product`/`inner_product`/
`__add__`/`__sub__` had overloads and `-> MultiVectorBase` impls but their arms still cast to
`typing.Self` (e.g. `__sub__`'s scalar arm `typing.cast(typing.Self, G2(coeff_scalar=-rhs, …))`),
redundant and dishonest. The cast came from `dispatch_method` passing `cast=cast_self` and
`result_block_stmts` wrapping each grade-changing arm in `cast(construct(...))`.

## What shipped

- **`_geometric_product` overloaded + returns `MultiVectorBase`** (like `__mul__`/`outer`/`inner`/
  `add`/`sub`): `product_overload_stubs("_geometric_product", …)` and `return_type=mvb_ann` on its
  `dispatch_method` call. `a._geometric_product(b)` reveals as `Rotor2`.
- **The unsound `Self` cast was dropped** from the grade-changing arms: `result_block_stmts`' else
  branch emits `return Rotor2(...)` (no cast), and `dispatch_method`'s `case _:` Gn-fallback drops
  the cast for the overloaded products/sums (`return_type is not None and cast is cast_self`). The
  full class (`-> Self`) and the sandwich (`cast_operand`) keep theirs. The `-> MultiVectorBase`
  impl return is what makes the un-cast concrete `return` legal.
- The same-type arms' `type(self)(...)` were left alone here; they were decided by
  `tasks/archive/2026/07/22/finalize-graded-types.md` (item 9).
- Result: **all product/sum methods on the graded types are cast-free.** In `g2.py`, Vector2 went
  10→5 `cast(typing.Self`; the remaining 5 were `even_part`/`r_vector_part` (unary grade ops) and
  `dual` (dimension method), out of scope for a products task.
- Runtime unchanged (impl `match` bodies untouched); the full class `G_n` untouched.

**Files:** `tools/gen_specialized.py` (overload `_geometric_product`; drop the cast in
`result_block_stmts` else + the `dispatch_method` fallback).

## Follow-ups (the remaining graded `Self` casts), spun into their own task docs

- **`r_vector_part`** → `tasks/archive/2026/07/22/overload-r-vector-part.md` (same overload
  technique keyed on `r: Literal[<grade>]`; impl `-> MultiVectorBase`, `Scalar(0)` cast dropped).
- **`even_part` / `odd_part`** → `tasks/archive/2026/07/22/retype-even-odd-part-off-self.md`
  (needed re-typing `base.even_part`/`odd_part` off `-> Self`; no argument to overload on).
- **`dual`** → owned by `tasks/archive/2026/07/22/generated-dimension-known-methods.md` (items
  4/5/11) and `tasks/archive/2026/07/22/precise-dual-typing.md`.
