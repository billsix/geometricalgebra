# Emit dimension-known methods directly, not by delegating to super() with `n`

**Status:** complete
**Completed:** 2026-07-22
Created 2026-07-21. (Bill's batch items 4, 5, and the first "11" — merged: they're the same idea.)
All gates green (283 tests, `ty` src/tests/tools clean, ruff clean, `check-regions` clean,
deterministic; parity with the old super-delegation verified against `Gn` for `G1`/`G2`/`G3`).

## Outcome (what actually shipped)

Changed **only the full class `G_n`** (`generate_class` in `tools/gen_specialized.py`) — the five
methods now emit the gen-time-known value instead of `super().<m>(DIMENSION if n is None else n)`:

- `unit_pseudoscalar()` → `cls(coeff_e_{1…n}=1, rest=0)` — the top-blade constant, built via `cls`
  so a subclass keeps its own type (and a *fresh* instance, not the shared `Cls.e_{1…n}` constant,
  so no mutation-aliasing).
- `unit_pseudoscalar_squared()` → `cls(coeff_scalar=±1, rest=0)` — the sign is computed at gen
  time by squaring the pseudoscalar in `Gn` (`+1` for 𝒢₁, `−1` for 𝒢₂/𝒢₃), not a hardcoded formula.
- `dual()` → the closed-form field map (`Gn`-derived, like the products), reusing `result_stmts` +
  `summed_value`. Full-class dual stays within `G_n` (`type(self)`).
- `bases()` → `yield from [cls(single-blade), …]` over the known blades.
- `symbolic_multivector(prefix)` → `cls(coeff_*=sympy.Symbol(prefix + "i"), …)` — symbol names
  match `base`'s `sympy.symbols(prefix + ":" + N)` so values are equal.

**Resolved open question 1 (keep vs drop `n`):** kept `n: int | None = None`. Dropping it is an
*invalid Liskov override* (`base`'s versions are `n`-required because `Gn` is dimension-agnostic),
which `ty` rejects. So each method is guarded `if n is None or n == <DIMENSION>: <known>` and a
non-default `n` **falls back to `super()`** — preserving exact prior semantics for the (nonsensical
but legal, e.g. `G2.bases(1)`) off-dimension call. `dim_or_n` was deleted (now unused).

**Not touched:** the graded subtypes (`Vector2`/`Bivector2`/…). Their `dual` was *already*
closed-form (guarded the same way); the other four are algebra-level ops that don't fit a single
graded subtype (𝒢₂'s pseudoscalar `e_12` isn't a `Vector2`) and were never emitted there — calling
e.g. `Vector2.unit_pseudoscalar()` raises `TypeError` (inherited `n`-required base), which is
untested and out of scope. And `Gn`/base are the reference — unchanged.

---

## Original plan (below, for reference)

## Goal

Several generated methods take a dimension `n` (defaulted from `DIMENSION`) and then just
**delegate to the base's general, runtime algorithm**. But the dimension — and in fact the whole
result — is **known at generation time**, so the generated class can emit the closed form / the
constant directly and stop carrying a redundant parameter.

## What's there now (verified in generated `g2.py`)

All of these are emitted as overrides that forward to `super()` with the fixed dimension:

```python
def dual(self, n: int | None = None) -> typing.Self:
    return super().dual(self.DIMENSION if n is None else n)


def unit_pseudoscalar(cls, n: int | None = None) -> typing.Self:
    return super().unit_pseudoscalar(cls.DIMENSION if n is None else n)


def unit_pseudoscalar_squared(cls, n: int | None = None) -> typing.Self:
    return super().unit_pseudoscalar_squared(cls.DIMENSION if n is None else n)


def bases(cls, n: int | None = None) -> Generator[typing.Self]:
    return super().bases(cls.DIMENSION if n is None else n)


def symbolic_multivector(cls, n=None, prefix=...) -> typing.Self:
    return super().symbolic_multivector(cls.DIMENSION if n is None else n, prefix)
```

The `n=None` default already means callers *needn't* pass it — but the method still (a) exposes a
meaningless `n` param on a fixed-dimension class, and (b) runs the base's general computation at
runtime.

## Plan (sketch — decide per method)

- **`unit_pseudoscalar` / `unit_pseudoscalar_squared`** — these are *constants* at generation time
  (𝒢₂'s unit pseudoscalar is `e_12`; its square is `-1`; 𝒢₃'s is `e_123`, square `-1`). Emit them
  as the concrete constant (return the `e_{1…n}` class constant / a `Scalar(-1)`), not a runtime
  `super()` call. Best value here.
- **`dual`** — `A* = A · I⁻¹`; the pseudoscalar and its inverse are known at gen time, so `dual`
  can be a closed-form generated method (like the products) instead of delegating with `n`.
- **`bases` / `symbolic_multivector`** — the basis is fixed at gen time; emit directly.
- **Drop the redundant `n` parameter** from the generated signatures (dimension is fixed). Note:
  the *base* (`MultiVectorBase`) versions still take `n` (Gn is dimension-agnostic) — only the
  generated overrides lose it. Check this stays a Liskov-compatible override (narrowing a
  parameter to nothing changes the signature — may need the generated method to keep accepting
  `n` for override-compat, or the base signature to change; resolve during implementation).

## Open questions

1. Is dropping `n` from the generated signatures worth a possible override-compat wrinkle, or is
   emitting the closed form / constant while *keeping* an ignored `n=None` acceptable? (My lean:
   emit constants/closed forms; keep the story simple on the signature.)

## Relationships

- Same closed-form-at-generation-time philosophy as `tasks/reference/generated-product-typing.md`
  and the code generator (`tasks/reference/code-generator-architecture.md`).
