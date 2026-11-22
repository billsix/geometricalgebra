import Mathlib

/-! # 𝒢₁ — the one-dimensional geometric algebra (the teaching twin of `G2`/`G3`)

    The smallest geometric algebra: basis {1, e₁}, Euclidean product e₁² = 1. Modelled for teaching
    (gacalc `src/gacalc/g1.py`): every construction of `G2.lean`/`G3.lean` has its degenerate 1D form
    here, and the three contrasts are the lesson —

      * the unit pseudoscalar is the vector `e₁` itself and `I² = +1` (not `−1` as in 𝒢₂/𝒢₃: the sign
        `(−1)^{r(r−1)/2}` is `+1` for `r = 1`);
      * the wedge of two vectors is **always zero** (any two 1D vectors are parallel), so the geometric
        product of vectors is pure scalar, `u*v = u·v`;
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

/-! ### Basis blades as elements, and the constants -/

def zero : G1 := { s := 0, c1 := 0 }
def one : G1 := { s := 1, c1 := 0 }

/-- The basis vector `e₁` — an element of the algebra, not a real. -/
def e_1 : G1 := { s := 0, c1 := 1 }

/-- A vector `x*e₁`. -/
def vec (x : ℝ) : G1 := { s := 0, c1 := x }

/-- The unit pseudoscalar of 𝒢₁ is the vector `e₁` itself. -/
def I : G1 := e_1

/-- `I⁻¹ = e₁` too, since `e₁² = 1`. -/
def I_inv : G1 := e_1

/-! ### Addition and the vector-space operations -/

noncomputable def add (a b : G1) : G1 := ⟨a.s + b.s, a.c1 + b.c1⟩

noncomputable def smul (r : ℝ) (a : G1) : G1 := ⟨r * a.s, r * a.c1⟩

/-- Componentwise subtraction. -/
noncomputable def sub (a b : G1) : G1 := ⟨a.s - b.s, a.c1 - b.c1⟩

/-- Componentwise negation. -/
noncomputable def neg (a : G1) : G1 := ⟨-a.s, -a.c1⟩

/-- Addition is **commutative**. -/
theorem add_comm (a b : G1) : add a b = add b a := by simp only [add]; ext <;> ring

/-- Addition is **associative**. -/
theorem add_assoc (a b c : G1) : add (add a b) c = add a (add b c) := by
  simp only [add]; ext <;> ring

/-- `zero` is a **right identity** for addition. -/
theorem add_zero (a : G1) : add a zero = a := by simp only [add, zero]; ext <;> ring

/-- `zero` is a **left identity** for addition. -/
theorem zero_add (a : G1) : add zero a = a := by simp only [add, zero]; ext <;> ring

/-- `neg a` is the **additive inverse**: `a + (−a) = 0`. -/
theorem add_neg_cancel (a : G1) : add a (neg a) = zero := by
  simp only [add, neg, zero]; ext <;> ring

/-! ### The geometric product and the wedge -/

/-- The Euclidean geometric product in 𝒢₁ (`e₁² = 1`), as emitted by `derive_lean_algebra.py 1`. -/
noncomputable def mul (a b : G1) : G1 := ⟨a.c1 * b.c1 + a.s * b.s, a.c1 * b.s + a.s * b.c1⟩

/-- The outer product in 𝒢₁ (grade 0 kept, as in gacalc): there is no grade 2, so vector∧vector is 0. -/
noncomputable def wedge (a b : G1) : G1 := ⟨a.s * b.s, a.c1 * b.s + a.s * b.c1⟩

/-- The reverse: grades 0 and 1 both have sign `+`, so it is the identity. -/
def reverse (a : G1) : G1 := ⟨a.s, a.c1⟩

/-! ### Magnitude (squared is the primitive) -/

noncomputable def normSq (a : G1) : ℝ := (mul a (reverse a)).s

noncomputable def magnitude (a : G1) : ℝ := Real.sqrt (normSq a)

/-! ### The scalar product (dot), the dual, and the inverse -/

/-- The dot (scalar part of the product), `normSq = ⟨a ã⟩`, and the magnitude — the same three
    definitions as in `G2`/`G3`. -/
noncomputable def dot (a b : G1) : ℝ := (mul a b).s

noncomputable def dual (a : G1) : G1 := mul a I_inv

noncomputable def inverse (a : G1) : G1 := smul (1 / normSq a) (reverse a)

/-! ### The multiplication table and the pseudoscalar sign (I² = +1) -/

theorem e_1_sq : mul e_1 e_1 = one := by simp only [mul, e_1, one]; ext <;> ring

/-- **`I² = +1` in 𝒢₁** — the contrast with `G2.I_sq`/`G3.I_sq` (`−1`): `(−1)^{r(r−1)/2} = +1` for `r = 1`. -/
theorem I_sq : mul I I = one := e_1_sq
theorem I_sq_eq_sign : (mul I I).s = (-1 : ℝ) ^ (1 * (1 - 1) / 2) := by
  simp only [mul, I, e_1]; norm_num
theorem I_mul_I_inv : mul I I_inv = one := e_1_sq
theorem reverse_reverse (a : G1) : reverse (reverse a) = a := by ext <;> rfl

/-! ### Commutativity and the algebra laws -/

/-- **𝒢₁ is commutative** (it is ℝ ⊕ ℝe₁ with `e₁² = 1`; no anticommuting pair exists). -/
theorem mul_comm (a b : G1) : mul a b = mul b a := by simp only [mul]; ext <;> ring

theorem mul_assoc (a b c : G1) : mul (mul a b) c = mul a (mul b c) := by simp only [mul]; ext <;> ring

theorem one_mul (a : G1) : mul one a = a := by simp only [mul, one]; ext <;> ring

theorem mul_add (a b c : G1) : mul a (add b c) = add (mul a b) (mul a c) := by
  simp only [mul, add]; ext <;> ring

/-- The product **distributes over addition on the right**. -/
theorem add_mul (a b c : G1) : mul (add a b) c = add (mul a c) (mul b c) := by
  simp only [mul, add]; ext <;> ring

/-- `one` is a **right identity**. -/
theorem mul_one (a : G1) : mul a one = a := by simp only [mul, one]; ext <;> ring

/-- `zero` **annihilates** from the left: `0 * a = 0`. -/
theorem zero_mul (a : G1) : mul zero a = zero := by simp only [mul, zero]; ext <;> ring

/-- A scalar pulls out of the **left** factor. -/
theorem smul_mul (k : ℝ) (a b : G1) : mul (smul k a) b = smul k (mul a b) := by
  simp only [mul, smul]; ext <;> ring

/-- A scalar pulls out of the **right** factor. -/
theorem mul_smul (k : ℝ) (a b : G1) : mul a (smul k b) = smul k (mul a b) := by
  simp only [mul, smul]; ext <;> ring

/-- Scalar multiples compose: `k • (m • a) = (k·m) • a`. -/
theorem smul_smul (k m : ℝ) (a : G1) : smul k (smul m a) = smul (k * m) a := by
  simp only [smul]; ext <;> ring

/-- `1 • a = a`. -/
theorem one_smul (a : G1) : smul 1 a = a := by simp only [smul]; ext <;> ring

/-! ### Grade-1 predicate -/

/-- `a` is a vector (grade 1): its scalar part vanishes. -/
def IsVector (a : G1) : Prop := a.s = 0

/-- A vector is `x e₁`: `a = vec a.c1`. -/
theorem eq_vec_of_isVector {a : G1} (ha : IsVector a) : a = vec a.c1 := by
  ext
  · exact ha
  · rfl

/-! ### Vectors: products, wedge, dot, magnitude, dual, and the vector inverse -/

/-- **The product of two vectors is a pure scalar**, `(x e₁)(y e₁) = xy` — there is no wedge part, so
    the product is the dot product times `1`. -/
theorem vec_mul {a b : G1} (ha : IsVector a) (hb : IsVector b) :
    mul a b = smul (dot a b) one := by
  unfold IsVector at ha hb
  simp only [mul, smul, dot, one, ha, hb]; ext <;> ring

/-- **Any two 1D vectors are parallel:** their wedge is zero. -/
theorem wedge_vec {a b : G1} (ha : IsVector a) (hb : IsVector b) : wedge a b = zero := by
  unfold IsVector at ha hb
  simp only [wedge, zero, ha, hb]; ext <;> ring

/-- The dot product of two vectors is the product of their coordinates, `(x e₁)·(y e₁) = x y`. -/
theorem dot_vec (x y : ℝ) : dot (vec x) (vec y) = x * y := by simp only [dot, mul, vec]; ring

/-- The fundamental identity `u v = u·v + u∧v`, degenerate: the wedge term is `0`. -/
theorem vec_mul_eq_dot_add_wedge {a b : G1} (ha : IsVector a) (hb : IsVector b) :
    mul a b = add (smul (dot a b) one) (wedge a b) := by
  rw [wedge_vec ha hb, vec_mul ha hb]
  simp only [add, smul, zero, one]; ext <;> ring

/-- `|x|²` of the vector `x e₁` is `x²`. -/
theorem normSq_vec (x : ℝ) : normSq (vec x) = x ^ 2 := by simp only [normSq, mul, reverse, vec]; ring

/-- `|x e₁| = |x|`. -/
theorem magnitude_vec (x : ℝ) : magnitude (vec x) = |x| := by
  rw [magnitude, normSq_vec, Real.sqrt_sq_eq_abs]

/-- The dual of a vector is a scalar (grade `1 ↦ 0`): `(x e₁) I⁻¹ = x`. -/
theorem dual_vec {a : G1} (ha : IsVector a) : dual a = smul a.c1 one := by
  unfold IsVector at ha
  simp only [dual, mul, I_inv, e_1, smul, one, ha]; ext <;> ring

/-- A nonzero vector times its inverse is `1`. -/
theorem mul_vec_inverse_self {a : G1} (ha : IsVector a) (han : normSq a ≠ 0) :
    mul a (inverse a) = one := by
  unfold IsVector at ha
  have hn : normSq a = a.c1 ^ 2 := by simp only [normSq, mul, reverse, ha]; ring
  rw [hn] at han
  have hc : a.c1 ≠ 0 := fun h => han (by rw [h]; ring)
  simp only [inverse, hn, mul, smul, reverse, one, ha]
  ext
  · field_simp [hc]
    ring
  · ring

end G1
end GacalcProofs
