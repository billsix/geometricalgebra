import GacalcProofs.G2
import GacalcProofs.G3
import GacalcProofs.Sandwich

/-! # The exponential map: exp of a bivector is a rotor

    gacalc's `exp` (base.py) is the closed form `cos|A| + sin|A|·Â` for a negative-square blade
    `A` (`A² < 0`: a bivector, or the 𝒢₃ pseudoscalar), and it is automatically a **unit versor**
    (a rotor), since `cos² + sin² = 1` (Dorst–Fontijne–Mann §7.4, "a rotor is the exp of a bivector").
    Here we prove the key special case — the exp of the unit-plane bivector `θ·e₁₂` (so `|A| = |θ|`,
    `Â = e₁₂`, `(e₁₂)² = −1`) — in both algebras: the closed form equals the even versor
    `⟨cos θ, …, sin θ, …⟩`, and its squared magnitude is 1.

    The 𝒢₃ section also proves the GENERAL case `exp B = cos|B|·1 + sin|B|·B̂` for any nonzero
    bivector `B = p·e₁₂ + q·e₁₃ + r·e₂₃` (every 𝒢₃ bivector is simple): a unit versor, `normSq = 1`. -/
namespace GacalcProofs

namespace G2

/-- `exp(θ·e₁₂)` in 𝒢₂ by the closed form `cos θ·1 + sin θ·e₁₂`. -/
noncomputable def expBivector (θ : ℝ) : G2 :=
  add (smul (Real.cos θ) one) (smul (Real.sin θ) e_12)

/-- `exp(θ·e₁₂)` is the even versor `⟨cos θ, 0, 0, sin θ⟩` — so the rotor/sandwich layer applies. -/
theorem expBivector_eq_evenVersor (θ : ℝ) :
    expBivector θ = evenVersor (Real.cos θ) (Real.sin θ) := by
  simp only [expBivector, evenVersor, add, smul, one, e_12]; ext <;> ring

/-- **exp of a bivector is a unit versor (rotor):** `|exp(θ·e₁₂)|² = 1`. -/
theorem normSq_expBivector (θ : ℝ) : normSq (expBivector θ) = 1 := by
  rw [expBivector_eq_evenVersor, normSq_evenVersor]
  exact Real.cos_sq_add_sin_sq θ

/-- `exp(θ·e₁₂)` is a **rotor** (`IsRotor`: even and unit), so the reverse-form sandwich
    `sandwich_eq_reverse_sandwich_of_isRotor` applies to it. -/
theorem isRotor_expBivector (θ : ℝ) : IsRotor (expBivector θ) :=
  ⟨by rw [expBivector_eq_evenVersor]; exact isEvenVersor_evenVersor _ _, normSq_expBivector θ⟩

end G2

namespace G3

/-- `exp(θ·e₁₂)` in 𝒢₃ by the closed form `cos θ·1 + sin θ·e₁₂` (the `e₁₂` plane; `(e₁₂)² = −1`). -/
noncomputable def expBivector12 (θ : ℝ) : G3 :=
  add (smul (Real.cos θ) one) (smul (Real.sin θ) e_12)

/-- `exp(θ·e₁₂)` is the even versor `⟨cos θ, …, sin θ, 0, 0, …⟩`. -/
theorem expBivector12_eq_evenVersor (θ : ℝ) :
    expBivector12 θ = evenVersor (Real.cos θ) (Real.sin θ) 0 0 := by
  simp only [expBivector12, evenVersor, add, smul, one, e_12]; ext <;> ring

/-- **exp of a bivector is a unit versor (rotor):** `|exp(θ·e₁₂)|² = 1`. -/
theorem normSq_expBivector12 (θ : ℝ) : normSq (expBivector12 θ) = 1 := by
  simp only [normSq, expBivector12, add, smul, one, e_12, mul, reverse]
  linear_combination Real.sin_sq_add_cos_sq θ

/-- `exp(θ·e₁₂)` is a **rotor** (`IsRotor`: even and unit). -/
theorem isRotor_expBivector12 (θ : ℝ) : IsRotor (expBivector12 θ) :=
  ⟨by rw [expBivector12_eq_evenVersor]; exact isEvenVersor_evenVersor _ _ _ _, normSq_expBivector12 θ⟩

/-- `exp B` for a **general** nonzero 𝒢₃ bivector `B = p·e₁₂ + q·e₁₃ + r·e₂₃`, by the closed form
    `cos|B|·1 + sin|B|·B̂` with `B̂ = B/|B|` and `|B| = √(p²+q²+r²)` — i.e. `cos|B|·1 + (sin|B|/|B|)·B`.
    In 𝒢₃ every bivector is simple (`B² = −|B|²`), so this is the full bivector case. -/
noncomputable def expBivectorGeneral (p q r : ℝ) : G3 :=
  add (smul (Real.cos (Real.sqrt (p ^ 2 + q ^ 2 + r ^ 2))) one)
      (smul (Real.sin (Real.sqrt (p ^ 2 + q ^ 2 + r ^ 2)) / Real.sqrt (p ^ 2 + q ^ 2 + r ^ 2))
        (bivector p q r))

/-- **exp of a general bivector is a unit versor (rotor):** `|exp B|² = 1` for `B ≠ 0`
    (`p²+q²+r² ≠ 0`). `|exp B|² = cos²|B| + (sin|B|/|B|)²·(p²+q²+r²) = cos²|B| + sin²|B| = 1`,
    using `|B|² = p²+q²+r²`. -/
theorem normSq_expBivectorGeneral (p q r : ℝ) (h : p ^ 2 + q ^ 2 + r ^ 2 ≠ 0) :
    normSq (expBivectorGeneral p q r) = 1 := by
  have hS : (0 : ℝ) ≤ p ^ 2 + q ^ 2 + r ^ 2 := by positivity
  simp only [expBivectorGeneral, normSq, add, smul, one, bivector, mul, reverse, zero]
  set m := Real.sqrt (p ^ 2 + q ^ 2 + r ^ 2) with hm
  have hm2 : m ^ 2 = p ^ 2 + q ^ 2 + r ^ 2 := Real.sq_sqrt hS
  have hmne : m ≠ 0 := Real.sqrt_ne_zero'.mpr (lt_of_le_of_ne hS (Ne.symm h))
  have hpyth : Real.sin m ^ 2 + Real.cos m ^ 2 = 1 := Real.sin_sq_add_cos_sq m
  field_simp
  nlinarith [hpyth, hm2, hmne]

/-- **exp of a general bivector is a rotor** (`IsRotor`: even and unit) for `B ≠ 0`. -/
theorem isRotor_expBivectorGeneral (p q r : ℝ) (h : p ^ 2 + q ^ 2 + r ^ 2 ≠ 0) :
    IsRotor (expBivectorGeneral p q r) :=
  ⟨by refine ⟨?_, ?_, ?_, ?_⟩ <;> simp only [expBivectorGeneral, add, smul, one, bivector, zero] <;> ring,
   normSq_expBivectorGeneral p q r h⟩

end G3

end GacalcProofs
