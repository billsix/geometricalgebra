# Push the delicate coordinate-core tier to object/getter form (optional)

**Status:** in progress — the 2D tier, the carries-from-to capstones, `cos_sq_add_sin_sq` and the Lagrange area form are getter-native (2026-10-05); the 3D projection-rotation scaffold and the remaining Sandwich/Projection3D/Cross coordinate leaves are the open remainder (see "Work record")
`tasks/archive/2026/10/04/lean-object-in-getters-out-proof-style.md`; updated 2026-10-04, William
Emerison Six <billsix@gmail.com>)
**Priority:** 8 (optional; the valuable polynomial tier is already done)
**Difficulty:** 8 (sqrt/`magnitude` algebra + delicate `calc`/`set` capstones)

## BLUF

The object-in-getters sweep converted every **polynomial**-proof theorem to "objects in, getters in the
body" and deliberately **retained the coordinate core** for the non-polynomial tier. This task is the
optional push to make that remaining tier getter-native too. It is **not required** — those theorems'
**public statements are already object-in**; only their *private* coordinate scaffold stays coordinate.
Expect higher risk and lower marginal value. "Done" = the targets below are getter-native (no scalar
`_coord` scaffold feeding them), `make lean` green.

## Why it was deferred (the obstruction)

These proofs are **not polynomial**, so `obtain`-getters + `ring` doesn't close them:

- **sqrt / `magnitude` / `normalizeVec`.** `magnitude a = √(normSq a)`, `normalizeVec a = (1/|a|)·a`, and
  G2 `versorFromVectors` is built from them. `ring` can't reason about `√`; these need `Real.sq_sqrt`
  and nonnegativity side-conditions. There is currently **no object `normSq_nonneg` and no object
  `magnitude_sq`** (only the coordinate `magnitude_sq_vec`); `Normalize.lean` already has the object
  `normSq_normalizeVec`/`magnitude_normalizeVec` as the model — that's the prerequisite (see below).
- **divide-by-`normSq(a∧b)` (degree blowup).** The plane-projection family (`reject`/`project_onto`
  onto `wedge a b`) divides by `normSq(a∧b)`, which is **quadratic** in `a,b`; `field_simp` on it
  cross-multiplies to degree-8 and times out. The `_coord` form exists precisely to prove these on a
  **literal bivector** (`bivector p q r`, degree 1) and instantiate — the deliberate blowup-avoidance.
- **delicate `calc`/`set` capstones.** `projRotation_eq_sandwich`/`_isometry`, `key_reverse_sq`, the
  bisector lemmas, `sandwich_carries_from_to`, `sandwich_fixes_*`, `sandwich_comp` — assembled from the
  sqrt/magnitude scaffold via `calc`/`set`/`rw` chains.

## Work record (2026-10-05)

**Prerequisite cleared** by the rotor work: `normSq_eq_sum_sq`, `normSq_nonneg`, `magnitude_sq_eq_normSq`,
`magnitude_ne_zero_of_normSq_ne_zero` (object, any multivector) — first in `Rotor.lean`, then moved down
into `G2.lean`/`G3.lean` (right after `magnitude`) so every module can use them; `R⁻¹ = R̃` for rotors is
`Sandwich.inverse_eq_reverse_of_isRotor`.

**Converted to getter-native (no `_coord` scaffold left), gate `[lean] OK`:**
- `ProjectionRotation2D.lean`, the whole file: `mul_vec_self`, `reject_plane_eq_zero`,
  `projRotation_eq_vec_mul`, `projRotation_carries_from_to`, `normSq_mul_three_vec`,
  `projRotation_isometry`, `versorFromVectors_mul_vec_eq`, `key_reverse_sq` (the `√` identity: object
  `hK2` from `magnitude_sq_eq_normSq` + `normSq_eq_sum_sq`, then the same `set`/`linear_combination`
  leaf), `fhat_that_eq_reverse_mul_inverse`, `projRotation_eq_sandwich`. Eight `_coord` lemmas and the
  two local magnitude helpers deleted.
- `Sandwich.lean`: `versorFromVectors_mul_reverse` (𝒢₂, direct) and `sandwich_carries_from_to` (𝒢₂ and
  𝒢₃) — the same structural script (`R a = |a|·h`, `b R = |b|·h`, `R R̃ = |R|²·1`, `field_simp`) on
  object hypotheses; three `_coord` lemmas deleted (the 𝒢₃ `versorFromVectors_mul_reverse_coord` /
  `_mul_inverse_coord` stay: `ProjectionRotation3D` still consumes them).
- `Trig.lean`: `cos_sq_add_sin_sq` (both grades) from `lagrange_property` + `normSq_nonneg` directly;
  `lagrange_property_coord` deleted (both grades). `Measures.normSq_wedge_eq_lagrange` likewise.
- `RotateComponents.sandwich_ahat` direct from the object carries; `sandwich_ahat_coord` deleted.
Lesson: the sqrt tier was never hard once the four object `√` lemmas existed — each conversion was the
coordinate script with `isVector_vec` replaced by the object hypothesis and `magnitude_sq_of_normSq_coord`
by `magnitude_sq_eq_normSq`. The "degree blow-up" tier (division by `normSq (f ∧ t)`) was not touched.

**Remaining (the open part of this task):** the `ProjectionRotation3D` scaffold (`projRotation_*_coord`,
`key_reverse_sq_coord`, `fhat_that_eq_reverse_mul_inverse_coord`, `normalizeVec_*_coord`,
`vec_mul_bisector_eq_coord`, the plane-projection `_coord`s — these divide by `normSq (f ∧ t)`, the
blow-up tier); `Sandwich` `sandwich_fixes_own_bivector/normal_coord`, `sandwich_comp_coord`, the 𝒢₃
`versorFromVectors_mul_reverse/inverse_coord`; `Projection3D` `reject_vec_eq_coord`,
`project_add_reject_coord`, `reject_eq_proj_normal_coord`, `project_eq_sub_reject_coord`;
`CrossStandardPosition` `cross_rot*_equivariant_coord`; `RotateComponents` `rotation_fixes_normal_coord`;
`TrigEquiv` `sin_between_eq_abs_signed_vec_coord`; `Versor2D`/`Rotation3D` bisector `_coord`s; the `G3`
`vec`-literal leaves kept by Decision 1. Regenerate the live list with the command below.

## Prerequisite (done — see the work record)

Add an **object `magnitude`/`normalizeVec` lemma layer** so the sqrt tier has getter-native tools:
`normSq_nonneg {a} : 0 ≤ normSq a` (or per-grade), `magnitude_sq {a} (ha : IsVector a) : magnitude a ^ 2
= normSq a` as an object lemma (shaped like the existing `Normalize.magnitude_normalizeVec`), `R⁻¹ = R̃`
for unit versors (a one-liner on `mul_reverse_self_of_isEvenVersor`; see
`tasks/archive/2026/10/05/lean-unit-versors-rotors-sandwich-with-reverse.md` Q3), etc. Without these the conversions below just
re-derive sqrt facts inline each time.

## Targets (apply the recipes from the reference doc once the prereq exists)

`cos_sq_add_sin_sq` (Trig), `sin_between_eq_abs_signed_vec` (TrigEquiv), `reject_vec_eq` (Projection3D —
structural Hestenes split), CrossStandardPosition's cos/sin-parameterized equivariance (if desired), and
the two `ProjectionRotation2D/3D` files' scaffold + capstones (`key_reverse_sq`,
`fhat_that_eq_reverse_mul_inverse`, `magnitude_sq_of_normSq`, `normalizeVec_*`, the bisector lemmas,
`projRotation_eq_sandwich`/`_isometry`). Plus the Sandwich delicate capstones still on their bridge
(`sandwich_carries_from_to` G2+G3, `sandwich_fixes_own_bivector`/`_normal`, `sandwich_comp`).

The retained coordinate `_coord` leaves feeding these can only be deleted once their capstones are
converted — do it bottom-up, `make lean`-green each step, keeping an `eq_vec`-reconstruction fallback for
any that still resist.

## Current retained `_coord` scaffold (as of the 2026-10-04 sweep)

The sweep confirmed **no `_coord` is orphaned** — each still feeds a retained coordinate-core proof.
Regenerate the live list (and spot any that a future conversion orphans) from the repo root with:

```sh
cd proofs && for n in $(grep -rhoE '^(theorem|lemma|def) [A-Za-z0-9_]*_coord' --include='*.lean' GacalcProofs/ \
  | sed -E 's/^(theorem|lemma|def) //' | sort -u); do
  echo "=== $n ==="; grep -rnE "\b$n\b" --include='*.lean' GacalcProofs/ | grep -vE ":[0-9]+:(theorem|lemma|def) $n"
done
```

The retained set at archive time, by cluster: **Sandwich** `versorFromVectors_mul_reverse_coord` (G2+G3),
`sandwich_carries_from_to_coord` (G2+G3), `versorFromVectors_mul_inverse_coord`,
`sandwich_fixes_own_bivector_coord`, `sandwich_fixes_own_normal_coord`, `sandwich_comp_coord`; **G3**
`wedge_self_vec_coord`, `dot_self_vec_eq_normSq_coord`, `mul_vec_self_coord` (feed Projection*,
StandardPosition, ProjectionRotation*); **Projection3D** `reject_vec_eq_coord`, `project_add_reject_coord`,
`reject_eq_proj_normal_coord`, `project_eq_sub_reject_coord`; **Trig** `lagrange_property_coord` (G2+G3,
feeds `cos_sq_add_sin_sq`); **CrossStandardPosition** `cross_rot{XY,XZ,YZ}_equivariant_coord`;
**Rotation3D/Versor2D** `versor_mul_from_eq_bisector_coord`, `from_mul_versor_eq_bisector_coord`;
**RotateComponents** `sandwich_ahat_coord`, `rotation_fixes_normal_coord`; **TrigEquiv**
`sin_between_eq_abs_signed_vec_coord`; and the whole **ProjectionRotation2D/3D** scaffold
(`key_reverse_sq_coord`, `fhat_that_eq_reverse_mul_inverse_coord`, `magnitude_sq_of_normSq_coord`,
`projRotation_*_coord`, `normalizeVec_*_coord`, `vec_mul_bisector_eq_coord`, the plane-projection `_coord`,
etc.) plus the form-D `vec`-literal bridges kept by Decision 1.

## See also

- `tasks/archive/2026/10/04/lean-object-in-getters-out-proof-style.md` — the completed sweep, per-file
  record, and the decision to retain this tier.
- `tasks/reference/lean-ga-proof-architecture.md` — the getter-native norm, the atomic-`normSq`-leaf
  recipe, the clean-`^2`-denominator derivation, and the "paths that don't work" dead-ends.
- `tasks/archive/2026/10/05/lean-unit-versors-rotors-sandwich-with-reverse.md` — the unit-versor `R⁻¹ = R̃` layer (overlaps
  the prerequisite).
