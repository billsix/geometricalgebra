# Explicit-inputs rewrite of the remaining symbolic tests + plot-helper cleanup

**Status:** DONE 2026-08-25. Both remainders finished: `test_numeric_magnitude.py` now inlines its two
`sym_vec3_1` uses as explicit `g3.Vector` symbolic vectors (dropped the `gn` import), and the redundant
`nbplotutils.cosine(v1, v2)` free function was removed — its two call sites now use the `v1.cosine(v2)`
method (verified numerically equal, 11/15). `nbplotutils.sine` kept as-is per the 2026-08-24 decision.
Verified: full suite 405 passed, ruff + ty clean, `displayrotations`/`displayg2` (the `create_x_and_y`
sine/cosine path) execute headless. (Earlier: `test_multivector.py` DONE + `nbplotutils.sine` resolved
2026-08-24.)
**Priority:** 5
**Difficulty:** 4

## Goal

Two related cleanups, both surfaced while making the frame/measure symbolic tests readable:

1. **Rewrite the remaining symbolic tests to the explicit-inputs style** — general vectors written
   out inline (`a = a_1 e_1 + a_2 e_2`) with expected outputs asserted against their exact formulas,
   so each test reads like the math (this is a **learning framework**; a test you can't read teaches
   nothing). No shared `sym_vec_*` fixtures, no `parametrize`/loops hiding the inputs and outputs.
2. **Remove/rewrite redundant helper functions** found in the audit.

## Part 1 — symbolic-test explicit rewrite

**Already done (2026-08-23/24), the pattern to copy:** `tests/test_measure.py`, `tests/test_frame.py`,
`tests/test_dot_wedge_projection_split.py` — inline general symbolic vectors, explicit expected
outputs (`signed_area == a_1 b_2 - a_2 b_1`, the 3×3 determinant written out, dot/wedge spelled out),
2D symbolic + concrete-numbers 3D where the symbolic output is intractable.

**Remaining candidates (audit 2026-08-24):**

- **`tests/test_multivector.py` — DONE 2026-08-24.** The `sym_vec2_1`/`sym_vec2_2`/`sym_vec3_1`/
  `sym_vec3_2`/`sym_vec_plane` imports were dropped; each symbolic test now inlines its general vectors
  (`u = a_1 e_1 + a_2 e_2`, `v = b_1 e_1 + b_2 e_2`, 3D analogously) and asserts the explicit formula
  (dot `== a_1 b_1 + a_2 b_2`, wedge `== (a_1 b_2 - a_2 b_1) e_12`, the full product split into dot +
  wedge parts, dual, even/odd, reverse, inverse, project/reject, normalize). A tautological
  `sym_vec3_1.dot(sym_vec3_2) == sym_vec3_1.dot(sym_vec3_2)` was replaced by the explicit 3D dot. 23
  tests pass; ruff + ty clean.
- **`tests/test_numeric_magnitude.py` — minor.** Two uses of `sym_vec3_1` (`abs(...)` is a
  `sympy.Expr`; `.inverse()` is not `None`). These are about numeric-magnitude behavior, not a formula
  to show — inline the vector for consistency, but low value.
- **EXCLUDE `tests/test_conformance.py`.** It uses `Gn.symbolic_multivector(...)` systematically to
  check that the general `Gn` and the generated graded types **agree** — the "output" is "the two
  representations are equal," not a formula a reader learns from. Leave the conformance style as-is.

## Part 2 — helper-function cleanup (audit 2026-08-24)

- **`nbplotutils.cosine(v1, v2)` — REMOVE (redundant).** Verified equal to the `cosine` **method** on
  `MultiVectorBase` (`v1.cosine(v2)`, base.py:743). Replace its two call sites in `nbplotutils.py`
  (~lines 289-290, 389-390) with `v1.cosine(v2)` and delete the free function.
- **`nbplotutils.sine(v1, v2)` — KEPT the rotate-90-then-project form (Bill, 2026-08-24), NOT rewritten
  via `signed_area`.** Bill likes the `rot90 = v1 * e_12; (rot90·v2)/|v1 v2|` form for teaching. **A
  `signed_area` rewrite was tried and rejected:** `signed_area` needs a fixed-`DIMENSION` type, but the
  plot helpers default to `cls=MultiVector` (the dimensionless `Gn`) and **`displaymv.py` draws its
  graph paper with that default**, so `signed_area` would raise (and 2 vectors in 3D is `k < n`, which
  also raises). **What changed:** added `assert v1.is_vector() and v2.is_vector()` — the `abs(v1*v2)`
  step uses `|v1 v2|` as `|v1||v2|`, which only holds for vectors (Bill's point). *(The mathematical
  identity `sine == signed_area/(|v1||v2|)` still holds for a fixed-dim 2D type — recorded for the
  book, just not used in the plot helper.)*
- **`base.py` `cosine` method — KEEP.** The canonical one, `cos θ = (Ã ∗ B)/(|A||B|)` (Hestenes &
  Sobczyk p. 14, eq 1.53b), 12 uses (tests + the display notebooks' `a.cosine(b)`). Bill confirmed:
  don't touch it. *(There is no `abs_sin`/`abs_cos`/`angle_between` — 0 hits; the real targets were
  the two `nbplotutils` free functions above.)*

## Verify (when implemented)

- `make format` green; full suite green. For Part 2, re-run the notebooks / plot helpers that call
  `sine`/`cosine` (the `create_x_and_y`/triangle-drawing paths) so the graph-paper figures are
  unchanged.

## Open questions

1. **Scope of the `test_multivector.py` rewrite** — do the whole file, or just the vector-identity
   assertions that most benefit (dot/wedge/product/dual)? *(Rec: the whole symbolic section, for
   consistency; it is the last big fixture-driven symbolic test file.)*
2. **`nbplotutils.sine`** — rewrite it via `signed_area` (my rec), or remove it entirely and inline
   `signed_area(...)/(|v1||v2|)` at its two call sites?
