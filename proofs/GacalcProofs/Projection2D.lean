import GacalcProofs.G2
import GacalcProofs.Versor2D
import GacalcProofs.Sandwich

/-! # Projection / rejection in 𝒢₂ — the 2D warm-up

    The 2D counterpart of `Projection.lean`: vector-onto-vector projection with the rejection ⊥ the
    vector, and the onto-the-pseudoscalar-plane case — where a 2D vector has **no** perpendicular
    component (the plane is the whole space), so its rejection from `I₂` is `0` and projecting it onto
    `I₂` recovers the vector. Uses the same Hestenes forms as 3D (`proj` = `(A·B)B⁻¹` for a vector `B`,
    `reject` = `(A∧B)B⁻¹`). -/
namespace GacalcProofs.G2

/-- The outer (wedge) product in 𝒢₂. -/
noncomputable def wedge (a b : G2) : G2 where
  s := a.s * b.s
  c1 := a.c1 * b.s + a.s * b.c1
  c2 := a.c2 * b.s + a.s * b.c2
  c12 := a.c1 * b.c2 - a.c2 * b.c1 + a.c12 * b.s + a.s * b.c12

/-- Vector projection of `b` onto the vector `a`: `proj_a b = (b·a / a·a)·a` (Hestenes `(A·B)B⁻¹`
    for a vector `B`). -/
noncomputable def proj (a b : G2) : G2 := smul (dot b a / dot a a) a

/-- Hestenes rejection `reject_B A = (A ∧ B) B⁻¹`. -/
noncomputable def reject (awayFrom a : G2) : G2 := mul (wedge a awayFrom) (inverse awayFrom)

/-- **The rejection is ⊥ the vector** (2D): `(b − proj_a b) · a = 0` for `a·a ≠ 0`. Structural, via the
    `dot` bilinearity lemmas — the exact shape of the 3D `reject_perp`, and general in `a, b`. -/
theorem reject_perp (a b : G2) (ha : dot a a ≠ 0) :
    dot (sub b (proj a b)) a = 0 := by
  rw [dot_sub_left, proj, dot_smul_left]
  field_simp
  ring

/-- **A 2D vector wedged with the pseudoscalar is zero**: `v ∧ I₂ = 0` (grade 1 + 2 = 3 exceeds the
    dimension). So a vector has no part outside the plane. -/
theorem vec_wedge_I_eq_zero (x y : ℝ) : wedge (vec x y) I = (⟨0, 0, 0, 0⟩ : G2) := by
  simp only [wedge, vec, I, e_12]; ext <;> ring

/-- **The rejection of a vector from the pseudoscalar plane is zero** — a 2D vector lies entirely in
    the plane, so nothing is rejected. `reject I₂ v = (v ∧ I₂) I₂⁻¹ = 0`. -/
theorem reject_from_I_eq_zero (x y : ℝ) : reject I (vec x y) = (⟨0, 0, 0, 0⟩ : G2) := by
  rw [reject, vec_wedge_I_eq_zero]
  ext <;> simp only [mul, inverse, smul, reverse, normSq, I, e_12] <;> ring

end GacalcProofs.G2
