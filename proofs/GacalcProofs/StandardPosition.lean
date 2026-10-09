import GacalcProofs.G3
import GacalcProofs.AlgebraLaws
import GacalcProofs.Projection3D

/-! # Reduction to standard position — elementary plane rotations, no versors

    "Reduction to standard position" (a.k.a. *frame reduction*) computes a hard operation by rotating
    the figure into a convenient frame, doing the easy version there, and rotating the result back —
    the method in the maintainer's matrix-math proof `multivariate-math/proofs/crossproduct.tex`
    (rotate `a` onto the x-axis by composing plane rotations, apply the same rotations to `b`, compute
    with trusted 2D steps, then apply the inverse rotations).

    **The rotations here are ELEMENTARY coordinate-plane rotations, built as procedures on a vector's
    components — deliberately NOT versors / the geometric-product sandwich.** A plane rotation
    `rotXY c s` takes the two in-plane components `(v.c1, v.c2)`, rotates them by `(cos(θ) = c, sin(θ) = s)`,
    and leaves the perpendicular component `v.c3` (and the scalar/bivector parts) untouched — the
    high-school "break the vector into its components, rotate the plane, add the axis part back"
    operation. Using a versor here would be **circular**: a versor is itself a geometric product, and
    the point of standard position is to *bootstrap* the geometric product from projection/rejection
    using only operations trusted independently of it (precalculus 2D rotation).

    We prove each plane rotation is linear and **preserves the dot product** (when `c² + s² = 1`),
    hence **projection and rejection are equivariant** under it: `proj (R a) (R b) = R (proj a b)`.
    That is exactly what makes "rotate to standard position, project, rotate back" valid. Composing
    `rotXY` then `rotXZ` with the `(cos, sin)` read off `b`'s own coordinates sends `b` to `|b|*e₁`
    (the standard position), where the projection is elementary. See
    `tasks/reference/reduction-to-standard-position.md`. -/
namespace GacalcProofs.G3

/-! ### Elementary coordinate-plane rotations (procedures on the components) -/

/-- Rotate the e₁,e₂ (xy-plane) components of a vector by `(cos(θ) = c, sin(θ) = s)`, leaving e₃ and the
    scalar/bivector/pseudoscalar parts untouched. The elementary 2D rotation embedded in the xy-plane
    — no matrices, no versors: it just recombines the components. -/
noncomputable def rotXY (c s : ℝ) (v : G3) : G3 :=
  ⟨v.s, c * v.c1 - s * v.c2, s * v.c1 + c * v.c2, v.c3, v.c12, v.c13, v.c23, v.c123⟩

/-- Rotate the e₁,e₃ (xz-plane) components by `(cos(θ) = c, sin(θ) = s)`, leaving e₂ and the other parts. -/
noncomputable def rotXZ (c s : ℝ) (v : G3) : G3 :=
  ⟨v.s, c * v.c1 - s * v.c3, v.c2, s * v.c1 + c * v.c3, v.c12, v.c13, v.c23, v.c123⟩

/-- `rotXY` pulls out scalars (linearity). -/
theorem rotXY_smul (c s k : ℝ) (v : G3) : rotXY c s (smul k v) = smul k (rotXY c s v) := by
  simp only [rotXY, smul]; ext <;> ring

/-- `rotXY` distributes over subtraction (linearity). -/
theorem rotXY_sub (c s : ℝ) (u v : G3) : rotXY c s (sub u v) = sub (rotXY c s u) (rotXY c s v) := by
  simp only [rotXY, sub]; ext <;> ring

/-- `rotXZ` pulls out scalars (linearity). -/
theorem rotXZ_smul (c s k : ℝ) (v : G3) : rotXZ c s (smul k v) = smul k (rotXZ c s v) := by
  simp only [rotXZ, smul]; ext <;> ring

/-- **`rotXY` preserves the dot product** when `c² + s² = 1` (it is a rotation): the cross terms
    cancel and `(c²+s²)` scales the in-plane part back to itself. -/
theorem rotXY_preserves_dot (c s : ℝ) (hcs : c ^ 2 + s ^ 2 = 1) (u v : G3) :
    dot (rotXY c s u) (rotXY c s v) = dot u v := by
  simp only [dot, rotXY, mul]
  linear_combination (u.c1 * v.c1 + u.c2 * v.c2) * hcs

/-- **`rotXZ` preserves the dot product** when `c² + s² = 1`. -/
theorem rotXZ_preserves_dot (c s : ℝ) (hcs : c ^ 2 + s ^ 2 = 1) (u v : G3) :
    dot (rotXZ c s u) (rotXZ c s v) = dot u v := by
  simp only [dot, rotXZ, mul]
  linear_combination (u.c1 * v.c1 + u.c3 * v.c3) * hcs

/-! ### Projection and rejection are equivariant under a plane rotation

    `proj a b = (b·a / a·a)·a`, and a plane rotation is linear and preserves the dot, so both the
    scalar coefficient and the direction `a` transform the same way — the projection commutes with the
    rotation. This is the justification of "rotate to standard position, project, rotate back": the
    answer is the same whether you project in place or in the rotated frame and rotate back. -/

/-- **Projection is equivariant under the xy-plane rotation:** `proj (R a) (R b) = R (proj a b)`
    for `R = rotXY c s` with `c² + s² = 1`. -/
theorem proj_rotXY_equivariant (c s : ℝ) (hcs : c ^ 2 + s ^ 2 = 1) (a b : G3) :
    proj (rotXY c s a) (rotXY c s b) = rotXY c s (proj a b) := by
  simp only [proj, rotXY_smul]
  rw [rotXY_preserves_dot c s hcs b a, rotXY_preserves_dot c s hcs a a]

/-- **Projection is equivariant under the xz-plane rotation.** -/
theorem proj_rotXZ_equivariant (c s : ℝ) (hcs : c ^ 2 + s ^ 2 = 1) (a b : G3) :
    proj (rotXZ c s a) (rotXZ c s b) = rotXZ c s (proj a b) := by
  simp only [proj, rotXZ_smul]
  rw [rotXZ_preserves_dot c s hcs b a, rotXZ_preserves_dot c s hcs a a]

/-- The **vector rejection** (perpendicular component) `b − proj_a b`. For a vector `a` with
    `a·a ≠ 0` this equals the Hestenes rejection `(b∧a)a⁻¹` (`reject_vec_eq`). -/
noncomputable def vecReject (a b : G3) : G3 := sub b (proj a b)

/-- **Rejection is equivariant under the xy-plane rotation** (from `proj_rotXY_equivariant` and
    `rotXY_sub`). Together with the projection lemma this covers Pass-1 (project + reject). -/
theorem vecReject_rotXY_equivariant (c s : ℝ) (hcs : c ^ 2 + s ^ 2 = 1) (a b : G3) :
    vecReject (rotXY c s a) (rotXY c s b) = rotXY c s (vecReject a b) := by
  simp only [vecReject]
  rw [rotXY_sub, proj_rotXY_equivariant c s hcs a b]

/-! ### The geometric product of vectors, reconstructed from projection + rejection

    The maintainer's claim (confirmed): once you have `project`/`reject` you can build the geometric
    product of two vectors, because `a = a∥ + a⊥` relative to `b` gives `ab = a·b + a∧b`. Here we do
    it with `a` as the reference vector: `a b = a (proj_a b) + a (b − proj_a b)`, the parallel part
    contributing the scalar `a·b` and the perpendicular part the bivector `a∧b`. The wedge half is
    already `plane_eq_wedge`; this adds the dot half and the reassembly. **Versor-free** — it uses
    only `proj`, `mul`, and the elementary product identities. -/

/-- **The projection recovers the dot** (object form): `a (proj_a b) = (b·a)·1` for a vector `a`
    (`|a|² ≠ 0`) and a vector `b`. -/
theorem mul_proj_eq_dot {a b : G3} (ha_isv : IsVector a) (hb_isv : IsVector b) (ha : normSq a ≠ 0) :
    mul a (proj a b) = smul (dot b a) one := by
  rw [eq_vec_of_isVector ha_isv, eq_vec_of_isVector hb_isv]
  have hdaa : dot (vec a.c1 a.c2 a.c3) (vec a.c1 a.c2 a.c3) ≠ 0 := by
    rw [dot_self_vec_eq_normSq_coord, ← eq_vec_of_isVector ha_isv]; exact ha
  rw [proj, GacalcProofs.G3.mul_smul, mul_vec_self_coord, GacalcProofs.G3.smul_smul,
      ← dot_self_vec_eq_normSq_coord]
  congr 1
  field_simp

/-- **The geometric product of two vectors, from projection + rejection:** `a b = (a·b)*1 + a∧b`,
    assembled as `a (proj_a b) + a (b − proj_a b)`. The payoff of the theme: the vector geometric
    product is built from `project`/`reject` (for `|a|² ≠ 0`). -/
theorem mul_eq_proj_dot_add_reject_wedge {a b : G3} (ha_isv : IsVector a) (hb_isv : IsVector b)
    (ha : normSq a ≠ 0) :
    mul a b = add (smul (dot b a) one) (wedge a b) := by
  rw [eq_vec_of_isVector ha_isv, eq_vec_of_isVector hb_isv]
  have ha' : normSq (vec a.c1 a.c2 a.c3) ≠ 0 := by rw [← eq_vec_of_isVector ha_isv]; exact ha
  have hsplit : mul (vec a.c1 a.c2 a.c3) (vec b.c1 b.c2 b.c3)
      = add (mul (vec a.c1 a.c2 a.c3) (proj (vec a.c1 a.c2 a.c3) (vec b.c1 b.c2 b.c3)))
            (mul (vec a.c1 a.c2 a.c3)
                 (sub (vec b.c1 b.c2 b.c3) (proj (vec a.c1 a.c2 a.c3) (vec b.c1 b.c2 b.c3)))) := by
    rw [← GacalcProofs.G3.mul_add]
    congr 1
    simp only [proj, add, sub, smul, vec]; ext <;> ring
  rw [hsplit, mul_proj_eq_dot (isVector_vec a.c1 a.c2 a.c3) (isVector_vec b.c1 b.c2 b.c3) ha',
      plane_eq_wedge a.c1 a.c2 a.c3 b.c1 b.c2 b.c3 ha']

/-! ### The explicit alignment: rotate `b` onto the x-axis by composing plane rotations

    The concrete standard position the maintainer described (as in `crossproduct.tex`): compose the
    xy-plane rotation that zeroes `b₂` with the xz-plane rotation that zeroes `b₃`, sending `b` to
    `|b|*e₁`. The `(cos, sin)` are read off `b`'s own coordinates. Stated with `k = √(b₁²+b₂²)` and
    `m = |b| = √(b₁²+b₂²+b₃²)` supplied via their squares, so the arithmetic is `ring`/`field_simp`;
    `rotate_b_to_e1_magnitude` then instantiates them as the actual magnitudes. -/

/-- **Step 1 — swing `b`'s xy-part onto the x-axis:** `rotXY (b₁/k) (−b₂/k)` sends `(b₁, b₂, b₃)` to
    `(k, 0, b₃)`, where `k = √(b₁²+b₂²)` (`k ≠ 0`, `k² = b₁²+b₂²`). -/
theorem rotXY_aligns_xy (b1 b2 b3 k : ℝ) (hk : k ≠ 0) (hk2 : k ^ 2 = b1 ^ 2 + b2 ^ 2) :
    rotXY (b1 / k) (-b2 / k) (vec b1 b2 b3) = vec k 0 b3 := by
  simp only [rotXY, vec]
  ext
  · rfl
  · field_simp; linear_combination -hk2
  · field_simp; ring
  · rfl
  · rfl
  · rfl
  · rfl
  · rfl

/-- **Step 2 — swing `(k, 0, b₃)` onto the x-axis:** `rotXZ (k/m) (−b₃/m)` sends `(k, 0, b₃)` to
    `(m, 0, 0)`, where `m = √(k²+b₃²)` (`m ≠ 0`, `m² = k²+b₃²`). -/
theorem rotXZ_aligns_xz (k b3 m : ℝ) (hm : m ≠ 0) (hm2 : m ^ 2 = k ^ 2 + b3 ^ 2) :
    rotXZ (k / m) (-b3 / m) (vec k 0 b3) = vec m 0 0 := by
  simp only [rotXZ, vec]
  ext
  · rfl
  · field_simp; linear_combination -hm2
  · rfl
  · field_simp; ring
  · rfl
  · rfl
  · rfl
  · rfl

/-- **`b` rotates onto the x-axis:** composing the two plane rotations sends `b` to `|b|*e₁ =
    vec m 0 0` (`m = |b|`). The elementary, versor-free standard-position alignment. -/
theorem rotate_b_to_e1 (b1 b2 b3 k m : ℝ) (hk : k ≠ 0) (hm : m ≠ 0)
    (hk2 : k ^ 2 = b1 ^ 2 + b2 ^ 2) (hm2 : m ^ 2 = b1 ^ 2 + b2 ^ 2 + b3 ^ 2) :
    rotXZ (k / m) (-b3 / m) (rotXY (b1 / k) (-b2 / k) (vec b1 b2 b3)) = vec m 0 0 := by
  rw [rotXY_aligns_xy b1 b2 b3 k hk hk2,
      rotXZ_aligns_xz k b3 m hm (by rw [hm2, hk2])]

/-- **`b` rotates onto the x-axis, entirely in `magnitude` terms** — the instantiated form of
    `rotate_b_to_e1` with `k = |b's xy-part| = magnitude (vec b₁ b₂ 0)` and `m = |b| =
    magnitude (vec b₁ b₂ b₃)`. Both `(cos, sin)` and the target `|b|*e₁` read as actual magnitudes
    (no raw `√(…)` or coordinate sums): `b's xy-part` swings onto the x-axis, then the residual `b₃`
    is rotated in. The square hypotheses `k² = b₁²+b₂²` and `m² = b₁²+b₂²+b₃²` are just the two
    `magnitude² = normSq` facts (`Real.sq_sqrt` + `normSq_vec`). -/
theorem rotate_b_to_e1_magnitude (b1 b2 b3 : ℝ)
    (hk : magnitude (vec b1 b2 0) ≠ 0) (hb : magnitude (vec b1 b2 b3) ≠ 0) :
    rotXZ (magnitude (vec b1 b2 0) / magnitude (vec b1 b2 b3))
          (-b3 / magnitude (vec b1 b2 b3))
      (rotXY (b1 / magnitude (vec b1 b2 0)) (-b2 / magnitude (vec b1 b2 0))
        (vec b1 b2 b3))
      = smul (magnitude (vec b1 b2 b3)) (vec 1 0 0) := by
  have hk2 : magnitude (vec b1 b2 0) ^ 2 = b1 ^ 2 + b2 ^ 2 := by
    rw [magnitude, Real.sq_sqrt (by rw [normSq_vec]; positivity), normSq_vec]; ring
  have hm2 : magnitude (vec b1 b2 b3) ^ 2 = b1 ^ 2 + b2 ^ 2 + b3 ^ 2 := by
    rw [magnitude, Real.sq_sqrt (by rw [normSq_vec]; positivity), normSq_vec]
  rw [rotate_b_to_e1 b1 b2 b3 _ _ hk hb hk2 hm2]
  simp only [vec, smul]; ext <;> ring

/-! ### The standard-position projection equals the Hestenes projection

    Python `standardposition.project_sp a b` (`_project_via_standard_position`): align `b` to the
    x-axis with `rotXY (b₁/k) (−b₂/k)` then `rotXZ (k/m) (−b₃/m)` (`k = |b's xy-part|`, `m = |b|`),
    apply the same to `a`, **keep the aligned `a`'s x-component** (projection onto the x-axis is the
    elementary "read off a coordinate" step — no product, `proj_onto_x_axis`), and rotate back (negate
    each sine, reverse the order). In the aligned frame that x-component IS the Hestenes projection onto
    `|b|*e₁`; the two rotations preserve the dot and are projection-equivariant, and each is undone by
    its negated-sine twin — so the whole procedure IS `proj b a`. This is the single theorem `CLAUDE.md`
    and the Python docstring promise; the degenerate z-axis case (`k = 0`) is excluded by hypothesis, as
    in Python. -/

/-- A plane rotation is undone by the one with the opposite sine (`s' = −s`), when `c² + s² = 1`. -/
theorem rotXY_inv (c s s' : ℝ) (hcs : c ^ 2 + s ^ 2 = 1) (h : s' + s = 0) (v : G3) :
    rotXY c s' (rotXY c s v) = v := by
  ext
  · rfl
  · show c * (c * v.c1 - s * v.c2) - s' * (s * v.c1 + c * v.c2) = v.c1
    linear_combination v.c1 * hcs - (s * v.c1 + c * v.c2) * h
  · show s' * (c * v.c1 - s * v.c2) + c * (s * v.c1 + c * v.c2) = v.c2
    linear_combination v.c2 * hcs + (c * v.c1 - s * v.c2) * h
  · rfl
  · rfl
  · rfl
  · rfl
  · rfl

theorem rotXZ_inv (c s s' : ℝ) (hcs : c ^ 2 + s ^ 2 = 1) (h : s' + s = 0) (v : G3) :
    rotXZ c s' (rotXZ c s v) = v := by
  ext
  · rfl
  · show c * (c * v.c1 - s * v.c3) - s' * (s * v.c1 + c * v.c3) = v.c1
    linear_combination v.c1 * hcs - (s * v.c1 + c * v.c3) * h
  · rfl
  · show s' * (c * v.c1 - s * v.c3) + c * (s * v.c1 + c * v.c3) = v.c3
    linear_combination v.c3 * hcs + (c * v.c1 - s * v.c3) * h
  · rfl
  · rfl
  · rfl
  · rfl

/-- `k = |b's xy-part| = magnitude (vec b₁ b₂ 0)` — the first standard-position magnitude. -/
noncomputable def xyMagnitude (b : G3) : ℝ := magnitude (vec b.c1 b.c2 0)

/-- **Align to the x-axis** (Python `align`): `rotXY (b₁/k) (−b₂/k)` then `rotXZ (k/m) (−b₃/m)`,
    with the `(cos, sin)` read off `b`'s own coordinates, applied to any `v`. -/
noncomputable def alignSP (b v : G3) : G3 :=
  rotXZ (xyMagnitude b / magnitude b) (-b.c3 / magnitude b)
    (rotXY (b.c1 / xyMagnitude b) (-b.c2 / xyMagnitude b) v)

/-- **Rotate back** (Python `rotate_back`): negate each sine, apply in the reverse order. -/
noncomputable def unalignSP (b v : G3) : G3 :=
  rotXY (b.c1 / xyMagnitude b) (b.c2 / xyMagnitude b)
    (rotXZ (xyMagnitude b / magnitude b) (b.c3 / magnitude b) v)

/-- **Projection onto the x-axis is "keep the x-component":** `proj (m·e₁) v = (v₁, 0, 0)` for any
    multivector `v` and `m ≠ 0` — the elementary step done in standard position, where no product is
    needed to project. -/
theorem proj_onto_x_axis (m : ℝ) (hm : m ≠ 0) (v : G3) : proj (vec m 0 0) v = vec v.c1 0 0 := by
  simp only [proj, dot, mul, smul, vec]
  ext <;> field_simp <;> ring

/-- **Standard-position projection** (Python `standardposition.project_sp a b`): align, keep the
    aligned `a`'s x-component (the elementary projection onto the x-axis), rotate back. -/
noncomputable def projectSP (a b : G3) : G3 := unalignSP b (vec (alignSP b a).c1 0 0)

/-- **Standard-position rejection** (Python `standardposition.reject_sp a b = a − project_sp a b`). -/
noncomputable def rejectSP (a b : G3) : G3 := sub a (projectSP a b)

/-- `k² = b₁² + b₂²`. -/
theorem xyMagnitude_sq (b : G3) : xyMagnitude b ^ 2 = b.c1 ^ 2 + b.c2 ^ 2 := by
  rw [xyMagnitude, magnitude, Real.sq_sqrt (by rw [normSq_vec]; positivity), normSq_vec]; ring

/-- `m² = |b|² = b₁² + b₂² + b₃²` for a vector `b`. -/
theorem magnitude_sq_of_isVector {b : G3} (hbv : IsVector b) :
    magnitude b ^ 2 = b.c1 ^ 2 + b.c2 ^ 2 + b.c3 ^ 2 := by
  have hnb : normSq b = b.c1 ^ 2 + b.c2 ^ 2 + b.c3 ^ 2 := by
    conv_lhs => rw [eq_vec_of_isVector hbv]
    exact normSq_vec b.c1 b.c2 b.c3
  rw [magnitude, Real.sq_sqrt (by rw [hnb]; positivity), hnb]

/-- The xy `(cos, sin)` read off `b` is a unit pair. -/
theorem cs_xy_unit {b : G3} (hk : xyMagnitude b ≠ 0) :
    (b.c1 / xyMagnitude b) ^ 2 + (-b.c2 / xyMagnitude b) ^ 2 = 1 := by
  rw [div_pow, div_pow, neg_sq, ← add_div, ← xyMagnitude_sq]
  exact div_self (pow_ne_zero 2 hk)

/-- The xz `(cos, sin)` read off `b` is a unit pair. -/
theorem cs_xz_unit {b : G3} (hbv : IsVector b) (hb : magnitude b ≠ 0) :
    (xyMagnitude b / magnitude b) ^ 2 + (-b.c3 / magnitude b) ^ 2 = 1 := by
  rw [div_pow, div_pow, neg_sq, ← add_div, xyMagnitude_sq, ← magnitude_sq_of_isVector hbv]
  exact div_self (pow_ne_zero 2 hb)

/-- Rotating back undoes the alignment. -/
theorem unalignSP_alignSP {b : G3} (hbv : IsVector b) (hk : xyMagnitude b ≠ 0)
    (hb : magnitude b ≠ 0) (v : G3) : unalignSP b (alignSP b v) = v := by
  simp only [unalignSP, alignSP]
  rw [rotXZ_inv _ _ _ (cs_xz_unit hbv hb) (by ring), rotXY_inv _ _ _ (cs_xy_unit hk) (by ring)]

/-- **The alignment sends `b` itself to `|b|*e₁`** — `rotate_b_to_e1` read through `alignSP`. -/
theorem alignSP_self {b : G3} (hbv : IsVector b) (hk : xyMagnitude b ≠ 0)
    (hb : magnitude b ≠ 0) : alignSP b b = vec (magnitude b) 0 0 := by
  have h := rotate_b_to_e1 b.c1 b.c2 b.c3 (xyMagnitude b) (magnitude b) hk hb (xyMagnitude_sq b)
    (magnitude_sq_of_isVector hbv)
  have hb' : rotXY (b.c1 / xyMagnitude b) (-b.c2 / xyMagnitude b) b
      = rotXY (b.c1 / xyMagnitude b) (-b.c2 / xyMagnitude b) (vec b.c1 b.c2 b.c3) := by
    rw [← eq_vec_of_isVector hbv]
  rw [alignSP, hb', h]

/-- **`project_sp = project`:** the standard-position projection of `a` onto `b` is the Hestenes
    projection `proj b a`, for a vector `b` not on the z-axis (`k ≠ 0`) and nonzero (`|b| ≠ 0`);
    `a` may be any multivector. In the aligned frame "keep the x-component" is `proj (|b|*e₁)`
    (`proj_onto_x_axis` + `alignSP_self`); then equivariance of `proj` under both plane rotations,
    and undo them. -/
theorem projectSP_eq_proj {b : G3} (hbv : IsVector b) (hk : xyMagnitude b ≠ 0)
    (hb : magnitude b ≠ 0) (a : G3) : projectSP a b = proj b a := by
  have hx : vec (alignSP b a).c1 0 0 = proj (alignSP b b) (alignSP b a) := by
    rw [alignSP_self hbv hk hb, proj_onto_x_axis (magnitude b) hb]
  rw [projectSP, hx]
  simp only [alignSP, unalignSP]
  rw [proj_rotXZ_equivariant _ _ (cs_xz_unit hbv hb), proj_rotXY_equivariant _ _ (cs_xy_unit hk),
      rotXZ_inv _ _ _ (cs_xz_unit hbv hb) (by ring), rotXY_inv _ _ _ (cs_xy_unit hk) (by ring)]

/-- **`reject_sp = reject`:** the standard-position rejection is the vector rejection
    `a − proj b a` (`vecReject`), hence the Hestenes `reject b a` for vectors (`reject_vec_eq`). -/
theorem rejectSP_eq_vecReject {b : G3} (hbv : IsVector b) (hk : xyMagnitude b ≠ 0)
    (hb : magnitude b ≠ 0) (a : G3) : rejectSP a b = vecReject b a := by
  simp only [rejectSP, vecReject, projectSP_eq_proj hbv hk hb]

theorem rejectSP_eq_reject {a b : G3} (hav : IsVector a) (hbv : IsVector b) (hk : xyMagnitude b ≠ 0)
    (hb : magnitude b ≠ 0) (hbn : normSq b ≠ 0) : rejectSP a b = reject b a := by
  rw [rejectSP_eq_vecReject hbv hk hb, vecReject, reject_vec_eq hbv hav hbn]

end GacalcProofs.G3
