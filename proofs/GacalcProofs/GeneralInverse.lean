import GacalcProofs.G2
import GacalcProofs.G3
import GacalcProofs.Sandwich

/-!
# The general multivector inverse in 𝒢₂ and 𝒢₃

`inverse a = Ã / |A|²` (`Sandwich.lean`, Python `MultiVectorBase.inverse`) is an inverse only when
`A * Ã` is a scalar: a blade or a versor. This file inverts **every** invertible element of 𝒢₂ and
𝒢₃, following Hitzer & Sangwine, "Multivector and multivector matrix inverses in real Clifford
algebras" (2017). Two sign flips are needed beside the reverse:

* the **grade involution** `Â`, which negates the odd grades;
* the **Clifford conjugate** `Ā` (the reverse of `Â`), which negates grades 1 and 2.

In 𝒢₂, `A * Ā` is a scalar, so `A⁻¹ = Ā / (A * Ā)`. In 𝒢₃, `N = A * Ā` is a scalar plus a
pseudoscalar, which commutes with everything. Its grade involution `N̂` flips the pseudoscalar's
sign, and `N * N̂ = N₀² + N₁₂₃²` is a scalar, so `A⁻¹ = Ā * N̂ / (N * N̂)`. Each is proved a two-sided
inverse whenever its scalar denominator is nonzero. In 𝒢₂ the general inverse of a vector equals the
`Ã / |A|²` inverse (`generalInverse_eq_inverse_of_isVector`); there is no 𝒢₃ counterpart.

The forms were checked symbolically with gacalc before being proved here
(`tasks/archive/2026/11/18/lean-general-multivector-inverse.md`). Python keeps the guarded
blade/versor formula for now (William Emerison Six <billsix@gmail.com>, 2026-11-18).
-/

namespace GacalcProofs.G2

/-- The **grade involution** `Â`: the odd grade (the vector part) negated. -/
noncomputable def gradeInvolution (a : G2) : G2 := ⟨a.s, -a.c1, -a.c2, a.c12⟩

/-- The **Clifford conjugate** `Ā`, the reverse of the grade involution: grades 1 and 2 negated. -/
noncomputable def cliffordConjugate (a : G2) : G2 := ⟨a.s, -a.c1, -a.c2, -a.c12⟩

/-- The conjugate is the reverse of the grade involution. -/
theorem cliffordConjugate_eq_reverse_gradeInvolution (a : G2) :
    cliffordConjugate a = reverse (gradeInvolution a) := by
  ext <;> simp [cliffordConjugate, reverse, gradeInvolution]

/-- The scalar `A * Ā`, the denominator of the general inverse. -/
noncomputable def conjNorm (a : G2) : ℝ := (mul a (cliffordConjugate a)).s

/-- `A * Ā` is a scalar, for every `A`. -/
theorem mul_cliffordConjugate (a : G2) :
    mul a (cliffordConjugate a) = scalar (conjNorm a) := by
  simp only [mul, cliffordConjugate, conjNorm, scalar]; ext <;> ring

/-- `Ā * A` is the same scalar. -/
theorem cliffordConjugate_mul (a : G2) :
    mul (cliffordConjugate a) a = scalar (conjNorm a) := by
  simp only [mul, cliffordConjugate, conjNorm, scalar]; ext <;> ring

/-- The **general inverse** `A⁻¹ = Ā / (A * Ā)`. -/
noncomputable def generalInverse (a : G2) : G2 := smul (conjNorm a)⁻¹ (cliffordConjugate a)

/-- A scalar times its reciprocal's multiple is `one`. -/
private theorem smul_inv_scalar {k : ℝ} (hk : k ≠ 0) : smul k⁻¹ (scalar k) = one := by
  simp only [smul, scalar, one]; ext <;> simp [inv_mul_cancel₀ hk]

/-- `A * A⁻¹ = 1` for every `A` whose `A * Ā` is nonzero. -/
theorem mul_generalInverse {a : G2} (h : conjNorm a ≠ 0) : mul a (generalInverse a) = one := by
  rw [generalInverse, mul_smul, mul_cliffordConjugate, smul_inv_scalar h]

/-- `A⁻¹ * A = 1` for every `A` whose `A * Ā` is nonzero. -/
theorem generalInverse_mul {a : G2} (h : conjNorm a ≠ 0) : mul (generalInverse a) a = one := by
  rw [generalInverse, smul_mul, cliffordConjugate_mul, smul_inv_scalar h]

/-- For a vector, `A * Ā = −|A|²`. -/
theorem conjNorm_of_isVector {a : G2} (ha : IsVector a) : conjNorm a = -normSq a := by
  obtain ⟨hs, h12⟩ := ha
  simp only [conjNorm, normSq, mul, cliffordConjugate, reverse, hs, h12]; ring

/-- For a vector the general inverse is the familiar `Ã / |A|²`. -/
theorem generalInverse_eq_inverse_of_isVector {a : G2} (ha : IsVector a) :
    generalInverse a = inverse a := by
  rw [generalInverse, inverse, conjNorm_of_isVector ha]
  obtain ⟨hs, h12⟩ := ha
  ext <;> simp only [smul, cliffordConjugate, reverse, hs, h12, one_div, inv_neg] <;> ring

end GacalcProofs.G2

namespace GacalcProofs.G3

/-- The **grade involution** `Â`: the odd grades (vector, pseudoscalar) negated. -/
noncomputable def gradeInvolution (a : G3) : G3 :=
  ⟨a.s, -a.c1, -a.c2, -a.c3, a.c12, a.c13, a.c23, -a.c123⟩

/-- The **Clifford conjugate** `Ā`, the reverse of the grade involution: grades 1 and 2 negated. -/
noncomputable def cliffordConjugate (a : G3) : G3 :=
  ⟨a.s, -a.c1, -a.c2, -a.c3, -a.c12, -a.c13, -a.c23, a.c123⟩

/-- The conjugate is the reverse of the grade involution. -/
theorem cliffordConjugate_eq_reverse_gradeInvolution (a : G3) :
    cliffordConjugate a = reverse (gradeInvolution a) := by
  ext <;> simp [cliffordConjugate, reverse, gradeInvolution]

/-- `N = A * Ā`: a scalar plus a pseudoscalar (the next theorem). -/
noncomputable def conjProduct (a : G3) : G3 := mul a (cliffordConjugate a)

/-- `A * Ā` has no vector or bivector part. -/
theorem conjProduct_grades (a : G3) :
    (conjProduct a).c1 = 0 ∧ (conjProduct a).c2 = 0 ∧ (conjProduct a).c3 = 0 ∧
      (conjProduct a).c12 = 0 ∧ (conjProduct a).c13 = 0 ∧ (conjProduct a).c23 = 0 := by
  simp only [conjProduct, mul, cliffordConjugate]
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_⟩ <;> ring

/-- `Ā * A = A * Ā`. -/
theorem cliffordConjugate_mul (a : G3) : mul (cliffordConjugate a) a = conjProduct a := by
  simp only [conjProduct, mul, cliffordConjugate]; ext <;> ring

/-- The scalar `N * N̂ = N₀² + N₁₂₃²`, the denominator of the general inverse. -/
noncomputable def conjNorm (a : G3) : ℝ :=
  (mul (conjProduct a) (gradeInvolution (conjProduct a))).s

/-- `N * N̂` is a scalar, for every `A`. -/
theorem conjProduct_mul_gradeInvolution (a : G3) :
    mul (conjProduct a) (gradeInvolution (conjProduct a)) = scalar (conjNorm a) := by
  simp only [conjNorm, conjProduct, mul, cliffordConjugate, gradeInvolution, scalar, zero]
  ext <;> ring

/-- `N̂` commutes with `A` (a scalar plus a pseudoscalar is central in 𝒢₃). -/
theorem gradeInvolution_conjProduct_comm (a : G3) :
    mul (gradeInvolution (conjProduct a)) a = mul a (gradeInvolution (conjProduct a)) := by
  simp only [conjProduct, mul, cliffordConjugate, gradeInvolution]; ext <;> ring

/-- The **general inverse** `A⁻¹ = Ā * N̂ / (N * N̂)`, with `N = A * Ā`. -/
noncomputable def generalInverse (a : G3) : G3 :=
  smul (conjNorm a)⁻¹ (mul (cliffordConjugate a) (gradeInvolution (conjProduct a)))

/-- A scalar times its reciprocal's multiple is `one`. -/
private theorem smul_inv_scalar {k : ℝ} (hk : k ≠ 0) : smul k⁻¹ (scalar k) = one := by
  simp only [smul, scalar, one, zero]; ext <;> simp [inv_mul_cancel₀ hk]

/-- `A * A⁻¹ = 1` for every `A` whose `N * N̂` is nonzero. -/
theorem mul_generalInverse {a : G3} (h : conjNorm a ≠ 0) : mul a (generalInverse a) = one := by
  rw [generalInverse, mul_smul, ← mul_assoc]
  change smul _ (mul (conjProduct a) _) = one
  rw [conjProduct_mul_gradeInvolution, smul_inv_scalar h]

/-- `A⁻¹ * A = 1` for every `A` whose `N * N̂` is nonzero. -/
theorem generalInverse_mul {a : G3} (h : conjNorm a ≠ 0) : mul (generalInverse a) a = one := by
  rw [generalInverse, smul_mul, mul_assoc, gradeInvolution_conjProduct_comm, ← mul_assoc,
    cliffordConjugate_mul, conjProduct_mul_gradeInvolution, smul_inv_scalar h]

end GacalcProofs.G3
