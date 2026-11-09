# Lean proofs: "geometric objects in, components out" — dissolve the scalar `_coord` layer

**Created:** 2026-10-03 · **Completed:** 2026-10-04 (William Emerison Six <billsix@gmail.com>)
**Absorbed:** `tasks/archive/2026/10/04/lean-lift-theorem-statements-to-objects.md` (the earlier
statement-lift sweep, Increments 1–23). **Optional follow-up:** `tasks/push-delicate-coordinate-core-tier.md`.
Recipes and dead-ends were harvested into `tasks/reference/lean-ga-proof-architecture.md`.

## Summary

Every Lean theorem whose proof is **polynomial** was converted to "geometric objects in, scalars in the
body, geometric objects out": it takes the object and a grade predicate (`{a : G3} (ha : IsVector a)`,
`{R} (hR : IsEvenVersor R)`, `{B} IsBivector`, `{T} IsTrivector`), concludes about objects, and drops to
coordinates only in the body (`obtain ⟨…⟩ := ha; simp only [defs, those-zeros]; ring`, computing on the
`a.c1`/`a.c12` getters). It never takes free scalars `(a1 a2 a3 : ℝ)` and constructs `vec a1 a2 a3` inside.
This removed most of the scalar-taking `_coord` leaves (`foo_coord (reals) : P (vec reals)` plus an object
`foo` bridging with `rwa [← eq_vec] at h`) that the statement-lift sweep had introduced. The non-polynomial
tier was kept on a coordinate core by a maintainer-approved decision (option (a), 2026-10-04). `make lean`
was green at every step.

The maintainer's direction (2026-10-03): "take geometric objects as inputs, and then in the body, get their
components, rather than taking scalars as inputs, and then constructing geometric objects."

## Technique

- **Two inline shapes, the first preferred.** `obtain` (pure): `obtain ⟨hs, h12, …⟩ := ha; simp only
  [sandwich, mul, reverse, normSq, hs, h12, …]; field_simp; ring`, with no `vec`/`evenVersor` ever rebuilt.
  `rw [eq_vec_of_isVector ha]` (lighter): turns the goal into the `vec`-literal form so an existing
  coordinate proof runs verbatim; used only to preserve a fragile proof.
- **Sharing moves to the object level.** The `_coord` leaves had looked shared only because the theorems
  above them were also `_coord`. Once composites composed object sub-lemmas (`sandwich_preserves_cos`/`sin`
  compose the object `dot`/`wedge`/`magnitude` isometries), each leaf's `_coord` lost its callers.
- **Textual ordering is a hard constraint.** A composite's `rw [leaf hR hu hv]` compiles only if the object
  leaf sits *above* it in the file. The lift sweep had put every object form in an end-of-namespace wrapper
  block, so composing them was a forward reference ("Unknown identifier"). The fix was to **convert in
  place**: rewrite each `_coord` leaf's body to `obtain`-getters, rename it (drop `_coord`), and delete the
  end-block duplicate. The `_coord` decls were already ordered leaf-before-composite, so the order held.
  "Bottom-up" had to mean bottom-up in the file, not only in the dependency DAG.
- **The divide-by-`normSq` pattern.** A direct getter proof of `sandwich_preserves_dot` failed: the inverse
  puts `(normSq R)²` in a denominator, the getter unfold expands it, and `field_simp [hr]` cannot match
  `hr : normSq R ≠ 0`. The fix was a leaf that keeps `normSq R` atomic, **`dot_reverse_sandwich`**
  (`(R u R̃) · (R v R̃) = normSq R ² · (u · v)`, G2 + G3), composed with `field_simp [hr]`. So there was no
  "fighter" class among the division proofs. `dot_smul_left/right` already existed (G2's in `Versor2D.lean`,
  missed by a first grep of `G2.lean` only).
- **Getter gotchas.** `inner_vb` builds a `vec`, so `vec` must be in the `simp` set; an `= a` RHS exposes
  `a`'s non-vector components only after `ext`, so the zero-substitution is repeated after `ext`.
- **Docstring hygiene.** Merging a `_coord` + wrapper meant deleting the stale leaf docstring: two
  `/-- … -/` before one declaration is a parse error (it bit bucket 1; found by a scan for that shape).

## Decisions (the maintainer, 2026-10-03: "go with your recommendations"; 2026-10-04 for the core)

1. **Form-D `vec`-unfold bridges stay coordinate** (`normSq_vec`, `dot_vec`, `cross_vec`, `dual_vec`,
   `wedge_vec_eq_biv`, `normSq_wedge_vec`, `magnitude_sq_vec`, `vec_mul`, `vec_eq_smul`, `reverse_vec`,
   `signedArea_eq`, `normSq_biv`). Flipping them to object-in (`normSq a = a.c1² + a.c2² + a.c3²`) only moves
   the coordinates onto the RHS, while they are used corpus-wide as `rw`-unfold lemmas. Those left unused
   after the conversion were deleted.
2. **Coordinate-parameterized defs stay coordinate** (`rotXY_vec`/`rotXZ_vec`/`rotYZ_vec`, `rotYZ_fixes_e1`,
   `rotXY_aligns_xy`, `rotate_b_to_e1`, `reduceToPlane_*`, `Exp.expBivector*`): the cos/sin (or `p q r`) are
   the construction's scalar input; `Exp` would need a def redesign.
3. **Genuine scalars kept:** the `Rotation2D` angle layer, `lagrange_2d`/`lagrange_3d`, the
   `cos_between`/`sin_between`/`versorFromVectors` scalar parameters, `k` multiples, and the companion
   lemmas `isVector_vec`/`isBivector_bivector`/`isTrivector_trivector`/`isEvenVersor_evenVersor`.
4. **The non-polynomial tier keeps its coordinate core** (option (a), 2026-10-04): sqrt/`magnitude`/
   `normalizeVec` proofs, the divide-by-`normSq(a∧b)` plane projections (degree blow-up), the cos/sin/angle
   cases, and the delicate `calc`/`set` capstones. Their public statements were already object-in; only the
   private scaffold stayed coordinate. Pushing it would need new object `magnitude`/`normalizeVec` lemmas
   first, at high risk for little gain; that is the optional follow-up task.
5. **Redundant `simp only` args were left** (low value): `simp only` ignores a rule that does not fire, and
   trimming per theorem needs a rebuild each.

## What was converted (all `make lean` green)

- **Bucket 1** (single-caller pass-throughs): `vec_mul_mul_self`, `sandwich_evenVersor_vec_isVector`,
  `rotation_fixes_plane_bivector`/`rotation_preserves_dot`, `reverse_versorFromVectors_mul`, and
  `sandwich_preserves_cos`/`sin` (G2 + G3, fully object).
- **`Sandwich.lean`, full** (G2 + G3): the vec/wedge cluster (`normSq_reverse_sandwich`,
  `wedge_reverse_sandwich`, `normSq_reverse_sandwich_wedge` as `obtain` leaves;
  `sandwich_preserves_normSq_of_vec`, `sandwich_preserves_wedge`, `sandwich_preserves_normSq_of_wedge`,
  `magnitude_sandwich_vec` composing them), `sandwich_preserves_dot` via `dot_reverse_sandwich`, and the
  inverse-self composites (`mul_biv_inverse_self`, `mul_triv_inverse_self`, `versorFromVectors_mul_inverse`).
  `RotateComponents.rotation_preserves_dot` was changed to compose the object `sandwich_preserves_dot`.
- **`Reflect.lean`, full;** **`Projection2D.lean`, full** (the G2 wedge cluster, all 5 `_coord` deleted);
  **`Projection3D.lean`**, 3 of 4 bivector proofs (`project_add_reject`, `reject_eq_proj_normal`,
  `project_eq_sub_reject`); **`G3.lean`** self-product wrappers; **`Trig.lagrange_property`** (G2 + G3);
  the pure-polynomial `ProjectionRotation` scaffold leaves (2D `mul_vec_self`, `normSq_mul_three_vec`; 3D
  `wedge_vec_wedge_self`).

**Retained coordinate core:** both `ProjectionRotation` capstone files (`key_reverse_sq`,
`fhat_that_eq_reverse_mul_inverse`, `magnitude_sq_of_normSq`, the bisector lemmas; G2 `versorFromVectors` is
`magnitude`-based, so `versorFromVectors_mul_vec_eq` left `magnitude` atoms unsolved and was reverted to its
bridge), `CrossStandardPosition`, `TrigEquiv`, `cos_sq_add_sin_sq` (needs `Real.sq_sqrt` + positivity),
`reject_vec_eq` (a structural Hestenes-split proof with many coordinate deps), `rotation_fixes_normal`
(its `cross b a` reconciliation), and the `Sandwich` delicate capstones (`sandwich_carries_from_to`,
`sandwich_fixes_own_bivector`/`_normal`, `sandwich_comp`).

## Final sweep (2026-10-04)

The maintainer asked "are those components even used?" Every remaining `_coord` was still consumed by a
retained-core proof, so none was orphaned; the deletable ones had gone in place as each file was converted.
Two dead helpers were removed: `normSq_triv` (its only caller had been deleted) and `signedArea_sq` (an
unused form-D restatement). The other bridges were live (`normSq_vec` 31 uses, `cross_vec` 8,
`wedge_vec_eq_biv` 9, `normSq_biv` 8, `magnitude_sq_vec` 6, the rest 1–3). A whole-library zero-use scan
flagged ~100 names, nearly all public deliverable theorems, so zero use was not a deletion criterion. No
unused `obtain` bindings: every destructured name appears in its `simp only` list, and the build showed no
`unusedVariables` warnings.
