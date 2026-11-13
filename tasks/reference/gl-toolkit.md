# `gacalc.gl` — the OpenGL toolkit, its packaging, and its traps

**Reference document.** It states what is true of `src/gacalc/gl/` and how to work on it. Read it
before writing or debugging GL, GLFW or imgui code in gacalc. Update it in place.

`gacalc.gl` came from github.com/billsix/modelviewprojection (mvp) on 2026-11-13
(`tasks/move-mvp-gl-toolkit-to-gacalc.md`). mvp's `tasks/reference/gl-and-imgui-gotchas.md` is
where most of these traps were found; its entries cite the debugging sessions. This doc keeps
the ones that apply to the moved code.

## In one paragraph

`gacalc.gl` holds four modules:
- `matrix_stack` — model / view / projection matrix stacks;
- `_pipeline` — GLFW + imgui setup, shader compilation, VAO builders;
- `cayley_gl` — the toolkit that draws `gacalc.cayley` scenes;
- `labels` — TeX billboard labels.

Eleven GLSL shaders ship next to them as package data. The modules need the optional `gl` extra
(glfw, PyOpenGL, imgui-bundle, Pillow), and nothing outside `gacalc.gl` imports them, so
`import gacalc` stays numpy + sympy only. `tests/test_gl_import_boundary.py` enforces that.

## Packaging and the import boundary

- **The `gl` extra** (`pyproject.toml`) is glfw, PyOpenGL, imgui-bundle[glfw] and Pillow.
  PyOpenGL-accelerate is left out: it has no Python 3.15 wheel, and the lean image has no compiler
  to build one. Without it PyOpenGL logs one INFO line at import and marshals arrays a little
  slower.
- **Only `gacalc.gl` imports GL code.** `gacalc/gl/__init__.py` itself imports no GL module, so
  `gacalc.gl.SHADER_DIR` is readable without the extra; the submodules need it.
  `tests/test_gl_import_boundary.py` imports `gacalc`, `gacalc.g3`, `gacalc.cayley.cayleyscene` and
  `gacalc.gl` in a fresh interpreter each and fails if glfw, OpenGL, imgui_bundle or PIL appears in
  `sys.modules`.
- **Shaders are package data.** `[tool.setuptools.package-data] "gacalc.gl" = ["*.vert", "*.frag",
  "*.geom", "*.glsl"]` puts them in the wheel; check with a built wheel, not the source tree.
  Programs load them with `shader_dir=gacalc.gl.SHADER_DIR`.
- **The image always installs the GL stack** (no feature flag). That is the `gl` extra in the
  Python dependency layer, plus `entrypoint/07-install-gl.sh` in its own late layer: GLFW, Mesa
  GL/EGL and drivers, and the X11/Wayland libraries GLFW 3.4 loads with `dlopen`. `make test`
  collects doctests from all of `src/`, so it imports `gacalc.gl`, and the lean CI image
  (`MINIMAL_IMAGE=1`) must pass that gate.

## Running a window

- **On the maintainer's host,** `make shell` passes X11 and Wayland through
  (`X_FLAGS_FOR_CONTAINER`, `WAYLAND_FLAGS_FOR_CONTAINER`).
- **Wayland needs `PYGLFW_LIBRARY=/usr/lib64/libglfw.so.3`**, which the Makefile sets. Fedora's
  libglfw is one build for both X11 and Wayland. Pointed at it, the glfw package loads it first,
  imgui_bundle binds the same library (it needs an X11 symbol), and GLFW picks Wayland at run
  time.
  - Do not use `PYGLFW_LIBRARY_VARIANT=wayland`. It loads a Wayland-only library and imgui_bundle
    dies on the missing `glfwGetX11Window`.
- **`import glfw` before `import imgui_bundle`, always.** The first GLFW loaded into the process
  wins. imgui_bundle bundles an X11-only `libglfw.so.3`; if that one loads first, PyOpenGL cannot
  see the context under Wayland, and every GL 4.2+ ARB-aliased call (`glBindImageTexture`, …) raises
  `NullFunctionError` while `glGetString` still reports 4.6. `cayley_gl` imports glfw and OpenGL.GL
  before imgui_bundle and re-exports `imgui`; programs take imgui from there.
- **Headless (CI, a sandbox)** works with software GL. Run Xvfb outside the container and share its
  socket: `Xvfb :97 &`, then `podman run -e DISPLAY=:97 -v /tmp/.X11-unix:/tmp/.X11-unix …`. glfw
  reports `4.6 (Compatibility Profile) Mesa`. Check the result with `glReadPixels` rather than a
  screenshot, because llvmpipe windows capture black. Wrap every launch in `timeout -s KILL`.

## Conventions the code relies on

- **Matrices are row-major, `M @ column_vector`.** The transpose happens exactly at the
  `glUniformMatrix4fv` boundary (`GL_TRUE`). Do not "fix" that flag.
- **Winding is counter-clockwise everywhere.** Outward normals depend on it, so a new geometry
  builder documents its winding.
- **`-1` means "uniform/attribute not present".** Justify each check on its own: gating one
  uniform's use on another's presence caused a real bug (`cayley_gl` documents it).
- **GL constants are not `int`.** PyOpenGL constants subclass `int` at run time, but the type
  checker sees `OpenGL.constant.Constant`, so enum/bitfield parameters use
  `_pipeline.GLenum` (`int | Constant`), never a `# ty: ignore`.
- **Shaders compose by string concatenation.** GLSL 330 has no `#include`, so `compile_program`
  appends a `project_*.glsl` snippet to the vertex shader. Each shader carries gacalc's licence
  header as `//` comments above `#version`, which GLSL allows. All 17 vertex × snippet ×
  geometry-shader combinations the toolkit uses were compiled and linked under Mesa on 2026-11-13.
- **GL resources are freed through a registry.** Create handles with `_pipeline`'s builders so
  `cleanup()` releases them.
- **A non-zero VAO stays bound.** macOS Core Profile requires one; `_pipeline` binds a default
  VAO on purpose and never binds 0.
- **imgui's `GlfwRenderer(window)` replaces the key callback without chaining.** Set your
  `glfw.set_key_callback` *after* creating it. It also swallows the mouse-button callback, so poll
  `glfw.get_mouse_button` and gate on `imgui.get_io().want_capture_mouse`.
- **Keep sympy out of the frame loop.** gacalc's general transform layer can return symbolic
  coefficients. If a visualization's frame time collapses, check coefficient types first.
  `cayleyscene.to_matrix` casts to float64 for exactly this reason
  (`tests/test_focus_to_matrix.py`).

## The graphing calculators (`gacalc.gl.grapher2d`, `grapher3d`)

- **Shape.** The authored data types (`PlottedFunction`, `Surface`), view state and numpy geometry
  builders are module-level and doctested. `run(functions)` / `run(surfaces)` opens the window and
  owns everything GL: pipelines, meshes, input handlers and the loop, as nested functions that
  close over the run's state (`nonlocal` for the few values they rebind). A runner (`examples/`, or
  modelviewprojection's) is a function list plus one `run` call.
- **2D: resample per pixel column.** Curves are resampled across the visible x range, one sample
  per pixel column, whenever the view pans or zooms. A fixed sample set over a fixed range cannot
  stay smooth when zoomed in and also avoid dropped sub-pixel segments (a dashed look at the peaks)
  when zoomed out.
- **2D: clear depth after the backdrop.** The shared GL setup leaves depth testing on (`GL_LESS`)
  and the whole plot sits at z = 0. A curve pixel over an already-drawn grid pixel then has equal
  depth and is rejected, punching holes in the curve where it runs along a grid line. `frame`
  clears the depth buffer after the backdrop.
- **2D: line smoothing needs blending on.** Thousands of tiny `GL_LINE_STRIP` segments drop pixels
  under GL's diamond-exit rule, so `run` enables `GL_LINE_SMOOTH` with blending. That is also why
  the label pass must restore `GL_BLEND` (below).
- **3D: the solid mesh is unlit**, shaded by normalised height per vertex. The lit (Blinn-Phong)
  version is `tasks/grapher3d-lit-mesh.md`.
- **Checking them headless:** run each runner under Xvfb with `timeout -s KILL 12`. Exit 137 with
  no traceback means it opened the window and drew frames for the whole run (2026-11-13, both
  runners).

## TeX billboard labels (`gacalc.gl.labels`)

- `LabelRenderer` shells out to `texExpToPng` (github.com/billsix/tex-expression-to-png) to render a
  LaTeX string to a transparent PNG. It uploads that as an RGBA texture and draws it as a
  camera-facing billboard (`billboard.vert` / `billboard.frag`) at a constant screen size, in
  both ortho and perspective views (`clip.xy += offset * clip.w`).
- **The image builds `texExpToPng` when `USE_TEX_LABELS=1`** (the Makefile's default; off with
  `MINIMAL_IMAGE=1`), pinned by the Dockerfile's `TEXEXP_COMMIT` ARG to the commit mvp builds.
  `entrypoint/08-install-tex-labels.sh` installs the build tools and the TeX set the tool's
  preamble loads (`standalone` with `varwidth`, `amsmath`, `xcolor`, `dvipng`);
  `entrypoint/install-texexp.sh` fetches, builds and installs it, then renders one label, so a
  broken TeX set fails the image build.
- **Where `texExpToPng` is not on `PATH`, labels turn off silently.** `LabelRenderer.available` is
  `False` and every method is a no-op, so a missing tool shows up only as a grapher with no labels.
  Check with `which texExpToPng` in the container.
- The shader paints the glyph using the texture's **alpha** as a mask, never its RGB, so the label
  colour comes from the shader whatever `--fg` produced.
- texExpToPng writes `formula.tex`/`.dvi` into the current directory, so the renderer runs it in
  its own scratch directory.
- A label pass drawn over another program must save and restore that program's GL state
  (`GL_BLEND`, `GL_DEPTH_TEST`, the VAO). `begin()` / `end()` do this. Forcing a fixed state broke
  grapher2d's line smoothing.
