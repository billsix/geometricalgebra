import GacalcProofs.G2
import GacalcProofs.G3

/-! # The algebra laws of 𝒢₂ and 𝒢₃

    Both `G2` and `G3` are **associative, unital ℝ-algebras**: the geometric product is associative
    and distributes over addition (both sides), `one` is a two-sided identity, and scalars pull
    through the product. Each is a polynomial identity in the coordinate fields, so the proof is
    `ext <;> ring` (a large but automatic expansion for `G3`'s eight fields). Plus the GA-specific
    fact that **orthogonal vectors anticommute** (`u·v = 0 ⟹ u v = −(v u)`).

    These are the axioms everything built on the product (the sandwich, projection, the rotation
    proofs) rests on. See `tasks/lean-proof-algebra-laws-g2-g3.md`. -/
namespace GacalcProofs

namespace G2

/-- The geometric product is **associative**. -/
theorem mul_assoc (a b c : G2) : mul (mul a b) c = mul a (mul b c) := by
  simp only [mul]; ext <;> ring

/-- The product **distributes over addition on the left**. -/
theorem mul_add (a b c : G2) : mul a (add b c) = add (mul a b) (mul a c) := by
  simp only [mul, add]; ext <;> ring

/-- The product **distributes over addition on the right**. -/
theorem add_mul (a b c : G2) : mul (add a b) c = add (mul a c) (mul b c) := by
  simp only [mul, add]; ext <;> ring

/-- `one` is a **left identity**. -/
theorem one_mul (a : G2) : mul one a = a := by simp only [mul, one]; ext <;> ring

/-- `one` is a **right identity**. -/
theorem mul_one (a : G2) : mul a one = a := by simp only [mul, one]; ext <;> ring

/-- A scalar pulls out of the **left** factor. -/
theorem smul_mul (k : ℝ) (a b : G2) : mul (smul k a) b = smul k (mul a b) := by
  simp only [mul, smul]; ext <;> ring

/-- A scalar pulls out of the **right** factor. -/
theorem mul_smul (k : ℝ) (a b : G2) : mul a (smul k b) = smul k (mul a b) := by
  simp only [mul, smul]; ext <;> ring

/-- Scalar multiples compose: `k • (m • a) = (k·m) • a`. -/
theorem smul_smul (k m : ℝ) (a : G2) : smul k (smul m a) = smul (k * m) a := by
  simp only [smul]; ext <;> ring

/-- `1 • a = a`. -/
theorem one_smul (a : G2) : smul 1 a = a := by simp only [smul]; ext <;> ring

/-- **Orthogonal vectors anticommute:** if `u·v = 0` (here `u₁*v₁ + u₂*v₂ = 0`) then `u v = −(v u)`.
    The scalar (inner) parts cancel by orthogonality; the bivector parts are already antisymmetric. -/
theorem vec_anticomm_perp (u1 u2 v1 v2 : ℝ) (h : u1 * v1 + u2 * v2 = 0) :
    mul (vec u1 u2) (vec v1 v2) = neg (mul (vec v1 v2) (vec u1 u2)) := by
  simp only [mul, neg, vec]
  ext
  · linear_combination 2 * h
  · ring
  · ring
  · ring

end G2

namespace G3

/-- The geometric product is **associative**. -/
theorem mul_assoc (a b c : G3) : mul (mul a b) c = mul a (mul b c) := by
  simp only [mul]; ext <;> ring

/-- The product **distributes over addition on the left**. -/
theorem mul_add (a b c : G3) : mul a (add b c) = add (mul a b) (mul a c) := by
  simp only [mul, add]; ext <;> ring

/-- The product **distributes over addition on the right**. -/
theorem add_mul (a b c : G3) : mul (add a b) c = add (mul a c) (mul b c) := by
  simp only [mul, add]; ext <;> ring

/-- The product **distributes over subtraction on the right**. -/
theorem sub_mul (a b c : G3) : mul (sub a b) c = sub (mul a c) (mul b c) := by
  simp only [mul, sub]; ext <;> ring

/-- Left distributivity over subtraction (the `mul_sub` twin of `sub_mul`). -/
theorem mul_sub (a b c : G3) : mul a (sub b c) = sub (mul a b) (mul a c) := by
  simp only [mul, sub]; ext <;> ring

/-- `one` is a **left identity**. -/
theorem one_mul (a : G3) : mul one a = a := by simp only [mul, one]; ext <;> ring

/-- `one` is a **right identity**. -/
theorem mul_one (a : G3) : mul a one = a := by simp only [mul, one]; ext <;> ring

/-- A scalar pulls out of the **left** factor. -/
theorem smul_mul (k : ℝ) (a b : G3) : mul (smul k a) b = smul k (mul a b) := by
  simp only [mul, smul]; ext <;> ring

/-- A scalar pulls out of the **right** factor. -/
theorem mul_smul (k : ℝ) (a b : G3) : mul a (smul k b) = smul k (mul a b) := by
  simp only [mul, smul]; ext <;> ring

/-- Scalar multiples compose: `k • (m • a) = (k·m) • a`. -/
theorem smul_smul (k m : ℝ) (a : G3) : smul k (smul m a) = smul (k * m) a := by
  simp only [smul]; ext <;> ring

/-- `1 • a = a`. -/
theorem one_smul (a : G3) : smul 1 a = a := by simp only [smul]; ext <;> ring

/-- **Orthogonal vectors anticommute:** if `a·b = 0` then `a b = −(b a)`. A corollary of
    `vec_mul_perp` (`a b = a∧b`) plus the antisymmetry of the wedge. -/
theorem vec_anticomm_perp {a b : G3} (ha : IsVector a) (hb : IsVector b) (h : dot a b = 0) :
    mul a b = neg (mul b a) := by
  have hba : dot b a = 0 := by rw [dot_comm b a]; exact h
  rw [mul_eq_wedge_of_perp ha hb h, mul_eq_wedge_of_perp hb ha hba, wedge_antisymm ha hb]

end G3

end GacalcProofs
