import GacalcProofs.G2
import GacalcProofs.G3
import GacalcProofs.AlgebraLaws
import GacalcProofs.Sandwich
import GacalcProofs.ProjectionRotation2D
import GacalcProofs.ProjectionRotation3D
import GacalcProofs.Rotation2D

/-! # Rotors from vectors: the versor chain, re-done with the reverse sandwich

    The versor chain is proven elsewhere: `projRotation f t v = sandwich (versorFromVectors f t) v`
    (the inverse sandwich `R * v * R⁻¹` of the un-normalized `R = b * a + |a| * |b|`), it carries `a` to `b`, and
    it is an isometry. This module proves **the same chain for rotors with the reverse sandwich
    `R * v * R̃`** — without re-proving anything about projections. The whole thing rests on one algebraic
    bridge (`rotorSandwich_normalize`; the `√` facts `normSq_nonneg`/`magnitude_sq_eq_normSq` live in `G2.lean`/`G3.lean`):

        (R/|R|) * v * (R/|R|)~  =  R * v * R̃ / |R|²  =  R * v * R⁻¹        for every R,

    so "the versor sandwich, divided by the magnitudes, is the rotor sandwich" (the maintainer's
    framing, 2026-10-05). Then `rotorFromVectors a b := normalize (versorFromVectors a b)` is a rotor
    (`IsRotor`), and each versor theorem becomes a rotor theorem by rewriting through the bridge.
    **Lagrange's identity** gives the versor's magnitude in closed form,
    `|versorFromVectors a b|² = 2 * |a| * |b| * (|a| * |b| + a·b)`, so the chain's `normSq R ≠ 0` guard reads
    "nonzero and not antiparallel". Both grades; a 2D coda ties the from-vectors rotor of two unit
    directions to the half-angle `rotor θ` and hence to `rot θ`. -/
namespace GacalcProofs

namespace G2

/-! ### `normalize` for any multivector, and normalizing a versor gives a rotor -/

/-- `normalize A = A / |A|` — gacalc's `MultiVectorBase.normalize`, for any multivector (the vector case
    is `normalizeVec`). -/
noncomputable def normalize (a : G2) : G2 := smul (1 / magnitude a) a

/-- A normalized nonzero multivector has unit squared magnitude. -/
theorem normSq_normalize {a : G2} (h : normSq a ≠ 0) : normSq (normalize a) = 1 := by
  rw [normalize, normSq_smul, div_pow, one_pow, magnitude_sq_eq_normSq, one_div, inv_mul_cancel₀ h]

/-- Scaling keeps a versor even. -/
theorem isEvenVersor_smul (k : ℝ) {R : G2} (hR : IsEvenVersor R) : IsEvenVersor (smul k R) := by
  obtain ⟨h0, h1⟩ := hR
  exact ⟨by simp only [smul, h0, mul_zero], by simp only [smul, h1, mul_zero]⟩

/-- **Normalizing a nonzero versor gives a rotor.** -/
theorem isRotor_normalize {R : G2} (hR : IsEvenVersor R) (h : normSq R ≠ 0) : IsRotor (normalize R) :=
  ⟨isEvenVersor_smul _ hR, normSq_normalize h⟩

/-! ### The rotor sandwich `R * v * R̃`, and the bridge to the versor sandwich `R * v * R⁻¹` -/

/-- The **rotor sandwich** `R * v * R̃` — the textbook rotation by a rotor (reverse, no division). -/
noncomputable def rotorSandwich (R v : G2) : G2 := mul (mul R v) (reverse R)

/-- For a rotor the versor sandwich `R * v * R⁻¹` IS the rotor sandwich (`R⁻¹ = R̃`). -/
theorem sandwich_eq_rotorSandwich_of_isRotor {R : G2} (hR : IsRotor R) (v : G2) :
    sandwich R v = rotorSandwich R v := sandwich_eq_reverse_sandwich_of_isRotor hR v

/-- **The bridge:** the rotor sandwich of the *normalized* versor equals the inverse sandwich of the
    un-normalized one, for EVERY `R` and `v`: `(R/|R|) * v * (R/|R|)~ = R * v * R̃ / |R|² = R * v * R⁻¹`. This is
    "the versor sandwich implementation, divided by the magnitudes, is the rotor sandwich
    implementation" — so every theorem about `sandwich (versorFromVectors a b)` transfers to
    `rotorSandwich (rotorFromVectors a b)` by one rewrite. Structural: pull the two scalars `1/|R|` out
    of the product (`smul_mul`/`mul_smul`), merge them (`smul_smul`), and use `(1/|R|)² = 1/|R|²`. -/
theorem rotorSandwich_normalize (R v : G2) : rotorSandwich (normalize R) v = sandwich R v := by
  have hk : (1 / magnitude R) * (1 / magnitude R) = 1 / normSq R := by
    rw [← magnitude_sq_eq_normSq R]; ring
  simp only [rotorSandwich, normalize, sandwich, inverse]
  rw [reverse_smul, GacalcProofs.G2.smul_mul (1 / magnitude R) R v,
    GacalcProofs.G2.smul_mul (1 / magnitude R) (mul R v) (smul (1 / magnitude R) (reverse R)),
    GacalcProofs.G2.mul_smul (1 / magnitude R) (mul R v) (reverse R),
    GacalcProofs.G2.smul_smul, hk, GacalcProofs.G2.mul_smul (1 / normSq R) (mul R v) (reverse R)]

/-- The rotor sandwich preserves the dot product (for a rotor) — via the bridge to the versor result. -/
theorem rotorSandwich_preserves_dot {R : G2} (hR : IsRotor R) {u v : G2} :
    dot (rotorSandwich R u) (rotorSandwich R v) = dot u v := by
  rw [← sandwich_eq_rotorSandwich_of_isRotor hR, ← sandwich_eq_rotorSandwich_of_isRotor hR,
    sandwich_preserves_dot hR.1 (normSq_ne_zero_of_isRotor hR)]

/-- The rotor sandwich preserves the squared magnitude (for a rotor). -/
theorem rotorSandwich_preserves_normSq {R : G2} (hR : IsRotor R) {v : G2} :
    normSq (rotorSandwich R v) = normSq v := by
  rw [← sandwich_eq_rotorSandwich_of_isRotor hR, sandwich_preserves_normSq hR.1 (normSq_ne_zero_of_isRotor hR)]

/-- The rotor sandwich preserves the magnitude (for a rotor). -/
theorem rotorSandwich_preserves_magnitude {R : G2} (hR : IsRotor R) {v : G2} :
    magnitude (rotorSandwich R v) = magnitude v := by
  rw [← sandwich_eq_rotorSandwich_of_isRotor hR, magnitude_sandwich hR.1 (normSq_ne_zero_of_isRotor hR)]

/-! ### The rotor from two vectors: the from-vectors versor, normalized -/

/-- The from-vectors versor `b * a + |a| * |b|` is even. -/
theorem isEvenVersor_versorFromVectors {a b : G2} (ha : IsVector a) (hb : IsVector b) :
    IsEvenVersor (versorFromVectors a b) := by
  obtain ⟨ha_s, ha_c12⟩ := ha
  obtain ⟨hb_s, hb_c12⟩ := hb
  refine ⟨?_, ?_⟩ <;>
    simp only [versorFromVectors, add, mul, smul, one, ha_s, ha_c12, hb_s, hb_c12] <;> ring

/-- **The rotor from two vectors**: `versorFromVectors a b`, normalized to unit magnitude — gacalc's
    `versor_from_vectors(a, b).normalize()`. -/
noncomputable def rotorFromVectors (a b : G2) : G2 := normalize (versorFromVectors a b)

/-- It is a rotor (even and unit) whenever the versor is nonzero. -/
theorem isRotor_rotorFromVectors {a b : G2} (ha : IsVector a) (hb : IsVector b)
    (hr : normSq (versorFromVectors a b) ≠ 0) : IsRotor (rotorFromVectors a b) :=
  isRotor_normalize (isEvenVersor_versorFromVectors ha hb) hr

/-- **The rotor sandwich from `a` to `b` IS the versor sandwich from `a` to `b`** (the bridge,
    specialized): `R̂ v R̂̃ = R * v * R⁻¹` with `R = versorFromVectors a b`, `R̂ = R/|R|`. -/
theorem rotorSandwich_rotorFromVectors (a b v : G2) :
    rotorSandwich (rotorFromVectors a b) v = sandwich (versorFromVectors a b) v :=
  rotorSandwich_normalize _ v

/-- **The rotor chain closes on the projection rotation:** `R̂ v R̂̃ = projRotation f t v` — the
    reverse-sandwich rotor rotation IS `transforms.projection_rotation`, through the versor result
    `projRotation_eq_sandwich`. -/
theorem rotorSandwich_rotorFromVectors_eq_projRotation {f t v : G2} (hf : IsVector f) (ht : IsVector t)
    (hv : IsVector v) (hfn : normSq f ≠ 0) (htn : normSq t ≠ 0)
    (hr : normSq (versorFromVectors f t) ≠ 0) :
    rotorSandwich (rotorFromVectors f t) v = projRotation f t v := by
  rw [rotorSandwich_rotorFromVectors, projRotation_eq_sandwich hf ht hv hfn htn hr]

/-- **The rotor from `a` to `b` carries `a` to `b`** (scaled to `a`'s length): `R̂ a R̂̃ = (|a|/|b|) * b`. -/
theorem rotorSandwich_rotorFromVectors_carries_from_to {a b : G2} (ha : IsVector a) (hb : IsVector b)
    (hbn : magnitude b ≠ 0) (hr : normSq (versorFromVectors a b) ≠ 0) :
    rotorSandwich (rotorFromVectors a b) a = smul (magnitude a / magnitude b) b := by
  rw [rotorSandwich_rotorFromVectors, sandwich_carries_from_to ha hb hbn hr]

/-! ### Lagrange: the from-vectors versor's magnitude in closed form -/

/-- **`|versorFromVectors a b|² = 2 * |a| * |b| * (|a| * |b| + a·b)`** — by Lagrange's identity (reference: `Lagrange.lean`)
    `(a·b)² + |a∧b|² = |a|² * |b|²` (`Trig.lagrange_property`, a `ring` identity in coordinates): the
    versor is `(|a| * |b| + a·b) + b∧a`, so its squared magnitude is `(|a| * |b| + a·b)² + |a∧b|²`, and
    Lagrange collapses `(a·b)² + |a∧b|²` to `|a|² * |b|²`. Hence the versor vanishes exactly when `a` and
    `b` are antiparallel (`a·b = −|a| * |b|`) or one is zero — the normalization is well-defined otherwise.
    (This is the identity the earlier Python-side attempt to normalize the versor was missing.) -/
theorem normSq_versorFromVectors {a b : G2} (ha : IsVector a) (hb : IsVector b) :
    normSq (versorFromVectors a b)
      = 2 * magnitude a * magnitude b * (magnitude a * magnitude b + dot a b) := by
  obtain ⟨ha_s, ha_c12⟩ := ha
  obtain ⟨hb_s, hb_c12⟩ := hb
  have hA : magnitude a ^ 2 = a.c1 ^ 2 + a.c2 ^ 2 := by
    rw [magnitude_sq_eq_normSq, normSq_eq_sum_sq, ha_s, ha_c12]; ring
  have hB : magnitude b ^ 2 = b.c1 ^ 2 + b.c2 ^ 2 := by
    rw [magnitude_sq_eq_normSq, normSq_eq_sum_sq, hb_s, hb_c12]; ring
  simp only [normSq, versorFromVectors, add, mul, smul, one, reverse, dot, ha_s, ha_c12, hb_s, hb_c12]
  linear_combination (-(magnitude b ^ 2)) * hA + (-(a.c1 ^ 2 + a.c2 ^ 2)) * hB

/-- The from-vectors versor is nonzero when `a`, `b` are nonzero and not antiparallel — the geometric
    reading of the `normSq (versorFromVectors a b) ≠ 0` guard carried by the whole chain. -/
theorem normSq_versorFromVectors_ne_zero {a b : G2} (ha : IsVector a) (hb : IsVector b)
    (hna : normSq a ≠ 0) (hnb : normSq b ≠ 0) (h : magnitude a * magnitude b + dot a b ≠ 0) :
    normSq (versorFromVectors a b) ≠ 0 := by
  rw [normSq_versorFromVectors ha hb]
  exact mul_ne_zero (mul_ne_zero (mul_ne_zero two_ne_zero (magnitude_ne_zero_of_normSq_ne_zero hna))
    (magnitude_ne_zero_of_normSq_ne_zero hnb)) h

end G2

namespace G3

/-! ### `normalize` for any multivector, and normalizing a versor gives a rotor -/

/-- `normalize A = A / |A|` — gacalc's `MultiVectorBase.normalize`, for any multivector (the vector case
    is `normalizeVec`). -/
noncomputable def normalize (a : G3) : G3 := smul (1 / magnitude a) a

/-- A normalized nonzero multivector has unit squared magnitude. -/
theorem normSq_normalize {a : G3} (h : normSq a ≠ 0) : normSq (normalize a) = 1 := by
  rw [normalize, normSq_smul, div_pow, one_pow, magnitude_sq_eq_normSq, one_div, inv_mul_cancel₀ h]

/-- Scaling keeps a versor even. -/
theorem isEvenVersor_smul (k : ℝ) {R : G3} (hR : IsEvenVersor R) : IsEvenVersor (smul k R) := by
  obtain ⟨h0, h1, h2, h3⟩ := hR
  exact ⟨by simp only [smul, h0, mul_zero], by simp only [smul, h1, mul_zero], by simp only [smul, h2, mul_zero], by simp only [smul, h3, mul_zero]⟩

/-- **Normalizing a nonzero versor gives a rotor.** -/
theorem isRotor_normalize {R : G3} (hR : IsEvenVersor R) (h : normSq R ≠ 0) : IsRotor (normalize R) :=
  ⟨isEvenVersor_smul _ hR, normSq_normalize h⟩

/-! ### The rotor sandwich `R * v * R̃`, and the bridge to the versor sandwich `R * v * R⁻¹` -/

/-- The **rotor sandwich** `R * v * R̃` — the textbook rotation by a rotor (reverse, no division). -/
noncomputable def rotorSandwich (R v : G3) : G3 := mul (mul R v) (reverse R)

/-- For a rotor the versor sandwich `R * v * R⁻¹` IS the rotor sandwich (`R⁻¹ = R̃`). -/
theorem sandwich_eq_rotorSandwich_of_isRotor {R : G3} (hR : IsRotor R) (v : G3) :
    sandwich R v = rotorSandwich R v := sandwich_eq_reverse_sandwich_of_isRotor hR v

/-- **The bridge:** the rotor sandwich of the *normalized* versor equals the inverse sandwich of the
    un-normalized one, for EVERY `R` and `v`: `(R/|R|) * v * (R/|R|)~ = R * v * R̃ / |R|² = R * v * R⁻¹`. This is
    "the versor sandwich implementation, divided by the magnitudes, is the rotor sandwich
    implementation" — so every theorem about `sandwich (versorFromVectors a b)` transfers to
    `rotorSandwich (rotorFromVectors a b)` by one rewrite. Structural: pull the two scalars `1/|R|` out
    of the product (`smul_mul`/`mul_smul`), merge them (`smul_smul`), and use `(1/|R|)² = 1/|R|²`. -/
theorem rotorSandwich_normalize (R v : G3) : rotorSandwich (normalize R) v = sandwich R v := by
  have hk : (1 / magnitude R) * (1 / magnitude R) = 1 / normSq R := by
    rw [← magnitude_sq_eq_normSq R]; ring
  simp only [rotorSandwich, normalize, sandwich, inverse]
  rw [reverse_smul, GacalcProofs.G3.smul_mul (1 / magnitude R) R v,
    GacalcProofs.G3.smul_mul (1 / magnitude R) (mul R v) (smul (1 / magnitude R) (reverse R)),
    GacalcProofs.G3.mul_smul (1 / magnitude R) (mul R v) (reverse R),
    GacalcProofs.G3.smul_smul, hk, GacalcProofs.G3.mul_smul (1 / normSq R) (mul R v) (reverse R)]

/-- The rotor sandwich preserves the dot product (for a rotor) — via the bridge to the versor result. -/
theorem rotorSandwich_preserves_dot {R : G3} (hR : IsRotor R) {u v : G3} :
    dot (rotorSandwich R u) (rotorSandwich R v) = dot u v := by
  rw [← sandwich_eq_rotorSandwich_of_isRotor hR, ← sandwich_eq_rotorSandwich_of_isRotor hR,
    sandwich_preserves_dot hR.1 (normSq_ne_zero_of_isRotor hR)]

/-- The rotor sandwich preserves the squared magnitude (for a rotor). -/
theorem rotorSandwich_preserves_normSq {R : G3} (hR : IsRotor R) {v : G3} :
    normSq (rotorSandwich R v) = normSq v := by
  rw [← sandwich_eq_rotorSandwich_of_isRotor hR, sandwich_preserves_normSq hR.1 (normSq_ne_zero_of_isRotor hR)]

/-- The rotor sandwich preserves the magnitude (for a rotor). -/
theorem rotorSandwich_preserves_magnitude {R : G3} (hR : IsRotor R) {v : G3} :
    magnitude (rotorSandwich R v) = magnitude v := by
  rw [← sandwich_eq_rotorSandwich_of_isRotor hR, magnitude_sandwich hR.1 (normSq_ne_zero_of_isRotor hR)]

/-! ### The rotor from two vectors: the from-vectors versor, normalized -/

/-- The from-vectors versor `b * a + |a| * |b|` is even. -/
theorem isEvenVersor_versorFromVectors {a b : G3} (ha : IsVector a) (hb : IsVector b) :
    IsEvenVersor (versorFromVectors a b) := by
  obtain ⟨ha_s, ha_c12, ha_c13, ha_c23, ha_c123⟩ := ha
  obtain ⟨hb_s, hb_c12, hb_c13, hb_c23, hb_c123⟩ := hb
  refine ⟨?_, ?_, ?_, ?_⟩ <;>
    simp only [versorFromVectors, add, mul, smul, one, ha_s, ha_c12, ha_c13, ha_c23, ha_c123, hb_s, hb_c12, hb_c13, hb_c23, hb_c123] <;> ring

/-- **The rotor from two vectors**: `versorFromVectors a b`, normalized to unit magnitude — gacalc's
    `versor_from_vectors(a, b).normalize()`. -/
noncomputable def rotorFromVectors (a b : G3) : G3 := normalize (versorFromVectors a b)

/-- It is a rotor (even and unit) whenever the versor is nonzero. -/
theorem isRotor_rotorFromVectors {a b : G3} (ha : IsVector a) (hb : IsVector b)
    (hr : normSq (versorFromVectors a b) ≠ 0) : IsRotor (rotorFromVectors a b) :=
  isRotor_normalize (isEvenVersor_versorFromVectors ha hb) hr

/-- **The rotor sandwich from `a` to `b` IS the versor sandwich from `a` to `b`** (the bridge,
    specialized): `R̂ v R̂̃ = R * v * R⁻¹` with `R = versorFromVectors a b`, `R̂ = R/|R|`. -/
theorem rotorSandwich_rotorFromVectors (a b v : G3) :
    rotorSandwich (rotorFromVectors a b) v = sandwich (versorFromVectors a b) v :=
  rotorSandwich_normalize _ v

/-- **The rotor chain closes on the projection rotation:** `R̂ v R̂̃ = projRotation f t v` — the
    reverse-sandwich rotor rotation IS `transforms.projection_rotation`, through the versor result
    `projRotation_eq_sandwich`. -/
theorem rotorSandwich_rotorFromVectors_eq_projRotation {f t v : G3} (hf : IsVector f) (ht : IsVector t)
    (hv : IsVector v) (hfn : normSq f ≠ 0) (htn : normSq t ≠ 0)
    (hpn : normSq (wedge f t) ≠ 0)
    (hr : normSq (versorFromVectors f t) ≠ 0) :
    rotorSandwich (rotorFromVectors f t) v = projRotation f t v := by
  rw [rotorSandwich_rotorFromVectors, projRotation_eq_sandwich hf ht hv hfn htn hpn hr]

/-- **The rotor from `a` to `b` carries `a` to `b`** (scaled to `a`'s length): `R̂ a R̂̃ = (|a|/|b|) * b`. -/
theorem rotorSandwich_rotorFromVectors_carries_from_to {a b : G3} (ha : IsVector a) (hb : IsVector b)
    (hbn : magnitude b ≠ 0) (hr : normSq (versorFromVectors a b) ≠ 0) :
    rotorSandwich (rotorFromVectors a b) a = smul (magnitude a / magnitude b) b := by
  rw [rotorSandwich_rotorFromVectors, sandwich_carries_from_to ha hb hbn hr]

/-! ### Lagrange: the from-vectors versor's magnitude in closed form -/

/-- **`|versorFromVectors a b|² = 2 * |a| * |b| * (|a| * |b| + a·b)`** — by Lagrange's identity (reference: `Lagrange.lean`)
    `(a·b)² + |a∧b|² = |a|² * |b|²` (`Trig.lagrange_property`, a `ring` identity in coordinates): the
    versor is `(|a| * |b| + a·b) + b∧a`, so its squared magnitude is `(|a| * |b| + a·b)² + |a∧b|²`, and
    Lagrange collapses `(a·b)² + |a∧b|²` to `|a|² * |b|²`. Hence the versor vanishes exactly when `a` and
    `b` are antiparallel (`a·b = −|a| * |b|`) or one is zero — the normalization is well-defined otherwise.
    (This is the identity the earlier Python-side attempt to normalize the versor was missing.) -/
theorem normSq_versorFromVectors {a b : G3} (ha : IsVector a) (hb : IsVector b) :
    normSq (versorFromVectors a b)
      = 2 * magnitude a * magnitude b * (magnitude a * magnitude b + dot a b) := by
  obtain ⟨ha_s, ha_c12, ha_c13, ha_c23, ha_c123⟩ := ha
  obtain ⟨hb_s, hb_c12, hb_c13, hb_c23, hb_c123⟩ := hb
  have hA : magnitude a ^ 2 = a.c1 ^ 2 + a.c2 ^ 2 + a.c3 ^ 2 := by
    rw [magnitude_sq_eq_normSq, normSq_eq_sum_sq, ha_s, ha_c12, ha_c13, ha_c23, ha_c123]; ring
  have hB : magnitude b ^ 2 = b.c1 ^ 2 + b.c2 ^ 2 + b.c3 ^ 2 := by
    rw [magnitude_sq_eq_normSq, normSq_eq_sum_sq, hb_s, hb_c12, hb_c13, hb_c23, hb_c123]; ring
  simp only [normSq, versorFromVectors, add, mul, smul, one, reverse, dot, ha_s, ha_c12, ha_c13, ha_c23, ha_c123, hb_s, hb_c12, hb_c13, hb_c23, hb_c123]
  linear_combination (-(magnitude b ^ 2)) * hA + (-(a.c1 ^ 2 + a.c2 ^ 2 + a.c3 ^ 2)) * hB

/-- The from-vectors versor is nonzero when `a`, `b` are nonzero and not antiparallel — the geometric
    reading of the `normSq (versorFromVectors a b) ≠ 0` guard carried by the whole chain. -/
theorem normSq_versorFromVectors_ne_zero {a b : G3} (ha : IsVector a) (hb : IsVector b)
    (hna : normSq a ≠ 0) (hnb : normSq b ≠ 0) (h : magnitude a * magnitude b + dot a b ≠ 0) :
    normSq (versorFromVectors a b) ≠ 0 := by
  rw [normSq_versorFromVectors ha hb]
  exact mul_ne_zero (mul_ne_zero (mul_ne_zero two_ne_zero (magnitude_ne_zero_of_normSq_ne_zero hna))
    (magnitude_ne_zero_of_normSq_ne_zero hnb)) h

end G3

/-! ## 2D coda: the from-vectors rotor of two unit directions IS the half-angle rotor -/

open Real

/-- `|uvec α|² = 1`. -/
theorem normSq_uvec (α : ℝ) : G2.normSq (uvec α) = 1 := by
  rw [G2.normSq_eq_sum_sq]
  simp only [uvec, G2.add, G2.smul, G2.e_1, G2.e_2]
  linear_combination cos_sq_add_sin_sq α

/-- `|uvec α| = 1`. -/
theorem magnitude_uvec (α : ℝ) : G2.magnitude (uvec α) = 1 := by
  simp only [G2.magnitude]; rw [normSq_uvec, Real.sqrt_one]

/-- **The from-vectors versor of two unit directions is `2cos(θ/2)` times the half-angle rotor**,
    `θ = β − α`: `uvec β * uvec α + 1 = (1 + cos(θ)) − sin(θ) * e₁₂ = 2cos(θ/2) * (cos(θ/2) − sin(θ/2) * e₁₂)`
    — the half-angle appears through `1 + cos(θ) = 2cos²(θ/2)` and `sin(θ) = 2 sin(θ/2) cos(θ/2)`. -/
theorem versorFromVectors_uvec (α β : ℝ) :
    G2.versorFromVectors (uvec α) (uvec β) = G2.smul (2 * cos ((β - α) / 2)) (rotor (β - α)) := by
  have hc : cos (β - α) = 2 * cos ((β - α) / 2) ^ 2 - 1 := by
    have h2 := cos_two_mul ((β - α) / 2)
    rw [show (2 : ℝ) * ((β - α) / 2) = β - α by ring] at h2
    exact h2
  have hs : sin (β - α) = 2 * sin ((β - α) / 2) * cos ((β - α) / 2) := by
    have h2 := sin_two_mul ((β - α) / 2)
    rw [show (2 : ℝ) * ((β - α) / 2) = β - α by ring] at h2
    exact h2
  rw [G2.versorFromVectors, uvec_mul_uvec, magnitude_uvec, magnitude_uvec,
    show α - β = -(β - α) by ring]
  simp only [fullAngleRotor, rotor, G2.add, G2.smul, G2.one, G2.e_12, cos_neg, sin_neg, hc, hs]
  ext <;> ring

/-- **Normalizing it gives exactly the half-angle rotor** (for `θ = β − α` with `cos(θ/2) > 0`, i.e.
    the directions not antiparallel): `rotorFromVectors (uvec α) (uvec β) = rotor (β − α)`. -/
theorem rotorFromVectors_uvec (α β : ℝ) (hc : 0 < cos ((β - α) / 2)) :
    G2.rotorFromVectors (uvec α) (uvec β) = rotor (β - α) := by
  have hpos : (0 : ℝ) < 2 * cos ((β - α) / 2) := by linarith
  have hm : G2.magnitude (G2.smul (2 * cos ((β - α) / 2)) (rotor (β - α)))
      = 2 * cos ((β - α) / 2) := by
    simp only [G2.magnitude]
    rw [G2.normSq_smul, (isRotor_rotor (β - α)).2, mul_one, Real.sqrt_sq hpos.le]
  rw [G2.rotorFromVectors, G2.normalize, versorFromVectors_uvec, hm, G2.smul_smul,
    one_div_mul_cancel hpos.ne', G2.one_smul]

/-- **The whole 2D chain:** the rotor built from the directions α and β, applied as the reverse
    sandwich `R̂ v R̂̃`, rotates `v` by the angle `β − α` between them — through the half-angle rotor
    (`rotorFromVectors_uvec`) and `sandwich_rotor`. -/
theorem rotorSandwich_rotorFromVectors_uvec (α β : ℝ) (hc : 0 < cos ((β - α) / 2)) {v : G2}
    (hv : G2.IsVector v) :
    G2.rotorSandwich (G2.rotorFromVectors (uvec α) (uvec β)) v = rot (β - α) v := by
  rw [rotorFromVectors_uvec α β hc, G2.rotorSandwich, sandwich_rotor (β - α) hv]

end GacalcProofs
