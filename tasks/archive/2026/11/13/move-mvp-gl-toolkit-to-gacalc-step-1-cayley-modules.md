# Step 1: move mvp's Cayley graph and scene into `gacalc.cayley`

**Done:** 2026-11-13. **Created:** 2026-11-13.
**Part of:** `tasks/archive/2026/11/13/move-mvp-gl-toolkit-to-gacalc.md`
**Next:** `tasks/archive/2026/11/13/move-mvp-gl-toolkit-to-gacalc-step-2-graphics-container.md`

## Outcome

`src/gacalc/cayley/` now holds `cayleygraph.py` and `cayleyscene.py`, copied from
github.com/billsix/modelviewprojection (`src/modelviewprojection/cayley/`). Their tests moved with
them: `tests/test_cayley_graph.py`, `test_cayley_scene.py` and `test_focus_to_matrix.py`. Nothing
in the subpackage imports `modelviewprojection` or OpenGL, and gacalc gained no dependency. mvp still
has its own copies; step 5 removes them.

- **Mechanics.** `tasks/adhoc/move-mvp-gl-toolkit-to-gacalc/copy_from_mvp.sh` did the copy. It
  replaces each file's leading comment block with gacalc's LGPL-2.1-only header (read from
  `tests/test_rotate_90_degrees.py`, with its `2025-2026` copyright, as gacalc's `CLAUDE.md`
  requires) and rewrites the imports of modules that have already moved. Steps 3 and 4 reuse it.
  Everything else was edited by hand.
- **Rotations.** `cayleyscene.CameraControls.apply` called mvp's `mathutils.rotate_y` and `rotate_x`.
  It now calls `plane_rotation(Vector.e_3, Vector.e_1)` and `plane_rotation(Vector.e_2, Vector.e_3)`
  directly (umbrella decision 4). The scene never displays those functions' LaTeX labels, so the
  `latex_repr` arguments mvp passed were not needed.
- **Tests.** The three test files bind module-level `rotate_x`, `rotate_y` and `rotate_z` from
  `plane_rotation`, so their expected-value arithmetic reads as it did in mvp. This was a judgment
  call: the bindings are test-local, not library API, so decision 4 (no copied helpers in the
  library) still holds. The header comments that pointed at mvp task docs became module docstrings.
- **Vectors from the basis constants.** Every `Vector(x, y, z)` and
  `Vector(coeff_e_1=…, …)` call in the moved modules, doctests and tests became a basis-constant
  sum with every coefficient written out, as gacalc's `CLAUDE.md` requires (the maintainer caught
  that the first pass had kept mvp's constructor calls). Examples:
  - `PADDLE1_POS = -9.0 * e_1 + 1.0 * e_2 + 0.0 * e_3`;
  - `translate(b=self.px * e_1 + self.py * e_2 + self.pz * e_3)` in `CameraControls.apply`;
  - `to_matrix` probes `f(1.0 * e_1 + 0.0 * e_2 + 0.0 * e_3)`.

  `tasks/adhoc/move-mvp-gl-toolkit-to-gacalc/basis_vectors.py` did the rewrite. It keeps each
  coefficient exactly as written (floats stay floats, ints stay ints), so no numeric path changed;
  a second run made no changes. `test_focus_to_matrix.py`'s `_v` helper, which only wrapped the
  constructor, was inlined into its one call.
- **Docstrings.** References that were false in gacalc were rewritten:
  - "for the `mvpvisualization` demos" and "per Bill";
  - mvp's "decision #4", which became "the projective squash stays a shader";
  - a link to this repo, which became "in this repo".

  Paragraphs the copy had left with one-word lines (an old 80-column reflow) were reflowed, per the
  house rule against orphaned words. No code changed apart from the rotation calls and the imports.
- **Docs.** The `CHANGELOG.md` `[Unreleased]` "Added" entry, a `gacalc.cayley` entry in
  `CLAUDE.md`'s "Module layout", and an update to
  `tasks/reference/composable-function-algebraic-identity.md`: its Cayley-graph section now
  describes `gacalc.cayley`, with the frame-graph vs blade-table naming trap.

## Verification

- In the sandbox, `pytest` on the three test files plus `src/gacalc/cayley`'s doctests gave 35
  passed.
- `make format` (nested) exited 0. ruff fixed the import order in four of the new files and
  reformatted four, and `ty` and the changelog check passed.
- `make test` (nested) exited 0: 1,220 passed, 2 skipped, 11 deselected (the `slow` tests) in
  69 s. That run includes `src/gacalc/cayley/*` doctests, `test_cayley_graph.py` (14),
  `test_cayley_scene.py` (15) and `test_focus_to_matrix.py` (2).

## Gate cost (for steps 2 to 4)

Each nested `make test` or `make format` after a `src/` change rebuilt the image from `COPY src`
onward. Every earlier layer came from the host's cache, but saving the last few layers through
fuse-overlayfs took 15 to 20 minutes per run. pytest itself took 69 s.
