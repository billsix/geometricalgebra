import GacalcProofs.G3
import GacalcProofs.Projection2D

/-! # Sine and cosine from the inner and outer products

    The sin/cos characterization of two vectors, read off the **inner and outer products** (no angle
    computed): `cos = (a·b)/(|a||b|)`, `sin = |a∧b|/(|a||b|)`, with `cos² + sin² = 1` — the leaf
    property the higher (rotation/angle) proofs build on. `cos² + sin² = 1` is exactly Lagrange's
    identity in coordinate-free form (`lagrange_property`: `(a·b)² + |a∧b|² = |a|²|b|²`). Proved for
    both 𝒢₂ and 𝒢₃. See `tasks/lean-proofs-make-coordinate-free.md`. -/

namespace GacalcProofs.G3

/-- **Lagrange, as a property** (coordinate-free): `(a·b)² + |a∧b|² = |a|²|b|²` — the inner-square plus
    the outer-square is the product of the squared magnitudes. This is `cos² + sin² = 1` scaled. -/
theorem lagrange_property (a1 a2 a3 b1 b2 b3 : ℝ) :
    dot (vec a1 a2 a3) (vec b1 b2 b3) ^ 2 + normSq (wedge (vec a1 a2 a3) (vec b1 b2 b3))
      = normSq (vec a1 a2 a3) * normSq (vec b1 b2 b3) := by
  simp only [dot, normSq, wedge, mul, reverse, vec]; ring

/-- `cos` of the angle between two vectors, from the inner product: `(a·b)/(|a||b|)`. -/
noncomputable def cos_between (a b : G3) : ℝ := dot a b / (magnitude a * magnitude b)

/-- `sin` of the angle between two vectors, from the outer product: `|a∧b|/(|a||b|)` (≥ 0). -/
noncomputable def sin_between (a b : G3) : ℝ := magnitude (wedge a b) / (magnitude a * magnitude b)

/-- **`cos² + sin² = 1`** — the Pythagorean identity for the sin/cos read off the inner/outer products,
    a corollary of `lagrange_property`. For nondegenerate vectors (`|a|², |b|² ≠ 0`). -/
theorem cos_sq_add_sin_sq (a1 a2 a3 b1 b2 b3 : ℝ)
    (ha : normSq (vec a1 a2 a3) ≠ 0) (hb : normSq (vec b1 b2 b3) ≠ 0) :
    cos_between (vec a1 a2 a3) (vec b1 b2 b3) ^ 2
      + sin_between (vec a1 a2 a3) (vec b1 b2 b3) ^ 2 = 1 := by
  have hna : (0 : ℝ) ≤ normSq (vec a1 a2 a3) := by rw [normSq_vec]; positivity
  have hnb : (0 : ℝ) ≤ normSq (vec b1 b2 b3) := by rw [normSq_vec]; positivity
  have hnw : (0 : ℝ) ≤ normSq (wedge (vec a1 a2 a3) (vec b1 b2 b3)) := by
    rw [normSq_wedge_vec]; positivity
  have hla := lagrange_property a1 a2 a3 b1 b2 b3
  simp only [cos_between, sin_between, magnitude, div_pow, mul_pow, Real.sq_sqrt hna,
             Real.sq_sqrt hnb, Real.sq_sqrt hnw]
  rw [← add_div, hla]
  exact div_self (mul_ne_zero ha hb)

/-- **A rotation preserves the cosine of the angle** between two vectors:
    `cos(R u R⁻¹, R v R⁻¹) = cos(u, v)`. From `sandwich_preserves_dot` (the numerator) and
    `magnitude_sandwich_vec` (the two denominators). Since `cos` determines the unoriented angle, the
    rotation preserves the angle — coordinate-free, straight off the inner-product leaves. -/
theorem sandwich_preserves_cos (s c12 c13 c23 u1 u2 u3 v1 v2 v3 : ℝ)
    (hr : s ^ 2 + c12 ^ 2 + c13 ^ 2 + c23 ^ 2 ≠ 0) :
    cos_between (sandwich (evenVersor s c12 c13 c23) (vec u1 u2 u3))
                (sandwich (evenVersor s c12 c13 c23) (vec v1 v2 v3))
      = cos_between (vec u1 u2 u3) (vec v1 v2 v3) := by
  simp only [cos_between]
  rw [sandwich_preserves_dot s c12 c13 c23 u1 u2 u3 v1 v2 v3 hr,
      magnitude_sandwich_vec s c12 c13 c23 u1 u2 u3 hr,
      magnitude_sandwich_vec s c12 c13 c23 v1 v2 v3 hr]

end GacalcProofs.G3

namespace GacalcProofs.G2

/-- **Lagrange, as a property** (coordinate-free), in 𝒢₂. -/
theorem lagrange_property (a1 a2 b1 b2 : ℝ) :
    dot (vec a1 a2) (vec b1 b2) ^ 2 + normSq (wedge (vec a1 a2) (vec b1 b2))
      = normSq (vec a1 a2) * normSq (vec b1 b2) := by
  simp only [dot, normSq, wedge, mul, reverse, vec]; ring

/-- `cos` from the inner product (2D). -/
noncomputable def cos_between (a b : G2) : ℝ := dot a b / (magnitude a * magnitude b)

/-- `sin` from the outer product (2D). -/
noncomputable def sin_between (a b : G2) : ℝ := magnitude (wedge a b) / (magnitude a * magnitude b)

/-- **`cos² + sin² = 1`** in 𝒢₂, from `lagrange_property`. -/
theorem cos_sq_add_sin_sq (a1 a2 b1 b2 : ℝ)
    (ha : normSq (vec a1 a2) ≠ 0) (hb : normSq (vec b1 b2) ≠ 0) :
    cos_between (vec a1 a2) (vec b1 b2) ^ 2 + sin_between (vec a1 a2) (vec b1 b2) ^ 2 = 1 := by
  have hna : (0 : ℝ) ≤ normSq (vec a1 a2) := by rw [normSq_vec]; positivity
  have hnb : (0 : ℝ) ≤ normSq (vec b1 b2) := by rw [normSq_vec]; positivity
  have hnw : (0 : ℝ) ≤ normSq (wedge (vec a1 a2) (vec b1 b2)) := by
    rw [normSq_wedge_vec]; positivity
  have hla := lagrange_property a1 a2 b1 b2
  simp only [cos_between, sin_between, magnitude, div_pow, mul_pow, Real.sq_sqrt hna,
             Real.sq_sqrt hnb, Real.sq_sqrt hnw]
  rw [← add_div, hla]
  exact div_self (mul_ne_zero ha hb)

/-- **A rotation preserves the cosine of the angle** between two vectors (2D):
    `cos(R u R⁻¹, R v R⁻¹) = cos(u, v)`. -/
theorem sandwich_preserves_cos (s c u1 u2 v1 v2 : ℝ) (hr : s ^ 2 + c ^ 2 ≠ 0) :
    cos_between (sandwich (evenVersor s c) (vec u1 u2)) (sandwich (evenVersor s c) (vec v1 v2))
      = cos_between (vec u1 u2) (vec v1 v2) := by
  simp only [cos_between]
  rw [sandwich_preserves_dot s c u1 u2 v1 v2 hr, magnitude_sandwich_vec s c u1 u2 hr,
      magnitude_sandwich_vec s c v1 v2 hr]

end GacalcProofs.G2
