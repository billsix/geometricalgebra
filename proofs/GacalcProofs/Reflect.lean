import GacalcProofs.Projection3D
import GacalcProofs.Projection2D

/-! # Reflection across a vector (𝒢₃)

    gacalc's `reflect(across=d)` is "the projection minus the rejection" (base.py),
    `reflect_d v = proj_d v − reject_d v`. Since `proj + reject = v` (here via `reject_vec_eq`), this
    equals `2*proj_d v − v` — the defining characterization proved below, reusing the already-proven
    `proj`/`reject`. From the coverage-map gap audit
    (`tasks/archive/2026/10/01/lean-coverage-gap-audit.md`). -/
namespace GacalcProofs.G3

/-- Reflection of `v` across the vector `d`: `reflect_d v = proj_d v − reject_d v`. -/
noncomputable def reflectVec (d v : G3) : G3 := sub (proj d v) (reject d v)

-- twin: GacalcProofs.G3.reflectVec_eq
/-- **Reflection = twice the projection minus the vector**: `reflect_d v = 2*proj_d v − v`
    (equivalently `proj − reject`), for a nonzero vector `d` and a vector `v`. The Hestenes reflection's
    defining identity. Structural over `reject_vec_eq` (`reject = v − proj`), so `proj` stays abstract. -/
theorem reflectVec_eq {d v : G3} (hd_isv : IsVector d) (hv_isv : IsVector v) (hd : normSq d ≠ 0) :
    reflectVec d v = sub (smul 2 (proj d v)) v := by
  simp only [reflectVec]
  rw [reject_vec_eq hd_isv hv_isv hd]
  ext <;> simp only [sub, smul] <;> ring

/-- **Reflection preserves length** (it is an isometry): `|reflect_d v|² = |v|²`, for a nonzero vector `d`
    and a vector `v`. From `reflect = 2*proj − v` with `proj = (v·d / d·d)·d`; the `(d·d)` denominator
    cancels and the coordinate identity closes by `ring`. -/
theorem normSq_reflectVec {d v : G3} (hd_isv : IsVector d) (hv_isv : IsVector v) (hd : normSq d ≠ 0) :
    normSq (reflectVec d v) = normSq v := by
  have hdd : d.c1 ^ 2 + d.c2 ^ 2 + d.c3 ^ 2 ≠ 0 := by
    rw [← normSq_vec, ← eq_vec_of_isVector hd_isv]; exact hd
  rw [reflectVec_eq hd_isv hv_isv hd, proj]
  obtain ⟨hds, hd12, hd13, hd23, hd123⟩ := hd_isv
  simp only [normSq, dot, smul, sub, mul, reverse, hds, hd12, hd13, hd23, hd123]
  field_simp [hdd]
  ring

-- twin: GacalcProofs.G3.reflectVec_eq_sandwich
/-- **The reflection as a product:** `reflect_d v = d * v * d⁻¹` (the book's `eq-reflect-sandwich`), for a
    nonzero vector `d` and a vector `v`. The part of `v` along `d` commutes with `d` and stays; the part
    across anticommutes and is negated. -/
theorem reflectVec_eq_sandwich {d v : G3} (hd_isv : IsVector d) (hv_isv : IsVector v)
    (hd : normSq d ≠ 0) : reflectVec d v = mul (mul d v) (inverse d) := by
  obtain ⟨d1, d2, d3, rfl⟩ : ∃ x y z, d = vec x y z := ⟨_, _, _, eq_vec_of_isVector hd_isv⟩
  obtain ⟨v1, v2, v3, rfl⟩ : ∃ x y z, v = vec x y z := ⟨_, _, _, eq_vec_of_isVector hv_isv⟩
  rw [normSq_vec] at hd
  rw [reflectVec_eq hd_isv hv_isv (by rw [normSq_vec]; exact hd), proj]
  have hc : (d1 ^ 2 + d2 ^ 2 + d3 ^ 2) * (d1 ^ 2 + d2 ^ 2 + d3 ^ 2)⁻¹ = 1 := mul_inv_cancel₀ hd
  simp only [inverse, normSq_vec]
  simp only [dot, mul, smul, sub, reverse, vec]
  ext <;> simp only <;>
    first | ring1 | linear_combination v1 * hc | linear_combination v2 * hc | linear_combination v3 * hc

/-- A reflection of a vector is a vector. -/
theorem isVector_reflectVec {d v : G3} (hd_isv : IsVector d) (hv_isv : IsVector v)
    (hd : normSq d ≠ 0) : IsVector (reflectVec d v) := by
  rw [reflectVec_eq hd_isv hv_isv hd]
  exact (IsVector.smul (IsVector.smul hd_isv _) 2 |>.sub hv_isv |> fun h => by
    simpa [proj] using h)

-- twin: GacalcProofs.G3.reflectVec_twice
/-- **Reflecting twice across the same line gives the vector back** (𝒢₃): `reflect_d (reflect_d v) = v`.
    Reflection is `2*proj_d v − v` and projecting `2*proj_d v − v` onto `d` gives `proj_d v` again, so the
    second reflection is `2*proj_d v − (2*proj_d v − v)`. -/
theorem reflectVec_twice {d v : G3} (hd_isv : IsVector d) (hv_isv : IsVector v)
    (hd : normSq d ≠ 0) : reflectVec d (reflectVec d v) = v := by
  have hdd : dot d d ≠ 0 := by rw [dot_self_vec_eq_normSq hd_isv]; exact hd
  have hdp : dot (proj d v) d = dot v d := by
    rw [proj, dot_smul_left]; field_simp
  have hproj : proj d (sub (smul 2 (proj d v)) v) = proj d v := by
    have e : dot (sub (smul 2 (proj d v)) v) d = dot v d := by
      rw [dot_sub_left, dot_smul_left, hdp]; ring
    show smul (dot (sub (smul 2 (proj d v)) v) d / dot d d) d = smul (dot v d / dot d d) d
    rw [e]
  rw [reflectVec_eq hd_isv (isVector_reflectVec hd_isv hv_isv hd) hd, reflectVec_eq hd_isv hv_isv hd,
    hproj]
  ext <;> simp only [sub, smul] <;> ring

/-! ## Reflection in a plane, and across the plane's normal -/

/-- **The dual of a plane is a vector**: for a bivector `B`, `dual B = B * I⁻¹` has only grade-1
    parts. -/
theorem isVector_dual_of_isBivector {B : G3} (hB : IsBivector B) : IsVector (dual B) := by
  obtain ⟨hBs, hB1, hB2, hB3, hB123⟩ := hB
  refine ⟨?_, ?_, ?_, ?_, ?_⟩ <;>
    simp only [dual, I_inv, mul, hBs, hB1, hB2, hB3, hB123] <;> ring

/-- **A plane's normal is as long as the plane**: `|dual B|² = |B|²`, for a bivector `B`. -/
theorem normSq_dual_of_isBivector {B : G3} (hB : IsBivector B) : normSq (dual B) = normSq B := by
  obtain ⟨hBs, hB1, hB2, hB3, hB123⟩ := hB
  simp only [normSq, dual, I_inv, mul, reverse, hBs, hB1, hB2, hB3, hB123]
  ring

/-- Reflection of `v` in the plane `B`: `reflect_B v = project_B v − reject_B v` (gacalc's
    `reflect(across=B)`, base.py): the in-plane part kept, the perpendicular part flipped. -/
noncomputable def reflectPlane (B v : G3) : G3 := sub (project_onto B v) (reject B v)

-- twin: GacalcProofs.G3.reflectPlane_eq_neg_reflectVec_dual
/-- **The mirror in a plane is minus the reflection across its normal**: for a plane bivector `B`
    (`|B|² ≠ 0`) and a vector `v`, `reflect_B v = −reflect_{dual B} v`. The in-plane part of `v` is its
    rejection from the normal and the perpendicular part is its projection onto the normal
    (`reject_eq_proj_normal`), so the two reflections keep and flip opposite parts. -/
theorem reflectPlane_eq_neg_reflectVec_dual {B v : G3} (hB : IsBivector B) (hBn : normSq B ≠ 0)
    (hv : IsVector v) : reflectPlane B v = neg (reflectVec (dual B) v) := by
  have hn_isv : IsVector (dual B) := isVector_dual_of_isBivector hB
  have hn : normSq (dual B) ≠ 0 := by rw [normSq_dual_of_isBivector hB]; exact hBn
  simp only [reflectPlane, reflectVec]
  rw [project_eq_sub_reject hB hBn hv, reject_eq_proj_normal hB hBn hv,
    reject_vec_eq hn_isv hv hn]
  ext <;> simp only [sub, neg] <;> ring

-- twin: GacalcProofs.G3.normSq_reflectPlane
/-- **The mirror in a plane keeps every length** (𝒢₃): `|reflect_B v|² = |v|²`, for a plane `B` with
    `|B|² ≠ 0` and a vector `v`. It is minus the reflection across the plane's normal, and negation and
    reflection across a vector both keep length. -/
theorem normSq_reflectPlane {B v : G3} (hB : IsBivector B) (hBn : normSq B ≠ 0) (hv : IsVector v) :
    normSq (reflectPlane B v) = normSq v := by
  have hn_isv : IsVector (dual B) := isVector_dual_of_isBivector hB
  have hn : normSq (dual B) ≠ 0 := by rw [normSq_dual_of_isBivector hB]; exact hBn
  rw [reflectPlane_eq_neg_reflectVec_dual hB hBn hv, ← normSq_reflectVec hn_isv hv hn]
  simp only [normSq, neg, mul, reverse]
  ring

end GacalcProofs.G3

namespace GacalcProofs.G2

/-- Reflection of `v` across the vector `d` in 𝒢₂: `reflect_d v = proj_d v − reject_d v`. -/
noncomputable def reflectVec (d v : G2) : G2 := sub (proj d v) (reject d v)

/-- **Reflection is twice the projection minus the vector** (𝒢₂): `reflect_d v = 2*proj_d v − v`. -/
theorem reflectVec_eq {d v : G2} (hd_isv : IsVector d) (hv_isv : IsVector v) (hd : normSq d ≠ 0) :
    reflectVec d v = sub (smul 2 (proj d v)) v := by
  obtain ⟨d1, d2, rfl⟩ : ∃ x y, d = vec x y := ⟨_, _, eq_vec_of_isVector hd_isv⟩
  obtain ⟨v1, v2, rfl⟩ : ∃ x y, v = vec x y := ⟨_, _, eq_vec_of_isVector hv_isv⟩
  rw [normSq_vec] at hd
  have hc : (d1 ^ 2 + d2 ^ 2) * (d1 ^ 2 + d2 ^ 2)⁻¹ = 1 := mul_inv_cancel₀ hd
  simp only [reflectVec, reject, proj, inverse, normSq_vec]
  simp only [dot, mul, smul, sub, wedge, reverse, vec]
  ext <;> simp only <;> first | ring1 | linear_combination (-v1) * hc | linear_combination (-v2) * hc

-- twin: GacalcProofs.G2.reflectVec_eq_sandwich
/-- **The reflection as a product, 𝒢₂:** `reflect_d v = d * v * d⁻¹` for a nonzero vector `d` and a vector
    `v`. The easy case `d = e₁` multiplies out to `(x, y) ↦ (x, −y)`. -/
theorem reflectVec_eq_sandwich {d v : G2} (hd_isv : IsVector d) (hv_isv : IsVector v)
    (hd : normSq d ≠ 0) : reflectVec d v = mul (mul d v) (inverse d) := by
  rw [reflectVec_eq hd_isv hv_isv hd]
  obtain ⟨d1, d2, rfl⟩ : ∃ x y, d = vec x y := ⟨_, _, eq_vec_of_isVector hd_isv⟩
  obtain ⟨v1, v2, rfl⟩ : ∃ x y, v = vec x y := ⟨_, _, eq_vec_of_isVector hv_isv⟩
  rw [normSq_vec] at hd
  have hc : (d1 ^ 2 + d2 ^ 2) * (d1 ^ 2 + d2 ^ 2)⁻¹ = 1 := mul_inv_cancel₀ hd
  simp only [proj, inverse, normSq_vec]
  simp only [dot, mul, smul, sub, reverse, vec]
  ext <;> simp only <;> first | ring1 | linear_combination v1 * hc | linear_combination v2 * hc

/-- **A reflection keeps every length** (𝒢₂): `|reflect_d v|² = |v|²`. -/
theorem normSq_reflectVec {d v : G2} (hd_isv : IsVector d) (hv_isv : IsVector v)
    (hd : normSq d ≠ 0) : normSq (reflectVec d v) = normSq v := by
  rw [reflectVec_eq hd_isv hv_isv hd]
  obtain ⟨d1, d2, rfl⟩ : ∃ x y, d = vec x y := ⟨_, _, eq_vec_of_isVector hd_isv⟩
  obtain ⟨v1, v2, rfl⟩ : ∃ x y, v = vec x y := ⟨_, _, eq_vec_of_isVector hv_isv⟩
  rw [normSq_vec] at hd
  have hc : (d1 ^ 2 + d2 ^ 2) * (d1 ^ 2 + d2 ^ 2)⁻¹ = 1 := mul_inv_cancel₀ hd
  simp only [proj, normSq_vec]
  simp only [normSq, dot, mul, smul, sub, reverse, vec]
  linear_combination 4 * (v1 * d1 + v2 * d2) ^ 2 * (d1 ^ 2 + d2 ^ 2)⁻¹ * hc

/-- A reflection of a vector is a vector (𝒢₂). -/
theorem isVector_reflectVec {d v : G2} (hd_isv : IsVector d) (hv_isv : IsVector v)
    (hd : normSq d ≠ 0) : IsVector (reflectVec d v) := by
  rw [reflectVec_eq hd_isv hv_isv hd]
  obtain ⟨hds, hd12⟩ := hd_isv
  obtain ⟨hvs, hv12⟩ := hv_isv
  exact ⟨by simp [sub, smul, proj, hds, hvs], by simp [sub, smul, proj, hd12, hv12]⟩

-- twin: GacalcProofs.G2.reflectVec_twice
/-- **Reflecting twice across the same line gives the vector back** (𝒢₂), by the same two steps as 𝒢₃. -/
theorem reflectVec_twice {d v : G2} (hd_isv : IsVector d) (hv_isv : IsVector v)
    (hd : normSq d ≠ 0) : reflectVec d (reflectVec d v) = v := by
  have hdd : dot d d ≠ 0 := by rw [dot_self_vec_eq_normSq hd_isv]; exact hd
  have hdp : dot (proj d v) d = dot v d := by
    rw [proj, dot_smul_left]; field_simp
  have hproj : proj d (sub (smul 2 (proj d v)) v) = proj d v := by
    have e : dot (sub (smul 2 (proj d v)) v) d = dot v d := by
      rw [dot_sub_left, dot_smul_left, hdp]; ring
    show smul (dot (sub (smul 2 (proj d v)) v) d / dot d d) d = smul (dot v d / dot d d) d
    rw [e]
  rw [reflectVec_eq hd_isv (isVector_reflectVec hd_isv hv_isv hd) hd, reflectVec_eq hd_isv hv_isv hd,
    hproj]
  ext <;> simp only [sub, smul] <;> ring

end GacalcProofs.G2
