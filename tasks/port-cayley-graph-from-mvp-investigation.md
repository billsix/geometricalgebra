# Should mvp's Cayley-graph and graphing-calculator code move to gacalc?

**Status:** proposed — investigated 2026-11-05; needs the maintainer's decision (open question 1)
**Priority:** 7
**Difficulty:** 2 (decision) / 4 (option c, if chosen)
**Created:** 2026-11-05 (William Emerison Six <billsix@gmail.com>)

## BLUF

The maintainer thought porting modelviewprojection's Cayley-graph and graphing-calculator work into gacalc
"might" make sense. Only one piece fits: `cayleygraph.py`, a pure graph of coordinate frames joined by gacalc
`InvertibleFunction`s. Its only import is gacalc. The graphing calculators and the Cayley scene/viewer need
OpenGL + imgui, contain no geometric algebra, and would push a GL stack onto a numpy+sympy library. Done means
the maintainer picks an option below, and if it's (c), a follow-on implementation task exists.

## Context

- mvp is github.com/billsix/modelviewprojection. It depends on gacalc (`requirements.txt: gacalc==0.0.20`), not
  the other way round. Its `CLAUDE.md` calls the Cayley graph + `InvertibleFunction` its central abstraction.
- gacalc already writes about mvp's Cayley layer: `tasks/reference/composable-function-algebraic-identity.md`
  (why "groupoid/torsor"). `src/gacalc/frame.py` has `Frame.to_invertible_function()`.
  `tasks/reference/book-outline.md` (Part I) asks for "something that works like their graphing calculator".

## Findings (2026-11-05, static reading of both repos)

| mvp file | Lines | Depends on | Fit for gacalc |
|---|---|---|---|
| `src/modelviewprojection/cayley/cayleygraph.py` | 366 | only `gacalc.transforms` (`InvertibleFunction`, `compose`, `identity`, `inverse`); unit-tested by `tests/test_cayley_graph.py` | **good**: pure math, sits next to `functions.py` and `Frame` |
| `cayley/cayleyscene.py` | 495 | numpy, mvp `mathutils.rotate_x/rotate_y`, GUI/animation types (`GuiButton`, `Timeline`, `to_matrix`) | poor: viewer code |
| `graphingcalculator/grapher2d.py`, `grapher3d.py` | 610 + 519 | glfw, PyOpenGL, imgui_bundle, mvp `cayley_gl`, `_pipeline`, `matrix_stack` | poor: plots plain `f(x)` / `f(x, y)`; no GA content |

- gacalc's runtime dependencies are only `numpy` and `sympy`. It has no glfw / PyOpenGL / imgui; mesa comes in
  only under `USE_SPYDER`. Its visualization is matplotlib and notebook based (`src/gacalc/nbplotutils.py`,
  `notebooks/display*.py`, ePiX figures, `tasks/displaygraded-geometric-plots.md`).
- **Naming trap:** mvp's "Cayley graph" is a graph of coordinate *frames* (a groupoid of invertible
  transforms). It is not a Cayley table or graph of basis-blade multiplication. A blade multiplication table
  would be new, separate gacalc work. `tasks/reference/design-decisions.md` records rejecting a Cayley-table
  *representation* (`DenseEuclidean(n)`), which is a different question.
- Moving the graphers to gacalc would either add GL dependencies to gacalc or create a dependency cycle, since
  they need mvp's `cayley_gl`.

## Options

- **(a) Move the graphers and the scene to gacalc.** Not recommended, for the reasons above.
- **(b) Copy them into gacalc.** Not recommended: two copies across repos, no gain.
- **(c) Move only `cayleygraph.py` into gacalc** (e.g. `gacalc.framegraph`). The maintainer owns both
  copyrights, so relicensing from mvp's GPL-2+ to gacalc's licence is fine. Cost: a new gacalc module plus its
  tests (moved from mvp) and a reference-doc section, a gacalc release, then in mvp an import change in
  `cayleyscene` and the 7 visualizations plus a pin bump. The scene, `cayley_gl` and the graphers stay in mvp.
- **(d) Leave everything where it is.**

**Recommendation:** (d) for the graphers and the scene. (c) only if gacalc should own the "frames joined by
invertible functions" abstraction, which its reference docs already discuss. That is the one place where
"might make sense" holds up.

Separately, the book-outline's "graphing calculator" would be better built in gacalc as a matplotlib/notebook
tool on `nbplotutils` than ported from mvp's OpenGL graphers. That would be its own task.

## Open questions

1. Which option: (c) move `cayleygraph.py` into gacalc, or (d) leave everything in mvp? Recommendation: (d)
   unless you want gacalc to own the frame-graph abstraction; if so, (c).
