import GacalcProofs.G2
import GacalcProofs.Projection2D

/-! # Reduction to standard position in 𝒢₂ — a SINGLE elementary plane rotation, no versors

    The 2D case of "reduction to standard position" (a.k.a. *frame reduction*): compute the projection
    of one vector onto another by rotating the figure into a convenient frame, doing the easy version
    there, and rotating back — the method in the maintainer's matrix-math proof
    `multivariate-math/proofs/crossproduct.tex`.

    **In 2D the whole picture lives in one plane, so a SINGLE elementary plane rotation does it** —
    there is no third coordinate to fold down, so the two-rotation (`rotXY` then `rotXZ`) composition of
    the 𝒢₃ `StandardPosition.lean` collapses to one `rotPlane`. This is the version the book presents
    first (`book/docs/proof-projection.rst`); the 𝒢₃ file is the 3D step-up.

    **The rotation here is an ELEMENTARY plane rotation, built as a procedure on the vector's components
    — deliberately NOT a versor / the geometric-product sandwich.** `rotPlane c s` takes the two
    components `(v.c1, v.c2)`, rotates them by `(cos(θ) = c, sin(θ) = s)`, and leaves the scalar/bivector parts
    untouched — the precalculus "rotate the coordinate pair" operation. Using a versor here would be
    **circular**: a versor is itself a geometric product, and the point of standard position is to
    *bootstrap* the geometric product from projection/rejection using only operations trusted
    independently of it. The `(cos, sin)` are read straight off `b`'s own coordinates
    (`c = b₁/|b|`, `s = −b₂/|b|`) — no inverse trig, no angle named.

    We prove the plane rotation is linear and **preserves the dot product** (when `c² + s² = 1`), hence
    **projection and rejection are equivariant** under it, so "rotate `b` onto the x-axis, read off the
    x-component, rotate back" IS the Hestenes projection: `projectSP a b = proj b a`
    (`projectSP_eq_proj`) and `rejectSP a b = reject b a` (`rejectSP_eq_reject`). See
    `tasks/reference/reduction-to-standard-position.md`. -/
namespace GacalcProofs.G2

/-! ### The elementary plane rotation (a procedure on the components) -/

/-- Rotate the `(e₁, e₂)` components of a 𝒢₂ vector by `(cos(θ) = c, sin(θ) = s)`, leaving the scalar and
    bivector parts untouched: `(x, y) ↦ (c x − s y, s x + c y)`. No matrices, no versors — it just
    recombines the components. (The 2D twin of `GacalcProofs.G3.rotXY`; in 2D there is only one plane,
    so this one rotation is the whole alignment.) -/
noncomputable def rotPlane (c s : ℝ) (v : G2) : G2 :=
  ⟨v.s, c * v.c1 - s * v.c2, s * v.c1 + c * v.c2, v.c12⟩

/-- `rotPlane` pulls out scalars (linearity). -/
theorem rotPlane_smul (c s k : ℝ) (v : G2) : rotPlane c s (smul k v) = smul k (rotPlane c s v) := by
  simp only [rotPlane, smul]; ext <;> ring

/-- `rotPlane` distributes over subtraction (linearity). -/
theorem rotPlane_sub (c s : ℝ) (u v : G2) :
    rotPlane c s (sub u v) = sub (rotPlane c s u) (rotPlane c s v) := by
  simp only [rotPlane, sub]; ext <;> ring

/-- **`rotPlane` preserves the dot product** when `c² + s² = 1` (it is a rotation): the cross terms
    cancel and `(c²+s²)` scales the in-plane part back to itself. -/
theorem rotPlane_preserves_dot (c s : ℝ) (hcs : c ^ 2 + s ^ 2 = 1) (u v : G2) :
    dot (rotPlane c s u) (rotPlane c s v) = dot u v := by
  simp only [dot, rotPlane, mul]
  linear_combination (u.c1 * v.c1 + u.c2 * v.c2) * hcs

/-! ### Projection and rejection are equivariant under the plane rotation

    `proj a b = (b·a / a·a)·a`, and the plane rotation is linear and preserves the dot, so both the
    scalar coefficient and the direction `a` transform the same way — the projection commutes with the
    rotation. This is the justification of "rotate to standard position, project, rotate back". -/

/-- **Projection is equivariant under the plane rotation:** `proj (R a) (R b) = R (proj a b)` for
    `R = rotPlane c s` with `c² + s² = 1`. -/
theorem proj_rotPlane_equivariant (c s : ℝ) (hcs : c ^ 2 + s ^ 2 = 1) (a b : G2) :
    proj (rotPlane c s a) (rotPlane c s b) = rotPlane c s (proj a b) := by
  simp only [proj, rotPlane_smul]
  rw [rotPlane_preserves_dot c s hcs b a, rotPlane_preserves_dot c s hcs a a]

/-- The **vector rejection** (perpendicular component) `b − proj_a b`. For a vector `a` with
    `a·a ≠ 0` this equals the Hestenes rejection `(b∧a)a⁻¹` (`reject_vec_eq`). -/
noncomputable def vecReject (a b : G2) : G2 := sub b (proj a b)

/-- **Rejection is equivariant under the plane rotation** (from `proj_rotPlane_equivariant` and
    `rotPlane_sub`). -/
theorem vecReject_rotPlane_equivariant (c s : ℝ) (hcs : c ^ 2 + s ^ 2 = 1) (a b : G2) :
    vecReject (rotPlane c s a) (rotPlane c s b) = rotPlane c s (vecReject a b) := by
  simp only [vecReject]
  rw [rotPlane_sub, proj_rotPlane_equivariant c s hcs a b]

/-! ### The explicit alignment: rotate `b` onto the x-axis with the single plane rotation

    The concrete 2D standard position: `rotPlane (b₁/m) (−b₂/m)` (with `m = |b|`, so the `(cos, sin)` is
    read off `b`'s coordinates) swings `b` onto `|b|*e₁`. One rotation — no second plane. -/

/-- **`b` rotates onto the x-axis:** `rotPlane (b₁/m) (−b₂/m)` sends `(b₁, b₂)` to `(m, 0)`, where
    `m = |b| = √(b₁²+b₂²)` (`m ≠ 0`, `m² = b₁²+b₂²`). The elementary, versor-free alignment. -/
theorem rotPlane_aligns (b1 b2 m : ℝ) (hm : m ≠ 0) (hm2 : m ^ 2 = b1 ^ 2 + b2 ^ 2) :
    rotPlane (b1 / m) (-b2 / m) (vec b1 b2) = vec m 0 := by
  simp only [rotPlane, vec]
  ext
  · rfl
  · field_simp; linear_combination -hm2
  · field_simp; ring
  · rfl

/-- The plane rotation is undone by the one with the opposite sine (`s' = −s`), when `c² + s² = 1`. -/
theorem rotPlane_inv (c s s' : ℝ) (hcs : c ^ 2 + s ^ 2 = 1) (h : s' + s = 0) (v : G2) :
    rotPlane c s' (rotPlane c s v) = v := by
  ext
  · rfl
  · show c * (c * v.c1 - s * v.c2) - s' * (s * v.c1 + c * v.c2) = v.c1
    linear_combination v.c1 * hcs - (s * v.c1 + c * v.c2) * h
  · show s' * (c * v.c1 - s * v.c2) + c * (s * v.c1 + c * v.c2) = v.c2
    linear_combination v.c2 * hcs + (c * v.c1 - s * v.c2) * h
  · rfl

/-- **Projection onto the x-axis is "keep the x-component":** `proj (m·e₁) v = (v₁, 0)` for any
    multivector `v` and `m ≠ 0` — the elementary step done in standard position, where no product is
    needed to project. -/
theorem proj_onto_x_axis (m : ℝ) (hm : m ≠ 0) (v : G2) : proj (vec m 0) v = vec v.c1 0 := by
  simp only [proj, dot, mul, smul, vec]
  ext <;> field_simp <;> ring

/-! ### The standard-position projection equals the Hestenes projection

    `project_sp a b`: align `b` to the x-axis with `rotPlane (b₁/m) (−b₂/m)` (`m = |b|`), apply the same
    to `a`, **keep the aligned `a`'s x-component** (projection onto the x-axis is the elementary "read
    off a coordinate" step — no product, `proj_onto_x_axis`), and rotate back (negate the sine). In the
    aligned frame that x-component IS the Hestenes projection onto `|b|*e₁`; the rotation preserves the
    dot and is projection-equivariant, and is undone by its negated-sine twin — so the whole procedure
    IS `proj b a`. The degenerate `b = 0` case (`|b| = 0`) is excluded by hypothesis. -/

/-- **Align to the x-axis:** `rotPlane (b₁/|b|) (−b₂/|b|)`, the `(cos, sin)` read off `b`'s own
    coordinates, applied to any `v`. -/
noncomputable def alignSP (b v : G2) : G2 :=
  rotPlane (b.c1 / magnitude b) (-b.c2 / magnitude b) v

/-- **Rotate back:** negate the sine. -/
noncomputable def unalignSP (b v : G2) : G2 :=
  rotPlane (b.c1 / magnitude b) (b.c2 / magnitude b) v

/-- **Standard-position projection** (`project_sp a b`): align, keep the aligned `a`'s x-component (the
    elementary projection onto the x-axis), rotate back. -/
noncomputable def projectSP (a b : G2) : G2 := unalignSP b (vec (alignSP b a).c1 0)

/-- **Standard-position rejection** (`reject_sp a b = a − project_sp a b`). -/
noncomputable def rejectSP (a b : G2) : G2 := sub a (projectSP a b)

/-- `m² = |b|² = b₁² + b₂²` for a vector `b`. -/
theorem magnitude_sq_of_isVector {b : G2} (hbv : IsVector b) :
    magnitude b ^ 2 = b.c1 ^ 2 + b.c2 ^ 2 := by
  have hnb : normSq b = b.c1 ^ 2 + b.c2 ^ 2 := by
    conv_lhs => rw [eq_vec_of_isVector hbv]
    exact normSq_vec b.c1 b.c2
  rw [magnitude, Real.sq_sqrt (by rw [hnb]; positivity), hnb]

/-- The `(cos, sin)` read off `b` is a unit pair. -/
theorem cs_unit {b : G2} (hbv : IsVector b) (hb : magnitude b ≠ 0) :
    (b.c1 / magnitude b) ^ 2 + (-b.c2 / magnitude b) ^ 2 = 1 := by
  rw [div_pow, div_pow, neg_sq, ← add_div, ← magnitude_sq_of_isVector hbv]
  exact div_self (pow_ne_zero 2 hb)

/-- Rotating back undoes the alignment. -/
theorem unalignSP_alignSP {b : G2} (hbv : IsVector b) (hb : magnitude b ≠ 0) (v : G2) :
    unalignSP b (alignSP b v) = v := by
  simp only [unalignSP, alignSP]
  rw [rotPlane_inv _ _ _ (cs_unit hbv hb) (by ring)]

/-- **The alignment sends `b` itself to `|b|*e₁`** — `rotPlane_aligns` read through `alignSP`. -/
theorem alignSP_self {b : G2} (hbv : IsVector b) (hb : magnitude b ≠ 0) :
    alignSP b b = vec (magnitude b) 0 := by
  have h := rotPlane_aligns b.c1 b.c2 (magnitude b) hb (magnitude_sq_of_isVector hbv)
  have hb' : rotPlane (b.c1 / magnitude b) (-b.c2 / magnitude b) b
      = rotPlane (b.c1 / magnitude b) (-b.c2 / magnitude b) (vec b.c1 b.c2) := by
    rw [← eq_vec_of_isVector hbv]
  rw [alignSP, hb', h]

/-- **`project_sp = project`:** the standard-position projection of `a` onto `b` is the Hestenes
    projection `proj b a`, for a nonzero vector `b` (`|b| ≠ 0`); `a` may be any multivector. In the
    aligned frame "keep the x-component" is `proj (|b|*e₁)` (`proj_onto_x_axis` + `alignSP_self`); then
    equivariance of `proj` under the plane rotation, and undo it. -/
theorem projectSP_eq_proj {b : G2} (hbv : IsVector b) (hb : magnitude b ≠ 0) (a : G2) :
    projectSP a b = proj b a := by
  have hx : vec (alignSP b a).c1 0 = proj (alignSP b b) (alignSP b a) := by
    rw [alignSP_self hbv hb, proj_onto_x_axis (magnitude b) hb]
  rw [projectSP, hx]
  simp only [alignSP, unalignSP]
  rw [proj_rotPlane_equivariant _ _ (cs_unit hbv hb),
      rotPlane_inv _ _ _ (cs_unit hbv hb) (by ring)]

/-- The geometric product distributes over subtraction on the left (2D). -/
theorem sub_mul (a b c : G2) : mul (sub a b) c = sub (mul a c) (mul b c) := by
  simp only [mul, sub]; ext <;> ring

/-- **Hestenes rejection onto a vector equals the projection-complement** (coordinates): `(b∧a)a⁻¹ =
    b − proj_a b`, for `a·a ≠ 0`. Structural (Hestenes), division-free: `b∧a = ba − (b·a)·1`, so
    `(b∧a)a⁻¹ = b(a a⁻¹) − (b·a)a⁻¹ = b − proj_a b`. -/
theorem reject_vec_eq_coord (a1 a2 b1 b2 : ℝ) (ha : a1 ^ 2 + a2 ^ 2 ≠ 0) :
    reject (vec a1 a2) (vec b1 b2)
      = sub (vec b1 b2) (proj (vec a1 a2) (vec b1 b2)) := by
  have hnorm : normSq (vec a1 a2) = a1 ^ 2 + a2 ^ 2 := normSq_vec a1 a2
  have hdaa : dot (vec a1 a2) (vec a1 a2) = a1 ^ 2 + a2 ^ 2 := by rw [dot_vec]; ring
  have hsplit : wedge (vec b1 b2) (vec a1 a2)
      = sub (mul (vec b1 b2) (vec a1 a2)) (smul (dot (vec b1 b2) (vec a1 a2)) one) := by
    rw [mul_eq_dot_add_wedge (isVector_vec b1 b2) (isVector_vec a1 a2)]
    simp only [sub, add, smul, one]; ext <;> ring
  have hinv : mul (vec a1 a2) (inverse (vec a1 a2)) = one := by
    rw [inverse, reverse_vec, mul_smul, hnorm,
        show mul (vec a1 a2) (vec a1 a2) = smul (a1 ^ 2 + a2 ^ 2) one by
          simp only [mul, vec, smul, one]; ext <;> ring,
        smul_smul, one_div_mul_cancel ha, one_smul]
  rw [reject, hsplit, sub_mul, mul_assoc, hinv, mul_one, smul_mul, one_mul]
  congr 1
  rw [proj, inverse, reverse_vec, smul_smul]
  congr 1
  rw [hnorm, hdaa]
  ring

/-- **Hestenes rejection onto a vector equals the projection-complement** (object form):
    `reject_a b = b − proj_a b`, for a nonzero vector `a` (`|a|² ≠ 0`) and a vector `b`. -/
theorem reject_vec_eq {a b : G2} (ha_isv : IsVector a) (hb_isv : IsVector b) (ha : normSq a ≠ 0) :
    reject a b = sub b (proj a b) := by
  have ha' : a.c1 ^ 2 + a.c2 ^ 2 ≠ 0 := by
    have hn : normSq a = a.c1 ^ 2 + a.c2 ^ 2 := by
      conv_lhs => rw [eq_vec_of_isVector ha_isv]
      exact normSq_vec a.c1 a.c2
    rwa [hn] at ha
  have h := reject_vec_eq_coord a.c1 a.c2 b.c1 b.c2 ha'
  rwa [← eq_vec_of_isVector ha_isv, ← eq_vec_of_isVector hb_isv] at h

/-- **`reject_sp = reject`:** the standard-position rejection is the vector rejection `a − proj b a`
    (`vecReject b a`), hence the Hestenes `reject b a` for vectors. -/
theorem rejectSP_eq_vecReject {b : G2} (hbv : IsVector b) (hb : magnitude b ≠ 0) (a : G2) :
    rejectSP a b = vecReject b a := by
  simp only [rejectSP, vecReject, projectSP_eq_proj hbv hb]

theorem rejectSP_eq_reject {a b : G2} (hav : IsVector a) (hbv : IsVector b) (hb : magnitude b ≠ 0)
    (hbn : normSq b ≠ 0) : rejectSP a b = reject b a := by
  rw [rejectSP_eq_vecReject hbv hb, vecReject, reject_vec_eq hbv hav hbn]

end GacalcProofs.G2
