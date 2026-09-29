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

/-- The **squared magnitude** `|A|² = ⟨A Ã⟩₀` — the scalar part of `A` times its reverse (Hestenes &
    Sobczyk p.13 eq 1.49, gacalc `magnitude_squared`; `⟨AÃ⟩ = ⟨ÃA⟩` since the scalar part is symmetric).
    For an even versor it is `s² + c²`. -/
noncomputable def normSq (a : G2) : ℝ := (mul a (reverse a)).s

/-- The **magnitude** `|A| = √⟨A Ã⟩` (Hestenes p.13 eq 1.49, gacalc `magnitude`). Correct for all grades
    (unlike the vector-only `mag = √(A·A)`, which has the wrong sign for a bivector). -/
noncomputable def magnitude (a : G2) : ℝ := Real.sqrt (normSq a)

/-- On a vector, the general magnitude agrees with `mag` (`√⟨AÃ⟩ = √(A·A)`, since `reverse` fixes a
    vector). -/
theorem magnitude_vec (x y : ℝ) : magnitude (vec x y) = mag (vec x y) := by
  simp only [magnitude, mag, normSq, dot, reverse, mul, vec]; congr 1; ring

/-- **Leaf:** `|a|² = a₁² + a₂²` on a coordinate vector (2D). Reuse this instead of re-deriving inline. -/
theorem normSq_vec (a1 a2 : ℝ) : normSq (vec a1 a2) = a1 ^ 2 + a2 ^ 2 := by
  simp only [normSq, mul, reverse, vec]; ring

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

/-- `normSq` of a scalar multiple: `|k•a|² = k²|a|²` (2D). -/
theorem normSq_smul (k : ℝ) (a : G2) : normSq (smul k a) = k ^ 2 * normSq a := by
  simp only [normSq, smul, reverse, mul]; ring

/-- `|R v R̃|² = |R|⁴ |v|²` for an even versor and a vector (2D), pure polynomial `ring`. -/
theorem normSq_reverse_sandwich (s c v1 v2 : ℝ) :
    normSq (mul (mul (evenVersor s c) (vec v1 v2)) (reverse (evenVersor s c)))
      = normSq (evenVersor s c) ^ 2 * normSq (vec v1 v2) := by
  simp only [normSq, evenVersor, mul, reverse, vec]; ring

/-- **The sandwich preserves a vector's squared magnitude** (2D): `|R v R⁻¹|² = |v|²`. -/
theorem sandwich_preserves_normSq_of_vec (s c v1 v2 : ℝ) (hr : s ^ 2 + c ^ 2 ≠ 0) :
    normSq (sandwich (evenVersor s c) (vec v1 v2)) = normSq (vec v1 v2) := by
  have hr' : normSq (evenVersor s c) ≠ 0 := by rw [normSq_evenVersor]; exact hr
  rw [sandwich, inverse, GacalcProofs.G2.mul_smul, normSq_smul, normSq_reverse_sandwich]
  field_simp [hr']

/-- **The sandwich preserves a vector's magnitude** (2D): `|R v R⁻¹| = |v|`. -/
theorem magnitude_sandwich_vec (s c v1 v2 : ℝ) (hr : s ^ 2 + c ^ 2 ≠ 0) :
    magnitude (sandwich (evenVersor s c) (vec v1 v2)) = magnitude (vec v1 v2) := by
  simp only [magnitude]
  rw [sandwich_preserves_normSq_of_vec s c v1 v2 hr]

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

/-- The **squared magnitude** `|A|² = ⟨A Ã⟩₀` (Hestenes & Sobczyk p.13 eq 1.49, gacalc
    `magnitude_squared`). For an even versor `s + B` it is `s² + |B|²`. -/
noncomputable def normSq (a : G3) : ℝ := (mul a (reverse a)).s

/-- The **magnitude** `|A| = √⟨A Ã⟩` (Hestenes p.13 eq 1.49, gacalc `magnitude`). Correct for all grades
    (unlike the vector-only `mag = √(A·A)`). -/
noncomputable def magnitude (a : G3) : ℝ := Real.sqrt (normSq a)

/-- On a vector, the general magnitude agrees with the vector-only `mag`. (The def `magnitude` itself
    is for **all** grades; this bridge is vector-only only because `mag` is.) -/
theorem magnitude_vec (x y z : ℝ) : magnitude (vec x y z) = mag (vec x y z) := by
  simp only [magnitude, mag, normSq, dot, reverse, mul, vec]; congr 1; ring

/-- **Leaf:** `|a|² = a₁² + a₂² + a₃²` on a coordinate vector. Reuse instead of re-deriving inline. -/
theorem normSq_vec (a1 a2 a3 : ℝ) : normSq (vec a1 a2 a3) = a1 ^ 2 + a2 ^ 2 + a3 ^ 2 := by
  simp only [normSq, mul, reverse, vec]; ring

/-- **Leaf:** `|a∧b|² = (a₁b₂−a₂b₁)² + (a₁b₃−a₃b₁)² + (a₂b₃−a₃b₂)²` — the squared magnitude of the plane
    bivector of two vectors. Reuse instead of re-deriving inline. -/
theorem normSq_wedge_vec (a1 a2 a3 b1 b2 b3 : ℝ) :
    normSq (wedge (vec a1 a2 a3) (vec b1 b2 b3))
      = (a1 * b2 - a2 * b1) ^ 2 + (a1 * b3 - a3 * b1) ^ 2 + (a2 * b3 - a3 * b2) ^ 2 := by
  simp only [normSq, wedge, mul, reverse, vec]; ring

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

/-- `normSq` of a scalar multiple: `|k•a|² = k²|a|²`. -/
theorem normSq_smul (k : ℝ) (a : G3) : normSq (smul k a) = k ^ 2 * normSq a := by
  simp only [normSq, smul, reverse, mul]; ring

/-- **The reverse sandwich scales the norm by `|R|²`:** `|R v R̃|² = |R|⁴ |v|²` for an even versor and a
    vector (the versor norm is multiplicative through the reverse sandwich). Pure polynomial `ring`. -/
theorem normSq_reverse_sandwich (s c12 c13 c23 v1 v2 v3 : ℝ) :
    normSq (mul (mul (evenVersor s c12 c13 c23) (vec v1 v2 v3))
                (reverse (evenVersor s c12 c13 c23)))
      = normSq (evenVersor s c12 c13 c23) ^ 2 * normSq (vec v1 v2 v3) := by
  simp only [normSq, evenVersor, mul, reverse, vec]; ring

/-- **The sandwich preserves a vector's squared magnitude:** `|R v R⁻¹|² = |v|²` — the inverse sandwich
    is a rotation. Structural: factor the inverse's scalar (`mul_smul`), scale by `normSq_smul`, use
    `|R v R̃|² = |R|⁴|v|²`, then cancel `(1/|R|²)²·|R|⁴ = 1` (`|R|² ≠ 0`). -/
theorem sandwich_preserves_normSq_of_vec (s c12 c13 c23 v1 v2 v3 : ℝ)
    (hr : s ^ 2 + c12 ^ 2 + c13 ^ 2 + c23 ^ 2 ≠ 0) :
    normSq (sandwich (evenVersor s c12 c13 c23) (vec v1 v2 v3)) = normSq (vec v1 v2 v3) := by
  have hr' : normSq (evenVersor s c12 c13 c23) ≠ 0 := by rw [normSq_evenVersor]; exact hr
  rw [sandwich, inverse, GacalcProofs.G3.mul_smul, normSq_smul, normSq_reverse_sandwich]
  field_simp [hr']

/-- **The sandwich preserves a vector's magnitude:** `|R v R⁻¹| = |v|` (from `_normSq_of_vec`). -/
theorem magnitude_sandwich_vec (s c12 c13 c23 v1 v2 v3 : ℝ)
    (hr : s ^ 2 + c12 ^ 2 + c13 ^ 2 + c23 ^ 2 ≠ 0) :
    magnitude (sandwich (evenVersor s c12 c13 c23) (vec v1 v2 v3)) = magnitude (vec v1 v2 v3) := by
  simp only [magnitude]
  rw [sandwich_preserves_normSq_of_vec s c12 c13 c23 v1 v2 v3 hr]

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

/-- **The from-vectors versor is an even versor** — `versorFromVectors a b = evenVersor …`, its scalar
    part `b·a + |a||b|` and its bivector part `b∧a`. This bridge lets the general `evenVersor` results
    (isometry, fixed bivector, fixed normal) apply to the actual a→b rotation. -/
theorem versorFromVectors_eq_evenVersor (a1 a2 a3 b1 b2 b3 : ℝ) :
    versorFromVectors (vec a1 a2 a3) (vec b1 b2 b3)
      = evenVersor (b1 * a1 + b2 * a2 + b3 * a3 + mag (vec a1 a2 a3) * mag (vec b1 b2 b3))
          (b1 * a2 - b2 * a1) (b1 * a3 - b3 * a1) (b2 * a3 - b3 * a2) := by
  simp only [versorFromVectors, evenVersor, mul, add, smul, one, vec]; ext <;> ring

/-- **A rotation fixes its own plane bivector** (orientation preserved): for an even versor
    `R = s + B` with `B = p·e₁₂ + q·e₁₃ + t·e₂₃`, `sandwich R B = B` (B commutes with R, so it rides
    through `R R⁻¹ = 1`). This is the "rotates the oriented angle correctly / it's a rotation, not a
    reflection" content: the plane of rotation is kept, with its orientation. -/
theorem sandwich_fixes_own_bivector (s p q t : ℝ) (hr : s ^ 2 + p ^ 2 + q ^ 2 + t ^ 2 ≠ 0) :
    sandwich (evenVersor s p q t) ⟨0, 0, 0, 0, p, q, t, 0⟩ = (⟨0, 0, 0, 0, p, q, t, 0⟩ : G3) := by
  have hd : normSq (evenVersor s p q t) = s ^ 2 + p ^ 2 + q ^ 2 + t ^ 2 := normSq_evenVersor s p q t
  simp only [sandwich, inverse, hd]
  simp only [evenVersor, mul, reverse, smul]
  ext <;> field_simp [hr] <;> ring

/-- **A rotation fixes the normal to its plane** (perpendicular components unchanged): for an even
    versor `R = s + (p·e₁₂ + q·e₁₃ + t·e₂₃)`, the vector `n = t·e₁ − q·e₂ + p·e₃` — the dual of the
    plane bivector, i.e. the axis ⊥ the plane — satisfies `sandwich R n = n` (`n` commutes with `R`,
    so it rides through `R R⁻¹ = 1`). The general-plane form of `sandwich_fixes_orthogonal`. -/
theorem sandwich_fixes_own_normal (s p q t : ℝ) (hr : s ^ 2 + p ^ 2 + q ^ 2 + t ^ 2 ≠ 0) :
    sandwich (evenVersor s p q t) (vec t (-q) p) = vec t (-q) p := by
  have hd : normSq (evenVersor s p q t) = s ^ 2 + p ^ 2 + q ^ 2 + t ^ 2 := normSq_evenVersor s p q t
  simp only [sandwich, inverse, hd]
  simp only [evenVersor, mul, reverse, smul, vec]
  ext <;> field_simp [hr] <;> ring

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
