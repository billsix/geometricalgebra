# project: narrow to the operand's grade/type (was widening to G_n)

Status: **DONE 2026-06-12** (Bill spotted it) · no prior task doc — recorded here.

## Symptom

`Vector3.project(onto=Bivector3.e_12)(v)` returned a **`G3`** instead of a
`Vector3` — even though projecting a vector always yields a vector.

## Cause

`base.project`'s `is_r_vector` branch was `return (value.dot(onto)) * onto.inverse()`.
`P_B(A) = (A·B)B⁻¹` is **grade-preserving** (a grade-r input projects to grade r),
so the *value* is always grade r. But the generic geometric product widens the
*type*: `value.dot(onto)` is already a `Vector3`, and the `* onto.inverse()` step
(`Vector3 * Bivector3⁻¹`) types as the odd part `{1,3}` → `G3`, because a
vector·bivector *could* carry a grade-3 part. For a projection that grade-3 part is
**identically zero** (confirmed empirically) — it was a vector wearing a `G3` tag.

## Fix (`base.py`, `project`'s `is_r_vector` branch)

Keep grade r and rebuild in the operand's own type (same spirit as the rotor
`sandwich`'s grade projection):

```python
projected = (value.dot(onto)) * onto.inverse()
grades = list(value.grades())
r = max(grades) if grades else 0
return type(value).from_blade_dict(projected.r_vector_part(r).to_blade_dict())
```

Now `Vector3.project(onto=Bivector3.e_12) → Vector3`, `Vector2.project(onto=Bivector2)
→ Vector2`, `Vector3.project(onto=Trivector3) → Vector3`. Values unchanged
everywhere; `Gn`/full classes rebuild as themselves (no change). Documented in
`CLAUDE.md` (project/reject grade-preservation note).

## Tests added

- `tests/test_conformance.py`: `test_project_vector_onto_bivector_2d` (G2 + Gn) and
  `test_project_vector_onto_bivector_and_trivector_3d` (G3) — vector onto a bivector
  plane keeps the in-plane part / drops the perpendicular; onto the trivector
  returns the vector.
- `tests/test_graded.py`: `test_project_vector_onto_bivector_trivector_subtypes` —
  asserts the **narrowed type** (`type(proj) is Vector2`/`Vector3`) for the
  subtypes, plus values.

Full suite (219) + ty + ruff green.

## Related

- The widening was the odd-`{1,3}` gap (`tasks/model-odd-graded-type.md`) showing
  up in `project`; this fixes `project` specifically (grade-preserving narrowing),
  independent of whether that odd type is ever modeled.
- `reject` (`(A∧B)B⁻¹`) is also grade-preserving but still only implemented for
  vector/bivector blades — see `tasks/generalize-reject-reflect-higher-grade.md`.
