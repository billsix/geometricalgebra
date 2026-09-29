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

end GacalcProofs.G3
