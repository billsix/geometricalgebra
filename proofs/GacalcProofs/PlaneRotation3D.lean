import GacalcProofs.G3
import GacalcProofs.AlgebraLaws
import GacalcProofs.Sandwich
import GacalcProofs.Projection3D
import GacalcProofs.Trig
import GacalcProofs.Rotor

/-! # The 3D half-angle rotor rotates by its angle, in its plane (`plane_rotation` / `bivector_rotation`)

    gacalc's `transforms.plane_rotation(a, b)(θ)` and `bivector_rotation(B)(θ)` build the half-angle rotor
    `R = cos(θ/2)·1 − sin(θ/2)·i` for the plane's **unit bivector** `i` and apply the reverse sandwich
    `R v R̃`. This module proves what that does to an arbitrary vector `v` in 𝒢₃ (the general plane, not
    only `e₁₂`): split `v` into its in-plane part `v∥ = project_onto i v` and its perpendicular part
    `v⊥ = reject i v`; then

        R v R̃  =  v⊥  +  cos θ · v∥  +  sin θ · (v ⌋ i),

    where `v ⌋ i = inner_vb v i` is `v∥` turned a quarter turn in the plane (for `i = e₁₂`,
    `(x, y, z) ⌋ e₁₂ = (−y, x, 0)`). So the perpendicular part is fixed and the in-plane part rotates by
    the full angle θ, orientation included — the 3D analogue of `Rotation2D.sandwich_rotor`
    (`R v R̃ = rot θ v`), whose `rot θ v = cos θ·v + sin θ·(v e₁₂)` is the `v⊥ = 0` case. Corollaries:
    the student-facing `cos_between (R v R̃) v = cos θ` for a nonzero in-plane `v`, and the plane's normal
    is fixed.

    Proof shape: `planeRotor` is a rotor (`IsRotor`, so the whole `Rotor.lean` layer applies: unit,
    isometry, `R⁻¹ = R̃`); the main identity is a coordinate leaf — after unfolding, each vector component
    is a polynomial identity modulo the two relations `cos²(θ/2) + sin²(θ/2) = 1` and `|i|² = 1`, closed by
    `linear_combination` with cofactors computed offline (sympy `reduced` over gacalc's own product; record in
    `tasks/archive/2026/10/05/lean-rotor-3d-angle-theorem.md`). -/
namespace GacalcProofs.G3

open Real

/-- gacalc's half-angle rotor for angle θ in the plane of the unit bivector `i`:
    `R = cos(θ/2)·1 − sin(θ/2)·i` — what `transforms._unit_bivector_rotor_factory`'s `rotor_for` builds
    (`Rotation2D.rotor θ` is the `i = e₁₂` case). -/
noncomputable def planeRotor (θ : ℝ) (i : G3) : G3 :=
  add (smul (cos (θ / 2)) one) (smul (-(sin (θ / 2))) i)

/-- `planeRotor θ i` is even for a bivector `i`. -/
theorem isEvenVersor_planeRotor (θ : ℝ) {i : G3} (hi : IsBivector i) :
    IsEvenVersor (planeRotor θ i) := by
  obtain ⟨_, hi1, hi2, hi3, hi123⟩ := hi
  refine ⟨?_, ?_, ?_, ?_⟩ <;> simp only [planeRotor, add, smul, one, hi1, hi2, hi3, hi123] <;> ring

/-- `|i|² = 1` read off the bivector's three coordinates. -/
theorem sum_sq_of_unit_bivector {i : G3} (hi : IsBivector i) (hu : normSq i = 1) :
    i.c12 ^ 2 + i.c13 ^ 2 + i.c23 ^ 2 = 1 := by
  obtain ⟨his, hi1, hi2, hi3, hi123⟩ := hi
  have h := hu
  rw [normSq_eq_sum_sq, his, hi1, hi2, hi3, hi123] at h
  linear_combination h

/-- `|planeRotor θ i|² = cos²(θ/2) + sin²(θ/2)·|i|² = 1` for a unit bivector `i`. -/
theorem normSq_planeRotor (θ : ℝ) {i : G3} (hi : IsBivector i) (hu : normSq i = 1) :
    normSq (planeRotor θ i) = 1 := by
  have hpqr := sum_sq_of_unit_bivector hi hu
  obtain ⟨his, hi1, hi2, hi3, hi123⟩ := hi
  rw [normSq_eq_sum_sq]
  simp only [planeRotor, add, smul, one, his, hi1, hi2, hi3, hi123]
  linear_combination Real.cos_sq_add_sin_sq (θ / 2) + sin (θ / 2) ^ 2 * hpqr

/-- **`planeRotor θ i` is a rotor** (even and unit) — so `R⁻¹ = R̃`, the sandwich is an isometry, and the
    reverse sandwich equals gacalc's inverse sandwich (`Rotor.lean`). -/
theorem isRotor_planeRotor (θ : ℝ) {i : G3} (hi : IsBivector i) (hu : normSq i = 1) :
    IsRotor (planeRotor θ i) :=
  ⟨isEvenVersor_planeRotor θ hi, normSq_planeRotor θ hi hu⟩

/-- **The 3D rotor angle theorem (the leaf):** for a unit bivector `i` and a vector `v`,
    `R v R̃ = v⊥ + cos θ·v∥ + sin θ·(v ⌋ i)` with `R = planeRotor θ i`, `v∥ = project_onto i v`,
    `v⊥ = reject i v` — the perpendicular part is fixed, the in-plane part is rotated by θ (orientation
    included: `v ⌋ i` is `v∥` turned +90° in the plane). Coordinate leaf: after unfolding (`|i|² = 1`
    makes `i⁻¹ = ĩ`), each vector component is a polynomial identity modulo `cos²(θ/2) + sin²(θ/2) = 1`
    and `|i|² = 1`, with the double-angle `cos θ = cos²(θ/2) − sin²(θ/2)`, `sin θ = 2 sin(θ/2) cos(θ/2)`
    substituted first; the scalar/bivector/trivector components vanish identically. -/
theorem rotorSandwich_planeRotor (θ : ℝ) {i v : G3} (hi : IsBivector i) (hu : normSq i = 1)
    (hv : IsVector v) :
    rotorSandwich (planeRotor θ i) v
      = add (reject i v) (add (smul (cos θ) (project_onto i v)) (smul (sin θ) (inner_vb v i))) := by
  have hc : cos θ = cos (θ / 2) ^ 2 - sin (θ / 2) ^ 2 := by
    have h2 := cos_two_mul (θ / 2)
    rw [show (2 : ℝ) * (θ / 2) = θ by ring] at h2
    linear_combination h2 + Real.sin_sq_add_cos_sq (θ / 2)
  have hs : sin θ = 2 * sin (θ / 2) * cos (θ / 2) := by
    have h2 := sin_two_mul (θ / 2)
    rw [show (2 : ℝ) * (θ / 2) = θ by ring] at h2
    exact h2
  have hcs : cos (θ / 2) ^ 2 + sin (θ / 2) ^ 2 = 1 := Real.cos_sq_add_sin_sq (θ / 2)
  have hpqr := sum_sq_of_unit_bivector hi hu
  obtain ⟨his, hi1, hi2, hi3, hi123⟩ := hi
  obtain ⟨hvs, hv12, hv13, hv23, hv123⟩ := hv
  simp only [rotorSandwich, planeRotor, reject, project_onto, inverse, hu, div_one, hc, hs]
  simp only [mul, add, smul, reverse, wedge, inner_vb, vec, one, his, hi1, hi2, hi3, hi123, hvs, hv12,
    hv13, hv23, hv123]
  ext
  · ring
  · linear_combination
      (-i.c12 ^ 2 * v.c1 + i.c12 * i.c23 * v.c3 - i.c13 ^ 2 * v.c1 - i.c13 * i.c23 * v.c2 + v.c1) * hcs
        + (v.c1 * (sin (θ / 2) - 1) * (sin (θ / 2) + 1)) * hpqr
  · linear_combination
      (-i.c12 ^ 2 * v.c2 - i.c12 * i.c13 * v.c3 - i.c13 * i.c23 * v.c1 - i.c23 ^ 2 * v.c2 + v.c2) * hcs
        + (v.c2 * (sin (θ / 2) - 1) * (sin (θ / 2) + 1)) * hpqr
  · linear_combination
      (-i.c12 * i.c13 * v.c2 + i.c12 * i.c23 * v.c1 - i.c13 ^ 2 * v.c3 - i.c23 ^ 2 * v.c3 + v.c3) * hcs
        + (v.c3 * (sin (θ / 2) - 1) * (sin (θ / 2) + 1)) * hpqr
  · ring
  · ring
  · ring
  · ring

/-- **Student-facing corollary:** for a nonzero vector `v` lying IN the plane (`reject i v = 0`), the
    cosine of the angle between `v` and its image `R v R̃` is `cos θ` — the rotor rotates by θ. From the
    leaf: `v⊥ = 0` and `v∥ = v`, the sandwich is an isometry (`|R v R̃| = |v|`), and `(v ⌋ i) · v = 0`
    (the quarter-turn is perpendicular to `v`). -/
theorem cos_between_rotorSandwich_planeRotor (θ : ℝ) {i v : G3} (hi : IsBivector i) (hu : normSq i = 1)
    (hv : IsVector v) (hin : reject i v = zero) (hvn : normSq v ≠ 0) :
    cos_between (rotorSandwich (planeRotor θ i) v) v = cos θ := by
  have hun : normSq i ≠ 0 := by rw [hu]; exact one_ne_zero
  have hproj : project_onto i v = v := by
    have h := project_add_reject hi hun hv
    rw [hin] at h
    have hz : add (project_onto i v) zero = project_onto i v := by
      simp only [add, zero]; ext <;> ring
    rwa [hz] at h
  have hmag : magnitude v * magnitude v = normSq v := by rw [← sq, magnitude_sq_eq_normSq]
  rw [cos_between, rotorSandwich_preserves_magnitude (isRotor_planeRotor θ hi hu), hmag,
    rotorSandwich_planeRotor θ hi hu hv, hin, hproj, div_eq_iff hvn]
  obtain ⟨his, hi1, hi2, hi3, hi123⟩ := hi
  obtain ⟨hvs, hv12, hv13, hv23, hv123⟩ := hv
  simp only [dot, normSq, add, zero, smul, inner_vb, mul, vec, reverse, his, hi1, hi2, hi3, hi123, hvs,
    hv12, hv13, hv23, hv123]
  ring

/-- **The plane's normal is fixed:** any multiple of the normal `(i₂₃, −i₁₃, i₁₂)` of the unit bivector
    `i` (the vector that commutes with `i`) is unchanged by the rotor sandwich — the "⊥ part is fixed"
    half of the angle theorem, stated on the normal itself. -/
theorem rotorSandwich_planeRotor_fixes_normal (θ k : ℝ) {i : G3} (hi : IsBivector i)
    (hu : normSq i = 1) :
    rotorSandwich (planeRotor θ i) (smul k (vec i.c23 (-i.c13) i.c12))
      = smul k (vec i.c23 (-i.c13) i.c12) := by
  have hcs : cos (θ / 2) ^ 2 + sin (θ / 2) ^ 2 = 1 := Real.cos_sq_add_sin_sq (θ / 2)
  have hpqr := sum_sq_of_unit_bivector hi hu
  obtain ⟨his, hi1, hi2, hi3, hi123⟩ := hi
  simp only [rotorSandwich, planeRotor, mul, add, smul, reverse, vec, one, his, hi1, hi2, hi3, hi123]
  ext
  · ring
  · linear_combination (k * i.c23) * hcs + (k * i.c23 * sin (θ / 2) ^ 2) * hpqr
  · linear_combination (-(k * i.c13)) * hcs + (-(k * i.c13) * sin (θ / 2) ^ 2) * hpqr
  · linear_combination (k * i.c12) * hcs + (k * i.c12 * sin (θ / 2) ^ 2) * hpqr
  · ring
  · ring
  · ring
  · ring

end GacalcProofs.G3
