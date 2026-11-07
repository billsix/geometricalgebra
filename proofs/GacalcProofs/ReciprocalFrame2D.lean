import GacalcProofs.Projection2D

/-! # The reciprocal frame in 𝒢₂, and `Frame`'s two inverses

    Machine-checks the 2D case of the 2026-11-07 frame work (`src/gacalc/frame.py`):

    * the **reciprocal frame** of a frame `a₁, a₂` (H&S p. 28 eq 3.7 with `n = 2`):
      `aᵏ = (−1)^(k−1)*face_k*A₂⁻¹`, with `A₂ = a₁ ∧ a₂` and `face_k` the wedge of every frame vector
      but `a_k` (Python's `all_wedged_except_the_kth`), so `face₁ = a₂` and `face₂ = a₁`;
    * that each `aᵏ` is a vector, that `aᵏ·a_j` is the Kronecker delta (eq 3.5), and that
      `y = (a¹·y)*a₁ + (a²·y)*a₂` (eq 3.4);
    * the **similar-triangles** reading of a coordinate
      (`tasks/reference/frames-qr-and-reciprocal-frames.md`): for any `m` perpendicular to the other
      frame vector, `x_i = (m·y)/(m·a_i)`, and `aⁱ = m/(m·a_i)`;
    * that the **last reciprocal vector is the last rejection** divided by its squared length, and that
      the rejection is perpendicular to `a₁`;
    * that **both inverses** of `Frame.to_invertible_function` (`"reciprocal"` and `"peel"`) undo the
      forward map `f(x) = (x·e₁)*a₁ + (x·e₂)*a₂` on both sides, and agree.

    The frame hypothesis is "the wedge of all frame vectors is nonzero", written `normSq (a₁ ∧ a₂) ≠ 0`.
    Statements take vectors with `IsVector` hypotheses; coordinates appear only inside proofs and in the
    `_vec` leaves, which unfold a definition on `vec` literals (CLAUDE.md, "Coordinates only when
    needed"). -/
namespace GacalcProofs.G2

/-! ### Definitions -/

/-- The first reciprocal vector, eq 3.7 with `k = 1`: `a¹ = (+1)*a₂*(a₁ ∧ a₂)⁻¹` (the face of `a₁` is
    `a₂`). -/
noncomputable def recip1 (a1 a2 : G2) : G2 := mul a2 (inverse (wedge a1 a2))

/-- The second reciprocal vector, eq 3.7 with `k = 2`: `a² = (−1)*a₁*(a₁ ∧ a₂)⁻¹` (the face of `a₂` is
    `a₁`). -/
noncomputable def recip2 (a1 a2 : G2) : G2 := smul (-1) (mul a1 (inverse (wedge a1 a2)))

/-- The forward map of `Frame.to_invertible_function`: `f(x) = (x·e₁)*a₁ + (x·e₂)*a₂`, sending
    `e_i ↦ a_i`. -/
noncomputable def frameMap (a1 a2 x : G2) : G2 :=
  add (smul (dot x e_1) a1) (smul (dot x e_2) a2)

/-- The `"reciprocal"` inverse: `g(y) = (a¹·y)*e₁ + (a²·y)*e₂`. -/
noncomputable def invReciprocal (a1 a2 y : G2) : G2 :=
  add (smul (dot (recip1 a1 a2) y) e_1) (smul (dot (recip2 a1 a2) y) e_2)

/-- The peel's first step: the last coordinate, `x₂ = (w₂·y)/|w₂|²`, with `w₂` the rejection of `a₂`
    from `a₁`. -/
noncomputable def peelLast (a1 a2 y : G2) : ℝ := dot (reject a1 a2) y / normSq (reject a1 a2)

/-- The peel's second step: remove `x₂*a₂`, then read `x₁ = (w₁·r)/|w₁|²` with `w₁ = a₁`. -/
noncomputable def peelFirst (a1 a2 y : G2) : ℝ :=
  dot a1 (sub y (smul (peelLast a1 a2 y) a2)) / normSq a1

/-- The `"peel"` inverse: back-substitution from the last frame vector. -/
noncomputable def invPeel (a1 a2 y : G2) : G2 :=
  add (smul (peelFirst a1 a2 y) e_1) (smul (peelLast a1 a2 y) e_2)

/-! ### Coordinate leaves (each unfolds one definition on `vec` literals) -/

/-- `|a ∧ b|²` of two coordinate vectors is the squared signed area. -/
theorem normSq_wedge_vec' (p q r t : ℝ) :
    normSq (wedge (vec p q) (vec r t)) = (p * t - q * r) ^ 2 := by
  simp only [normSq, mul, reverse, wedge, vec]; ring

/-- A nonzero signed area makes the first vector nonzero. -/
theorem sumSq_ne_zero_of_area {p q r t : ℝ} (hd : p * t - q * r ≠ 0) : p ^ 2 + q ^ 2 ≠ 0 := by
  intro h
  have hp : p = 0 := pow_eq_zero_iff two_ne_zero |>.mp (by nlinarith [sq_nonneg p, sq_nonneg q])
  have hq : q = 0 := pow_eq_zero_iff two_ne_zero |>.mp (by nlinarith [sq_nonneg p, sq_nonneg q])
  exact hd (by rw [hp, hq]; ring)

theorem recip1_vec {p q r t : ℝ} (hd : p * t - q * r ≠ 0) :
    recip1 (vec p q) (vec r t) = vec (t / (p * t - q * r)) (-r / (p * t - q * r)) := by
  simp only [recip1, inverse, normSq_wedge_vec']
  ext <;> simp only [mul, smul, reverse, wedge, vec] <;> field_simp <;> ring

theorem recip2_vec {p q r t : ℝ} (hd : p * t - q * r ≠ 0) :
    recip2 (vec p q) (vec r t) = vec (-q / (p * t - q * r)) (p / (p * t - q * r)) := by
  simp only [recip2, inverse, normSq_wedge_vec']
  ext <;> simp only [mul, smul, reverse, wedge, vec] <;> field_simp <;> ring

theorem reject_vec {p q r t : ℝ} (hn : p ^ 2 + q ^ 2 ≠ 0) :
    reject (vec p q) (vec r t)
      = vec (-(q * (p * t - q * r)) / (p ^ 2 + q ^ 2)) (p * (p * t - q * r) / (p ^ 2 + q ^ 2)) := by
  simp only [reject, inverse, normSq_vec]
  ext <;> simp only [mul, smul, reverse, wedge, vec] <;> field_simp <;> ring

theorem normSq_reject_vec {p q r t : ℝ} (hn : p ^ 2 + q ^ 2 ≠ 0) :
    normSq (reject (vec p q) (vec r t)) = (p * t - q * r) ^ 2 / (p ^ 2 + q ^ 2) := by
  rw [reject_vec hn, normSq_vec]
  field_simp
  ring

/-- The frame hypothesis on two vectors, as a nonzero signed area. -/
theorem area_ne_zero {a1 a2 : G2} (ha1 : IsVector a1) (ha2 : IsVector a2)
    (hA : normSq (wedge a1 a2) ≠ 0) : a1.c1 * a2.c2 - a1.c2 * a2.c1 ≠ 0 := by
  rw [eq_vec_of_isVector ha1, eq_vec_of_isVector ha2, normSq_wedge_vec'] at hA
  simpa [vec] using hA

/-! ### The reciprocal frame (eqs 3.5, 3.4) -/

/-- **Each reciprocal vector is a vector** (grade 1), as eq 3.7 promises. -/
theorem isVector_recip1 {a1 a2 : G2} (ha1 : IsVector a1) (ha2 : IsVector a2)
    (hA : normSq (wedge a1 a2) ≠ 0) : IsVector (recip1 a1 a2) := by
  have hd := area_ne_zero ha1 ha2 hA
  rw [eq_vec_of_isVector ha1, eq_vec_of_isVector ha2, recip1_vec hd]
  exact isVector_vec _ _

theorem isVector_recip2 {a1 a2 : G2} (ha1 : IsVector a1) (ha2 : IsVector a2)
    (hA : normSq (wedge a1 a2) ≠ 0) : IsVector (recip2 a1 a2) := by
  have hd := area_ne_zero ha1 ha2 hA
  rw [eq_vec_of_isVector ha1, eq_vec_of_isVector ha2, recip2_vec hd]
  exact isVector_vec _ _

/-- **Eq 3.5, the Kronecker delta:** `aᵏ·a_j = 1` when `j = k` and `0` otherwise, all four cases. -/
theorem dot_recip_kronecker {a1 a2 : G2} (ha1 : IsVector a1) (ha2 : IsVector a2)
    (hA : normSq (wedge a1 a2) ≠ 0) :
    dot (recip1 a1 a2) a1 = 1 ∧ dot (recip1 a1 a2) a2 = 0 ∧
      dot (recip2 a1 a2) a1 = 0 ∧ dot (recip2 a1 a2) a2 = 1 := by
  have hd := area_ne_zero ha1 ha2 hA
  rw [eq_vec_of_isVector ha1, eq_vec_of_isVector ha2, recip1_vec hd, recip2_vec hd]
  refine ⟨?_, ?_, ?_, ?_⟩ <;> simp only [dot_vec] <;> field_simp <;> ring

/-- **Eq 3.4, reconstruction:** a vector is the sum of its reciprocal-frame coordinates times the frame,
    `y = (a¹·y)*a₁ + (a²·y)*a₂`. -/
theorem reconstruct {a1 a2 y : G2} (ha1 : IsVector a1) (ha2 : IsVector a2) (hy : IsVector y)
    (hA : normSq (wedge a1 a2) ≠ 0) :
    add (smul (dot (recip1 a1 a2) y) a1) (smul (dot (recip2 a1 a2) y) a2) = y := by
  have hd := area_ne_zero ha1 ha2 hA
  rw [eq_vec_of_isVector ha1, eq_vec_of_isVector ha2, eq_vec_of_isVector hy, recip1_vec hd,
    recip2_vec hd]
  ext <;> simp only [add, smul, dot_vec, vec] <;> field_simp <;> ring

/-! ### Similar triangles -/

/-- **One dot product reads off an oblique coordinate.** If `m` is perpendicular to `a₂` and not to
    `a₁`, then the coordinate of `y = x₁*a₁ + x₂*a₂` on `a₁` is `x₁ = (m·y)/(m·a₁)`: the height of `y`
    above `a₂`'s line, in units of `a₁`'s height. Structural (bilinearity of `dot`). -/
theorem coord1_of_perp {a1 a2 m : G2} (x1 x2 : ℝ) (hm2 : dot m a2 = 0) (hm1 : dot m a1 ≠ 0) :
    dot m (add (smul x1 a1) (smul x2 a2)) / dot m a1 = x1 := by
  rw [dot_add_right, dot_smul_right, dot_smul_right, hm2]
  field_simp
  ring

/-- The same for the coordinate on `a₂`, with `m` perpendicular to `a₁`. -/
theorem coord2_of_perp {a1 a2 m : G2} (x1 x2 : ℝ) (hm1 : dot m a1 = 0) (hm2 : dot m a2 ≠ 0) :
    dot m (add (smul x1 a1) (smul x2 a2)) / dot m a2 = x2 := by
  rw [dot_add_right, dot_smul_right, dot_smul_right, hm1]
  field_simp
  ring

/-- **The reciprocal vector is that normal, folded with its height:** for any vector `m` perpendicular
    to `a₂` with `m·a₁ ≠ 0`, `a¹ = m/(m·a₁)`. So eq 3.7 builds exactly the similar-triangles ratio. -/
theorem recip1_eq_normal_div {a1 a2 m : G2} (ha1 : IsVector a1) (ha2 : IsVector a2)
    (hm : IsVector m) (hA : normSq (wedge a1 a2) ≠ 0) (hm2 : dot m a2 = 0)
    (hm1 : dot m a1 ≠ 0) :
    recip1 a1 a2 = smul (1 / dot m a1) m := by
  have hd := area_ne_zero ha1 ha2 hA
  rw [eq_vec_of_isVector ha1, eq_vec_of_isVector ha2, eq_vec_of_isVector hm] at hm1 hm2 ⊢
  rw [recip1_vec hd]
  simp only [dot_vec] at hm1 hm2
  ext <;> simp only [smul, vec, dot_vec] <;> field_simp
  · linear_combination (-a1.c2) * hm2
  · linear_combination a1.c1 * hm2

theorem recip2_eq_normal_div {a1 a2 m : G2} (ha1 : IsVector a1) (ha2 : IsVector a2)
    (hm : IsVector m) (hA : normSq (wedge a1 a2) ≠ 0) (hm1 : dot m a1 = 0)
    (hm2 : dot m a2 ≠ 0) :
    recip2 a1 a2 = smul (1 / dot m a2) m := by
  have hd := area_ne_zero ha1 ha2 hA
  rw [eq_vec_of_isVector ha1, eq_vec_of_isVector ha2, eq_vec_of_isVector hm] at hm1 hm2 ⊢
  rw [recip2_vec hd]
  simp only [dot_vec] at hm1 hm2
  ext <;> simp only [smul, vec, dot_vec] <;> field_simp
  · linear_combination a2.c2 * hm1
  · linear_combination (-a2.c1) * hm1

/-! ### The peel: rejection orthogonality, and the last reciprocal vector -/

/-- **The rejection is perpendicular to what it was rejected from:** `w₂·a₁ = 0`, `w₂ = reject a₁ a₂`.
    The peel's first step rests on it. -/
theorem dot_reject_self {a1 a2 : G2} (ha1 : IsVector a1) (ha2 : IsVector a2)
    (hA : normSq (wedge a1 a2) ≠ 0) : dot (reject a1 a2) a1 = 0 := by
  have hn := sumSq_ne_zero_of_area (area_ne_zero ha1 ha2 hA)
  rw [eq_vec_of_isVector ha1, eq_vec_of_isVector ha2] at hn ⊢
  rw [reject_vec hn, dot_vec]
  field_simp
  ring

/-- **The last reciprocal vector is the last rejection over its squared length:** `a² = w₂/|w₂|²`.
    The peel finds one face normal by rejection; the reciprocal frame folds its height in. -/
theorem recip2_eq_reject_div {a1 a2 : G2} (ha1 : IsVector a1) (ha2 : IsVector a2)
    (hA : normSq (wedge a1 a2) ≠ 0) :
    recip2 a1 a2 = smul (1 / normSq (reject a1 a2)) (reject a1 a2) := by
  have hd := area_ne_zero ha1 ha2 hA
  have hn := sumSq_ne_zero_of_area hd
  rw [eq_vec_of_isVector ha1, eq_vec_of_isVector ha2] at hn ⊢
  rw [normSq_reject_vec hn, reject_vec hn, recip2_vec hd]
  ext <;> simp only [smul, vec] <;> field_simp <;> ring

/-! ### Both inverses undo the forward map, and agree -/

theorem invReciprocal_frameMap {a1 a2 x : G2} (ha1 : IsVector a1) (ha2 : IsVector a2)
    (hx : IsVector x) (hA : normSq (wedge a1 a2) ≠ 0) :
    invReciprocal a1 a2 (frameMap a1 a2 x) = x := by
  have hd := area_ne_zero ha1 ha2 hA
  rw [eq_vec_of_isVector ha1, eq_vec_of_isVector ha2, eq_vec_of_isVector hx]
  simp only [invReciprocal, frameMap, recip1_vec hd, recip2_vec hd]
  ext <;> simp only [add, smul, dot, mul, vec, e_1, e_2] <;> field_simp <;> ring

theorem frameMap_invReciprocal {a1 a2 y : G2} (ha1 : IsVector a1) (ha2 : IsVector a2)
    (hy : IsVector y) (hA : normSq (wedge a1 a2) ≠ 0) :
    frameMap a1 a2 (invReciprocal a1 a2 y) = y := by
  have hd := area_ne_zero ha1 ha2 hA
  rw [eq_vec_of_isVector ha1, eq_vec_of_isVector ha2, eq_vec_of_isVector hy]
  simp only [invReciprocal, frameMap, recip1_vec hd, recip2_vec hd]
  ext <;> simp only [add, smul, dot, mul, vec, e_1, e_2] <;> field_simp <;> ring

theorem invPeel_frameMap {a1 a2 x : G2} (ha1 : IsVector a1) (ha2 : IsVector a2)
    (hx : IsVector x) (hA : normSq (wedge a1 a2) ≠ 0) :
    invPeel a1 a2 (frameMap a1 a2 x) = x := by
  have hd := area_ne_zero ha1 ha2 hA
  have hn := sumSq_ne_zero_of_area hd
  rw [eq_vec_of_isVector ha1, eq_vec_of_isVector ha2, eq_vec_of_isVector hx] at *
  simp only [invPeel, peelFirst, peelLast, frameMap, normSq_reject_vec hn, reject_vec hn,
    normSq_vec]
  ext <;> simp only [add, sub, smul, dot, mul, vec, e_1, e_2] <;> field_simp <;> ring

theorem frameMap_invPeel {a1 a2 y : G2} (ha1 : IsVector a1) (ha2 : IsVector a2)
    (hy : IsVector y) (hA : normSq (wedge a1 a2) ≠ 0) :
    frameMap a1 a2 (invPeel a1 a2 y) = y := by
  have hd := area_ne_zero ha1 ha2 hA
  have hn := sumSq_ne_zero_of_area hd
  rw [eq_vec_of_isVector ha1, eq_vec_of_isVector ha2, eq_vec_of_isVector hy] at *
  simp only [invPeel, peelFirst, peelLast, frameMap, normSq_reject_vec hn, reject_vec hn,
    normSq_vec]
  ext <;> simp only [add, sub, smul, dot, mul, vec, e_1, e_2] <;> field_simp <;> ring

/-- **The two inverses agree** on every vector: both recover the unique coordinates. -/
theorem invReciprocal_eq_invPeel {a1 a2 y : G2} (ha1 : IsVector a1) (ha2 : IsVector a2)
    (hy : IsVector y) (hA : normSq (wedge a1 a2) ≠ 0) :
    invReciprocal a1 a2 y = invPeel a1 a2 y := by
  have hd := area_ne_zero ha1 ha2 hA
  have hn := sumSq_ne_zero_of_area hd
  rw [eq_vec_of_isVector ha1, eq_vec_of_isVector ha2, eq_vec_of_isVector hy] at *
  simp only [invReciprocal, invPeel, peelFirst, peelLast, recip1_vec hd, recip2_vec hd,
    normSq_reject_vec hn, reject_vec hn, normSq_vec]
  ext <;> simp only [add, sub, smul, dot, mul, vec, e_1, e_2] <;> field_simp <;> ring

end GacalcProofs.G2
