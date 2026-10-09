import GacalcProofs.G3
import GacalcProofs.Sandwich

/-! # `normalize` — unit magnitude (𝒢₃)

    gacalc's `normalize` (base.py: `A*|A|⁻¹` = `(1/|A|)*A`) rescales to magnitude 1. This proves,
    for the vector case, that it does: `normSq (normalize v) = 1`, hence `magnitude (normalize v) = 1`,
    given `normSq v ≠ 0`. Kept squared (`normSq`) per the proof conventions; the single `√` step uses
    `Real.sq_sqrt` on `normSq (vec …) = a1²+a2²+a3² ≥ 0`. From the coverage-map gap audit
    (`tasks/archive/2026/10/01/lean-coverage-gap-audit.md`). -/
namespace GacalcProofs.G3

/-- `normalize v = (1/|v|)*v` (gacalc `normalize`). -/
noncomputable def normalizeVec (a : G3) : G3 := smul (1 / magnitude a) a

/-- A normalized nonzero vector has unit squared-magnitude (object form). -/
theorem normSq_normalizeVec {a : G3} (ha_isv : IsVector a) (h : normSq a ≠ 0) :
    normSq (normalizeVec a) = 1 := by
  rw [eq_vec_of_isVector ha_isv]
  have h' : normSq (vec a.c1 a.c2 a.c3) ≠ 0 := by rw [← eq_vec_of_isVector ha_isv]; exact h
  have hpos : (0 : ℝ) ≤ normSq (vec a.c1 a.c2 a.c3) := by rw [normSq_vec]; positivity
  simp only [normalizeVec]
  rw [normSq_smul]
  simp only [magnitude]
  rw [div_pow, one_pow, Real.sq_sqrt hpos, one_div, inv_mul_cancel₀ h']

/-- …hence unit magnitude (object form). -/
theorem magnitude_normalizeVec {a : G3} (ha_isv : IsVector a) (h : normSq a ≠ 0) :
    magnitude (normalizeVec a) = 1 := by
  simp only [magnitude]
  rw [normSq_normalizeVec ha_isv h, Real.sqrt_one]
