# Move modelviewprojection's Cayley graph, OpenGL toolkit and graphers into gacalc (umbrella)

**Status:** in progress. The gacalc side (steps 1 to 4) is done and committed as version 0.1.1,
which is not yet tagged or published. Step 5, in mvp, waits for that release on PyPI.
**Priority:** 4
**Difficulty:** 7 (the whole initiative; each step is rated in its own doc)
**Created:** 2026-11-13
**Source:** the investigation `tasks/archive/2026/11/13/port-cayley-graph-from-mvp-investigation.md`.

## BLUF

gacalc should be able to plot with OpenGL, alongside its ePiX figures, and it should own the Cayley
graph: coordinate frames joined by `InvertibleFunction`s, which is math, not rendering. This
initiative moves four things from github.com/billsix/modelviewprojection (mvp) into gacalc:
- the Cayley modules;
- mvp's whole OpenGL toolkit;
- the 2D and 3D graphers, as library code.

mvp then imports all of it from gacalc and keeps only thin grapher runners and its book demos. Done
means:
- gacalc ships `gacalc.cayley` and, behind a `gl` extra, `gacalc.gl`;
- a released gacalc carries them;
- mvp pins that release and no longer contains the moved files;
- both repos have short grapher runners that pass their own function lists.

## Context (read first)

- **Dependency direction.** mvp already depends on gacalc (`requirements.txt: gacalc==0.0.20`), so
  moving code mvp uses into gacalc adds no cycle. gacalc must never import mvp.
- **Licence.** The maintainer wrote both libraries (confirmed by `git log` on every file below).
  Moved code takes gacalc's licence, LGPL-2.1-only, matching the rest of the library (William
  Emerison Six <billsix@gmail.com>, 2026-11-13). Each moved file gets gacalc's LGPL-2.1-only header,
  copied verbatim from `tests/test_rotate_90_degrees.py` (`CLAUDE.md`, "License headers"), in place
  of mvp's header. Each step also updates `CLAUDE.md`'s "Module layout" for what it adds.
- **What moves** (mvp paths under `src/modelviewprojection/`, about 3,900 lines):

  | mvp file | Lines | Goes to | Step |
  |---|---|---|---|
  | `cayley/cayleygraph.py` | 366 | `gacalc.cayley.cayleygraph` | 1 |
  | `cayley/cayleyscene.py` | 495 | `gacalc.cayley.cayleyscene` | 1 |
  | `matrix_stack.py` | 559 | `gacalc.gl.matrix_stack` | 3 |
  | `mvpvisualization/_pipeline.py` | 870 | `gacalc.gl._pipeline` | 3 |
  | `mvpvisualization/cayley_gl.py` | 790 | `gacalc.gl.cayley_gl` | 3 |
  | `mvpvisualization/labels.py` | 331 | `gacalc.gl.labels` | 3 |
  | `mvpvisualization/*.vert`, `*.frag`, `*.glsl` (10 shaders) | | `gacalc/gl/` package data | 3 |
  | `graphingcalculator/grapher2d.py`, `grapher3d.py` | 621 + 530 | `gacalc.gl.grapher2d`, `grapher3d` | 4 |

  Tests move with their modules: mvp `tests/test_cayley_graph.py`, `test_cayley_scene.py`,
  `test_focus_to_matrix.py` (step 1) and `test_matrix_stack.py` (step 3).
- **What stays in mvp:** the book, the demos (`demos/demo21`–`demo24`), the other
  `mvpvisualization/` modules (`coordinatesystems`, `model`, `modelview`, `modelview2d`,
  `modelvieworthoprojection`, `modelviewperspectiveprojection`, `pushmatrix`), `pgzero_gl/`,
  `util/shaderutils.py`, `wxapp.py`, `mathutils.py`, and two grapher runner scripts. The book
  quotes none of the moved files as source; `book/docs/ch02.rst` only shows a Cayley-graph figure.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-13)

1. **The GL dependencies are an optional extra.** glfw, PyOpenGL, imgui-bundle[glfw] and Pillow go
   in `[project.optional-dependencies] gl`, like the existing `notebooks` extra. `pip install gacalc`
   still needs only numpy and sympy, so `import gacalc` must never import `gacalc.gl`.
   - PyOpenGL-accelerate, which mvp also pins, was left out in step 2 (the agent's call,
     2026-11-13). It has no binary wheel for Python 3.15, so it would need a compiler that gacalc's
     lean image lacks. It is optional: it speeds up array marshalling and silences an INFO log
     line.
2. **The whole GL toolkit moves**, not part of it, so that `cayley_gl` does not straddle two repos.
3. **The graphers become library functions**, e.g. `gacalc.gl.grapher2d.run(functions)`. mvp and
   gacalc each keep a short runner script that passes its own function list, so the runner is not
   copied between the repos.
4. **mvp's `rotate_x`, `rotate_y` and `rotate_z` are not copied.** The moved Cayley code calls gacalc's
   `transforms.plane_rotation` directly (step 1).
5. **The lit-mesh work waits for the move and lives in gacalc**: `tasks/grapher3d-lit-mesh.md`, moved
   from mvp. Its triangulation and normals are written in gacalc from the start.

**Module names (chosen by the agent, 2026-11-13; change before step 1 if you prefer):** `gacalc.cayley`
for the GL-free graph and scene, and `gacalc.gl` for everything that needs OpenGL. Naming the
subpackage after the extra keeps the rule easy to check: only `gacalc.gl` imports the GL
dependencies.

## Steps (the index)

Each step is its own commit. Steps 1 to 4 are gacalc work and end in a single gacalc release. Step 5
is mvp work.

- [x] 1. `tasks/archive/2026/11/13/move-mvp-gl-toolkit-to-gacalc-step-1-cayley-modules.md`:
      `gacalc.cayley`, GL-free, no new dependencies. Done 2026-11-13.
- [x] 2. `tasks/archive/2026/11/13/move-mvp-gl-toolkit-to-gacalc-step-2-graphics-container.md`:
      the `gl` extra, plus gacalc's image can open a GL window. Done 2026-11-13.
- [x] 3. `tasks/archive/2026/11/13/move-mvp-gl-toolkit-to-gacalc-step-3-gl-toolkit.md`:
      `gacalc.gl` (matrix stack, pipeline, `cayley_gl`, labels, shaders). Done 2026-11-13.
- [x] 4. `tasks/archive/2026/11/13/move-mvp-gl-toolkit-to-gacalc-step-4-graphers-as-library.md`:
      `grapher2d.run` and `grapher3d.run`, plus gacalc's runners, and the 0.1.1 version bump.
      Done 2026-11-13; the maintainer tags and publishes 0.1.1 (`make release`).
- [ ] 5. mvp `tasks/move-mvp-gl-toolkit-to-gacalc-step-5-mvp-switch.md` (in
      github.com/billsix/modelviewprojection): pin the new gacalc, switch the imports, delete the
      moved files, and reduce the graphers to runners.

After step 4: `tasks/grapher3d-lit-mesh.md` (not a step of this initiative; it depends on step 4).

## Cross-step notes

- **Release coupling.** mvp sees nothing from gacalc until a release is published and mvp's pin
  moves. So the gacalc-side steps should land in a single release, not one per step. mvp's pin is
  currently `0.0.20`, and gacalc's next release is `0.1.1`. That bump crosses the breaking changes
  in `CHANGELOG.md` `## [0.1.0]`, which step 5 must also absorb. Installed over mvp's tree in a
  throwaway container, 0.1.1 left mvp's 112 tests passing and its `ty` diagnostics unchanged (22
  before and after), so the jump needs no migration (step 5's doc has the detail).
- **Moved code keeps its behaviour but follows gacalc's conventions.** Moving a file must not change
  what it does, and redesigning it is out of scope. But once it lives in gacalc it is gacalc code,
  so the rules in gacalc's `CLAUDE.md` ("Conventions the agent must obey") apply from the start,
  tests included. The one the mvp code breaks most is **vectors built from the basis constants with
  every coefficient written out** (`-9.0 * e_1 + 1.0 * e_2 + 0.0 * e_3`), never
  `Vector(-9.0, 1.0, 0.0)` (William Emerison Six <billsix@gmail.com>, 2026-11-13).
  `tasks/adhoc/move-mvp-gl-toolkit-to-gacalc/basis_vectors.py` does that rewrite and keeps each
  coefficient's number type; run it on every moved file. Directions stay bare
  (`plane_rotation(Vector.e_3, Vector.e_1)`).
- **GL lore travels with the code.** mvp's `tasks/reference/gl-and-imgui-gotchas.md` sections 1
  (imgui/GLFW), 6 (Python-side traps), 7 (repo-wide GL conventions), 8 (flat 2D plot on the 3D
  setup) and 9 (TeX billboard labels) describe code that moves. Steps 3 and 4 copy what applies into
  a gacalc reference doc. mvp's doc keeps a pointer to it.

## History

The gacalc side ran on one branch over 2026-11-12 and 2026-11-13. In order:

1. **Investigation and plan (2026-11-12 to 2026-11-13).** The investigation
   (`tasks/archive/2026/11/13/port-cayley-graph-from-mvp-investigation.md`) first proposed
   moving only the Cayley modules. The maintainer widened it: gacalc should plot with OpenGL, and
   the Cayley graph is math, so it belongs in a math library. The five decisions above were
   answered "yes" together, and the umbrella, steps 1 to 4 and the lit-mesh task were written.
2. **Step 1, `gacalc.cayley`.** The modules and their tests moved, and the maintainer committed
   them. The first version kept mvp's `Vector(1, 0, 0)`; the maintainer rejected that (gacalc code
   builds vectors from the basis constants, `1 * e_1`), and `tasks/adhoc/move-mvp-gl-toolkit-to-gacalc/basis_vectors.py`
   rewrote every moved file and test. That rule was then added to the cross-step notes so later
   steps applied it from the start.
3. **Step 2, the `gl` extra and a GL-capable image.** PyOpenGL-accelerate was dropped from the
   extra (no Python 3.15 wheel). The GL system libraries got their own late, unflagged image layer
   so the slow TeX and Lean layers before it stayed cached.
4. **Step 3, `gacalc.gl`.** The toolkit and eleven shaders moved, with a test that `import gacalc`
   pulls in no GL module and a reference doc (`tasks/reference/gl-toolkit.md`). The first shader
   copy dropped the explanatory comments of the `project_*.glsl` snippets; the copy script was
   fixed to strip only the leading copyright block. The move also deleted `labels.py`'s claim that
   `texExpToPng` was in the image, because gacalc's image did not build it. That left the graphers
   without labels in gacalc's image, and nothing reported it: the renderer turns itself off when
   the tool is missing.
5. **Step 4, the graphers as library modules, and 0.1.1.** `grapher2d.run` and `grapher3d.run`,
   runners in `examples/`, and a patch bump to 0.1.1 (additions only), committed but not tagged.
   Both runners were checked headless under Xvfb only.
6. **TeX labels restored (2026-11-13).** On a real display the maintainer saw the graphers draw no
   TeX labels, the one problem found. gacalc's image now builds `texExpToPng` under a new
   `USE_TEX_LABELS` flag (on by default, off with `MINIMAL_IMAGE=1`), pinned to the same commit
   mvp builds: `entrypoint/08-install-tex-labels.sh` and `entrypoint/install-texexp.sh`. The
   install script renders one label, so a broken TeX set fails the image build instead of
   silently disabling labels. Choices made along the way:
   - **A flag of its own, not `BUILD_DOCS`.** mvp builds `texExpToPng` under `BUILD_DOCS` because
     its book renders math with it; in gacalc the labels belong to the graphers, not the book, so
     tying them to the docs toolchain would have hidden why the tool is there.
   - **mvp's pin, not GitHub's newest commit.** GitHub's master had moved past the commit mvp pins
     (and past the maintainer's local clone), and no image had built it. The pinned commit already
     builds on Fedora 45 in mvp's image and supports `--fg`/`--bg`.
   - **A stale claim corrected.** `tasks/reference/gl-toolkit.md` said `texExpToPng` ignores
     `--fg`; the pinned commit passes it to `dvipng`. The doc now says only what the code relies
     on: the shader colours the glyph from the texture's alpha.
   - The new layer sits after the GL libraries, so a full nested `make image` reused every earlier
     layer from cache.
7. **Format on exit runs from the repo root (2026-11-13).** Not part of the move, but on the same
   branch: the shell's exit hook (`entrypoint/dotfiles/.extrabashrc`) ran `cd /gacalc/src/` before
   `format.sh`, whose paths are repo-relative, so formatting on exit failed. It now runs
   `cd /gacalc`. The rule was generalized in the shared conventions of
   github.com/billsix/runClaudeInContainer and github.com/billsix/runCrushInContainer and in the
   maintainer's personal conventions.
