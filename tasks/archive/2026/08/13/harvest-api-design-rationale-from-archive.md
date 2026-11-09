# Harvest archived API/design rationale into the live docs

**Created:** 2026-08-13 · **Completed:** 2026-08-13

Group B of the 2026-08-13 archive gap-analysis sweep (medium-confidence design/API rationale,
mostly rejected alternatives). Siblings: the other `harvest-*` tasks in this folder and
`tasks/archive/2026/08/13/blade-dict-interchange-reference.md`.

## What was harvested, and where

All six items were verified against the current source before writing. Five went to
`tasks/reference/design-decisions.md`, one to CLAUDE.md. (Source docs are under
`tasks/archive/`.)

- **`to_matrix` two backends + convention** → design-decisions `to_matrix` entry.
  `backend="numpy"` (float32, default, for GL) vs `"sympy"` (exact/symbolic); column-vector /
  premultiply convention with the translation in the **last column**, matching mvp's
  `pyMatrixStack` (a cross-repo contract); `Gn` needs an explicit `n` (specialized classes read
  `DIMENSION`). From `2026/06/08/invertiblefunction-to-matrix.md` and
  `2026/06/12/to-matrix-build-by-columns.md`.
- **`x`/`y`/`z` coordinate properties are grade-1-only** (Vector1/2/3), deliberately not on
  rotors/bivectors/full types ("a vector's coordinates ARE its coefficients") → CLAUDE.md
  Architecture. From `2026/07/09/upgrade-rotation-and-ctc-vector-mapping.md`.
- **Declined vector-API additions** → design-decisions (API › rejected alternatives): no `cross`
  (it is `(a∧b).dual()`, zero call sites), no `__getitem__`/`__len__` (`__iter__` already yields
  blade-order coefficients), no zero-safe `normalize`. Same source.
  - **Correction found while verifying:** the archived "a zero vector raises" claim was only half
    true. A *float*-zero vector raises `ZeroDivisionError`, but an *int/symbolic*-zero vector
    yields a silent `nan` (sympy `0**-1 → zoo`). The doc recorded the accurate behavior.
- **`InvertibleFunction.__matmul__` overloads preserve invertibility in the type** (invertible @
  invertible → invertible; @ composable → composable) → design-decisions (composable-function
  hierarchy). The generic-TypeVar-bound alternative was tried and rejected: ty rejects a generic
  bound (`invalid-type-variable-bound`), and bounding by the bare base is unsound for subclasses
  (`Rotation @ Rotation` would falsely type as `Rotation`, while `compose` only returns a plain
  `InvertibleFunction`). From `2026/07/18/release-0-0-10-and-bump-mvp.md`.
- **Why rotation normalizes from/to, and rotor-sandwich scaling** → design-decisions (near
  derived-sandwich). Un-normalized rotate "works" only in 2D; in 3D it scales the in-plane
  component by `|from||to|` and leaves the perpendicular component unscaled, a non-uniform
  distortion no single rotor sandwich reproduces. The three-way distinction: dividing by the
  scalar `R R̃` (= `magnitude_squared`) recovers the pure rotation; dividing by the sandwich's own
  `magnitude_squared` gives the geometric inverse; normalizing `R` needs `sqrt(R R̃)`, a nested
  radical sympy chokes on. From `2026/06/06/graded-blade-subtypes.md`.
- **Animation-layer semantics** → design-decisions (API › composable-function), checked against
  the 2026-07-17 composable-function reassessment first: the `at(t)` three-tier resolution (own
  `interpolate` law → recurse through `components` → else step at t≥1); `compose` must store
  `components` for `at`/`steps` to recurse; per-factory laws (`translate(b)` → `translate(b·t)`,
  `uniform_scale(m)` → linear 1→m); and the invariant **`inverse(f).at(t) == inverse(f.at(t))`
  at every t**, which lets an against-the-arrow edge animate smoothly rather than snap. From
  `2026/06/08/port-animation-layer-from-mvp.md`.
