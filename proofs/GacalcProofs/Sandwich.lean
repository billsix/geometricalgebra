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

/-- The inverse `R⁻¹ = R̃ / |R|²` (valid when `|R|² ≠ 0`). -/
noncomputable def inverse (a : G2) : G2 := smul (1 / normSq a) (reverse a)

/-- The scale-invariant versor sandwich `R v R⁻¹`. -/
noncomputable def sandwich (r v : G2) : G2 := mul (mul r v) (inverse r)

/-- An **even versor** `s + c·e₁₂` — an element of 𝒢₂'s even subalgebra (≅ ℂ), the rotations. -/
def evenVersor (s c : ℝ) : G2 := ⟨s, 0, 0, c⟩

/-- `R` is an **even versor** (grades 0 and 2): its vector part vanishes — how "`R` is an even versor"
    is stated for an arbitrary `R : G2` (no versor subtype). An even versor need **not** be unit length;
    a *rotor* is a unit even versor (tracked: `tasks/lean-unit-versors-rotors-sandwich-with-reverse.md`). -/
def IsEvenVersor (R : G2) : Prop := R.c1 = 0 ∧ R.c2 = 0

/-- An even versor is the `evenVersor` of its own scalar and bivector coordinates — the bridge to the
    `evenVersor …` lemmas. -/
theorem eq_evenVersor_of_isEvenVersor {R : G2} (hR : IsEvenVersor R) : R = evenVersor R.s R.c12 := by
  obtain ⟨h1, h2⟩ := hR
  ext <;> simp only [evenVersor] <;> first | rfl | assumption

/-- A coordinate `evenVersor s c` is an even versor — lets a caller discharge the `IsEvenVersor`
    hypothesis of an object-level theorem when it holds a concrete `evenVersor`. -/
theorem isEvenVersor_evenVersor (s c : ℝ) : IsEvenVersor (evenVersor s c) := ⟨rfl, rfl⟩

/-- `|evenVersor s c|² = s² + c²`. -/
theorem normSq_evenVersor (s c : ℝ) : normSq (evenVersor s c) = s ^ 2 + c ^ 2 := by
  simp only [normSq, evenVersor, mul, reverse]; ring

/-- `|a|² = a · ã`: `normSq` is the scalar part of `a ã`, i.e. the dot with the reverse (definitional). -/
theorem normSq_eq_dot_reverse (a : G2) : normSq a = dot a (reverse a) := rfl

/-- `R R̃ = |R|²·1` for an even versor `R` (object form) (2D): `R R̃` is a pure scalar. Leaf, `ext <;> ring`. -/
theorem mul_reverse_self_of_isEvenVersor {R : G2} (hR : IsEvenVersor R) :
    mul R (reverse R) = smul (normSq R) one := by
  obtain ⟨hR1, hR2⟩ := hR
  simp only [normSq, mul, reverse, one, smul, hR1, hR2]
  ext <;> ring

/-- `R̃ R = |R|²·1` for an even versor `R` (2D) — the same scalar from the other side. -/
theorem reverse_mul_self_of_isEvenVersor {R : G2} (hR : IsEvenVersor R) :
    mul (reverse R) R = smul (normSq R) one := by
  obtain ⟨hR1, hR2⟩ := hR
  simp only [normSq, mul, reverse, one, smul, hR1, hR2]
  ext <;> ring

/-- **Conjugation by an even versor scales the scalar part:** `⟨R X R̃⟩₀ = |R|²·⟨X⟩₀` for ANY `X` (2D).
    The scalar part of a product is cyclic (`dot_comm` moves `R̃` to the front), then `R̃ R = |R|²·1`. -/
theorem dot_reverse_conj {R : G2} (hR : IsEvenVersor R) (X : G2) :
    dot (mul R X) (reverse R) = normSq R * X.s := by
  rw [dot_comm]
  simp only [dot]
  rw [← GacalcProofs.G2.mul_assoc, reverse_mul_self_of_isEvenVersor hR, GacalcProofs.G2.smul_mul,
      GacalcProofs.G2.one_mul]
  simp only [smul]

/-- **The reverse sandwich scales the dot product by `|R|⁴`** (2D): `(R u R̃) · (R v R̃) = |R|⁴·(u · v)` for an
    even versor `R` and ANY `u`, `v` — no grade hypothesis, because the proof never looks at `u` or `v`:
    `(R u R̃)(R v R̃) = R u (R̃ R) v R̃ = |R|²·R (u v) R̃` by associativity and `R̃ R = |R|²·1`, then
    `dot_reverse_conj` on `X = u v`. The dot leaf behind `sandwich_preserves_dot`. -/
theorem dot_reverse_sandwich {R : G2} (hR : IsEvenVersor R) {u v : G2} :
    dot (mul (mul R u) (reverse R)) (mul (mul R v) (reverse R)) = normSq R ^ 2 * dot u v := by
  have h : mul (mul (mul R u) (reverse R)) (mul (mul R v) (reverse R))
      = smul (normSq R) (mul (mul R (mul u v)) (reverse R)) := by
    simp only [GacalcProofs.G2.mul_assoc]
    rw [← GacalcProofs.G2.mul_assoc (reverse R) R, reverse_mul_self_of_isEvenVersor hR,
        GacalcProofs.G2.smul_mul, GacalcProofs.G2.one_mul, GacalcProofs.G2.mul_smul,
        GacalcProofs.G2.mul_smul]
  have h2 : dot (mul (mul R u) (reverse R)) (mul (mul R v) (reverse R))
      = normSq R * dot (mul R (mul u v)) (reverse R) := by
    simp only [dot]; rw [h]; simp only [smul]
  rw [h2, dot_reverse_conj hR]
  simp only [dot]; ring

/-- **The sandwich preserves the dot product** (object form, hence angles, 2D): for an even versor `R`
    with `|R|² ≠ 0` and ANY `u`, `v` (stated for vectors in the book; the identity needs no grade),
    `(R u R⁻¹) · (R v R⁻¹) = u · v`. Structural: pull the inverse's `1/|R|²` out of each factor
    (`mul_smul`), collect through the bilinear dot (`dot_smul_left/right`), apply
    `dot_reverse_sandwich`, then cancel. -/
theorem sandwich_preserves_dot {R : G2} (hR : IsEvenVersor R) (hr : normSq R ≠ 0) {u v : G2} :
    dot (sandwich R u) (sandwich R v) = dot u v := by
  simp only [sandwich, inverse, GacalcProofs.G2.mul_smul]
  rw [dot_smul_left, dot_smul_right, dot_reverse_sandwich hR]
  field_simp [hr]

/-- `normSq` of a scalar multiple: `|k•a|² = k²|a|²` (2D). -/
theorem normSq_smul (k : ℝ) (a : G2) : normSq (smul k a) = k ^ 2 * normSq a := by
  simp only [normSq, smul, reverse, mul]; ring

/-- **The reverse sandwich scales the norm by `|R|⁴`** (2D): `|R v R̃|² = |R|⁴ |v|²` for an even versor
    `R` and ANY `v` (the versor norm is multiplicative through the reverse sandwich). Structural: `|X|²`
    is `X · X̃`, the reverse is an anti-automorphism (`R v R̃` reverses to `R ṽ R̃`), so this is
    `dot_reverse_sandwich` at `u = v`, `v = ṽ`. -/
theorem normSq_reverse_sandwich {R : G2} (hR : IsEvenVersor R) {v : G2} :
    normSq (mul (mul R v) (reverse R)) = normSq R ^ 2 * normSq v := by
  rw [normSq_eq_dot_reverse (mul (mul R v) (reverse R)), reverse_mul, reverse_mul, reverse_reverse,
      ← GacalcProofs.G2.mul_assoc, dot_reverse_sandwich hR, normSq_eq_dot_reverse v]

/-- **The sandwich preserves the squared magnitude** (object form, 2D): `|R v R⁻¹|² = |v|²` for ANY `v`. -/
theorem sandwich_preserves_normSq {R : G2} (hR : IsEvenVersor R) (hr : normSq R ≠ 0) {v : G2} :
    normSq (sandwich R v) = normSq v := by
  rw [sandwich, inverse, GacalcProofs.G2.mul_smul, normSq_smul, normSq_reverse_sandwich hR]
  field_simp [hr]

/-- **The sandwich preserves the magnitude** (object form, 2D): `|R v R⁻¹| = |v|` for ANY `v`. -/
theorem magnitude_sandwich {R : G2} (hR : IsEvenVersor R) (hr : normSq R ≠ 0) {v : G2} :
    magnitude (sandwich R v) = magnitude v := by
  simp only [magnitude]
  rw [sandwich_preserves_normSq hR hr]

/-- `R R̃ = |R|²·1` for the from-vectors versor (even, so `R R̃` is a pure scalar). -/
theorem versorFromVectors_mul_reverse_coord (a1 a2 b1 b2 : ℝ) :
    mul (versorFromVectors (vec a1 a2) (vec b1 b2))
        (reverse (versorFromVectors (vec a1 a2) (vec b1 b2)))
      = smul (normSq (versorFromVectors (vec a1 a2) (vec b1 b2))) one := by
  simp only [normSq, versorFromVectors, mul, reverse, add, smul, one, vec]
  ext <;> ring

/-- **The versor from `a, b` carries `a` to `b`** in 𝒢₂: `R a R⁻¹ = (|a|/|b|)·b` (angle-free) — the
    2D twin of `Rotation3D`'s `sandwich_carries_from_to`, same assembly. In 𝒢₂ the plane is the whole
    space, so this is the whole rotation. Needs `|b| ≠ 0`, `|R|² ≠ 0`. -/
theorem sandwich_carries_from_to_coord (a1 a2 b1 b2 : ℝ)
    (hb : magnitude (vec b1 b2) ≠ 0)
    (hr : normSq (versorFromVectors (vec a1 a2) (vec b1 b2)) ≠ 0) :
    sandwich (versorFromVectors (vec a1 a2) (vec b1 b2)) (vec a1 a2)
      = smul (magnitude (vec a1 a2) / magnitude (vec b1 b2)) (vec b1 b2) := by
  have hbis : bisector (vec a1 a2) (vec b1 b2)
      = smul (1 / magnitude (vec b1 b2)) (mul (vec b1 b2) (versorFromVectors (vec a1 a2) (vec b1 b2))) := by
    rw [from_mul_versor_eq_bisector (isVector_vec a1 a2) (isVector_vec b1 b2),
        GacalcProofs.G2.smul_smul, one_div_mul_cancel hb,
        GacalcProofs.G2.one_smul]
  have hkey : mul (bisector (vec a1 a2) (vec b1 b2))
                  (inverse (versorFromVectors (vec a1 a2) (vec b1 b2)))
      = smul (1 / magnitude (vec b1 b2)) (vec b1 b2) := by
    rw [hbis, GacalcProofs.G2.smul_mul, inverse, GacalcProofs.G2.mul_smul,
        GacalcProofs.G2.mul_assoc, versorFromVectors_mul_reverse_coord, GacalcProofs.G2.mul_smul,
        GacalcProofs.G2.mul_one, GacalcProofs.G2.smul_smul, GacalcProofs.G2.smul_smul]
    congr 1
    field_simp
  rw [sandwich, versor_mul_from_eq_bisector (isVector_vec a1 a2) (isVector_vec b1 b2),
      GacalcProofs.G2.smul_mul, hkey,
      GacalcProofs.G2.smul_smul, mul_one_div]

/-- **The versor from `a, b` carries `a` to `b`** (object form, 2D): `R a R⁻¹ = (|a|/|b|)·b` for vectors
    `a`, `b` with `|b| ≠ 0` and `|R|² ≠ 0`. -/
theorem sandwich_carries_from_to {a b : G2} (ha : IsVector a) (hb : IsVector b)
    (hbn : magnitude b ≠ 0) (hr : normSq (versorFromVectors a b) ≠ 0) :
    sandwich (versorFromVectors a b) a = smul (magnitude a / magnitude b) b := by
  have h := sandwich_carries_from_to_coord a.c1 a.c2 b.c1 b.c2
    (by rw [← eq_vec_of_isVector hb]; exact hbn)
    (by rw [← eq_vec_of_isVector ha, ← eq_vec_of_isVector hb]; exact hr)
  rwa [← eq_vec_of_isVector ha, ← eq_vec_of_isVector hb] at h

/-! ### Object-form wrappers for the scaffold lemmas -/

theorem versorFromVectors_mul_reverse {a b : G2} (ha : IsVector a) (hb : IsVector b) :
    mul (versorFromVectors a b) (reverse (versorFromVectors a b))
      = smul (normSq (versorFromVectors a b)) one := by
  have h := versorFromVectors_mul_reverse_coord a.c1 a.c2 b.c1 b.c2
  rwa [← eq_vec_of_isVector ha, ← eq_vec_of_isVector hb] at h

end GacalcProofs.G2

namespace GacalcProofs.G3

/-- The inverse `R⁻¹ = R̃ / |R|²` (valid when `|R|² ≠ 0`). -/
noncomputable def inverse (a : G3) : G3 := smul (1 / normSq a) (reverse a)

/-- The scale-invariant versor sandwich `R v R⁻¹`. -/
noncomputable def sandwich (r v : G3) : G3 := mul (mul r v) (inverse r)

/-- An **even versor** `s + c₁₂·e₁₂ + c₁₃·e₁₃ + c₂₃·e₂₃` — an element of 𝒢₃'s even subalgebra
    (≅ the quaternions), whose nonzero elements are exactly the rotations via `R v R⁻¹`. -/
def evenVersor (s c12 c13 c23 : ℝ) : G3 := ⟨s, 0, 0, 0, c12, c13, c23, 0⟩

/-- `R` is an **even versor** (grades 0 and 2): its vector and pseudoscalar parts vanish — how "`R` is an
    even versor" is stated for an arbitrary `R : G3`. An even versor need **not** be unit length; a *rotor*
    is a unit even versor (tracked: `tasks/lean-unit-versors-rotors-sandwich-with-reverse.md`). -/
def IsEvenVersor (R : G3) : Prop := R.c1 = 0 ∧ R.c2 = 0 ∧ R.c3 = 0 ∧ R.c123 = 0

/-- An even versor is the `evenVersor` of its own scalar and bivector coordinates — the bridge to the
    `evenVersor …` lemmas. -/
theorem eq_evenVersor_of_isEvenVersor {R : G3} (hR : IsEvenVersor R) :
    R = evenVersor R.s R.c12 R.c13 R.c23 := by
  obtain ⟨h1, h2, h3, h123⟩ := hR
  ext <;> simp only [evenVersor] <;> first | rfl | assumption

/-- A coordinate `evenVersor s c₁₂ c₁₃ c₂₃` is an even versor — lets a caller discharge the
    `IsEvenVersor` hypothesis of an object-level theorem when it holds a concrete `evenVersor`. -/
theorem isEvenVersor_evenVersor (s c12 c13 c23 : ℝ) :
    IsEvenVersor (evenVersor s c12 c13 c23) := ⟨rfl, rfl, rfl, rfl⟩

/-- `|evenVersor s c₁₂ c₁₃ c₂₃|² = s² + c₁₂² + c₁₃² + c₂₃²`. -/
theorem normSq_evenVersor (s c12 c13 c23 : ℝ) :
    normSq (evenVersor s c12 c13 c23) = s ^ 2 + c12 ^ 2 + c13 ^ 2 + c23 ^ 2 := by
  simp only [normSq, evenVersor, mul, reverse]; ring

/-- **Leaf:** `|B|² = p² + q² + r²` for a bivector `B = p·e₁₂ + q·e₁₃ + r·e₂₃`. Reuse instead of
    re-deriving inline. -/
theorem normSq_biv (p q r : ℝ) : normSq (bivector p q r) = p ^ 2 + q ^ 2 + r ^ 2 := by
  simp only [normSq, bivector, zero, mul, reverse]; ring

/-- `T T̃ = |T|²·1` for a trivector (pseudoscalar) `T` (object form). -/
theorem mul_triv_reverse_self {T : G3} (hT : IsTrivector T) :
    mul T (reverse T) = smul (normSq T) one := by
  obtain ⟨hTs, _, _, _, hT12, hT13, hT23⟩ := hT
  simp only [normSq, mul, reverse, one, smul, hTs, hT12, hT13, hT23]
  ext <;> ring

/-- `T T⁻¹ = 1` for a trivector `T` with `|T|² ≠ 0` (object form). -/
theorem mul_triv_inverse_self {T : G3} (hT : IsTrivector T) (hTn : normSq T ≠ 0) :
    mul T (inverse T) = one := by
  rw [inverse, GacalcProofs.G3.mul_smul, mul_triv_reverse_self hT, GacalcProofs.G3.smul_smul,
      one_div_mul_cancel hTn, GacalcProofs.G3.one_smul]

/-- **Reverse is an anti-automorphism:** `(a b)~ = b~ a~`. General (no evenness needed). -/
theorem reverse_mul (a b : G3) : reverse (mul a b) = mul (reverse b) (reverse a) := by
  simp only [reverse, mul]; ext <;> ring

/-- `|a|² = a · ã`: `normSq` is the scalar part of `a ã`, i.e. the dot with the reverse (definitional). -/
theorem normSq_eq_dot_reverse (a : G3) : normSq a = dot a (reverse a) := rfl

/-- `R R̃ = |R|²·1` for an even versor `R` (object form): `R R̃` is a pure scalar. Leaf, `ext <;> ring`. -/
theorem mul_reverse_self_of_isEvenVersor {R : G3} (hR : IsEvenVersor R) :
    mul R (reverse R) = smul (normSq R) one := by
  obtain ⟨hR1, hR2, hR3, hR123⟩ := hR
  simp only [normSq, mul, reverse, one, smul, hR1, hR2, hR3, hR123]
  ext <;> ring

/-- `R̃ R = |R|²·1` for an even versor `R` — the same scalar from the other side. -/
theorem reverse_mul_self_of_isEvenVersor {R : G3} (hR : IsEvenVersor R) :
    mul (reverse R) R = smul (normSq R) one := by
  obtain ⟨hR1, hR2, hR3, hR123⟩ := hR
  simp only [normSq, mul, reverse, one, smul, hR1, hR2, hR3, hR123]
  ext <;> ring

/-- **Conjugation by an even versor scales the scalar part:** `⟨R X R̃⟩₀ = |R|²·⟨X⟩₀` for ANY `X`.
    The scalar part of a product is cyclic (`dot_comm` moves `R̃` to the front), then `R̃ R = |R|²·1`. -/
theorem dot_reverse_conj {R : G3} (hR : IsEvenVersor R) (X : G3) :
    dot (mul R X) (reverse R) = normSq R * X.s := by
  rw [dot_comm]
  simp only [dot]
  rw [← GacalcProofs.G3.mul_assoc, reverse_mul_self_of_isEvenVersor hR, GacalcProofs.G3.smul_mul,
      GacalcProofs.G3.one_mul]
  simp only [smul]

/-- **The reverse sandwich scales the dot product by `|R|⁴`**: `(R u R̃) · (R v R̃) = |R|⁴·(u · v)` for an
    even versor `R` and ANY `u`, `v` — no grade hypothesis, because the proof never looks at `u` or `v`:
    `(R u R̃)(R v R̃) = R u (R̃ R) v R̃ = |R|²·R (u v) R̃` by associativity and `R̃ R = |R|²·1`, then
    `dot_reverse_conj` on `X = u v`. The dot leaf behind `sandwich_preserves_dot`. -/
theorem dot_reverse_sandwich {R : G3} (hR : IsEvenVersor R) {u v : G3} :
    dot (mul (mul R u) (reverse R)) (mul (mul R v) (reverse R)) = normSq R ^ 2 * dot u v := by
  have h : mul (mul (mul R u) (reverse R)) (mul (mul R v) (reverse R))
      = smul (normSq R) (mul (mul R (mul u v)) (reverse R)) := by
    simp only [GacalcProofs.G3.mul_assoc]
    rw [← GacalcProofs.G3.mul_assoc (reverse R) R, reverse_mul_self_of_isEvenVersor hR,
        GacalcProofs.G3.smul_mul, GacalcProofs.G3.one_mul, GacalcProofs.G3.mul_smul,
        GacalcProofs.G3.mul_smul]
  have h2 : dot (mul (mul R u) (reverse R)) (mul (mul R v) (reverse R))
      = normSq R * dot (mul R (mul u v)) (reverse R) := by
    simp only [dot]; rw [h]; simp only [smul]
  rw [h2, dot_reverse_conj hR]
  simp only [dot]; ring

/-- **The sandwich preserves the dot product** (object form, hence angles): for an even versor `R` with
    `|R|² ≠ 0` and ANY `u`, `v` (stated for vectors in the book; the identity needs no grade),
    `(R u R⁻¹) · (R v R⁻¹) = u · v`. Structural: pull the inverse's `1/|R|²` out of each factor
    (`mul_smul`), collect through the bilinear dot (`dot_smul_left/right`), apply
    `dot_reverse_sandwich`, then cancel `(1/|R|²)²·|R|⁴ = 1`. -/
theorem sandwich_preserves_dot {R : G3} (hR : IsEvenVersor R) (hr : normSq R ≠ 0) {u v : G3} :
    dot (sandwich R u) (sandwich R v) = dot u v := by
  simp only [sandwich, inverse, GacalcProofs.G3.mul_smul]
  rw [dot_smul_left, dot_smul_right, dot_reverse_sandwich hR]
  field_simp [hr]

/-- `R R̃ = |R|²·1` for the from-vectors versor (it is even — scalar + bivector — so `R R̃` is a
    pure scalar). Proved by `ext <;> ring`: the odd/bivector components vanish structurally, with no
    `√` fact needed (the magnitudes appear only in the scalar coefficient). -/
theorem versorFromVectors_mul_reverse_coord (a1 a2 a3 b1 b2 b3 : ℝ) :
    mul (versorFromVectors (vec a1 a2 a3) (vec b1 b2 b3))
        (reverse (versorFromVectors (vec a1 a2 a3) (vec b1 b2 b3)))
      = smul (normSq (versorFromVectors (vec a1 a2 a3) (vec b1 b2 b3))) one := by
  simp only [normSq, versorFromVectors, mul, reverse, add, smul, one, vec]
  ext <;> ring

/-- **The from-vectors versor is invertible: `R R⁻¹ = 1`** (for `|R|² ≠ 0`). Uses `R R̃ = |R|²·1`,
    `mul_smul`, `smul_smul`, and `1/|R|² · |R|² = 1`. -/
theorem versorFromVectors_mul_inverse_coord (a1 a2 a3 b1 b2 b3 : ℝ)
    (hr : normSq (versorFromVectors (vec a1 a2 a3) (vec b1 b2 b3)) ≠ 0) :
    mul (versorFromVectors (vec a1 a2 a3) (vec b1 b2 b3))
        (inverse (versorFromVectors (vec a1 a2 a3) (vec b1 b2 b3))) = one := by
  rw [inverse, GacalcProofs.G3.mul_smul, versorFromVectors_mul_reverse_coord,
      GacalcProofs.G3.smul_smul, one_div_mul_cancel hr]
  simp only [smul, one]; ext <;> ring

/-- **The versor from `a, b` carries `a` to `b`**: `R a R⁻¹ = (|a|/|b|)·b` (angle-free). The
    scale-invariant sandwich sends the from-vector to the to-vector, scaled to length `|a|` (the
    rotation preserves length, so `a` of length `|a|` lands on `b̂` at length `|a|`). Assembled from
    `R a = |a|·h`, `b R = |b|·h`, `R R̃ = |R|²·1`, and `R R⁻¹ = 1`. Needs `|b| ≠ 0`, `|R|² ≠ 0`. -/
theorem sandwich_carries_from_to_coord (a1 a2 a3 b1 b2 b3 : ℝ)
    (hb : magnitude (vec b1 b2 b3) ≠ 0)
    (hr : normSq (versorFromVectors (vec a1 a2 a3) (vec b1 b2 b3)) ≠ 0) :
    sandwich (versorFromVectors (vec a1 a2 a3) (vec b1 b2 b3)) (vec a1 a2 a3)
      = smul (magnitude (vec a1 a2 a3) / magnitude (vec b1 b2 b3)) (vec b1 b2 b3) := by
  -- The bisector expressed via `b R` (from `b R = |b|·h`, undone with |b| ≠ 0).
  have hbis : bisector (vec a1 a2 a3) (vec b1 b2 b3)
      = smul (1 / magnitude (vec b1 b2 b3))
             (mul (vec b1 b2 b3) (versorFromVectors (vec a1 a2 a3) (vec b1 b2 b3))) := by
    rw [from_mul_versor_eq_bisector (isVector_vec a1 a2 a3) (isVector_vec b1 b2 b3),
        GacalcProofs.G3.smul_smul, one_div_mul_cancel hb,
        GacalcProofs.G3.one_smul]
  -- The heart: h R⁻¹ = (1/|b|)·b, via associativity + R R̃ = |R|² + mul_one.
  have hkey : mul (bisector (vec a1 a2 a3) (vec b1 b2 b3))
                  (inverse (versorFromVectors (vec a1 a2 a3) (vec b1 b2 b3)))
      = smul (1 / magnitude (vec b1 b2 b3)) (vec b1 b2 b3) := by
    rw [hbis, GacalcProofs.G3.smul_mul, inverse, GacalcProofs.G3.mul_smul,
        GacalcProofs.G3.mul_assoc, versorFromVectors_mul_reverse_coord, GacalcProofs.G3.mul_smul,
        GacalcProofs.G3.mul_one, GacalcProofs.G3.smul_smul, GacalcProofs.G3.smul_smul]
    congr 1
    field_simp
  -- Assemble: sandwich R a = |a|·(h R⁻¹) = |a|·(1/|b|)·b = (|a|/|b|)·b.
  rw [sandwich, versor_mul_from_eq_bisector (isVector_vec a1 a2 a3) (isVector_vec b1 b2 b3),
      GacalcProofs.G3.smul_mul, hkey,
      GacalcProofs.G3.smul_smul, mul_one_div]

/-- **The versor from `a, b` carries `a` to `b`** (object form): `R a R⁻¹ = (|a|/|b|)·b` for vectors
    `a`, `b` with `|b| ≠ 0` and `|R|² ≠ 0`. -/
theorem sandwich_carries_from_to {a b : G3} (ha : IsVector a) (hb : IsVector b)
    (hbn : magnitude b ≠ 0) (hr : normSq (versorFromVectors a b) ≠ 0) :
    sandwich (versorFromVectors a b) a = smul (magnitude a / magnitude b) b := by
  have h := sandwich_carries_from_to_coord a.c1 a.c2 a.c3 b.c1 b.c2 b.c3
    (by rw [← eq_vec_of_isVector hb]; exact hbn)
    (by rw [← eq_vec_of_isVector ha, ← eq_vec_of_isVector hb]; exact hr)
  rwa [← eq_vec_of_isVector ha, ← eq_vec_of_isVector hb] at h

/-- `normSq` of a scalar multiple: `|k•a|² = k²|a|²`. -/
theorem normSq_smul (k : ℝ) (a : G3) : normSq (smul k a) = k ^ 2 * normSq a := by
  simp only [normSq, smul, reverse, mul]; ring

/-- **The reverse sandwich scales the norm by `|R|⁴`**: `|R v R̃|² = |R|⁴ |v|²` for an even versor
    `R` and ANY `v` (the versor norm is multiplicative through the reverse sandwich). Structural: `|X|²`
    is `X · X̃`, the reverse is an anti-automorphism (`R v R̃` reverses to `R ṽ R̃`), so this is
    `dot_reverse_sandwich` at `u = v`, `v = ṽ`. -/
theorem normSq_reverse_sandwich {R : G3} (hR : IsEvenVersor R) {v : G3} :
    normSq (mul (mul R v) (reverse R)) = normSq R ^ 2 * normSq v := by
  rw [normSq_eq_dot_reverse (mul (mul R v) (reverse R)), reverse_mul, reverse_mul, reverse_reverse,
      ← GacalcProofs.G3.mul_assoc, dot_reverse_sandwich hR, normSq_eq_dot_reverse v]

/-- **The sandwich preserves the squared magnitude** (object form): `|R v R⁻¹|² = |v|²` for ANY `v` — the
    inverse sandwich is an isometry. Structural: factor the inverse's scalar (`mul_smul`), scale by
    `normSq_smul`, use `|R v R̃|² = |R|⁴|v|²`, then cancel `(1/|R|²)²·|R|⁴ = 1` (`|R|² ≠ 0`). -/
theorem sandwich_preserves_normSq {R : G3} (hR : IsEvenVersor R) (hr : normSq R ≠ 0) {v : G3} :
    normSq (sandwich R v) = normSq v := by
  rw [sandwich, inverse, GacalcProofs.G3.mul_smul, normSq_smul, normSq_reverse_sandwich hR]
  field_simp [hr]

/-- **The sandwich preserves the magnitude** (object form): `|R v R⁻¹| = |v|` for ANY `v`. -/
theorem magnitude_sandwich {R : G3} (hR : IsEvenVersor R) (hr : normSq R ≠ 0) {v : G3} :
    magnitude (sandwich R v) = magnitude v := by
  simp only [magnitude]
  rw [sandwich_preserves_normSq hR hr]

/-- **The reverse-sandwich is an outermorphism up to `|R|²`:** `(R u R̃) ∧ (R v R̃) = |R|²·R (u∧v) R̃`.
    A pure polynomial identity (no division) — the unnormalized core of `sandwich_preserves_wedge`, the
    outer-product twin of `normSq_reverse_sandwich`. -/
theorem wedge_reverse_sandwich {R : G3} (hR : IsEvenVersor R) {u v : G3} :
    wedge (mul (mul R u) (reverse R)) (mul (mul R v) (reverse R))
      = smul (normSq R) (mul (mul R (wedge u v)) (reverse R)) := by
  obtain ⟨hR1, hR2, hR3, hR123⟩ := hR
  simp only [normSq, wedge, mul, reverse, smul, hR1, hR2, hR3, hR123]
  ext <;> ring

/-- **The sandwich preserves the outer product** (object form, the *outermorphism* property):
    `(R u R⁻¹) ∧ (R v R⁻¹) = R (u ∧ v) R⁻¹` for an even versor `R` with `|R|² ≠ 0` and ANY `u`, `v`.
    Since it is multiplicative and grade-preserving, it carries the plane bivector `u ∧ v` intact
    (orientation included) — the outer-product analogue of `sandwich_preserves_dot`, and the leaf behind
    sine / oriented-angle preservation. Structural: pull the inverse's `1/|R|²` out of each factor
    (`mul_smul`), collect the scalars through the bilinear wedge, apply `wedge_reverse_sandwich`, then
    `(1/|R|²)²·|R|² = 1/|R|²`. -/
theorem sandwich_preserves_wedge {R : G3} (hR : IsEvenVersor R) (hr : normSq R ≠ 0) {u v : G3} :
    wedge (sandwich R u) (sandwich R v) = sandwich R (wedge u v) := by
  simp only [sandwich, inverse, GacalcProofs.G3.mul_smul, GacalcProofs.G3.wedge_smul_left,
             GacalcProofs.G3.wedge_smul_right, GacalcProofs.G3.smul_smul]
  rw [wedge_reverse_sandwich hR, GacalcProofs.G3.smul_smul]
  congr 1
  field_simp

/-- **The reverse sandwich scales the wedge's norm by `|R|²`:** `|R (u∧v) R̃|² = |R|⁴ |u∧v|²` for an
    even versor — the grade-2 twin of `normSq_reverse_sandwich`, stated on the plane bivector `u∧v`
    itself (not a raw coordinate literal). Pure polynomial. -/
theorem normSq_reverse_sandwich_wedge {R : G3} (hR : IsEvenVersor R) {u v : G3} :
    normSq (mul (mul R (wedge u v)) (reverse R)) = normSq R ^ 2 * normSq (wedge u v) := by
  obtain ⟨hR1, hR2, hR3, hR123⟩ := hR
  simp only [normSq, wedge, mul, reverse, hR1, hR2, hR3, hR123]
  ring

/-- **The sandwich preserves the wedge's squared magnitude** (object form): `|R (u∧v) R⁻¹|² = |u∧v|²` — a
    rotation is an isometry on the plane bivector too, not just on vectors (ANY `u`, `v`). Same structural
    shape as `sandwich_preserves_normSq`, over `normSq_reverse_sandwich_wedge`. -/
theorem sandwich_preserves_normSq_of_wedge {R : G3} (hR : IsEvenVersor R) (hr : normSq R ≠ 0)
    {u v : G3} :
    normSq (sandwich R (wedge u v)) = normSq (wedge u v) := by
  rw [sandwich, inverse, GacalcProofs.G3.mul_smul, normSq_smul, normSq_reverse_sandwich_wedge hR]
  field_simp [hr]

/-- **A plane rotation leaves the orthogonal axis fixed** — the 3D fact with no 2D analogue. A versor
    in the e₁e₂ plane (`R = s + c₁₂·e₁₂`, `c₁₃ = c₂₃ = 0`) fixes the e₃ component: `R (z e₃) R⁻¹ = z e₃`
    (e₃ commutes with the plane bivector, so it slides through `R R⁻¹ = 1`). This is exactly the
    maintainer's "no effect on components orthogonal to the plane of rotation." -/
theorem sandwich_fixes_orthogonal (s c12 z : ℝ) (hr : normSq (evenVersor s c12 0 0) ≠ 0) :
    sandwich (evenVersor s c12 0 0) (vec 0 0 z) = vec 0 0 z := by
  have hd : normSq (evenVersor s c12 0 0) = s ^ 2 + c12 ^ 2 := by
    simp only [normSq, evenVersor, mul, reverse]; ring
  rw [hd] at hr
  simp only [sandwich, inverse, hd]
  simp only [evenVersor, mul, reverse, smul, vec]
  ext <;> field_simp [hr] <;> ring

/-- **A plane rotation keeps in-plane vectors in the plane.** A versor in the e₁e₂ plane sends a
    vector `x e₁ + y e₂` to another vector in that plane — its e₃ component stays `0`. With
    `sandwich_fixes_orthogonal`, the plane and its normal are both invariant, so the 3D sandwich
    reduces to a 2D rotation in the plane. -/
theorem sandwich_plane_invariant (s c12 x y : ℝ) (hr : normSq (evenVersor s c12 0 0) ≠ 0) :
    (sandwich (evenVersor s c12 0 0) (vec x y 0)).c3 = 0 := by
  have hd : normSq (evenVersor s c12 0 0) = s ^ 2 + c12 ^ 2 := by
    simp only [normSq, evenVersor, mul, reverse]; ring
  rw [hd] at hr
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

/-- The sandwich is **linear** in the rotated vector: it distributes over subtraction. -/
theorem sandwich_sub (r u v : G3) : sandwich r (sub u v) = sub (sandwich r u) (sandwich r v) := by
  simp only [sandwich]; rw [GacalcProofs.G3.mul_sub, GacalcProofs.G3.sub_mul]

/-- **The sandwich of a vector by an even versor stays a vector** — grade-preserving (the scalar,
    bivector and pseudoscalar parts of `R v R⁻¹` all vanish), for any even versor `R` and vector `v`
    (no `|R|² ≠ 0` needed: each vanishing part is `(1/|R|²)·0`). -/
theorem sandwich_evenVersor_vec_isVector {R : G3} (hR : IsEvenVersor R) {v : G3} (hv : IsVector v) :
    IsVector (sandwich R v) := by
  rw [eq_evenVersor_of_isEvenVersor hR, eq_vec_of_isVector hv]
  refine ⟨?_, ?_, ?_, ?_, ?_⟩ <;>
    simp only [sandwich, inverse, evenVersor, mul, reverse, smul, vec] <;> ring

/-- **The from-vectors versor is an even versor** — `versorFromVectors a b = evenVersor …`, its scalar
    part `b·a + |a||b|` and its bivector part `b∧a`. This bridge lets the general `evenVersor` results
    (isometry, fixed bivector, fixed normal) apply to the actual a→b rotation. -/
theorem versorFromVectors_eq_evenVersor (a1 a2 a3 b1 b2 b3 : ℝ) :
    versorFromVectors (vec a1 a2 a3) (vec b1 b2 b3)
      = evenVersor (b1 * a1 + b2 * a2 + b3 * a3 + magnitude (vec a1 a2 a3) * magnitude (vec b1 b2 b3))
          (b1 * a2 - b2 * a1) (b1 * a3 - b3 * a1) (b2 * a3 - b3 * a2) := by
  simp only [versorFromVectors, evenVersor, mul, add, smul, one, vec]; ext <;> ring

/-- **A rotation fixes its own plane bivector** (orientation preserved): for an even versor
    `R = s + B` with `B = p·e₁₂ + q·e₁₃ + t·e₂₃`, `sandwich R B = B` (B commutes with R, so it rides
    through `R R⁻¹ = 1`). This is the "rotates the oriented angle correctly / it's a rotation, not a
    reflection" content: the plane of rotation is kept, with its orientation. -/
theorem sandwich_fixes_own_bivector_coord (s p q t : ℝ) (hr : normSq (evenVersor s p q t) ≠ 0) :
    sandwich (evenVersor s p q t) (bivector p q t) = bivector p q t := by
  have hd : normSq (evenVersor s p q t) = s ^ 2 + p ^ 2 + q ^ 2 + t ^ 2 := normSq_evenVersor s p q t
  rw [hd] at hr
  simp only [sandwich, inverse, hd]
  simp only [evenVersor, bivector, zero, mul, reverse, smul]
  ext <;> field_simp [hr] <;> ring

/-- Object form: an even versor fixes its own plane bivector, `sandwich R (grade-2 part of R) =
    (grade-2 part of R)`, for `|R|² ≠ 0`. -/
theorem sandwich_fixes_own_bivector {R : G3} (hR : IsEvenVersor R) (hr : normSq R ≠ 0) :
    sandwich R (bivector R.c12 R.c13 R.c23) = bivector R.c12 R.c13 R.c23 := by
  have h := sandwich_fixes_own_bivector_coord R.s R.c12 R.c13 R.c23
    (by rw [← eq_evenVersor_of_isEvenVersor hR]; exact hr)
  rwa [← eq_evenVersor_of_isEvenVersor hR] at h

/-- **A rotation fixes the normal to its plane** (perpendicular components unchanged): for an even
    versor `R = s + (p·e₁₂ + q·e₁₃ + t·e₂₃)`, the vector `n = t·e₁ − q·e₂ + p·e₃` — the dual of the
    plane bivector, i.e. the axis ⊥ the plane — satisfies `sandwich R n = n` (`n` commutes with `R`,
    so it rides through `R R⁻¹ = 1`). The general-plane form of `sandwich_fixes_orthogonal`. -/
theorem sandwich_fixes_own_normal_coord (s p q t : ℝ) (hr : normSq (evenVersor s p q t) ≠ 0) :
    sandwich (evenVersor s p q t) (vec t (-q) p) = vec t (-q) p := by
  have hd : normSq (evenVersor s p q t) = s ^ 2 + p ^ 2 + q ^ 2 + t ^ 2 := normSq_evenVersor s p q t
  rw [hd] at hr
  simp only [sandwich, inverse, hd]
  simp only [evenVersor, mul, reverse, smul, vec]
  ext <;> field_simp [hr] <;> ring

/-- Object form: an even versor fixes the normal to its plane (the dual of its grade-2 part),
    for `|R|² ≠ 0`. -/
theorem sandwich_fixes_own_normal {R : G3} (hR : IsEvenVersor R) (hr : normSq R ≠ 0) :
    sandwich R (vec R.c23 (-R.c13) R.c12) = vec R.c23 (-R.c13) R.c12 := by
  have h := sandwich_fixes_own_normal_coord R.s R.c12 R.c13 R.c23
    (by rw [← eq_evenVersor_of_isEvenVersor hR]; exact hr)
  rwa [← eq_evenVersor_of_isEvenVersor hR] at h

/-! ### Composition: rotations compose by multiplying versors -/

/-- `reverse` fixes any grade-1 element (the `IsVector` form of `reverse_vec`): the grades 2 and 3
    it flips are absent from a vector. -/
theorem reverse_of_isVector {a : G3} (ha : IsVector a) : reverse a = a := by
  obtain ⟨_, h12, h13, h23, h123⟩ := ha
  simp only [reverse]; ext <;> simp [h12, h13, h23, h123]

/-- **Reverse reverses a product of two vectors:** `(a b)~ = b a` for vectors `a, b`. Corollary of
    the anti-automorphism `reverse_mul` and `reverse` fixing a vector (`reverse_of_isVector`). -/
theorem reverse_mul_vec {a b : G3} (ha : IsVector a) (hb : IsVector b) :
    reverse (mul a b) = mul b a := by
  rw [reverse_mul, reverse_of_isVector ha, reverse_of_isVector hb]

/-- **Reverse reverses a product of three vectors:** `(a b c)~ = c b a` for vectors `a, b, c` (3D).
    Corollary of `reverse_mul` applied twice, `reverse_of_isVector`, and associativity
    (`mul_assoc`) to normalise the result to `(c b) a`. -/
theorem reverse_mul3_vec {a b c : G3} (ha : IsVector a) (hb : IsVector b) (hc : IsVector c) :
    reverse (mul (mul a b) c) = mul (mul c b) a := by
  rw [reverse_mul, reverse_of_isVector hc, reverse_mul, reverse_of_isVector hb,
      reverse_of_isVector ha]
  exact (GacalcProofs.G3.mul_assoc c b a).symm

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
theorem sandwich_comp_coord (s1 p1 q1 t1 s2 p2 q2 t2 : ℝ) (v : G3)
    (h1 : normSq (evenVersor s1 p1 q1 t1) ≠ 0) (h2 : normSq (evenVersor s2 p2 q2 t2) ≠ 0) :
    sandwich (mul (evenVersor s1 p1 q1 t1) (evenVersor s2 p2 q2 t2)) v
      = sandwich (evenVersor s1 p1 q1 t1) (sandwich (evenVersor s2 p2 q2 t2) v) := by
  simp only [sandwich]
  rw [inverse_mul s1 p1 q1 t1 s2 p2 q2 t2 h1 h2]
  simp only [GacalcProofs.G3.mul_assoc]

/-- **Rotations compose by multiplying versors** (object form): `(R₁ R₂) v (R₁ R₂)⁻¹
    = R₁ (R₂ v R₂⁻¹) R₁⁻¹`, for even versors `R₁`, `R₂` with nonzero norm and any `v`. -/
theorem sandwich_comp {R1 R2 : G3} (hR1 : IsEvenVersor R1) (hR2 : IsEvenVersor R2) (v : G3)
    (h1 : normSq R1 ≠ 0) (h2 : normSq R2 ≠ 0) :
    sandwich (mul R1 R2) v = sandwich R1 (sandwich R2 v) := by
  have h := sandwich_comp_coord R1.s R1.c12 R1.c13 R1.c23 R2.s R2.c12 R2.c13 R2.c23 v
    (by rw [← eq_evenVersor_of_isEvenVersor hR1]; exact h1)
    (by rw [← eq_evenVersor_of_isEvenVersor hR2]; exact h2)
  rwa [← eq_evenVersor_of_isEvenVersor hR1, ← eq_evenVersor_of_isEvenVersor hR2] at h

/-! ### Object-form wrappers for the scaffold lemmas -/

theorem mul_biv_reverse_self {B : G3} (hB : IsBivector B) :
    mul B (reverse B) = smul (normSq B) one := by
  obtain ⟨_, hB1, hB2, hB3, hB123⟩ := hB
  simp only [normSq, mul, reverse, one, smul, hB1, hB2, hB3, hB123]
  ext <;> ring

theorem mul_biv_inverse_self {B : G3} (hB : IsBivector B) (hBn : normSq B ≠ 0) :
    mul B (inverse B) = one := by
  rw [inverse, GacalcProofs.G3.mul_smul, mul_biv_reverse_self hB, GacalcProofs.G3.smul_smul,
      one_div_mul_cancel hBn, GacalcProofs.G3.one_smul]

theorem versorFromVectors_mul_reverse {a b : G3} (ha : IsVector a) (hb : IsVector b) :
    mul (versorFromVectors a b) (reverse (versorFromVectors a b))
      = smul (normSq (versorFromVectors a b)) one := by
  obtain ⟨has, ha12, ha13, ha23, ha123⟩ := ha
  obtain ⟨hbs, hb12, hb13, hb23, hb123⟩ := hb
  simp only [normSq, versorFromVectors, mul, reverse, add, smul, one,
             has, ha12, ha13, ha23, ha123, hbs, hb12, hb13, hb23, hb123]
  ext <;> ring

theorem versorFromVectors_mul_inverse {a b : G3} (ha : IsVector a) (hb : IsVector b)
    (hr : normSq (versorFromVectors a b) ≠ 0) :
    mul (versorFromVectors a b) (inverse (versorFromVectors a b)) = one := by
  rw [inverse, GacalcProofs.G3.mul_smul, versorFromVectors_mul_reverse ha hb,
      GacalcProofs.G3.smul_smul, one_div_mul_cancel hr, GacalcProofs.G3.one_smul]

end GacalcProofs.G3
