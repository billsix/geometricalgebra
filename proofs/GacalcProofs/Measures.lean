import GacalcProofs.G2
import GacalcProofs.G3
import GacalcProofs.Trig
import GacalcProofs.Cross
import GacalcProofs.GradeProjection

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

/-- The **area** of the parallelogram on `a`, `b` = `|a ∧ b|` (gacalc `measure.area`), the 2D twin of
    `G3.area`. -/
noncomputable def area (a b : G2) : ℝ := magnitude (wedge a b)

/-- The **signed area** (2D) = the oriented wedge coefficient (gacalc `signed_area`), i.e. the `e₁₂`
    part of `a ∧ b`. -/
noncomputable def signedArea (a b : G2) : ℝ := (wedge a b).c12

/-- The signed area of two vectors is the oriented determinant `a₁*b₂ − a₂*b₁`. -/
theorem signedArea_eq {a b : G2} (ha : IsVector a) (hb : IsVector b) :
    signedArea a b = a.c1 * b.c2 - a.c2 * b.c1 := by
  obtain ⟨has, ha12⟩ := ha
  obtain ⟨hbs, hb12⟩ := hb
  simp only [signedArea, wedge, has, ha12, hbs, hb12]; ring

/-- **The signed area is the grade-2 (pseudoscalar) part** of `a ∧ b` — Python reads the top-grade
    coefficient; this records `signedArea = ⟨a∧b⟩₂`'s `e₁₂` component. -/
theorem signedArea_eq_rVectorPart_two (a b : G2) :
    signedArea a b = (rVectorPart 2 (wedge a b)).c12 := by
  simp only [signedArea, rVectorPart, smul, e_12]; ring

/-- The bivector `a∧b` carries only the `e₁₂` coefficient, so `|a∧b|² = signedArea²` (the 2D twin of
    `G3.normSq_wedge3_eq_signedVolume_sq`). -/
theorem normSq_wedge_eq_signedArea_sq {a b : G2} (ha : IsVector a) (hb : IsVector b) :
    normSq (wedge a b) = signedArea a b ^ 2 := by
  obtain ⟨has, ha12⟩ := ha
  obtain ⟨hbs, hb12⟩ := hb
  simp only [normSq, signedArea, wedge, mul, reverse, has, ha12, hbs, hb12]; ring

/-- `area² = signedArea²` — so `area = |signedArea| = |det[a,b]|`. -/
theorem area_sq_vec {a b : G2} (ha : IsVector a) (hb : IsVector b) :
    area a b ^ 2 = signedArea a b ^ 2 := by
  simp only [area, magnitude]
  rw [Real.sq_sqrt (by rw [normSq_wedge_eq_signedArea_sq ha hb]; exact sq_nonneg _)]
  exact normSq_wedge_eq_signedArea_sq ha hb

end G2

end GacalcProofs
