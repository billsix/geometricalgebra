import GacalcProofs.G3
import GacalcProofs.Cross
import GacalcProofs.Projection3D
import GacalcProofs.StandardPosition

/-! # Reduction to standard position as a GENERAL tool — reduce both vectors to the e₁*e₂ plane (𝒢₃)

    `StandardPosition.lean` reduces ONE vector to the `e₁` axis (2 elementary plane rotations) and does
    `project`/`reject`/the geometric product there. This file makes the technique **uniform**: three
    elementary plane rotations (`rotXY`, `rotXZ`, `rotYZ` — procedures on the components, NOT versors)
    put BOTH vectors into the `e₁*e₂` plane — `a` on `e₁ = (|a|,0,0)`, `b = (b₁',b₂',0)` — after which
    EVERY operation is an elementary 2-D operation in that plane, rotated back. The same 3-rotation
    reduction serves `project`, `reject`, AND the `cross` product (mirroring the maintainer's
    `multivariate-math/proofs/crossproduct.tex`). The 3rd rotation (`rotYZ`, swinging `b` into the
    plane) is not needed by `project`/`reject` alone, but it is used uniformly so the whole frame is 2-D
    for every operation.

    The engine is **equivariance**: each operation commutes with each elementary plane rotation
    (`OP (R a) (R b) = R (OP a b)` for `cos²(θ) + sin²(θ) = 1`), which is exactly what licenses "rotate to standard
    position, do the elementary 2-D op, rotate back." Equivariance is proved against the canonical
    definitions (`proj`, `vecReject = b − proj_a b`, `cross = dual (wedge ..)` / `cross_vec`), so each
    reduced computation equals the canonical result. -/
namespace GacalcProofs.G3

/-! ### The third elementary plane rotation `rotYZ` (about the fixed `e₁` axis) -/

/-- Rotate the e₂,e₃ (yz-plane) components by `(cos(θ) = c, sin(θ) = s)`, leaving e₁ and the scalar/bivector/
    pseudoscalar parts untouched. -/
noncomputable def rotYZ (c s : ℝ) (v : G3) : G3 :=
  ⟨v.s, v.c1, c * v.c2 - s * v.c3, s * v.c2 + c * v.c3, v.c12, v.c13, v.c23, v.c123⟩

theorem rotYZ_smul (c s k : ℝ) (v : G3) : rotYZ c s (smul k v) = smul k (rotYZ c s v) := by
  simp only [rotYZ, smul]; ext <;> ring

theorem rotYZ_sub (c s : ℝ) (u v : G3) : rotYZ c s (sub u v) = sub (rotYZ c s u) (rotYZ c s v) := by
  simp only [rotYZ, sub]; ext <;> ring

theorem rotYZ_preserves_dot (c s : ℝ) (hcs : c ^ 2 + s ^ 2 = 1) (u v : G3) :
    dot (rotYZ c s u) (rotYZ c s v) = dot u v := by
  simp only [dot, rotYZ, mul]
  linear_combination (u.c2 * v.c2 + u.c3 * v.c3) * hcs

/-- `rotXZ` distributes over subtraction (the `rotXZ` twin of the existing `rotXY_sub`; needed for the
    rejection's `rotXZ`-equivariance). -/
theorem rotXZ_sub (c s : ℝ) (u v : G3) : rotXZ c s (sub u v) = sub (rotXZ c s u) (rotXZ c s v) := by
  simp only [rotXZ, sub]; ext <;> ring

/-! ### A plane rotation of a vector is a vector (with transformed coordinates) -/

theorem rotXY_vec (c s x y z : ℝ) :
    rotXY c s (vec x y z) = vec (c * x - s * y) (s * x + c * y) z := by
  simp only [rotXY, vec]

theorem rotXZ_vec (c s x y z : ℝ) :
    rotXZ c s (vec x y z) = vec (c * x - s * z) y (s * x + c * z) := by
  simp only [rotXZ, vec]

theorem rotYZ_vec (c s x y z : ℝ) :
    rotYZ c s (vec x y z) = vec x (c * y - s * z) (s * y + c * z) := by
  simp only [rotYZ, vec]

/-- A plane rotation about `e₁` fixes a vector already on `e₁`. -/
theorem rotYZ_fixes_e1 (c s m : ℝ) : rotYZ c s (vec m 0 0) = vec m 0 0 := by
  simp only [rotYZ, vec]; ext <;> ring

/-! ### Projection and rejection are equivariant under the third rotation too

    (`proj_rotXY_equivariant`/`proj_rotXZ_equivariant` and `vecReject_rotXY_equivariant` are in
    `StandardPosition.lean`; these complete the set so all three ops are equivariant under all three
    rotations — the uniform tool.) -/

theorem proj_rotYZ_equivariant (c s : ℝ) (hcs : c ^ 2 + s ^ 2 = 1) (a b : G3) :
    proj (rotYZ c s a) (rotYZ c s b) = rotYZ c s (proj a b) := by
  simp only [proj, rotYZ_smul]
  rw [rotYZ_preserves_dot c s hcs b a, rotYZ_preserves_dot c s hcs a a]

theorem vecReject_rotXZ_equivariant (c s : ℝ) (hcs : c ^ 2 + s ^ 2 = 1) (a b : G3) :
    vecReject (rotXZ c s a) (rotXZ c s b) = rotXZ c s (vecReject a b) := by
  simp only [vecReject]
  rw [rotXZ_sub, proj_rotXZ_equivariant c s hcs a b]

theorem vecReject_rotYZ_equivariant (c s : ℝ) (hcs : c ^ 2 + s ^ 2 = 1) (a b : G3) :
    vecReject (rotYZ c s a) (rotYZ c s b) = rotYZ c s (vecReject a b) := by
  simp only [vecReject]
  rw [rotYZ_sub, proj_rotYZ_equivariant c s hcs a b]

/-! ### `cross` is equivariant under each elementary plane rotation (for `cos²(θ) + sin²(θ) = 1`)

    The cross product transforms as a (pseudo)vector under a proper rotation. Each is a coordinate
    identity: unfold to `vec` form via the `*_vec` lemmas, then `ring` on the components the rotation
    leaves alone and one `cos²(θ) + sin²(θ) = 1` step on the component the rotation acts in (the cross-component
    of the rotation's fixed axis). -/

theorem cross_rotXY_equivariant {a b : G3} (ha : IsVector a) (hb : IsVector b) (c s : ℝ)
    (hcs : c ^ 2 + s ^ 2 = 1) :
    cross (rotXY c s a) (rotXY c s b) = rotXY c s (cross a b) := by
  rw [eq_vec_of_isVector ha, eq_vec_of_isVector hb]
  simp only [rotXY_vec, cross_vec]
  simp only [vec]
  ext
  · ring
  · ring
  · ring
  · linear_combination (a.c1 * b.c2 - a.c2 * b.c1) * hcs
  · ring
  · ring
  · ring
  · ring

theorem cross_rotXZ_equivariant {a b : G3} (ha : IsVector a) (hb : IsVector b) (c s : ℝ)
    (hcs : c ^ 2 + s ^ 2 = 1) :
    cross (rotXZ c s a) (rotXZ c s b) = rotXZ c s (cross a b) := by
  rw [eq_vec_of_isVector ha, eq_vec_of_isVector hb]
  simp only [rotXZ_vec, cross_vec]
  simp only [vec]
  ext
  · ring
  · ring
  · linear_combination (a.c3 * b.c1 - a.c1 * b.c3) * hcs
  · ring
  · ring
  · ring
  · ring
  · ring

theorem cross_rotYZ_equivariant {a b : G3} (ha : IsVector a) (hb : IsVector b) (c s : ℝ)
    (hcs : c ^ 2 + s ^ 2 = 1) :
    cross (rotYZ c s a) (rotYZ c s b) = rotYZ c s (cross a b) := by
  rw [eq_vec_of_isVector ha, eq_vec_of_isVector hb]
  simp only [rotYZ_vec, cross_vec]
  simp only [vec]
  ext
  · ring
  · linear_combination (a.c2 * b.c3 - a.c3 * b.c2) * hcs
  · ring
  · ring
  · ring
  · ring
  · ring
  · ring

/-! ### The 3rd rotation: swing `b` into the e₁*e₂ plane -/

/-- `rotYZ (b₂/k) (−b₃/k)` sends `(b₁, b₂, b₃)` to `(b₁, k, 0)` — `b`'s yz-part swung onto `e₂`, so `b`
    lands in the `e₁*e₂` plane. `k = √(b₂²+b₃²)` (`k ≠ 0`, `k² = b₂²+b₃²`). The analog of
    `rotXY_aligns_xy` for the final reduction. -/
theorem rotYZ_aligns_yz (b1 b2 b3 k : ℝ) (hk : k ≠ 0) (hk2 : k ^ 2 = b2 ^ 2 + b3 ^ 2) :
    rotYZ (b2 / k) (-b3 / k) (vec b1 b2 b3) = vec b1 k 0 := by
  simp only [rotYZ, vec]
  ext
  · rfl
  · rfl
  · field_simp; linear_combination -hk2
  · field_simp; ring
  · rfl
  · rfl
  · rfl
  · rfl

/-! ### The general 3-rotation reduction to the e₁*e₂ plane -/

/-- The full reduction: compose the two rotations that put `a` on `e₁` (`rotXZ ∘ rotXY`, as in
    `StandardPosition.rotate_b_to_e1`) with the `rotYZ` that swings `b` into the `e₁*e₂` plane. -/
noncomputable def reduceToPlane (cx sx cz sz cy sy : ℝ) (v : G3) : G3 :=
  rotYZ cy sy (rotXZ cz sz (rotXY cx sx v))

/-- **`a` lands on `e₁`:** the full reduction sends `a` to `|a|*e₁` — the first two rotations put it on
    `e₁` (`rotate_b_to_e1_magnitude`), and the third (`rotYZ`, about `e₁`) fixes it. The `(cos,sin)` of
    the first two are read off `a`; `cy`,`sy` are arbitrary (they do not move an `e₁` vector). -/
theorem reduceToPlane_a_on_e1 (a1 a2 a3 cy sy : ℝ)
    (hk : magnitude (vec a1 a2 0) ≠ 0) (hm : magnitude (vec a1 a2 a3) ≠ 0) :
    reduceToPlane (a1 / magnitude (vec a1 a2 0)) (-a2 / magnitude (vec a1 a2 0))
        (magnitude (vec a1 a2 0) / magnitude (vec a1 a2 a3)) (-a3 / magnitude (vec a1 a2 a3))
        cy sy (vec a1 a2 a3)
      = smul (magnitude (vec a1 a2 a3)) (vec 1 0 0) := by
  simp only [reduceToPlane]
  rw [rotate_b_to_e1_magnitude a1 a2 a3 hk hm]
  simp only [rotYZ, smul, vec]; ext <;> ring

/-- **`b` lands in the `e₁*e₂` plane:** after the two `a`-rotations carry `b` to some `(P,Q,R)`, the
    third rotation `rotYZ (Q/j) (−R/j)` (`j = √(Q²+R²)`) zeroes its `e₃` component. So `b`'s reduced
    `e₃` coordinate is `0` — it lies in the plane. `(cx,sx,cz,sz)` are the `a`-rotation `(cos,sin)`. -/
theorem reduceToPlane_b_in_plane (cx sx cz sz b1 b2 b3 j : ℝ) (hj : j ≠ 0)
    (hj2 : j ^ 2 = (sx * b1 + cx * b2) ^ 2 + (sz * (cx * b1 - sx * b2) + cz * b3) ^ 2) :
    (reduceToPlane cx sx cz sz
        ((sx * b1 + cx * b2) / j) (-(sz * (cx * b1 - sx * b2) + cz * b3) / j)
        (vec b1 b2 b3)).c3 = 0 := by
  simp only [reduceToPlane, rotXY_vec, rotXZ_vec]
  rw [rotYZ_aligns_yz (cz * (cx * b1 - sx * b2) - sz * b3) (sx * b1 + cx * b2)
        (sz * (cx * b1 - sx * b2) + cz * b3) j hj hj2]
  simp only [vec]

/-! ### The elementary 2-D operations in the reduced frame (`a` on `e₁`, `b` in the plane)

    With `a = (m,0,0)` and `b = (b₁,b₂,0)`, each operation is elementary — computed from the canonical
    definitions. Combined with the equivariance lemmas above (the operation commutes with every plane
    rotation of the reduction), this is "reduce both to the plane, do the easy 2-D operation, rotate
    back," uniformly for all three. -/

/-- **Projection in the reduced frame:** `proj_a b = (b₁,0,0)` — `b`'s component along `a = e₁`. -/
theorem proj_reduced (m b1 b2 : ℝ) (hm : m ≠ 0) :
    proj (vec m 0 0) (vec b1 b2 0) = vec b1 0 0 := by
  simp only [proj, dot, mul, smul, vec]
  ext <;> field_simp [hm] <;> ring

/-- **Rejection in the reduced frame:** `b − proj_a b = (0,b₂,0)` — `b`'s perpendicular component.
    (`vecReject = b − proj_a b` equals the canonical Hestenes `reject` for vectors, `reject_vec_eq`.) -/
theorem vecReject_reduced (m b1 b2 : ℝ) (hm : m ≠ 0) :
    vecReject (vec m 0 0) (vec b1 b2 0) = vec 0 b2 0 := by
  simp only [vecReject]
  rw [proj_reduced m b1 b2 hm]
  simp only [sub, vec]; ext <;> ring

/-- **Cross product in the reduced frame:** `a × b = (0,0,m·b₂)` — a pure `e₃` vector, `a`'s
    axis-length times `b`'s in-plane height. Immediate from `cross_vec`. -/
theorem cross_reduced (m b1 b2 : ℝ) : cross (vec m 0 0) (vec b1 b2 0) = vec 0 0 (m * b2) := by
  rw [cross_vec]; ext <;> ring

/-! ### The cross-via-reduction capstone: cross = reduce → cross-in-frame → rotate back

    Assembles the step-lemmas above into the statement that the canonical cross product is
    recovered by reducing both vectors to the `e₁*e₂` plane, crossing there (a pure `e₃` vector),
    and rotating back — closing the cross arc the way `StandardPosition.projectSP_eq_proj` caps the
    project/reject arc. The stated form is over vector OBJECTS (`IsVector`); the reduction angles are
    introduced inside via `reduceToPlane`, exactly as `projectSP_eq_proj` hides its angles in
    `alignSP`. -/

/-- A plane rotation about the fixed `e₁` axis is invertible: negate the sine and reapply. The
    `rotYZ` twin of `StandardPosition.rotXY_inv`/`rotXZ_inv`. -/
theorem rotYZ_inv (c s s' : ℝ) (hcs : c ^ 2 + s ^ 2 = 1) (h : s' + s = 0) (v : G3) :
    rotYZ c s' (rotYZ c s v) = v := by
  ext
  · rfl
  · rfl
  · show c * (c * v.c2 - s * v.c3) - s' * (s * v.c2 + c * v.c3) = v.c2
    linear_combination v.c2 * hcs - (s * v.c2 + c * v.c3) * h
  · show s' * (c * v.c2 - s * v.c3) + c * (s * v.c2 + c * v.c3) = v.c3
    linear_combination v.c3 * hcs + (c * v.c2 - s * v.c3) * h
  · rfl
  · rfl
  · rfl
  · rfl

/-! A plane rotation sends a vector to a vector (needed to chain the object-form equivariance
    lemmas through the composed reduction). -/

theorem isVector_rotXY {v : G3} (hv : IsVector v) (c s : ℝ) : IsVector (rotXY c s v) := by
  rw [eq_vec_of_isVector hv, rotXY_vec]; exact isVector_vec _ _ _

theorem isVector_rotXZ {v : G3} (hv : IsVector v) (c s : ℝ) : IsVector (rotXZ c s v) := by
  rw [eq_vec_of_isVector hv, rotXZ_vec]; exact isVector_vec _ _ _

theorem isVector_rotYZ {v : G3} (hv : IsVector v) (c s : ℝ) : IsVector (rotYZ c s v) := by
  rw [eq_vec_of_isVector hv, rotYZ_vec]; exact isVector_vec _ _ _

/-- **`cross` commutes with the full 3-rotation reduction** (for unit angle pairs) — the engine
    behind "reduce, cross, rotate back." Three applications of the elementary cross-equivariance
    (outermost rotation first), chaining through the vector-preservation helpers. -/
theorem cross_reduceToPlane_equivariant {a b : G3} (ha : IsVector a) (hb : IsVector b)
    (cx sx cz sz cy sy : ℝ) (hx : cx ^ 2 + sx ^ 2 = 1) (hz : cz ^ 2 + sz ^ 2 = 1)
    (hy : cy ^ 2 + sy ^ 2 = 1) :
    cross (reduceToPlane cx sx cz sz cy sy a) (reduceToPlane cx sx cz sz cy sy b)
      = reduceToPlane cx sx cz sz cy sy (cross a b) := by
  simp only [reduceToPlane]
  rw [cross_rotYZ_equivariant (isVector_rotXZ (isVector_rotXY ha cx sx) cz sz)
        (isVector_rotXZ (isVector_rotXY hb cx sx) cz sz) cy sy hy,
      cross_rotXZ_equivariant (isVector_rotXY ha cx sx) (isVector_rotXY hb cx sx) cz sz hz,
      cross_rotXY_equivariant ha hb cx sx hx]

/-- **Rotate back** the full reduction: negate each sine, apply the three inverse rotations in the
    reverse order (the `reduceToPlane` twin of `StandardPosition.unalignSP`). -/
noncomputable def unreduceToPlane (cx sx cz sz cy sy : ℝ) (w : G3) : G3 :=
  rotXY cx (-sx) (rotXZ cz (-sz) (rotYZ cy (-sy) w))

/-- Rotating back undoes the reduction (for unit angle pairs) — the three `rot*_inv` lemmas in
    reverse order. -/
theorem unreduceToPlane_reduceToPlane (cx sx cz sz cy sy : ℝ)
    (hx : cx ^ 2 + sx ^ 2 = 1) (hz : cz ^ 2 + sz ^ 2 = 1) (hy : cy ^ 2 + sy ^ 2 = 1) (v : G3) :
    unreduceToPlane cx sx cz sz cy sy (reduceToPlane cx sx cz sz cy sy v) = v := by
  simp only [unreduceToPlane, reduceToPlane]
  rw [rotYZ_inv cy sy (-sy) hy (by ring), rotXZ_inv cz sz (-sz) hz (by ring),
      rotXY_inv cx sx (-sx) hx (by ring)]

/-- **Cross via reduction equals the canonical cross** (round-trip form, any unit angle pairs):
    reducing both vectors to the `e₁*e₂` plane, crossing there, and rotating back recovers `cross a b`.
    This is the "both routes agree" payoff — the projection-formula sibling is
    `ProjectionRotation3D.projRotation_eq_sandwich`. Pure assembly: `cross` commutes with the
    reduction (`cross_reduceToPlane_equivariant`, i.e. the three elementary equivariances) and the
    reduction is invertible (`unreduceToPlane_reduceToPlane`). -/
theorem cross_eq_unreduce_cross_reduce {a b : G3} (ha : IsVector a) (hb : IsVector b)
    (cx sx cz sz cy sy : ℝ) (hx : cx ^ 2 + sx ^ 2 = 1) (hz : cz ^ 2 + sz ^ 2 = 1)
    (hy : cy ^ 2 + sy ^ 2 = 1) :
    cross a b = unreduceToPlane cx sx cz sz cy sy
        (cross (reduceToPlane cx sx cz sz cy sy a) (reduceToPlane cx sx cz sz cy sy b)) := by
  rw [cross_reduceToPlane_equivariant ha hb cx sx cz sz cy sy hx hz hy,
      unreduceToPlane_reduceToPlane cx sx cz sz cy sy hx hz hy]

/-- **The cross capstone (standard-position form).** Given a reduction (unit angle pairs) that puts
    `a` on `e₁` (`ha_on_e1`) and lands `b` in the `e₁*e₂` plane (`hb_c3 : reduced b's e₃ = 0`), the
    cross product is recovered by crossing in that frame — where it is the pure-`e₃` vector
    `(0, 0, |a| * (reduced b).e₂)` (`cross_reduced`) — and rotating back
    (`cross_eq_unreduce_cross_reduce`). This is the cross analogue of
    `StandardPosition.projectSP_eq_proj`: stated over vector objects, with the angles supplied as the
    reduction that standardizes `a` and `b`. `cross_via_reduction_of_vectors` discharges `ha_on_e1`/
    `hb_c3` from the explicit reduction angles via `reduceToPlane_a_on_e1`/`reduceToPlane_b_in_plane`. -/
theorem cross_via_reduction {a b : G3} (hav : IsVector a) (hbv : IsVector b)
    (cx sx cz sz cy sy : ℝ) (hx : cx ^ 2 + sx ^ 2 = 1) (hz : cz ^ 2 + sz ^ 2 = 1)
    (hy : cy ^ 2 + sy ^ 2 = 1)
    (ha_on_e1 : reduceToPlane cx sx cz sz cy sy a = vec (magnitude a) 0 0)
    (hb_c3 : (reduceToPlane cx sx cz sz cy sy b).c3 = 0) :
    cross a b = unreduceToPlane cx sx cz sz cy sy
        (vec 0 0 (magnitude a * (reduceToPlane cx sx cz sz cy sy b).c2)) := by
  rw [cross_eq_unreduce_cross_reduce hav hbv cx sx cz sz cy sy hx hz hy]
  congr 1
  rw [ha_on_e1]
  have hb_vec : IsVector (reduceToPlane cx sx cz sz cy sy b) :=
    isVector_rotYZ (isVector_rotXZ (isVector_rotXY hbv cx sx) cz sz) cy sy
  have hbform : reduceToPlane cx sx cz sz cy sy b
      = vec (reduceToPlane cx sx cz sz cy sy b).c1 (reduceToPlane cx sx cz sz cy sy b).c2 0 := by
    conv_lhs => rw [eq_vec_of_isVector hb_vec]
    rw [hb_c3]
  conv_lhs => rw [hbform]
  rw [cross_reduced]

/-- **The cross capstone over explicit vectors** — `cross_via_reduction` with the reduction angles
    that actually standardize `a` and `b`, so it cites the placement lemmas `reduceToPlane_a_on_e1`
    (sends `a` to `|a|*e₁`) and `reduceToPlane_b_in_plane` (lands `b` in the `e₁*e₂` plane). The
    reduction `(cos, sin)` are read off `a`'s coordinates (align `a` to `e₁`) plus the swing that
    puts `b` in the plane; `hk` = `a` off the z-axis, `hm` = `a` nonzero, `j` = `b`'s reduced
    in-plane height with `hj`/`hj2` (so `b` is not aligned with `a`). This is the fully-assembled
    "reduce → cross-in-frame → rotate back = canonical cross" for the cross arc. -/
theorem cross_via_reduction_of_vectors (a1 a2 a3 b1 b2 b3 j : ℝ)
    (hk : magnitude (vec a1 a2 0) ≠ 0) (hm : magnitude (vec a1 a2 a3) ≠ 0) (hj : j ≠ 0)
    (hj2 : j ^ 2 =
       (-a2 / magnitude (vec a1 a2 0) * b1 + a1 / magnitude (vec a1 a2 0) * b2) ^ 2 +
       (-a3 / magnitude (vec a1 a2 a3) *
            (a1 / magnitude (vec a1 a2 0) * b1 - -a2 / magnitude (vec a1 a2 0) * b2) +
          magnitude (vec a1 a2 0) / magnitude (vec a1 a2 a3) * b3) ^ 2) :
    cross (vec a1 a2 a3) (vec b1 b2 b3)
      = unreduceToPlane (a1 / magnitude (vec a1 a2 0)) (-a2 / magnitude (vec a1 a2 0))
          (magnitude (vec a1 a2 0) / magnitude (vec a1 a2 a3)) (-a3 / magnitude (vec a1 a2 a3))
          ((-a2 / magnitude (vec a1 a2 0) * b1 + a1 / magnitude (vec a1 a2 0) * b2) / j)
          (-(-a3 / magnitude (vec a1 a2 a3) *
                (a1 / magnitude (vec a1 a2 0) * b1 - -a2 / magnitude (vec a1 a2 0) * b2) +
              magnitude (vec a1 a2 0) / magnitude (vec a1 a2 a3) * b3) / j)
          (vec 0 0 (magnitude (vec a1 a2 a3) *
             (reduceToPlane (a1 / magnitude (vec a1 a2 0)) (-a2 / magnitude (vec a1 a2 0))
                (magnitude (vec a1 a2 0) / magnitude (vec a1 a2 a3)) (-a3 / magnitude (vec a1 a2 a3))
                ((-a2 / magnitude (vec a1 a2 0) * b1 + a1 / magnitude (vec a1 a2 0) * b2) / j)
                (-(-a3 / magnitude (vec a1 a2 a3) *
                      (a1 / magnitude (vec a1 a2 0) * b1 - -a2 / magnitude (vec a1 a2 0) * b2) +
                    magnitude (vec a1 a2 0) / magnitude (vec a1 a2 a3) * b3) / j)
                (vec b1 b2 b3)).c2)) := by
  have hkpos : magnitude (vec a1 a2 0) ^ 2 = a1 ^ 2 + a2 ^ 2 := by rw [magnitude_sq_vec]; ring
  have hmpos : magnitude (vec a1 a2 a3) ^ 2 = a1 ^ 2 + a2 ^ 2 + a3 ^ 2 := by rw [magnitude_sq_vec]
  have hx : (a1 / magnitude (vec a1 a2 0)) ^ 2 + (-a2 / magnitude (vec a1 a2 0)) ^ 2 = 1 := by
    rw [div_pow, div_pow, neg_sq, ← add_div, ← hkpos]; exact div_self (pow_ne_zero 2 hk)
  have hz : (magnitude (vec a1 a2 0) / magnitude (vec a1 a2 a3)) ^ 2
        + (-a3 / magnitude (vec a1 a2 a3)) ^ 2 = 1 := by
    rw [div_pow, div_pow, neg_sq, ← add_div, hkpos, ← hmpos]; exact div_self (pow_ne_zero 2 hm)
  have hy : ((-a2 / magnitude (vec a1 a2 0) * b1 + a1 / magnitude (vec a1 a2 0) * b2) / j) ^ 2
        + (-(-a3 / magnitude (vec a1 a2 a3) *
                (a1 / magnitude (vec a1 a2 0) * b1 - -a2 / magnitude (vec a1 a2 0) * b2) +
              magnitude (vec a1 a2 0) / magnitude (vec a1 a2 a3) * b3) / j) ^ 2 = 1 := by
    rw [div_pow, div_pow, neg_sq, ← add_div, ← hj2]; exact div_self (pow_ne_zero 2 hj)
  have ha_on_e1 : reduceToPlane (a1 / magnitude (vec a1 a2 0)) (-a2 / magnitude (vec a1 a2 0))
        (magnitude (vec a1 a2 0) / magnitude (vec a1 a2 a3)) (-a3 / magnitude (vec a1 a2 a3))
        ((-a2 / magnitude (vec a1 a2 0) * b1 + a1 / magnitude (vec a1 a2 0) * b2) / j)
        (-(-a3 / magnitude (vec a1 a2 a3) *
              (a1 / magnitude (vec a1 a2 0) * b1 - -a2 / magnitude (vec a1 a2 0) * b2) +
            magnitude (vec a1 a2 0) / magnitude (vec a1 a2 a3) * b3) / j)
        (vec a1 a2 a3)
      = vec (magnitude (vec a1 a2 a3)) 0 0 := by
    rw [reduceToPlane_a_on_e1 a1 a2 a3 _ _ hk hm]; simp only [smul, vec]; ext <;> ring
  have hb_c3 := reduceToPlane_b_in_plane (a1 / magnitude (vec a1 a2 0))
      (-a2 / magnitude (vec a1 a2 0)) (magnitude (vec a1 a2 0) / magnitude (vec a1 a2 a3))
      (-a3 / magnitude (vec a1 a2 a3)) b1 b2 b3 j hj hj2
  exact cross_via_reduction (isVector_vec a1 a2 a3) (isVector_vec b1 b2 b3)
    (a1 / magnitude (vec a1 a2 0)) (-a2 / magnitude (vec a1 a2 0))
    (magnitude (vec a1 a2 0) / magnitude (vec a1 a2 a3)) (-a3 / magnitude (vec a1 a2 a3))
    ((-a2 / magnitude (vec a1 a2 0) * b1 + a1 / magnitude (vec a1 a2 0) * b2) / j)
    (-(-a3 / magnitude (vec a1 a2 a3) *
          (a1 / magnitude (vec a1 a2 0) * b1 - -a2 / magnitude (vec a1 a2 0) * b2) +
        magnitude (vec a1 a2 0) / magnitude (vec a1 a2 a3) * b3) / j)
    hx hz hy ha_on_e1 hb_c3

end GacalcProofs.G3
