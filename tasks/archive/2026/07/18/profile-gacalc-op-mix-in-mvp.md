# Profile gacalc's real op-mix in mvp workloads (CtC + demos + mvpVisualization)

**Status:** complete
**Completed:** 2026-07-18 — op-mix captured for soccer/kinetix/avenger (2D) +
mvpViz perspective (3D); findings drove the now-implemented fast paths (see
archived `generated-dispatch-fast-paths.md`). Remaining CtC/demos/mvpViz sweep was
optional extra coverage, not pursued.
**Created:** 2026-07-18 (Bill: profile gacalc on the real mvp consumers, live-play,
collect profiles, produce a fast-path plan)

Companion to `generated-dispatch-fast-paths.md` (the *fix* task). That task requires
op-mix metrics "from Code the Classics, **in 2D**"; **this widens it to 3D** — the
mvp demos + `mvpvisualization` exercise `Vector3`/`G3`, not just CtC's `Vector2`.
Findings here feed the fast-path priorities there.

## Method

- **Workloads** (all run in the mvp container, software GL — see constraints):
  - **CtC** (2D, `Vector2`): vol1 `boing/bunner/cavern/myriapod/soccer`, vol2
    `avenger/beatstreets/eggzy/kinetix/leadingedge`. Launch: from
    `ports/codetheclassics/`, `python vol1/<game>/<game>.py` (each ends in `go()`).
    Hot ones per the fix task: soccer, kinetix, avenger.
  - **mvp demos** (3D, `Vector3`/matrices): `python -m modelviewprojection.demos.demoNN`.
  - **mvpVisualization** (3D + imgui): `python -m modelviewprojection.mvpvisualization.<name>`
    (module-level `cayley_gl.run_loop(...)`, no `__main__`).
- **Instrumentation** (augment "as I see fit"; nothing committed to gacalc):
  - **op-mix counter** — env-gated (`GACALC_PROFILE=1`) monkeypatch shim that wraps
    the `Vector2/Vector3/G2/G3`(+graded) dunders and tallies calls **by operand-type
    pair** (same-type add/sub, scalar mul, `scalar_product`, `magnitude`/`normalize`,
    rotor sandwich). Dict-increment (framerate-independent) → dumped per run. PRIMARY
    signal (software GL dominates wall-clock, so counts beat timing).
  - **py-spy** sampling → per-run flamegraph (secondary; shows gacalc's share of
    Python time). Temporary image add.
- **Custom gacalc**: build a local wheel (`make dist`, bakes generated `g*.py`) and
  install it over the PyPI `gacalc>=0.0.9` in the mvp image (temporary override).
- **Collect**: each run dumps op-mix + flamegraph to a host-mounted `profiles/` dir.
  Bill plays + exits each; I aggregate.

## Constraints / environment (verified 2026-07-18)

- Nested podman OK; every inner run needs `--cgroups=disabled` (standing arrangement).
- **No `/dev/dri` → software GL only (Mesa llvmpipe).** `_smoketest.py` already renders
  offscreen via EGL pbuffer on llvmpipe, so windowed llvmpipe should work. Wall-clock
  is GL-bound → rely on the op-mix COUNTER, not sampling, for the frequency table.
- Display passthrough available (`DISPLAY=:0`, `wayland-0` socket); mirror mvp's
  `shell` target flags (`USE_X` + `WAYLAND_FLAGS_FOR_CONTAINER`, incl.
  `PYGLFW_LIBRARY=/usr/lib64/libglfw.so.3`).
- mvp image built trimmed for speed: `BUILD_DOCS=0 USE_EMACS=0 USE_JUPYTER=0
  USE_SPYDER=0 USE_X_WINDOWS=1` (profiling can't touch docs/emacs/jupyter paths).
- Temporary build-file additions (local-gacalc override, py-spy) per Bill's standing
  dev-tool arrangement — reverted when the task closes.

## Progress log

- 2026-07-18: investigated launch mechanics; built trimmed mvp image; boing smoke
  test ✅ (windowed software GL works: **llvmpipe, GL 4.6 Core, Mesa 26.1.4**).
- 2026-07-18: built local **gacalc 0.0.9 wheel** + op-mix `sitecustomize.py` shim;
  validated harness (wheel override + shim + 2 s periodic flush all work).
- **Gotcha (resolved):** automated `PGZERO_MAX_FRAMES` timing probes appeared to run
  at <1 fps, but that was **Wayland frame-callback throttling** for an unfocused
  surface, NOT slow rendering. With the window focused (Bill playing), it's smooth.
  So the interactive plan stands; ignore headless-timing fps numbers.
- **Clean-exit note:** the shim's SIGTERM handler doesn't always win the race under
  a C GL call (`podman stop` → SIGKILL / exit 137), but the **2 s periodic flush is
  the backstop** — every run's data is captured up to the last ~2 s regardless.

## Results (op-mix per workload)

Raw JSON in scratchpad `prof/out/<label>.json`. Counts include internal delegation
(e.g. one `magnitude()` → `magnitude_squared` → `scalar_product` → `reverse` +
`__mul__`), which is intentional — it shows the real dispatch load.

### soccer (vol1, 2D `Vector2`) — 37.5 s play, **3,890,825 calls**
| method | calls | note |
| --- | ---: | --- |
| `__mul__` | 803,535 | Vector2×Vector2 **560k**; scalar: float 172k / **sympy Float 63k** / int 7k |
| `scalar_product(Vector2)` | 560,176 | == the Vector2×Vector2 muls (it *is* the geom product) |
| `magnitude` | 537,244 | inherited base method → to/from_blade_dict round-trip |
| `magnitude_squared` | 537,244 | same |
| `reverse` | 537,244 | driven by magnitude chain |
| `__sub__(Vector2)` | 379,221 | same-type |
| `__add__(Vector2)` | 188,491 | same-type |
| `__iter__` | 153,448 | coords for rendering |
| `normalize` / `__abs__` | 96,133 / 96,133 | |

**Reads:** confirms **candidate #4** (closed-form `magnitude`/`magnitude_squared`/
`normalize` — the biggest single lever; the magnitude chain alone is ~1.7M of 3.9M
calls) and **candidate #1** (same-type exact-type early-out — `Vector2×Vector2`,
`+`, `-` all dominant). The **63k sympy-`Float` muls** are the numeric-preservation
leak (task's "Related" note). `int`-scalar mul is rare here (7k) vs `float` (172k).

### kinetix (vol2, 2D) — 82 s play, **102,809 calls** (render-bound, ~80× lighter than soccer)
| method | calls | note |
| --- | ---: | --- |
| `__iter__` | 92,842 | **90%** — `list(vector)` coord conversion for rendering sprites |
| `__add__(Vector2)` | 9,112 | movement |
| `__mul__` | 172 | tiny |
| `magnitude`/`_squared`/`scalar_product`/`reverse` | 56–136 | tiny |
| `Rotor2.sandwich` | 9 | the `_turn` rotation |
| `__mul__(One)` | 1 | **sympy exact `One` leaking** → numeric-preservation issue in `_turn` |

**Reads:** a *render-bound* consumer — dominated by `__iter__` (coord conversion),
almost no physics math. Confirms a **fast/cheap `__iter__`** (or fewer `list()`
conversions at the render boundary) matters for sprite-heavy games. Also the first
sighting of the **rotor sympy-leak** (`Rotor2.sandwich` + `__mul__(One)`) the task
predicted for `_turn`. Contrast with soccer (math-bound) — the two stress different
paths, so fast-path priorities must cover both.

### avenger (vol2, 2D) — 82 s play, **479,612 calls** (mixed)
| method | calls |
| --- | ---: |
| `__iter__` | 174,801 |
| `__mul__` | 62,419 |
| `magnitude_squared`/`reverse`/`scalar_product` | 39,895 ea |
| `magnitude` | 39,846 |
| `__add__` / `__sub__` | 33,641 / 26,696 |
| `normalize` / `__abs__` | 11,262 ea |

**Reads:** the middle ground — meaningful `__iter__` (render) **and** magnitude chain
(enemy-swarm movement/AI).

### mvpviz_perspective (3D `Vector3`/`Bivector3`/`Rotor3`) — 133 s, **730,357 calls**
| method | calls | note |
| --- | ---: | --- |
| `Rotor3.sandwich` | 201,072 | **the 3D rotation path — #1 op** |
| `Vector3.__add__` | 137,808 | same-type |
| `Vector3.__sub__` | 109,568 | same-type |
| `Bivector3.__add__` | 100,556 | rotor build / plane rotation |
| `Bivector3.__mul__` | 50,284 | rotor build |
| `Rotor3.reverse` | 49,696 | inside sandwich |
| `Vector3.__neg__` / `__mul__` | 40,671 / 40,664 | |
| `Vector3.magnitude`/`normalize`/`outer_product` | 3–6 | **~absent** (opposite of soccer) |

**Reads:** 3D is **rotor-and-arithmetic-bound** (`Rotor3.sandwich`+`reverse` ≈ 250k;
`Bivector3` add/mul ≈ 150k; `Vector3` same-type add/sub/neg/mul ≈ 328k). The
magnitude chain that dominates soccer is negligible here. `Rotor3.sandwich` already
has a generated closed form — good — but at 200k calls it must stay fast.

## Cross-cutting synthesis (4 workloads)

Universal, both 2D and 3D:
- **Same-type binary ops dominate everywhere** (`Vector*×Vector*`, `+`, `-`, `neg`)
  → **candidate #1 (exact-type early-out before the `match` ladder)** is the
  broadest win; helps every workload.
2D-specific (CtC):
- **The magnitude chain** (`magnitude`→`magnitude_squared`→`scalar_product`→`reverse`
  +`__mul__`) is soccer's #1 cost and big in avenger → **candidate #4 (closed-form
  `magnitude`/`magnitude_squared`/`normalize` on graded types)**.
- **`__iter__`** (coord conversion for rendering) is huge in kinetix/avenger →
  a cheap/fast `__iter__` (or fewer `list()` conversions at the render boundary).
- **sympy leak**: `__mul__(Float)` 63k in soccer, `__mul__(One)` in kinetix →
  numeric-preservation (task's "Related" note; `_turn`/`plane_rotation`).
3D-specific (demos/mvpViz):
- **`Rotor3.sandwich`/`reverse` + `Bivector3` add/mul** are the hot paths →
  keep sandwich's closed form fast; consider Bivector3 fast paths.
- Scalar-mul on `Vector3`/`Bivector3` matters (candidate #3 direct field arithmetic).

Priority read: **#1 (same-type early-out)** helps all; **#4 (closed-form magnitude)**
is the biggest 2D lever; **Rotor3.sandwich/Bivector3** are the 3D levers; the
**sympy-leak** is a correctness-flavored perf fix wanted pre-tag.

- **Next:** optional — one numbered book `demo` + another mvpViz (cayley/coordinate
  systems) for breadth; then finalize the fast-path plan into
  `generated-dispatch-fast-paths.md`.

## Open questions

- Exact workload set to sweep (all CtC + all mvpViz + which demos?) — defaulting to
  all CtC + all mvpViz + a hot demo subset unless Bill says every `demoNN`.
- py-spy worth it under software GL, or op-mix counter + a focused headless
  update-loop micro-benchmark only?
