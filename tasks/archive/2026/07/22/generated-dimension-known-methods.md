# Emit dimension-known methods directly, not by delegating to super() with `n`

**Created:** 2026-07-21 · **Completed:** 2026-07-22

The maintainer's batch items 4, 5, and the first "11", merged because they are the same idea. All
gates green (283 tests, `ty` src/tests/tools clean, ruff clean, `check-regions` clean,
deterministic; parity with the old super-delegation verified against `Gn` for `G1`/`G2`/`G3`).

## Starting point

Five generated methods took a dimension `n` (defaulted from `DIMENSION`) and delegated to the
base's general runtime algorithm, e.g. `def dual(self, n: int | None = None) -> typing.Self: return
super().dual(self.DIMENSION if n is None else n)`; likewise `unit_pseudoscalar`,
`unit_pseudoscalar_squared`, `bases`, `symbolic_multivector`. The dimension, and the whole result,
is known at generation time, so the closed form or constant can be emitted directly (the same
closed-form-at-generation-time philosophy as `tasks/reference/generated-product-typing.md` and
`tasks/reference/code-generator-architecture.md`).

## What shipped

Only the **full class `G_n`** changed (`generate_class` in `tools/gen_specialized.py`); the five
methods emit the gen-time-known value:

- `unit_pseudoscalar()` → `cls(coeff_e_{1…n}=1, rest=0)`: the top-blade constant, built via `cls`
  so a subclass keeps its own type (and a *fresh* instance, not the shared `Cls.e_{1…n}` constant,
  so no mutation-aliasing).
- `unit_pseudoscalar_squared()` → `cls(coeff_scalar=±1, rest=0)`: the sign is computed at gen
  time by squaring the pseudoscalar in `Gn` (`+1` for 𝒢₁, `−1` for 𝒢₂/𝒢₃), not a hardcoded formula.
- `dual()` → the closed-form field map (`Gn`-derived, like the products), reusing `result_stmts` +
  `summed_value`. Full-class dual stays within `G_n` (`type(self)`).
- `bases()` → `yield from [cls(single-blade), …]` over the known blades.
- `symbolic_multivector(prefix)` → `cls(coeff_*=sympy.Symbol(prefix + "i"), …)`; symbol names
  match `base`'s `sympy.symbols(prefix + ":" + N)` so values are equal.

## Decision: keep `n`

The `n: int | None = None` parameter was kept. Dropping it is an *invalid Liskov override*
(`base`'s versions are `n`-required because `Gn` is dimension-agnostic), which `ty` rejects. So
each method is guarded `if n is None or n == <DIMENSION>: <known>` and a non-default `n` **falls
back to `super()`**, preserving exact prior semantics for the (nonsensical but legal, e.g.
`G2.bases(1)`) off-dimension call. `dim_or_n` was deleted as unused.

## Not touched

The graded subtypes (`Vector2`/`Bivector2`/…): their `dual` was already closed-form (guarded the
same way); the other four are algebra-level ops that don't fit a single graded subtype (𝒢₂'s
pseudoscalar `e_12` isn't a `Vector2`) and were never emitted there. Calling e.g.
`Vector2.unit_pseudoscalar()` raises `TypeError` (inherited `n`-required base), which was untested
and out of scope. `Gn`/base, the reference, were unchanged.
