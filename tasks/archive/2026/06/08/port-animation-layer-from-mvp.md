# Port the InvertibleFunction animation layer from mvp into gacalc

**Completed:** 2026-06-08

## Background

modelviewprojection (mvp) was migrating its math onto gacalc (github.com/billsix/modelviewprojection
`tasks/archive/2026/07/09/gacalc-math-migration.md`). mvp's `InvertibleFunction` was a strict superset
of gacalc's plainer `(func, inverse, latex_repr, latex_repr_inv)`: it added an animation layer that
interpolates a transform from identity (`t=0`) to its full effect (`t=1`) and iterates a composite's
leaf steps. For mvp to delete its own class and import gacalc's, the layer had to live in gacalc first,
and mvp depends on gacalc from PyPI (then `0.0.3`), so it also needed a release.

## What landed

All in `transforms.py`, ported from mvp's `src/modelviewprojection/mathutils.py`:

- Two optional fields on `InvertibleFunction`: `interpolate` (a primitive's law mapping `t∈[0,1]` to
  the partial function) and `components` (a composite's constituents).
- `at(t)` with three-tier resolution: use the `interpolate` law; else
  `compose([c.at(t) for c in components])`; else (hand-built) a step — identity until `t≥1`, then the
  function itself.
- `steps()` yields the leaf primitives in application order, flattening nested composites.
- The factories attach laws: `translate(b)` → `translate(b * t)`; `uniform_scale(m)` → linear `1→m`;
  `scale_non_uniform(*f)` → per-factor linear `1→fᵢ`; `identity()` → identity.
- `compose(...)` always stores `components=list(functions)`, without which `at`/`steps` cannot recurse.
- **`inverse` commutes with `at` at every `t`**, not just the endpoints, so an against-the-arrow edge
  (world→camera) animates smoothly instead of snapping: `inverse(f).interpolate(t) =
  inverse(f.interpolate(t))`, and `inverse(f).components = [inverse(c) for c in reversed(...)]` — the
  inverse-of-a-composition rule applied to the interpolation structure.
- `InvertibleFunction` became `Generic[V]` again (bound to `AbstractMultiVector`), as it was in mvp;
  the type-preserving operations (`__call__`, `at`, `steps`, `@`, `inverse`, `compose`, `translate`,
  `compose_intermediate_fns`) are parameterized.

Tests in `tests/test_transforms.py` ported mvp's interpolation suite and added more: `at(0)` is
identity and `at(1)` the full function; midpoints for translate and scale; invertibility at every `t`;
composites recurse without a stored law; `steps()` counts leaves and an inverted composite decomposes
into inverted leaves; the headline guard `inverse(f).at(t)(p) == inverse(f.at(t))(p)` for a primitive
and a 3-deep composite; against-the-arrow equals the negated parameter
(`inverse(T.at(t)) == translate(-b*t)`). `ty`/`ruff` were clean and the full suite passed (200).

mvp consumed it: its rebuilt rotations carry their laws via `interpolate=`, driving `at()`/`steps()`,
confirmed working on 2026-06-08. The formal PyPI wheel release was left to the maintainer as a separate
step.

## Decisions

- **Module shape: on the class in `transforms.py`, replicating mvp — not a separate module.** The
  maintainer had first asked for a new module under `gacalc`. Two designs were weighed: (A) the enriched
  class in `transforms.py`, so the factories naturally produce it, with no circular import and one type;
  (B) an animation-capable class and interpolating factories in a new `gacalc/animation.py`, cleanly
  separated but with two flavours of every factory. The maintainer decided on the class, keeping one
  type and one import path for mvp.
- `compose` stores `components` always (tiny memory cost, simplest), not only when animation is used.
- The field additions were coordinated with the linearity tag
  (`tasks/archive/2026/06/08/classify-functions-linear-affine-nonlinear.md`) and the matrix work
  (`tasks/archive/2026/06/08/invertiblefunction-to-matrix.md`), which touch the same
  `InvertibleFunction` / `compose` surface.
