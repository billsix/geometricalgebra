# Step 4: the 2D and 3D graphers as `gacalc.gl` library functions, plus gacalc's runners

**Status:** proposed, approved (the umbrella's decisions).
**Priority:** 4
**Difficulty:** 5
**Created:** 2026-11-13
**Part of:** `tasks/move-mvp-gl-toolkit-to-gacalc.md`
**Depends on:** step 3 (`gacalc.gl`).
**Next:** the gacalc release, then mvp's step 5
(github.com/billsix/modelviewprojection `tasks/move-mvp-gl-toolkit-to-gacalc-step-5-mvp-switch.md`).

## BLUF

mvp's `graphingcalculator/grapher2d.py` (621 lines) and `grapher3d.py` (530) are scripts. They
`sys.exit` when imported and keep their window, view and GL objects as module-level globals. Turn
each into a library module, `gacalc.gl.grapher2d` and `grapher3d`. Each module gets one entry
point, `run(functions)` (2D) or `run(surfaces)` (3D), which opens the window and runs the loop.
Then add gacalc runner scripts that pass gacalc's own function lists. Done means:
- both modules import without opening a window;
- the pure-geometry builders are doctested;
- the gacalc runners plot their functions;
- the gacalc release is staged.

## Context

- **What each script holds now** (read mvp's files first):
  - the authored data types `PlottedFunction` (2D) and `Surface` (3D);
  - the module-level lists `FUNCTIONS` and `SURFACES`;
  - view state (`View2D`, `View3D`);
  - pure numpy geometry builders (`sample_curve`, `build_grid`, `build_axes_and_ticks`,
    `build_basis_*`, `build_origin_dot`, `build_wireframe`, `build_solid`, `build_axes`);
  - after the `if __name__ != "__main__": sys.exit(...)` guard, the window, the GL objects, the
    imgui menubar, the key/mouse handlers, and the event loop at module level.
- **Shape:**
  - the data types and builders become plain module-level definitions, importable and doctested;
  - the window, GL objects and view state become locals of `run` or fields of a small state
    dataclass that `run` creates, replacing the globals the handlers mutate now;
  - the function list becomes `run`'s argument.

  This is the one deliberate restructure in the initiative. Keep the behaviour identical:
  - same controls and same menubar;
  - 2D: one sample per pixel column, and the depth clear after the backdrop;
  - same labels.

  mvp's `tasks/reference/gl-and-imgui-gotchas.md` section 8 explains the 2D plot traps; copy what
  applies into gacalc's `tasks/reference/gl-toolkit.md` (from step 3).
- **Runners.** gacalc's go in a new `demos/` or `examples/` directory of gacalc. Pick whichever
  matches the repo's existing demo layout (e.g. `notebooks/`). Each is about 20 lines: an authored
  function list and a `run(...)` call. They can plot GA-flavoured functions, but that is optional;
  the point is that each repo owns its own list (umbrella decision 3).
- `imgui.ini` sits beside mvp's graphers (`graphingcalculator/imgui.ini`). Decide whether imgui
  should write it into the working directory or nowhere (`imguiio.ini_filename = None`), and record
  the choice.

## Plan

1. Create `src/gacalc/gl/grapher2d.py` and `grapher3d.py` in the shape above, with the LGPL header.
2. Add doctests for the builders, for example the vertex count from `build_grid(1.0)` and the
   triangle count from `build_solid`.
3. Add the two gacalc runners and check them by eye on the host (only the maintainer can see a
   window) or under Xvfb with a screenshot.
4. Run `make test` and `make type-check`.
5. Add a `CHANGELOG.md` `[Unreleased]` entry. Then stage the release: bump `version` in
   `pyproject.toml` (new features before 1.0 mean `0.Y.0`, so `0.2.0` unless `[Unreleased]` already
   names a version) and promote `[Unreleased]`. The maintainer tags and publishes.
