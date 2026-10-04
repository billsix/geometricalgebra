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
    for a vector `B`).

    The denominator is the self-inner-product `a·a` (Hestenes `dot`), **not** `normSq a`. They agree
    for a vector (`a·a = |a|²`), but this def is general in `a : G2`, where `a·a ≠ normSq a` on grade ≥ 2
    (`normSq` uses the reverse). Do NOT tighten the denominator to `normSq a`. (Same call as 3D `proj`.) -/
noncomputable def proj (a b : G2) : G2 := smul (dot b a / dot a a) a

/-- The wedge distributes over subtraction on the right (2D). -/
theorem wedge_sub_right (a u w : G2) : wedge a (sub u w) = sub (wedge a u) (wedge a w) := by
  simp only [wedge, sub]; ext <;> ring

/-- The wedge distributes over addition on the right (2D). -/
theorem wedge_add_right (a u w : G2) : wedge a (add u w) = add (wedge a u) (wedge a w) := by
  simp only [wedge, add]; ext <;> ring

/-- The wedge pulls out a scalar on the right (2D). -/
theorem wedge_smul_right (k : ℝ) (a u : G2) : wedge a (smul k u) = smul k (wedge a u) := by
  simp only [wedge, smul]; ext <;> ring

/-- The wedge distributes over subtraction on the left (2D). -/
theorem wedge_sub_left (u w a : G2) : wedge (sub u w) a = sub (wedge u a) (wedge w a) := by
  simp only [wedge, sub]; ext <;> ring

/-- The wedge distributes over addition on the left (2D). -/
theorem wedge_add_left (u w a : G2) : wedge (add u w) a = add (wedge u a) (wedge w a) := by
  simp only [wedge, add]; ext <;> ring

/-- The wedge pulls out a scalar on the left (2D). -/
theorem wedge_smul_left (k : ℝ) (u a : G2) : wedge (smul k u) a = smul k (wedge u a) := by
  simp only [wedge, smul]; ext <;> ring

/-- `a ∧ a = 0` for a vector `a` (2D). -/
theorem wedge_self_vec {a : G2} (ha : IsVector a) : wedge a a = (⟨0, 0, 0, 0⟩ : G2) := by
  obtain ⟨has, _⟩ := ha
  simp only [wedge, has]; ext <;> ring

/-- **The wedge of vectors is antisymmetric:** `a∧b = −(b∧a)` (2D), for vectors `a`, `b`. -/
theorem wedge_antisymm {a b : G2} (ha : IsVector a) (hb : IsVector b) :
    wedge a b = neg (wedge b a) := by
  rw [eq_vec_of_isVector ha, eq_vec_of_isVector hb]
  simp only [wedge, vec, neg]; ext <;> ring

/-- **The fundamental identity `a b = a·b + a∧b`, for arbitrary vectors** (2D): for grade-1 `a`, `b`,
    the geometric product splits into its scalar (inner) part `a·b` and its pseudoscalar (outer) part
    `a∧b`. The 2D twin of the 𝒢₃ `mul_eq_dot_add_wedge`. -/
theorem mul_eq_dot_add_wedge {a b : G2} (ha : IsVector a) (hb : IsVector b) :
    mul a b = add (smul (dot a b) one) (wedge a b) := by
  obtain ⟨_, ha12⟩ := ha
  obtain ⟨hbs, hb12⟩ := hb
  simp only [mul, wedge, smul, one, dot, add]
  ext <;> simp only [ha12, hbs, hb12] <;> ring

/-- **Orthogonal vectors' geometric product is their wedge** (2D, arbitrary vectors): `a·b = 0 ⟹ a b = a∧b`. -/
theorem mul_eq_wedge_of_perp {a b : G2} (ha : IsVector a) (hb : IsVector b) (h : dot a b = 0) :
    mul a b = wedge a b := by
  rw [mul_eq_dot_add_wedge ha hb, h]
  simp only [smul, one, add]; ext <;> ring

/-- **Leaf:** `|a∧b|² = (a₁b₂ − a₂b₁)²` — the squared magnitude of the plane bivector of two vectors (2D). -/
theorem normSq_wedge_vec (a1 a2 b1 b2 : ℝ) :
    normSq (wedge (vec a1 a2) (vec b1 b2)) = (a1 * b2 - a2 * b1) ^ 2 := by
  simp only [normSq, wedge, mul, reverse, vec]; ring

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
    dimension). So a vector has no part outside the plane. -/
theorem vec_wedge_I_eq_zero (x y : ℝ) : wedge (vec x y) I = (⟨0, 0, 0, 0⟩ : G2) := by
  simp only [wedge, vec, I, e_12]; ext <;> ring

/-- **The rejection of a vector from the pseudoscalar plane is zero** — a 2D vector lies entirely in
    the plane, so nothing is rejected. `reject I₂ v = (v ∧ I₂) I₂⁻¹ = 0`. -/
theorem reject_from_I_eq_zero (x y : ℝ) : reject I (vec x y) = (⟨0, 0, 0, 0⟩ : G2) := by
  rw [reject, vec_wedge_I_eq_zero]
  ext <;> simp only [mul, inverse, smul, reverse, normSq, I, e_12] <;> ring

/-- **The reverse-sandwich is an outermorphism up to `|R|²`** (2D): `(R u R̃) ∧ (R v R̃) = |R|²·R (u∧v) R̃`.
    A pure polynomial identity (atomic `normSq R`) — the unnormalized core of the 2D
    `sandwich_preserves_wedge`. -/
theorem wedge_reverse_sandwich {R : G2} (hR : IsEvenVersor R) {u v : G2} :
    wedge (mul (mul R u) (reverse R)) (mul (mul R v) (reverse R))
      = smul (normSq R) (mul (mul R (wedge u v)) (reverse R)) := by
  obtain ⟨hR1, hR2⟩ := hR
  simp only [normSq, wedge, mul, reverse, smul, hR1, hR2]
  ext <;> ring

/-- **The sandwich preserves the outer product** (object form, 2D outermorphism):
    `(R u R⁻¹) ∧ (R v R⁻¹) = R (u∧v) R⁻¹` for an even versor `R` with `|R|² ≠ 0` and vectors `u`, `v`.
    In 𝒢₂ the wedge is the pseudoscalar (signed area), so this is "a rotation preserves signed area." -/
theorem sandwich_preserves_wedge {R : G2} (hR : IsEvenVersor R) (hr : normSq R ≠ 0)
    {u v : G2} (hu : IsVector u) (hv : IsVector v) :
    wedge (sandwich R u) (sandwich R v) = sandwich R (wedge u v) := by
  simp only [sandwich, inverse, GacalcProofs.G2.mul_smul, GacalcProofs.G2.wedge_smul_left,
             GacalcProofs.G2.wedge_smul_right, GacalcProofs.G2.smul_smul]
  rw [wedge_reverse_sandwich hR, GacalcProofs.G2.smul_smul]
  congr 1
  field_simp

/-- **The reverse sandwich scales the wedge's norm by `|R|²`** (2D): `|R (u∧v) R̃|² = |R|⁴ |u∧v|²`,
    stated on the pseudoscalar `u∧v` itself (atomic `normSq R`). Pure polynomial. -/
theorem normSq_reverse_sandwich_wedge {R : G2} (hR : IsEvenVersor R) {u v : G2} :
    normSq (mul (mul R (wedge u v)) (reverse R)) = normSq R ^ 2 * normSq (wedge u v) := by
  obtain ⟨hR1, hR2⟩ := hR
  simp only [normSq, wedge, mul, reverse, hR1, hR2]
  ring

/-- **The sandwich preserves the wedge's squared magnitude** (object form, 2D): `|R (u∧v) R⁻¹|² = |u∧v|²`
    for an even versor `R` with `|R|² ≠ 0` and vectors `u`, `v` — a rotation preserves signed area. -/
theorem sandwich_preserves_normSq_of_wedge {R : G2} (hR : IsEvenVersor R) (hr : normSq R ≠ 0)
    {u v : G2} (hu : IsVector u) (hv : IsVector v) :
    normSq (sandwich R (wedge u v)) = normSq (wedge u v) := by
  rw [sandwich, inverse, GacalcProofs.G2.mul_smul, normSq_smul, normSq_reverse_sandwich_wedge hR]
  field_simp [hr]

end GacalcProofs.G2
