import GacalcProofs.Sandwich
import GacalcProofs.Projection3D
import GacalcProofs.Cross

/-! # The 3D sandwich rotates in-plane components correctly (sin/cos from dot & wedge)

    Extends the sandwich beyond "carries `a` to `b`" (see `tasks/lean-proof-sandwich-rotates-components.md`):
    in the orthonormal frame `{â, r̂}` of the rotation plane (`â = a/|a|`, `r̂ = r/|r|`,
    `r = b − proj_a b`), the sandwich `R v R⁻¹` acts as the 2D rotation matrix `[[c, −s], [s, c]]`, with
    `c = cos θ = (a·b)/(|a||b|)` and `s = sin θ` read off the **dot and wedge** of `a` and `b`, and the
    angle θ never computed. Built in stages; this file currently carries Stage 1 (linearity + `â ↦ b̂`).

    Frame/orientation decisions (maintainer, 2026-09-29): orthonormal `{â, r̂}`; `sin θ ≥ 0` oriented by
    `a ∧ b`; prove the explicit rotated-vector equation with `c² + s² = 1` (from `lagrange_3d`) as a
    corollary. -/
namespace GacalcProofs.G3

/-- **The sandwich sends `â` to `b̂`** (the first column of the rotation matrix): the unit vector along
    `a` maps to the unit vector along `b`. From linearity + `sandwich_carries_from_to`
    (`R a R⁻¹ = (|a|/|b|)·b`), the `|a|` scales cancel. Since `b̂ = cos θ·â + sin θ·r̂`, this already
    exhibits `â`'s image with components `(cos θ, sin θ)` in the plane frame. -/
theorem sandwich_ahat_coord (a1 a2 a3 b1 b2 b3 : ℝ)
    (ha : magnitude (vec a1 a2 a3) ≠ 0) (hb : magnitude (vec b1 b2 b3) ≠ 0)
    (hr : normSq (versorFromVectors (vec a1 a2 a3) (vec b1 b2 b3)) ≠ 0) :
    sandwich (versorFromVectors (vec a1 a2 a3) (vec b1 b2 b3))
             (smul (1 / magnitude (vec a1 a2 a3)) (vec a1 a2 a3))
      = smul (1 / magnitude (vec b1 b2 b3)) (vec b1 b2 b3) := by
  rw [sandwich_smul, sandwich_carries_from_to_coord a1 a2 a3 b1 b2 b3 hb hr,
      GacalcProofs.G3.smul_smul]
  congr 1
  field_simp

/-- Object form of `sandwich_ahat_coord`, for nonzero vectors `a`, `b`. -/
theorem sandwich_ahat {a b : G3} (ha_isv : IsVector a) (hb_isv : IsVector b)
    (ha : magnitude a ≠ 0) (hb : magnitude b ≠ 0)
    (hr : normSq (versorFromVectors a b) ≠ 0) :
    sandwich (versorFromVectors a b) (smul (1 / magnitude a) a)
      = smul (1 / magnitude b) b := by
  have h := sandwich_ahat_coord a.c1 a.c2 a.c3 b.c1 b.c2 b.c3
    (by rw [← eq_vec_of_isVector ha_isv]; exact ha)
    (by rw [← eq_vec_of_isVector hb_isv]; exact hb)
    (by rw [← eq_vec_of_isVector ha_isv, ← eq_vec_of_isVector hb_isv]; exact hr)
  rwa [← eq_vec_of_isVector ha_isv, ← eq_vec_of_isVector hb_isv] at h

/-! ### The three goals, for the actual a→b rotation `R = versorFromVectors a b`

    Goal 1 (rotates in the plane a→b): `sandwich_carries_from_to` (a↦b) + `plane_eq_wedge` (the plane
    is `a∧b`), plus `rotation_fixes_plane_bivector` below (the plane, oriented, is invariant).
    Goal 2 (rotates the *oriented* angle correctly): the sandwich is an oriented isometry —
    `rotation_preserves_dot` (angle magnitude) + `rotation_fixes_plane_bivector` (orientation); with
    `sandwich_carries_from_to` this pins the rotation by the oriented angle a→b.
    Goal 3 (perpendicular components unchanged): `rotation_fixes_normal`. -/

/-- **The rotation keeps its plane (oriented) fixed**: `sandwich R (b∧a) = b∧a` for the a→b rotation
    `R = versorFromVectors a b`. Orientation is preserved — the mark of a rotation, not a reflection. -/
theorem rotation_fixes_plane_bivector {a b : G3} (ha : IsVector a) (hb : IsVector b)
    (hr : normSq (versorFromVectors a b) ≠ 0) :
    sandwich (versorFromVectors a b) (wedge b a) = wedge b a := by
  rw [eq_vec_of_isVector ha, eq_vec_of_isVector hb] at hr ⊢
  have hw := wedge_vec_eq_biv b.c1 b.c2 b.c3 a.c1 a.c2 a.c3
  rw [versorFromVectors_eq_evenVersor, hw]
  rw [versorFromVectors_eq_evenVersor] at hr
  exact sandwich_fixes_own_bivector_coord _ _ _ _ hr

/-- **The rotation fixes the normal to its plane**: the axis `b×a = dual(b∧a)` (⊥ both `a` and `b`) is
    unchanged. This is "components perpendicular to the plane are not changed" for the a→b rotation. -/
theorem rotation_fixes_normal_coord (a1 a2 a3 b1 b2 b3 : ℝ)
    (hr : normSq (versorFromVectors (vec a1 a2 a3) (vec b1 b2 b3)) ≠ 0) :
    sandwich (versorFromVectors (vec a1 a2 a3) (vec b1 b2 b3))
             (vec (b2 * a3 - b3 * a2) (-(b1 * a3 - b3 * a1)) (b1 * a2 - b2 * a1))
      = vec (b2 * a3 - b3 * a2) (-(b1 * a3 - b3 * a1)) (b1 * a2 - b2 * a1) := by
  rw [versorFromVectors_eq_evenVersor]
  rw [versorFromVectors_eq_evenVersor] at hr
  exact sandwich_fixes_own_normal_coord _ _ _ _ hr

/-- Object form of `rotation_fixes_normal_coord`: the normal `b × a = dual(b∧a)` is fixed. Stated
    coordinate-free as the cross product `cross b a` (= the explicit normal, via `cross_vec`). -/
theorem rotation_fixes_normal {a b : G3} (ha : IsVector a) (hb : IsVector b)
    (hr : normSq (versorFromVectors a b) ≠ 0) :
    sandwich (versorFromVectors a b) (cross b a) = cross b a := by
  have h := rotation_fixes_normal_coord a.c1 a.c2 a.c3 b.c1 b.c2 b.c3
    (by rw [← eq_vec_of_isVector ha, ← eq_vec_of_isVector hb]; exact hr)
  have hcross : cross b a
      = vec (b.c2 * a.c3 - b.c3 * a.c2) (b.c3 * a.c1 - b.c1 * a.c3) (b.c1 * a.c2 - b.c2 * a.c1) := by
    conv_lhs => rw [eq_vec_of_isVector hb, eq_vec_of_isVector ha]
    rw [cross_vec]
  have hsign : -(b.c1 * a.c3 - b.c3 * a.c1) = b.c3 * a.c1 - b.c1 * a.c3 := by ring
  rw [hcross]
  rw [← eq_vec_of_isVector ha, ← eq_vec_of_isVector hb, hsign] at h
  exact h

/-- **Any perpendicular vector is fixed** — every scalar multiple of the normal `b×a = dual(b∧a)` is
    unchanged by the rotation. In 3D the orthogonal complement of the a∧b plane is exactly the normal
    line, so this is the full "components perpendicular to the plane are not changed" for any vector
    (its perpendicular part is a multiple of the normal). Linearity + `rotation_fixes_normal`. -/
theorem rotation_fixes_perp {a b : G3} (ha : IsVector a) (hb : IsVector b) (k : ℝ)
    (hr : normSq (versorFromVectors a b) ≠ 0) :
    sandwich (versorFromVectors a b) (smul k (cross b a)) = smul k (cross b a) := by
  rw [sandwich_smul, rotation_fixes_normal ha hb hr]

/-- **The rotation preserves the dot product** (angle magnitude): `(R u R⁻¹)·(R v R⁻¹) = u·v` for the
    a→b rotation `R = versorFromVectors a b` and ANY `u`, `v`; the oriented isometry. -/
theorem rotation_preserves_dot {a b u v : G3}
    (ha : IsVector a) (hb : IsVector b)
    (hr : normSq (versorFromVectors a b) ≠ 0) :
    dot (sandwich (versorFromVectors a b) u) (sandwich (versorFromVectors a b) v)
      = dot u v := by
  have hR : IsEvenVersor (versorFromVectors a b) := by
    rw [eq_vec_of_isVector ha, eq_vec_of_isVector hb, versorFromVectors_eq_evenVersor]
    exact isEvenVersor_evenVersor _ _ _ _
  exact sandwich_preserves_dot hR hr

end GacalcProofs.G3
