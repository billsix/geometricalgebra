# Make the transforms (translate/rotate/scale/compose) work with G1/G2/G3

**Created:** 2026-06-04 · **Completed:** 2026-06-05 (implemented 2026-06-04)

The `InvertibleFunction` transform layer in `gn.py` (`translate`, `uniform_scale`,
`scale_non_uniform_2d`, `rotate`, `rotate_around`, `compose`, …) was hardwired to `Gn`, so a `G2`
input came back as `Gn`. The layer was studied, four options were weighed, and the chosen one was
implemented: the transforms are now representation-preserving (a `G2` in gives a `G2` out).

## Findings (2026-06-04)

The binding to `Gn` was much narrower than it looked. Every function in the layer (`gn.py:190–615`
at the time) was classified and checked at runtime with a `G2` vector:

| Function | Bound to `Gn`? | Why |
| --- | --- | --- |
| `InvertibleFunction`, `inverse`, `compose`, `compose_intermediate_fns[_and_fn]`, `identity` | No | pure plumbing |
| `uniform_scale(m)` | No | `vector * m`; verified `G2`→`G2` |
| `translate(b)` | No | `vector + b`; the type follows `b` |
| `rotate_90_degrees`, `rotate`, `rotate_around` | Yes | bake `e_1 * e_2` from the module-level `Gn` constants |
| `scale_non_uniform_2d` | Yes | `MultiVector.project(onto=e_1)` with the `Gn` basis |
| `is_clockwise` / `is_counter_clockwise` | Yes | `Gn` pseudoscalar + `rotate_90_degrees` |

So only a few factories baked in `Gn` basis constants; the notebook "bug" for `translate` was just
feeding it arguments built from `gn.e_1` instead of `g2.e_1`. A second, representation-agnostic
system already existed on the ABC (`project`, `reject`, `reflect`, `identity`, an angle-free
`rotate(from_vec, to_vec)`), returning bare `MultiVectorFn` callables with no LaTeX, `compose` or
`inverse`. That duality was the design tension.

## Options

- **A — resolve the basis from `type(vector)` at call time** in the few bound factories. Smallest
  change, no duplication, no generator work, works for every present and future algebra. Cost:
  transforms are basis-late-bound, and mixed-type pipelines still coerce (a caller convention).
- **B — the generator emits per-class transforms into each `g*.py`.** Rejected: copies pure
  plumbing that has no representation dependence into every module; much more generator complexity.
- **C — promote the transforms to ABC classmethods.** A legitimate larger refactor, but the ABC
  versions lack LaTeX/compose/inverse, so it would either pull `InvertibleFunction` into `base.py`
  or lose those ergonomics. Not taken.
- **D — pass right-typed arguments only.** A stopgap that left `rotate`/`scale_non_uniform_2d`
  `Gn`-bound and the ask unaddressed.

## Decisions (the maintainer, 2026-06-04)

- **Option A plus two refinements:** (1) relocate the representation-agnostic layer out of `gn.py`
  into its own module, in the **same change** as the generalization, re-exported from `gn.py` for
  back-compat; (2) add a basis accessor to the interchange protocol.
- **The `modelviewprojection` portability constraint was dropped**: the maintainer confirmed that
  project's constraints did not matter here. That removed the main argument against B/C, but A still
  won on its own merits.
- **Rotation stays 2D.** `rotate`/`rotate_90_degrees`/`rotate_around` are inherently planar
  (`e_1∧e_2`), so they stay 2D-assuming but type-preserving. A general vector-to-vector rotation was
  left as a separate future task; the notebook rotation demo went in the G2 notebook only, with G3
  rotation held off until then.
- **Scale is generalized** to n-D `scale_non_uniform(*factors)`, with `scale_non_uniform_2d` kept as
  a thin 2D wrapper.
- The two transform systems (ABC `MultiVectorFn` vs `InvertibleFunction`) were deliberately **not**
  merged in this task.

## What changed

- **New `src/geometricalgebra/transforms.py`** (imports only `base`): `InvertibleFunction`,
  `inverse`, `compose`, `compose_intermediate_fns[_and_fn]`, `identity`, `translate`,
  `uniform_scale`, `scale_non_uniform`, `scale_non_uniform_2d`, `rotate_90_degrees`, `rotate`,
  `rotate_around`, `is_clockwise`, `is_counter_clockwise`, each resolving its basis from
  `type(vector)` where it needs one.
- **`base.py`:** a `basis_vector(i)` classmethod; `unit_pseudoscalar`/`bases` use it.
- **`gn.py`:** the transform layer and the unused `import math` were removed; it re-exports the
  transform names.
- **`nbplotutils.py`:** `cosine`/`sine` broadened to `AbstractMultiVector`; unused `MultiVector`
  import dropped.
- The broken transform doctests (they imported `modelviewprojection.mathutils`) were rewritten
  against `geometricalgebra.transforms` with correct numeric examples, covering item #1 of
  `tasks/archive/2026/06/05/cleanups-and-hygiene.md` for these functions.
- Split out: per-transform type round-trip unit tests went to
  `tasks/archive/2026/06/06/transform-type-roundtrip-tests.md`; the 2D `rotate` / n-D `scale` demo in
  the G2 notebook was folded into `tasks/archive/2026/06/05/port-displaymv-2d-to-displayg2.md`
  (Tier 1).

## Verification

118 tests pass; `ty check src` and `ty check tests` clean; ruff clean; 31 transform doctests pass;
`displaymv`, `displayg2` and `displayg3` execute with exit 0; a smoke test confirmed `G2`/`G3` in →
same type out for every transform with correct values (rotating `3e₁+4e₂` by π/2 gives `−4e₁+3e₂`).
