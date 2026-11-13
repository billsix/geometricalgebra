# Step 4: the 2D and 3D graphers as `gacalc.gl` library functions, plus gacalc's runners

**Done:** 2026-11-13. **Created:** 2026-11-13.
**Part of:** `tasks/move-mvp-gl-toolkit-to-gacalc.md`
**Next:** the maintainer tags and publishes 0.1.1. Then mvp's step 5
(github.com/billsix/modelviewprojection `tasks/move-mvp-gl-toolkit-to-gacalc-step-5-mvp-switch.md`)
and `tasks/grapher3d-lit-mesh.md`.

## Outcome

- **`src/gacalc/gl/grapher2d.py` and `grapher3d.py`** come from mvp's
  `graphingcalculator/grapher2d.py` (621 lines) and `grapher3d.py` (530). Those were run-by-path
  programs that `sys.exit`ed when imported and kept their window and GL objects as module
  globals.
  - The authored data types (`PlottedFunction`, `Surface`), view state (`View2D`, `View3D`), the
    mesh dataclasses and the numpy geometry builders are now module-level. The builders gained
    doctests: vertex counts for the grid, axes, wireframe, solid mesh and origin dot, the
    arrowhead tip, and a sampled line.
  - `run(functions, title=…)` / `run(surfaces, title=…)` holds everything GL. The program body
    became nested functions that close over the run's state; the three globals the handlers
    rebound (`built_spacing`, `curve_build_key`, `mouse_prev`, and `built_key` in 3D) are
    `nonlocal`, and the function list is the parameter.
  - Behaviour is unchanged: the same controls, menus, constants, per-pixel-column resampling and
    depth clear.
- **Deliberate differences from mvp's programs:**
  - shaders load from `gacalc.gl.SHADER_DIR`;
  - `label_renderer.cleanup()` runs at the end of `run`, before `cayley_gl.shutdown()`, while the
    GL context still exists. mvp used `atexit`, which ran after the context was gone; `cleanup()`
    swallowed the resulting errors;
  - the key handlers' `if`/`elif` chains became a `match` with a `case _` default, the house rule
    for total dispatch;
  - `zip(..., strict=True)` where the curve meshes pair with the functions.
- **Runners: `examples/grapher2d.py` and `examples/grapher3d.py`.** Their functions are computed with
  gacalc:
  - 2D: the e_1 and e_2 coefficients of `e_1.rotate(θ)`, and `|x * e_1 + 1 * e_2|`;
  - 3D: `|x * e_1 + y * e_2|` (a cone), a dot product with `1 * e_1 + 1 * e_2` (a plane), and the
    e_12 coefficient of `a ∧ b` for `a` and its mirror image (a saddle).

  `examples/` sits outside pytest's `testpaths`, so a test run never opens a window;
  `entrypoint/format.sh` gained `ty check examples`. The LaTeX captions follow the book's notation
  rules (explicit `*`, unit coefficients written out).
- **Annotation gaps in the moved code**, found with `tools/check_annotations.py`:
  - `cayleyscene.to_matrix` now takes `InvertibleFunction[Vector]` (it was bare);
  - `_pipeline.make_vao` and `build_cylinders_for_edges` take a `Sequence`, not an invariant
    `list`.

  The remaining rows in the moved files are the exempt kinds (loop targets, enum members, tuple
  unpacks, `TypeVar`s).
- **Docs:**
  - the README's layout lists `cayley/`, `gl/` and `examples/`, and a new "Plotting with OpenGL"
    block gives the commands;
  - `CHANGELOG.md`, `CLAUDE.md`'s module layout, and a graphers section in
    `tasks/reference/gl-toolkit.md` (the 2D traps from mvp's gotchas §8).
  - `imgui.ini` is gitignored, because the headless run left one in the repo root.
- **Release:** version **0.1.1**, `[Unreleased]` promoted to `## [0.1.1] — 2026-11-13`, and
  `tools/check_changelog.py` passes. It is a patch bump because everything is additive, per the
  pre-1.0 rule (breaking → `0.Y.0`, compatible → patch). The plan had guessed 0.2.0. The release
  is not tagged or published.
  - **Found along the way:** the repo has no `v0.1.0` tag (the latest is `v0.0.20`), although
    `CHANGELOG.md` records `## [0.1.0] — 2026-11-10`.

## Verification

All on the nested image, through the targets' own `podman run` lines:
- `format.sh` exited 0 with all six checks clean, including the new `ty check examples`;
- 1,240 tests passed, 2 skipped, 11 deselected;
- all 17 shader combinations compiled under Xvfb;
- both runners ran for 12 s under Xvfb until `timeout -s KILL` (exit 137), with no traceback. Each
  window opened, built its meshes and drew frames.

**Not run:** `make test-full` (the `slow` 3D symbolic frame tests, which nothing here touches; CI
runs it), `make dist` with g4/g5, and a look at the windows on a real display.
