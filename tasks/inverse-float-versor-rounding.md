# `inverse()` rejects a float versor because of rounding, so 3D float `versor_rotation` crashes

**Status:** proposed — needs go-ahead
**Priority:** 3
**Difficulty:** 3
**Created:** 2026-11-18 (William Emerison Six <billsix@gmail.com>; found while writing
`tests/test_frame_svd.py` for `tasks/archive/2026/11/18/frame-svd-investigation.md`)

## BLUF

`MultiVectorBase.inverse` (`src/gacalc/base.py`) raises `RuntimeError("inverse() supports a blade
or versor …")` unless `Ã * A` is exactly a scalar. With float coefficients, a 𝒢₃ versor's `Ã * A`
carries a rounding residue in a bivector coefficient (8.9e-16 below), so the check fails. Because
`versor_rotation` inverts its versor, it crashes on ordinary float vectors in 3D. Done means:
- a float versor inverts;
- a genuinely mixed-grade float element is still rejected;
- a test pins both;
- the gates pass.

## Reproduction

```python
from gacalc.g3 import e_1, e_2, e_3
from gacalc.transforms import versor_rotation
a = 2.0 * e_1 + 1.0 * e_2 + 0.5 * e_3
b = 0.5 * e_1 + 3.0 * e_2 + 1.0 * e_3
R = a.versor_from_vectors(from_vector=a, to_vector=b)
R.reverse() * R   # Versor(coeff_scalar=173.646…, coeff_e_12=0.0, coeff_e_13=0.0, coeff_e_23=8.88e-16)
versor_rotation(from_vector=a, to_vector=b)(1.0 * e_3)   # RuntimeError
```

In 2D the problem cannot occur, because a 𝒢₂ versor's `Ã * A` has no bivector term to round. The
3D route-1 test in `tests/test_frame_svd.py` works around it by wrapping `projection_rotation` in an
`InvertibleFunction`, and its comment names this task.

## Context (read first)

- `base.py` `inverse`: the gate `if not reverse_times_self.is_scalar()`, then `Ã / |A|²`.
- `tasks/reference/approximate-float-equality.md`: `isclose`, gacalc's tolerance model.
- `tasks/reference/numeric-symbolic-mode.md`: the recommendation to decide float tolerance from the
  coefficients (`tasks/tolerance-from-coefficient-type.md`). This gate is one more place that needs
  that decision.

## Plan

1. When `Ã * A` has float coefficients, accept it as a scalar if its non-scalar part is small
   relative to the scalar part. A relative tolerance is needed: here `|A|²` is 173, so an absolute
   1e-15 would be wrong for large vectors. Keep the exact test for integer and symbolic input.
2. Tests:
   - the reproduction above rotates `e_3` and round-trips through `inverse`;
   - a float mixed-grade element (scalar + vector) still raises.
3. Decide whether this lands before or with `tasks/tolerance-from-coefficient-type.md`; it can use
   that task's shared `_has_float` once that exists.

## Open questions

None yet.
