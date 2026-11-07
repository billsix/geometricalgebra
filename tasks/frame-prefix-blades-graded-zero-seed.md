# `prefix_blades` returned zeros on graded `Vector` input (the `A_0 = 1` seed was dropped)

**Created:** 2026-11-04 (William Emerison Six <billsix@gmail.com>), found while prototyping
`tasks/archive/2026/11/04/frame-class-orthonormal-invertible-function.md`. **Done:** 2026-11-07.

## Outcome

`prefix_blades`, `make_orthogonal_frame_hestenes`, and `make_orthogonal_frame_hestenes_inverse`
(`src/gacalc/frame.py`) returned all zeros on the generated graded `g2.Vector` / `g3.Vector` types (the
inverse form raised `ZeroDivisionError`). The fold was seeded with `type(vectors[0]).one()`, and a graded
`Vector`'s `one()` is the zero vector: a grade-1 type cannot hold a scalar (the graded silent drop in
`tasks/reference/blade-dict-interchange.md`).

The fix landed during the reciprocal-frame work
(`tasks/archive/2026/11/07/reciprocal-frame-hestenes.md`), which hit the same trap: a private helper
`_scalar_one(vector) = type(vector.dot(vector)).one()` seeds the fold with the scalar type's one, and both
`prefix_blades` and `all_wedged_except_the_kth` use it. The `Gn` path is unchanged (`Gn.dot` returns a
`Gn`). This task was not closed at the time; it was archived on 2026-11-07 when the overlap was noticed.

Tests in `tests/test_frame.py`: `test_prefix_blades_on_a_graded_type` (g2), and
`test_hestenes_forms_on_a_graded_type`, parametrized over a concrete oblique g2 and g3 frame, which checks
that the inverse form equals the rejection frame exactly and that the reverse form is a positive multiple
of it. The `CHANGELOG.md` `[Unreleased]` "Fixed" entry was written with the fix.
