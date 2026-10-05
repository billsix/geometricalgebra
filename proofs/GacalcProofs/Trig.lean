import GacalcProofs.G3
import GacalcProofs.Projection2D

/-! # Sine and cosine from the inner and outer products

    The sin/cos characterization of two vectors, read off the **inner and outer products** (no angle
    computed): `cos = (a·b)/(|a||b|)`, `sin = |a∧b|/(|a||b|)`, with `cos² + sin² = 1` — the leaf
    property the higher (rotation/angle) proofs build on. `cos² + sin² = 1` is exactly Lagrange's
    identity in coordinate-free form (reference: `Lagrange.lean`) (`lagrange_property`: `(a·b)² + |a∧b|² = |a|²|b|²`). Proved for
    both 𝒢₂ and 𝒢₃. See `tasks/reference/lean-ga-proof-architecture.md`. -/

namespace GacalcProofs.G3

/-- **Lagrange, as a property** (object form): `(a·b)² + |a∧b|² = |a|²|b|²` for vectors `a`, `b`. -/
theorem lagrange_property {a b : G3} (ha : IsVector a) (hb : IsVector b) :
    dot a b ^ 2 + normSq (wedge a b) = normSq a * normSq b := by
  obtain ⟨_, ha12, ha13, ha23, ha123⟩ := ha
  obtain ⟨hbs, hb12, hb13, hb23, hb123⟩ := hb
  simp only [dot, normSq, wedge, mul, reverse, ha12, ha13, ha23, ha123,
             hbs, hb12, hb13, hb23, hb123]
  ring

/-- `cos` of the angle between two vectors, from the inner product: `(a·b)/(|a||b|)`. -/
noncomputable def cos_between (a b : G3) : ℝ := dot a b / (magnitude a * magnitude b)

/-- `sin` of the angle between two vectors, from the outer product: `|a∧b|/(|a||b|)` (≥ 0). -/
noncomputable def sin_between (a b : G3) : ℝ := magnitude (wedge a b) / (magnitude a * magnitude b)

/-- **`cos² + sin² = 1`** — the Pythagorean identity for the sin/cos read off the inner/outer products,
    a corollary of `lagrange_property`. For nondegenerate vectors (`|a|², |b|² ≠ 0`). -/
theorem cos_sq_add_sin_sq {a b : G3} (ha_isv : IsVector a) (hb_isv : IsVector b)
    (ha : normSq a ≠ 0) (hb : normSq b ≠ 0) :
    cos_between a b ^ 2 + sin_between a b ^ 2 = 1 := by
  have hla := lagrange_property ha_isv hb_isv
  simp only [cos_between, sin_between, magnitude, div_pow, mul_pow, Real.sq_sqrt (normSq_nonneg a),
             Real.sq_sqrt (normSq_nonneg b), Real.sq_sqrt (normSq_nonneg (wedge a b))]
  rw [← add_div, hla]
  exact div_self (mul_ne_zero ha hb)

/-- **A rotation preserves the cosine of the angle**: `cos(R u R⁻¹, R v R⁻¹) = cos(u, v)` for an even
    versor `R` with `|R|² ≠ 0` and ANY `u`, `v` (meaningful for vectors) — straight off the object
    dot/magnitude isometries. -/
theorem sandwich_preserves_cos {R : G3} (hR : IsEvenVersor R) (hr : normSq R ≠ 0) {u v : G3} :
    cos_between (sandwich R u) (sandwich R v) = cos_between u v := by
  simp only [cos_between]
  rw [sandwich_preserves_dot hR hr, magnitude_sandwich hR hr, magnitude_sandwich hR hr]

/-- **A rotation preserves the sine of the angle**: `sin(R u R⁻¹, R v R⁻¹) = sin(u, v)` for an even
    versor `R` with `|R|² ≠ 0` and ANY `u`, `v` (meaningful for vectors). The numerator `|u∧v|` is preserved by the
    outermorphism + bivector isometry; the denominators by `magnitude_sandwich`. -/
theorem sandwich_preserves_sin {R : G3} (hR : IsEvenVersor R) (hr : normSq R ≠ 0) {u v : G3} :
    sin_between (sandwich R u) (sandwich R v) = sin_between u v := by
  have hnum : magnitude (wedge (sandwich R u) (sandwich R v)) = magnitude (wedge u v) := by
    rw [sandwich_preserves_wedge hR hr]
    simp only [magnitude]
    rw [sandwich_preserves_normSq_of_wedge hR hr]
  simp only [sin_between]
  rw [hnum, magnitude_sandwich hR hr, magnitude_sandwich hR hr]

end GacalcProofs.G3

namespace GacalcProofs.G2

/-- **Lagrange, as a property** (object form, 2D): `(a·b)² + |a∧b|² = |a|²|b|²` for vectors `a`, `b`. -/
theorem lagrange_property {a b : G2} (ha : IsVector a) (hb : IsVector b) :
    dot a b ^ 2 + normSq (wedge a b) = normSq a * normSq b := by
  obtain ⟨has, ha12⟩ := ha
  obtain ⟨hbs, hb12⟩ := hb
  simp only [dot, normSq, wedge, mul, reverse, has, ha12, hbs, hb12]
  ring

/-- `cos` from the inner product (2D). -/
noncomputable def cos_between (a b : G2) : ℝ := dot a b / (magnitude a * magnitude b)

/-- `sin` from the outer product (2D). -/
noncomputable def sin_between (a b : G2) : ℝ := magnitude (wedge a b) / (magnitude a * magnitude b)

/-- **`cos² + sin² = 1`** in 𝒢₂, from `lagrange_property`. -/
theorem cos_sq_add_sin_sq {a b : G2} (ha_isv : IsVector a) (hb_isv : IsVector b)
    (ha : normSq a ≠ 0) (hb : normSq b ≠ 0) :
    cos_between a b ^ 2 + sin_between a b ^ 2 = 1 := by
  have hla := lagrange_property ha_isv hb_isv
  simp only [cos_between, sin_between, magnitude, div_pow, mul_pow, Real.sq_sqrt (normSq_nonneg a),
             Real.sq_sqrt (normSq_nonneg b), Real.sq_sqrt (normSq_nonneg (wedge a b))]
  rw [← add_div, hla]
  exact div_self (mul_ne_zero ha hb)

/-- **A rotation preserves the cosine of the angle** (2D): `cos(R u R⁻¹, R v R⁻¹) = cos(u, v)` for an
    even versor `R` with `|R|² ≠ 0` and ANY `u`, `v` (meaningful for vectors). -/
theorem sandwich_preserves_cos {R : G2} (hR : IsEvenVersor R) (hr : normSq R ≠ 0) {u v : G2} :
    cos_between (sandwich R u) (sandwich R v) = cos_between u v := by
  simp only [cos_between]
  rw [sandwich_preserves_dot hR hr, magnitude_sandwich hR hr, magnitude_sandwich hR hr]

/-- **A rotation preserves the sine of the angle** (2D): `sin(R u R⁻¹, R v R⁻¹) = sin(u, v)` for an
    even versor `R` with `|R|² ≠ 0` and ANY `u`, `v` (meaningful for vectors). -/
theorem sandwich_preserves_sin {R : G2} (hR : IsEvenVersor R) (hr : normSq R ≠ 0) {u v : G2} :
    sin_between (sandwich R u) (sandwich R v) = sin_between u v := by
  have hnum : magnitude (wedge (sandwich R u) (sandwich R v)) = magnitude (wedge u v) := by
    rw [sandwich_preserves_wedge hR hr]
    simp only [magnitude]
    rw [sandwich_preserves_normSq_of_wedge hR hr]
  simp only [sin_between]
  rw [hnum, magnitude_sandwich hR hr, magnitude_sandwich hR hr]

end GacalcProofs.G2
