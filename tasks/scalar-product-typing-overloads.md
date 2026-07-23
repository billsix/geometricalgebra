# Give the generated `ScalarN` classes the `@typing.overload` product signatures

**Status:** proposed — needs go-ahead. Created 2026-07-23 (Bill).

## Goal

The generated **graded** types (`Vector2`/`Bivector2`/`Rotor2`, the 𝒢₃ set) carry `@typing.overload`
signatures on their bilinear products, so a known-type call types precisely (`v2 * v2 → Rotor2`,
etc. — see `tasks/reference/generated-product-typing.md`). The per-algebra **`Scalar1`/`Scalar2`/
`Scalar3`** types do **not**. Determine *why*, and give them the overloads **if we can**, so e.g.
`Scalar2 * Vector2` types statically as `Vector2`, `Scalar2 * Bivector2` as `Bivector2`, `Scalar3 *
Trivector3` as `Trivector3`, `Scalar2 * Scalar2` as `Scalar2`.

## Why they don't have them now (starting point)

`ScalarN` is emitted by the **bespoke** `generate_scalar(n, name, full_name)`
(`tools/gen_specialized.py:1216`), which hand-writes `__mul__` / `_geometric_product` /
`outer_product` / `inner_product` / `__add__` / … with plain `-> typing.Self` (and, for the
general-multivector arm, an unsound `cast(Self, coeff * rhs)`). It does **not** call
`product_overload_stubs(...)` (`:1163`), which is what `generate_graded_type` uses (`:2114`) to emit
the per-rhs `@overload`s. So the scalar products aren't precise, and `Scalar * X` still mistypes as
`ScalarN` (or is cast).

## Investigate

- Can `generate_scalar` reuse `product_overload_stubs` / the same `product_result` resolution? The
  scalar result rule is simple and known: `ScalarN * X` (X graded/full) is grade-preserving scaling →
  X's type; `ScalarN * ScalarN → ScalarN`; `ScalarN * number → ScalarN`. So the overload set is one
  per rhs type (all the algebra's types) + the number case, all resolvable at gen time.
- The wrinkle: `generate_scalar` is hand-built (not the `match`-dispatch machinery of
  `generate_graded_type`), so the overloads must be bolted onto its existing hand-written impls (which
  keep the inline `if isinstance(rhs, …)` bodies). Confirm the impl return can broaden to
  `MultiVectorBase` (like the graded impls) so the overloads are consistent + the `cast(Self, …)` on
  the general arm drops.
- Also fold in `__add__`/`__sub__` if the same applies (Scalar + Bivector2 → Rotor2, etc.).

## Verify

`ty` src/tests/tools clean; add `assert_type` guards (`Scalar2 * Vector2 → Vector2`, …) to
`tests/test_operator_typing.py`; suite/regions/determinism green; runtime unchanged.

## Relationships

- `tasks/reference/generated-product-typing.md` (the overload design + the `ScalarN`-as-lhs note under
  "Not yet done").
- `tasks/archive/2026/07/22/per-algebra-scalar-types.md` (the per-algebra `ScalarN` split).
- Sibling: `tasks/reflected-operator-typing-overloads.md` (the `__radd__`/`__rmul__` question).
