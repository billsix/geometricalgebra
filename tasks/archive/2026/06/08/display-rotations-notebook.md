# Notebook: rotations two ways (rotor sandwich vs projection)

**Status:** complete
**Completed:** 2026-06-08

## What was done

- Added **`notebooks/displayrotations.py`** (jupytext percent format). It shows,
  for a symbolic vector and symbolic angle θ, that the two formulations of a
  rotation agree in 𝒢₂ and 𝒢₃:
  - the **rotor sandwich** `R v R⁻¹` (via `Gn`), and
  - the **projection formula** `Gn.rotate(from, to)`,
  - proving equality: `sandwich − projection` renders as the **zero**
    multivector in both dimensions. A `simplified()` helper
    (`expand_trig` + `simplify`) renders the clean `v1·cosθ − v2·sinθ` form;
    the 3D case visibly leaves `e_3` (perpendicular to the plane) untouched.
- Added a **`show_mult` breakdown** of the sandwich as two products
  (`show_mult(R, v)` then `show_mult(R·v, R⁻¹)`), the same intermediate-product
  layout used for associativity — highlighting that `R·v` carries a trivector
  (grades [1,3]) that **cancels** in the second product (grades → [1]), i.e. why
  a rotor sandwich of a vector is always a vector.
- **Fixed `src/gacalc/nbplotutils.py` to import headless:** `set_matplotlib_formats("svg")`
  ran at module load and raised without an IPython shell; it's now guarded by
  `if get_ipython() is not None:`. The module (and `show_mult`) now import under
  a plain script / pytest, while still configuring the inline SVG backend in
  Jupyter. ty + ruff clean.

## Follow-up (optional, not done)

`pytest.ini` still `--ignore`s `src/gacalc/nbplotutils.py` (added when it
couldn't import headless). Now that it can, that ignore could be removed so the
module is collected — left for later to avoid surfacing unrelated matplotlib
warnings-as-errors in the headless suite.
