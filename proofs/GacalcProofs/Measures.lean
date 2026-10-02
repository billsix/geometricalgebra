import GacalcProofs.G2
import GacalcProofs.G3
import GacalcProofs.Trig
import GacalcProofs.Cross

/-! # Measures: area, volume, signed area (Williamson & Trotter 1979)

    gacalc's named measures (`measure.py`): `area a b = |a∧b|`, `volume a b c = |a∧b∧c|`, and the 2D
    `signed_area` = the oriented wedge coefficient. `signed_volume` is already covered
    (`Cross.dot_cross_eq_signedVolume = det[a,b,c]`). Kept squared to avoid `√`. The general `content`
    (`|a₁∧…∧aₖ|`, arbitrary `k`) waits on the general-`Gn` Lean layer; here area/volume are its `k=2,3`
    instances. -/
namespace GacalcProofs

namespace G3

/-- The **area** of the parallelogram on `a`, `b` = `|a ∧ b|` (gacalc `measure.area`). -/
noncomputable def area (a b : G3) : ℝ := magnitude (wedge a b)

/-- `area² = |a∧b|²` on vectors (squared form; `normSq (wedge ..) ≥ 0`). -/
theorem area_sq_vec (a1 a2 a3 b1 b2 b3 : ℝ) :
    area (vec a1 a2 a3) (vec b1 b2 b3) ^ 2
      = normSq (wedge (vec a1 a2 a3) (vec b1 b2 b3)) := by
  have h : (0 : ℝ) ≤ normSq (wedge (vec a1 a2 a3) (vec b1 b2 b3)) := by
    rw [normSq_wedge_vec]; positivity
  simp only [area, magnitude]
  exact Real.sq_sqrt h

/-- **Lagrange form of the area:** `|a∧b|² = |a|²|b|² − (a·b)²` (rearranged `lagrange_property`). -/
theorem normSq_wedge_eq_lagrange (a1 a2 a3 b1 b2 b3 : ℝ) :
    normSq (wedge (vec a1 a2 a3) (vec b1 b2 b3))
      = normSq (vec a1 a2 a3) * normSq (vec b1 b2 b3)
        - dot (vec a1 a2 a3) (vec b1 b2 b3) ^ 2 := by
  have h := lagrange_property a1 a2 a3 b1 b2 b3
  linarith

/-- The **volume** of the parallelepiped on `a,b,c` = `|a ∧ b ∧ c|` (gacalc `measure.volume`). -/
noncomputable def volume (a b c : G3) : ℝ := magnitude (wedge (wedge a b) c)

/-- The trivector `a∧b∧c` carries only the `e₁₂₃` coefficient, so `|a∧b∧c|² = signedVolume²`. -/
theorem normSq_wedge3_eq_signedVolume_sq (a1 a2 a3 b1 b2 b3 c1 c2 c3 : ℝ) :
    normSq (wedge (wedge (vec a1 a2 a3) (vec b1 b2 b3)) (vec c1 c2 c3))
      = signedVolume (vec a1 a2 a3) (vec b1 b2 b3) (vec c1 c2 c3) ^ 2 := by
  simp only [normSq, signedVolume, wedge, mul, reverse, vec]; ring

/-- `volume² = signedVolume²` — so `volume = |signedVolume| = |det[a,b,c]|`. -/
theorem volume_sq_vec (a1 a2 a3 b1 b2 b3 c1 c2 c3 : ℝ) :
    volume (vec a1 a2 a3) (vec b1 b2 b3) (vec c1 c2 c3) ^ 2
      = signedVolume (vec a1 a2 a3) (vec b1 b2 b3) (vec c1 c2 c3) ^ 2 := by
  simp only [volume, magnitude]
  rw [Real.sq_sqrt (by rw [normSq_wedge3_eq_signedVolume_sq]; exact sq_nonneg _)]
  exact normSq_wedge3_eq_signedVolume_sq a1 a2 a3 b1 b2 b3 c1 c2 c3

-- TODO (deferred): the GENERAL `content |a₁∧…∧aₖ|` for arbitrary grade `k` needs a dimension-general
-- `Gn` Lean representation, which does not exist here (these proofs use the concrete G2/G3 structs).
-- Building it is the prerequisite task `tasks/lean-general-gn-product-and-hestenes-dot-wedge.md`
-- (deliberately deferred). `area` (k=2) and `volume` (k=3) above are its concrete instances.

end G3

namespace G2

/-- The **signed area** (2D) = the oriented wedge coefficient (gacalc `signed_area`), i.e. the `e₁₂`
    part of `a b` — the signed `a₁b₂ − a₂b₁` (= the 2×2 determinant). -/
noncomputable def signedArea (a1 a2 b1 b2 : ℝ) : ℝ := (mul (vec a1 a2) (vec b1 b2)).c12

/-- The signed area is the oriented determinant `a₁b₂ − a₂b₁`. -/
theorem signedArea_eq (a1 a2 b1 b2 : ℝ) :
    signedArea a1 a2 b1 b2 = a1 * b2 - a2 * b1 := by
  simp only [signedArea, mul, vec]; ring

/-- `|signed_area| = area`: the area is the magnitude of the signed area (squared, `(a₁b₂−a₂b₁)²`). -/
theorem signedArea_sq (a1 a2 b1 b2 : ℝ) :
    signedArea a1 a2 b1 b2 ^ 2 = (a1 * b2 - a2 * b1) ^ 2 := by
  rw [signedArea_eq]

end G2

end GacalcProofs
