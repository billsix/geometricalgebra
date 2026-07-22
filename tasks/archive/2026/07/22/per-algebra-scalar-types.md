# Per-algebra `Scalar1`/`Scalar2`/`Scalar3` types — precise `ScalarN.dual()`

**Status:** complete
**Completed:** 2026-07-22 (code + all gates; the 0.0.13 **release is Bill's**, batched with the
dual-typing change and tracked on the work stack). Created 2026-07-22. Follow-on to `tasks/archive/2026/07/22/precise-dual-typing.md`:
that task made every *fixed-dimension* dual precise but left `Scalar.dual() -> MultiVectorBase`
because the single **shared** `Scalar` didn't know its dimension. This task split `Scalar` into one
type per algebra so `ScalarN.dual()` is precise (the original Goal).

## Outcome (what shipped, 2026-07-22)

`Scalar` is now **per-algebra** — `Scalar1`/`Scalar2`/`Scalar3`, each generated into its own
`gN.py`; **`scalar.py` is gone**. `Scalar1.dual() -> Vector1`, `Scalar2.dual() -> Bivector2`,
`Scalar3.dual() -> Trivector3` (grade 0 → the pseudoscalar), no unsound cast — the original Goal met.
Every grade-0 result now carries its algebra (`Vector3.inner_product(Vector3) -> Scalar3`,
`Bivector2 * Bivector2 -> Scalar2`), and `ScalarN` carries `DIMENSION` like the other graded types.

All gates green: `ty` src/tests/tools clean (incl. new `assert_type` guards for `ScalarN.dual`),
`ruff` clean, **297 tests** pass in-container, `check-regions` clean, generator deterministic;
runtime values unchanged (a static-typing + type-identity change — grade-0 results are now `ScalarN`,
not the old shared `Scalar`).

- **Generator (`tools/gen_specialized.py`)**: `SCALAR` const → `scalar_spec(n)`; `generate_scalar()`
  → `generate_scalar(n, name, full_name)` (parametrized class name, `DIMENSION`, precise `dual` via
  `dim_mismatch_guard` + `unary_result`/`unary_stmt`); `main()` emits `ScalarN` into each `gN.py`
  first, no separate `scalar.py`; header drops the `Scalar` import; `SCALAR_HEADER`/`scalar_doc`
  adjusted. `unary_result`'s `full_name` arg **must** be the `G_n` name (not `ScalarN`) — it keys the
  full-class fallback spec in `resolve`.
- **Build files**: `setup.py` `GENERATED`, `Makefile` `GENERATED` + comments, `.gitignore`,
  `check_doc_regions.py` docstring — dropped `scalar.py`.
- **Tests** (`test_operator_typing`, `test_graded`, `test_subclass_preservation`,
  `test_vector_ergonomics`, `test_generator`): per-algebra `ScalarN` imports + assertions.
- **Notebook** `displaygraded.py` + **docs** (`README.md`, `CLAUDE.md`, both `tasks/reference/*`
  generator/product docs) updated off the shared-Scalar framing.
- **Downstream mvp**: untouched (zero `Scalar`-type references, verified).

## Goal

`Scalar1.dual() -> Vector1`, `Scalar2.dual() -> Bivector2`, `Scalar3.dual() -> Trivector3`
(grade 0 → grade n = that algebra's pseudoscalar), with no unsound cast.

## The architectural crux (why the shared type can't do it)

`ScalarN.dual()` must *reference* the pseudoscalar type (`Vector1`/`Bivector2`/`Trivector3`), which
lives in `g1.py`/`g2.py`/`g3.py`. Those import `Scalar`. So keeping a shared `scalar.py` forces a
circular import (`scalar` → `g3` for `Trivector3`; `g3` → `scalar`). This also kills the
"keep shared `Scalar`, add `@overload`s on `n`" idea (same cycle, and `dual` has no overload key).

**Resolution: eliminate `scalar.py`; generate `ScalarN` into each `gN.py`.** Each algebra module
becomes self-contained (`Scalar3` + `Vector3` + … + `G3` all in `g3.py`), so `Scalar3.dual() ->
Trivector3` references a same-module type — no cycle. Bonus: `Scalar` stops being the odd-one-out
(the only dimensionless graded type) and becomes uniform with `VectorN`/`BivectorN` (carries
`DIMENSION`).

## Blast radius (verified 2026-07-22)

- **mvp: zero `Scalar`-type references** (Explore sweep of src/ports/tests/notebooks/book) — consumes
  gacalc via `Vector2`/`Vector3`/`transforms` only. **No breaking change downstream, no release-gate
  coupling** (contrast the dual work). mvp's book has no `literalinclude` of gacalc's `scalar.py`.
- **Inside gacalc, only g1/g2/g3 import `gacalc.scalar`** — nothing else. `base.py` mentions `Scalar`
  only in prose. So dropping `scalar.py` is internally clean.

## Plan

**Generator (`tools/gen_specialized.py`):**
- `SCALAR` constant → `scalar_spec(n)` (`TypeSpec(f"Scalar{n}", ((),), n, "scalar")`); thread through
  `registry_for_dim`/`resolve` + the ~6 dispatch call-sites + `generate_graded_type`'s zero-scalar
  construct + `generate_constants`' `__all__`.
- `generate_scalar()` → `generate_scalar(n, name)`: parametrize the class name, add `DIMENSION`, and
  replace the `n`-required `dual` with a precise closed form (reuse `dim_mismatch_guard` +
  `unary_result`/`unary_stmt`, mirroring the graded `dual_method`).
- `main()`: stop writing `scalar.py`; emit `generate_scalar(n, f"Scalar{n}")` into each `gN.py`; drop
  `from gacalc.scalar import Scalar` from the header; delete `SCALAR_HEADER`. Remove `scalar.py` file
  + `.gitignore` line.

**Tests:** swap `from gacalc.scalar import Scalar` for per-algebra `ScalarN` and update assertions in
`test_operator_typing.py`, `test_graded.py`, `test_subclass_preservation.py`,
`test_vector_ergonomics.py`; update registry-name expectations in `test_generator.py`; add
`ScalarN.dual()` guards.

**Notebooks:** `displaygraded.py` (`Scalar` import + `Scalar.from_scalar(5)`) → `ScalarN`.

**Docs:** `README.md` (shared-Scalar row + return-type tables) and `CLAUDE.md` (module-layout bullet;
graded-subtype notes) — drop the "shared scalar.py" framing.

## Naming decision (Bill, 2026-07-22)

`Scalar1`/`Scalar2`/`Scalar3` (distinct names), **not** a per-module `Scalar` (which would collide on
the name across modules and make `assert_type(..., Scalar)` ambiguous).

## Verify

Regenerate; `ty` src/tests/tools clean; `reveal_type`/`assert_type` (`Scalar3.dual() -> Trivector3`);
suite + `check-regions` + determinism green; runtime values unchanged.

## Release

Batched with `tasks/archive/2026/07/22/precise-dual-typing.md` — Bill bumps 0.0.12 → 0.0.13 and runs `make release`
*after* this work lands (his call, 2026-07-22). See the work stack.

## Relationships

- `tasks/archive/2026/07/22/precise-dual-typing.md` (parent; the shared-Scalar limitation this removes).
- `tasks/reference/generated-product-typing.md` (the precise-typing design this extends).
- `tasks/model-odd-graded-type.md` (unrelated, but the same "add a graded type" shape).
