# Overloads on `_geometric_product`, and drop the unsound Self cast in the product arms

**Status:** complete
**Completed:** 2026-07-22
All gates green (283 tests, `ty` src/tests/tools clean, ruff clean, `check-regions` clean,
deterministic; runtime product values unchanged). Created 2026-07-21. (Bill's batch items 7, 8 —
merged.)

## Outcome (2026-07-22)

- **`_geometric_product` overloaded + returns `MultiVectorBase`** (like `__mul__`/`outer`/`inner`/
  `add`/`sub`): added `product_overload_stubs("_geometric_product", …)` and `return_type=mvb_ann`
  to its `dispatch_method` call. Verified `a._geometric_product(b)` now reveals as `Rotor2`.
- **Dropped the unsound `Self` cast** from the grade-changing arms: `result_block_stmts`' else
  branch now emits `return Rotor2(...)` (no cast); and `dispatch_method`'s `case _:` Gn-fallback
  drops the cast for the overloaded products/sums (`return_type is not None and cast is cast_self`)
  — the full class (`-> Self`) and the sandwich (`cast_operand`) keep theirs.
- Result: **all product/sum methods on the graded types are cast-free.** In `g2.py`, Vector2 went
  10→5 `cast(typing.Self`; the remaining 5 are `even_part`/`r_vector_part` (unary grade ops) and
  `dual` (dimension method) — **out of scope for a *products* task** (see the follow-ups).
- Runtime unchanged (impl `match` bodies untouched); the full class `G_n` untouched.

**Files:** `tools/gen_specialized.py` (overload `_geometric_product`; drop the cast in
`result_block_stmts` else + the `dispatch_method` fallback).

## Follow-ups (the remaining graded `Self` casts) — spun into their own task docs

- **`r_vector_part`** → `tasks/overload-r-vector-part.md` (same overload technique, keyed on
  `r: Literal[<grade>]`; impl `-> MultiVectorBase`, drop the `Scalar(0)` cast; no base change).
- **`even_part` / `odd_part`** → `tasks/retype-even-odd-part-off-self.md` (needs re-typing
  `base.even_part`/`odd_part` off `-> Self` — no argument to overload on).
- **`dual`** → owned by `generated-dimension-known-methods` (items 4/5/11).

## Goal

Finish the precise-typing work: `__mul__`/`__xor__`/`outer_product`/`inner_product` got
`@typing.overload`s (see `tasks/reference/generated-product-typing.md`), but the internal
primitive **`_geometric_product` did not** — it still returns `-> typing.Self` and each arm does
`typing.cast(typing.Self, Rotor2(...))` (the unsound cast: a `Rotor2` asserted to be a `Vector2`).
Give `_geometric_product` the same overloads, and drop the now-redundant/unsound `Self` cast from
the arms of **all** the dispatch methods (their impls already return `-> MultiVectorBase`, so an
arm can just `return Rotor2(...)`).

## What's there now (verified in generated `g2.py`)

- `_geometric_product(self, rhs) -> typing.Self:` — **no overloads**; arms are
  `return typing.cast(typing.Self, Rotor2(...))`.
- `outer_product`/`inner_product`/`__add__`/`__sub__` **do** carry overloads and their impls
  return `-> MultiVectorBase`, **but their arms still cast to `typing.Self`** — e.g. `__sub__`'s
  scalar arm is `return typing.cast(typing.Self, G2(coeff_scalar=-rhs, …))`. Since the method
  returns `MultiVectorBase`, that cast is redundant *and* dishonest (Rotor2/G2 aren't `Self`).
- The cast comes from `dispatch_method` passing `cast=cast_self` and `result_block_stmts` wrapping
  each grade-changing arm in `cast(construct(...))`.

## Plan (sketch)

1. **Overload `_geometric_product`** via `product_overload_stubs` (as `__mul__` etc. already do),
   set its impl return to `MultiVectorBase`.
2. **Drop the arm cast.** For grade-changing arms (`result != self`), emit `return Rotor2(...)`
   instead of `return typing.cast(typing.Self, Rotor2(...))`. The same-type arms already build via
   `type(self)(...)` — leave those (subclass preservation; and see the separate
   `concrete-type-vs-type-self.md` task for whether *those* change). The `MultiVectorBase` impl
   return makes the concrete `return` type-check with no cast.
3. Regenerate; verify runtime is byte-identical in behavior (289-test suite + conformance); `ty`
   src/tests/tools clean; `reveal_type(a._geometric_product(b))` → the precise type.

## Notes / caveats

- **Keep the same-type arm's `type(self)(...)`** (or defer to the type(self) task) — dropping the
  cast is about the *grade-changing* arms, which never had subclass preservation anyway.
- Confirm dropping the cast doesn't reintroduce a `ty` complaint; the `-> MultiVectorBase` impl is
  what makes the un-cast concrete `return` legal (that pairing was the whole point of the earlier
  broadening — see `tasks/reference/generated-product-typing.md`).

## Relationships

- Direct continuation of the operator-overload work in
  `tasks/reference/generated-product-typing.md`.
- Interacts with **`concrete-type-vs-type-self.md`** (item 9) — that one decides the same-type
  arms; this one only touches the grade-changing arms + `_geometric_product`.
