# Lean: the G2/G3 laws in teaching order, and the "scalars in" theorems

**Created:** 2026-11-09 · **Completed:** 2026-11-09
**Source:** `tasks/review/2026/11/08/repo-review.md` §7.2
**Related:** `tasks/push-delicate-coordinate-core-tier.md` (the `_coord` tier; it now also lists the
three theorems left below) and `tasks/lean-proofs-remove-extras.md` (unused tactics). Both are kept
separate.

## What changed

### The laws, in teaching order (`tasks/reference/algebra-teaching-order.md` Part II)

- **G2 and G3 `### The algebra laws`** now read in the order a student meets them: addition first,
  then the product with distributivity last, then the unchanged scalar laws. The section docstring
  says so.
  - New addition laws: `add_comm`, `add_assoc`, `add_zero`, `zero_add`, `add_neg_cancel`.
  - The product: `mul_assoc`, `one_mul`, `mul_one`, `zero_mul`, then `mul_add`, `add_mul`, `sub_mul`,
    `mul_sub`.
- **`G2`** gains `def zero` (G1 and G3 had one). `G2.mul_sub` is new; `G2.sub_mul` moved here from
  `StandardPosition2D.lean`.
- **`G3`'s laws** that lived in `ProjectionRotation3D.lean` (`zero_mul`, `add_zero`, `zero_add`, under
  "Small algebra helpers (absent elsewhere)") moved into `G3.lean`.
- **`G3`'s `dot`** moved from after the laws into "The geometric product, the wedge, and the dot", as
  in `G2`. The later section is now "The inverse pseudoscalar and the dual".
- **Name shadowing.** With `G3.zero_mul` visible to every G3 file, `Predicates3D.lean`'s real-number
  `zero_mul` became `MulZeroClass.zero_mul`. `mul_zero` was deliberately not added to G2/G3, because
  several proofs use the real one inside those namespaces.

### "Scalars in" theorems

Each theorem the review flagged was classified against `CLAUDE.md` › "Coordinates only when needed".

**Restated over `IsVector` objects** (consumers updated):

- `Projection2D.vec_wedge_I_eq_zero (x y)` → `wedge_I_eq_zero {a} (ha : IsVector a)`;
  `reject_from_I_eq_zero` likewise.
- `Projection3D.wedge_reject`, `plane_eq_wedge` and `mul_vec_inverse_self` → object form, with the
  coordinates only in the body (`eq_vec_of_isVector`). Their consumers are
  `StandardPosition.lean`'s projection proof and `Projection3D.reject_vec_eq`.

**Removed:** `G3.vec_mul_perp`. It was unused, a coordinate duplicate of the object
`mul_eq_wedge_of_perp`, and `vec_anticomm_perp`'s doc comment wrongly said it rested on it; that
comment now names `mul_eq_wedge_of_perp`.

**Left as they are, because the rule allows them:**

- the `vec`-literal unfold leaves, whose right side *is* coordinate arithmetic: `G1.vec_mul`,
  `wedge_vec`, `vec_mul_eq_dot_add_wedge`, `mul_vec_inverse_self`, and `G2.dual_vec_perp`;
- `RotateFromTo2D.rotateFromTo_collapse`/`_carries`, whose reals are a rotation's cosine and sine
  readings ("genuine scalars stay scalar");
- `CrossStandardPosition.cross_via_reduction_of_vectors`, the explicit form beside the object
  `cross_via_reduction`;
- the definitions `Measures.signedArea` and `Exp.expBivectorGeneral`.

**Left for `tasks/push-delicate-coordinate-core-tier.md`:** `Sandwich.sandwich_fixes_orthogonal`,
`sandwich_plane_invariant` (both unused) and `normSq_mul`. Each needs a judgment about its object
form ("a versor in the e₁₂ plane").

**Docs:** `tasks/reference/lean-ga-proof-architecture.md` (the theorem names and the new statement
shapes) and `tasks/reference/algebra-teaching-order.md` Part III (the laws order, the moves).

## Verification

- `lake build` and `bash proofs/check.sh`: green. "axioms gate: 1043 declarations rest only on
  propext, Classical.choice, Quot.sound".
- The build's warnings are the pre-existing ones: 2 lines in `G2.lean`, 6 in
  `ProjectionRotation3D.lean`, both tracked by `tasks/lean-proofs-remove-extras.md`. No new ones.
