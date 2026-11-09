# `nbplotutils.sine`: correct for graded vectors, and only in the plane

**Created:** 2026-11-09 · **Completed:** 2026-11-09
**Source:** `tasks/review/2026/11/08/repo-review.md` §4.2

## What was wrong

`nbplotutils.sine` turned `v1` by 90° with `v1 * type(v1).from_blade_dict({(1, 2): 1})`. On a graded
`Vector` that silently drops the bivector, so the turn was zero: `sine(1*g2.e_1, 1*g2.e_2)` gave 0.
It also gave 0 for perpendicular vectors off the e₁e₂ plane. It used `abs(v1 * v2)` (against the
"`|a| * |b|`, never `abs(b * a)`" decision) and a bare `assert`.

## What changed

- **The formula.** `sine(v1, v2)` is the `e₁₂` coefficient of `v1 ∧ v2` (the signed area) over
  `|v1| * |v2|`. It runs `require_vectors` first, keeps the zero-vector `ValueError`, and raises
  `ValueError` when the wedge has a part outside the e₁e₂ plane. It works for `Gn`, the 𝒢₂ types,
  and plane vectors of any representation.
- **Why not `measure.signed_area`.** It was the first choice, but on `Gn` it infers the space's
  dimension from the vectors, so two vectors along `e_1` (which `draw_ndc` passes) look like a 1-D
  space and raise. That is the review's §4.3 lead about `signed_content` on dependent `Gn` sets,
  left as it is.
- **Tests in `tests/test_nbplotutils.py`:**
  - `sine(e_1, e_2) = 1`, `sine(e_2, e_1) = −1` and `sine(3*e_1, 2*e_1 + 2*e_2) = √2/2`, on `Gn`,
    `g2.Vector` and `g2.G`;
  - two 𝒢₃ vectors off the plane raise;
  - a bivector argument raises.

  3 of them fail on the old code.

There is no changelog entry: `nbplotutils` is the notebooks' plotting helper.

## Verification

- `tests/test_nbplotutils.py`: 6 passed.
- `ty check --no-respect-ignore-files src` and `ruff`: clean.
