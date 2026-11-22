import GacalcProofs.Projection3D

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

end GacalcProofs.G3
