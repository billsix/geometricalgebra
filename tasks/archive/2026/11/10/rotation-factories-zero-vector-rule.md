# Rotation factories: from 0 to 0 is the identity; 0 to nonzero is a ValueError

**Created:** 2026-11-10 (William Emerison Six <billsix@gmail.com>) · **Done:** 2026-11-10
**Split from:** `tasks/archive/2026/11/14/standard-position-e3-axis-and-vector-rotations.md`

Decision (William Emerison Six <billsix@gmail.com>, 2026-11-10): the zero-vector rule applies to all
the public rotation factories. A rotation from the zero vector to the zero vector is the identity; from
zero to a nonzero vector, or back, raises `ValueError`.

- **Before:** every factory failed on a zero vector. `projection_rotation` raised "point in opposite
  directions" (the zero wedge sent it into the parallel branch, where `0 · 0` is not positive);
  `versor_rotation` and `rotor_from_vectors` raised `ZeroDivisionError`; `versor_from_vectors(0, 0)`
  returned the zero versor.
- **Guard:** `MultiVectorBase.require_rotation_endpoints(from_vector, to_vector)` (`base.py`, a
  `@validation_guard`): requires vectors, then raises when exactly one is zero.
- **Identity:** `versor_from_vectors` returns `type(to_vector * from_vector).one()` (the versor `1`
  at the versor's type) when both are zero, so `versor_rotation` and `rotor_from_vectors` inherit the
  identity. `projection_rotation` treats both-zero like same-direction parallel vectors.
- **Not covered:** `plane_rotation(a, b)` and `bivector_rotation` take a plane and an angle, not a
  from/to pair; `project_sp` (the reason for the rule) stays parked with its task.
- **Tests/docs:** `tests/test_rotation_zero_vector_rule.py` (24 cases: four factories × `Gn`/`g3` ×
  identity and both raising directions); simple-first doctests on `projection_rotation`,
  `versor_rotation`, `versor_from_vectors`; `tasks/reference/transform-and-composable-function-layer.md`;
  CHANGELOG `[Unreleased]` → Changed.
- **Gate (host):** ruff + ty clean; `pytest -m "not slow"` 797 passed before the new test file, plus
  its 24.
