import Mathlib

/-! # 𝒢₁ — the one-dimensional geometric algebra (the teaching twin of `G2`/`G3`)

    The smallest geometric algebra: basis {1, e₁}, Euclidean product e₁² = 1. Modelled for teaching
    (gacalc `src/gacalc/g1.py`): every construction of `G2.lean`/`G3.lean` has its degenerate 1D form
    here, and the three contrasts are the lesson —

      * the unit pseudoscalar is the vector `e₁` itself and `I² = +1` (not `−1` as in 𝒢₂/𝒢₃: the sign
        `(−1)^{r(r−1)/2}` is `+1` for `r = 1`);
      * the wedge of two vectors is **always zero** (any two 1D vectors are parallel), so the geometric
        product of vectors is pure scalar, `u v = u·v`;
      * the algebra is **commutative** (𝒢₁ ≅ ℝ ⊕ ℝe₁; `mul_comm`), and the reverse is the identity.

    Same representation as the higher algebras: coefficients as fields, basis blades as elements
    (`one`, `e_1 : G1`). The product and wedge were transcribed from gacalc's `Gn` oracle
    (`tools/derive_lean_algebra.py 1`). -/
namespace GacalcProofs

/-- An element of 𝒢₁ by its two real coefficients on {1, e₁}. -/
@[ext]
structure G1 where
  s : ℝ   -- coefficient of the scalar unit 1 (grade 0)
  c1 : ℝ  -- coefficient of the basis vector e₁ (grade 1)

namespace G1

/-- The Euclidean geometric product in 𝒢₁ (`e₁² = 1`), as emitted by `derive_lean_algebra.py 1`. -/
noncomputable def mul (a b : G1) : G1 := ⟨a.c1 * b.c1 + a.s * b.s, a.c1 * b.s + a.s * b.c1⟩

/-- The outer product in 𝒢₁ (grade 0 kept, as in gacalc): there is no grade 2, so vector∧vector is 0. -/
noncomputable def wedge (a b : G1) : G1 := ⟨a.s * b.s, a.c1 * b.s + a.s * b.c1⟩

noncomputable def add (a b : G1) : G1 := ⟨a.s + b.s, a.c1 + b.c1⟩
noncomputable def smul (r : ℝ) (a : G1) : G1 := ⟨r * a.s, r * a.c1⟩

/-- The reverse: grades 0 and 1 both have sign `+`, so it is the identity. -/
def reverse (a : G1) : G1 := ⟨a.s, a.c1⟩

def zero : G1 := ⟨0, 0⟩
def one : G1 := ⟨1, 0⟩
/-- The basis vector `e₁` — an element of the algebra, not a real. -/
def e_1 : G1 := ⟨0, 1⟩
/-- A vector `x·e₁`. -/
def vec (x : ℝ) : G1 := ⟨0, x⟩
/-- The unit pseudoscalar of 𝒢₁ is the vector `e₁` itself. -/
def I : G1 := e_1
/-- `I⁻¹ = e₁` too, since `e₁² = 1`. -/
def I_inv : G1 := e_1

/-- `a` is a vector (grade 1): its scalar part vanishes. -/
def IsVector (a : G1) : Prop := a.s = 0

/-- The dot (scalar part of the product), `normSq = ⟨a ã⟩`, and the magnitude — the same three
    definitions as in `G2`/`G3`. -/
noncomputable def dot (a b : G1) : ℝ := (mul a b).s
noncomputable def normSq (a : G1) : ℝ := (mul a (reverse a)).s
noncomputable def magnitude (a : G1) : ℝ := Real.sqrt (normSq a)
noncomputable def dual (a : G1) : G1 := mul a I_inv
noncomputable def inverse (a : G1) : G1 := smul (1 / normSq a) (reverse a)

theorem reverse_reverse (a : G1) : reverse (reverse a) = a := by ext <;> rfl
theorem e_1_sq : mul e_1 e_1 = one := by simp only [mul, e_1, one]; ext <;> ring

/-- **`I² = +1` in 𝒢₁** — the contrast with `G2.I_sq`/`G3.I_sq` (`−1`): `(−1)^{r(r−1)/2} = +1` for `r = 1`. -/
theorem I_sq : mul I I = one := e_1_sq
theorem I_sq_eq_sign : (mul I I).s = (-1 : ℝ) ^ (1 * (1 - 1) / 2) := by
  simp only [mul, I, e_1]; norm_num
theorem I_mul_I_inv : mul I I_inv = one := e_1_sq

/-- **𝒢₁ is commutative** (it is ℝ ⊕ ℝe₁ with `e₁² = 1`; no anticommuting pair exists). -/
theorem mul_comm (a b : G1) : mul a b = mul b a := by simp only [mul]; ext <;> ring
theorem mul_assoc (a b c : G1) : mul (mul a b) c = mul a (mul b c) := by simp only [mul]; ext <;> ring
theorem one_mul (a : G1) : mul one a = a := by simp only [mul, one]; ext <;> ring
theorem mul_add (a b c : G1) : mul a (add b c) = add (mul a b) (mul a c) := by
  simp only [mul, add]; ext <;> ring

/-- **The product of two vectors is a pure scalar**, `(x e₁)(y e₁) = xy` — there is no wedge part. -/
theorem vec_mul (x y : ℝ) : mul (vec x) (vec y) = smul (x * y) one := by
  simp only [mul, vec, smul, one]; ext <;> ring
/-- **Any two 1D vectors are parallel:** their wedge is zero. -/
theorem wedge_vec (x y : ℝ) : wedge (vec x) (vec y) = zero := by
  simp only [wedge, vec, zero]; ext <;> ring
theorem dot_vec (x y : ℝ) : dot (vec x) (vec y) = x * y := by simp only [dot, mul, vec]; ring
/-- The fundamental identity `u v = u·v + u∧v`, degenerate: the wedge term is `0`. -/
theorem vec_mul_eq_dot_add_wedge (x y : ℝ) :
    mul (vec x) (vec y) = add (smul (dot (vec x) (vec y)) one) (wedge (vec x) (vec y)) := by
  simp only [mul, vec, add, smul, dot, one, wedge]; ext <;> ring
theorem normSq_vec (x : ℝ) : normSq (vec x) = x ^ 2 := by simp only [normSq, mul, reverse, vec]; ring
/-- `|x e₁| = |x|`. -/
theorem magnitude_vec (x : ℝ) : magnitude (vec x) = |x| := by
  rw [magnitude, normSq_vec, Real.sqrt_sq_eq_abs]
/-- The dual of a vector is a scalar (grade `1 ↦ 0`): `(x e₁) I⁻¹ = x`. -/
theorem dual_vec (x : ℝ) : dual (vec x) = smul x one := by
  simp only [dual, mul, vec, I_inv, e_1, smul, one]; ext <;> ring
/-- A nonzero vector times its inverse is `1`. -/
theorem mul_vec_inverse_self (x : ℝ) (hx : x ≠ 0) : mul (vec x) (inverse (vec x)) = one := by
  rw [inverse, normSq_vec]
  simp only [mul, smul, reverse, vec, one]
  ext
  · field_simp; ring
  · ring

end G1
end GacalcProofs
