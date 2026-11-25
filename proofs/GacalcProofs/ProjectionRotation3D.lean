import GacalcProofs.G3
import GacalcProofs.G2
import GacalcProofs.Projection3D
import GacalcProofs.Sandwich
import GacalcProofs.Rotation3D
import GacalcProofs.Trig

/-! # A general rotation defined from project/reject (𝒢₃)

    **Step 3 of the reduce-to-standard-position bootstrap arc**
    (`tasks/reference/reduction-to-standard-position.md`): a *general* rotation built from
    **projection / rejection** — which are themselves derived from the three elementary
    coordinate-plane rotations — so no versor / geometric-product sandwich is presupposed as the
    primitive. This mirrors gacalc's `transforms.projection_rotation` (`src/gacalc/transforms.py`):
    split `v` into its part in the `from ∧ to` plane and its perpendicular part, turn the in-plane
    part through the from→to angle by multiplying by the two unit vectors `from̂`, `tô`, and leave the
    perpendicular part fixed.

    It *does* use the geometric product (`mul`) — but in the arc the product is itself derived from
    project/reject, so this stays non-circular (the elementary plane rotations sit underneath). This is
    the projection-formula sibling of the versor sandwich `R*v*R⁻¹` (`Sandwich.lean`); the two routes to
    a general rotation agree (route P here vs route V there). -/
namespace GacalcProofs.G3

/-- Normalize a vector to unit length: `v̂ = (1/|v|)*v` (the 𝒢₃ twin of `ProjectionRotation2D.normalizeVec`). -/
noncomputable def normalizeVec (a : G3) : G3 := smul (1 / magnitude a) a

/-- **General rotation from projection/rejection** (mirrors `transforms.projection_rotation`):
    `projRotation f t v = (project_{f∧t} v) · f̂ · t̂ + reject_{f∧t} v` — turn the in-plane part of `v`
    through the from→to angle, leave the perpendicular part fixed. -/
noncomputable def projRotation (f t v : G3) : G3 :=
  add (mul (mul (project_onto (wedge f t) v) (normalizeVec f)) (normalizeVec t))
      (reject (wedge f t) v)

/-- A vector is `vec` of its coordinates, for substituting in a proof body that needs them. -/
theorem exists_vec {a : G3} (ha : IsVector a) : ∃ x y z : ℝ, a = vec x y z :=
  ⟨a.c1, a.c2, a.c3, eq_vec_of_isVector ha⟩

/-- The wedge of two vectors is a bivector (a plane). -/
theorem isBivector_wedge {f t : G3} (hf : IsVector f) (ht : IsVector t) : IsBivector (wedge f t) := by
  obtain ⟨a1, a2, a3, rfl⟩ := exists_vec hf
  obtain ⟨b1, b2, b3, rfl⟩ := exists_vec ht
  rw [wedge_vec_eq_biv]
  exact ⟨rfl, rfl, rfl, rfl, rfl⟩

/-- **A nondegenerate plane has a nonzero first vector:** `|f∧t|² ≠ 0` forces `|f|² ≠ 0`, because Lagrange's
    identity `(f·t)² + |f∧t|² = |f|²*|t|²` would otherwise leave `|f∧t|² = −(f·t)² ≤ 0`. -/
theorem normSq_ne_zero_of_wedge_left {f t : G3} (hf : IsVector f) (ht : IsVector t)
    (hpn : normSq (wedge f t) ≠ 0) : normSq f ≠ 0 := fun h0 => by
  have hl := lagrange_property hf ht
  rw [h0] at hl
  exact hpn (le_antisymm (by nlinarith [sq_nonneg (dot f t)]) (normSq_nonneg (wedge f t)))

/-- The same for the second vector of the plane. -/
theorem normSq_ne_zero_of_wedge_right {f t : G3} (hf : IsVector f) (ht : IsVector t)
    (hpn : normSq (wedge f t) ≠ 0) : normSq t ≠ 0 := fun h0 => by
  have hl := lagrange_property hf ht
  rw [h0] at hl
  exact hpn (le_antisymm (by nlinarith [sq_nonneg (dot f t)]) (normSq_nonneg (wedge f t)))

/-! ### `from` lies in the `from ∧ to` plane -/

/-- A vector wedged with a plane that contains it vanishes: `f ∧ (f ∧ t) = 0`. -/
theorem wedge_vec_wedge_self {f t : G3} (hf : IsVector f) (ht : IsVector t) :
    wedge f (wedge f t) = zero := by
  obtain ⟨a1, a2, a3, rfl⟩ := exists_vec hf
  obtain ⟨b1, b2, b3, rfl⟩ := exists_vec ht
  simp only [wedge, vec, zero]; ext <;> ring

/-- **The rejection of `f` from the `f∧t` plane is zero** — `f` lies in the plane. -/
theorem reject_in_plane_self {f t : G3} (hf : IsVector f) (ht : IsVector t) :
    reject (wedge f t) f = zero := by
  obtain ⟨a1, a2, a3, rfl⟩ := exists_vec hf
  obtain ⟨b1, b2, b3, rfl⟩ := exists_vec ht
  rw [reject, wedge_vec_wedge_self hf ht, zero_mul]

/-- `(f · (f∧t)) · reverse(f∧t) = |f∧t|²*f` — a polynomial identity: the in-plane projection
    numerator recovers `f` scaled by the plane's squared magnitude. -/
theorem inner_vb_mul_reverse_self {f t : G3} (hf : IsVector f) (ht : IsVector t) :
    mul (inner_vb f (wedge f t))
        (reverse (wedge f t))
      = smul (normSq (wedge f t)) f := by
  obtain ⟨a1, a2, a3, rfl⟩ := exists_vec hf
  obtain ⟨b1, b2, b3, rfl⟩ := exists_vec ht
  simp only [inner_vb, wedge, reverse, mul, smul, vec, normSq]
  ext <;> ring

/-- **The projection of `f` onto the `f∧t` plane is `f`** (for a nondegenerate plane `|f∧t|² ≠ 0`). -/
theorem project_onto_in_plane_self {f t : G3} (hf : IsVector f) (ht : IsVector t)
    (hn : normSq (wedge f t) ≠ 0) :
    project_onto (wedge f t) f = f := by
  obtain ⟨a1, a2, a3, rfl⟩ := exists_vec hf
  obtain ⟨b1, b2, b3, rfl⟩ := exists_vec ht
  simp only [project_onto, inverse]
  rw [GacalcProofs.G3.mul_smul, inner_vb_mul_reverse_self hf ht, GacalcProofs.G3.smul_smul,
      one_div_mul_cancel hn, GacalcProofs.G3.one_smul]

/-! ### Properties of the rotation -/

/-- **The perpendicular part passes through unchanged:** if `v` has no component in the plane
    (`project_{f∧t} v = 0`) then `projRotation f t v = reject_{f∧t} v` (the in-plane term is turned,
    the perpendicular term is left alone — here the in-plane term is zero). Combined with
    `project_add_reject` (`project + reject = v`), a fully-perpendicular `v` is fixed. -/
theorem projRotation_perp (f t v : G3) (h : project_onto (wedge f t) v = zero) :
    projRotation f t v = reject (wedge f t) v := by
  rw [projRotation, h, zero_mul, zero_mul, zero_add]

/-- **The rotation carries `from` to `to`:** `projRotation f t f = (|f|/|t|)*t` (so for unit `f`, `t`
    it sends `f ↦ t`). `f` is in the plane, so its perpendicular part vanishes and its in-plane part is
    `f` itself; then `f · f̂ · t̂ = |f|*t̂ = (|f|/|t|)*t`. The defining property of the rotation. For
    nonzero vectors `f`, `t` with a nondegenerate plane. -/
theorem projRotation_carries_from_to {f t : G3} (hf : IsVector f) (ht : IsVector t)
    (hpn : normSq (wedge f t) ≠ 0) :
    projRotation f t f = smul (magnitude f / magnitude t) t := by
  have hfn := normSq_ne_zero_of_wedge_left hf ht hpn
  have htn := normSq_ne_zero_of_wedge_right hf ht hpn
  rw [projRotation, project_onto_in_plane_self hf ht hpn, reject_in_plane_self hf ht, add_zero]
  simp only [normalizeVec, GacalcProofs.G3.mul_smul, GacalcProofs.G3.smul_mul,
    GacalcProofs.G3.smul_smul]
  rw [mul_vec_self hf, GacalcProofs.G3.scalar_mul, GacalcProofs.G3.smul_smul]
  congr 1
  have hmf := magnitude_ne_zero_of_normSq_ne_zero hfn
  have hmt := magnitude_ne_zero_of_normSq_ne_zero htn
  rw [← magnitude_sq_eq_normSq f]; field_simp

/-! ### Scaffold for the isometry (how the `√` obstruction dissolves)

    The in-plane term `(project_{f∧t} v) · f̂ · t̂` carries a factor `1/(|f|*|t|)`; a brute
    `field_simp; ring` stalls because `ring` cannot relate `magnitude f` to `normSq f`, and the
    in-plane×⊥ cross term keeps a bare `1/(|f|*|t|)` that only vanishes by orthogonality. The way
    through (no brute coordinates on the whole expression): pull the two unit scalars out of the
    in-plane term as one `smul (1/(|f|*|t|))`, so every `√` appears **squared** (`(1/|f|)² = 1/|f|²`,
    killed by `magnitude² = normSq`) or **cancels exactly** (the cross term's bare `1/(|f|*|t|)`
    multiplies a provably-zero orthogonality core). Then `normSq` splits by the four lemmas below. -/

/-- **Polarization in 𝒢₃:** `|x + y|² = |x|² + |y|² + 2⟨x ỹ⟩`, where `⟨x ỹ⟩ = (x·ȳ).s` is the
    symmetric bilinear form behind `normSq`. Pure `ring` over the sixteen coordinates. -/
theorem normSq_add (x y : G3) :
    normSq (add x y) = normSq x + normSq y + 2 * (mul x (reverse y)).s := by
  simp only [normSq, add, reverse, mul]; ring

/-- **Orthogonal Pythagoras:** if `⟨x ȳ⟩ = (x·ȳ).s = 0` then `|x + y|² = |x|² + |y|²`. The cross
    term in `normSq_add` drops. -/
theorem normSq_add_of_orthogonal (x y : G3) (h : (mul x (reverse y)).s = 0) :
    normSq (add x y) = normSq x + normSq y := by
  rw [normSq_add, h]; ring

/-- **A vector factor is multiplicative on `normSq`:** `|M a|² = |a|²*|M|²` for ANY multivector
    `M` and a vector `a` — because `a ã = a·a = |a|²` is a scalar that rides out of the sandwich
    `(Ma)(Ma)~ = M a a M̃ = |a|² M M̃`. Pure `ring`; this is where the two unit factors each turn a
    `1/|·|²` into the matching coordinate sum. -/
theorem normSq_mul_vec {M a : G3} (ha : IsVector a) :
    normSq (mul M a) = normSq a * normSq M := by
  obtain ⟨a1, a2, a3, rfl⟩ := exists_vec ha
  simp only [normSq, mul, reverse, vec]; ring

set_option maxHeartbeats 8000000 in
set_option maxRecDepth 8000 in
/-- **Orthogonality core (`√`-free):** the *un-normalized* rotated in-plane vector
    `(project_{f∧t} v) · f · t` is perpendicular to the rejection `reject_{f∧t} v` — their scalar
    product `⟨… reverse(reject)⟩` is `0`. All three of `project`, `f`, `t` lie in the `f∧t` plane,
    so their product is in-plane, hence ⊥ the (normal) rejection. A rational identity in the
    coordinates: `field_simp; ring`. The normalized version is this times `1/(|f|*|t|)`. -/
theorem inplane_perp_reject {f t v : G3} (hf : IsVector f) (ht : IsVector t) (hv : IsVector v)
    (hn : normSq (wedge f t) ≠ 0) :
    (mul (mul (mul (project_onto (wedge f t) v)
          f) t)
         (reverse (reject (wedge f t) v))).s = 0 := by
  obtain ⟨a1, a2, a3, rfl⟩ := exists_vec hf
  obtain ⟨b1, b2, b3, rfl⟩ := exists_vec ht
  obtain ⟨c1, c2, c3, rfl⟩ := exists_vec hv
  rw [wedge_vec_eq_biv] at hn ⊢
  have hd := normSq_biv (a1 * b2 - a2 * b1) (a1 * b3 - a3 * b1) (a2 * b3 - a3 * b2)
  rw [hd] at hn
  simp only [project_onto, reject, inner_vb, inverse, hd]
  simp only [wedge, mul, reverse, smul, vec, bivector, zero]
  field_simp [hn]
  ring

/-- **The projection and the rejection are orthogonal (`√`-free):** `⟨project_B v · reverse(reject_B v)⟩
    = 0` for a plane `B` — the in-plane and perpendicular components of `v` meet at a right angle. A
    rational identity in the coordinates (`field_simp; ring`). -/
theorem project_perp_reject {B v : G3} (hB : IsBivector B) (hv : IsVector v) (hn : normSq B ≠ 0) :
    (mul (project_onto B v) (reverse (reject B v))).s = 0 := by
  obtain ⟨p, q, r, rfl⟩ : ∃ p q r : ℝ, B = bivector p q r :=
    ⟨B.c12, B.c13, B.c23, eq_bivector_of_isBivector hB⟩
  obtain ⟨c1, c2, c3, rfl⟩ := exists_vec hv
  have hd := normSq_biv p q r
  rw [hd] at hn
  simp only [project_onto, reject, inner_vb, inverse, hd]
  simp only [mul, reverse, smul, wedge, vec, bivector, zero]
  field_simp [hn]
  ring

/-- **Plane Pythagoras:** `|project_B v|² + |reject_B v|² = |v|²` for a nondegenerate plane `B`. The
    in-plane and perpendicular parts split the squared length. Structural (no giant `simp`):
    `project + reject = v` (`project_add_reject`) and `project ⊥ reject` (`project_perp_reject`), so
    `normSq_add_of_orthogonal` splits `|v|²`. -/
theorem plane_pythagorean {B v : G3} (hB : IsBivector B) (hv : IsVector v) (hn : normSq B ≠ 0) :
    normSq (project_onto B v) + normSq (reject B v) = normSq v := by
  rw [← normSq_add_of_orthogonal _ _ (project_perp_reject hB hv hn),
    project_add_reject hB hn hv]

/-- **The rotation is an isometry:** `|projRotation f t v|² = |v|²` (for nonzero vectors `f`, `t`, a
    nondegenerate `f∧t` plane, and any vector `v`). The in-plane part is turned (length-preserving), the
    perpendicular part is fixed, so the squared length is unchanged. Assembled from the scaffold: pull the
    unit scalars out of the in-plane term (`hin`), split `normSq` across the ⊥ decomposition
    (`normSq_add_of_orthogonal` + `inplane_perp_reject`), reduce the in-plane norm to `|project|²`
    (`normSq_mul_vec` twice, `magnitude² = normSq` cancelling the `1/(|f|*|t|)²`), then close with
    `plane_pythagorean`. No `√` survives. -/
theorem projRotation_isometry {f t v : G3} (hf : IsVector f) (ht : IsVector t) (hv : IsVector v)
    (hpn : normSq (wedge f t) ≠ 0) :
    normSq (projRotation f t v) = normSq v := by
  have hfn := normSq_ne_zero_of_wedge_left hf ht hpn
  have htn := normSq_ne_zero_of_wedge_right hf ht hpn
  have hmf := magnitude_ne_zero_of_normSq_ne_zero hfn
  have hmt := magnitude_ne_zero_of_normSq_ne_zero htn
  rw [projRotation]
  set P := project_onto (wedge f t) v with hP
  set Rj := reject (wedge f t) v with hRj
  -- Pull the two unit factors' scalars out of the in-plane term.
  have hin : mul (mul P (normalizeVec f)) (normalizeVec t)
      = smul (1 / magnitude t * (1 / magnitude f)) (mul (mul P f) t) := by
    simp only [normalizeVec, GacalcProofs.G3.mul_smul, GacalcProofs.G3.smul_mul,
      GacalcProofs.G3.smul_smul]
  -- The in-plane term ⊥ the rejection (normalized core = scalar · un-normalized core = scalar · 0).
  have horth : (mul (mul (mul P (normalizeVec f)) (normalizeVec t)) (reverse Rj)).s = 0 := by
    rw [hin, GacalcProofs.G3.smul_mul]
    simp only [smul]
    rw [hP, hRj, inplane_perp_reject hf ht hv hpn]
    ring
  -- The in-plane norm collapses to `|project|²` once the `1/(|f|*|t|)²` meets `magnitude² = normSq`.
  have hcoef : (1 / magnitude t * (1 / magnitude f)) ^ 2 * (normSq t * (normSq f * normSq P))
      = normSq P := by
    rw [← magnitude_sq_eq_normSq f, ← magnitude_sq_eq_normSq t]; field_simp
  rw [normSq_add_of_orthogonal _ _ horth, hin, normSq_smul, normSq_mul_vec ht, normSq_mul_vec hf,
    hcoef, hP, hRj]
  exact plane_pythagorean (isBivector_wedge hf ht) hv hpn

/-! ### Route-equivalence: the projection route equals the versor sandwich (route P = route V)

    The payoff — the two general-rotation constructions agree:
    `projRotation f t v = sandwich (versorFromVectors f t) v`. The structural key is that the
    *scalar* part `|f|*|t|*1` of `R = versorFromVectors f t = t*f + |f|*|t|` commutes with everything,
    so every identity below reduces to a `√`-free rational core about the bivector part `t∧f`:

      * **In-plane vectors anticommute through `R`** → `R w = w R̃` (so the double-sided sandwich
        collapses to a one-sided product).
      * **The perpendicular (reject) part commutes with `R`** → `R Rⱼ = Rⱼ R` (so the sandwich fixes
        it, `R Rⱼ R⁻¹ = Rⱼ`).
      * **`f̂ t̂ = R̃*R⁻¹`**, assembled from the bisector identities `t̂ R = h` and `f̂ h = R̃`
        (`Rotation3D.lean`), with no coordinate `√` ever expanded.

    The irreducible `√(|f|*|t|)` that defeats a brute coordinate attack never appears because it rides
    the scalar `1`, which is pulled out abstractly via `R*R⁻¹ = 1` rather than expanded. -/

/-- **The normalized to-vector times the versor is the half-angle bisector:** `t̂ R = h`. From
    `t R = |t|*h` (`from_mul_versor_eq_bisector`), scaled by `1/|t|`. -/
theorem normalizeVec_to_mul_versor_eq_bisector {f t : G3} (ht : IsVector t)
    (htn : magnitude t ≠ 0) :
    mul (normalizeVec t) (versorFromVectors f t) = bisector f t := by
  rw [normalizeVec, GacalcProofs.G3.smul_mul, from_mul_versor_eq_bisector ht,
      GacalcProofs.G3.smul_smul, one_div_mul_cancel htn, GacalcProofs.G3.one_smul]

/-- **The from-vector times the bisector is the (scaled) reverse versor:** `f h = |f|*R̃`. The
    division-free companion to `f̂ h = R̃`. The only analytic fact is `|f|² = f·f` (`magnitude_sq_vec`),
    used on the single scalar component; every other component is pure `ring`. Mirrors
    `versor_mul_from_eq_bisector`. -/
theorem vec_mul_bisector_eq {f t : G3} (hf : IsVector f) (ht : IsVector t) :
    mul f (bisector f t)
      = smul (magnitude f)
             (reverse (versorFromVectors f t)) := by
  obtain ⟨a1, a2, a3, rfl⟩ := exists_vec hf
  obtain ⟨b1, b2, b3, rfl⟩ := exists_vec ht
  simp only [bisector, versorFromVectors, reverse]
  set sa := magnitude (vec a1 a2 a3)
  set sb := magnitude (vec b1 b2 b3)
  have hsa : sa ^ 2 = a1 ^ 2 + a2 ^ 2 + a3 ^ 2 := magnitude_sq_vec a1 a2 a3
  clear_value sa sb
  simp only [mul, add, smul, one, vec]
  -- Every component is pure `ring` except the scalar, which needs `|f|² = f·f` (`hsa`).
  ext <;> try ring_nf
  linear_combination -sb * hsa

/-- **`f̂ t̂ R = R̃`** — the key alignment identity: the product of the two unit vectors, times the
    versor, is the reverse versor. Assembled from `t̂ R = h` and `f̂ h = R̃` (via `f h = |f|*R̃`), with
    the `1/|f|`, `1/|t|` cancelling against the bisector scalings — no coordinate `√` expanded. -/
theorem normalizeVec_mul_versor_eq_reverse {f t : G3} (hf : IsVector f) (ht : IsVector t)
    (hfn : magnitude f ≠ 0) (htn : magnitude t ≠ 0) :
    mul (mul (normalizeVec f) (normalizeVec t)) (versorFromVectors f t)
      = reverse (versorFromVectors f t) := by
  rw [GacalcProofs.G3.mul_assoc, normalizeVec_to_mul_versor_eq_bisector ht htn,
      normalizeVec, GacalcProofs.G3.smul_mul, vec_mul_bisector_eq hf ht,
      GacalcProofs.G3.smul_smul, one_div_mul_cancel hfn, GacalcProofs.G3.one_smul]

set_option maxHeartbeats 8000000 in
set_option maxRecDepth 8000 in
/-- **In-plane vectors anticommute through the versor:** `R P = P R̃` for `P = project_{f∧t} v` (in the
    `f∧t` plane). The scalar part `|f|*|t|*1` of `R` commutes trivially; the bivector part `t∧f`
    anticommutes with the in-plane `P` — so the identity has NO `√` (both sides carry the same
    `|f|*|t|*P` term, which cancels), reducing to a rational core (`field_simp; ring`). -/
theorem versor_mul_project_eq {f t v : G3} (hf : IsVector f) (ht : IsVector t) (hv : IsVector v)
    (hn : normSq (wedge f t) ≠ 0) :
    mul (versorFromVectors f t)
        (project_onto (wedge f t) v)
      = mul (project_onto (wedge f t) v)
            (reverse (versorFromVectors f t)) := by
  obtain ⟨a1, a2, a3, rfl⟩ := exists_vec hf
  obtain ⟨b1, b2, b3, rfl⟩ := exists_vec ht
  obtain ⟨c1, c2, c3, rfl⟩ := exists_vec hv
  rw [wedge_vec_eq_biv] at hn ⊢
  have hd := normSq_biv (a1 * b2 - a2 * b1) (a1 * b3 - a3 * b1) (a2 * b3 - a3 * b2)
  rw [hd] at hn
  simp only [versorFromVectors, project_onto, inner_vb, inverse, mul, reverse, add,
    smul, one, vec, bivector, zero]
  ext <;> field_simp [hn] <;> ring

set_option maxHeartbeats 8000000 in
set_option maxRecDepth 8000 in
/-- **The perpendicular (reject) part commutes with the versor:** `R Rⱼ = Rⱼ R` for
    `Rⱼ = reject_{f∧t} v` (⊥ the plane). The scalar part of `R` commutes trivially; the bivector part
    `t∧f` commutes with the normal `Rⱼ` (a vector ⊥ the plane commutes with the plane bivector) — again
    `√`-free (`field_simp; ring`). -/
theorem versor_mul_reject_comm {f t v : G3} (hf : IsVector f) (ht : IsVector t) (hv : IsVector v)
    (hn : normSq (wedge f t) ≠ 0) :
    mul (versorFromVectors f t)
        (reject (wedge f t) v)
      = mul (reject (wedge f t) v)
            (versorFromVectors f t) := by
  obtain ⟨a1, a2, a3, rfl⟩ := exists_vec hf
  obtain ⟨b1, b2, b3, rfl⟩ := exists_vec ht
  obtain ⟨c1, c2, c3, rfl⟩ := exists_vec hv
  rw [wedge_vec_eq_biv] at hn ⊢
  have hd := normSq_biv (a1 * b2 - a2 * b1) (a1 * b3 - a3 * b1) (a2 * b3 - a3 * b2)
  rw [hd] at hn
  simp only [versorFromVectors, reject, inverse, wedge, mul, reverse, add, smul, one, vec,
    bivector, zero]
  ext <;> field_simp [hn] <;> ring

/-- **`f̂ t̂ = R̃*R⁻¹`:** the one-sided unit-vector product equals the reverse-times-inverse of the
    versor, from `f̂ t̂ R = R̃` and `R*R⁻¹ = 1`. -/
theorem fhat_that_eq_reverse_mul_inverse {f t : G3} (hf : IsVector f) (ht : IsVector t)
    (hfn : normSq f ≠ 0) (htn : normSq t ≠ 0) (hr : normSq (versorFromVectors f t) ≠ 0) :
    mul (normalizeVec f) (normalizeVec t)
      = mul (reverse (versorFromVectors f t)) (inverse (versorFromVectors f t)) := by
  have hA := normalizeVec_mul_versor_eq_reverse hf ht (magnitude_ne_zero_of_normSq_ne_zero hfn)
    (magnitude_ne_zero_of_normSq_ne_zero htn)
  calc mul (normalizeVec f) (normalizeVec t)
      = mul (mul (normalizeVec f) (normalizeVec t))
            (mul (versorFromVectors f t) (inverse (versorFromVectors f t))) := by
          rw [mul_inverse_self_of_isEvenVersor (isEvenVersor_versorFromVectors hf ht) hr,
            GacalcProofs.G3.mul_one]
    _ = mul (mul (mul (normalizeVec f) (normalizeVec t)) (versorFromVectors f t))
            (inverse (versorFromVectors f t)) := (GacalcProofs.G3.mul_assoc _ _ _).symm
    _ = mul (reverse (versorFromVectors f t)) (inverse (versorFromVectors f t)) := by rw [hA]

/-- **Route-equivalence (route P = route V):** the projection-formula rotation equals the versor
    sandwich, `projRotation f t v = sandwich (versorFromVectors f t) v`, for nonzero vectors `f`, `t`, a
    nondegenerate plane (`|f∧t|² ≠ 0`), a nondegenerate versor (`|R|² ≠ 0`, i.e. `f`, `t` not
    antiparallel) and any vector `v`. Structural: split `v = project + reject`, send the in-plane part
    through `R*P*R⁻¹ = P (R̃*R⁻¹) = P f̂ t̂` (anticommutation + `f̂ t̂ = R̃*R⁻¹`) and fix the ⊥ part
    `R Rⱼ R⁻¹ = Rⱼ` (commutation). This is the projection-formula sibling of `sandwich_carries_from_to`
    (route V), confirming the Python `transforms.projection_rotation` docstring's "both agree." -/
theorem projRotation_eq_sandwich {f t v : G3} (hf : IsVector f) (ht : IsVector t) (hv : IsVector v)
    (hpn : normSq (wedge f t) ≠ 0)
    (hrn : normSq (versorFromVectors f t) ≠ 0) :
    projRotation f t v = sandwich (versorFromVectors f t) v := by
  have hfn := normSq_ne_zero_of_wedge_left hf ht hpn
  have htn := normSq_ne_zero_of_wedge_right hf ht hpn
  have hAt := fhat_that_eq_reverse_mul_inverse hf ht hfn htn hrn
  -- In-plane: `sandwich R P = P f̂ t̂`.
  have hI : sandwich (versorFromVectors f t) (project_onto (wedge f t) v)
      = mul (mul (project_onto (wedge f t) v) (normalizeVec f)) (normalizeVec t) := by
    symm
    rw [GacalcProofs.G3.mul_assoc, hAt, ← GacalcProofs.G3.mul_assoc,
        ← versor_mul_project_eq hf ht hv hpn]
    simp only [sandwich]
  -- Perpendicular: `sandwich R Rⱼ = Rⱼ`.
  have hII : sandwich (versorFromVectors f t) (reject (wedge f t) v) = reject (wedge f t) v := by
    simp only [sandwich]
    rw [versor_mul_reject_comm hf ht hv hpn, GacalcProofs.G3.mul_assoc,
        mul_inverse_self_of_isEvenVersor (isEvenVersor_versorFromVectors hf ht) hrn,
        GacalcProofs.G3.mul_one]
  -- `project + reject = v`, converting the plane wedge to its bivector literal.
  have hsplit : add (project_onto (wedge f t) v) (reject (wedge f t) v) = v := by
    obtain ⟨a1, a2, a3, rfl⟩ := exists_vec hf
    obtain ⟨b1, b2, b3, rfl⟩ := exists_vec ht
    obtain ⟨c1, c2, c3, rfl⟩ := exists_vec hv
    rw [wedge_vec_eq_biv]
    exact project_add_reject_coord c1 c2 c3 _ _ _ (by rwa [wedge_vec_eq_biv] at hpn)
  rw [projRotation, ← hI, ← hII, ← sandwich_add, hsplit]

end GacalcProofs.G3
