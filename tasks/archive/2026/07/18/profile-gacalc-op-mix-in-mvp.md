# Profile gacalc's real op-mix in mvp workloads (CtC + demos + mvpVisualization)

**Created:** 2026-07-18 · **Completed:** 2026-07-18

The maintainer asked to profile gacalc on the real mvp consumers by live play, collect profiles, and
produce a fast-path plan. The op-mix was captured for soccer, kinetix and avenger (2D) and the
mvpViz perspective scene (3D); the findings drove the fast paths implemented in
`tasks/archive/2026/07/18/generated-dispatch-fast-paths.md`. That task had asked for metrics "from Code
the Classics, in 2D"; this widened them to 3D, since the mvp demos and `mvpvisualization` exercise
`Vector3`/`G3`. A broader sweep (the remaining CtC games, a numbered book demo, more mvpViz scenes) was
optional extra coverage and was not pursued.

## Method

- **Workloads**, all in the mvp container under software GL: CtC games (`python vol1/<game>/<game>.py`
  from `ports/codetheclassics/`), mvp demos (`python -m modelviewprojection.demos.demoNN`), and
  mvpVisualization (`python -m modelviewprojection.mvpvisualization.<name>`).
- **Op-mix counter (the primary signal)**: an env-gated (`GACALC_PROFILE=1`) `sitecustomize.py`
  monkeypatch shim wrapping the `Vector2/Vector3/G2/G3` (+ graded) dunders and tallying calls **by
  operand-type pair**, dumped per run. Counts are framerate-independent, which mattered because
  software GL dominated wall-clock. py-spy sampling was planned as a secondary signal; the counter
  carried the analysis. Nothing was committed to gacalc.
- **Custom gacalc**: a local gacalc 0.0.9 wheel (`make dist`, generated `g*.py` baked) installed over
  the PyPI pin in a trimmed mvp image (`BUILD_DOCS=0 USE_EMACS=0 USE_JUPYTER=0 USE_SPYDER=0
  USE_X_WINDOWS=1`), as a temporary build-file addition under the maintainer's standing dev-tool
  arrangement, reverted at close. The maintainer played each game; the agent aggregated.
- **Environment**: nested podman with `--cgroups=disabled`; no `/dev/dri`, so Mesa llvmpipe (GL 4.6
  Core, Mesa 26.1.4) — a boing smoke test confirmed windowed software GL worked; display passthrough
  mirrored mvp's `shell` flags (incl. `PYGLFW_LIBRARY=/usr/lib64/libglfw.so.3`).
- **Gotchas**: automated `PGZERO_MAX_FRAMES` timing probes appeared to run at <1 fps, but that was
  Wayland frame-callback throttling of an unfocused surface, not slow rendering; with the window
  focused it was smooth, so headless fps numbers were ignored. The shim's SIGTERM handler didn't always
  win the race under a C GL call (`podman stop` → SIGKILL / exit 137); a 2 s periodic flush was the
  backstop, so every run's data was captured to within ~2 s.

## Results

Raw JSON was kept in the session scratchpad (not committed). Counts include internal delegation (one
`magnitude()` → `magnitude_squared` → `scalar_product` → `reverse` + `__mul__`), deliberately, to show
the real dispatch load.

- **soccer (2D, 37.5 s, 3,890,825 calls) — math-bound.** `__mul__` 803,535 (Vector2×Vector2 560k;
  scalar: float 172k / sympy Float 63k / int 7k); `scalar_product(Vector2)` 560,176; `magnitude`,
  `magnitude_squared`, `reverse` 537,244 each; `__sub__(Vector2)` 379,221; `__add__(Vector2)` 188,491;
  `__iter__` 153,448; `normalize` / `__abs__` 96,133 each. The magnitude chain alone was ~1.7 M of
  3.9 M calls.
- **kinetix (2D, 82 s, 102,809 calls) — render-bound.** `__iter__` 92,842 (**90%**, `list(vector)` for
  sprites); `__add__(Vector2)` 9,112; `__mul__` 172; magnitude chain 56–136; `Rotor2.sandwich` 9 (the
  `_turn`); one `__mul__(One)`, the first sighting of the rotor sympy leak in `_turn`.
- **avenger (2D, 82 s, 479,612 calls) — mixed.** `__iter__` 174,801; `__mul__` 62,419; magnitude chain
  ~39,9k each; `__add__` / `__sub__` 33,641 / 26,696; `normalize` / `__abs__` 11,262 each.
- **mvpviz_perspective (3D, 133 s, 730,357 calls) — rotor-and-arithmetic-bound.** `Rotor3.sandwich`
  201,072 (the #1 op); `Vector3.__add__` 137,808, `__sub__` 109,568; `Bivector3.__add__` 100,556,
  `__mul__` 50,284 (rotor build); `Rotor3.reverse` 49,696; `Vector3.__neg__` / `__mul__` ~40,7k each;
  the magnitude chain was nearly absent (3–6), the opposite of soccer.

## Conclusions (fed to the fast-path task)

- **Same-type binary ops dominated every workload**, 2D and 3D → candidate #1, an exact-type early-out
  before the `match` ladder, was the broadest win.
- **The magnitude chain** was soccer's #1 cost and large in avenger → candidate #4, closed-form
  `magnitude`/`magnitude_squared`/`normalize` on the graded types, was the biggest 2D lever.
- **`__iter__`** was huge in the render-bound games → a cheap `__iter__`, or fewer `list()` conversions
  at the render boundary.
- **`Rotor3.sandwich`/`reverse` + `Bivector3` add/mul** were the 3D hot paths: keep the sandwich's
  closed form fast; consider `Bivector3` fast paths. Scalar mul on `Vector3`/`Bivector3` mattered too
  (candidate #3).
- **The sympy leak** (`__mul__(Float)` 63k in soccer, `__mul__(One)` in kinetix) was a
  numeric-preservation issue in `_turn`/`plane_rotation`, a correctness-flavoured perf fix.
