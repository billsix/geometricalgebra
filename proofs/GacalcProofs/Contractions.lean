import GacalcProofs.G3
import GacalcProofs.GradeProjection

/-! # Left and right contraction (Taylor 2021, p.103)

    `leftContraction k m A B = ⟨A B⟩_{m−k}` and `rightContraction k m A B = ⟨A B⟩_{k−m}`, for a
    grade-`k` `A` and grade-`m` `B` (gacalc `left_contraction`/`right_contraction`, base.py).
    The operand grades are passed explicitly (the concrete struct carries no grade tag). Unlike the
    Hestenes dot (`inner_product`), the contractions **include grade 0** — see
    `tasks/reference/contraction-and-dot-definitions.md`; `leftContraction_scalar_vec` below exhibits
    that difference. -/
namespace GacalcProofs

namespace G3

/-- Left contraction `A ⌋ B = ⟨A B⟩_{m−k}` (grade of `A` is `k`, of `B` is `m`), zero when `m < k`: a
    bigger blade cannot be contracted out of a smaller one (gacalc `left_contraction`; the grade
    subtraction is in ℕ, so the `k ≤ m` guard is what keeps `m − k` from truncating to grade 0). -/
noncomputable def leftContraction (k m : ℕ) (a b : G3) : G3 :=
  if k ≤ m then rVectorPart (m - k) (mul a b) else zero

/-- Right contraction `A ⌊ B = ⟨A B⟩_{k−m}`, zero when `k < m`. -/
noncomputable def rightContraction (k m : ℕ) (a b : G3) : G3 :=
  if m ≤ k then rVectorPart (k - m) (mul a b) else zero

/-- **A bigger blade cannot be contracted out of a smaller one:** if the left grade `k` exceeds the
    right grade `m`, the left contraction is zero (gacalc's `(e_1 * e_2) ⌋ e_1 = 0`). -/
theorem leftContraction_eq_zero_of_lt {k m : ℕ} (h : m < k) (a b : G3) :
    leftContraction k m a b = zero := by
  simp [leftContraction, Nat.not_le.mpr h]

/-- The mirror: if the right grade `m` exceeds the left grade `k`, the right contraction is zero. -/
theorem rightContraction_eq_zero_of_lt {k m : ℕ} (h : k < m) (a b : G3) :
    rightContraction k m a b = zero := by
  simp [rightContraction, Nat.not_le.mpr h]

/-- **Grade `k = m`:** equal grades contract to the grade-0 part, the scalar `⟨a b⟩₀`, from either side. -/
theorem leftContraction_same_grade (k : ℕ) (a b : G3) :
    leftContraction k k a b = rVectorPart 0 (mul a b) := by
  simp [leftContraction]

/-- Likewise for the right contraction. -/
theorem rightContraction_same_grade (k : ℕ) (a b : G3) :
    rightContraction k k a b = rVectorPart 0 (mul a b) := by
  simp [rightContraction]

/-- For two vectors (grade 1 each) the **left** contraction is the scalar dot `⟨ab⟩₀`. -/
theorem leftContraction_vec_vec {a b : G3} (ha : IsVector a) (hb : IsVector b) :
    leftContraction 1 1 a b = scalar (dot a b) := by
  obtain ⟨has, ha12, ha13, ha23, ha123⟩ := ha
  obtain ⟨hbs, hb12, hb13, hb23, hb123⟩ := hb
  simp only [leftContraction, Nat.le_refl, ↓reduceIte, rVectorPart, mul, scalar, dot, zero,
    has, ha12, ha13, ha23, ha123, hbs, hb12, hb13, hb23, hb123]

/-- For two vectors the **right** contraction is likewise the scalar dot `⟨ab⟩₀`. -/
theorem rightContraction_vec_vec {a b : G3} (ha : IsVector a) (hb : IsVector b) :
    rightContraction 1 1 a b = scalar (dot a b) := by
  obtain ⟨has, ha12, ha13, ha23, ha123⟩ := ha
  obtain ⟨hbs, hb12, hb13, hb23, hb123⟩ := hb
  simp only [rightContraction, Nat.le_refl, ↓reduceIte, rVectorPart, mul, scalar, dot, zero,
    has, ha12, ha13, ha23, ha123, hbs, hb12, hb13, hb23, hb123]

/-- **Grade-0 inclusion — the Taylor-vs-Hestenes difference.** A *scalar* `α` (grade 0) left-contracted
    with a vector `b` keeps the vector: `α ⌋ b = α·b` (grade `1−0 = 1`). The Hestenes dot
    (`inner_product`) of a grade-0 operand is `0`, so the contraction genuinely differs here.
    (`α` is a genuine scalar parameter — stays `ℝ`; `b` is a vector object.) -/
theorem leftContraction_scalar_vec (α : ℝ) {b : G3} (hb : IsVector b) :
    leftContraction 0 1 (scalar α) b = smul α b := by
  obtain ⟨hbs, hb12, hb13, hb23, hb123⟩ := hb
  simp only [leftContraction, Nat.zero_le, ↓reduceIte, rVectorPart, mul, scalar, smul, zero,
    hbs, hb12, hb13, hb23, hb123]
  ext <;> ring

end G3

end GacalcProofs
