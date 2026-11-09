import GacalcProofs.Projection3D

/-! # The reciprocal frame in 𝒢₃, and `Frame`'s two inverses

    The 3D case of the 2026-11-07 frame work (`src/gacalc/frame.py`); the 2D case, with the same
    theorem list, is `ReciprocalFrame2D.lean`.

    * the **reciprocal frame** of `a₁, a₂, a₃` (H&S p. 28 eq 3.7 with `n = 3`):
      `aᵏ = (−1)^(k−1)*face_k*A₃⁻¹`, `A₃ = a₁ ∧ a₂ ∧ a₃`, with `face₁ = a₂ ∧ a₃`, `face₂ = a₁ ∧ a₃`,
      `face₃ = a₁ ∧ a₂` (Python's `all_wedged_except_the_kth`);
    * each `aᵏ` is a vector, `aᵏ·a_j` is the Kronecker delta (eq 3.5), and both reconstructions
      `y = Σ (aᵏ·y)*a_k` and `y = Σ (a_k·y)*aᵏ` (eq 3.4);
    * **similar triangles:** for `m` perpendicular to the other two frame vectors,
      `x_i = (m·y)/(m·a_i)` and `aⁱ = m/(m·a_i)`;
    * the **last reciprocal vector is the last rejection** over its squared length, `a³ = w₃/|w₃|²`,
      with `w₃` the rejection of `a₃` from the plane `a₁ ∧ a₂`;
    * **both inverses** of `Frame.to_invertible_function` undo `f(x) = Σ (x*e_i)*a_i` on both sides and
      agree. The peel is proved structurally: on `y = x₁*a₁ + x₂*a₂ + x₃*a₃` it reads back `x₃`, `x₂`,
      `x₁` in turn, because each rejection is perpendicular to the frame vectors before it.

    The frame hypothesis is `normSq (a₁ ∧ a₂ ∧ a₃) ≠ 0`. Coordinates appear only inside proofs and in the
    `_vec` leaves; `det3` (the signed volume) and `crossSq` (`|a₁ × a₂|²`) name the two scalars those
    leaves divide by. -/
namespace GacalcProofs.G3

/-! ### Definitions -/

/-- The volume trivector `A₃ = a₁ ∧ a₂ ∧ a₃`. -/
noncomputable def vol3 (a1 a2 a3 : G3) : G3 := wedge (wedge a1 a2) a3

/-- `a¹ = (+1)*(a₂ ∧ a₃)*A₃⁻¹` (eq 3.7, `k = 1`). -/
noncomputable def recip1 (a1 a2 a3 : G3) : G3 := mul (wedge a2 a3) (inverse (vol3 a1 a2 a3))

/-- `a² = (−1)*(a₁ ∧ a₃)*A₃⁻¹` (eq 3.7, `k = 2`). -/
noncomputable def recip2 (a1 a2 a3 : G3) : G3 :=
  smul (-1) (mul (wedge a1 a3) (inverse (vol3 a1 a2 a3)))

/-- `a³ = (+1)*(a₁ ∧ a₂)*A₃⁻¹` (eq 3.7, `k = 3`). -/
noncomputable def recip3 (a1 a2 a3 : G3) : G3 := mul (wedge a1 a2) (inverse (vol3 a1 a2 a3))

/-- `x₁*a₁ + x₂*a₂ + x₃*a₃`. -/
noncomputable def comb (a1 a2 a3 : G3) (x1 x2 x3 : ℝ) : G3 :=
  add (add (smul x1 a1) (smul x2 a2)) (smul x3 a3)

/-- The forward map of `Frame.to_invertible_function`: `f(x) = Σ (x*e_i)*a_i`, sending `e_i ↦ a_i`. -/
noncomputable def frameMap (a1 a2 a3 x : G3) : G3 := comb a1 a2 a3 (dot x e_1) (dot x e_2) (dot x e_3)

/-- The `"reciprocal"` inverse: `g(y) = Σ (aⁱ·y)*e_i`. -/
noncomputable def invReciprocal (a1 a2 a3 y : G3) : G3 :=
  comb e_1 e_2 e_3 (dot (recip1 a1 a2 a3) y) (dot (recip2 a1 a2 a3) y) (dot (recip3 a1 a2 a3) y)

/-- The peel's first step: `x₃ = (w₃·y)/|w₃|²`, `w₃` the rejection of `a₃` from the plane `a₁ ∧ a₂`. -/
noncomputable def peelLast (a1 a2 a3 y : G3) : ℝ :=
  dot (reject (wedge a1 a2) a3) y / normSq (reject (wedge a1 a2) a3)

/-- The second step: remove `x₃*a₃`, then `x₂ = (w₂·r)/|w₂|²`, `w₂` the rejection of `a₂` from `a₁`. -/
noncomputable def peelMid (a1 a2 a3 y : G3) : ℝ :=
  dot (reject a1 a2) (sub y (smul (peelLast a1 a2 a3 y) a3)) / normSq (reject a1 a2)

/-- The last step: remove `x₂*a₂` too, then `x₁ = (w₁·r)/|w₁|²` with `w₁ = a₁`. -/
noncomputable def peelFirst (a1 a2 a3 y : G3) : ℝ :=
  dot a1 (sub (sub y (smul (peelLast a1 a2 a3 y) a3)) (smul (peelMid a1 a2 a3 y) a2)) / normSq a1

/-- The `"peel"` inverse: back-substitution from the last frame vector. -/
noncomputable def invPeel (a1 a2 a3 y : G3) : G3 :=
  comb e_1 e_2 e_3 (peelFirst a1 a2 a3 y) (peelMid a1 a2 a3 y) (peelLast a1 a2 a3 y)

/-! ### Coordinate leaves -/

/-- The signed volume of three coordinate vectors, `a₁·(a₂ × a₃)`. -/
noncomputable def det3 (p1 p2 p3 r1 r2 r3 t1 t2 t3 : ℝ) : ℝ :=
  p1 * (r2 * t3 - r3 * t2) - p2 * (r1 * t3 - r3 * t1) + p3 * (r1 * t2 - r2 * t1)

/-- `|a₁ × a₂|²` of two coordinate vectors (equal to `|a₁ ∧ a₂|²`). -/
noncomputable def crossSq (p1 p2 p3 r1 r2 r3 : ℝ) : ℝ :=
  (p2 * r3 - p3 * r2) ^ 2 + (p1 * r3 - p3 * r1) ^ 2 + (p1 * r2 - p2 * r1) ^ 2

theorem normSq_vol3_vec (p1 p2 p3 r1 r2 r3 t1 t2 t3 : ℝ) :
    normSq (vol3 (vec p1 p2 p3) (vec r1 r2 r3) (vec t1 t2 t3))
      = det3 p1 p2 p3 r1 r2 r3 t1 t2 t3 ^ 2 := by
  simp only [vol3, normSq, mul, reverse, wedge, vec, det3]; ring

theorem det3_ne_zero_vec {p1 p2 p3 r1 r2 r3 t1 t2 t3 : ℝ}
    (hA : normSq (vol3 (vec p1 p2 p3) (vec r1 r2 r3) (vec t1 t2 t3)) ≠ 0) :
    det3 p1 p2 p3 r1 r2 r3 t1 t2 t3 ≠ 0 :=
  fun h => hA (by rw [normSq_vol3_vec, h]; ring)

theorem normSq_wedge_vec3 (p1 p2 p3 r1 r2 r3 : ℝ) :
    normSq (wedge (vec p1 p2 p3) (vec r1 r2 r3)) = crossSq p1 p2 p3 r1 r2 r3 := by
  simp only [normSq, mul, reverse, wedge, vec, crossSq]; ring

/-- A nonzero volume makes the plane of the first two vectors nondegenerate. -/
theorem crossSq_ne_zero_of_det3 {p1 p2 p3 r1 r2 r3 t1 t2 t3 : ℝ}
    (hD : det3 p1 p2 p3 r1 r2 r3 t1 t2 t3 ≠ 0) : crossSq p1 p2 p3 r1 r2 r3 ≠ 0 := by
  intro h
  simp only [crossSq] at h
  have e1 : p2 * r3 - p3 * r2 = 0 := pow_eq_zero_iff two_ne_zero |>.mp (by
    nlinarith [sq_nonneg (p2 * r3 - p3 * r2), sq_nonneg (p1 * r3 - p3 * r1),
      sq_nonneg (p1 * r2 - p2 * r1)])
  have e2 : p1 * r3 - p3 * r1 = 0 := pow_eq_zero_iff two_ne_zero |>.mp (by
    nlinarith [sq_nonneg (p2 * r3 - p3 * r2), sq_nonneg (p1 * r3 - p3 * r1),
      sq_nonneg (p1 * r2 - p2 * r1)])
  have e3 : p1 * r2 - p2 * r1 = 0 := pow_eq_zero_iff two_ne_zero |>.mp (by
    nlinarith [sq_nonneg (p2 * r3 - p3 * r2), sq_nonneg (p1 * r3 - p3 * r1),
      sq_nonneg (p1 * r2 - p2 * r1)])
  exact hD (by simp only [det3]; linear_combination t1 * e1 - t2 * e2 + t3 * e3)

/-- A nonzero plane makes its first vector nonzero. -/
theorem sumSq_ne_zero_of_crossSq {p1 p2 p3 r1 r2 r3 : ℝ}
    (hC : crossSq p1 p2 p3 r1 r2 r3 ≠ 0) : p1 ^ 2 + p2 ^ 2 + p3 ^ 2 ≠ 0 := by
  intro h
  have hp1 : p1 = 0 := pow_eq_zero_iff two_ne_zero |>.mp (by
    nlinarith [sq_nonneg p1, sq_nonneg p2, sq_nonneg p3])
  have hp2 : p2 = 0 := pow_eq_zero_iff two_ne_zero |>.mp (by
    nlinarith [sq_nonneg p1, sq_nonneg p2, sq_nonneg p3])
  have hp3 : p3 = 0 := pow_eq_zero_iff two_ne_zero |>.mp (by
    nlinarith [sq_nonneg p1, sq_nonneg p2, sq_nonneg p3])
  exact hC (by simp only [crossSq, hp1, hp2, hp3]; ring)

theorem recip1_vec {p1 p2 p3 r1 r2 r3 t1 t2 t3 : ℝ} (hD : det3 p1 p2 p3 r1 r2 r3 t1 t2 t3 ≠ 0) :
    recip1 (vec p1 p2 p3) (vec r1 r2 r3) (vec t1 t2 t3)
      = vec ((r2 * t3 - r3 * t2) / det3 p1 p2 p3 r1 r2 r3 t1 t2 t3)
          ((r3 * t1 - r1 * t3) / det3 p1 p2 p3 r1 r2 r3 t1 t2 t3)
          ((r1 * t2 - r2 * t1) / det3 p1 p2 p3 r1 r2 r3 t1 t2 t3) := by
  simp only [recip1, inverse, normSq_vol3_vec]
  ext <;> simp only [vol3, mul, smul, reverse, wedge, vec] <;> field_simp <;>
    (try simp only [det3]) <;> ring

theorem recip2_vec {p1 p2 p3 r1 r2 r3 t1 t2 t3 : ℝ} (hD : det3 p1 p2 p3 r1 r2 r3 t1 t2 t3 ≠ 0) :
    recip2 (vec p1 p2 p3) (vec r1 r2 r3) (vec t1 t2 t3)
      = vec ((t2 * p3 - t3 * p2) / det3 p1 p2 p3 r1 r2 r3 t1 t2 t3)
          ((t3 * p1 - t1 * p3) / det3 p1 p2 p3 r1 r2 r3 t1 t2 t3)
          ((t1 * p2 - t2 * p1) / det3 p1 p2 p3 r1 r2 r3 t1 t2 t3) := by
  simp only [recip2, inverse, normSq_vol3_vec]
  ext <;> simp only [vol3, mul, smul, reverse, wedge, vec] <;> field_simp <;>
    (try simp only [det3]) <;> ring

theorem recip3_vec {p1 p2 p3 r1 r2 r3 t1 t2 t3 : ℝ} (hD : det3 p1 p2 p3 r1 r2 r3 t1 t2 t3 ≠ 0) :
    recip3 (vec p1 p2 p3) (vec r1 r2 r3) (vec t1 t2 t3)
      = vec ((p2 * r3 - p3 * r2) / det3 p1 p2 p3 r1 r2 r3 t1 t2 t3)
          ((p3 * r1 - p1 * r3) / det3 p1 p2 p3 r1 r2 r3 t1 t2 t3)
          ((p1 * r2 - p2 * r1) / det3 p1 p2 p3 r1 r2 r3 t1 t2 t3) := by
  simp only [recip3, inverse, normSq_vol3_vec]
  ext <;> simp only [vol3, mul, smul, reverse, wedge, vec] <;> field_simp <;>
    (try simp only [det3]) <;> ring

/-- The rejection of `a₃` from the plane `a₁ ∧ a₂`: `(det/|c|²)*c`, with `c = a₁ × a₂`. -/
theorem reject_plane_vec {p1 p2 p3 r1 r2 r3 t1 t2 t3 : ℝ} (hC : crossSq p1 p2 p3 r1 r2 r3 ≠ 0) :
    reject (wedge (vec p1 p2 p3) (vec r1 r2 r3)) (vec t1 t2 t3)
      = vec (det3 p1 p2 p3 r1 r2 r3 t1 t2 t3 * (p2 * r3 - p3 * r2) / crossSq p1 p2 p3 r1 r2 r3)
          (det3 p1 p2 p3 r1 r2 r3 t1 t2 t3 * (p3 * r1 - p1 * r3) / crossSq p1 p2 p3 r1 r2 r3)
          (det3 p1 p2 p3 r1 r2 r3 t1 t2 t3 * (p1 * r2 - p2 * r1) / crossSq p1 p2 p3 r1 r2 r3) := by
  simp only [reject, inverse, normSq_wedge_vec3]
  ext <;> simp only [mul, smul, reverse, wedge, vec] <;> field_simp <;>
    (try simp only [det3, crossSq]) <;> ring

/-- The rejection of `a₂` from `a₁`: `a₂ − ((a₁·a₂)/|a₁|²)*a₁`. -/
theorem reject_line_vec {p1 p2 p3 r1 r2 r3 : ℝ} (hn : p1 ^ 2 + p2 ^ 2 + p3 ^ 2 ≠ 0) :
    reject (vec p1 p2 p3) (vec r1 r2 r3)
      = vec (r1 - (p1 * r1 + p2 * r2 + p3 * r3) / (p1 ^ 2 + p2 ^ 2 + p3 ^ 2) * p1)
          (r2 - (p1 * r1 + p2 * r2 + p3 * r3) / (p1 ^ 2 + p2 ^ 2 + p3 ^ 2) * p2)
          (r3 - (p1 * r1 + p2 * r2 + p3 * r3) / (p1 ^ 2 + p2 ^ 2 + p3 ^ 2) * p3) := by
  simp only [reject, inverse, normSq_vec]
  ext <;> simp only [mul, smul, reverse, wedge, vec] <;> field_simp <;> ring

theorem normSq_reject_plane_vec {p1 p2 p3 r1 r2 r3 t1 t2 t3 : ℝ}
    (hC : crossSq p1 p2 p3 r1 r2 r3 ≠ 0) :
    normSq (reject (wedge (vec p1 p2 p3) (vec r1 r2 r3)) (vec t1 t2 t3))
      = det3 p1 p2 p3 r1 r2 r3 t1 t2 t3 ^ 2 / crossSq p1 p2 p3 r1 r2 r3 := by
  rw [reject_plane_vec hC, normSq_vec]
  field_simp
  simp only [crossSq]
  ring

theorem normSq_reject_line_vec {p1 p2 p3 r1 r2 r3 : ℝ} (hn : p1 ^ 2 + p2 ^ 2 + p3 ^ 2 ≠ 0) :
    normSq (reject (vec p1 p2 p3) (vec r1 r2 r3))
      = crossSq p1 p2 p3 r1 r2 r3 / (p1 ^ 2 + p2 ^ 2 + p3 ^ 2) := by
  rw [reject_line_vec hn, normSq_vec]
  field_simp
  simp only [crossSq]
  ring

/-! ### Object-level facts about the frame -/

/-- The frame hypothesis, unpacked: the volume and the plane `a₁ ∧ a₂` are nonzero, and so is `a₁`. -/
theorem frame_nonzero {a1 a2 a3 : G3} (ha1 : IsVector a1) (ha2 : IsVector a2) (ha3 : IsVector a3)
    (hA : normSq (vol3 a1 a2 a3) ≠ 0) :
    normSq (wedge a1 a2) ≠ 0 ∧ normSq a1 ≠ 0 := by
  obtain ⟨p1, p2, p3, rfl⟩ : ∃ x y z, a1 = vec x y z := ⟨_, _, _, eq_vec_of_isVector ha1⟩
  obtain ⟨r1, r2, r3, rfl⟩ : ∃ x y z, a2 = vec x y z := ⟨_, _, _, eq_vec_of_isVector ha2⟩
  obtain ⟨t1, t2, t3, rfl⟩ : ∃ x y z, a3 = vec x y z := ⟨_, _, _, eq_vec_of_isVector ha3⟩
  have hC := crossSq_ne_zero_of_det3 (det3_ne_zero_vec hA)
  rw [normSq_wedge_vec3, normSq_vec]
  exact ⟨hC, sumSq_ne_zero_of_crossSq hC⟩

/-! ### The reciprocal frame (eqs 3.5, 3.4) -/

theorem isVector_recip {a1 a2 a3 : G3} (ha1 : IsVector a1) (ha2 : IsVector a2) (ha3 : IsVector a3)
    (hA : normSq (vol3 a1 a2 a3) ≠ 0) :
    IsVector (recip1 a1 a2 a3) ∧ IsVector (recip2 a1 a2 a3) ∧ IsVector (recip3 a1 a2 a3) := by
  obtain ⟨p1, p2, p3, rfl⟩ : ∃ x y z, a1 = vec x y z := ⟨_, _, _, eq_vec_of_isVector ha1⟩
  obtain ⟨r1, r2, r3, rfl⟩ : ∃ x y z, a2 = vec x y z := ⟨_, _, _, eq_vec_of_isVector ha2⟩
  obtain ⟨t1, t2, t3, rfl⟩ : ∃ x y z, a3 = vec x y z := ⟨_, _, _, eq_vec_of_isVector ha3⟩
  have hD := det3_ne_zero_vec hA
  rw [recip1_vec hD, recip2_vec hD, recip3_vec hD]
  exact ⟨isVector_vec _ _ _, isVector_vec _ _ _, isVector_vec _ _ _⟩

/-- **Eq 3.5, the Kronecker delta:** `aᵏ·a_j = 1` when `j = k` and `0` otherwise, all nine cases. -/
theorem dot_recip_kronecker {a1 a2 a3 : G3} (ha1 : IsVector a1) (ha2 : IsVector a2)
    (ha3 : IsVector a3) (hA : normSq (vol3 a1 a2 a3) ≠ 0) :
    (dot (recip1 a1 a2 a3) a1 = 1 ∧ dot (recip1 a1 a2 a3) a2 = 0 ∧ dot (recip1 a1 a2 a3) a3 = 0) ∧
    (dot (recip2 a1 a2 a3) a1 = 0 ∧ dot (recip2 a1 a2 a3) a2 = 1 ∧ dot (recip2 a1 a2 a3) a3 = 0) ∧
    (dot (recip3 a1 a2 a3) a1 = 0 ∧ dot (recip3 a1 a2 a3) a2 = 0 ∧ dot (recip3 a1 a2 a3) a3 = 1) := by
  obtain ⟨p1, p2, p3, rfl⟩ : ∃ x y z, a1 = vec x y z := ⟨_, _, _, eq_vec_of_isVector ha1⟩
  obtain ⟨r1, r2, r3, rfl⟩ : ∃ x y z, a2 = vec x y z := ⟨_, _, _, eq_vec_of_isVector ha2⟩
  obtain ⟨t1, t2, t3, rfl⟩ : ∃ x y z, a3 = vec x y z := ⟨_, _, _, eq_vec_of_isVector ha3⟩
  have hD := det3_ne_zero_vec hA
  rw [recip1_vec hD, recip2_vec hD, recip3_vec hD]
  refine ⟨⟨?_, ?_, ?_⟩, ⟨?_, ?_, ?_⟩, ⟨?_, ?_, ?_⟩⟩ <;> simp only [dot_vec] <;> field_simp <;>
    (try simp only [det3]) <;> ring

/-- **Eq 3.4, reconstruction:** `y = (a¹·y)*a₁ + (a²·y)*a₂ + (a³·y)*a₃`. -/
theorem reconstruct {a1 a2 a3 y : G3} (ha1 : IsVector a1) (ha2 : IsVector a2) (ha3 : IsVector a3)
    (hy : IsVector y) (hA : normSq (vol3 a1 a2 a3) ≠ 0) :
    comb a1 a2 a3 (dot (recip1 a1 a2 a3) y) (dot (recip2 a1 a2 a3) y) (dot (recip3 a1 a2 a3) y)
      = y := by
  obtain ⟨p1, p2, p3, rfl⟩ : ∃ x y z, a1 = vec x y z := ⟨_, _, _, eq_vec_of_isVector ha1⟩
  obtain ⟨r1, r2, r3, rfl⟩ : ∃ x y z, a2 = vec x y z := ⟨_, _, _, eq_vec_of_isVector ha2⟩
  obtain ⟨t1, t2, t3, rfl⟩ : ∃ x y z, a3 = vec x y z := ⟨_, _, _, eq_vec_of_isVector ha3⟩
  obtain ⟨y1, y2, y3, rfl⟩ : ∃ u v w, y = vec u v w := ⟨_, _, _, eq_vec_of_isVector hy⟩
  have hD := det3_ne_zero_vec hA
  rw [recip1_vec hD, recip2_vec hD, recip3_vec hD]
  simp only [dot_vec]
  ext <;> simp only [comb, add, smul, vec] <;> field_simp <;> (try simp only [det3]) <;> ring

/-- **Eq 3.4 with the roles swapped:** `y = (a₁·y)*a¹ + (a₂·y)*a² + (a₃·y)*a³`. -/
theorem reconstruct_dual {a1 a2 a3 y : G3} (ha1 : IsVector a1) (ha2 : IsVector a2)
    (ha3 : IsVector a3) (hy : IsVector y) (hA : normSq (vol3 a1 a2 a3) ≠ 0) :
    comb (recip1 a1 a2 a3) (recip2 a1 a2 a3) (recip3 a1 a2 a3) (dot a1 y) (dot a2 y) (dot a3 y)
      = y := by
  obtain ⟨p1, p2, p3, rfl⟩ : ∃ x y z, a1 = vec x y z := ⟨_, _, _, eq_vec_of_isVector ha1⟩
  obtain ⟨r1, r2, r3, rfl⟩ : ∃ x y z, a2 = vec x y z := ⟨_, _, _, eq_vec_of_isVector ha2⟩
  obtain ⟨t1, t2, t3, rfl⟩ : ∃ x y z, a3 = vec x y z := ⟨_, _, _, eq_vec_of_isVector ha3⟩
  obtain ⟨y1, y2, y3, rfl⟩ : ∃ u v w, y = vec u v w := ⟨_, _, _, eq_vec_of_isVector hy⟩
  have hD := det3_ne_zero_vec hA
  rw [recip1_vec hD, recip2_vec hD, recip3_vec hD]
  simp only [dot_vec]
  ext <;> simp only [comb, add, smul, vec] <;> field_simp <;> (try simp only [det3]) <;> ring

/-! ### Similar triangles -/

/-- **One dot product reads off an oblique coordinate:** if `m` is perpendicular to `a₂` and `a₃` and
    not to `a₁`, the coordinate on `a₁` of `y = x₁*a₁ + x₂*a₂ + x₃*a₃` is `(m·y)/(m·a₁)`. -/
theorem coord1_of_perp {a1 a2 a3 m : G3} (x1 x2 x3 : ℝ) (hm2 : dot m a2 = 0) (hm3 : dot m a3 = 0)
    (hm1 : dot m a1 ≠ 0) : dot m (comb a1 a2 a3 x1 x2 x3) / dot m a1 = x1 := by
  simp only [comb, dot_add_right, dot_smul_right, hm2, hm3]
  field_simp
  ring

theorem coord2_of_perp {a1 a2 a3 m : G3} (x1 x2 x3 : ℝ) (hm1 : dot m a1 = 0) (hm3 : dot m a3 = 0)
    (hm2 : dot m a2 ≠ 0) : dot m (comb a1 a2 a3 x1 x2 x3) / dot m a2 = x2 := by
  simp only [comb, dot_add_right, dot_smul_right, hm1, hm3]
  field_simp
  ring

theorem coord3_of_perp {a1 a2 a3 m : G3} (x1 x2 x3 : ℝ) (hm1 : dot m a1 = 0) (hm2 : dot m a2 = 0)
    (hm3 : dot m a3 ≠ 0) : dot m (comb a1 a2 a3 x1 x2 x3) / dot m a3 = x3 := by
  simp only [comb, dot_add_right, dot_smul_right, hm1, hm2]
  field_simp
  ring

/-- **The reciprocal vector is that normal, folded with its height:** for any vector `m` perpendicular
    to `a₂` and `a₃` with `m·a₁ ≠ 0`, `a¹ = m/(m·a₁)`. Structural: `m = Σ (a_k·m)*aᵏ`
    (`reconstruct_dual`), and only the first term survives. -/
theorem recip1_eq_normal_div {a1 a2 a3 m : G3} (ha1 : IsVector a1) (ha2 : IsVector a2)
    (ha3 : IsVector a3) (hm : IsVector m) (hA : normSq (vol3 a1 a2 a3) ≠ 0)
    (hm2 : dot m a2 = 0) (hm3 : dot m a3 = 0) (hm1 : dot m a1 ≠ 0) :
    recip1 a1 a2 a3 = smul (1 / dot m a1) m := by
  have h := reconstruct_dual ha1 ha2 ha3 hm hA
  rw [dot_comm a1 m, dot_comm a2 m, dot_comm a3 m, hm2, hm3] at h
  generalize hc : dot m a1 = c at hm1 h ⊢
  rw [← h]
  ext <;> simp only [comb, add, smul] <;> field_simp <;> ring

theorem recip2_eq_normal_div {a1 a2 a3 m : G3} (ha1 : IsVector a1) (ha2 : IsVector a2)
    (ha3 : IsVector a3) (hm : IsVector m) (hA : normSq (vol3 a1 a2 a3) ≠ 0)
    (hm1 : dot m a1 = 0) (hm3 : dot m a3 = 0) (hm2 : dot m a2 ≠ 0) :
    recip2 a1 a2 a3 = smul (1 / dot m a2) m := by
  have h := reconstruct_dual ha1 ha2 ha3 hm hA
  rw [dot_comm a1 m, dot_comm a2 m, dot_comm a3 m, hm1, hm3] at h
  generalize hc : dot m a2 = c at hm2 h ⊢
  rw [← h]
  ext <;> simp only [comb, add, smul] <;> field_simp <;> ring

theorem recip3_eq_normal_div {a1 a2 a3 m : G3} (ha1 : IsVector a1) (ha2 : IsVector a2)
    (ha3 : IsVector a3) (hm : IsVector m) (hA : normSq (vol3 a1 a2 a3) ≠ 0)
    (hm1 : dot m a1 = 0) (hm2 : dot m a2 = 0) (hm3 : dot m a3 ≠ 0) :
    recip3 a1 a2 a3 = smul (1 / dot m a3) m := by
  have h := reconstruct_dual ha1 ha2 ha3 hm hA
  rw [dot_comm a1 m, dot_comm a2 m, dot_comm a3 m, hm1, hm2] at h
  generalize hc : dot m a3 = c at hm3 h ⊢
  rw [← h]
  ext <;> simp only [comb, add, smul] <;> field_simp <;> ring

/-! ### The peel: the rejections, and the last reciprocal vector -/

/-- **The rejection from the plane is perpendicular to the plane's vectors**, and its dot with `a₃` is
    its squared length: `w₃·a₁ = 0`, `w₃·a₂ = 0`, `w₃·a₃ = |w₃|²`. -/
theorem reject_plane_facts {a1 a2 a3 : G3} (ha1 : IsVector a1) (ha2 : IsVector a2)
    (ha3 : IsVector a3) (hA : normSq (vol3 a1 a2 a3) ≠ 0) :
    dot (reject (wedge a1 a2) a3) a1 = 0 ∧ dot (reject (wedge a1 a2) a3) a2 = 0 ∧
      dot (reject (wedge a1 a2) a3) a3 = normSq (reject (wedge a1 a2) a3) ∧
      normSq (reject (wedge a1 a2) a3) ≠ 0 := by
  obtain ⟨p1, p2, p3, rfl⟩ : ∃ x y z, a1 = vec x y z := ⟨_, _, _, eq_vec_of_isVector ha1⟩
  obtain ⟨r1, r2, r3, rfl⟩ : ∃ x y z, a2 = vec x y z := ⟨_, _, _, eq_vec_of_isVector ha2⟩
  obtain ⟨t1, t2, t3, rfl⟩ : ∃ x y z, a3 = vec x y z := ⟨_, _, _, eq_vec_of_isVector ha3⟩
  have hD := det3_ne_zero_vec hA
  have hC := crossSq_ne_zero_of_det3 hD
  rw [normSq_reject_plane_vec hC, reject_plane_vec hC]
  refine ⟨?_, ?_, ?_, div_ne_zero (pow_ne_zero 2 hD) hC⟩
  · rw [dot_vec]; field_simp; ring
  · rw [dot_vec]; field_simp; ring
  · rw [dot_vec]; field_simp; simp only [det3]; ring

/-- **The rejection of `a₂` from `a₁`** is perpendicular to `a₁`, its dot with `a₂` is its squared
    length, and it is nonzero. -/
theorem reject_line_facts {a1 a2 a3 : G3} (ha1 : IsVector a1) (ha2 : IsVector a2)
    (ha3 : IsVector a3) (hA : normSq (vol3 a1 a2 a3) ≠ 0) :
    dot (reject a1 a2) a1 = 0 ∧ dot (reject a1 a2) a2 = normSq (reject a1 a2) ∧
      normSq (reject a1 a2) ≠ 0 := by
  obtain ⟨p1, p2, p3, rfl⟩ : ∃ x y z, a1 = vec x y z := ⟨_, _, _, eq_vec_of_isVector ha1⟩
  obtain ⟨r1, r2, r3, rfl⟩ : ∃ x y z, a2 = vec x y z := ⟨_, _, _, eq_vec_of_isVector ha2⟩
  obtain ⟨t1, t2, t3, rfl⟩ : ∃ x y z, a3 = vec x y z := ⟨_, _, _, eq_vec_of_isVector ha3⟩
  have hC := crossSq_ne_zero_of_det3 (det3_ne_zero_vec hA)
  have hn := sumSq_ne_zero_of_crossSq hC
  rw [normSq_reject_line_vec hn, reject_line_vec hn]
  refine ⟨?_, ?_, div_ne_zero hC hn⟩
  · rw [dot_vec]; field_simp; ring
  · rw [dot_vec]; field_simp; simp only [crossSq]; ring

/-- **The last reciprocal vector is the last rejection over its squared length:** `a³ = w₃/|w₃|²`. -/
theorem recip3_eq_reject_div {a1 a2 a3 : G3} (ha1 : IsVector a1) (ha2 : IsVector a2)
    (ha3 : IsVector a3) (hA : normSq (vol3 a1 a2 a3) ≠ 0) :
    recip3 a1 a2 a3
      = smul (1 / normSq (reject (wedge a1 a2) a3)) (reject (wedge a1 a2) a3) := by
  obtain ⟨p1, p2, p3, rfl⟩ : ∃ x y z, a1 = vec x y z := ⟨_, _, _, eq_vec_of_isVector ha1⟩
  obtain ⟨r1, r2, r3, rfl⟩ : ∃ x y z, a2 = vec x y z := ⟨_, _, _, eq_vec_of_isVector ha2⟩
  obtain ⟨t1, t2, t3, rfl⟩ : ∃ x y z, a3 = vec x y z := ⟨_, _, _, eq_vec_of_isVector ha3⟩
  have hD := det3_ne_zero_vec hA
  have hC := crossSq_ne_zero_of_det3 hD
  rw [normSq_reject_plane_vec hC, reject_plane_vec hC, recip3_vec hD]
  ext <;> simp only [smul, vec] <;> field_simp <;> ring

/-! ### Both inverses undo the forward map, and agree -/

/-- **The peel reads back the coordinates of any combination of the frame.** Structural: `w₃` sees only
    `a₃`'s term, then `w₂` sees only `a₂`'s, then `a₁` sees only its own. -/
theorem invPeel_comb {a1 a2 a3 : G3} (ha1 : IsVector a1) (ha2 : IsVector a2) (ha3 : IsVector a3)
    (hA : normSq (vol3 a1 a2 a3) ≠ 0) (x1 x2 x3 : ℝ) :
    invPeel a1 a2 a3 (comb a1 a2 a3 x1 x2 x3) = comb e_1 e_2 e_3 x1 x2 x3 := by
  obtain ⟨h31, h32, h33, h3n⟩ := reject_plane_facts ha1 ha2 ha3 hA
  obtain ⟨h21, h22, h2n⟩ := reject_line_facts ha1 ha2 ha3 hA
  have h1n : normSq a1 ≠ 0 := (frame_nonzero ha1 ha2 ha3 hA).2
  have h11 : dot a1 a1 = normSq a1 := dot_self_vec_eq_normSq ha1
  have hl : peelLast a1 a2 a3 (comb a1 a2 a3 x1 x2 x3) = x3 := by
    simp only [peelLast, comb, dot_add_right, dot_smul_right, h31, h32, h33]
    field_simp
    ring
  have hm : peelMid a1 a2 a3 (comb a1 a2 a3 x1 x2 x3) = x2 := by
    rw [peelMid, hl]
    simp only [comb, dot_sub_right, dot_add_right, dot_smul_right, h21, h22]
    field_simp
    ring
  have hf : peelFirst a1 a2 a3 (comb a1 a2 a3 x1 x2 x3) = x1 := by
    rw [peelFirst, hl, hm]
    simp only [comb, dot_sub_right, dot_add_right, dot_smul_right, h11]
    field_simp
    ring
  simp only [invPeel, hf, hm, hl]

/-- `Σ (x*e_i)*e_i = x` for a vector. -/
theorem comb_basis_dot {x : G3} (hx : IsVector x) :
    comb e_1 e_2 e_3 (dot x e_1) (dot x e_2) (dot x e_3) = x := by
  obtain ⟨x1, x2, x3, rfl⟩ : ∃ a b c, x = vec a b c := ⟨_, _, _, eq_vec_of_isVector hx⟩
  ext <;> simp only [comb, add, smul, dot, mul, vec, e_1, e_2, e_3] <;> ring

/-- The coordinates of `Σ x_i*e_i` are the `x_i`. -/
theorem dot_comb_basis (x1 x2 x3 : ℝ) :
    dot (comb e_1 e_2 e_3 x1 x2 x3) e_1 = x1 ∧ dot (comb e_1 e_2 e_3 x1 x2 x3) e_2 = x2 ∧
      dot (comb e_1 e_2 e_3 x1 x2 x3) e_3 = x3 := by
  refine ⟨?_, ?_, ?_⟩ <;> simp only [comb, add, smul, dot, mul, e_1, e_2, e_3] <;> ring

theorem invPeel_frameMap {a1 a2 a3 x : G3} (ha1 : IsVector a1) (ha2 : IsVector a2)
    (ha3 : IsVector a3) (hx : IsVector x) (hA : normSq (vol3 a1 a2 a3) ≠ 0) :
    invPeel a1 a2 a3 (frameMap a1 a2 a3 x) = x := by
  rw [frameMap, invPeel_comb ha1 ha2 ha3 hA, comb_basis_dot hx]

/-- On any vector, the peel returns the reciprocal-frame coordinates. -/
theorem invPeel_eq_reciprocal_coords {a1 a2 a3 y : G3} (ha1 : IsVector a1) (ha2 : IsVector a2)
    (ha3 : IsVector a3) (hy : IsVector y) (hA : normSq (vol3 a1 a2 a3) ≠ 0) :
    invPeel a1 a2 a3 y
      = comb e_1 e_2 e_3 (dot (recip1 a1 a2 a3) y) (dot (recip2 a1 a2 a3) y)
          (dot (recip3 a1 a2 a3) y) := by
  have key := invPeel_comb ha1 ha2 ha3 hA (dot (recip1 a1 a2 a3) y) (dot (recip2 a1 a2 a3) y)
    (dot (recip3 a1 a2 a3) y)
  rwa [reconstruct ha1 ha2 ha3 hy hA] at key

theorem frameMap_invPeel {a1 a2 a3 y : G3} (ha1 : IsVector a1) (ha2 : IsVector a2)
    (ha3 : IsVector a3) (hy : IsVector y) (hA : normSq (vol3 a1 a2 a3) ≠ 0) :
    frameMap a1 a2 a3 (invPeel a1 a2 a3 y) = y := by
  obtain ⟨d1, d2, d3⟩ := dot_comb_basis (dot (recip1 a1 a2 a3) y) (dot (recip2 a1 a2 a3) y)
    (dot (recip3 a1 a2 a3) y)
  rw [invPeel_eq_reciprocal_coords ha1 ha2 ha3 hy hA, frameMap, d1, d2, d3]
  exact reconstruct ha1 ha2 ha3 hy hA

theorem frameMap_invReciprocal {a1 a2 a3 y : G3} (ha1 : IsVector a1) (ha2 : IsVector a2)
    (ha3 : IsVector a3) (hy : IsVector y) (hA : normSq (vol3 a1 a2 a3) ≠ 0) :
    frameMap a1 a2 a3 (invReciprocal a1 a2 a3 y) = y := by
  obtain ⟨d1, d2, d3⟩ := dot_comb_basis (dot (recip1 a1 a2 a3) y) (dot (recip2 a1 a2 a3) y)
    (dot (recip3 a1 a2 a3) y)
  rw [invReciprocal, frameMap, d1, d2, d3]
  exact reconstruct ha1 ha2 ha3 hy hA

theorem invReciprocal_frameMap {a1 a2 a3 x : G3} (ha1 : IsVector a1) (ha2 : IsVector a2)
    (ha3 : IsVector a3) (hx : IsVector x) (hA : normSq (vol3 a1 a2 a3) ≠ 0) :
    invReciprocal a1 a2 a3 (frameMap a1 a2 a3 x) = x := by
  obtain ⟨⟨k11, k12, k13⟩, ⟨k21, k22, k23⟩, ⟨k31, k32, k33⟩⟩ :=
    dot_recip_kronecker ha1 ha2 ha3 hA
  conv_rhs => rw [← comb_basis_dot hx]
  rw [invReciprocal, frameMap]
  simp only [comb, dot_add_right, dot_smul_right]
  rw [k11, k12, k13, k21, k22, k23, k31, k32, k33]
  ring_nf

/-- **The two inverses agree** on every vector. -/
theorem invReciprocal_eq_invPeel {a1 a2 a3 y : G3} (ha1 : IsVector a1) (ha2 : IsVector a2)
    (ha3 : IsVector a3) (hy : IsVector y) (hA : normSq (vol3 a1 a2 a3) ≠ 0) :
    invReciprocal a1 a2 a3 y = invPeel a1 a2 a3 y := by
  rw [invPeel_eq_reciprocal_coords ha1 ha2 ha3 hy hA, invReciprocal]

end GacalcProofs.G3
