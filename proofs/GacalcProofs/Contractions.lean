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

/-- Left contraction `A ⌋ B = ⟨A B⟩_{m−k}` (grade of `A` is `k`, of `B` is `m`). -/
noncomputable def leftContraction (k m : ℕ) (a b : G3) : G3 := rVectorPart (m - k) (mul a b)

/-- Right contraction `A ⌊ B = ⟨A B⟩_{k−m}`. -/
noncomputable def rightContraction (k m : ℕ) (a b : G3) : G3 := rVectorPart (k - m) (mul a b)

/-- For two vectors (grade 1 each) the **left** contraction is the scalar dot `⟨ab⟩₀`. -/
theorem leftContraction_vec_vec {a b : G3} (ha : IsVector a) (hb : IsVector b) :
    leftContraction 1 1 a b = scalar (dot a b) := by
  obtain ⟨has, ha12, ha13, ha23, ha123⟩ := ha
  obtain ⟨hbs, hb12, hb13, hb23, hb123⟩ := hb
  simp only [leftContraction, rVectorPart, mul, scalar, dot, zero,
    has, ha12, ha13, ha23, ha123, hbs, hb12, hb13, hb23, hb123]

/-- For two vectors the **right** contraction is likewise the scalar dot `⟨ab⟩₀`. -/
theorem rightContraction_vec_vec {a b : G3} (ha : IsVector a) (hb : IsVector b) :
    rightContraction 1 1 a b = scalar (dot a b) := by
  obtain ⟨has, ha12, ha13, ha23, ha123⟩ := ha
  obtain ⟨hbs, hb12, hb13, hb23, hb123⟩ := hb
  simp only [rightContraction, rVectorPart, mul, scalar, dot, zero,
    has, ha12, ha13, ha23, ha123, hbs, hb12, hb13, hb23, hb123]

/-- **Grade-0 inclusion — the Taylor-vs-Hestenes difference.** A *scalar* `α` (grade 0) left-contracted
    with a vector `b` keeps the vector: `α ⌋ b = α·b` (grade `1−0 = 1`). The Hestenes dot
    (`inner_product`) of a grade-0 operand is `0`, so the contraction genuinely differs here.
    (`α` is a genuine scalar parameter — stays `ℝ`; `b` is a vector object.) -/
theorem leftContraction_scalar_vec (α : ℝ) {b : G3} (hb : IsVector b) :
    leftContraction 0 1 (scalar α) b = smul α b := by
  obtain ⟨hbs, hb12, hb13, hb23, hb123⟩ := hb
  simp only [leftContraction, rVectorPart, mul, scalar, smul, zero,
    hbs, hb12, hb13, hb23, hb123]
  ext <;> ring

end G3

end GacalcProofs
