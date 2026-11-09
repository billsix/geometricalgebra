# Give the generated `ScalarN` classes the `@typing.overload` product signatures

**Completed:** 2026-07-23

## Starting point

The generated graded types carried `@typing.overload`s on their bilinear products
(`tasks/reference/generated-product-typing.md`); the per-algebra `Scalar1`/`Scalar2`/`Scalar3` did
not. `ScalarN` was emitted by the bespoke `generate_scalar(n, name, full_name)`, which hand-wrote
`__mul__` / `_geometric_product` / `outer_product` / `inner_product` / `__add__` / `__sub__` with
plain `-> typing.Self` (and, on the general-multivector arm, an unsound `cast(Self, coeff * rhs)`),
and never called `product_overload_stubs(...)`. So `Scalar * X` mistyped as `ScalarN`. The scalar
result rule is known at gen time: `ScalarN * X` is grade-preserving scaling → X's type.

## What was done

Rather than bolting overloads onto the hand-written impls, `generate_scalar`'s arithmetic was routed
through the **same `product_overload_stubs` + `dispatch_method`** the graded generator uses,
replacing the bespoke methods. The approach was first verified with a
`dispatch_method`-on-`scalar_spec` spike.

- Result: `Scalar2 * Vector2 → Vector2`, `Scalar2 * Bivector2 → Bivector2`,
  `Scalar3 * Trivector3 → Trivector3`, `Scalar2 + Bivector2 → Rotor2`, `Scalar2 + Vector2 → G2`,
  `Scalar2.inner_product(X) → Scalar2`, precise for `ty`.
- The impls return `-> MultiVectorBase`, construct the resolved concrete type per rhs, and the
  `case _` **coerces a foreign/`Gn` operand to `G_n`** (so `Scalar2 * Gn → G2`, matching the
  catch-all; the old body returned a bare `Gn`).
- Reflected ops (`__rmul__`/`__radd__`/`__rsub__`) were left as-is; they were the separate
  `tasks/archive/2026/07/23/reflected-operator-typing-overloads.md`.

Design + rationale were harvested to `tasks/reference/generated-product-typing.md` (the "ScalarN as
a product lhs" section), including the one remaining gap: **ScalarN contractions** (`<`/`>`) were
still inherited from `base` (`-> Self`) and mistyped, noted there as an optional follow-up outside
this task's product/sum scope.

## Verification

ruff clean · ty src/tests/tools clean · full suite 297 + operator-typing 13 pass (new
`test_scalar_lhs_static_types` / `…_runtime_types_and_values` guard the static + runtime types) ·
doc-regions clean (overload stubs correctly skipped) · generation deterministic. Runtime
value-identical (conformance green). Generator-only change (`tools/gen_specialized.py`).

## Related

- `tasks/archive/2026/07/22/per-algebra-scalar-types.md` (the per-algebra `ScalarN` split).
- Sibling: `tasks/archive/2026/07/23/reflected-operator-typing-overloads.md`.
