# Type-precise products/sums on the generated graded types

**Status:** DONE 2026-07-21. The operators and named products/sums on the generated graded types
now type precisely and soundly (`v2 * v2 : Rotor2`, `v2 ^ v2 : Bivector2`, `2 + 3*i2 : Rotor2`)
instead of the old unsound `-> Self`. Gates green: 289 tests, `ty` src/tests/tools clean, ruff
clean, `check-regions` clean, deterministic.

> **Design rationale, decisions, and rejected alternatives live in
> `tasks/reference/generated-product-typing.md`** (kept as durable reference). This doc is just
> the work record.

## What shipped

Every generated graded type's product/sum methods (`__mul__`, `__xor__`, `outer_product`,
`inner_product`, `__add__`, `__sub__`, and `__radd__`/`__rsub__`) now carry `@typing.overload`
signatures returning the resolved concrete type. Runtime is unchanged — the overloads only supply
precise static types. Full details and the "why" are in the reference doc above.

## Paths tried (work log)

1. **Path 1 — free functions + delegation (built, then reverted).** Per-pair free functions
   (`geometric_product_vector2_vector2 -> Rotor2`) + an overloaded front per op + generic-`match`
   delegation, leaving the operators untouched. Surfaced the `Scalar`-as-lhs unsoundness (scalar.py
   coerces zero results to `Gn`). Worked (388 tests) but **left `v2 * v2` still mistyped as
   `Vector2`** → Bill had it reverted, along with its test `tests/test_typed_products.py`.
2. **Path 2 — overload the operators directly (shipped).** Enabled by verifying (contra an earlier
   wrong assumption) that `ty` accepts subclass `@overload`s returning non-`Self` over a `-> Self`
   base, soundly. `@overload`s went onto `__mul__`/`__xor__`/`outer_product`/`inner_product`.
3. **`+` / `-` extension.** Overloaded `__add__`/`__sub__` and typed `__radd__`/`__rsub__` so
   `scalar + bivector` and all four `±` orderings narrow to `Rotor2`.
4. **Impl-return broadening to `MultiVectorBase`.** Retyped the six overloaded impls from `-> Self`
   to `-> MultiVectorBase` (the one common supertype of the overload returns; `G2` was tried and
   rejected — the graded types are siblings of `G2`, not subclasses).

## Files changed

- `tools/gen_specialized.py` — `product_overload_stubs(...)`, wired onto the six methods; impls set
  to `-> MultiVectorBase`; `__radd__`/`__rsub__` typed to the resolved `self ± scalar` type.
- `tools/astbuild.py` — `_is_overload(...)` + skip in `inject_region_markers` (so `@overload` stubs
  don't emit duplicate doc-regions).
- `tests/test_operator_typing.py` (new) — `typing.assert_type` static guards + runtime checks.
- Removed `tests/test_typed_products.py` (Path 1's test). base.py and scalar.py untouched. The
  generated `g*.py` are gitignored (they grow, but don't appear in `git diff`).

## Follow-ups

- mvp `tasks/switch-typechecker-pyright-to-ty.md` — make `ty` the only checker (proposed).
- mvp `tasks/precise-product-types-coefficient-cleanup.md` — `.coefficient(...)` → `.coeff_e_12`
  cleanups (proposed; gated on a gacalc release + pin bump).
- Overload the `wedge`/`dot` aliases too (still `-> Self`). Low priority.
- Bring the gacalc notebooks into the `ty` scope now that their GA code type-checks cleanly
  (bigger — jupytext/matplotlib; separate task if wanted).
- `Scalar` as a product lhs — gated on `scalar.py` adopting the resolve-and-construct discipline.
