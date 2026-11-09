import GacalcProofs.G2
import GacalcProofs.Versor2D
import GacalcProofs.Sandwich

/-! # Projection / rejection in 𝒢₂ — the 2D warm-up

    The 2D counterpart of `Projection3D.lean`: vector-onto-vector projection with the rejection ⊥ the
    vector, and the onto-the-pseudoscalar-plane case — where a 2D vector has **no** perpendicular
    component (the plane is the whole space), so its rejection from `I₂` is `0` and projecting it onto
    `I₂` recovers the vector. Uses the same Hestenes forms as 3D (`proj` = `(A·B)B⁻¹` for a vector `B`,
    `reject` = `(A∧B)B⁻¹`). -/
namespace GacalcProofs.G2

/-- Vector projection of `b` onto the vector `a`: `proj_a b = (b·a / a·a)·a` (Hestenes `(A·B)B⁻¹`
    for a vector `B`).

    The denominator is the self-inner-product `a·a` (Hestenes `dot`), **not** `normSq a`. They agree
    for a vector (`a·a = |a|²`), but this def is general in `a : G2`, where `a·a ≠ normSq a` on grade ≥ 2
    (`normSq` uses the reverse). Do NOT tighten the denominator to `normSq a`. (Same call as 3D `proj`.) -/
noncomputable def proj (a b : G2) : G2 := smul (dot b a / dot a a) a

/-- Hestenes rejection `reject_B A = (A ∧ B) B⁻¹`. -/
noncomputable def reject (awayFrom a : G2) : G2 := mul (wedge a awayFrom) (inverse awayFrom)

/-- **The rejection is ⊥ the vector** (2D): `(b − proj_a b) · a = 0` for `a·a ≠ 0`. Structural, via the
    `dot` bilinearity lemmas — the exact shape of the 3D `reject_perp_dot`, and general in `a, b`.

    The hypothesis is the **general** `dot a a ≠ 0`, deliberately not `normSq a ≠ 0`: it holds for any
    `a : G2`, and for a non-vector `a` the two differ (see `proj`). Do NOT tighten it to `normSq`. -/
theorem reject_perp_dot (a b : G2) (ha : dot a a ≠ 0) :
    dot (sub b (proj a b)) a = 0 := by
  rw [dot_sub_left, proj, dot_smul_left]
  field_simp
  ring

/-- **A 2D vector wedged with the pseudoscalar is zero**: `v ∧ I₂ = 0` (grade 1 + 2 = 3 exceeds the
    dimension). So a vector has no part outside the plane. A corollary of the object-form
    `wedge_isVector_isBivector_eq_zero`, with `isBivector_I` discharging the bivector side. -/
theorem wedge_I_eq_zero {a : G2} (ha : IsVector a) : wedge a I = (⟨0, 0, 0, 0⟩ : G2) :=
  wedge_isVector_isBivector_eq_zero ha isBivector_I

/-- **The rejection of a vector from the pseudoscalar plane is zero** — a 2D vector lies entirely in
    the plane, so nothing is rejected. `reject I₂ v = (v ∧ I₂) I₂⁻¹ = 0`. -/
theorem reject_from_I_eq_zero {a : G2} (ha : IsVector a) : reject I a = (⟨0, 0, 0, 0⟩ : G2) := by
  rw [reject, wedge_I_eq_zero ha]
  ext <;> simp only [mul, inverse, smul, reverse, normSq, I, e_12] <;> ring

end GacalcProofs.G2
