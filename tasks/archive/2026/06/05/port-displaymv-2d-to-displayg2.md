# Port the remaining 2D cells from displaymv.py into displayg2.py

**Status:** complete
**Completed:** 2026-06-05
**Started:** 2026-06-04 · **Tier 1 + Tier 2 implemented:** 2026-06-04

## Goal

Now that the transform layer is representation-preserving (`G2` in → `G2` out), more of
`displaymv.py`'s 2D content can move into `notebooks/displayg2.py` as genuine `G2` demos — chiefly
the `InvertibleFunction` transform cells (`translate`/`scale`/`rotate`/`compose`) and the matplotlib
graph-paper visualizations. This task plans that port. It **subsumes** the leftover "notebook demo of
the now-working 2D rotate / n-D scale in displayg2" TODO from
`tasks/investigate-how-to-extract-translate-etc.md` (that demo is Tier 1 below).

## What's in displaymv.py but NOT yet in displayg2.py (2D-relevant)

Classified by how hard it is to port to real `G2`:

### Tier 1 — trivially portable now (genuinely `G2`, no library changes)
These use only `G2` values + the (now type-preserving) transforms; they display latex / numbers.
- The molarity worked example `gram_fe_to_mol_fe` (uses `e_1`, `e_2`, `.inverse()`) — a nice applied
  2D example.
- Transform-construction display cells (build from `g2.e_1`/`g2.e_2`, render `_repr_latex_`):
  `translate(5*e_1)`, `scale_non_uniform_2d(5,6)`, `inverse(translate(5*e_1))`,
  `translate(5*e_1 + 6*e_2)`, `rotate(pi/2)`, `compose([rotate(pi/2), translate(5*e_1+6*e_2)])`,
  `inverse(compose([...]))`. (Skip the 3D `… + 7*e_3` variants.)
- **NEW demo (covers the other task's TODO): apply transforms to a concrete `G2` vector and show the
  `G2` result** — e.g. `rotate(pi/2)(3*e_1+4*e_2)`, `scale_non_uniform(2,3)(v)`,
  `compose([rotate, translate])(v)` — asserting/displaying the output is a `G2`. This is the part
  that actually exercises the new representation-preserving behavior.

### Tier 2 — needs `nbplotutils` graph-paper helpers generalized first
The matplotlib graph-paper plots: the `with create_graphs() …` blocks ("Draw graph paper", the two
"relative graph paper" blocks, "composed functions" graph paper) and the `compose_intermediate_fns`
bottom-up / top-down visualizations, plus `draw_right_triangle` / `draw_second_right_triangle` /
`draw_isoceles_triangle`.

**Blocker:** `create_basis`, `create_x_and_y`, `create_unit_circle`, `generategridlines`, and the
`draw_*_triangle` helpers build their sample points from the **module-level `Gn`** constants
(`e_1`, `e_2`, `zero`) and read coordinates via `.component(e_1)`. Passing a `G2`-built `fn` *runs*
(it just coerces internally), but nothing stays `G2`. To make these plots genuinely `G2` we must
parameterize the helpers by representation — the same generalization already applied to
`plot_multivector` / `show_mult`.

**Honest caveat:** these graph-paper plots visualize *coordinate transforms*; the rendered image is
identical whether sampled in `Gn` or `G2`. So Tier 2's payoff is **consistency/purity** (a truly
`G2`-only notebook), not new visible behavior. That's the decision to make before doing the work.

### Out of scope (inherently >2D — stays in displaymv.py)
`sym_vec3_*`, projection onto `e_2*e_3`/`e_1*e_3` planes, `dual(3)`, the 8-/9-dimensional symbolic
cells, anything using `e_3`/`e_4`.

## Plan

### Tier 1 (DONE — 2026-06-04)
- [x] Added an "Applied example" + "Transforms" + "Applying transforms to a `G2` vector" set of
      sections to `displayg2.py`; extended imports (`sympy`, and `compose`/`inverse`/`rotate`/
      `scale_non_uniform`/`translate` from `geometricalgebra.transforms`).
- [x] Ported the transform-construction display cells using `g2` basis constants (`translate`,
      `scale_non_uniform`, `rotate(pi/2)`, `compose`, `inverse`).
- [x] Added the molarity `gram_fe_to_mol_fe` example, retyped to `G2`.
- [x] Added apply-to-a-`G2`-vector demos: `rotate(pi/2)(w)` → −4e₁+3e₂, `scale_non_uniform(2,3)(w)`
      → 6e₁+12e₂, `compose([rotate, translate])(w)`, a `type(...).__name__` cell proving the result
      is a `G2`, and an `inverse(fn)(fn(w)) == w` round-trip. **(Satisfies the notebook-demo TODO from
      `tasks/investigate-how-to-extract-translate-etc.md`.)**
- [x] Notebook executes end-to-end (`MPLBACKEND=Agg`, exit 0), ruff-clean, `ruff format` stable;
      values verified correct.

### Tier 2 (DONE — 2026-06-04)
- [x] Generalized the `nbplotutils` graph-paper helpers to take an optional `cls:
      type[AbstractMultiVector] = MultiVector` (defaults to `Gn`, so `displaymv.py` is unchanged):
      `generategridlines`, `create_basis`, `create_x_and_y`, `create_unit_circle`,
      `draw_isoceles_triangle`, `draw_right_triangle`, `draw_second_right_triangle`, `draw_ndc`,
      `draw_screen` — each derives `e_1`/`e_2`/`zero` via `cls.basis_vector(i)` / `cls.zero()` instead
      of the module `Gn` constants. Dropped the now-unused `e_1`/`e_2`/`zero` imports.
- [x] Ported the graph-paper + `compose_intermediate_fns` plot cells into `displayg2.py`, all driving
      the helpers with `cls=G2` (graph paper, relative graph paper + right triangles, composed-fn
      graph paper, and the bottom-up / top-down `compose_intermediate_fns` isoceles-triangle walks).
- [x] Verified: `displaymv.py` (Gn default) regression exit 0; `displayg2.py` exit 0; ruff clean on
      all source + both new-content notebooks; `ty check src` + `ty check tests` clean; 118 tests pass.
      (Only ruff residue is pre-existing junk in `displaymv.py`, untouched.)

### Implementation summary (Tier 2)
- **`nbplotutils.py`:** added `cls` param to the 9 graph-paper helpers; basis now from
  `cls.basis_vector(...)`/`cls.zero()`; removed `e_1`/`e_2`/`zero` imports (kept `MultiVector` as the
  default). `displaymv.py` keeps working via the `Gn` default.
- **`displayg2.py`:** new "Graph paper" section (5 plot cells / loops) + imports for the helpers,
  `compose_intermediate_fns`, and `math`.

## Open questions

- **Do Tier 2 at all?** Given the plots look identical in `Gn` vs `G2`, is the purity worth
  generalizing ~6 helper functions? (Tier 1 alone already showcases `G2` transforms.) My lean: do
  Tier 1 now; treat Tier 2 as optional/later.
- If Tier 2: parameterize helpers by a `cls` argument, by explicit basis vectors, or by reading the
  type off the passed `fn`'s output? (Leaning: an optional `cls`/`basis` kwarg defaulting to `Gn`.)
- Keep the molarity example (it's a cute applied bit) or skip as off-topic for a `G2` showcase?
