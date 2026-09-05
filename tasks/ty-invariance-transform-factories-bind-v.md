# Type the transform factories/`compose`/`to_matrix` to bind the caller's precise `V` (ty invariance)

**Status:** IMPLEMENTED 2026-09-05 (staged, awaiting maintainer release as 0.0.19). ty-clean + 441 tests pass; mvp usage pattern verified to typecheck against the fixed code.
**Priority:** 3
**Difficulty:** 5

## BLUF

Under `ty` ≥ 0.0.72 (strict invariance enforcement), gacalc's **scalar-argument** transform
factories and combinators are typed to return `InvertibleFunction[MultiVectorBase]`. Because
`InvertibleFunction` is **invariant** in its type parameter, that result cannot be assigned to a
caller's precise `InvertibleFunction[Vector]` (e.g. `g2.Vector` / `g3.Vector`). Downstream code
that annotates precisely then fails to type-check — concretely, ~25 `ty` errors in
**modelviewprojection**'s demos/tests. Fix: make these factories/combinators **bind or accept the
caller's `V`**, so `[Vector]` in yields `[Vector]` out. Ship as **gacalc 0.0.19**. Done = a
downstream file annotating `InvertibleFunction[g3.Vector]` and composing these passes `ty` ≥ 0.0.74,
and gacalc's own tests/`ty` stay green.

## Context

- **Where this came from:** modelviewprojection's `ty` 0.0.72/0.0.74 strictness sweep
  (`github.com/billsix/modelviewprojection` → `tasks/ty-0072-strictness-sweep.md`). ~25 of mvp's
  errors are this one class; mvp deliberately keeps precise `InvertibleFunction[Vector]`
  annotations (the course teaches with that precision), so loosening them there is rejected — the
  fix belongs here.
- **Root cause:** the scalar factories have no *vector* argument to bind the generic `V`, so they
  default `V = MultiVectorBase`; `compose`/`@`/`to_matrix` propagate that. `ty` now enforces the
  invariance, so `InvertibleFunction[MultiVectorBase]` ≠ `InvertibleFunction[Vector]`.
- **Affected surface** (verified in `src/gacalc/transforms.py`, 2026-09-05):
  - `uniform_scale(m: float) -> InvertibleFunction[MultiVectorBase]` (`:518`)
  - `scale_non_uniform(*factors: float) -> InvertibleFunction[MultiVectorBase]` (`:552`)
  - the rotation constructors returning `InvertibleFunction[MultiVectorBase]` (`:341`, `:392`)
  - `compose_intermediate_fns` (`:75`) / `compose_intermediate_fns_and_fn` (`:118`)
  - `to_matrix(fn: InvertibleFunction[MultiVectorBase], …)` (`:598-599`) — mvp's
    `tests/test_mathutils.py:353,373` hit this passing `InvertibleFunction[g3.Vector]`.
- **Runtime is already correct** — this is purely a typing precision gap; the functions operate on
  whatever vector is passed.

## Approach options (to decide)

1. **Make the scalar factories generic over `V` with an explicit bind** (e.g. `uniform_scale[V]`
   / a target-type parameter), so the caller's `Vector` flows through. Narrowest, safest.
2. **Generalize `to_matrix`** to `fn: InvertibleFunction[V]` for the caller's `V` (rather than a
   fixed `MultiVectorBase`).
3. **Make `InvertibleFunction` covariant** in its parameter — broad fix (assignment works
   everywhere), but needs a soundness review: covariance is unsound if the type is used in an
   input position anywhere (the `inverse`/`__call__` surface). Only if provably sound.

## Verify

Add a `ty`-checked test in gacalc that annotates `InvertibleFunction[g2.Vector]`/`[g3.Vector]`,
composes `uniform_scale`/`scale_non_uniform`/rotations/`compose`/`to_matrix`, and must pass
`ty` ≥ 0.0.74. Then mvp bumps its gacalc pin and its ~25 errors clear (that's the downstream
acceptance test).

## Open questions

1. **Covariance vs explicit binding** — make `InvertibleFunction` covariant (broad, needs a
   soundness proof re: input positions) or add explicit `V`-binding to the factories/`to_matrix`
   (narrower, certainly sound)? *Recommend the latter unless covariance is provably sound.*

## Related

- Downstream driver: `github.com/billsix/modelviewprojection` `tasks/ty-0072-strictness-sweep.md`.

## Implementation (2026-09-05) — done, verified, awaiting release

Changed `src/gacalc/transforms.py` (staged):

- **`uniform_scale(m: float) -> InvertibleFunction[V]`** and
  **`scale_non_uniform(*factors) -> InvertibleFunction[V]`** — was `[MultiVectorBase]`. The
  return-only `V` (bound `MultiVectorBase`) is inferred from the **caller's annotation** (verified:
  ty 0.0.74 does return-only-typevar inference from the assignment target, and it stays sound — a
  wrong target still errors). The pedagogically-central `f`/`f_inv` bodies are unchanged; a single
  `typing.cast(InvertibleFunction[V], ...)` at the wrapper return bridges the gap ty can't see
  through the grade-general scalar product (`vector * m` types as `MultiVectorBase`, unlike
  `translate`'s type-preserving `vector + b`). **Note:** this cast shows in any downstream book
  region that `literalinclude`s the `uniform scale body` / `scale non-uniform body` markers.
- **`to_matrix(fn: InvertibleFunction[typing.Any], cls: type[MultiVectorBase], ...)`** — was
  `fn: InvertibleFunction[MultiVectorBase]`. Chose **`[Any]`** (not `[V]` bound from `cls`) per
  gacalc's own convention ("a param that accepts any transform and applies it internally is
  `InvertibleFunction[Any]`"): it accepts mvp's concrete `[Vector]` fns AND gacalc's own
  representation-agnostic `[MultiVectorBase]` test fns, so **no test changes were needed**. (A
  first attempt with `cls: type[V]` bound `V` too tightly and broke `test_transforms.py`.)

**Verification:** `ty check src/tests/tools` clean; `make test` **441 passed**; a throwaway file
importing the real `gacalc.g2`/`g3` and exercising all three mvp patterns reported **0 diagnostics**.
(The `make format` gate shows one **pre-existing, unrelated** E501 in
`tasks/adhoc/drop-graded-type-dimension-suffixes/codemod.py:23` — not touched here.)

**Rotation factories NOT changed** — mvp's failing sites don't use gacalc's rotation factories
directly (mvp wraps them in its own concretely-typed `rotate_*`), so they aren't needed for the
unblock. Threading `V` through `bivector_rotation`/`plane_rotation`/`rotor_rotation` is a possible
follow-up for completeness, not required.

**Next:** maintainer bumps `version` to 0.0.19 and releases; then mvp bumps its pin
(`requirements.txt` + Dockerfile `ARG GACALC_VERSION`) and its 36 remaining ty errors clear.
