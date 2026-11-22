import GacalcProofs.G2

/-! # The 2D versor from two vectors — the angle-free technique, shown in 𝒢₂

    The pedagogical warm-up for the 3D versor sandwich (`Rotation3D.lean`): build the rotation versor
    directly from two vectors, with **no angle parameter**, exactly as in the 3D case and in gacalc's
    `versor_from_vectors`. It is not *necessary* in 2D — 𝒢₂ already has the angle-parameterized
    `sandwich_rotor` in `Rotation2D.lean` — but showing the *same* construction here, in the simplest
    algebra, makes the 3D case read as "the same thing."

    **The 2D-vs-3D point:** in 𝒢₂ the plane of rotation is the *whole space*, so there is no
    orthogonal complement and nothing is "left fixed" — the sandwich is purely the rotation. In 𝒢₃
    the identical `R = b*a + |a|*|b|` acts in the `a∧b` plane and *additionally* fixes any component
    along the normal. So 2D isolates "the rotation itself"; 3D adds "and the orthogonal complement is
    untouched."

    Mirrors `Rotation3D.lean`: `bisector`, `versorFromVectors`, and `versor_mul_from_eq_bisector`
    (`R*a = |a|*h`). Terminology: versor, not rotor (un-normalized; applied by `R*v*R⁻¹`). -/
namespace GacalcProofs.G2

open Real

/-- The **half-angle (bisector) vector** of `from`/`to`: `h = |to|*from + |from|*to`. -/
noncomputable def bisector (fromV toV : G2) : G2 :=
  add (smul (magnitude toV) fromV) (smul (magnitude fromV) toV)

/-- The **half-angle versor** taking `from` toward `to`: `R = to*from + |from|*|to|` (scalar +
    bivector), applied by the scale-invariant sandwich `R*v*R⁻¹`. -/
noncomputable def versorFromVectors (fromV toV : G2) : G2 :=
  add (mul toV fromV) (smul (magnitude fromV * magnitude toV) one)

/-- `|a|² = a₁²+a₂²` for a coordinate vector. `magnitude = √normSq`, so this is `normSq_vec`
    under the square root. -/
theorem magnitude_sq_vec (a1 a2 : ℝ) : magnitude (vec a1 a2) ^ 2 = a1 ^ 2 + a2 ^ 2 := by
  rw [magnitude, Real.sq_sqrt (by rw [normSq_vec]; positivity), normSq_vec]

/-- **A vector sandwiched by its own square:** `(b a) a = |a|²*b` (2D twin of
    `Rotation3D.vec_mul_mul_self`): `b(aa) = b|a|²`, since `a a = |a|²`. -/
theorem vec_mul_mul_self {a b : G2} (ha : IsVector a) :
    mul (mul b a) a = smul (normSq a) b := by
  rw [mul_assoc, mul_vec_self ha]
  simp only [mul, scalar, smul]; ext <;> ring

/-- **A vector times itself inside a product:** `a (a b) = |a|²*b` (2D). -/
theorem vec_mul_self_mul {a b : G2} (ha : IsVector a) :
    mul a (mul a b) = smul (normSq a) b := by
  rw [← mul_assoc, mul_vec_self ha, scalar_mul]

/-- **The half-angle versor times the from-vector is the (scaled) bisector**: `R*a = |a|*h`,
    the 2D twin of `Rotation3D.versor_mul_from_eq_bisector`, by the same reason: `R a = (b a) a +
    |a||b| a` and `(b a) a = |a|² b`. -/
theorem versor_mul_from_eq_bisector {fromV toV : G2} (hf : IsVector fromV) :
    mul (versorFromVectors fromV toV) fromV = smul (magnitude fromV) (bisector fromV toV) := by
  rw [versorFromVectors, add_mul, vec_mul_mul_self hf, smul_mul, one_mul, bisector,
    ← magnitude_sq_eq_normSq fromV]
  simp only [smul, add]; ext <;> ring

/-- Companion identity: `b*R = |b|*h` (multiplying the versor on the LEFT by the to-vector),
    the 2D twin of `Rotation3D.from_mul_versor_eq_bisector`. With `R*a = |a|*h` it drives the
    "carries a to b" capstone. -/
theorem from_mul_versor_eq_bisector {fromV toV : G2} (ht : IsVector toV) :
    mul toV (versorFromVectors fromV toV) = smul (magnitude toV) (bisector fromV toV) := by
  rw [versorFromVectors, mul_add, vec_mul_self_mul ht, mul_smul, mul_one, bisector,
    ← magnitude_sq_eq_normSq toV]
  simp only [smul, add]; ext <;> ring

end GacalcProofs.G2
