# Type the transform factories/`compose`/`to_matrix` to bind the caller's precise `V` (ty invariance)

**Created:** 2026-09-05 · **Completed:** 2026-09-06 (implemented 2026-09-05; released as gacalc
0.0.19 on PyPI 2026-09-05; confirmed downstream 2026-09-06)
**Source:** github.com/billsix/modelviewprojection `tasks/archive/2026/09/06/ty-0072-strictness-sweep.md`

## The problem

Under `ty` ≥ 0.0.72 (strict invariance), gacalc's scalar-argument transform factories and
combinators returned `InvertibleFunction[MultiVectorBase]`. Because `InvertibleFunction` is invariant,
that result could not be assigned to a caller's precise `InvertibleFunction[g2.Vector]` /
`[g3.Vector]`, producing ~25 ty errors in modelviewprojection's demos and tests. mvp deliberately
keeps the precise annotations (the course teaches with them), so loosening them there was rejected
and the fix belonged in gacalc. Root cause: the scalar factories have no vector argument to bind `V`,
so it defaulted to `MultiVectorBase`, and `compose`/`@`/`to_matrix` propagated that. Runtime was
already correct; this was purely a typing gap.

## Decision

**Explicit `V`-binding on the factories and `to_matrix`, not making `InvertibleFunction`
covariant.** Covariance would fix assignment everywhere but is unsound if the type parameter appears
in an input position (the `inverse` / `__call__` surface); explicit binding is narrower and certainly
sound.

## What changed (`src/gacalc/transforms.py`)

- **`uniform_scale(m: float) -> InvertibleFunction[V]`** and **`scale_non_uniform(*factors) ->
  InvertibleFunction[V]`** (were `[MultiVectorBase]`). The return-only `V` (bound `MultiVectorBase`)
  is inferred from the caller's annotation — verified that ty 0.0.74 does return-only-TypeVar
  inference from the assignment target and stays sound (a wrong target still errors). The teaching
  `f`/`f_inv` bodies were unchanged; one `typing.cast(InvertibleFunction[V], ...)` at the wrapper
  return bridges what ty can't see through the grade-general scalar product (`vector * m` types as
  `MultiVectorBase`, unlike `translate`'s type-preserving `vector + b`). Note: that cast shows in any
  downstream book region that `literalinclude`s the `uniform scale body` / `scale non-uniform body`
  markers.
- **`to_matrix(fn: InvertibleFunction[typing.Any], cls: type[MultiVectorBase], ...)`** (was
  `[MultiVectorBase]`). `[Any]` was chosen over a `V` bound from `cls`, per gacalc's convention for a
  param that accepts any transform and applies it internally: it accepts mvp's concrete `[Vector]`
  functions and gacalc's own `[MultiVectorBase]` test functions, so no test changed. A first attempt
  with `cls: type[V]` bound `V` too tightly and broke `test_transforms.py`.
- **Rotation factories not changed:** mvp wraps them in its own concretely typed `rotate_*`, so they
  were not needed for the unblock; threading `V` through `bivector_rotation` / `plane_rotation` /
  `rotor_rotation` was noted as optional.

## Verification

`ty check src/tests/tools` clean; `make test` 441 passed; a throwaway file importing the real
`gacalc.g2`/`g3` and exercising all three mvp patterns reported 0 diagnostics. (`make format` then
showed one pre-existing, unrelated E501 in the ad-hoc `drop-graded-type-dimension-suffixes` codemod,
later fixed by `tasks/archive/2026/09/05/fix-make-format-ruff-errors.md`.) Downstream: the maintainer
released 0.0.19; mvp bumped its pin (`requirements.txt` + Dockerfile `ARG GACALC_VERSION`), rebuilt,
and its 36 remaining invariance errors cleared with no change beyond removing two now-unused
`# ty: ignore`s (`make format` green).
