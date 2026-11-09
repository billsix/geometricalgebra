import GacalcProofs.G3

/-! # Orthogonality / parallelism predicates (𝒢₃)

    The geometric content of gacalc's two vector predicates:

    * `is_orthogonal_to` (base.py) tests `a·b = 0`. Its geometric meaning: the product is a pure
      wedge, `a b = a ∧ b` (no scalar part) — proved both ways below (`perp_iff_mul_eq_wedge`).
    * `is_parallel_to` tests `a ∧ b = 0` — the wedge vanishing (linear dependence), so anti-parallel
      vectors count as parallel; a vector is parallel to its scalar multiples, `a ∧ (k·a) = 0`
      (`wedge_parallel_smul`), and the converse holds for `a ≠ 0` (`parallel_of_wedge_eq_zero`), so
      `a ∧ b = 0 ⟺ b = k*a` (`wedge_eq_zero_iff_parallel`).

    From the coverage-map gap audit (`tasks/archive/2026/10/01/lean-coverage-gap-audit.md`). -/
namespace GacalcProofs.G3

/-- **Orthogonality ⟺ the product is a pure wedge**: for vectors `a`, `b`, `a ⊥ b` (`a·b = 0`,
    gacalc `is_orthogonal_to`) iff `a b = a ∧ b`. Forward is `mul_eq_wedge_of_perp`; backward reads
    the scalar part (`(a b).s = a·b`, `(a ∧ b).s = 0`). -/
theorem perp_iff_mul_eq_wedge {a b : G3} (ha : IsVector a) (hb : IsVector b) :
    dot a b = 0 ↔ mul a b = wedge a b := by
  constructor
  · exact mul_eq_wedge_of_perp ha hb
  · intro h
    have hs : (mul a b).s = (wedge a b).s := by rw [h]
    simp only [dot]
    rw [hs]
    -- (a ∧ b).s = a.s*b.s (the outer product keeps the scalar×scalar part); a.s = 0 for a vector.
    simp only [wedge]
    rw [ha.1, MulZeroClass.zero_mul]

/-- **A vector is parallel to its scalar multiples**: `a ∧ (k·a) = 0` — the correct geometric
    "parallel" (the outer product / linear dependence vanishes), including the anti-parallel `k < 0`
    case. See the module note on the Python `is_parallel_to`'s narrower `cosine == 1`. -/
theorem wedge_parallel_smul {a : G3} (ha : IsVector a) (k : ℝ) :
    wedge a (smul k a) = zero := by
  obtain ⟨has, ha12, ha13, ha23, ha123⟩ := ha
  ext <;> simp only [wedge, smul, zero, has, ha12, ha13, ha23, ha123] <;> ring

/-- **Wedge zero ⟹ parallel** (the converse of `wedge_parallel_smul`): for vectors `a`, `b` with
    `a ≠ 0`, if `a ∧ b = 0` then `b = k*a` for some real `k`. The three bivector components of
    `a ∧ b` say `a₁*b₂ = a₂*b₁`, `a₁*b₃ = a₃*b₁`, `a₂*b₃ = a₃*b₂`; dividing by a nonzero component of
    `a` gives `k`, and those equations give the other components. -/
theorem parallel_of_wedge_eq_zero {a b : G3} (ha : IsVector a) (hb : IsVector b)
    (ha0 : a ≠ zero) (h : wedge a b = zero) : ∃ k : ℝ, b = smul k a := by
  obtain ⟨has, ha12, ha13, ha23, ha123⟩ := ha
  obtain ⟨hbs, hb12, hb13, hb23, hb123⟩ := hb
  -- The three bivector components of `a ∧ b = 0`.
  have h12 : a.c1 * b.c2 - a.c2 * b.c1 = 0 := by
    have hc := congrArg G3.c12 h
    simp only [wedge, zero, ha12, hbs, has, hb12] at hc
    linear_combination hc
  have h13 : a.c1 * b.c3 - a.c3 * b.c1 = 0 := by
    have hc := congrArg G3.c13 h
    simp only [wedge, zero, ha13, hbs, has, hb13] at hc
    linear_combination hc
  have h23 : a.c2 * b.c3 - a.c3 * b.c2 = 0 := by
    have hc := congrArg G3.c23 h
    simp only [wedge, zero, ha23, hbs, has, hb23] at hc
    linear_combination hc
  -- Divide by a nonzero component of `a`; the equations give the other components.
  by_cases h1 : a.c1 = 0
  · by_cases h2 : a.c2 = 0
    · by_cases h3 : a.c3 = 0
      · exact absurd (by ext <;> simp only [zero] <;> assumption) ha0
      · have hb1 : b.c1 = 0 := by
          have hp : a.c3 * b.c1 = 0 := by rw [h1] at h13; linear_combination -h13
          exact (mul_eq_zero.mp hp).resolve_left h3
        have hb2 : b.c2 = 0 := by
          have hp : a.c3 * b.c2 = 0 := by rw [h2] at h23; linear_combination -h23
          exact (mul_eq_zero.mp hp).resolve_left h3
        refine ⟨b.c3 / a.c3, ?_⟩
        ext <;> simp only [smul, has, hbs, ha12, hb12, ha13, hb13, ha23, hb23, ha123, hb123,
          h1, h2, hb1, hb2, mul_zero]
        field_simp
    · have hb1 : b.c1 = 0 := by
        have hp : a.c2 * b.c1 = 0 := by rw [h1] at h12; linear_combination -h12
        exact (mul_eq_zero.mp hp).resolve_left h2
      refine ⟨b.c2 / a.c2, ?_⟩
      ext <;> simp only [smul, has, hbs, ha12, hb12, ha13, hb13, ha23, hb23, ha123, hb123,
        h1, hb1, mul_zero]
      · field_simp
      · field_simp; linear_combination h23
  · refine ⟨b.c1 / a.c1, ?_⟩
    ext <;> simp only [smul, has, hbs, ha12, hb12, ha13, hb13, ha23, hb23, ha123, hb123, mul_zero]
    · field_simp
    · field_simp; linear_combination h12
    · field_simp; linear_combination h13

/-- **`a ∧ b = 0 ⟺ a ∥ b`** for vectors with `a ≠ 0`: the wedge vanishes exactly when `b` is a real
    multiple of `a` — the equivalence gacalc's `is_parallel_to` rests on. Forward is
    `parallel_of_wedge_eq_zero`, backward is `wedge_parallel_smul`. -/
theorem wedge_eq_zero_iff_parallel {a b : G3} (ha : IsVector a) (hb : IsVector b)
    (ha0 : a ≠ zero) : wedge a b = zero ↔ ∃ k : ℝ, b = smul k a :=
  ⟨parallel_of_wedge_eq_zero ha hb ha0, fun ⟨k, hk⟩ => hk ▸ wedge_parallel_smul ha k⟩
