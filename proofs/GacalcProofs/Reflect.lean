import GacalcProofs.Projection3D

/-! # Reflection across a vector (𝒢₃)

    gacalc's `reflect(across=d)` is "the projection minus the rejection" (base.py:1463),
    `reflect_d v = proj_d v − reject_d v`. Since `proj + reject = v` (here via `reject_vec_eq`), this
    equals `2·proj_d v − v` — the defining characterization proved below, reusing the already-proven
    `proj`/`reject`. From the coverage-map gap audit
    (`tasks/archive/2026/10/01/lean-coverage-gap-audit.md`). -/
namespace GacalcProofs.G3

/-- Reflection of `v` across the vector `d`: `reflect_d v = proj_d v − reject_d v`. -/
noncomputable def reflectVec (d v : G3) : G3 := sub (proj d v) (reject d v)

/-- **Reflection = twice the projection minus the vector**: `reflect_d v = 2·proj_d v − v`
    (equivalently `proj − reject`), for `d·d ≠ 0`. The Hestenes reflection's defining identity. -/
theorem reflectVec_eq (d1 d2 d3 v1 v2 v3 : ℝ) (hd : normSq (vec d1 d2 d3) ≠ 0) :
    reflectVec (vec d1 d2 d3) (vec v1 v2 v3)
      = sub (smul 2 (proj (vec d1 d2 d3) (vec v1 v2 v3))) (vec v1 v2 v3) := by
  simp only [reflectVec]
  rw [reject_vec_eq d1 d2 d3 v1 v2 v3 hd]
  ext <;> simp only [sub, smul] <;> ring

/-- **Reflection preserves length** (it is an isometry): `|reflect_d v|² = |v|²`, for `d·d ≠ 0`.
    From `reflect = 2·proj − v` with `proj = (v·d / d·d)·d`; the `(d·d)` denominator cancels and the
    coordinate identity closes by `ring`. -/
theorem normSq_reflectVec (d1 d2 d3 v1 v2 v3 : ℝ) (hd : normSq (vec d1 d2 d3) ≠ 0) :
    normSq (reflectVec (vec d1 d2 d3) (vec v1 v2 v3)) = normSq (vec v1 v2 v3) := by
  have hdd : d1 ^ 2 + d2 ^ 2 + d3 ^ 2 ≠ 0 := by rw [← normSq_vec]; exact hd
  rw [reflectVec_eq d1 d2 d3 v1 v2 v3 hd, proj, dot_self_vec_eq_normSq, normSq_vec]
  simp only [dot, smul, sub, mul, reverse, normSq, vec]
  field_simp
  ring
