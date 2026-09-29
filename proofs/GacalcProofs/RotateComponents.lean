import GacalcProofs.Sandwich
import GacalcProofs.Projection

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
theorem sandwich_ahat (a1 a2 a3 b1 b2 b3 : ℝ)
    (ha : mag (vec a1 a2 a3) ≠ 0) (hb : mag (vec b1 b2 b3) ≠ 0)
    (hr : normSq (versorFromVectors (vec a1 a2 a3) (vec b1 b2 b3)) ≠ 0) :
    sandwich (versorFromVectors (vec a1 a2 a3) (vec b1 b2 b3))
             (smul (1 / mag (vec a1 a2 a3)) (vec a1 a2 a3))
      = smul (1 / mag (vec b1 b2 b3)) (vec b1 b2 b3) := by
  rw [sandwich_smul, sandwich_carries_from_to a1 a2 a3 b1 b2 b3 hb hr,
      GacalcProofs.G3.smul_smul]
  congr 1
  field_simp

/-! ### The three goals, for the actual a→b rotation `R = versorFromVectors a b`

    Goal 1 (rotates in the plane a→b): `sandwich_carries_from_to` (a↦b) + `plane_eq_wedge` (the plane
    is `a∧b`), plus `rotation_fixes_plane_bivector` below (the plane, oriented, is invariant).
    Goal 2 (rotates the *oriented* angle correctly): the sandwich is an oriented isometry —
    `rotation_preserves_dot` (angle magnitude) + `rotation_fixes_plane_bivector` (orientation); with
    `sandwich_carries_from_to` this pins the rotation by the oriented angle a→b.
    Goal 3 (perpendicular components unchanged): `rotation_fixes_normal`. -/

/-- **The rotation keeps its plane (oriented) fixed**: `sandwich R (b∧a) = b∧a`. Orientation is
    preserved — the mark of a rotation, not a reflection. (`R` is even with plane bivector `b∧a`.) -/
theorem rotation_fixes_plane_bivector (a1 a2 a3 b1 b2 b3 : ℝ)
    (hr : normSq (versorFromVectors (vec a1 a2 a3) (vec b1 b2 b3)) ≠ 0) :
    sandwich (versorFromVectors (vec a1 a2 a3) (vec b1 b2 b3))
             (wedge (vec b1 b2 b3) (vec a1 a2 a3))
      = wedge (vec b1 b2 b3) (vec a1 a2 a3) := by
  have hw : wedge (vec b1 b2 b3) (vec a1 a2 a3)
      = (⟨0, 0, 0, 0, b1 * a2 - b2 * a1, b1 * a3 - b3 * a1, b2 * a3 - b3 * a2, 0⟩ : G3) := by
    simp only [wedge, vec]; ext <;> ring
  rw [versorFromVectors_eq_evenVersor, hw]
  rw [versorFromVectors_eq_evenVersor, normSq_evenVersor] at hr
  exact sandwich_fixes_own_bivector _ _ _ _ hr

/-- **The rotation fixes the normal to its plane**: the axis `b×a = dual(b∧a)` (⊥ both `a` and `b`) is
    unchanged. This is "components perpendicular to the plane are not changed" for the a→b rotation. -/
theorem rotation_fixes_normal (a1 a2 a3 b1 b2 b3 : ℝ)
    (hr : normSq (versorFromVectors (vec a1 a2 a3) (vec b1 b2 b3)) ≠ 0) :
    sandwich (versorFromVectors (vec a1 a2 a3) (vec b1 b2 b3))
             (vec (b2 * a3 - b3 * a2) (-(b1 * a3 - b3 * a1)) (b1 * a2 - b2 * a1))
      = vec (b2 * a3 - b3 * a2) (-(b1 * a3 - b3 * a1)) (b1 * a2 - b2 * a1) := by
  rw [versorFromVectors_eq_evenVersor]
  rw [versorFromVectors_eq_evenVersor, normSq_evenVersor] at hr
  exact sandwich_fixes_own_normal _ _ _ _ hr

/-- **The rotation preserves the dot product** (angle magnitude): `(R u R⁻¹)·(R v R⁻¹) = u·v`, for the
    actual a→b rotation `R = versorFromVectors a b`. With `rotation_fixes_plane_bivector` (orientation),
    this is the oriented isometry — "rotates the oriented angle correctly." -/
theorem rotation_preserves_dot (a1 a2 a3 b1 b2 b3 u1 u2 u3 v1 v2 v3 : ℝ)
    (hr : normSq (versorFromVectors (vec a1 a2 a3) (vec b1 b2 b3)) ≠ 0) :
    dot (sandwich (versorFromVectors (vec a1 a2 a3) (vec b1 b2 b3)) (vec u1 u2 u3))
        (sandwich (versorFromVectors (vec a1 a2 a3) (vec b1 b2 b3)) (vec v1 v2 v3))
      = dot (vec u1 u2 u3) (vec v1 v2 v3) := by
  rw [versorFromVectors_eq_evenVersor]
  rw [versorFromVectors_eq_evenVersor, normSq_evenVersor] at hr
  exact sandwich_preserves_dot _ _ _ _ u1 u2 u3 v1 v2 v3 hr

end GacalcProofs.G3
