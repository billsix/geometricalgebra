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
theorem area_sq_vec {a b : G3} (ha : IsVector a) (hb : IsVector b) :
    area a b ^ 2 = normSq (wedge a b) := by
  have h : (0 : ℝ) ≤ normSq (wedge a b) := by
    rw [eq_vec_of_isVector ha, eq_vec_of_isVector hb, normSq_wedge_vec]; positivity
  simp only [area, magnitude]
  exact Real.sq_sqrt h

/-- **Lagrange form of the area:** `|a∧b|² = |a|²|b|² − (a·b)²` (rearranged `lagrange_property`). -/
theorem normSq_wedge_eq_lagrange {a b : G3} (ha : IsVector a) (hb : IsVector b) :
    normSq (wedge a b) = normSq a * normSq b - dot a b ^ 2 := by
  have h := lagrange_property ha hb
  linarith

/-- The **volume** of the parallelepiped on `a,b,c` = `|a ∧ b ∧ c|` (gacalc `measure.volume`). -/
noncomputable def volume (a b c : G3) : ℝ := magnitude (wedge (wedge a b) c)

/-- The trivector `a∧b∧c` carries only the `e₁₂₃` coefficient, so `|a∧b∧c|² = signedVolume²`. -/
theorem normSq_wedge3_eq_signedVolume_sq {a b c : G3}
    (ha : IsVector a) (hb : IsVector b) (hc : IsVector c) :
    normSq (wedge (wedge a b) c) = signedVolume a b c ^ 2 := by
  obtain ⟨has, ha12, ha13, ha23, ha123⟩ := ha
  obtain ⟨hbs, hb12, hb13, hb23, hb123⟩ := hb
  obtain ⟨hcs, hc12, hc13, hc23, hc123⟩ := hc
  simp only [normSq, signedVolume, wedge, mul, reverse,
    has, ha12, ha13, ha23, ha123, hbs, hb12, hb13, hb23, hb123, hcs, hc12, hc13, hc23, hc123]
  ring

/-- `volume² = signedVolume²` — so `volume = |signedVolume| = |det[a,b,c]|`. -/
theorem volume_sq_vec {a b c : G3} (ha : IsVector a) (hb : IsVector b) (hc : IsVector c) :
    volume a b c ^ 2 = signedVolume a b c ^ 2 := by
  simp only [volume, magnitude]
  rw [Real.sq_sqrt (by rw [normSq_wedge3_eq_signedVolume_sq ha hb hc]; exact sq_nonneg _)]
  exact normSq_wedge3_eq_signedVolume_sq ha hb hc

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

end G2

end GacalcProofs
