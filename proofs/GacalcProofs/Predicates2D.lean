import GacalcProofs.Versor2D

/-! # Orthogonality predicate (𝒢₂)

    The 2D twin of `Predicates3D.lean`. States perpendicularity through the named scalar
    product `dot` (⟨A B⟩₀, defined in `Versor2D.lean`) over an arbitrary vector (`IsVector`),
    rather than by reading a raw coordinate field — the object/named-function form of the
    coordinate leaf `G2.dual_vec_perp` (`G2.lean`), which stays as the bridge it rests on. -/
namespace GacalcProofs.G2

/-- **The dual of a vector is perpendicular to it** (2D): for any vector `v` (`IsVector`), the dot
    product of its dual with itself is zero, `(v*) · v = 0`. The named-`dot`, object-level form of
    the coordinate leaf `dual_vec_perp`. -/
theorem dual_perp {v : G2} (hv : IsVector v) : dot (dual v) v = 0 := by
  obtain ⟨hs, h12⟩ := hv
  simp only [dot, dual, I_inv, mul, hs, h12]; ring

end GacalcProofs.G2
