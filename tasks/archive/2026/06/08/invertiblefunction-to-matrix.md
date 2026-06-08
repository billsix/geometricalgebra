# Convert an InvertibleFunction to its matrix

**Status:** complete
**Completed:** 2026-06-08
(Code landed in gacalc and **consumed by mvp** — `mathutils` imports `to_matrix`
and `test_mathutils` ties `rotate_z` to it; confirmed working on mvp 2026-06-08.
Only the formal PyPI wheel release remains — Bill's separate, out-of-container step.)

**Landed:** `to_matrix(fn, cls, n=None, *, backend="numpy")` in `transforms.py` —
always homogeneous (n+1)×(n+1) via basis+origin probing; linear ⇒ zero
translation column; translation in the last column (matches `pyMatrixStack`);
`backend="numpy"` (float32, default) / `backend="sympy"` (exact); raises on
NONLINEAR; `Gn` needs explicit `n`. Tests in `tests/test_transforms.py`.
`ty`/`ruff` clean, suite green (200).

## Goal

Given an `InvertibleFunction`, produce the matrix that represents the same
transformation — the linear `n×n` for a linear map, the homogeneous `(n+1)×(n+1)`
for an affine map. This is the bridge between the *function* world and the
*matrix* world that graphics code (and /mvp's `pyMatrixStack.py`) lives in.

In /mvp the matrix forms are currently **hand-written in parallel**:
`pyMatrixStack.py` has its own `rotate_x/y/z`, `translate`, `scale`, `ortho`,
`perspective` that each fill in an `np.matrix` by hand, entirely separate from the
`InvertibleFunction` factories in `mathutils.py`. The point of this task is to
**derive** those matrices from the functions instead of maintaining two
hand-kept copies — so the matrix is provably the same transform as the function.

## How (representation-agnostic, leans on gacalc vectors)

**DECIDED 2026-06-07 (after checking mvp `pyMatrixStack.py`): always emit a
homogeneous `(n+1)×(n+1)` matrix — 4×4 for 3D — even for a linear map.** In
graphics every matrix is 4×4 (mvp's `pyMatrixStack` stores 4×4 `float32`
throughout; `rotate_x`/`scale` are pure-linear yet 4×4 with a zero translation
column). So the matrix *size* is **not** chosen by linearity; it's always
homogeneous. One unified extraction by probing the basis + origin:

```
column i (i<n)  = f(e_i) − f(0)     # linear part (cls.basis_vector(i+1))
last column     = f(0)              # translation; ZERO automatically when f is linear
last row        = (0, …, 0, 1)
```

- **linear** `f(x)=Ax`: `f(0)=0` ⇒ the last column comes out zero on its own —
  exactly the "4×4 with translation set to zero" graphics wants. No special path.
- **affine** `f(x)=Ax+b`: `f(0)=b` lands in the last column. Same formula.
- **non-linear** (e.g. `perspective`): the affine extraction is **wrong** — it
  can't recover the projective last row. (Verified: mvp's `pyMatrixStack.perspective`
  has last row `[0,0,-1,0]`, the w-divide; an R³→R³ probe assumes w=1 and misses
  it.) → **raise `ValueError`.** The projective 4×4 is supplied directly where
  needed (mvp side); a recognized-perspective special-case is deferred.

**The linearity tag is a guard, not a size selector** (depends on
`tasks/classify-functions-linear-affine-nonlinear.md`): LINEAR/AFFINE → the
homogeneous extraction is exact; NON-LINEAR → raise.

## Why gacalc is a good home for it

- Probing is trivial and exact: `f(Vector3.e_1)` etc., and the result can be a
  **`sympy.Matrix`** (gacalc already depends on sympy) — so the matrix is
  symbolic/exact, not just float. A symbolic `rotate_z(θ)` yields the literal
  `[[cosθ, −sinθ, 0], …]` matrix.
- It doubles as a **correctness check**: build the matrix by probing, and compare
  to the closed-form — a cheap test that a factory does what it claims.
- Dimension comes from the value's type (`DIMENSION` on `G1/G2/G3`, or an explicit
  `n` for `Gn`).

## Sketch

- `to_matrix(fn, cls, n=None, *, backend="numpy")`:
  - `backend="numpy"` (default, for mvp/GL) → `np.ndarray` `float32`;
    `backend="sympy"` → `sympy.Matrix` (exact; stays symbolic for a symbolic `fn`).
    Same probing either way — only the assembly differs. (Resolves the earlier
    "numpy vs sympy" question: support **both**, numpy default.)
  - Resolve `n` from `cls.DIMENSION` (specialized) or an explicit arg (`Gn`).
  - Build the homogeneous `(n+1)×(n+1)` via the one extraction above (no
    per-linearity branch on size); **raise on `NONLINEAR`**.
  - Convention: row-major array, **translation in the last column**, column-vector
    / premultiply — matching `pyMatrixStack` exactly.
- Tests: `translate(b)` → identity-3×3 + `b` in the last column; `uniform_scale(m)`
  → `diag(m,m,m,1)`; a linear map → 4×4 with a **zero** translation column
  (the headline requirement); `compose([f,g])` → `to_matrix(f) @ to_matrix(g)`
  (same order `compose` applies); `inverse(f)` → matrix inverse; `NONLINEAR`
  raises. Cross-check `rotate`/`ortho` against mvp's `pyMatrixStack` hand-written
  forms so the two agree (numerically, float-tolerant).

## Resolved / open

- **Return type — RESOLVED:** both backends, `numpy` float32 default, `sympy`
  optional.
- **Convention — RESOLVED:** row-major, translation in the last column,
  column-vector premultiply; matches `pyMatrixStack`.
- **Size — RESOLVED:** always homogeneous `(n+1)×(n+1)`; linear ⇒ zero translation
  column.
- **Non-linear — RESOLVED:** raise; projective perspective supplied directly
  (mvp), special-case deferred.
- **Open (minor):** also offer a bare non-homogeneous `n×n` (e.g.
  `homogeneous=False`) for pure-math/sympy use? Default: homogeneous-only for now,
  add the flag if a real need appears.
- **Open (minor):** `Gn` (no fixed dimension) requires an explicit `n`; infer it
  for `G1/G2/G3` from `DIMENSION`.
```
```
