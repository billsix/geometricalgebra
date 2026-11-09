# G2 and G3 demo notebooks (mirroring displaymv.py)

**Created:** 2026-06-04 · **Completed:** 2026-06-05

Two jupytext (percent-format) demo notebooks, `notebooks/displayg2.py` and `notebooks/displayg3.py`,
were created to show the specialized `G2` (𝒢₂) and `G3` (𝒢₃) classes the way
`notebooks/displaymv.py` (497 lines) shows the general `Gn`: basic products, dot/wedge, symbolic
values, `r_vector_part`, duals, inverse, plots, and in `G3` the 3D cells (3D vectors, bivector
duals, the trivector/pseudoscalar). The maintainer ran them on 2026-06-05 and confirmed they looked
good.

## Decisions (2026-06-04)

1. **`Gn`-only helpers were adapted to the ABC.** `plot_multivector` and `show_mult` in
   `src/geometricalgebra/nbplotutils.py` read `mv.coefficient_of_blade` (a `Gn`-only attribute);
   they now use `to_blade_dict()`, and `show_mult` builds each row product as `left * right` instead
   of `math.prod(..., start=one)` so it stays in the concrete type (the unused `one` import went).
2. **Specialized-only character:** the notebooks show `G2`/`G3` on their own, with no side-by-side
   `Gn` contrast.
3. **Symbolic values** use the specialized `symbolic_multivector`: `G2`/`G3` inherit the full ABC
   API and their `symbolic_multivector` defaults `n` to `DIMENSION`, so no hand-built
   `sympy.symbols` per field were needed.
4. **Filenames** mirror `displaymv.py`.
5. **The `gn.py` transform and graph-paper cells were omitted.** `translate`/`rotate`/
   `scale_non_uniform_2d`/`compose` close over the `Gn` basis constants (e.g.
   `MultiVector.project(onto=e_1)`), so a `G2` input coerces back to `Gn`; they did not fit a
   specialized-only notebook and are covered in `displaymv.py`. The ABC's type-preserving `rotate`
   classmethod was the option for a rotation demo.

## Verification

Both notebooks ran end to end as scripts under `MPLBACKEND=Agg` (exit 0) and were ruff-clean; the
full suite (118 tests) and `ty check src` stayed green.
