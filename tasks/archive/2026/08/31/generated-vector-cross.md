# Generated closed-form `g3.Vector.cross` (type-precise `Vector -> Vector`)

**Created:** 2026-08-31 · **Completed:** 2026-08-31 (shipped in 0.0.18,
`tasks/archive/2026/08/31/release-0.0.18.md`)
**Source:** spun out of `tasks/archive/2026/08/31/custom-symbols-and-vector-calc.md`, where it was
parked as a separate follow-up; the maintainer approved pulling it forward the same day ("yes,
before release")

## What changed

`tools/gen_specialized.py` emits a `cross` method on the 𝒢₃ `Vector` class: a generator-derived
closed form (`a₂b₃ − a₃b₂`, …) with a precise `@overload (other: Vector) -> Vector`, so consumers
(mvp's ty-gated `find_normal`) get the right static type with no casts, plus a `MultiVectorBase`
catch-all whose impl falls back to `MultiVectorBase.cross` (the pass-through to `vectorcalc.cross`),
which handles `Gn` mixing and raises the guard errors.

- **Where:** the `if n == 3:` block in the Vector section of the graded-class builder (search
  "cross(a, b) = (a ∧ b) I₃⁻¹"). It reuses existing machinery: `product_result` derives the closed
  form by running `lambda a, b: a.outer_product(b).dual(3)` symbolically in `Gn`;
  `result_block_stmts` renders the constructor; the `type(other) is Vector` early-out is the products'
  idiom; the docstring is copied from `MultiVectorBase.cross` via `method_doc_stmts`, so they cannot
  drift.
- **Why not `dispatch_method`:** it emits one closed-form arm per rhs type; cross is vector×vector
  only, so it got a single specialized arm plus the fallback.
- **Only 𝒢₃:** only in 3-D is the dual of a bivector a vector. `g1`/`g2` `Vector` inherit the base
  pass-through, whose runtime guard raises. The generated `dual` is dimension-locked (0.0.17), which
  is why the free function requires `DIMENSION == 3`.

## Verification

`tests/test_vectorcalc.py`: `test_generated_closed_form_matches_definition` proves the closed form
symbolically against both the free function's wedge+dual path and the slow reference algebra `Gn`
(an oracle sharing no generated code), pins the runtime type, and asserts the cyclic identities
(`e₁×e₂=e₃`, `e₂×e₃=e₁`, `e₃×e₁=e₂`, maintainer-requested) through the closed form;
`test_generated_cross_falls_back_for_foreign_operands` covers the `Gn`-mixing and error arms. Full
suite green (host and containerized `make test`), ruff, ty (including the generated modules in full
context), `make check-regions`, `make check-generated`.
