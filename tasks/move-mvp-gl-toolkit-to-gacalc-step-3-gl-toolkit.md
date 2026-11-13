# Step 3: move mvp's OpenGL toolkit into `gacalc.gl`

**Status:** proposed, approved (the umbrella's decisions).
**Priority:** 4
**Difficulty:** 6
**Created:** 2026-11-13
**Part of:** `tasks/move-mvp-gl-toolkit-to-gacalc.md`
**Depends on:** step 1 (`cayley_gl` imports `cayleyscene`) and step 2 (the `gl` extra and a
GL-capable image).
**Next:** `tasks/move-mvp-gl-toolkit-to-gacalc-step-4-graphers-as-library.md`

## BLUF

Copy mvp's GL toolkit into a new `src/gacalc/gl/` subpackage:
- `matrix_stack.py`;
- `mvpvisualization/_pipeline.py`, `cayley_gl.py` and `labels.py`;
- the ten shaders.

The source is github.com/billsix/modelviewprojection, under `src/modelviewprojection/`. Done means:
- `gacalc.gl` imports cleanly in the image;
- the shaders load as package data;
- `test_matrix_stack.py` passes in gacalc;
- `import gacalc` alone still pulls in no GL module.

## Context

- Imports to rewrite:
  - `_pipeline.py` imports `modelviewprojection.matrix_stack`, plus `gacalc.g3.Vector` and
    `gacalc.vectorcalc.cross`, which already point into gacalc;
  - `cayley_gl.py` imports `matrix_stack`, `_pipeline` and `modelviewprojection.cayley.cayleyscene`,
    which becomes `gacalc.cayley.cayleyscene` from step 1;
  - `labels.py` imports only numpy, PyOpenGL and PIL;
  - `matrix_stack.py` imports only numpy. It could live outside `gacalc.gl`, but it serves the GL
    pipeline, so it goes with it.
- The shaders are `billboard.{vert,frag}`, `passthrough.frag`, `passthrough_geom.frag`,
  `per_vertex_color.vert`, `uniform_color.vert` and `project_{identity,modelview2d,ortho,perspective}.glsl`.
  The callers find them with `os.path.dirname(os.path.abspath(cayley_gl.__file__))` (`MVP_SHADER_DIR`
  in the graphers). Ship them as package data, using setuptools `package-data` in `pyproject.toml`,
  so the same lookup works from an installed wheel and not only from the source tree. Check this by
  building a wheel and listing it.
- **Gotcha — doctest collection imports every module.** gacalc's `pytest.ini` runs `--doctest-modules`
  over `src`, so it will import `gacalc.gl.*`. That works only where the `gl` extra and its system
  libraries are installed, which the dev image is after step 2. Either keep it that way, or skip
  `gacalc/gl` when the extra is absent (a `conftest.py` `collect_ignore` keyed on
  `importlib.util.find_spec("glfw")`). A module that opens a window when imported must not exist
  after step 4.
- **Keep `import gacalc` GL-free.** `src/gacalc/__init__.py` must not import `gacalc.gl`. Add a test
  that imports `gacalc` in a subprocess and checks that `glfw` is not in `sys.modules` afterwards.

## Plan

1. Create `src/gacalc/gl/` with the four modules and the shaders. Rewrite the imports and apply
   gacalc's LGPL-2.1-only header.
2. Add the package-data entry and check that a built wheel contains the shaders.
3. Move mvp's `tests/test_matrix_stack.py` into gacalc and add the GL-free-import test.
4. Run `make test` and `make type-check` and fix what they report.
5. Copy the gotchas that apply to this code from mvp's `tasks/reference/gl-and-imgui-gotchas.md`
   (sections 1, 6, 7 and 9) into a new gacalc reference doc, `tasks/reference/gl-toolkit.md`. That
   doc also covers the `gl` extra and the import rule.
6. Add a `CHANGELOG.md` `[Unreleased]` "Added" entry for `gacalc.gl` and the `gl` extra, and update
   `CLAUDE.md`'s "Module layout" and its Packaging line (extras `notebooks`/`jupyter`/`dev`/`gl`).
