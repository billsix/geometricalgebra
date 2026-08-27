# Add matplotlib plots to displaygraded.py — show the geometry, not just the values

**Status:** proposed — needs go-ahead
**Priority:** 5
**Difficulty:** 4
**Started:** 2026-06-06

## Goal

`displaygraded.py` now prints each result cleanly (the `show()` helper renders `Type: <latex>`, and the
two table cells render as a Math list / Markdown table). But the *geometric meaning* is still only
implied by coefficients. Add **matplotlib plots** alongside the key cells so a reader can see what each
operation does to vectors/planes — arrows for vectors, an oriented area for a bivector, before/after
arrows for a rotation, etc.

## Why

This is a geometric-algebra teaching notebook; the payoff is *geometric intuition*. A rotor that turns
`e_1 → e_2`, a wedge that sweeps an oriented parallelogram, the dual of a plane that points along its
normal — these land far harder as pictures than as blade-dicts. The repo already has plotting
infrastructure in `nbplotutils.py` (`create_graphs`, `create_basis`, `draw_*`, `plot_multivector`) and
`displayg2.py` / `displaymv.py` already draw graph-paper transforms, so there's a pattern to build on.

## Concepts to visualize (2D, 𝒢₂ — the bulk of the notebook)

1. **A vector** (`a = 3 e_1 + 4 e_2`): an arrow from the origin.
2. **Two vectors + their wedge** (`a`, `b`, `a ^ b`): the two arrows plus the **oriented parallelogram**
   they span (the bivector = signed area), with an arc/arrow showing orientation. Tie it to
   `a * b = a·b + a∧b` (the dot = projection length, the wedge = area).
3. **A rotor rotating a vector** (`quarter * e_1 * quarter.reverse()`): `e_1` and its rotated image
   (a quarter turn), with the swept arc.
4. **The un-normalized rotor sandwich** (the cell that compares `R w R̃` vs `R w R⁻¹` vs `rotate(w)`):
   overlay `w = e_1`, the **scaled** result `R w R̃ = 2 e_2` (a longer arrow), the **pure** result
   `R w R⁻¹ = e_2`, and `rotate(w) = e_2`. The picture *is* the lesson: the bare sandwich scales,
   `R⁻¹` divides it out, and the pure result coincides with `rotate`. **Highest-value plot.**
5. **`plane_of_rotation()`**: the e_1 e_2 plane shown as the shaded oriented unit area.

## Concepts to visualize (3D, 𝒢₃ — optional, harder)

6. **`u`, `v`, `biv = u ^ v`, `biv.dual()`**: 3D arrows for `u`/`v`, the spanned plane patch for the
   bivector, and the dual as the **normal vector** — the geometric-algebra cross product. Needs
   `mpl_toolkits.mplot3d`. Scope decision below.

## Approach / building blocks

- A small `draw_vectors(ax, *(vec, label, color), ...)` (arrows via `ax.annotate`/`quiver`) and a
  `draw_bivector(ax, a, b)` (a shaded parallelogram + orientation arc) — either added to
  `nbplotutils.py` (reusable, but that module is matplotlib-heavy and excluded from the test suite) or
  kept **inline** in the notebook (simpler, self-contained). Decide in the plan.
- Pull components out of a `G2`/`Vector2` via `to_blade_dict()` (e.g. `d.get((1,), 0)`, `d.get((2,), 0)`),
  cast to `float`. (Symbolic values like the `quarter` rotor's `cos/sin(pi/4)` need `float(...)`.)
- Reuse `create_graphs` for axes/grid if it fits; otherwise a plain `plt.subplots` with equal aspect.

## Plan (once approved)

- [ ] Decide: helpers in `nbplotutils.py` vs inline in the notebook; and 2D-only vs include the 3D §.
- [ ] Add `draw_vectors` / `draw_bivector` (wherever decided).
- [ ] Insert a plot cell after each concept above (1–5, and 6 if in scope), each as its own `# %%`
      cell right after the value it illustrates.
- [ ] Headless-verify rendering: run the figures under the `Agg` backend (no GUI) to confirm no
      exceptions and sane extents; the actual SVG is only seen in Jupyter.
- [ ] `entrypoint/format.sh` clean (ruff + ty). Notebooks aren't run by the suite, so no test delta;
      confirm the suite stays green anyway.

## Notes / considerations

- Notebook-/plotting-only; **no library change** expected (just reading `to_blade_dict()` / fields).
- Keep each plot small and captioned by the markdown cell above it; the plot *complements* the
  `show()` output, it doesn't replace it.
- `warnings.filterwarnings("error", category=RuntimeWarning)` is set at the top of the sibling
  notebooks — watch for matplotlib RuntimeWarnings becoming errors.

## Open questions

- **Helpers in `nbplotutils.py` or inline?** Inline keeps it self-contained and avoids touching the
  GUI-backend module; a shared helper pays off if `displayg2`/`displaymv` would reuse it. Lean inline
  unless reuse is obvious.
- **Include the 3D 𝒢₃ plots (concept 6)?** They're the most striking (dual = cross product) but need
  `mplot3d` and more fiddling. Could be a fast-follow.
- **Bivector rendering:** parallelogram + orientation arc (concrete, ties to "signed area") vs a
  simpler arc-only glyph. Pick during implementation.

## Folded-in ideas (2026-08-27, William Emerison Six <billsix@gmail.com>) — two batch-triage bullets map here

Two maintainer bullets were triaged into this task because it already owns the notebook plotting:

- **Bullet: *"Matplotlib print vectors 2d and 3d, put in the notebooks."*** — this is concept 1 (2D
  vector arrows) plus the 3D vector case. **The 3D half is genuinely new infrastructure** — all current
  plotting (`src/gacalc/nbplotutils.py`: `plot_multivector:495`, `create_graphs:143`, `_to_xy:68`) is
  **2D only**; there is no 3D helper yet (concept 6 above already flagged `mplot3d`). See the existing
  "include the 3D plots?" open question — this bullet raises its priority.
- **Bullet: *"2D Plot things like scalar vector multiplication. Plot things like vector vector
  multiplication."*** — vector·vector is already covered (concept 2: `a*b = a·b + a∧b`, dot = projection
  length, wedge = parallelogram area). **Scalar·vector scaling is the net-new add** (an arrow and its
  scaled image). `nbplotutils.show_mult` (`src/gacalc/nbplotutils.py:615`) already renders a
  multiplication *table* (values, not geometry) — decide whether to add a geometry panel there or keep
  these as standalone plots (Q below).

**New open questions (block these additions):**
- **Is 3D plotting in scope now** (this bullet asks for it explicitly), or still deferred as the
  "fast-follow" the 3D §/concept-6 question already contemplates? 3D may motivate
  `epix-plot-integration.md`.
- **Scalar·vector** — extend `show_mult` with a geometry panel, or a standalone scaling plot?
