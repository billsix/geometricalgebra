# Generated closed-form `g3.Vector.cross` (type-precise `Vector -> Vector`)

**Status:** IMPLEMENTED 2026-08-31 — pending maintainer review; ships in 0.0.18
**Priority:** 3
**Difficulty:** 4
**Created:** 2026-08-31 (spun out of `[[custom-symbols-and-vector-calc]]`, where it
was parked as "a separate follow-up"; approved and pulled forward by the maintainer
the same day — "yes, before release")

## BLUF

`tools/gen_specialized.py` now emits a `cross` method on the 𝒢₃ `Vector` class: a
generator-derived closed form (`a₂b₃ − a₃b₂`, …) with a precise
`@overload (other: Vector) -> Vector` — so consumers (mvp's ty-gated `find_normal`)
get the right static type with no casts — plus a `MultiVectorBase` catch-all whose
impl falls back to `MultiVectorBase.cross` (the `[[custom-symbols-and-vector-calc]]`
pass-through → `vectorcalc.cross`), which handles `Gn` mixing and raises the guard
errors. Done means reviewed and released in 0.0.18 (`tasks/release-0.0.18.md`).

## Context

- **Code:** the `if n == 3:` block inside the Vector section of the graded-class
  builder in `tools/gen_specialized.py` (search "cross(a, b) = (a ∧ b) I₃⁻¹").
  Emission reuses the existing machinery: `product_result` derives the closed form
  by running `lambda a, b: a.outer_product(b).dual(3)` symbolically in `Gn`;
  `result_block_stmts` renders the constructor; the exact-type early-out
  (`type(other) is Vector`) is the same idiom as the products. Docstring is copied
  from `MultiVectorBase.cross` via `method_doc_stmts`, so the two never drift.
- **Why not `dispatch_method`:** that helper emits one closed-form arm per rhs type;
  cross is vector×vector only, so it gets a single specialized arm + fallback.
- **Only 𝒢₃:** the cross product exists only there (only in 3-D is the dual of a
  bivector a vector); `g1`/`g2` `Vector` inherit the base pass-through, whose
  runtime guard raises. The generated `dual` is dimension-locked (0.0.17), which is
  why the free function requires `DIMENSION == 3` rather than passing other `n`.
- **Tests:** `tests/test_vectorcalc.py` —
  `test_generated_closed_form_matches_definition` proves the closed form
  symbolically against BOTH the free function's wedge+dual path and the slow
  reference algebra `Gn` (an oracle sharing no generated code), pins the runtime
  type, and asserts the cyclic identities (`e₁×e₂=e₃`, `e₂×e₃=e₁`, `e₃×e₁=e₂`,
  maintainer-requested) through the closed form itself;
  `test_generated_cross_falls_back_for_foreign_operands` covers the `Gn`-mixing and
  error arms.
- **Verified:** full suite green (host + containerized `make test`), `ruff`, `ty`
  (including the generated modules passed together in full context),
  `make check-regions`, `make check-generated` (determinism).
