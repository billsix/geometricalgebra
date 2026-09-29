import GacalcProofs.G2
import GacalcProofs.G3
import GacalcProofs.Versor2D
import GacalcProofs.Rotation3D
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

/-- `R R̃ = |R|²·1` for the from-vectors versor (even, so `R R̃` is a pure scalar). -/
theorem versorFromVectors_mul_reverse (a1 a2 b1 b2 : ℝ) :
    mul (versorFromVectors (vec a1 a2) (vec b1 b2))
        (reverse (versorFromVectors (vec a1 a2) (vec b1 b2)))
      = smul (normSq (versorFromVectors (vec a1 a2) (vec b1 b2))) one := by
  simp only [normSq, versorFromVectors, mul, reverse, add, smul, one, vec]
  ext <;> ring

/-- **The versor from `a, b` carries `a` to `b`** in 𝒢₂: `R a R⁻¹ = (|a|/|b|)·b` (angle-free) — the
    2D twin of `Rotation3D`'s `sandwich_carries_from_to`, same assembly. In 𝒢₂ the plane is the whole
    space, so this is the whole rotation. Needs `|b| ≠ 0`, `|R|² ≠ 0`. -/
theorem sandwich_carries_from_to (a1 a2 b1 b2 : ℝ)
    (hb : mag (vec b1 b2) ≠ 0)
    (hr : normSq (versorFromVectors (vec a1 a2) (vec b1 b2)) ≠ 0) :
    sandwich (versorFromVectors (vec a1 a2) (vec b1 b2)) (vec a1 a2)
      = smul (mag (vec a1 a2) / mag (vec b1 b2)) (vec b1 b2) := by
  have hbis : bisector (vec a1 a2) (vec b1 b2)
      = smul (1 / mag (vec b1 b2)) (mul (vec b1 b2) (versorFromVectors (vec a1 a2) (vec b1 b2))) := by
    rw [from_mul_versor_eq_bisector, GacalcProofs.G2.smul_smul, one_div_mul_cancel hb,
        GacalcProofs.G2.one_smul]
  have hkey : mul (bisector (vec a1 a2) (vec b1 b2))
                  (inverse (versorFromVectors (vec a1 a2) (vec b1 b2)))
      = smul (1 / mag (vec b1 b2)) (vec b1 b2) := by
    rw [hbis, GacalcProofs.G2.smul_mul, inverse, GacalcProofs.G2.mul_smul,
        GacalcProofs.G2.mul_assoc, versorFromVectors_mul_reverse, GacalcProofs.G2.mul_smul,
        GacalcProofs.G2.mul_one, GacalcProofs.G2.smul_smul, GacalcProofs.G2.smul_smul]
    congr 1
    field_simp
  rw [sandwich, versor_mul_from_eq_bisector, GacalcProofs.G2.smul_mul, hkey,
      GacalcProofs.G2.smul_smul, mul_one_div]

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

/-- `R R̃ = |R|²·1` for the from-vectors versor (it is even — scalar + bivector — so `R R̃` is a
    pure scalar). Proved by `ext <;> ring`: the odd/bivector components vanish structurally, with no
    `√` fact needed (the magnitudes appear only in the scalar coefficient). -/
theorem versorFromVectors_mul_reverse (a1 a2 a3 b1 b2 b3 : ℝ) :
    mul (versorFromVectors (vec a1 a2 a3) (vec b1 b2 b3))
        (reverse (versorFromVectors (vec a1 a2 a3) (vec b1 b2 b3)))
      = smul (normSq (versorFromVectors (vec a1 a2 a3) (vec b1 b2 b3))) one := by
  simp only [normSq, versorFromVectors, mul, reverse, add, smul, one, vec]
  ext <;> ring

/-- **The from-vectors versor is invertible: `R R⁻¹ = 1`** (for `|R|² ≠ 0`). Uses `R R̃ = |R|²·1`,
    `mul_smul`, `smul_smul`, and `1/|R|² · |R|² = 1`. -/
theorem versorFromVectors_mul_inverse (a1 a2 a3 b1 b2 b3 : ℝ)
    (hr : normSq (versorFromVectors (vec a1 a2 a3) (vec b1 b2 b3)) ≠ 0) :
    mul (versorFromVectors (vec a1 a2 a3) (vec b1 b2 b3))
        (inverse (versorFromVectors (vec a1 a2 a3) (vec b1 b2 b3))) = one := by
  rw [inverse, GacalcProofs.G3.mul_smul, versorFromVectors_mul_reverse,
      GacalcProofs.G3.smul_smul, one_div_mul_cancel hr]
  simp only [smul, one]; ext <;> ring

/-- **The versor from `a, b` carries `a` to `b`**: `R a R⁻¹ = (|a|/|b|)·b` (angle-free). The
    scale-invariant sandwich sends the from-vector to the to-vector, scaled to length `|a|` (the
    rotation preserves length, so `a` of length `|a|` lands on `b̂` at length `|a|`). Assembled from
    `R a = |a|·h`, `b R = |b|·h`, `R R̃ = |R|²·1`, and `R R⁻¹ = 1`. Needs `|b| ≠ 0`, `|R|² ≠ 0`. -/
theorem sandwich_carries_from_to (a1 a2 a3 b1 b2 b3 : ℝ)
    (hb : mag (vec b1 b2 b3) ≠ 0)
    (hr : normSq (versorFromVectors (vec a1 a2 a3) (vec b1 b2 b3)) ≠ 0) :
    sandwich (versorFromVectors (vec a1 a2 a3) (vec b1 b2 b3)) (vec a1 a2 a3)
      = smul (mag (vec a1 a2 a3) / mag (vec b1 b2 b3)) (vec b1 b2 b3) := by
  -- The bisector expressed via `b R` (from `b R = |b|·h`, undone with |b| ≠ 0).
  have hbis : bisector (vec a1 a2 a3) (vec b1 b2 b3)
      = smul (1 / mag (vec b1 b2 b3))
             (mul (vec b1 b2 b3) (versorFromVectors (vec a1 a2 a3) (vec b1 b2 b3))) := by
    rw [from_mul_versor_eq_bisector, GacalcProofs.G3.smul_smul, one_div_mul_cancel hb,
        GacalcProofs.G3.one_smul]
  -- The heart: h R⁻¹ = (1/|b|)·b, via associativity + R R̃ = |R|² + mul_one.
  have hkey : mul (bisector (vec a1 a2 a3) (vec b1 b2 b3))
                  (inverse (versorFromVectors (vec a1 a2 a3) (vec b1 b2 b3)))
      = smul (1 / mag (vec b1 b2 b3)) (vec b1 b2 b3) := by
    rw [hbis, GacalcProofs.G3.smul_mul, inverse, GacalcProofs.G3.mul_smul,
        GacalcProofs.G3.mul_assoc, versorFromVectors_mul_reverse, GacalcProofs.G3.mul_smul,
        GacalcProofs.G3.mul_one, GacalcProofs.G3.smul_smul, GacalcProofs.G3.smul_smul]
    congr 1
    field_simp
  -- Assemble: sandwich R a = |a|·(h R⁻¹) = |a|·(1/|b|)·b = (|a|/|b|)·b.
  rw [sandwich, versor_mul_from_eq_bisector, GacalcProofs.G3.smul_mul, hkey,
      GacalcProofs.G3.smul_smul, mul_one_div]

/-- **A plane rotation leaves the orthogonal axis fixed** — the 3D fact with no 2D analogue. A versor
    in the e₁e₂ plane (`R = s + c₁₂·e₁₂`, `c₁₃ = c₂₃ = 0`) fixes the e₃ component: `R (z e₃) R⁻¹ = z e₃`
    (e₃ commutes with the plane bivector, so it slides through `R R⁻¹ = 1`). This is exactly the
    maintainer's "no effect on components orthogonal to the plane of rotation." -/
theorem sandwich_fixes_orthogonal (s c12 z : ℝ) (hr : s ^ 2 + c12 ^ 2 ≠ 0) :
    sandwich (evenVersor s c12 0 0) (vec 0 0 z) = vec 0 0 z := by
  have hd : normSq (evenVersor s c12 0 0) = s ^ 2 + c12 ^ 2 := by
    simp only [normSq, evenVersor, mul, reverse]; ring
  simp only [sandwich, inverse, hd]
  simp only [evenVersor, mul, reverse, smul, vec]
  ext <;> field_simp [hr] <;> ring

/-- **A plane rotation keeps in-plane vectors in the plane.** A versor in the e₁e₂ plane sends a
    vector `x e₁ + y e₂` to another vector in that plane — its e₃ component stays `0`. With
    `sandwich_fixes_orthogonal`, the plane and its normal are both invariant, so the 3D sandwich
    reduces to a 2D rotation in the plane. -/
theorem sandwich_plane_invariant (s c12 x y : ℝ) (hr : s ^ 2 + c12 ^ 2 ≠ 0) :
    (sandwich (evenVersor s c12 0 0) (vec x y 0)).c3 = 0 := by
  have hd : normSq (evenVersor s c12 0 0) = s ^ 2 + c12 ^ 2 := by
    simp only [normSq, evenVersor, mul, reverse]; ring
  simp only [sandwich, inverse, hd]
  simp only [evenVersor, mul, reverse, smul, vec]
  field_simp [hr]
  ring

/-- The sandwich is **linear** in the rotated vector: it distributes over addition. -/
theorem sandwich_add (r u v : G3) : sandwich r (add u v) = add (sandwich r u) (sandwich r v) := by
  simp only [sandwich]; rw [GacalcProofs.G3.mul_add, GacalcProofs.G3.add_mul]

/-- The sandwich is **linear** in the rotated vector: it pulls out scalars. -/
theorem sandwich_smul (k : ℝ) (r v : G3) : sandwich r (smul k v) = smul k (sandwich r v) := by
  simp only [sandwich]; rw [GacalcProofs.G3.mul_smul, GacalcProofs.G3.smul_mul]

/-! ### Composition: rotations compose by multiplying versors -/

/-- **Reverse is an anti-automorphism:** `(a b)~ = b~ a~`. General (no evenness needed). -/
theorem reverse_mul (a b : G3) : reverse (mul a b) = mul (reverse b) (reverse a) := by
  simp only [reverse, mul]; ext <;> ring

/-- **The versor norm is multiplicative:** `|R₁ R₂|² = |R₁|² |R₂|²` for even versors (the norm on
    𝒢₃'s even subalgebra ≅ the quaternions). -/
theorem normSq_mul (s1 p1 q1 t1 s2 p2 q2 t2 : ℝ) :
    normSq (mul (evenVersor s1 p1 q1 t1) (evenVersor s2 p2 q2 t2))
      = normSq (evenVersor s1 p1 q1 t1) * normSq (evenVersor s2 p2 q2 t2) := by
  simp only [normSq, evenVersor, mul, reverse]; ring

/-- **Inverse of a product:** `(R₁ R₂)⁻¹ = R₂⁻¹ R₁⁻¹` for even versors (`|R₁|², |R₂|² ≠ 0`). Uses the
    anti-automorphism of reverse and multiplicativity of the norm. -/
theorem inverse_mul (s1 p1 q1 t1 s2 p2 q2 t2 : ℝ)
    (h1 : normSq (evenVersor s1 p1 q1 t1) ≠ 0) (h2 : normSq (evenVersor s2 p2 q2 t2) ≠ 0) :
    inverse (mul (evenVersor s1 p1 q1 t1) (evenVersor s2 p2 q2 t2))
      = mul (inverse (evenVersor s2 p2 q2 t2)) (inverse (evenVersor s1 p1 q1 t1)) := by
  simp only [inverse, reverse_mul, normSq_mul, GacalcProofs.G3.smul_mul,
             GacalcProofs.G3.mul_smul, GacalcProofs.G3.smul_smul]
  congr 1
  field_simp

/-- **Rotations compose by multiplying versors:** `(R₁ R₂) v (R₁ R₂)⁻¹ = R₁ (R₂ v R₂⁻¹) R₁⁻¹`, i.e.
    applying the sandwich by `R₂` then by `R₁` equals the single sandwich by the product `R₁ R₂`.
    (For even versors with nonzero norm; `inverse_mul` + associativity.) -/
theorem sandwich_comp (s1 p1 q1 t1 s2 p2 q2 t2 : ℝ) (v : G3)
    (h1 : normSq (evenVersor s1 p1 q1 t1) ≠ 0) (h2 : normSq (evenVersor s2 p2 q2 t2) ≠ 0) :
    sandwich (mul (evenVersor s1 p1 q1 t1) (evenVersor s2 p2 q2 t2)) v
      = sandwich (evenVersor s1 p1 q1 t1) (sandwich (evenVersor s2 p2 q2 t2) v) := by
  simp only [sandwich]
  rw [inverse_mul s1 p1 q1 t1 s2 p2 q2 t2 h1 h2]
  simp only [GacalcProofs.G3.mul_assoc]

end GacalcProofs.G3
