# Precise `even_part`/`odd_part` — retype off `-> Self` so the graded override can narrow

**Status:** complete
**Completed:** 2026-07-22
Created 2026-07-22. (Follow-up spun from `overloads-and-drop-cast-on-product-primitives`; the last
of the three, and the only one needing a `base.py` change.) All gates green (287 tests incl. 2 new
even/odd guards, `ty` src/tests/tools clean, ruff clean, `check-regions` clean, deterministic;
runtime values/types unchanged — a pure static-typing fix).

## Outcome (what shipped)

- **`base.py`**: `even_part`/`odd_part` retyped `-> typing.Self` → `-> MultiVectorBase` (bodies
  untouched). This is the floor that lets a graded override *narrow* the return.
- **Generator (`generate_graded_type`)**: a new `parity_part` helper emits each graded
  `even_part`/`odd_part` **declaring its resolved return type** (`unary_result`-computed) with **no
  overloads** (there's no argument to key a `Literal` on) and **no cast** — e.g. `Vector2.even_part
  -> Scalar`, `Vector2.odd_part -> Vector2`, `Bivector3.odd_part -> Scalar`, `Rotor2.even_part ->
  Rotor2`. The old unsound `cast(typing.Self, Scalar(0))` is gone from every graded arm.
- **Full class `G1`/`G2`/`G3`** unchanged (`even_part`/`odd_part` stay `-> Self` = `G_n`, a valid
  narrowing of the broadened base). **`Scalar`** unchanged (`-> Self`, already correct).
- **Generator plumbing**: broadened `gn_unary` param on `unary_result`/`unary_body`/`parity_part`
  from `Callable[[Gn], Gn]` to `Callable[[Gn], MultiVectorBase]` (`even_part` now returns
  `MultiVectorBase`; `Gn`-returning ops like `dual` still fit by covariance), and `result_mv: Gn`
  → `MultiVectorBase` in `unary_result`.
- Static guard added to `tests/test_operator_typing.py` (`assert_type`).

**Resolved the open `Gn` decision → let `Gn` inherit the `-> MultiVectorBase` floor (no override).**
Checked every `even_part`/`odd_part` call site (`tests/`, `notebooks/`, `src/`): all use the result
only through base operations (`==`, `+`) or runtime `type(...)` checks — **nothing depends on
`Gn.even_part()` statically being `Gn`**. So an override would be pure ceremony; instead **`gn.py`
is untouched and no new cast is introduced anywhere** — the cleanest realization of the goal (the
task was to *remove* unsound casts, not trade them). The only effect is `Gn.even_part()` /
`odd_part()` now declare the honest `MultiVectorBase` (runtime still builds a `Gn`).

## Original plan (below, for reference)

## Goal

Make the generated `even_part`/`odd_part` precisely typed (return the resolved even/odd-grade
type) and drop their unsound `Scalar(0)` cast — e.g. `Vector2.even_part()` should be `Scalar`, not
`cast(typing.Self, Scalar(0))`.

## What's there now (verified in `g2.py`)

`even_part(self) -> typing.Self` returning, for a type with no even part, `return typing.cast(
typing.Self, Scalar(coeff_scalar=cast(Coef, 0)))` — a `Scalar` asserted to be `Vector2`. Same
unsound pattern the products had, on the unary grade-parity ops.

## Why this needs a base change (unlike the products / `r_vector_part`)

The product overloads and the `r_vector_part` follow-up work because they have an **argument to key
`@typing.overload` on** (the rhs type; the grade `Literal`). `even_part`/`odd_part` take **no
argument** — there's no key, so `@overload` can't give them a per-call precise return. The only way
to declare `Vector2.even_part() -> Scalar` is a real override, and overriding `base.even_part ->
Self` (= `-> Vector2` on Vector2) with `-> Scalar` is an **invalid override** (`Scalar` isn't a
subtype of `Self`), which `ty` rejects.

So the fix is: **retype `MultiVectorBase.even_part`/`odd_part` from `-> Self` to `->
MultiVectorBase`.** Then a generated override narrowing to the resolved grade type
(`Vector2.even_part -> Scalar`, `Rotor2.even_part -> Rotor2`, …) is a *valid covariant-return
override*.

## The decision this forces (open question)

Retyping the base loosens `Gn.even_part` from `-> Self` (= `Gn`) to `-> MultiVectorBase` — a
**precision loss for `Gn`** (its even part genuinely is a `Gn`). Options:
1. Accept `Gn.even_part -> MultiVectorBase` (simplest; `Gn` is the slow reference, precision there
   matters less).
2. Have `Gn` **override** `even_part`/`odd_part` back to `-> Gn` (keep `Gn` precise; one extra
   override on the general class). *Likely the right call.*

## Plan (sketch)

1. `base.py`: `even_part`/`odd_part` → `-> MultiVectorBase` (was `-> Self`). Keep the bodies.
2. Generator: emit graded `even_part`/`odd_part` with the **resolved even/odd-grade type**
   (`unary_result` already resolves it) as the declared return, dropping the `Scalar(0)` cast.
3. Resolve the `Gn` question (option 2: `Gn` overrides back to `-> Gn`).
4. Regenerate; `ty` src/tests/tools clean (watch for any caller that relied on `even_part -> Self`);
   suite/regions/determinism.

## Relationships

- Same "honest return, no unsound `Self` cast" goal as
  `tasks/reference/generated-product-typing.md` and `overload-r-vector-part.md`; this is the harder
  case because there's no overload key.
