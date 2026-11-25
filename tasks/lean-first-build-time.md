# Make the first `make lean` on a fresh checkout fast (done: measured; the claimed cost does not reproduce)

**Created:** 2026-11-21 (William Emerison Six <billsix@gmail.com>), from a slow first build measured while finishing `tasks/archive/2026/11/21/book-opening-vectors-supersede-geometry-types.md`, which recorded `G3.lean` alone at 1725 s. **Done:** 2026-11-25.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-25)

Measure first: split the clean-build time and find the slow proofs before choosing a cache. Caching only hides the cost, so no cache is added.

## Result

- **The 1725 s `G3.lean` figure does not reproduce.** In a clean copy of `proofs/` (empty `.lake/build`, Mathlib cached, 24 cores, Lean v4.34.1), `G3.lean` builds in 4 s, and the whole library builds in **2 min 42 s** wall (6 min 21 s CPU; the per-module times sum to about 265 s). The 2026-11-21 run was most likely in a slow or throttled environment, and the cause was never found, so the figure should not be relied on.
- **Where the time goes:** one module, `ProjectionRotation3D.lean` (119 s of the 162 s wall), because three 𝒢₃ theorems end in a large `field_simp`: `inplane_perp_reject` (about 147 s elaboration), `versor_mul_project_eq` (about 44 s) and `versor_mul_reject_comm` (about 39 s). Everything else is under 12 s per module. Method and numbers are in `tasks/reference/lean-for-gacalc.md` ("Build time (measured 2026-11-25)"), with the profiler command that names slow declarations.
- **Not done:** making those three proofs faster. A plain `generalize` of the denominator does not work (the identity needs the denominator's definition), so a cut needs a structural proof or a polynomial `linear_combination`. That is `tasks/lean-speed-up-projection-rotation-3d-proofs.md`, proposed and optional.
- **CI:** `lean.yml` runs on `v*` tags only, so a first build costs about the wall time above divided over the runner's cores; no change was made.
