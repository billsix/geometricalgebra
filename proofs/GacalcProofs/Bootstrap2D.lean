import GacalcProofs.Projection2D
import GacalcProofs.StandardPosition2D
import GacalcProofs.ProjectionRotation2D

/-! # The 2D bootstrap: the two steps that redefine projection and rotation through the product

    The book's Part III, "The 2D Bootstrap" (`book/docs/bootstrap-*.rst`), runs the whole arc in 𝒢₂:
    the precalculus rotation → projection from rotation → rotation from projection → the geometric
    product → projection through the product → rotation through the product. Most steps already have
    their theorems elsewhere (cited on each page). This file holds the ones that were missing:

    * `proj_eq_dot_mul_inverse` — projection through the product: `proj_a b = (b·a)*a⁻¹`, the scalar
      `b·a` (the scalar part of `b*a`) times the inverse of `a`.
    * `mul_proj_eq_dot`, `mul_reject_eq_wedge` — `a*proj_a b = a·b` and `a*rej_a b = a∧b`, with the
      mirrors `mul_proj_symm` (`b*proj_b a = a*proj_a b`) and `mul_reject_antisymm`
      (`b*rej_b a = −(a*rej_a b)`), and the split `mul_eq_mul_proj_add_mul_reject`.
    * Step 3's rotation from `a` to `b` of every `v`. The book defines it as Step 1's blend with the
      cosine and sine of the angle from `a` to `b`, read off `b`'s projection and rejection on `a`:
      the `rotPlane` of `rotPlane_fromTo_eq_vec_mul`, which shows it is `v*(â*b̂)`.
      `rotPlane_fromTo_eq_rotateFromToProj` identifies it with `rotateFromToProj`, the same map
      written through `v`'s coordinates in `a`'s standard position rebuilt along and across `b`.
      `rotateFromToProj` carries the properties:
      * `rotateFromToProj_eq_unalign_align` (it is `(R_b^{e₁})⁻¹ ∘ R_a^{e₁}`);
      * `rotateFromToProj_eq_vec_mul` (it is `v*(â*b̂)`);
      * `rotateFromToProj_preserves_dot` (it keeps lengths and angles);
      * `rotateFromToProj_smul_smul` (rescaling `a`, `b` by positive numbers changes nothing: only
        directions matter);
      * `rotateFromToProj_normalize` (it carries `â` to `b̂`).

    Objects in, coordinates only in the body. -/
namespace GacalcProofs.G2

/-- **Projection through the product.** For vectors `a`, `b` with `a` invertible, the projection of
    `b` onto `a` is the scalar `b·a` times `a⁻¹`: `proj_a b = (b·a)*a⁻¹`. Here `b·a` is `dot b a`, the
    scalar part of the geometric product `b*a`, and `a⁻¹ = ã/|a|²`. -/
theorem proj_eq_dot_mul_inverse {a b : G2} (ha : IsVector a) (hb : IsVector b)
    (han : normSq a ≠ 0) :
    proj a b = mul (scalar (dot b a)) (inverse a) := by
  obtain ⟨has, ha12⟩ := ha
  obtain ⟨hbs, hb12⟩ := hb
  have han' : a.c1 * a.c1 + a.c2 * a.c2 ≠ 0 := by
    simpa [normSq, mul, reverse, has, ha12] using han
  simp only [proj, inverse, normSq, reverse, mul, scalar, smul, dot, has, ha12, hbs, hb12]
  ext <;> simp only <;> field_simp <;> ring

-- twin: GacalcProofs.G2.mul_proj_eq_dot
/-- **The dot product is `a` times the projection of `b` onto `a`:** `a*proj_a b = a·b`. The
    projection lies along `a`, so its product with `a` has no area part and is the plain number
    `a·b`. A result about the product, stated for vectors (Step 4). -/
theorem mul_proj_eq_dot {a b : G2} (ha : IsVector a) (hb : IsVector b) (han : normSq a ≠ 0) :
    mul a (proj a b) = scalar (dot a b) := by
  obtain ⟨has, ha12⟩ := ha
  obtain ⟨hbs, hb12⟩ := hb
  have han' : a.c1 * a.c1 + a.c2 * a.c2 ≠ 0 := by
    simpa [normSq, mul, reverse, has, ha12] using han
  have h2 : a.c1 ^ 2 + a.c2 ^ 2 ≠ 0 := fun h => han' (by linear_combination h)
  simp only [proj, mul, scalar, smul, dot, has, ha12, hbs, hb12]
  ext <;> simp only <;> (ring_nf; try (field_simp; ring))

-- twin: GacalcProofs.G2.mul_reject_eq_wedge
/-- **The wedge is `a` times the rejection of `b` from `a`:** `a*rej_a b = a∧b`. The rejection lies
    across `a`, so its product with `a` is pure area. A result about the product, stated for vectors
    (Step 4). -/
theorem mul_reject_eq_wedge {a b : G2} (ha : IsVector a) (hb : IsVector b) (han : normSq a ≠ 0) :
    mul a (reject a b) = wedge a b := by
  obtain ⟨has, ha12⟩ := ha
  obtain ⟨hbs, hb12⟩ := hb
  have han' : a.c1 * a.c1 + a.c2 * a.c2 ≠ 0 := by
    simpa [normSq, mul, reverse, has, ha12] using han
  have h2 : a.c1 ^ 2 + a.c2 ^ 2 ≠ 0 := fun h => han' (by linear_combination h)
  simp only [reject, inverse, normSq, reverse, mul, wedge, smul, has, ha12, hbs, hb12]
  ext <;> simp only <;> (ring_nf; try (field_simp; ring))

/-- **The mirror of the dot:** `b*proj_b a = a*proj_a b`, both `a·b`. Projecting the other way and
    multiplying by the other vector gives the same number. -/
theorem mul_proj_symm {a b : G2} (ha : IsVector a) (hb : IsVector b) (han : normSq a ≠ 0)
    (hbn : normSq b ≠ 0) :
    mul b (proj b a) = mul a (proj a b) := by
  rw [mul_proj_eq_dot hb ha hbn, mul_proj_eq_dot ha hb han, dot_comm]

/-- **The mirror of the wedge flips its sign:** `b*rej_b a = −(a*rej_a b)`, that is `b∧a = −(a∧b)`.
    Unlike the dot, the wedge is antisymmetric. -/
theorem mul_reject_antisymm {a b : G2} (ha : IsVector a) (hb : IsVector b) (han : normSq a ≠ 0)
    (hbn : normSq b ≠ 0) :
    mul b (reject b a) = neg (mul a (reject a b)) := by
  rw [mul_reject_eq_wedge hb ha hbn, mul_reject_eq_wedge ha hb han]
  obtain ⟨has, ha12⟩ := ha
  obtain ⟨hbs, hb12⟩ := hb
  simp only [wedge, neg]
  ext <;> simp only [has, ha12, hbs, hb12] <;> ring

/-- **The product splits along and across `a`:** `a*b = a*proj_a b + a*rej_a b`, which is
    `a·b + a∧b` by `mul_proj_eq_dot` and `mul_reject_eq_wedge`. -/
theorem mul_eq_mul_proj_add_mul_reject {a b : G2} (ha : IsVector a) (hb : IsVector b)
    (han : normSq a ≠ 0) :
    mul a b = add (mul a (proj a b)) (mul a (reject a b)) := by
  rw [mul_proj_eq_dot ha hb han, mul_reject_eq_wedge ha hb han, mul_eq_dot_add_wedge ha hb]

/-- **The rotation from projection is the one-sided product.** The elementary rotation whose cosine
    and sine are `(a·b)/(|a|*|b|)` and `(a∧b)/(|a|*|b|)` — the projection and rejection of `b` measured
    in `a`'s standard position, divided by `|b|` (`bprime_coords`, `rotateFromTo_collapse`) — applied
    to a vector `v` equals `v*(â*b̂)`, the right product with the two unit vectors. -/
theorem rotPlane_fromTo_eq_vec_mul {a b v : G2} (ha : IsVector a) (hb : IsVector b)
    (hv : IsVector v) (hma : magnitude a ≠ 0) (hmb : magnitude b ≠ 0) :
    rotPlane (dot a b / (magnitude a * magnitude b)) ((wedge a b).c12 / (magnitude a * magnitude b)) v
      = mul v (mul (normalizeVec a) (normalizeVec b)) := by
  obtain ⟨has, ha12⟩ := ha
  obtain ⟨hbs, hb12⟩ := hb
  obtain ⟨hvs, hv12⟩ := hv
  simp only [rotPlane, normalizeVec, smul, mul, dot, wedge, has, ha12, hbs, hb12, hvs, hv12]
  ext <;> simp only <;> field_simp <;> ring

/-! ### Step 3: the rotation from `a` to `b`, defined for every vector, from projection -/

/-- **Step 3's rotation from `a` to `b`**, for any `v`. Read `v`'s coordinates `(x, y)` in `a`'s
    standard position (`alignSP a v`): `x` is the signed length of `v`'s projection on `a`, `y` of its
    rejection. Rebuild them along and across `b`: `x*b̂ + y*b̂⊥`, with `b̂⊥ = rot90 b̂` the quarter turn
    of the unit vector along `b`. Only the directions `â`, `b̂` enter. -/
noncomputable def rotateFromToProj (a b v : G2) : G2 :=
  add (smul (alignSP a v).c1 (normalizeVec b)) (smul (alignSP a v).c2 (rot90 (normalizeVec b)))

/-- **It is the composition of Step 2's two rotations:** `(R_b^{e₁})⁻¹ ∘ R_a^{e₁}`, turning `a`'s
    frame onto the x-axis and then the x-axis onto `b`'s frame. -/
theorem rotateFromToProj_eq_unalign_align {a b v : G2} (hb : IsVector b) (hv : IsVector v) :
    rotateFromToProj a b v = unalignSP b (alignSP a v) := by
  obtain ⟨hbs, hb12⟩ := hb
  obtain ⟨hvs, hv12⟩ := hv
  simp only [rotateFromToProj, unalignSP, alignSP, rotPlane, normalizeVec, smul, add, rot90, vec,
    hbs, hb12, hvs, hv12]
  ext <;> simp only <;> ring

/-- **It is the one-sided product:** `rotateFromToProj a b v = v*(â*b̂)`. -/
theorem rotateFromToProj_eq_vec_mul {a b v : G2} (ha : IsVector a) (hb : IsVector b)
    (hv : IsVector v) :
    rotateFromToProj a b v = mul v (mul (normalizeVec a) (normalizeVec b)) := by
  obtain ⟨has, ha12⟩ := ha
  obtain ⟨hbs, hb12⟩ := hb
  obtain ⟨hvs, hv12⟩ := hv
  simp only [rotateFromToProj, alignSP, rotPlane, normalizeVec, smul, add, rot90, vec, mul,
    has, ha12, hbs, hb12, hvs, hv12]
  ext <;> simp only <;> ring

/-- `(b₁/|b|, b₂/|b|)` is a unit pair: the cosine and sine `unalignSP b` turns by. -/
theorem cs_unit_unalign {b : G2} (hbv : IsVector b) (hb : magnitude b ≠ 0) :
    (b.c1 / magnitude b) ^ 2 + (b.c2 / magnitude b) ^ 2 = 1 := by
  rw [div_pow, div_pow, ← add_div, ← magnitude_sq_of_isVector hbv]
  exact div_self (pow_ne_zero 2 hb)

/-- **It is a rotation: it keeps every dot product**, so every length and every angle:
    `R u · R w = u · w`. -/
theorem rotateFromToProj_preserves_dot {a b u w : G2} (ha : IsVector a) (hb : IsVector b)
    (hu : IsVector u) (hw : IsVector w) (hma : magnitude a ≠ 0) (hmb : magnitude b ≠ 0) :
    dot (rotateFromToProj a b u) (rotateFromToProj a b w) = dot u w := by
  rw [rotateFromToProj_eq_unalign_align hb hu, rotateFromToProj_eq_unalign_align hb hw]
  simp only [unalignSP, alignSP]
  rw [rotPlane_preserves_dot _ _ (cs_unit_unalign hb hmb),
    rotPlane_preserves_dot _ _ (cs_unit ha hma)]

/-- A scalar multiple of a vector is a vector. -/
theorem isVector_smul_of_isVector (k : ℝ) {a : G2} (ha : IsVector a) : IsVector (smul k a) :=
  ⟨by simp [smul, ha.1], by simp [smul, ha.2]⟩

/-- `|k*a| = k*|a|` for `k ≥ 0`. -/
theorem magnitude_smul_of_nonneg {k : ℝ} (hk : 0 ≤ k) (a : G2) :
    magnitude (smul k a) = k * magnitude a := by
  unfold magnitude
  rw [normSq_smul, Real.sqrt_mul (sq_nonneg k), Real.sqrt_sq hk]

/-- Rescaling by a positive number does not change the direction: `normalizeVec (k*a) = â`. -/
theorem normalizeVec_smul_of_pos {k : ℝ} (hk : 0 < k) {a : G2} (hma : magnitude a ≠ 0) :
    normalizeVec (smul k a) = normalizeVec a := by
  have hk' : k ≠ 0 := hk.ne'
  unfold normalizeVec
  rw [magnitude_smul_of_nonneg hk.le]
  simp only [smul]
  ext <;> simp only <;> field_simp

/-- **Only directions matter:** rescaling `a` and `b` by positive numbers gives the same rotation. -/
theorem rotateFromToProj_smul_smul {a b v : G2} {k m : ℝ} (hk : 0 < k) (hm : 0 < m)
    (ha : IsVector a) (hb : IsVector b) (hv : IsVector v)
    (hma : magnitude a ≠ 0) (hmb : magnitude b ≠ 0) :
    rotateFromToProj (smul k a) (smul m b) v = rotateFromToProj a b v := by
  rw [rotateFromToProj_eq_vec_mul (isVector_smul_of_isVector k ha) (isVector_smul_of_isVector m hb) hv,
    rotateFromToProj_eq_vec_mul ha hb hv, normalizeVec_smul_of_pos hk hma,
    normalizeVec_smul_of_pos hm hmb]

/-- **It carries `â` to `b̂`:** `a`'s direction lands on `b`'s. -/
theorem rotateFromToProj_normalize {a b : G2} (ha : IsVector a) (hma : magnitude a ≠ 0) :
    rotateFromToProj a b (normalizeVec a) = normalizeVec b := by
  have hx : (alignSP a (normalizeVec a)).c1 = 1 := by
    have e : (alignSP a (normalizeVec a)).c1 = (a.c1 ^ 2 + a.c2 ^ 2) / magnitude a ^ 2 := by
      simp only [alignSP, rotPlane, normalizeVec, smul]
      ring
    rw [e, ← magnitude_sq_of_isVector ha]
    exact div_self (pow_ne_zero 2 hma)
  have hy : (alignSP a (normalizeVec a)).c2 = 0 := by
    simp only [alignSP, rotPlane, normalizeVec, smul]
    ring
  simp only [rotateFromToProj, hx, hy]
  simp only [normalizeVec, smul, add, rot90, vec]
  ext <;> simp only <;> ring

/-- **The book's definition and `rotateFromToProj` are the same map.** Step 1's blend with the
    cosine and sine of the angle from `a` to `b` (read off `b`'s projection and rejection on `a`)
    equals `v`'s coordinates in `a`'s standard position rebuilt along and across `b`: both are
    `v*(â*b̂)`. -/
theorem rotPlane_fromTo_eq_rotateFromToProj {a b v : G2} (ha : IsVector a) (hb : IsVector b)
    (hv : IsVector v) (hma : magnitude a ≠ 0) (hmb : magnitude b ≠ 0) :
    rotPlane (dot a b / (magnitude a * magnitude b)) ((wedge a b).c12 / (magnitude a * magnitude b)) v
      = rotateFromToProj a b v := by
  rw [rotPlane_fromTo_eq_vec_mul ha hb hv hma hmb, rotateFromToProj_eq_vec_mul ha hb hv]

end GacalcProofs.G2
