import Mathlib

/-! # 𝒢₂ from scratch: dot and wedge as the parts of the geometric product

    A self-contained construction of the 2D geometric algebra over ℝ in the basis
    {1, e₁, e₂, e₁ * e₂}, with the Euclidean geometric product (e₁²=e₂²=1,
    e₁ * e₂=−e₂ * e₁). It proves the facts the book derives from rotation:

      * for vectors u, v:  u v = (u·v) + (u∧v) * e₁ * e₂,
      * the **dot product** is the symmetric part  ½(uv + vu)  (its scalar part), and
      * the **wedge product** is the antisymmetric part  ½(uv − vu)  (its e₁ * e₂ part),
      * the unit pseudoscalar squares to −1:  I² = −1 = (−1)^(r(r−1)/2) with r = 2.

    ## Representation: coordinates as fields, basis blades as *elements*

    A multivector is a real linear combination of the four basis blades
    `1`, `e₁`, `e₂`, `e₁ * e₂`. We store it concretely by its four real **coefficients**
    (`s`, `c1`, `c2`, `c12`) — a field is a coefficient, so it is an `ℝ`. But the
    basis blades themselves are NOT reals: `e₁`, `e₂` are *vectors* and `e₁ * e₂` a
    *bivector* — elements of the algebra. So they are defined below as genuine values
    `one`, `e_1`, `e_2`, `e_12` of type `G2` (e.g. `e_1 : G2`, not `ℝ`), and the GA
    multiplication table (`e_1_sq`, `e_1_mul_e_2`, `e_2_mul_e_1`, `e_12_sq`) is proved
    from the product. `eq_smul_basis` shows every `g : G2` is `s * 1 + c1 * e₁ + c2 * e₂ +
    c12 * e₁ * e₂`, tying the coefficient fields back to the basis elements.

    This mirrors the standard GA-in-Lean formalizations — Mathlib's `CliffordAlgebra`
    and pygae/lean-ga (Wieser & Song, *Formalizing Geometric Algebra in Lean*, 2021,
    arXiv:2110.03551) — where a basis vector `eᵢ` maps into the algebra via the linear
    map `ι Q : M →ₗ[R] CliffordAlgebra Q`, so `ι Q eᵢ : CliffordAlgebra Q` is an
    *element of the algebra* and the scalars enter via `algebraMap R _`. Those use a
    basis-free tensor-algebra quotient; gacalc's Lean policy is standalone/from-scratch
    (see `tasks/reference/lean-for-gacalc.md`), so we use the concrete coordinate model
    here and reserve the abstract `CliffordAlgebra` for the *equivalence* direction.

    "Special case + equivalence to the general case": the dot here equals the
    coordinate sum u₁ * v₁ + u₂ * v₂ (`dot_eq_coord_sum`), i.e. the general Euclidean dot
    product / Mathlib's `@inner ℝ (EuclideanSpace ℝ (Fin 2))`. (The book's full
    sin/cos → rotation → geometric-product derivation is in `Rotation2D.lean`; this
    module establishes the dot/wedge-as-parts step it culminates in.) -/
namespace GacalcProofs

/-- An element of 𝒢₂, stored by its four real **coefficients** on the basis blades
    {1, e₁, e₂, e₁ * e₂}. The fields are coefficients, hence reals; the basis blades
    themselves are the elements `one`/`e_1`/`e_2`/`e_12 : G2` defined below.

    (No `deriving Repr/DecidableEq`: `ℝ` is noncomputable, so those instances don't
    compile — and proofs don't need them. `@[ext]` gives the `ext` tactic a
    componentwise extensionality lemma.) -/
@[ext]
structure G2 where
  s : ℝ    -- coefficient of the scalar unit 1     (grade 0)
  c1 : ℝ   -- coefficient of the basis vector e₁    (grade 1)
  c2 : ℝ   -- coefficient of the basis vector e₂    (grade 1)
  c12 : ℝ  -- coefficient of the unit bivector e₁ * e₂ (grade 2)

namespace G2

/-- The Euclidean geometric product in 𝒢₂ (from the table e₁²=e₂²=1, e₁ * e₂=−e₂ * e₁,
    (e₁ * e₂)²=−1). `noncomputable` because `ℝ`'s field ops are. -/
noncomputable def mul (a b : G2) : G2 where
  s   := a.s * b.s + a.c1 * b.c1 + a.c2 * b.c2 - a.c12 * b.c12
  c1  := a.s * b.c1 + a.c1 * b.s - a.c2 * b.c12 + a.c12 * b.c2
  c2  := a.s * b.c2 + a.c2 * b.s + a.c1 * b.c12 - a.c12 * b.c1
  c12 := a.s * b.c12 + a.c12 * b.s + a.c1 * b.c2 - a.c2 * b.c1

/-- Componentwise addition. -/
noncomputable def add (a b : G2) : G2 := ⟨a.s + b.s, a.c1 + b.c1, a.c2 + b.c2, a.c12 + b.c12⟩

/-- Componentwise subtraction. -/
noncomputable def sub (a b : G2) : G2 := ⟨a.s - b.s, a.c1 - b.c1, a.c2 - b.c2, a.c12 - b.c12⟩

/-- Componentwise negation. -/
noncomputable def neg (a : G2) : G2 := ⟨-a.s, -a.c1, -a.c2, -a.c12⟩

/-- Scalar multiple. -/
noncomputable def smul (r : ℝ) (a : G2) : G2 := ⟨r * a.s, r * a.c1, r * a.c2, r * a.c12⟩

/-- Reverse `R̃` — reverses the order of the vector factors in each blade. Per grade k the
    sign is (−1)^(k(k−1)/2): k=0,1 → +, k=2 → −, so in 𝒢₂ it negates the grade-2 (e₁ * e₂)
    coefficient and fixes grades 0 and 1. (Used by the versor/rotor sandwich.) -/
noncomputable def reverse (a : G2) : G2 := ⟨a.s, a.c1, a.c2, -a.c12⟩

/-- Reverse is an involution: `R̃̃ = R`. -/
theorem reverse_reverse (a : G2) : reverse (reverse a) = a := by
  simp only [reverse]; ext <;> ring

/-- The scalar unit `1` (grade 0) — an element of 𝒢₂. -/
def one : G2 := ⟨1, 0, 0, 0⟩

/-- The basis vector e₁ (grade 1) — an element of 𝒢₂, NOT a real. -/
def e_1 : G2 := ⟨0, 1, 0, 0⟩

/-- The basis vector e₂ (grade 1) — an element of 𝒢₂. -/
def e_2 : G2 := ⟨0, 0, 1, 0⟩

/-- The unit bivector e₁ * e₂ (grade 2) — an element of 𝒢₂. Equals `mul e_1 * e_2`
    (`e_1_mul_e_2`); it is the unit pseudoscalar `I` in 2D. -/
def e_12 : G2 := ⟨0, 0, 0, 1⟩

/-- A grade-1 vector from its two coordinates (its e₁ and e₂ coefficients); equals
    `x·e₁ + y·e₂` (`vec_eq_smul`). -/
def vec (x y : ℝ) : G2 := ⟨0, x, y, 0⟩

/-- The unit pseudoscalar I = e₁ * e₂. -/
def I : G2 := e_12

/-- The **squared magnitude** `|A|² = ⟨A Ã⟩₀` (Hestenes p.13 eq 1.49, gacalc `magnitude_squared`). -/
noncomputable def normSq (a : G2) : ℝ := (mul a (reverse a)).s

/-- The **magnitude** `|A| = √⟨A Ã⟩`, for all grades. -/
noncomputable def magnitude (a : G2) : ℝ := Real.sqrt (normSq a)

/-- `normSq a = Σ (component)²` — the scalar part of `a ã` is positive-definite (every blade's reverse
    sign cancels its square's sign). -/
theorem normSq_eq_sum_sq (a : G2) : normSq a = a.s ^ 2 + a.c1 ^ 2 + a.c2 ^ 2 + a.c12 ^ 2 := by
  simp only [normSq, mul, reverse]; ring

theorem normSq_nonneg (a : G2) : 0 ≤ normSq a := by
  rw [normSq_eq_sum_sq]; positivity

/-- `|a|² = normSq a` for ANY multivector — the one `√` fact the magnitude tier needs. -/
theorem magnitude_sq_eq_normSq (a : G2) : magnitude a ^ 2 = normSq a := by
  simp only [magnitude]; exact Real.sq_sqrt (normSq_nonneg a)

theorem magnitude_ne_zero_of_normSq_ne_zero {a : G2} (h : normSq a ≠ 0) : magnitude a ≠ 0 := by
  simp only [magnitude]
  exact Real.sqrt_ne_zero'.mpr (lt_of_le_of_ne (normSq_nonneg a) (Ne.symm h))

/-- **Leaf:** `|a|² = a₁² + a₂²` on a coordinate vector. -/
theorem normSq_vec (a1 a2 : ℝ) : normSq (vec a1 a2) = a1 ^ 2 + a2 ^ 2 := by
  simp only [normSq, mul, reverse, vec]; ring

/-- Every element is the linear combination of the basis blades with its coefficients:
    `g = s * 1 + c1 * e₁ + c2 * e₂ + c12 * e₁ * e₂`. This is the bridge between the coefficient
    fields and the basis *elements*. -/
theorem eq_smul_basis (g : G2) :
    g = add (add (smul g.s one) (smul g.c1 e_1)) (add (smul g.c2 e_2) (smul g.c12 e_12)) := by
  simp only [add, smul, one, e_1, e_2, e_12]; ext <;> ring

/-- A vector is `x·e₁ + y·e₂`. -/
theorem vec_eq_smul (x y : ℝ) : vec x y = add (smul x e_1) (smul y e_2) := by
  simp only [vec, add, smul, e_1, e_2]; ext <;> ring

/-! ### The geometric-product multiplication table for the basis vectors -/

/-- e₁² = 1. -/
theorem e_1_sq : mul e_1 e_1 = one := by simp only [mul, e_1, one]; ext <;> ring

/-- e₂² = 1. -/
theorem e_2_sq : mul e_2 e_2 = one := by simp only [mul, e_2, one]; ext <;> ring

/-- e₁ * e₂ = e₁₂ (the bivector is the product of the two basis vectors). -/
theorem e_1_mul_e_2 : mul e_1 e_2 = e_12 := by simp only [mul, e_1, e_2, e_12]; ext <;> ring

/-- e₂ * e₁ = −e₁₂ (anticommuting: the product is antisymmetric on orthogonal vectors). -/
theorem e_2_mul_e_1 : mul e_2 e_1 = neg e_12 := by simp only [mul, e_2, e_1, e_12, neg]; ext <;> ring

/-- (e₁ * e₂)² = −1. -/
theorem e_12_sq : mul e_12 e_12 = neg one := by simp only [mul, e_12, neg, one]; ext <;> ring

/-! ### Dot and wedge as the parts of the geometric product -/

/-- The geometric product of two vectors splits into a scalar (dot) plus an e₁ * e₂
    (wedge) part: u v = (u·v) + (u∧v) * e₁ * e₂. -/
theorem vec_mul (u1 u2 v1 v2 : ℝ) :
    mul (vec u1 u2) (vec v1 v2)
      = ⟨u1 * v1 + u2 * v2, 0, 0, u1 * v2 - u2 * v1⟩ := by
  simp only [mul, vec]; ext <;> ring

/-- A multivector is a **vector** (grade 1) exactly when its scalar and bivector (pseudoscalar) parts
    vanish — how "`a` is a vector" is stated for an arbitrary `a : G2` (no vector subtype). -/
def IsVector (a : G2) : Prop := a.s = 0 ∧ a.c12 = 0

/-- A grade-1 multivector is the `vec` of its own coordinates (2D) — the bridge to the `vec …` lemmas. -/
theorem eq_vec_of_isVector {a : G2} (ha : IsVector a) : a = vec a.c1 a.c2 := by
  obtain ⟨hs, h12⟩ := ha
  ext <;> simp only [vec] <;> first | rfl | assumption

/-- A coordinate vector `vec x y` is a vector (grade 1) — lets a caller discharge the `IsVector`
    hypothesis of an object-level theorem when it holds a concrete `vec`. -/
theorem isVector_vec (x y : ℝ) : IsVector (vec x y) := ⟨rfl, rfl⟩

/-- The **dot product** is the scalar part of the symmetric product ½(ab + ba) — for vectors `a`, `b`
    (object form; the coordinates are pulled from the operands for the computation). -/
theorem dot_is_sym_part {a b : G2} (ha : IsVector a) (hb : IsVector b) :
    (smul (1 / 2) (add (mul a b) (mul b a))).s = a.c1 * b.c1 + a.c2 * b.c2 := by
  obtain ⟨has, ha12⟩ := ha
  obtain ⟨hbs, hb12⟩ := hb
  simp only [smul, add, mul, has, ha12, hbs, hb12]; ring

/-- The **wedge product** is the e₁ * e₂ part of the antisymmetric product ½(ab − ba) — for vectors. -/
theorem wedge_is_antisym_part {a b : G2} (ha : IsVector a) (hb : IsVector b) :
    (smul (1 / 2) (sub (mul a b) (mul b a))).c12 = a.c1 * b.c2 - a.c2 * b.c1 := by
  obtain ⟨has, ha12⟩ := ha
  obtain ⟨hbs, hb12⟩ := hb
  simp only [smul, sub, mul, has, ha12, hbs, hb12]; ring

/-- Equivalence to the general case: the dot is the Euclidean coordinate sum ∑ aᵢbᵢ
    (= `@inner ℝ (EuclideanSpace ℝ (Fin 2)) _ a b`) — for vectors. -/
theorem dot_eq_coord_sum {a b : G2} (ha : IsVector a) (hb : IsVector b) :
    (mul a b).s = a.c1 * b.c1 + a.c2 * b.c2 := by
  obtain ⟨has, ha12⟩ := ha
  obtain ⟨hbs, hb12⟩ := hb
  simp only [mul, has, ha12, hbs, hb12]; ring

/-- The unit pseudoscalar squares to −1 (a scalar). -/
theorem I_sq : mul I I = ⟨-1, 0, 0, 0⟩ := by
  simp only [mul, I, e_12]; ext <;> ring

/-- I² = (−1)^(r(r−1)/2) with r = 2 — the special case of the general
    pseudoscalar-square sign (`tasks/reference/pseudoscalar-square-sign.md`). -/
theorem I_sq_eq_sign : (mul I I).s = (-1 : ℝ) ^ (2 * (2 - 1) / 2) := by
  simp only [mul, I, e_12]; norm_num

/-! ### The dual, and: the dual of a vector is perpendicular to it (2D) -/

/-- The inverse unit pseudoscalar I₂⁻¹ = −e₁₂ (since I₂² = −1, so I₂⁻¹ = −I₂). -/
def I_inv : G2 := ⟨0, 0, 0, -1⟩

/-- I₂ · I₂⁻¹ = 1, confirming `I_inv` is the inverse of the pseudoscalar `I`. -/
theorem I_mul_I_inv : mul I I_inv = one := by
  simp only [mul, I, e_12, I_inv, one]; ext <;> ring

/-- The dual `A* = A · I₂⁻¹` (grade r ↦ grade 2−r), matching gacalc's `dual` (base.py). -/
noncomputable def dual (a : G2) : G2 := mul a I_inv

/-- The dual of a vector is again a vector — the −90° rotation `(x, y) ↦ (y, −x)`. -/
theorem dual_vec (x y : ℝ) : dual (vec x y) = vec y (-x) := by
  simp only [dual, I_inv, mul, vec]; ext <;> ring

/-- **The dual of a vector is perpendicular to it** (2D): the dot product of `dual v` and
    `v` — the scalar part of their geometric product (`dot_eq_coord_sum`) — is zero. -/
theorem dual_vec_perp (x y : ℝ) : (mul (dual (vec x y)) (vec x y)).s = 0 := by
  simp only [dual, I_inv, mul, vec]; ring

/-! ### Reverse is an anti-automorphism, and reverses a product of vectors -/

/-- **Reverse is an anti-automorphism:** `(a b)~ = b~ a~`. General (no evenness needed) — the
    2D twin of `GacalcProofs.G3.reverse_mul`. -/
theorem reverse_mul (a b : G2) : reverse (mul a b) = mul (reverse b) (reverse a) := by
  simp only [reverse, mul]; ext <;> ring

/-- `reverse` fixes a coordinate vector (grade 1): the grade-2 part it flips is absent. -/
theorem reverse_vec (x y : ℝ) : reverse (vec x y) = vec x y := by
  simp only [reverse, vec]; ext <;> ring

/-- `reverse` fixes any grade-1 element (the `IsVector` form of `reverse_vec`). -/
theorem reverse_of_isVector {a : G2} (ha : IsVector a) : reverse a = a := by
  obtain ⟨_, h12⟩ := ha
  simp only [reverse]; ext <;> simp [h12]

/-- **Reverse reverses a product of vectors:** `(a b)~ = b a` for vectors `a, b` (2D). Corollary of
    the anti-automorphism `reverse_mul` and `reverse` fixing a vector (`reverse_of_isVector`). -/
theorem reverse_mul_vec {a b : G2} (ha : IsVector a) (hb : IsVector b) :
    reverse (mul a b) = mul b a := by
  rw [reverse_mul, reverse_of_isVector ha, reverse_of_isVector hb]

end G2

end GacalcProofs
