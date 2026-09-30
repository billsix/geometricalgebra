import GacalcProofs.G3

/-! # The cross product, the vector dual, and the scalar triple product (𝒢₃)

    Promotes three symbolic-unit-test identities to Lean theorems (see
    `tasks/lean-candidates-from-symbolic-tests.md`), all in 𝒢₃:

      * the **cross product** `a × b = (a ∧ b) I₃⁻¹` — the dual of the wedge (gacalc
        `vectorcalc.cross`): its coordinate formula, anticommutativity, and ⊥-ness
        (`tests/test_vectorcalc.py`);
      * the **dual of a vector** is the perpendicular bivector (`tests/test_multivector.py`);
      * the **scalar triple product = signed volume**: `a · (b × c)` equals the pseudoscalar
        (e₁₂₃) coefficient of `a ∧ b ∧ c`, the 3×3 determinant (`tests/test_vectorcalc.py`,
        `tests/test_measure.py`).

    Everything is a leaf coordinate identity: unfold the definitions and `ring`. In Lean `dot` is
    the scalar part `⟨A B⟩₀` (gacalc's `scalar_product`), which for two vectors is the Euclidean
    dot product. -/
namespace GacalcProofs.G3

/-- The **cross product** `a × b = (a ∧ b) I₃⁻¹` — the dual of the wedge (gacalc `vectorcalc.cross`).
    In 𝒢₃ the dual of the bivector `a ∧ b` is the vector normal to that plane. -/
noncomputable def cross (a b : G3) : G3 := dual (wedge a b)

/-- **The cross-product coordinate formula:**
    `a × b = (a₂b₃−a₃b₂, a₃b₁−a₁b₃, a₁b₂−a₂b₁)` (right-handed). -/
theorem cross_vec (a1 a2 a3 b1 b2 b3 : ℝ) :
    cross (vec a1 a2 a3) (vec b1 b2 b3)
      = vec (a2 * b3 - a3 * b2) (a3 * b1 - a1 * b3) (a1 * b2 - a2 * b1) := by
  simp only [cross, dual, I_inv, wedge, mul, vec]; ext <;> ring

/-- **The cross product is anticommutative:** `a × b = −(b × a)`. -/
theorem cross_anticomm_vec (a1 a2 a3 b1 b2 b3 : ℝ) :
    cross (vec a1 a2 a3) (vec b1 b2 b3) = neg (cross (vec b1 b2 b3) (vec a1 a2 a3)) := by
  simp only [cross, dual, I_inv, wedge, mul, neg, vec]; ext <;> ring

/-- **The cross product is perpendicular to its left factor:** `(a × b) · a = 0`. -/
theorem cross_perp_left (a1 a2 a3 b1 b2 b3 : ℝ) :
    dot (cross (vec a1 a2 a3) (vec b1 b2 b3)) (vec a1 a2 a3) = 0 := by
  simp only [dot, cross, dual, I_inv, wedge, mul, vec]; ring

/-- **The cross product is perpendicular to its right factor:** `(a × b) · b = 0`. -/
theorem cross_perp_right (a1 a2 a3 b1 b2 b3 : ℝ) :
    dot (cross (vec a1 a2 a3) (vec b1 b2 b3)) (vec b1 b2 b3) = 0 := by
  simp only [dot, cross, dual, I_inv, wedge, mul, vec]; ring

/-- **The dual of a 3D vector is a bivector — the perpendicular plane:**
    `(x, y, z)* = −z·e₁₂ + y·e₁₃ − x·e₂₃` (grade 2; its scalar, vector and pseudoscalar parts all
    vanish). This is the 3D companion of the 2D `G2.dual_vec` (which is the −90° turn). -/
theorem dual_vec (x y z : ℝ) :
    dual (vec x y z) = bivector (-z) y (-x) := by
  simp only [dual, I_inv, mul, vec, bivector, zero]; ext <;> ring

/-- The **signed volume** of three vectors = the pseudoscalar (e₁₂₃) coefficient of `a ∧ b ∧ c`
    (gacalc `measure.signed_volume`; the 3×3 determinant with rows `a`, `b`, `c`). -/
noncomputable def signedVolume (a b c : G3) : ℝ := (wedge (wedge a b) c).c123

/-- **The scalar triple product equals the signed volume:** `a · (b × c) = signedVolume a b c`.
    Both are the 3×3 determinant `det[a, b, c]` — the scalar-triple form via the cross product, the
    signed-volume form via the pseudoscalar part of the triple wedge. -/
theorem dot_cross_eq_signedVolume (a1 a2 a3 b1 b2 b3 c1 c2 c3 : ℝ) :
    dot (vec a1 a2 a3) (cross (vec b1 b2 b3) (vec c1 c2 c3))
      = signedVolume (vec a1 a2 a3) (vec b1 b2 b3) (vec c1 c2 c3) := by
  simp only [dot, cross, dual, I_inv, wedge, mul, signedVolume, vec]; ring

end GacalcProofs.G3
