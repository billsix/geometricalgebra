# Give `project`/`reject`/`reflect` (and `projection_rotation`) LaTeX labels so they compose in the pipeline

**Created:** 2026-07-16 · **Completed:** 2026-07-16

## Problem

The algebra-derived functions `project`, `reject`, `reflect`, `identity` (on `MultiVectorBase` in
`base.py`) and `projection_rotation` (in `transforms.py`) returned a **bare `MultiVectorFn`** with no
LaTeX label, while the `transforms.py` factories (`translate`, `uniform_scale`, `scale_non_uniform`,
`rotor_rotation`, `plane_rotation`) return an **`InvertibleFunction`** that carries
`latex_repr`/`latex_repr_inv` and composes via `@` / `compose` into one rendered LaTeX expression. So a
projection/rejection/reflection — equally worth showing in a derivation — could not join a labelled,
displayable `@`-pipeline. `InvertibleFunction` is the shared display/compose layer, also used by the
mvp book.

## Decision (William Emerison Six <billsix@gmail.com>, 2026-07-16) — Option 4, an opt-in `labeled` wrapper

`project`/`reject`/`reflect`/`identity` keep returning a bare `MultiVectorFn` (zero churn on the
algebra functions); a small `labeled(fn, latex_repr, ...)` helper is applied at the call site only when
a label and pipeline membership are wanted. The wrapper is about labelling/display, not about claiming
an inverse — `project`/`reject` are genuinely not invertible.

The compose detail was settled as **(a)**: `labeled` returns an `InvertibleFunction` whose default
`inverse` is a raising stub (`NotInvertibleError`), so compose/label/`_repr_latex_` all work and only
`.inverse()` through such a chain errors. Rejected: (b) teaching `compose`/`@` a separate label-only
object (a larger change, two types). The raising inverse is confined to the explicit opt-in wrapper,
never baked into `project`/`reject`.

## Deferred alternatives

Invertibility of the functions concerned: `identity` and `reflect(B)` (an involution) are their own
inverses; `projection_rotation(from, to)` inverts by the reverse rotation; `project(B)`/`reject(B)` are
idempotent and lossy, with no inverse. Alternatives considered and not chosen:

1. A labelled-but-not-invertible function type in the compose layer — the honest model, but larger.
2. `InvertibleFunction` with a sentinel/raising inverse baked into `project`/`reject` — **rejected**:
   pretending a projection has an inverse.
3. Labelling only the invertible ones (`reflect`, `identity`, `projection_rotation`) first.
4. (Option 5) An `Invertibility` flag mirroring `Linearity` — kept as the upgrade path if labelling
   later wants to be automatic rather than wrapped by hand.

## What was done

- `transforms.labeled(func, latex_repr, *, latex_repr_inv=None, linearity=NONLINEAR, inverse=None)`
  was added, plus `NotInvertibleError`; both in `transforms.__all__`, with `labeled` re-exported from
  `gn.py`. A caller can pass a real inverse (e.g. a reflection is its own).
- `project`/`reject`/`reflect`/`identity`/`projection_rotation` were unchanged (still bare
  `MultiVectorFn`), so existing `InvertibleFunction` behaviour and mvp's pipelines were untouched.
- A doctest on `labeled`, 4 tests in `tests/test_transforms.py`, and a demo section in
  `notebooks/displaygraded.py`.
- The exact LaTeX conventions (`P_{B}` / `P^{\perp}_{B}` / `\mathrm{refl}_{B}`) were left to the
  caller, since the label is a `labeled` argument.

## Verification

Suite **286 passed**, ruff/ty clean.

## Surfaced limitation

A labelled projection is `InvertibleFunction[MultiVectorBase]` (project's return is type-erased), which
won't `@`-unify with a concretely-typed factory (`translate(Vector3…)` → `InvertibleFunction[Vector3]`)
under the invariant generic — fine at runtime, not statically. It fed
`tasks/archive/2026/07/17/reassess-composable-function-interface.md`.
