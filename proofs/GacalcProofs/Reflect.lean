import GacalcProofs.Projection3D

/-! # Reflection across a vector (𝒢₃)

    gacalc's `reflect(across=d)` is "the projection minus the rejection" (base.py),
    `reflect_d v = proj_d v − reject_d v`. Since `proj + reject = v` (here via `reject_vec_eq`), this
    equals `2 * proj_d v − v` — the defining characterization proved below, reusing the already-proven
    `proj`/`reject`. From the coverage-map gap audit
    (`tasks/archive/2026/10/01/lean-coverage-gap-audit.md`). -/
namespace GacalcProofs.G3

/-- Reflection of `v` across the vector `d`: `reflect_d v = proj_d v − reject_d v`. -/
noncomputable def reflectVec (d v : G3) : G3 := sub (proj d v) (reject d v)

/-- **Reflection = twice the projection minus the vector**: `reflect_d v = 2 * proj_d v − v`
    (equivalently `proj − reject`), for a nonzero vector `d` and a vector `v`. The Hestenes reflection's
    defining identity. Structural over `reject_vec_eq` (`reject = v − proj`), so `proj` stays abstract. -/
theorem reflectVec_eq {d v : G3} (hd_isv : IsVector d) (hv_isv : IsVector v) (hd : normSq d ≠ 0) :
    reflectVec d v = sub (smul 2 (proj d v)) v := by
  simp only [reflectVec]
  rw [reject_vec_eq hd_isv hv_isv hd]
  ext <;> simp only [sub, smul] <;> ring

/-- **Reflection preserves length** (it is an isometry): `|reflect_d v|² = |v|²`, for a nonzero vector `d`
    and a vector `v`. From `reflect = 2 * proj − v` with `proj = (v·d / d·d)·d`; the `(d·d)` denominator
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
