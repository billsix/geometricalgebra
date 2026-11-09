import GacalcProofs.Versor2D

/-! # Orthogonality / parallelism predicates (𝒢₂)

    The 2D twin of `Predicates3D.lean`. Parallelism is the wedge test: `a ∧ b = 0 ⟺ b = k*a` for a
    nonzero vector `a` (`wedge_eq_zero_iff_parallel`). It states perpendicularity through the named scalar
    product `dot` (⟨A B⟩₀, defined in `Versor2D.lean`) over an arbitrary vector (`IsVector`),
    rather than by reading a raw coordinate field — the object/named-function form of the
    coordinate leaf `G2.dual_vec_perp` (`G2.lean`), which stays as the bridge it rests on. -/
namespace GacalcProofs.G2

/-- **The dual of a vector is perpendicular to it** (2D): for any vector `v` (`IsVector`), the dot
    product of its dual with itself is zero, `(v*) · v = 0`. The named-`dot`, object-level form of
    the coordinate leaf `dual_vec_perp`. -/
theorem dual_perp_dot {v : G2} (hv : IsVector v) : dot (dual v) v = 0 := by
  obtain ⟨hs, h12⟩ := hv
  simp only [dot, dual, I_inv, mul, hs, h12]; ring

/-- **A vector is parallel to its scalar multiples** (2D): `a ∧ (k*a) = 0`, including the
    anti-parallel `k < 0` case. The 2D twin of `G3.wedge_parallel_smul`. -/
theorem wedge_parallel_smul {a : G2} (ha : IsVector a) (k : ℝ) :
    wedge a (smul k a) = (⟨0, 0, 0, 0⟩ : G2) := by
  obtain ⟨has, ha12⟩ := ha
  ext <;> simp only [wedge, smul, has, ha12] <;> ring

/-- **Wedge zero ⟹ parallel** (2D): for vectors `a`, `b` with `a ≠ 0`, if `a ∧ b = 0` (that is,
    `a₁*b₂ = a₂*b₁`) then `b = k*a` for some real `k`. The 2D twin of `G3.parallel_of_wedge_eq_zero`. -/
theorem parallel_of_wedge_eq_zero {a b : G2} (ha : IsVector a) (hb : IsVector b)
    (ha0 : a ≠ (⟨0, 0, 0, 0⟩ : G2)) (h : wedge a b = (⟨0, 0, 0, 0⟩ : G2)) :
    ∃ k : ℝ, b = smul k a := by
  obtain ⟨has, ha12⟩ := ha
  obtain ⟨hbs, hb12⟩ := hb
  have h12 : a.c1 * b.c2 - a.c2 * b.c1 = 0 := by
    have hc := congrArg G2.c12 h
    simp only [wedge, ha12, hbs, has, hb12] at hc
    linear_combination hc
  by_cases h1 : a.c1 = 0
  · by_cases h2 : a.c2 = 0
    · exact absurd (by ext <;> assumption) ha0
    · have hb1 : b.c1 = 0 := by
        have hp : a.c2 * b.c1 = 0 := by rw [h1] at h12; linear_combination -h12
        exact (mul_eq_zero.mp hp).resolve_left h2
      refine ⟨b.c2 / a.c2, ?_⟩
      ext <;> simp only [smul, has, hbs, ha12, hb12, h1, hb1, mul_zero]
      field_simp
  · refine ⟨b.c1 / a.c1, ?_⟩
    ext <;> simp only [smul, has, hbs, ha12, hb12, mul_zero]
    · field_simp
    · field_simp; linear_combination h12

/-- **`a ∧ b = 0 ⟺ a ∥ b`** (2D) for vectors with `a ≠ 0`. -/
theorem wedge_eq_zero_iff_parallel {a b : G2} (ha : IsVector a) (hb : IsVector b)
    (ha0 : a ≠ (⟨0, 0, 0, 0⟩ : G2)) :
    wedge a b = (⟨0, 0, 0, 0⟩ : G2) ↔ ∃ k : ℝ, b = smul k a :=
  ⟨parallel_of_wedge_eq_zero ha hb ha0, fun ⟨k, hk⟩ => hk ▸ wedge_parallel_smul ha k⟩

end GacalcProofs.G2
