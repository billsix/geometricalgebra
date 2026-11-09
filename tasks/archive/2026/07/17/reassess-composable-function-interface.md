# Reassess the composable-function interface now that non-invertible functions exist

**Created:** 2026-07-16 · **Completed:** 2026-07-17

The core shipped in gacalc 0.0.9 (2026-07-17). Two non-blocking follow-ups were spun off to
`tasks/composable-function-followups.md`.

## The problem

Adding non-invertible labelled functions (`transforms.labeled` + `NotInvertibleError`, 2026-07-16,
`tasks/archive/2026/07/16/latex-labels-for-project-reject-in-pipeline.md`) showed the single
`InvertibleFunction` type was doing two jobs with conflicting requirements. Its two consumers:

1. **The Cayley-graph engine** (mvp's `cayley/cayleygraph.py`): `Step.fn` and `Edge` are typed
   `InvertibleFunction`, and the engine walks edges backward by calling `inverse(...)`. Walking a
   group's Cayley graph requires every generator to be invertible (a group axiom).
2. **Display / compose / animation pipelines** (demos, notebooks, `mathutils.py`): they need
   `@`-composition, a LaTeX label and interpolation, but not an inverse.

`project`/`reject` belong to consumer 2 but must never be consumer-1 edges, yet a `labeled(project)`
type-checked as an `Edge` and raised `NotInvertibleError` only when the graph was walked backward — a
runtime landmine a good abstraction makes unrepresentable. A secondary problem: `project`/`reject`/
`reflect` were typed `-> MultiVectorFn` (erased to `MultiVectorBase`), so a labelled projection would
not `@`-unify with a concretely typed factory under the invariant `Generic[V]` (hit while writing the
`labeled` tests). Also noted: `to_matrix` keys off `linearity`, not invertibility, showing
linear/affine and invertible were already orthogonal axes.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-07-17)

- **A layered hierarchy**: a base `ComposableFunction` (call + `latex_repr` + `@`/`compose` +
  `linearity` + `at`/`steps`, no inverse) with `InvertibleFunction(ComposableFunction)` adding
  `inverse` + `latex_repr_inv`. Cayley `Step.fn`/`Edge` stay typed `InvertibleFunction`, so a
  projection-as-edge is a static type error. Rejected: one type plus an `Invertibility` flag
  mirroring `Linearity` (the old "Option 5") — a smaller diff, but it enforces the group invariant only
  by a runtime check.
- **API breakage was acceptable**: a version bump, with mvp's dependency bumped to match, rather than
  trading the invariant away to avoid churn.
- **Housing — Option A, a new leaf module** `src/gacalc/functions.py`. It imports **nothing internal**
  (else the cycle with `base` returns), so its `TypeVar` is **unbounded**; the abstraction is
  domain-agnostic (its doctest runs on plain `int`s). Chosen over B2 (the hierarchy defined in `base`,
  keeping the `MultiVectorBase` bound) for separation of concerns. The layering rule was relaxed and
  documented in `CLAUDE.md` rather than silently broken. `transforms.py` keeps the GA-specific
  factories and `to_matrix` and **re-exports** the moved names.
- **`Self` typing was first chosen, then decided against** the same day: the morning's plan was
  `-> ComposableFunction[Self]` on the algebra methods; the implemented form types returns at
  `MultiVectorBase`, keeping `base` cast-free, and a caller wanting the concrete parameter casts at the
  use site. Measured: 0 casts in the core, ~0 in real callers. The cost of this whole effort was the
  invertible/composable distinction itself, not the module split.

## What was done

- `src/gacalc/functions.py`: `ComposableFunction`, `InvertibleFunction`, `Linearity`,
  `NotInvertibleError`, `compose`/`inverse`/`identity`; `base.py` imports it; `transforms.py`
  re-exports it for back-compat.
- `project`/`reject` return `ComposableFunction`; `reflect`/`identity` return `InvertibleFunction`, with
  auto-derived labels `P_{…}` / `P^{\perp}_{…}` / `\mathrm{refl}_{…}` / `I`. `compose` returns
  `InvertibleFunction` iff all parts are (overloads); `inverse()` raises `NotInvertibleError` on a
  non-invertible. The `InvertibleFunction` constructor was reordered to keyword-friendly
  `(func, latex_repr, inverse, latex_repr_inv, *, linearity/interpolate/components)`.
- **`labeled` was removed**: callers construct `ComposableFunction`/`InvertibleFunction` directly.
- **mvp**: 2 constructor sites (`perspective`/`ortho` in `mathutils.py`) moved to keyword args;
  `requirements.txt` pinned `gacalc>=0.0.9`.

## Verification

gacalc containerized `make test`: **285 passed** (fresh generation, pinned toolchain); host ty + ruff
clean. mvp was checked against the new gacalc by a host smoke test (perspective round-trips,
`plane_rotation` works); its full container gate waited on gacalc 0.0.9 reaching PyPI.

## Follow-ups (spun off)

`tasks/composable-function-followups.md`: (1) reassess the `functions` vs `transforms` module names
from a newcomer's view; (2) decide whether the animation layer (`at`/`steps`) sits on the base
`ComposableFunction` or only on `InvertibleFunction`.
