import Mathlib
import GacalcProofs.G2

/-! # Rotation from scratch, and the geometric product derived from it (2D)

    The book's spine: define rotation from sin/cos, then *derive the geometric
    product from rotation*, then read off the dot and wedge. This module does the
    2D case (the foundation the dot/wedge/projection step-tasks build on):

      * `rot θ` — rotation of a coordinate pair by θ, the geometric definition;
        it composes by adding angles (`rot_add`) and preserves the norm
        (`rot_normSq`).
      * `rotor θ = cos θ + sin θ · e₁e₂ ∈ 𝒢₂`, and **the geometric product ENACTS
        rotation**: right-multiplying a vector by the rotor rotates it
        (`vec_mul_rotor`).
      * **The geometric product of two unit vectors IS the rotor of the angle
        between them** (`uvec_mul_uvec`): (uvec α)(uvec β) = rotor (β − α). This is
        the geometric product *derived from rotation*.
      * Reading off its parts: the scalar part is cos(β − α) = the **dot** product,
        the e₁e₂ part is sin(β − α) = the **wedge** — connecting to
        `GacalcProofs.G2` (dot = symmetric part, wedge = antisymmetric part).
      * **Rotation "from a to b" for general (non-unit) vectors** (the book's exact
        framing): with vectors in polar form, `b = (|b|/|a|) · rot (φb − φa) a`
        (`rot_from_to`) — magnitude scales by the ratio, direction rotates by the
        angle from a to b; and the rotor built from the two directions carries one
        to the other (`rotorFromTo_carry`).

    DESIGN (decided by the author 2026-09-28): keep the GA construction **standalone**
    (our own `rot`/`rotor`/`G2`), using Mathlib only for the trig lemmas
    (`cos_add`/`sin_add`/`cos_sub`/`sin_sub`/`cos_sq_add_sin_sq`); the *equivalence to
    the general case* (Mathlib's `Real.Angle`/rotation, `@inner`) is where we map to
    Mathlib, and that mapping is the only place we lean on its GA/rotation machinery.

    STATUS: `tasks/lean-proof-rotation-from-scratch.md`. 2D core + the general-vector
    "from a to b" framing landed; the sandwich/rotor-composition story, the
    Mathlib-rotation *equivalence* proof, and the 3D version remain. -/
namespace GacalcProofs

open Real

/-- Rotation of a coordinate pair by angle θ — the geometric definition, from
    sin/cos. -/
noncomputable def rot (θ : ℝ) (v : ℝ × ℝ) : ℝ × ℝ :=
  (v.1 * cos θ - v.2 * sin θ, v.1 * sin θ + v.2 * cos θ)

/-- Rotations compose by adding their angles. -/
theorem rot_add (θ φ : ℝ) (v : ℝ × ℝ) : rot θ (rot φ v) = rot (φ + θ) v := by
  simp only [rot, cos_add, sin_add, Prod.mk.injEq]
  constructor <;> ring

/-- Rotation preserves the squared norm (magnitudes are unchanged). -/
theorem rot_normSq (θ x y : ℝ) :
    (rot θ (x, y)).1 ^ 2 + (rot θ (x, y)).2 ^ 2 = x ^ 2 + y ^ 2 := by
  simp only [rot]
  linear_combination (x ^ 2 + y ^ 2) * cos_sq_add_sin_sq θ

/-- The rotor for angle θ, as a linear combination of the basis *elements* `one` and
    `e_12` (not a raw coordinate tuple): R = cos θ · 1 + sin θ · e₁e₂ ∈ 𝒢₂. -/
noncomputable def rotor (θ : ℝ) : G2 := G2.add (G2.smul (cos θ) G2.one) (G2.smul (sin θ) G2.e_12)

/-- The geometric product ENACTS rotation: right-multiplying a vector by the rotor
    for θ rotates the vector by θ. -/
theorem vec_mul_rotor (θ x y : ℝ) :
    G2.mul (G2.vec x y) (rotor θ) = G2.vec (rot θ (x, y)).1 (rot θ (x, y)).2 := by
  simp only [G2.mul, G2.vec, rotor, G2.add, G2.smul, G2.one, G2.e_12, rot]; ext <;> ring

/-- A unit vector at angle α, as a linear combination of the basis *elements* `e_1`
    and `e_2` (not a raw coordinate tuple): cos α · e₁ + sin α · e₂. -/
noncomputable def uvec (α : ℝ) : G2 := G2.add (G2.smul (cos α) G2.e_1) (G2.smul (sin α) G2.e_2)

/-- The unit vector `uvec α` in coordinate form — its e₁, e₂ coefficients are cos α,
    sin α. Bridges the element-form definition to `G2.vec`, so `vec_mul_rotor` applies. -/
theorem uvec_eq_vec (α : ℝ) : uvec α = G2.vec (cos α) (sin α) := by
  simp only [uvec, G2.vec, G2.add, G2.smul, G2.e_1, G2.e_2]; ext <;> ring

/-- **The geometric product of two unit vectors is the rotor of the angle between
    them:** (uvec α)(uvec β) = rotor (β − α). This is the geometric product derived
    from rotation. -/
theorem uvec_mul_uvec (α β : ℝ) : G2.mul (uvec α) (uvec β) = rotor (β - α) := by
  simp only [G2.mul, uvec, rotor, G2.add, G2.smul, G2.one, G2.e_1, G2.e_2, G2.e_12,
    cos_sub, sin_sub]
  ext <;> ring

/-- Reading off the scalar part: the **dot product** of two unit vectors is the
    cosine of the angle between them. -/
theorem uvec_dot (α β : ℝ) : (G2.mul (uvec α) (uvec β)).s = cos (β - α) := by
  rw [uvec_mul_uvec]; simp only [rotor, G2.add, G2.smul, G2.one, G2.e_12]; ring

/-- Reading off the e₁e₂ part: the **wedge product** of two unit vectors is the sine
    of the angle between them. -/
theorem uvec_wedge (α β : ℝ) : (G2.mul (uvec α) (uvec β)).c12 = sin (β - α) := by
  rw [uvec_mul_uvec]; simp only [rotor, G2.add, G2.smul, G2.one, G2.e_12]; ring

/-! ## Rotation "from a to b" for general (non-unit) vectors

    The book defines rotation as taking "the direction of vec 1 to vec 2, magnitudes
    irrelevant." Written with vectors in polar form `a = polar ra φa`, `b = polar rb
    φb` (magnitude and direction angle), that is: **b is a rescaled and rotated,
    `b = (|b|/|a|) · rot (φb − φa) a`** — the direction rotates by the angle from a to
    b, and the magnitude scales by the ratio |b|/|a|. -/

/-- A coordinate vector in polar form: magnitude `r`, direction angle `φ`. -/
noncomputable def polar (r φ : ℝ) : ℝ × ℝ := (r * cos φ, r * sin φ)

/-- Scale a coordinate pair by a real factor (kept standalone rather than reaching
    for `ℝ × ℝ`'s module instance, so the construction stays self-contained). -/
def scale (c : ℝ) (v : ℝ × ℝ) : ℝ × ℝ := (c * v.1, c * v.2)

/-- Rotating a polar vector by θ adds θ to its direction angle and leaves its
    magnitude alone — direction rotates, magnitude is preserved. -/
theorem rot_polar (r φ θ : ℝ) : rot θ (polar r φ) = polar r (φ + θ) := by
  simp only [rot, polar, cos_add, sin_add, Prod.mk.injEq]
  constructor <;> ring

/-- **Rotation from a to b** (the book's framing) for general, possibly non-unit
    vectors: writing `a = polar ra φa` and `b = polar rb φb` with `a ≠ 0` (`ra ≠ 0`),
    b is a rotated by the angle from a to b and rescaled by the magnitude ratio:
    `b = (|b|/|a|) · rot (φb − φa) a`. -/
theorem rot_from_to (ra rb φa φb : ℝ) (h : ra ≠ 0) :
    polar rb φb = scale (rb / ra) (rot (φb - φa) (polar ra φa)) := by
  have hφ : φa + (φb - φa) = φb := by ring
  rw [rot_polar, hφ]
  simp only [polar, scale, Prod.mk.injEq]
  constructor <;> field_simp

/-- Rotating a unit direction: `rot θ` sends the unit vector at angle α to the unit
    vector at angle α + θ (the r = 1 case of `rot_polar`, stated on `(cos α, sin α)`). -/
theorem rot_cossin (α θ : ℝ) : rot θ (cos α, sin α) = (cos (α + θ), sin (α + θ)) := by
  simp only [rot, cos_add, sin_add]
  ext <;> ring

/-- The rotor that carries direction α to direction β, as the geometric product of
    the two unit vectors: `R = (uvec α)(uvec β) = rotor (β − α)`. -/
noncomputable def rotorFromTo (α β : ℝ) : G2 := G2.mul (uvec α) (uvec β)

/-- **The rotor from a to b carries a to b:** right-multiplying the unit vector at
    angle α by the rotor from α to β yields the unit vector at angle β. This is
    "rotation from the direction of a to the direction of b", enacted by the
    geometric product. -/
theorem rotorFromTo_carry (α β : ℝ) :
    G2.mul (uvec α) (rotorFromTo α β) = uvec β := by
  have hφ : α + (β - α) = β := by ring
  rw [rotorFromTo, uvec_mul_uvec, uvec_eq_vec α, uvec_eq_vec β]
  simp only [vec_mul_rotor, rot_cossin, hφ]

/-! ## The versor sandwich: rotation as `R v R̃`, and the half-angle relationship

    The general GA rotation (the one that generalizes to 3D) is the **sandwich**
    `v ↦ R v R̃` by a unit versor `R`. gacalc's versor uses the **half angle**:
    `R = cos(θ/2)·1 − sin(θ/2)·e₁₂`, and sandwiching a vector by it rotates by the *full*
    angle θ (`sandwich_versor`). For a unit versor `R R̃ = 1` (`versor_unit`/`versor_unit'`),
    so `R̃` is the two-sided inverse and the reverse sandwich `R v R̃` equals the inverse
    sandwich `R v R⁻¹` that gacalc's `MultiVectorBase.sandwich` implements. The
    un-normalized versor + inverse-sandwich form (scale-invariant, magnitude irrelevant) is
    the next step — see `tasks/reference/unit-bivector-and-rotors.md` §6. -/

/-- gacalc's unit versor that rotates by θ *through the sandwich*: `R = cos(θ/2)·1 −
    sin(θ/2)·e₁₂`, a linear combination of the basis elements `one` and `e_12`. The half
    angle is deliberate — see `sandwich_versor`. -/
noncomputable def versor (θ : ℝ) : G2 :=
  G2.add (G2.smul (cos (θ / 2)) G2.one) (G2.smul (-(sin (θ / 2))) G2.e_12)

/-- `versor θ` is a **unit** versor: `R R̃ = 1`. -/
theorem versor_unit (θ : ℝ) : G2.mul (versor θ) (G2.reverse (versor θ)) = G2.one := by
  simp only [versor, G2.reverse, G2.mul, G2.add, G2.smul, G2.one, G2.e_12]
  ext <;> first | linear_combination sin_sq_add_cos_sq (θ / 2) | ring

/-- …and `R̃ R = 1` too, so `R̃` is a genuine two-sided inverse. Hence for this unit versor
    the reverse sandwich `R v R̃` coincides with the inverse sandwich `R v R⁻¹`. -/
theorem versor_unit' (θ : ℝ) : G2.mul (G2.reverse (versor θ)) (versor θ) = G2.one := by
  simp only [versor, G2.reverse, G2.mul, G2.add, G2.smul, G2.one, G2.e_12]
  ext <;> first | linear_combination sin_sq_add_cos_sq (θ / 2) | ring

/-- **The half-angle sandwich equals the full rotation** — the equivalence to check:
    sandwiching a vector between the half-angle versor and its reverse rotates it by the
    full angle θ, exactly the map `rot θ`. (The `cos θ = cos²(θ/2) − sin²(θ/2)` and
    `sin θ = 2 sin(θ/2) cos(θ/2)` double-angle identities are where the half turns whole.) -/
theorem sandwich_versor (θ x y : ℝ) :
    G2.mul (G2.mul (versor θ) (G2.vec x y)) (G2.reverse (versor θ))
      = G2.vec (rot θ (x, y)).1 (rot θ (x, y)).2 := by
  have hc : cos θ = cos (θ / 2) ^ 2 - sin (θ / 2) ^ 2 := by
    have h2 := cos_two_mul (θ / 2)
    rw [show (2 : ℝ) * (θ / 2) = θ by ring] at h2
    linear_combination h2 + sin_sq_add_cos_sq (θ / 2)
  have hs : sin θ = 2 * sin (θ / 2) * cos (θ / 2) := by
    have h2 := sin_two_mul (θ / 2)
    rw [show (2 : ℝ) * (θ / 2) = θ by ring] at h2
    exact h2
  simp only [versor, G2.reverse, G2.mul, G2.vec, G2.add, G2.smul, G2.one, G2.e_12, rot, hc, hs]
  ext <;> ring

/-- The half-angle sandwich reproduces the one-sided full-angle operator `v * rotor θ` —
    the two 2D rotation mechanisms agree. -/
theorem sandwich_versor_eq_vec_mul_rotor (θ x y : ℝ) :
    G2.mul (G2.mul (versor θ) (G2.vec x y)) (G2.reverse (versor θ))
      = G2.mul (G2.vec x y) (rotor θ) := by
  rw [sandwich_versor, vec_mul_rotor]

/-- **Versors compose by multiplication, and half-angles add:** `R θ₂ · R θ₁ = R (θ₁+θ₂)`,
    so composing two sandwich rotations is a single sandwich by the product versor (the
    total rotation angle is θ₁ + θ₂). -/
theorem versor_mul (θ₁ θ₂ : ℝ) : G2.mul (versor θ₂) (versor θ₁) = versor (θ₁ + θ₂) := by
  simp only [versor, G2.mul, G2.add, G2.smul, G2.one, G2.e_12]
  rw [show (θ₁ + θ₂) / 2 = θ₂ / 2 + θ₁ / 2 by ring]
  simp only [cos_add, sin_add]
  ext <;> ring

end GacalcProofs
