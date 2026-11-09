# Convert an InvertibleFunction to its matrix

**Completed:** 2026-06-08

## What landed

`to_matrix(fn, cls, n=None, *, backend="numpy")` in `transforms.py`: always a homogeneous
(n+1)×(n+1) matrix built by probing the basis and the origin; a linear map gets a zero translation
column; translation sits in the last column (matching mvp's `pyMatrixStack`); `backend="numpy"`
(float32, the default) or `backend="sympy"` (exact, symbolic for a symbolic `fn`); raises on
NONLINEAR; `Gn` needs an explicit `n`, while `G1/G2/G3` take it from `DIMENSION`. Tests in
`tests/test_transforms.py`; `ty`/`ruff` clean, suite passed (200 tests).

mvp consumed it: `mathutils` imports `to_matrix` and `test_mathutils` ties `rotate_z` to it, confirmed
working on 2026-06-08. The formal PyPI wheel release was left to the maintainer as a separate
out-of-container step.

## Why

mvp kept its matrix forms hand-written in parallel: `pyMatrixStack.py` had its own
`rotate_x/y/z`, `translate`, `scale`, `ortho`, `perspective`, each filling an `np.matrix` by hand,
separate from the `InvertibleFunction` factories in `mathutils.py`. Deriving the matrix from the
function makes it provably the same transform. gacalc suited it: probing is exact, a `sympy.Matrix`
backend gives a literal symbolic matrix (a symbolic `rotate_z(θ)` yields `[[cos(θ), −sin(θ), 0], …]`),
and probing doubles as a cheap correctness check of a factory.

## Decisions

- **Always homogeneous (decided 2026-06-07, after checking mvp's `pyMatrixStack.py`).** In graphics
  every matrix is 4×4 (`pyMatrixStack` stores 4×4 `float32` throughout; pure-linear `rotate_x`/`scale`
  are 4×4 with a zero translation column), so size is not chosen by linearity. One extraction:

  ```
  column i (i<n)  = f(e_i) − f(0)     # linear part
  last column     = f(0)              # translation; zero automatically when f is linear
  last row        = (0, …, 0, 1)
  ```

- **Non-linear raises `ValueError`.** The affine extraction cannot recover a projective last row
  (verified: `pyMatrixStack.perspective` has last row `[0,0,-1,0]`, the w-divide, which an R³→R³ probe
  assuming w=1 misses). The projective 4×4 is supplied directly on the mvp side; a recognized-perspective
  special case was deferred.
- **The linearity tag is a guard, not a size selector** — it comes from
  `tasks/archive/2026/06/08/classify-functions-linear-affine-nonlinear.md`.
- **Both backends,** numpy float32 by default, sympy optional; same probing, different assembly.
- **Convention:** row-major, translation in the last column, column-vector premultiply, matching
  `pyMatrixStack`.
- A bare non-homogeneous n×n (`homogeneous=False`) was not added; it was left for a real need.

The tests cover `translate(b)` (identity plus `b` in the last column), `uniform_scale(m)`
(`diag(m,m,m,1)`), a linear map with a zero translation column, `compose([f,g])` equal to
`to_matrix(f) @ to_matrix(g)`, `inverse(f)` as the matrix inverse, and NONLINEAR raising.
