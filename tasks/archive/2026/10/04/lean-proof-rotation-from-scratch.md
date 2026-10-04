# Lean proof — rotation from scratch (sin/cos → geometric product → dot & wedge)

**Part of:** `tasks/archive/2026/10/04/investigate-lean-proofs-for-ga.md` (the foundation step).
**Status:** DONE 2026-10-04, archived 2026-10-04 (`make lean` green). **Priority:** 7. **Difficulty:** 8.
**Archived together with** `tasks/archive/2026/10/04/rename-rotor-to-versor.md` (the maintainer's coupling:
both grew from "a rotor is really a unit versor").
**Durable record:** `tasks/reference/lean-ga-proof-architecture.md` (the versor layer, the leaf/structural
technique, inventory of `Rotation2D`/`Rotation3D`/`Versor2D`/`Sandwich`/`RotateComponents`/`MathlibBridge`,
"Program decisions"); `tasks/reference/unit-bivector-and-rotors.md` (the rotor math);
`tasks/reference/reduction-to-standard-position.md` (the complementary route P).

## BLUF

The book's foundational derivation was formalized from scratch and bridged to Mathlib: sine/cosine →
rotation → the geometric product → dot and wedge as its parts, in 2D; the angle-free 3D versor from two
vectors and its sandwich (carries `a→b`, isometry, fixes the orthogonal complement, composes by versor
product); and finally the equivalence to the general case — the from-scratch `rot θ` IS Mathlib's
`Orientation.rotation θ` on the oriented plane ℂ, and so is the 2D versor sandwich.

## What was done (chronological)

- **2026-09-28, 2D core** (`Rotation2D.lean`): `rot θ` on pairs from sin/cos, `rot_add` (angles add),
  `rot_normSq`; `rotor θ = cos θ + sin θ·e₁₂` and `vec_mul_rotor` (the product enacts rotation);
  `uvec_mul_uvec` (the product of two unit vectors is the rotor of the angle between them) with
  `uvec_dot`/`uvec_wedge` (dot = cos, wedge = sin); the general-vector framing `polar`/`scale`/`rot_polar`/
  `rot_from_to` (`b = (|b|/|a|)·rot(φ_b − φ_a) a`) and `rotorFromTo_carry`. Representation decision: the
  coordinate struct `G2` with basis blades as genuine elements (not Mathlib `CliffordAlgebra`), mapping
  to Mathlib only for equivalence (resolved 2026-09-28; the Wieser & Song formalization was the model).
- **2026-09-29, angle-free 3D** (`Rotation3D.lean`, `Sandwich.lean`, `Projection3D.lean`): the maintainer
  redirected the 3D sandwich to mirror `versor_from_vectors` — no trig, the half angle implicit in the
  vectors (an angle-parameterized attempt was abandoned). `bisector`, `versorFromVectors`,
  `versor_mul_from_eq_bisector` (`R·a = |a|·h`) and `from_mul_versor_eq_bisector`; `vec_mul_perp` and
  `plane_eq_wedge` (the plane `a(b − proj_a b) = a∧b`); the sandwich infrastructure and isometry
  (`sandwich_preserves_dot`, length), `sandwich_fixes_orthogonal`/`sandwich_plane_invariant`; the capstone
  `sandwich_carries_from_to` (`R a R⁻¹ = (|a|/|b|)·b`); and the composition story `sandwich_comp` with
  `reverse_mul`/`normSq_mul`/`inverse_mul`. The optional "`h` genuinely bisects the angle" lemma was
  analyzed (Mathlib's unoriented-angle lemmas suffice) and not pursued.
- **2026-10-04, the Mathlib bridge** (`MathlibBridge.lean`): `toC` reads a pair as a complex number;
  `toC_rot` (`toC (rot θ v) = Complex.orientation.rotation θ (toC v)`, via `Orientation.rotation_apply`
  and `Complex.rightAngleRotation`, i.e. multiplication by `I`, with the local instance
  `Fact (finrank ℝ ℂ = 2)`); `toC_rot_rot` (composition); and `versor_sandwich_eq_rotation` — the
  from-scratch rotor `R v R̃`, `R = cos(θ/2) − sin(θ/2)·e₁₂`, read as a complex number, is Mathlib's
  rotation by exactly `θ` (via `sandwich_versor`). ℂ was chosen over `EuclideanSpace ℝ (Fin 2)` because
  `Complex.orientation`'s right-angle rotation is a one-line simp lemma.
- The from-rotation derivation of dot/wedge was declared discharged by `uvec_mul_uvec`/`uvec_dot`/
  `uvec_wedge` (maintainer, 2026-10-04).

## Decisions

- Route V (versor sandwich, product-based) and route P (project/reject via standard position,
  non-circular) are kept distinct; this task is route V.
- gacalc rotates with the inverse sandwich `R v R⁻¹` (scale-invariant), the textbook `R v R̃` needs a unit
  rotor; both agree when `R` is unit — which is why the general object was renamed "versor"
  (`rename-rotor-to-versor`).
