# G2 and G3 demo notebooks (mirroring displaymv.py)

**Status:** complete — user ran the notebook (2026-06-05) and confirmed it looks good
**Completed:** 2026-06-05
**Started:** 2026-06-04

## Goal

Create **two** new jupytext (percent-format) demo notebooks under `notebooks/` — one for the
**specialized `G2` class** (𝒢₂) and one for **`G3`** (𝒢₃) — that showcase the specialized classes
the way `notebooks/displaymv.py` showcases the general `MultiVector`/`Gn`. Each notebook reproduces
as much of `displaymv.py` as is meaningful in its dimension — basic products, dot/wedge, symbolic
vectors, `r_vector_part`, duals, and (where applicable) the `InvertibleFunction` transforms and the
`nbplotutils` plots — but built on `G2`/`G3` and their own basis constants (e.g.
`from geometricalgebra.g2 import G2, e_1, e_2`) rather than the general representation. The G3
notebook additionally covers the 3D-specific cells from `displaymv.py` (3D vectors, bivector duals,
trivector/pseudoscalar). First study `displaymv.py` to decide what carries over to each dimension,
what is inherently general-only, and how the shared helpers interact with specialized values.

## Plan

- [x] Study `displaymv.py` cell-by-cell; classify each cell as 2D-applicable / 3D-applicable / general-only.
- [x] Check what `g2.py`/`g3.py` export and which `AbstractMultiVector` methods `G2`/`G3` support.
      → Both inherit the full ABC API and have `symbolic_multivector` (defaulting `n` to `DIMENSION`).
- [x] Decide how to handle `coefficient_of_blade`-reading helpers and the `gn.py` transforms.
      → Adapted `plot_multivector`/`show_mult` in `nbplotutils.py` to the ABC (`to_blade_dict()`,
        and `show_mult` now builds each row product as `left * right` instead of `math.prod(...,
        start=one)` so it stays in the concrete type). Omitted the `Gn`-bound transform/graph-paper
        cells from the specialized notebooks.
- [x] Draft `notebooks/displayg2.py` — 2D cells ported to `G2`.
- [x] Draft `notebooks/displayg3.py` — 3D cells ported to `G3` (incl. trivector, bivector duals).
- [x] Verify both notebooks run end to end (executed as scripts under `MPLBACKEND=Agg`, exit 0),
      ruff-clean, and the full suite (118 tests) + `ty check src` stay green.

**Status: implementation complete — pending user review.** Files created: `notebooks/displayg2.py`,
`notebooks/displayg3.py`. File changed: `src/geometricalgebra/nbplotutils.py` (helpers broadened to
the ABC; dropped now-unused `one` import).

## Notes / decisions

- `displaymv.py` is 497 lines, percent-format, kernel `geometricalgebra`. GPL header at top.
- Mixing a specialized value with a `Gn` value coerces to `Gn` (per CLAUDE.md) — relevant where the
  shared transform/plot helpers are written against `MultiVector`.
- **Constraint found:** `plot_multivector` and `show_mult` in `nbplotutils.py` access
  `mv.coefficient_of_blade` (a `Gn`-only dict attribute); `G2`/`G3` expose `to_blade_dict()` instead,
  so these helpers don't work on specialized values without adaptation/coercion.
- **Constraint found:** the `InvertibleFunction` transforms (`translate`/`rotate`/
  `scale_non_uniform_2d`/`compose`) and all `nbplotutils` graph-paper helpers are written against
  `MultiVector`/`Gn`; feeding them a `G2` coerces results to `Gn`.

## Decisions (settled 2026-06-04)

1. **Gn-only helpers → adapt to the ABC.** Make `plot_multivector`/`show_mult` (and any other
   `coefficient_of_blade`-reading helper) work on any `AbstractMultiVector` via `to_blade_dict()`,
   so they accept `G2`/`G3`/`Gn`. This is a small `nbplotutils.py` source change separate from the
   notebooks.
2. **Specialized-only character.** The notebooks show `G2`/`G3` doing the algebra on their own
   (products, dot/wedge, `r_vector_part`, duals, inverse, …). No side-by-side `Gn` contrast.
3. **Symbolic demos: prefer a specialized constructor if `G2`/`G3` provide one;** otherwise build
   symbolic values by hand from `sympy.symbols` per field. (Need to check whether one exists.)
4. **Filenames:** `notebooks/displayg2.py` and `notebooks/displayg3.py` (mirror `displaymv.py`).

## Open questions

- Does `G2`/`G3` expose a symbolic-multivector constructor, or only `Gn.symbolic_multivector`?
  (Decides decision 3's branch.)
- Do the `gn.py` transforms make sense to show at all in a *specialized-only* notebook given they
  return `Gn`? Leaning: omit the transform/graph-paper cells from the specialized notebooks (they're
  well covered in `displaymv.py`), unless you want them.

## Notes (transforms — answered 2026-06-04)

The `gn.py` `translate`/`rotate`/`scale_non_uniform_2d`/`compose` factories are **bound to the
general `Gn`**: they close over the module-level `Gn` basis constants (`scale_non_uniform_2d` uses
`MultiVector.project(onto=e_1)`, `rotate` builds `e_1*e_2` from the `Gn` `e_*`), and feeding a `G2`
in coerces the result back to `Gn`. So they don't fit a specialized-only notebook. The ABC, however,
has a representation-preserving `rotate` *classmethod* (`base.py:511`, returns a `MultiVectorFn`)
that keeps the `G2`/`G3` type — usable if a rotation demo is wanted. **Plan:** omit the
`gn.py` transform + graph-paper cells from the specialized notebooks; optionally show `G2.rotate`/
`G3.rotate` (the classmethod) instead.
