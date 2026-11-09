# Per-algebra `Scalar1`/`Scalar2`/`Scalar3` types: precise `ScalarN.dual()`

**Created:** 2026-07-22 · **Completed:** 2026-07-22

Follow-on to `tasks/archive/2026/07/22/precise-dual-typing.md`, which made every
*fixed-dimension* dual precise but left `Scalar.dual() -> MultiVectorBase` because the single
**shared** `Scalar` didn't know its dimension. This task split `Scalar` into one type per algebra so
`ScalarN.dual()` is precise.

## Outcome

`Scalar` became **per-algebra**: `Scalar1`/`Scalar2`/`Scalar3`, each generated into its own
`gN.py`; **`scalar.py` was removed**. `Scalar1.dual() -> Vector1`, `Scalar2.dual() -> Bivector2`,
`Scalar3.dual() -> Trivector3` (grade 0 → the pseudoscalar), with no unsound cast. Every grade-0
result carries its algebra (`Vector3.inner_product(Vector3) -> Scalar3`,
`Bivector2 * Bivector2 -> Scalar2`), and `ScalarN` carries `DIMENSION` like the other graded types.

All gates green: `ty` src/tests/tools clean (incl. new `assert_type` guards for `ScalarN.dual`),
`ruff` clean, **297 tests** pass in-container, `check-regions` clean, generator deterministic.
Runtime values were unchanged; this was a static-typing + type-identity change (grade-0 results are
`ScalarN`, not the old shared `Scalar`).

## The architectural crux

`ScalarN.dual()` must *reference* the pseudoscalar type (`Vector1`/`Bivector2`/`Trivector3`), which
lives in `g1.py`/`g2.py`/`g3.py`, and those imported `Scalar`. Keeping a shared `scalar.py` forced a
circular import (`scalar` → `g3` for `Trivector3`; `g3` → `scalar`). That also ruled out "keep the
shared `Scalar`, add `@overload`s on `n`" (same cycle, and `dual` has no overload key).

**Resolution: eliminate `scalar.py`; generate `ScalarN` into each `gN.py`.** Each algebra module is
self-contained (`Scalar3` + `Vector3` + … + `G3` all in `g3.py`), so `Scalar3.dual() -> Trivector3`
references a same-module type. `Scalar` also stopped being the odd-one-out (the only dimensionless
graded type).

## Naming decision (William Emerison Six <billsix@gmail.com>, 2026-07-22)

`Scalar1`/`Scalar2`/`Scalar3` (distinct names), **not** a per-module `Scalar`, which would collide on
the name across modules and make `assert_type(..., Scalar)` ambiguous.

## Blast radius (verified 2026-07-22)

- **mvp (github.com/billsix/modelviewprojection): zero `Scalar`-type references** (sweep of
  src/ports/tests/notebooks/book); it consumes gacalc via `Vector2`/`Vector3`/`transforms` only, and
  its book has no `literalinclude` of `scalar.py`. No breaking change downstream, no release-gate
  coupling.
- **Inside gacalc, only g1/g2/g3 imported `gacalc.scalar`**; `base.py` mentions `Scalar` only in
  prose.

## What changed

- **Generator (`tools/gen_specialized.py`)**: `SCALAR` const → `scalar_spec(n)` (threaded through
  `registry_for_dim`/`resolve`, the dispatch call-sites, `generate_graded_type`'s zero-scalar
  construct, `generate_constants`' `__all__`); `generate_scalar()` → `generate_scalar(n, name,
  full_name)` (parametrized class name, `DIMENSION`, precise `dual` via `dim_mismatch_guard` +
  `unary_result`/`unary_stmt`); `main()` emits `ScalarN` into each `gN.py` first, no separate
  `scalar.py`; the header drops the `Scalar` import; `SCALAR_HEADER`/`scalar_doc` adjusted.
  `unary_result`'s `full_name` arg **must** be the `G_n` name (not `ScalarN`): it keys the
  full-class fallback spec in `resolve`.
- **Build files**: `setup.py` `GENERATED`, `Makefile` `GENERATED` + comments, `.gitignore`,
  `check_doc_regions.py` docstring dropped `scalar.py`.
- **Tests** (`test_operator_typing`, `test_graded`, `test_subclass_preservation`,
  `test_vector_ergonomics`, `test_generator`): per-algebra `ScalarN` imports + assertions.
- **Notebook** `displaygraded.py` + **docs** (`README.md`, `CLAUDE.md`, the
  `tasks/reference/` generator/product docs) updated off the shared-Scalar framing.

## Release

Batched with `tasks/archive/2026/07/22/precise-dual-typing.md`: the 0.0.12 → 0.0.13 bump and
`make release` were the maintainer's to run after this work (his call, 2026-07-22); `v0.0.13` was
tagged.

## Related

- `tasks/archive/2026/07/22/precise-dual-typing.md` (parent).
- `tasks/reference/generated-product-typing.md` (the precise-typing design this extends).
- `tasks/archive/2026/09/05/model-odd-graded-type.md` (unrelated, but the same "add a graded type"
  shape).
