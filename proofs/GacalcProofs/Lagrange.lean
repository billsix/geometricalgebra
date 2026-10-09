import Mathlib

/-! # Lagrange's identity (squared form)

    ‖a‖²‖b‖² = (a·b)² + ‖a∧b‖²   (equivalently ‖a∧b‖² = ‖a‖²‖b‖² − (a·b)²).

    In coordinates the wedge magnitude is the sum of the squared 2×2 minors; each
    identity below is that statement, proved by `ring`. This is the identity the
    book uses to derive sin/cos (`notebooks/displayg2.py`). See
    <https://en.wikipedia.org/wiki/Lagrange%27s_identity>. General reference:
    Mathlib's `inner_mul_le_norm_mul_norm` (Cauchy–Schwarz) is the ≤ half. -/
namespace GacalcProofs

/-- Lagrange's identity in 2D (a∧b is the single minor a₁*b₂ − a₂*b₁). -/
theorem lagrange_2d (a1 a2 b1 b2 : ℝ) :
    (a1 ^ 2 + a2 ^ 2) * (b1 ^ 2 + b2 ^ 2)
      = (a1 * b1 + a2 * b2) ^ 2 + (a1 * b2 - a2 * b1) ^ 2 := by
  ring

/-- Lagrange's identity in 3D (‖a∧b‖² is the sum of the three squared 2×2 minors;
    in 3D these are the components of a×b). -/
theorem lagrange_3d (a1 a2 a3 b1 b2 b3 : ℝ) :
    (a1 ^ 2 + a2 ^ 2 + a3 ^ 2) * (b1 ^ 2 + b2 ^ 2 + b3 ^ 2)
      = (a1 * b1 + a2 * b2 + a3 * b3) ^ 2
        + ((a1 * b2 - a2 * b1) ^ 2 + (a2 * b3 - a3 * b2) ^ 2 + (a3 * b1 - a1 * b3) ^ 2) := by
  ring

end GacalcProofs
