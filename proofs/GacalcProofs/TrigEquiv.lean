import GacalcProofs.Trig
import GacalcProofs.Rotation2D
import GacalcProofs.Versor2D

/-! # Trig equivalence: property-form ↔ angle-form, and the signed 2D sine (𝒢₂)

    Ties the two characterizations of sine/cosine that already live in the proofs:

    * the **property form** (`GacalcProofs.G2.cos_between` / `sin_between`, Trig.lean) — sin/cos read
      off the inner/outer products, `cos = (a·b)/(|a||b|)`, `sin = |a∧b|/(|a||b|)` (the latter
      UNSIGNED, the Python `abs_sin`); and
    * the **angle form** (`uvec_dot` / `uvec_wedge`, Rotation.lean) — for unit vectors at angles
      `α, β`, `(uvec α · uvec β) = cos (β−α)` and `(uvec α ∧ uvec β).c12 = sin (β−α)`.

    It also gives the **signed** 2D sine (the Python `g2.Vector.sine`, `(a∧b).c12 / (|a||b|)`) a Lean
    definition and shows the unsigned `sin_between` is its absolute value — mirroring the Python pair
    `abs_sin` (unsigned) / `sine` (signed), `abs(sine) == abs_sin`.

    The *fixed-grade = graded-part* half of Phase 4 needs no new theorem here: that dot is the grade-0
    part and wedge the grade-2 part of the product is already `GacalcProofs.G2.vec_mul` /
    `mul_eq_dot_add_wedge`. See `tasks/reference/lean-ga-proof-architecture.md`. -/

namespace GacalcProofs

open Real

/-- A unit vector `uvec α` has magnitude 1 (from `cos²+sin² = 1`). -/
theorem uvec_magnitude (α : ℝ) : G2.magnitude (uvec α) = 1 := by
  simp only [uvec_eq_vec, G2.magnitude, G2.normSq_vec, cos_sq_add_sin_sq, Real.sqrt_one]

/-- **`cos_between` of two unit vectors is the angle cosine** — ties the property-form
    `G2.cos_between` to the angle form `uvec_dot`. -/
theorem cos_between_uvec (α β : ℝ) :
    G2.cos_between (uvec α) (uvec β) = cos (β - α) := by
  simp only [G2.cos_between, uvec_magnitude, mul_one, div_one, G2.dot]
  exact uvec_dot α β

/-- The **signed** 2D sine of the angle from `a` to `b` (the Python `g2.Vector.sine`): the e₁₂
    coefficient of the wedge over the magnitudes. Sign = turn direction (swapping `a`, `b` negates it);
    the unsigned companion is `G2.sin_between` (the Python `abs_sin`). -/
noncomputable def signed_sin_between (a b : G2) : ℝ :=
  (G2.wedge a b).c12 / (G2.magnitude a * G2.magnitude b)

/-- **The signed sine of two unit vectors is the angle sine** `sin (β−α)` — ties the signed 2D sine
    to the angle form `uvec_wedge`. -/
theorem signed_sin_between_uvec (α β : ℝ) :
    signed_sin_between (uvec α) (uvec β) = sin (β - α) := by
  rw [signed_sin_between, uvec_magnitude α, uvec_magnitude β, mul_one, div_one]
  simp only [uvec_eq_vec, G2.wedge, G2.vec, sin_sub]
  ring

/-- **The unsigned `sin_between` is the absolute value of the signed sine**, for any two vectors —
    the Lean mirror of the Python relation `abs(sine) == abs_sin`. In 𝒢₂ the wedge of two vectors is a
    pure bivector, so its magnitude is `|c12|`. -/
theorem sin_between_eq_abs_signed_vec (a1 a2 b1 b2 : ℝ) :
    G2.sin_between (G2.vec a1 a2) (G2.vec b1 b2)
      = |signed_sin_between (G2.vec a1 a2) (G2.vec b1 b2)| := by
  have hden : (0 : ℝ) ≤ G2.magnitude (G2.vec a1 a2) * G2.magnitude (G2.vec b1 b2) := by
    simp only [G2.magnitude]; positivity
  have hw : G2.magnitude (G2.wedge (G2.vec a1 a2) (G2.vec b1 b2))
      = |(G2.wedge (G2.vec a1 a2) (G2.vec b1 b2)).c12| := by
    have hnsq : G2.normSq (G2.wedge (G2.vec a1 a2) (G2.vec b1 b2))
        = (G2.wedge (G2.vec a1 a2) (G2.vec b1 b2)).c12 ^ 2 := by
      simp only [G2.normSq, G2.wedge, G2.vec, G2.mul, G2.reverse]; ring
    rw [G2.magnitude, hnsq, Real.sqrt_sq_eq_abs]
  rw [G2.sin_between, hw, signed_sin_between, abs_div, abs_of_nonneg hden]

/-- Corollary: for unit vectors the unsigned `sin_between` is `|sin (β−α)|`. -/
theorem sin_between_uvec (α β : ℝ) :
    G2.sin_between (uvec α) (uvec β) = |sin (β - α)| := by
  rw [uvec_eq_vec α, uvec_eq_vec β, sin_between_eq_abs_signed_vec, ← uvec_eq_vec α,
      ← uvec_eq_vec β, signed_sin_between_uvec]

end GacalcProofs
