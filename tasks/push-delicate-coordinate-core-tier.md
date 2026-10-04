# Push the delicate coordinate-core tier to object/getter form (optional)

**Status:** proposed — needs go-ahead (spun off 2026-10-04 from the completed object-in-getters sweep,
`tasks/archive/2026/10/04/lean-object-in-getters-out-proof-style.md`)
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
  and nonnegativity side-conditions. There is currently **no object `normSq_nonneg` / `magnitude`
  lemma layer** — that's the prerequisite (see below).
- **divide-by-`normSq(a∧b)` (degree blowup).** The plane-projection family (`reject`/`project_onto`
  onto `wedge a b`) divides by `normSq(a∧b)`, which is **quadratic** in `a,b`; `field_simp` on it
  cross-multiplies to degree-8 and times out. The `_coord` form exists precisely to prove these on a
  **literal bivector** (`bivector p q r`, degree 1) and instantiate — the deliberate blowup-avoidance.
- **delicate `calc`/`set` capstones.** `projRotation_eq_sandwich`/`_isometry`, `key_reverse_sq`, the
  bisector lemmas, `sandwich_carries_from_to`, `sandwich_fixes_*`, `sandwich_comp` — assembled from the
  sqrt/magnitude scaffold via `calc`/`set`/`rw` chains.

## Prerequisite (do this first)

Add an **object `magnitude`/`normalizeVec` lemma layer** so the sqrt tier has getter-native tools:
`normSq_nonneg {a} : 0 ≤ normSq a` (or per-grade), `magnitude_sq {a} (ha : IsVector a) : magnitude a ^ 2
= normSq a` as an object lemma, `magnitude_normalizeVec`, `R⁻¹ = R̃` for unit versors (overlaps
`tasks/lean-unit-versors-rotors-sandwich-with-reverse.md`), etc. Without these the conversions below just
re-derive sqrt facts inline each time.

## Targets (apply the recipes from the reference doc once the prereq exists)

`cos_sq_add_sin_sq` (Trig), `sin_between_eq_abs_signed_vec` (TrigEquiv), `reject_vec_eq` (Projection3D —
structural Hestenes split), CrossStandardPosition's cos/sin-parameterized equivariance (if desired), and
the two `ProjectionRotation2D/3D` files' scaffold + capstones (`key_reverse_sq`,
`fhat_that_eq_reverse_mul_inverse`, `magnitude_sq_of_normSq`, `normalizeVec_*`, the bisector lemmas,
`projRotation_eq_sandwich`/`_isometry`). Plus the Sandwich delicate capstones still on their bridge
(`sandwich_carries_from_to` G2+G3, `sandwich_fixes_own_bivector`/`_normal`, `sandwich_comp`).

The retained coordinate `_coord` leaves feeding these (listed in the archived parent task) can only be
deleted once their capstones are converted — do it bottom-up, `make lean`-green each step, keeping an
`eq_vec`-reconstruction fallback for any that still resist.

## See also

- `tasks/archive/2026/10/04/lean-object-in-getters-out-proof-style.md` — the completed sweep, per-file
  record, and the decision to retain this tier.
- `tasks/reference/lean-ga-proof-architecture.md` — the getter-native norm, the atomic-`normSq`-leaf
  recipe, the clean-`^2`-denominator derivation, and the "paths that don't work" dead-ends.
- `tasks/lean-unit-versors-rotors-sandwich-with-reverse.md` — the unit-versor `R⁻¹ = R̃` layer (overlaps
  the prerequisite).
