# Should mvp's Cayley-graph and graphing-calculator code move to gacalc? (investigation)

**Done:** 2026-11-13. **Created:** 2026-11-05 (William Emerison Six <billsix@gmail.com>).
**Follow-on:** `tasks/move-mvp-gl-toolkit-to-gacalc.md` (the umbrella, with steps 1 to 4 in gacalc
and step 5 in github.com/billsix/modelviewprojection), plus `tasks/grapher3d-lit-mesh.md`.

## Outcome

The maintainer decided to move all of it into gacalc. That covers the Cayley graph and scene, mvp's
whole OpenGL toolkit, and the 2D and 3D graphers as library functions. mvp keeps only thin grapher
runners and its book demos (William Emerison Six <billsix@gmail.com>, 2026-11-13). The investigation
had recommended much less, so the reasoning that changed it is recorded below.

## What the investigation found (2026-11-05)

It worked from a static reading of both repos.
- `cayley/cayleygraph.py` (366 lines) imports only `gacalc.transforms`. It is pure math and fits
  next to `functions.py` and `Frame`.
- `cayley/cayleyscene.py` (495 lines) imports numpy, mvp's `mathutils.rotate_x` and `rotate_y`, and
  plain GUI and animation dataclasses. It contains no GL.
- `graphingcalculator/grapher2d.py` and `grapher3d.py` (about 1,150 lines) need glfw, PyOpenGL,
  imgui_bundle and mvp's GL toolkit (`cayley_gl`, `_pipeline`, `matrix_stack`). They plot plain
  `f(x)` and `f(x, y)` and contain no geometric algebra.
- **Naming trap:** mvp's "Cayley graph" is a graph of coordinate frames (a groupoid of invertible
  transforms). It is not a Cayley table of blade multiplication.

It offered four options:
- (a) move the graphers and the scene;
- (b) copy them;
- (c) move only `cayleygraph.py`;
- (d) leave everything in mvp.

It recommended (d), or (c) if gacalc should own the frame-graph abstraction. It rejected (a) and (b)
because gacalc's dependencies are only numpy and sympy, and because moving the graphers without the
toolkit would create a dependency cycle.

## Why the decision went further (2026-11-13)

- **The maintainer wants gacalc to plot with OpenGL**, alongside its ePiX figures (github.com/billsix/epix-mirror).
  The "no GL in a numpy and sympy library" objection is answered by making the GL dependencies an
  optional `gl` extra, so `pip install gacalc` stays numpy and sympy only.
- **The cycle goes away if the toolkit moves too.** mvp already depends on gacalc, so moving
  `cayley_gl`, `_pipeline`, `labels`, `matrix_stack` and the shaders into gacalc keeps the
  dependency pointing from mvp to gacalc.
- **The Cayley graph is math**, in the maintainer's view, so it belongs in the math library. That
  goes beyond option (c): the scene moves as well as the graph.
- A first counter-proposal was weighed and set aside: keep the pure-numpy core in gacalc, keep the
  GL runners in mvp, and give gacalc a matplotlib runner. Once the toolkit moves, a gacalc OpenGL
  runner costs nothing extra.
- The maintainer's own suggestion of a *copied* runner in each repo became one library function
  (`grapher2d.run(functions)`) with a short runner per repo, so only the function lists differ.
- **Licence:** the maintainer wrote both libraries (confirmed by `git log`). Moved code becomes
  LGPL-2.1-only, like the rest of gacalc.
- mvp's `rotate_x`, `rotate_y` and `rotate_z` are replaced with direct `transforms.plane_rotation`
  calls, not copied.
- The lit-mesh task moved from mvp to gacalc and waits for the move.

The full decision list is in the umbrella's "Decisions".
