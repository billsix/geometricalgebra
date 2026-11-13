# Step 3: move mvp's OpenGL toolkit into `gacalc.gl`

**Done:** 2026-11-13. **Created:** 2026-11-13.
**Part of:** `tasks/move-mvp-gl-toolkit-to-gacalc.md`
**Next:** `tasks/archive/2026/11/13/move-mvp-gl-toolkit-to-gacalc-step-4-graphers-as-library.md`

## Outcome

`src/gacalc/gl/` now holds, from github.com/billsix/modelviewprojection (mvp):
- `matrix_stack.py`, from `src/modelviewprojection/`;
- `_pipeline.py`, `cayley_gl.py` and `labels.py`, from `mvpvisualization/`;
- all **eleven** shaders from there (`billboard.{vert,frag}`, `passthrough.frag`,
  `passthrough_geom.frag`, `per_vertex_color.vert`, `uniform_color.vert`, `thick_lines.geom`, and
  `project_{identity,modelview2d,ortho,perspective}.glsl`). The plan's count of ten missed
  `thick_lines.geom`.

`tests/test_matrix_stack.py` moved too. mvp keeps its copies until step 5. Durable knowledge from
this step is in `tasks/reference/gl-toolkit.md`, new in this step.

- **`gacalc/gl/__init__.py`** imports no GL module. It documents the subpackage and defines
  `SHADER_DIR`, the shaders' directory, with a doctest listing the vertex shaders.
- **Shaders as package data:** `[tool.setuptools.package-data] "gacalc.gl" = [...]` in
  `pyproject.toml`. A wheel built in the image contains all eleven.
- **The import boundary is tested.** `tests/test_gl_import_boundary.py` imports `gacalc`,
  `gacalc.g3`, `gacalc.cayley.cayleyscene` and `gacalc.gl`, each in a fresh interpreter with
  `PYTHONPATH` set to this checkout's `src/`. Without that, the subprocess imported the image's
  installed, non-editable gacalc. It fails if glfw, OpenGL, imgui_bundle or PIL gets imported.
- **Mechanics:**
  - `copy_from_mvp.sh` (from step 1) copied the Python files;
  - `tasks/adhoc/move-mvp-gl-toolkit-to-gacalc/copy_shaders.py` copied the shaders. It replaces a
    leading `// Copyright` block with gacalc's LGPL header as `//` comments, and adds the header
    above any shader that had none.
  - Its first version stripped *any* leading `//` block, which dropped the explanatory first
    comments of the four `project_*.glsl` files. The agent's own body-equality check had ignored
    `//` lines and missed it. An exact comparison caught it, and the script was fixed and rerun:
    every shader body now matches mvp's byte for byte below the header.
- **gacalc conventions applied to the moved code:**
  - `_cross_arrays` builds its operands from basis constants (`float(a[0]) * e_1 + …`) rather than
    `Vector(*map(float, a))`;
  - docstrings and comments that were false in gacalc were rewritten: "the mvpvisualization demos",
    demo numbers, mvp task paths, "in a book about matrices", and the claim that `texExpToPng` is
    in the image;
  - two comments that narrated history were made present-tense (the `u_time`/`u_fov` gating note
    and `matrix_stack._not_a_stack`);
  - paragraphs with orphaned one-word lines were reflowed. They were found with a tokenize/ast
    scanner, and a few continuation lines that hold a single unbreakable name were left alone.
    The same scan also fixed four in `gacalc.cayley`.
- **Window-system libraries.** GLFW 3.4 loads its X11 and Wayland libraries with `dlopen`, so
  Fedora's `glfw` package does not depend on them. They were in the image only through other
  packages. `07-install-gl.sh` now names them: `libwayland-{client,cursor,egl}`, `libxkbcommon`,
  `libX11`, `libXcursor`, `libXi`, `libXinerama`, `libXrandr`.
- **Wayland passthrough.** The Makefile's `WAYLAND_FLAGS_FOR_CONTAINER` gained mvp's
  `PYGLFW_LIBRARY=/usr/lib64/libglfw.so.3` and `XDG_SESSION_TYPE=wayland`. The reason (the dual
  X11+Wayland libglfw keeps imgui_bundle's X11 symbol) is in the Makefile comment and the
  reference doc.
- **Docs:** `CHANGELOG.md` `[Unreleased]` "Added" for `gacalc.gl`, a `CLAUDE.md` "Module layout"
  entry, and the new `tasks/reference/gl-toolkit.md`. That doc keeps the entries from mvp's
  `tasks/reference/gl-and-imgui-gotchas.md` §§1, 6, 7 and 9 that apply to the moved code, plus
  the packaging, import-boundary, Wayland and headless facts.

## Verification

All checks ran against the nested image rebuilt with the expanded `07-install-gl.sh`; that
`make image` exited 0.
- `format.sh` (ruff, `ty` over `src`/`tests`/`tools`/notebooks, the changelog guard) passed.
- `make test`'s run line: 1,232 passed, 2 skipped, 11 deselected. That is the previous 1,220 plus
  the moved matrix-stack tests, the four import-boundary checks and the new doctests. The two
  warnings are a Python 3.15 `ctypes.__version__` deprecation inside PyOpenGL.
- Under Xvfb, `_pipeline.compile_program` compiled and linked all 17 vertex × `project_*.glsl` ×
  (with or without `thick_lines.geom`) combinations, plus the billboard pair, from `SHADER_DIR`
  (Mesa 26.2.6, core 3.3 context).
- `rpm -q` in the image found the explicitly listed window-system libraries.

**Not verified here:** a window on a real Wayland session with the new `PYGLFW_LIBRARY` flag. The
sandbox has no compositor, so that needs a `make shell` on the maintainer's host.
