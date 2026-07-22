# Emit dimension-known methods directly, not by delegating to super() with `n`

**Status:** proposed — needs go-ahead. Created 2026-07-21. (Bill's batch items 4, 5, and the
first "11" — merged: they're the same idea.)

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
