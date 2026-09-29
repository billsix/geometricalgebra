import GacalcProofs.G2
import GacalcProofs.G3
import GacalcProofs.Versor2D
import GacalcProofs.AlgebraLaws

/-! # The versor sandwich is an isometry: it preserves lengths and angles (𝒢₂ pilot)

    The scale-invariant sandwich `R v R⁻¹` (with `R⁻¹ = R̃ / |R|²`) by an even versor `R` — the
    rotations of the plane — preserves the dot product, hence lengths and angles. Proved here in 𝒢₂
    for a general even versor (`evenVersor s c = s + c·e₁₂`, the elements of 𝒢₂'s even subalgebra ≅ ℂ);
    the 𝒢₃ versions follow the same shape (see `tasks/lean-proof-rotation-preserves-length.md` and
    `-angles.md`). Uses the magnitude-squared (`dot`) form throughout to stay `√`-free. -/
namespace GacalcProofs.G2

/-- The versor norm `|R|² = ⟨R R̃⟩₀`. For an even versor it is `s² + c²`. -/
noncomputable def normSq (a : G2) : ℝ := (mul a (reverse a)).s

/-- The inverse `R⁻¹ = R̃ / |R|²` (valid when `|R|² ≠ 0`). -/
noncomputable def inverse (a : G2) : G2 := smul (1 / normSq a) (reverse a)

/-- The scale-invariant versor sandwich `R v R⁻¹`. -/
noncomputable def sandwich (r v : G2) : G2 := mul (mul r v) (inverse r)

/-- An **even versor** `s + c·e₁₂` — an element of 𝒢₂'s even subalgebra (≅ ℂ), the rotations. -/
def evenVersor (s c : ℝ) : G2 := ⟨s, 0, 0, c⟩

/-- `|evenVersor s c|² = s² + c²`. -/
theorem normSq_evenVersor (s c : ℝ) : normSq (evenVersor s c) = s ^ 2 + c ^ 2 := by
  simp only [normSq, evenVersor, mul, reverse]; ring

/-- **The sandwich preserves the dot product** (hence angles): for an even versor `R` with
    `|R|² ≠ 0`, `(R u R⁻¹) · (R v R⁻¹) = u · v`. -/
theorem sandwich_preserves_dot (s c u1 u2 v1 v2 : ℝ) (hr : s ^ 2 + c ^ 2 ≠ 0) :
    dot (sandwich (evenVersor s c) (vec u1 u2)) (sandwich (evenVersor s c) (vec v1 v2))
      = dot (vec u1 u2) (vec v1 v2) := by
  simp only [dot, sandwich, inverse, normSq_evenVersor]
  simp only [evenVersor, mul, reverse, smul, vec]
  field_simp [hr]
  ring

/-- **The sandwich preserves length** (magnitude-squared form): for an even versor `R` with
    `|R|² ≠ 0`, `|R v R⁻¹|² = |v|²`. A corollary of `sandwich_preserves_dot` (`u = v`). -/
theorem sandwich_preserves_normSq_vec (s c v1 v2 : ℝ) (hr : s ^ 2 + c ^ 2 ≠ 0) :
    dot (sandwich (evenVersor s c) (vec v1 v2)) (sandwich (evenVersor s c) (vec v1 v2))
      = dot (vec v1 v2) (vec v1 v2) :=
  sandwich_preserves_dot s c v1 v2 v1 v2 hr

end GacalcProofs.G2

namespace GacalcProofs.G3

/-- The versor norm `|R|² = ⟨R R̃⟩₀`. For an even versor `s + B` it is `s² + |B|²`. -/
noncomputable def normSq (a : G3) : ℝ := (mul a (reverse a)).s

/-- The inverse `R⁻¹ = R̃ / |R|²` (valid when `|R|² ≠ 0`). -/
noncomputable def inverse (a : G3) : G3 := smul (1 / normSq a) (reverse a)

/-- The scale-invariant versor sandwich `R v R⁻¹`. -/
noncomputable def sandwich (r v : G3) : G3 := mul (mul r v) (inverse r)

/-- An **even versor** `s + c₁₂·e₁₂ + c₁₃·e₁₃ + c₂₃·e₂₃` — an element of 𝒢₃'s even subalgebra
    (≅ the quaternions), whose nonzero elements are exactly the rotations via `R v R⁻¹`. -/
def evenVersor (s c12 c13 c23 : ℝ) : G3 := ⟨s, 0, 0, 0, c12, c13, c23, 0⟩

/-- `|evenVersor s c₁₂ c₁₃ c₂₃|² = s² + c₁₂² + c₁₃² + c₂₃²`. -/
theorem normSq_evenVersor (s c12 c13 c23 : ℝ) :
    normSq (evenVersor s c12 c13 c23) = s ^ 2 + c12 ^ 2 + c13 ^ 2 + c23 ^ 2 := by
  simp only [normSq, evenVersor, mul, reverse]; ring

/-- **The sandwich preserves the dot product** (hence angles): for an even versor `R` with
    `|R|² ≠ 0`, `(R u R⁻¹) · (R v R⁻¹) = u · v`. -/
theorem sandwich_preserves_dot (s c12 c13 c23 u1 u2 u3 v1 v2 v3 : ℝ)
    (hr : s ^ 2 + c12 ^ 2 + c13 ^ 2 + c23 ^ 2 ≠ 0) :
    dot (sandwich (evenVersor s c12 c13 c23) (vec u1 u2 u3))
        (sandwich (evenVersor s c12 c13 c23) (vec v1 v2 v3))
      = dot (vec u1 u2 u3) (vec v1 v2 v3) := by
  simp only [dot, sandwich, inverse, normSq_evenVersor]
  simp only [evenVersor, mul, reverse, smul, vec]
  field_simp [hr]
  ring

/-- **The sandwich preserves length** (magnitude-squared form): for an even versor `R` with
    `|R|² ≠ 0`, `|R v R⁻¹|² = |v|²`. A corollary of `sandwich_preserves_dot` (`u = v`). -/
theorem sandwich_preserves_normSq_vec (s c12 c13 c23 v1 v2 v3 : ℝ)
    (hr : s ^ 2 + c12 ^ 2 + c13 ^ 2 + c23 ^ 2 ≠ 0) :
    dot (sandwich (evenVersor s c12 c13 c23) (vec v1 v2 v3))
        (sandwich (evenVersor s c12 c13 c23) (vec v1 v2 v3))
      = dot (vec v1 v2 v3) (vec v1 v2 v3) :=
  sandwich_preserves_dot s c12 c13 c23 v1 v2 v3 v1 v2 v3 hr

end GacalcProofs.G3
