# Port the remaining 2D cells from displaymv.py into displayg2.py

**Created:** 2026-06-04 · **Completed:** 2026-06-05 (Tiers 1 and 2 implemented 2026-06-04)

Once the transform layer became representation-preserving
(`tasks/archive/2026/06/05/investigate-how-to-extract-translate-etc.md`), the remaining 2D content
of `notebooks/displaymv.py` was ported into `notebooks/displayg2.py` as genuine `G2` demos. This
also covered that task's split-out "demo the 2D rotate / n-D scale in the G2 notebook" item.
Inherently >2D content stayed in `displaymv.py`: `sym_vec3_*`, projection onto the `e_2*e_3` /
`e_1*e_3` planes, `dual(3)`, the 8-/9-dimensional symbolic cells, anything using `e_3`/`e_4`.

## Tier 1 — portable as-is (done 2026-06-04)

- New "Applied example", "Transforms" and "Applying transforms to a `G2` vector" sections, with
  imports of `sympy` and `compose`/`inverse`/`rotate`/`scale_non_uniform`/`translate` from
  `geometricalgebra.transforms`.
- The transform-construction display cells (`translate`, `scale_non_uniform`, `rotate(pi/2)`,
  `compose`, `inverse`) built from the `g2` basis constants; the 3D `… + 7*e_3` variants skipped.
- The molarity example `gram_fe_to_mol_fe`, retyped to `G2` (kept as a small applied example).
- Apply-to-a-vector demos: `rotate(pi/2)(w)` → −4e₁+3e₂, `scale_non_uniform(2,3)(w)` → 6e₁+12e₂,
  `compose([rotate, translate])(w)`, a `type(...).__name__` cell showing the result is a `G2`, and an
  `inverse(fn)(fn(w)) == w` round-trip.

## Tier 2 — graph-paper plots (done 2026-06-04)

The graph-paper helpers built their sample points from the module-level `Gn` constants, so a
`G2`-built function ran but nothing stayed `G2`. The rendered plots are identical either way, so the
payoff was consistency (a truly `G2`-only notebook), not new visible behavior; Tier 2 was done
anyway.

- **Decision:** parameterize the helpers by an optional `cls: type[AbstractMultiVector] =
  MultiVector` keyword (defaulting to `Gn`, so `displaymv.py` is unchanged), rather than explicit
  basis vectors or reading the type off the passed function's output.
- `nbplotutils.py`: `generategridlines`, `create_basis`, `create_x_and_y`, `create_unit_circle`,
  `draw_isoceles_triangle`, `draw_right_triangle`, `draw_second_right_triangle`, `draw_ndc`,
  `draw_screen` derive `e_1`/`e_2`/`zero` from `cls.basis_vector(i)` / `cls.zero()`; the unused
  `e_1`/`e_2`/`zero` imports were removed.
- `displayg2.py`: a new "Graph paper" section (graph paper, relative graph paper + right triangles,
  composed-function graph paper, and the bottom-up / top-down `compose_intermediate_fns`
  isoceles-triangle walks), all driven with `cls=G2`.

## Verification

`displaymv.py` (the `Gn` default) and `displayg2.py` both execute end to end under `MPLBACKEND=Agg`
(exit 0), with values checked; ruff clean on all source and the new notebook content (the only ruff
residue was pre-existing in `displaymv.py`), `ruff format` stable; `ty check src` and `ty check
tests` clean; 118 tests pass.
