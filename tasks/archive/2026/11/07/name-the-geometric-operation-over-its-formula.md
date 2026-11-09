# Write the named geometric operation (project, reject, …) where code computed its formula by hand

**Created:** 2026-11-07 (William Emerison Six <billsix@gmail.com>) · **Completed:** 2026-11-07

The maintainer wanted gacalc's code to show a student how the math works, ahead of raw speed: "I think
'project' and 'reject' make much more sense to a student, than using the dot product directly." Four
places that computed a dot-product formula by hand were changed to call the named operation, with equal results;
`reflect` lost its bare `assert` and bare `Exception`; the rule is in `CLAUDE.md`. The cost: the 3D
symbolic frame tests took about twice as long (below).

## What changed

1. **`Frame.coefficients()` and the peel step** (`src/gacalc/frame.py`) read each coefficient through a
   new private helper, `_projection_coefficient(v, onto=w) = (v.projected_onto(w) / w).scalar_part()`:
   how many copies of `w` the projection of `v` onto `w` is. It replaced `_exact_quotient`, which was deleted.
   Exactness holds without it, because `project` and `/` divide through `inverse` (ints become exact
   rationals, floats stay floats); the helper's doctest shows both. `frame.py` stopped importing
   `sympy`; the `reciprocal_frame` doctest imports it itself.
2. **The book notebooks** `book/docs/notebooks/frame-qr-2d.py` and `frame-qr-3d.py`: the five
   coordinate steps (`x_1`, `x_2` in 2D; `x_3`, `x_2`, `x_1` in 3D) project and divide. The markdown says
   "project", and keeps the "two heights, one divided by the other" reading, since the projection's
   length is the height. The setup cells' dot products stayed: they show that `w_1` is *not*
   perpendicular to the last vector, which is a dot-product fact. The figures' labels (`w_2 · y / |w_2|`
   as a height) stayed: they draw heights.
3. **The forward map** was changed to read `x.coefficient(cls.basis_vector(i))`.
4. **`_project_point`** (`book/figures/epix/_projection_scene.py`) builds two `g2` vectors, calls
   `projected_onto`, and reads the point back with `coefficient(blade=…)`. Its result is identical to the
   old hand formula (difference 0.0 in both coordinates, checked in the container).
5. **`reflect`** (`src/gacalc/base.py`): the applied reflection checks with
   `MultiVectorBase.require_vector(value, "reflect")`; an `across` that is neither a vector nor a bivector
   raises `ValueError` naming `reflect`. Tests: `test_reflect_across_a_scalar_raises` and
   `test_reflect_of_a_non_vector_raises` in `tests/test_conformance.py`. `CHANGELOG.md` `[Unreleased]`
   › Changed has the breaking entry.
6. **`CLAUDE.md`**: "Write the named geometric operation where the code means it", next to the
   dot-product rule, with the exceptions (the primitives' own definitions, code whose subject is the dot
   product).

## Cost, measured

| | before | after |
|---|---|---|
| `tests/test_frame.py` + `tests/test_frame_class.py` | 6:04 (81 passed) | 12:15 (88 passed: +7 doctests from `frame.py`) |
| `test_coefficients_are_triangular_with_unit_diagonal[frame_3d]` | 70 s | 190 s |
| `test_composed_round_trip_is_identity_symbolic[3d-peel]` | 64 s | 200 s |
| `test_inverse_methods_are_equivalent_symbolic[3d]` | 38 s | 151 s |
| one coefficient, general 3D frame, `(w_2, v_3)` | 1.9 s | 62 s |

The cause is `Gn`'s eager `sympy.simplify`, which runs after the projection's inverse and product and
again after the division by `w`; the dot-product quotient simplified once. Every other test was
unchanged. The full suite went from 6:19 (776 tests) to 12:15 (787).

## Gates

- `entrypoint/format.sh` (ruff, ty over src/tests/tools/notebooks, the ePiX keyword check, changelog):
  green. ty first caught two notebook annotations (`projected_onto` on a `MultiVectorBase` operand
  returns `MultiVectorBase`, not `Vector`) and the keyword check caught `coefficient(e_1)`; both fixed.
- Full `pytest` (with doctests), 12:15: 781 passed, 6 failed. The six were the new
  `test_reflect_across_a_scalar_raises`: `reflect` built `reject(across)` before checking `across`, and
  `reject` raised its own bare `Exception` first. `reflect` was changed to build the projection and rejection inside
  `reflection(blade)`, after the `match` has checked the blade; `tests/test_conformance.py` and the other
  reflect tests then passed (241 passed), and `format.sh` stayed green.
- **Not run: `make docs`.** The local image is the lean one (no ePiX, no Sphinx), so the projection figure
  was not re-rendered; its point was checked numerically instead.

## Left alone, and why

The primitives' definitions (`project`/`reject`, `cross`, `sandwich`, `exp`, `cosine`, the measures);
code that already used the named operations (`reflect`, `projection_rotation`, `make_orthogonal_frame`);
the reciprocal inverse `vⁱ · y` (that dot product is eq 3.5, explained in
`tasks/reference/frames-qr-and-reciprocal-frames.md`); the trigonometric rotor in `transforms.py` (the
sine/cosine presentation rule); notebooks whose subject is the dot product; `standardposition.py` (the
deliberate standard-position duplicate); the generated `g1`–`g3` modules (the fast path by design).

## Decisions after the work

1. **Keep the projection form in `frame.py` despite the doubled 3D symbolic test time** (William Emerison
   Six <billsix@gmail.com>, 2026-11-07: "yes").
2. **`reject` had the same bare `raise Exception("TODO - implement project for " + …)` as `reflect`**;
   fixed the same way on the maintainer's "sure" (2026-11-07): `ValueError` naming `reject`,
   `test_reject_away_from_a_scalar_raises`, and a `CHANGELOG.md` breaking entry.
