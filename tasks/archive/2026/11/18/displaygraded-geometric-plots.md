# Add matplotlib plots to displaygraded.py — show the geometry, not just the values

**Completed:** 2026-11-18 (William Emerison Six <billsix@gmail.com>; authorized batch
`ready-tasks-batch-2026-11-18`)
**Priority:** 5
**Difficulty:** 4
**Started:** 2026-06-06

## Outcome

`notebooks/displaygraded.py` printed each result's type and value but never drew the geometry.
It now has a plot cell after each key result:

1. the vector `a` as an arrow;
2. scalar times vector (new, from the 2026-08-27 bullet): `b`, `2 * b` and `-1 * b`;
3. `a ∧ b` as the oriented parallelogram, with the arc from `a` toward `b`;
4. the quarter-turn versor carrying `e_1` to `e_2`, with the turn's arc;
5. `plane_of_rotation()` as the oriented unit square `e_12`;
6. the un-normalized sandwich: `w`, `R * w * R̃` (stretched by `|R|² = 2`) and `R * w * R⁻¹`. The
   Markdown cell says this last arrow is the one `projection_rotation` gives, as the `==` cell shows;
7. 3D: `u`, `v`, the patch `u ∧ v` and its dual, the normal `u × v`.

The helpers are in `src/gacalc/nbplotutils.py`:
- `draw_vectors([(vector, label, colour), ...])`
- `draw_bivector(a, b, label, color)`
- `draw_angle(from_vector, to_vector, color, radius)`
- `create_graphs_3d(bound, title, elevation, azimuth)`

The `draw_*` helpers draw into the axes of the enclosing block and dispatch on it with a `match`:
2-D inside `create_graphs`, 3-D (`Axes3D`) inside `create_graphs_3d`. `draw_angle` sweeps the arc in
the plane of the two vectors, from the first toward the second, so one function shows orientation in
either dimension.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-18)

1. Helpers in `nbplotutils.py`, not inline, so `displayg2`/`displaymv` can reuse them.
2. The 3D 𝒢₃ plot is in scope now.
3. Scalar·vector is a standalone plot; `show_mult` stays a values table.
4. Bivector rendering: a shaded parallelogram plus an orientation arc (left to implementation).

## Judgment calls

- **3D camera.** Matplotlib's default camera (elevation 30°, azimuth −60°) happens to look almost
  straight down `u × v` = (−3, 6, −3), so the normal collapsed to a dot. The notebook passes
  `elevation=20, azimuth=0`, which shows the plane at a slant and the normal side-on.
  `create_graphs_3d` keeps matplotlib's defaults.
- **Labels.** Labels follow the vector-notation rule (`\vec{\mathbf{a}}`, `\mathbf{e}_{12}`), which
  matplotlib's mathtext renders. Labels too long for a small figure were shortened, and the
  Markdown says the rest.

## Verification

- The notebook ran headless (Agg backend, `RuntimeWarning` as error) with all 7 figures saved and
  looked at.
- ruff, `ty check` on the module and notebook, and the nbplotutils doctests/tests passed.
- `tools/check_annotations.py` reports one new row, the `LabelledVector` type alias, which is a
  classified-out kind.
