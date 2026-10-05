import GacalcProofs.G2
import GacalcProofs.G3
import GacalcProofs.Projection2D
import GacalcProofs.Cross
import GacalcProofs.Rotation2D

/-! # Bridges to Mathlib's general objects — "equivalence to the general case"

    The from-scratch algebras `G2`/`G3` prove facts about their own definitions. This module is the
    bridge the umbrella task's decisions 4 and 6 ask for: the from-scratch quantities ARE the standard
    ones, so Mathlib's library of theorems about the standard objects provably applies to them.

      * **dot** — `toE` maps a vector into `EuclideanSpace ℝ (Fin n)`; `dot a b = ⟪toE a, toE b⟫_ℝ` and
        `‖toE a‖ = magnitude a`. Payoff: symmetry and Cauchy–Schwarz on `G2`/`G3`, *proved by citing*
        Mathlib's `real_inner_comm` / `abs_real_inner_le_norm`.
      * **wedge** — the 2D wedge is the `2×2` determinant (`Matrix.det_fin_two_of`); the 3D wedge's
        three components are the three minors; the dual of the 3D wedge is Mathlib's `crossProduct`,
        and the signed volume is `Matrix.det` of the three rows (`triple_product_eq_det`).
      * **rotation** — `toC` reads a 𝒢₂ vector as a complex number; `rot θ` is `Complex.orientation.rotation θ`
        (Mathlib's `Orientation.rotation` on the oriented plane ℂ), and so is the from-scratch 2D
        versor sandwich `R v R̃` via `sandwich_rotor`.

    The constructions stay standalone (decision 2026-09-28); Mathlib is mapped in only here. -/
namespace GacalcProofs

open Matrix

/-- ℂ is a real plane — the instance `Orientation.rotation` needs; Mathlib states the dimension as a
    theorem (`Complex.finrank_real_complex`), so register it as a local `Fact`. -/
local instance : Fact (Module.finrank ℝ ℂ = 2) := ⟨Complex.finrank_real_complex⟩

/-! ### Dot ↦ `inner`, wedge ↦ `det` (2D) -/
namespace G2

/-- A 𝒢₂ element's vector coordinates as a point of Mathlib's Euclidean plane. -/
noncomputable def toE (a : G2) : EuclideanSpace ℝ (Fin 2) := WithLp.toLp 2 ![a.c1, a.c2]

/-- **The from-scratch dot IS Mathlib's inner product** (2D), for vectors. -/
theorem dot_eq_inner {a b : G2} (ha : IsVector a) (hb : IsVector b) :
    dot a b = @inner ℝ _ _ (toE a) (toE b) := by
  obtain ⟨has, ha12⟩ := ha
  obtain ⟨hbs, hb12⟩ := hb
  simp [toE, EuclideanSpace.inner_toLp_toLp, dotProduct, Fin.sum_univ_two, dot, mul, has, ha12, hbs,
        hb12]; ring

/-- **The from-scratch magnitude IS Mathlib's norm** (2D), for vectors. -/
theorem norm_toE {a : G2} (ha : IsVector a) : ‖toE a‖ = magnitude a := by
  obtain ⟨has, ha12⟩ := ha
  rw [EuclideanSpace.norm_eq, magnitude]
  congr 1
  simp [toE, Fin.sum_univ_two, normSq, mul, reverse, has, ha12]; ring

/-- Symmetry of the dot, proved by citing Mathlib's `real_inner_comm` through the bridge. -/
theorem dot_comm_of_inner {a b : G2} (ha : IsVector a) (hb : IsVector b) : dot a b = dot b a := by
  rw [dot_eq_inner ha hb, dot_eq_inner hb ha, real_inner_comm]

/-- **Cauchy–Schwarz** on 𝒢₂ vectors, by citing Mathlib's `abs_real_inner_le_norm` through the bridge. -/
theorem abs_dot_le_magnitude_mul {a b : G2} (ha : IsVector a) (hb : IsVector b) :
    |dot a b| ≤ magnitude a * magnitude b := by
  rw [dot_eq_inner ha hb, ← norm_toE ha, ← norm_toE hb]
  exact abs_real_inner_le_norm _ _

/-- **The 2D wedge is the `2×2` determinant** of the two coordinate rows. -/
theorem wedge_eq_det {a b : G2} (ha : IsVector a) (hb : IsVector b) :
    (wedge a b).c12 = Matrix.det !![a.c1, a.c2; b.c1, b.c2] := by
  obtain ⟨has, ha12⟩ := ha
  obtain ⟨hbs, hb12⟩ := hb
  rw [Matrix.det_fin_two_of]
  simp only [wedge, has, ha12, hbs, hb12]; ring

end G2

/-! ### Dot ↦ `inner`, wedge ↦ minors / `crossProduct` / `det` (3D) -/
namespace G3

/-- A 𝒢₃ element's vector coordinates as a point of Mathlib's Euclidean 3-space. -/
noncomputable def toE (a : G3) : EuclideanSpace ℝ (Fin 3) := WithLp.toLp 2 ![a.c1, a.c2, a.c3]

/-- The same coordinates as a plain `Fin 3 → ℝ` — the form Mathlib's `crossProduct` and `Matrix.det` use. -/
def toF (a : G3) : Fin 3 → ℝ := ![a.c1, a.c2, a.c3]

theorem dot_eq_inner {a b : G3} (ha : IsVector a) (hb : IsVector b) :
    dot a b = @inner ℝ _ _ (toE a) (toE b) := by
  obtain ⟨has, ha12, ha13, ha23, ha123⟩ := ha
  obtain ⟨hbs, hb12, hb13, hb23, hb123⟩ := hb
  simp [toE, EuclideanSpace.inner_toLp_toLp, dotProduct, Fin.sum_univ_three, dot, mul, has, ha12, ha13,
        ha23, ha123, hbs, hb12, hb13, hb23, hb123]; ring

theorem norm_toE {a : G3} (ha : IsVector a) : ‖toE a‖ = magnitude a := by
  obtain ⟨has, ha12, ha13, ha23, ha123⟩ := ha
  rw [EuclideanSpace.norm_eq, magnitude]
  congr 1
  simp [toE, Fin.sum_univ_three, normSq, mul, reverse, has, ha12, ha13, ha23, ha123]; ring

theorem dot_comm_of_inner {a b : G3} (ha : IsVector a) (hb : IsVector b) : dot a b = dot b a := by
  rw [dot_eq_inner ha hb, dot_eq_inner hb ha, real_inner_comm]

/-- **Cauchy–Schwarz** on 𝒢₃ vectors, by citing Mathlib's `abs_real_inner_le_norm`. -/
theorem abs_dot_le_magnitude_mul {a b : G3} (ha : IsVector a) (hb : IsVector b) :
    |dot a b| ≤ magnitude a * magnitude b := by
  rw [dot_eq_inner ha hb, ← norm_toE ha, ← norm_toE hb]
  exact abs_real_inner_le_norm _ _

/-- **The 3D wedge's components are the three `2×2` minors** of the two coordinate rows. -/
theorem wedge_c12_eq_det {a b : G3} (ha : IsVector a) (hb : IsVector b) :
    (wedge a b).c12 = Matrix.det !![a.c1, a.c2; b.c1, b.c2] := by
  obtain ⟨has, ha12, ha13, ha23, ha123⟩ := ha
  obtain ⟨hbs, hb12, hb13, hb23, hb123⟩ := hb
  rw [Matrix.det_fin_two_of]
  simp only [wedge, has, ha12, ha13, ha23, ha123, hbs, hb12, hb13, hb23, hb123]; ring

theorem wedge_c13_eq_det {a b : G3} (ha : IsVector a) (hb : IsVector b) :
    (wedge a b).c13 = Matrix.det !![a.c1, a.c3; b.c1, b.c3] := by
  obtain ⟨has, ha12, ha13, ha23, ha123⟩ := ha
  obtain ⟨hbs, hb12, hb13, hb23, hb123⟩ := hb
  rw [Matrix.det_fin_two_of]
  simp only [wedge, has, ha12, ha13, ha23, ha123, hbs, hb12, hb13, hb23, hb123]; ring

theorem wedge_c23_eq_det {a b : G3} (ha : IsVector a) (hb : IsVector b) :
    (wedge a b).c23 = Matrix.det !![a.c2, a.c3; b.c2, b.c3] := by
  obtain ⟨has, ha12, ha13, ha23, ha123⟩ := ha
  obtain ⟨hbs, hb12, hb13, hb23, hb123⟩ := hb
  rw [Matrix.det_fin_two_of]
  simp only [wedge, has, ha12, ha13, ha23, ha123, hbs, hb12, hb13, hb23, hb123]; ring

/-- **The from-scratch cross product IS Mathlib's `crossProduct`** (`⨯₃`), for vectors. -/
theorem toF_cross {a b : G3} (ha : IsVector a) (hb : IsVector b) :
    toF (cross a b) = toF a ⨯₃ toF b := by
  rw [eq_vec_of_isVector ha, eq_vec_of_isVector hb, cross_vec, cross_apply]
  ext i; fin_cases i <;> simp [toF, vec]

/-- **The signed volume is a determinant:** `signedVolume a b c = det ![a, b, c]`, through Mathlib's
    `triple_product_eq_det` (`a ⬝ᵥ (b ⨯₃ c) = det ![a, b, c]`) and the from-scratch
    `dot_cross_eq_signedVolume`. -/
theorem signedVolume_eq_det {a b c : G3} (ha : IsVector a) (hb : IsVector b) (hc : IsVector c) :
    signedVolume a b c = Matrix.det ![toF a, toF b, toF c] := by
  rw [← triple_product_eq_det, ← toF_cross hb hc, ← dot_cross_eq_signedVolume ha hb hc]
  rw [eq_vec_of_isVector ha, eq_vec_of_isVector hb, eq_vec_of_isVector hc, cross_vec]
  simp [dot, mul, toF, vec, dotProduct, Fin.sum_univ_three]

end G3

/-! ### Rotation ↦ `Orientation.rotation` (on the oriented plane ℂ) -/

/-- A 𝒢₂ vector as a complex number — Mathlib's oriented plane — read off its named components:
    `c1` (the e₁ coefficient) is the real part, `c2` (the e₂ coefficient) the imaginary part. -/
noncomputable def toC (v : G2) : ℂ := ⟨v.c1, v.c2⟩

/-- **The from-scratch rotation IS Mathlib's `Orientation.rotation`:** `rot θ` on 𝒢₂ vectors is rotation
    by the angle `θ` for the standard orientation of ℂ (`Complex.orientation`), whose right-angle
    rotation is multiplication by `I`. Holds for every `v` (both sides read only `c1`/`c2`). -/
theorem toC_rot (θ : ℝ) (v : G2) :
    toC (rot θ v) = Complex.orientation.rotation (θ : Real.Angle) (toC v) := by
  rw [Orientation.rotation_apply, Complex.rightAngleRotation]
  apply Complex.ext <;>
    simp [toC, rot, G2.vec, Real.Angle.cos_coe, Real.Angle.sin_coe, Complex.cos_ofReal_re,
      Complex.sin_ofReal_re] <;>
    ring

/-- Composition of from-scratch rotations is composition of Mathlib rotations (`rot_add` ↔
    `Orientation.rotation_rotation`). -/
theorem toC_rot_rot (θ φ : ℝ) (v : G2) :
    toC (rot θ (rot φ v))
      = Complex.orientation.rotation (θ : Real.Angle)
          (Complex.orientation.rotation (φ : Real.Angle) (toC v)) := by
  rw [toC_rot, toC_rot]

/-- **The 2D rotor sandwich IS Mathlib's rotation:** `R v R̃` for `R = rotor θ`
    (`cos(θ/2) − sin(θ/2)·e₁₂`) and a vector `v`, read as a complex number, is
    `Complex.orientation.rotation θ` of `v` — the from-scratch rotor rotates by exactly the Mathlib
    angle `θ`. Via `sandwich_rotor` (`R v R̃ = rot θ v`) and `toC_rot`. -/
theorem rotor_sandwich_eq_rotation (θ : ℝ) {v : G2} (hv : G2.IsVector v) :
    toC (G2.mul (G2.mul (rotor θ) v) (G2.reverse (rotor θ)))
      = Complex.orientation.rotation (θ : Real.Angle) (toC v) := by
  rw [sandwich_rotor θ hv]
  exact toC_rot θ v

end GacalcProofs
