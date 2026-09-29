import GacalcProofs.G2

/-! # The 2D versor from two vectors — the angle-free technique, shown in 𝒢₂

    The pedagogical warm-up for the 3D versor sandwich (`Rotation3D.lean`): build the rotation versor
    directly from two vectors, with **no angle parameter**, exactly as in the 3D case and in gacalc's
    `versor_from_vectors`. It is not *necessary* in 2D — 𝒢₂ already has the angle-parameterized
    `sandwich_versor` in `Rotation.lean` — but showing the *same* construction here, in the simplest
    algebra, makes the 3D case read as "the same thing."

    **The 2D-vs-3D point:** in 𝒢₂ the plane of rotation is the *whole space*, so there is no
    orthogonal complement and nothing is "left fixed" — the sandwich is purely the rotation. In 𝒢₃
    the identical `R = b·a + |a||b|` acts in the `a∧b` plane and *additionally* fixes any component
    along the normal. So 2D isolates "the rotation itself"; 3D adds "and the orthogonal complement is
    untouched."

    Mirrors `Rotation3D.lean`: `bisector`, `versorFromVectors`, and `versor_mul_from_eq_bisector`
    (`R·a = |a|·h`). Terminology: versor, not rotor (un-normalized; applied by `R v R⁻¹`). -/
namespace GacalcProofs.G2

open Real

/-- The scalar product `a·b = ⟨a b⟩₀` in 𝒢₂ (scalar part of the geometric product; for vectors the
    Euclidean dot `a₁b₁ + a₂b₂`). -/
noncomputable def dot (a b : G2) : ℝ := (mul a b).s

/-- `dot` distributes over subtraction on the left (it is bilinear) — the 𝒢₂ twin of
    `G3.dot_sub_left`, letting projection proofs be structural rather than coordinate-based. -/
theorem dot_sub_left (u w v : G2) : dot (sub u w) v = dot u v - dot w v := by
  simp only [dot, mul, sub]; ring

/-- `dot` pulls out a scalar on the left. -/
theorem dot_smul_left (k : ℝ) (u v : G2) : dot (smul k u) v = k * dot u v := by
  simp only [dot, mul, smul]; ring

/-- The magnitude `|a| = √(a·a)`. -/
noncomputable def mag (a : G2) : ℝ := Real.sqrt (dot a a)

/-- The **half-angle (bisector) vector** of `from`/`to`: `h = |to|·from + |from|·to`. -/
noncomputable def bisector (fromV toV : G2) : G2 :=
  add (smul (mag toV) fromV) (smul (mag fromV) toV)

/-- The **half-angle versor** taking `from` toward `to`: `R = to·from + |from||to|` (scalar +
    bivector), applied by the scale-invariant sandwich `R v R⁻¹`. -/
noncomputable def versorFromVectors (fromV toV : G2) : G2 :=
  add (mul toV fromV) (smul (mag fromV * mag toV) one)

/-- `|a|² = a·a` for a vector. -/
theorem mag_sq_vec (a1 a2 : ℝ) : mag (vec a1 a2) ^ 2 = a1 ^ 2 + a2 ^ 2 := by
  have hd : dot (vec a1 a2) (vec a1 a2) = a1 ^ 2 + a2 ^ 2 := by
    simp only [dot, mul, vec]; ring
  rw [mag, hd, Real.sq_sqrt (by positivity)]

/-- **The half-angle versor times the from-vector is the (scaled) bisector**: `R · a = |a| · h`,
    the 2D twin of `Rotation3D.versor_mul_from_eq_bisector`. Angle-free; the only non-`ring` step is
    `|a|² = a·a`. -/
theorem versor_mul_from_eq_bisector (a1 a2 b1 b2 : ℝ) :
    mul (versorFromVectors (vec a1 a2) (vec b1 b2)) (vec a1 a2)
      = smul (mag (vec a1 a2)) (bisector (vec a1 a2) (vec b1 b2)) := by
  simp only [versorFromVectors, bisector]
  set sa := mag (vec a1 a2)
  set sb := mag (vec b1 b2)
  have hsa : sa ^ 2 = a1 ^ 2 + a2 ^ 2 := mag_sq_vec a1 a2
  clear_value sa sb
  simp only [mul, add, smul, one, vec]
  ext
  · ring
  · linear_combination -b1 * hsa
  · linear_combination -b2 * hsa
  · ring

/-- Companion identity: `b · R = |b| · h` (multiplying the versor on the LEFT by the to-vector),
    the 2D twin of `Rotation3D.from_mul_versor_eq_bisector`. With `R·a = |a|·h` it drives the
    "carries a to b" capstone. -/
theorem from_mul_versor_eq_bisector (a1 a2 b1 b2 : ℝ) :
    mul (vec b1 b2) (versorFromVectors (vec a1 a2) (vec b1 b2))
      = smul (mag (vec b1 b2)) (bisector (vec a1 a2) (vec b1 b2)) := by
  simp only [versorFromVectors, bisector]
  set sa := mag (vec a1 a2)
  set sb := mag (vec b1 b2)
  have hsb : sb ^ 2 = b1 ^ 2 + b2 ^ 2 := mag_sq_vec b1 b2
  clear_value sa sb
  simp only [mul, add, smul, one, vec]
  ext
  · ring
  · linear_combination -a1 * hsb
  · linear_combination -a2 * hsb
  · ring

end GacalcProofs.G2
