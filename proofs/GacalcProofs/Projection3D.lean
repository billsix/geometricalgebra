import GacalcProofs.G3
import GacalcProofs.Sandwich

/-! # Projection in 𝒢₃ — the geometric construction

    The chain that builds 3D projection from vector projections + the dual, feeding the
    3D versor sandwich (see `tasks/reference/lean-ga-proof-architecture.md`):

      * `proj a b = (b·a / a·a) · a` — vector projection; the rejection `b − proj_a b` is
        perpendicular to `a` (`reject_perp_dot`).
      * The wedge sees only the rejection: `a ∧ b = a ∧ (b − proj_a b)` (`wedge_reject`).
      * The dual of `a ∧ b` (the plane normal, gacalc's `cross`) is ⊥ both spanning
        vectors (`dual_wedge_perp_left_dot`/`_right`).

    Still to come: projection onto the plane `= (c·B)B⁻¹` (the Hestenes formula), then the
    3D sandwich as a corollary of the G2 `sandwich_rotor`. -/
namespace GacalcProofs.G3

/-- Vector projection of `b` onto `a`: `proj_a b = (b·a / a·a) · a`. Lies along `a`.

    The denominator is the self-inner-product `a·a` (Hestenes `dot`), **not** `normSq a`. They agree
    for a vector (`a·a = |a|²`), but this def is stated for a general `a : G3`, where `a·a ≠ normSq a`
    (they have opposite signs on grade ≥ 2, since `normSq` uses the reverse: `normSq a = ⟨a ã⟩`).
    Rewriting the denominator to `normSq a` would narrow the def incorrectly — so it stays `dot a a`. -/
noncomputable def proj (a b : G3) : G3 := smul (dot b a / dot a a) a

/-- **The rejection is perpendicular to `a`**: `(b − proj_a b) · a = 0`, for `a·a ≠ 0`.

    The hypothesis is the **general** `dot a a ≠ 0`, deliberately not `normSq a ≠ 0`: this holds for
    any `a : G3`, and for a non-vector `a` the two differ (see `proj`). Do NOT tighten it to `normSq`. -/
theorem reject_perp_dot (a b : G3) (ha : dot a a ≠ 0) :
    dot (sub b (proj a b)) a = 0 := by
  rw [dot_sub_left, proj, dot_smul_left]
  field_simp
  ring

/-- **The wedge sees only the rejection**: for a vector `a`, `a ∧ b = a ∧ (b − proj_a b)`
    (the parallel part `proj_a b` wedges to zero, so only the perpendicular part remains). -/
theorem wedge_reject (a1 a2 a3 : ℝ) (b : G3) :
    wedge (vec a1 a2 a3) (sub b (proj (vec a1 a2 a3) b)) = wedge (vec a1 a2 a3) b := by
  rw [wedge_sub_right, proj, wedge_smul_right, wedge_self_vec_coord]
  simp only [smul, zero, sub]; ext <;> ring

/-- **The dual of `a ∧ b` (the plane normal) is ⊥ `a`** — for vectors `a`, `b`. The dual of
    the wedge is `cross a b` (gacalc), and `(a × b) · a = 0`. -/
theorem dual_wedge_perp_left_dot {a b : G3} (ha : IsVector a) (hb : IsVector b) :
    dot (dual (wedge a b)) a = 0 := by
  obtain ⟨has, _, _, _, _⟩ := ha
  obtain ⟨hbs, _, _, _, _⟩ := hb
  simp only [dot, dual, I_inv, wedge, mul,
    has, hbs]
  ring

/-- …and ⊥ `b`. -/
theorem dual_wedge_perp_right_dot {a b : G3} (hb : IsVector b) :
    dot (dual (wedge a b)) b = 0 := by
  obtain ⟨hbs, hb12, hb13, hb23, _⟩ := hb
  simp only [dot, dual, I_inv, wedge, mul,
    hbs, hb12, hb13, hb23]
  ring

/-- **The rotation plane is `a (b − proj_a b)`**: for a vector `a` with `a·a ≠ 0`,
    `a (b − proj_a b) = a ∧ b`. The rejection `r = b − proj_a b` is ⊥ `a`, so the geometric
    product loses its scalar (inner) part and only the bivector survives, and the wedge ignores the
    rejection — exhibiting the plane of rotation as the pure bivector `a ∧ b`, built from `a` and
    `b`. This is the step that reduces the 3D versor sandwich to the 2D case. -/
theorem plane_eq_wedge (a1 a2 a3 b1 b2 b3 : ℝ)
    (ha : normSq (vec a1 a2 a3) ≠ 0) :
    mul (vec a1 a2 a3) (sub (vec b1 b2 b3) (proj (vec a1 a2 a3) (vec b1 b2 b3)))
      = wedge (vec a1 a2 a3) (vec b1 b2 b3) := by
  -- Structural, on the fundamental split: `a r = a·r + a∧r` with `r = b − proj_a b` the rejection.
  -- The rejection is ⊥ `a` (`reject_perp_dot`), so the scalar part dies; and the wedge ignores the
  -- parallel part (`wedge_reject`), so the bivector part is `a∧b`.
  have hdaa : dot (vec a1 a2 a3) (vec a1 a2 a3) ≠ 0 := by
    rw [dot_self_vec_eq_normSq_coord]; exact ha
  have hpv : IsVector (proj (vec a1 a2 a3) (vec b1 b2 b3)) := by
    rw [proj]; exact (isVector_vec a1 a2 a3).smul _
  have hrv : IsVector (sub (vec b1 b2 b3) (proj (vec a1 a2 a3) (vec b1 b2 b3))) :=
    (isVector_vec b1 b2 b3).sub hpv
  have hd0 : dot (vec a1 a2 a3) (sub (vec b1 b2 b3) (proj (vec a1 a2 a3) (vec b1 b2 b3))) = 0 := by
    rw [dot_comm]; exact reject_perp_dot (vec a1 a2 a3) (vec b1 b2 b3) hdaa
  rw [mul_eq_dot_add_wedge (isVector_vec a1 a2 a3) hrv, wedge_reject, hd0]
  simp only [smul, one, add]; ext <;> ring

/-- **Hestenes rejection** `reject_B A = (A ∧ B) · B⁻¹` — the component of `A` orthogonal to the
    subspace (blade) `B` (gacalc `reject`, base.py; Hestenes & Sobczyk p.18). `B` may be a vector or a
    (simple) bivector — the *same* formula — using the blade inverse `inverse` (from `Sandwich.lean`,
    `B̃ / (B B̃)`; `B · inverse B = 1`). Companion to `proj`; the outer product picks out only the part
    of `A` outside `B`. -/
noncomputable def reject (awayFrom a : G3) : G3 := mul (wedge a awayFrom) (inverse awayFrom)

/-- **A vector times its own inverse is `1`** (the blade-inverse identity `B B⁻¹ = 1` for a vector,
    `a·a ≠ 0`): `a⁻¹ = ã/|a|² = a/|a|²`, and `a a = |a|²`, so `a a⁻¹ = |a|²/|a|² = 1`. -/
theorem mul_vec_inverse_self (a1 a2 a3 : ℝ) (ha : normSq (vec a1 a2 a3) ≠ 0) :
    mul (vec a1 a2 a3) (inverse (vec a1 a2 a3)) = one := by
  rw [inverse, reverse_vec, GacalcProofs.G3.mul_smul, mul_vec_self_coord, GacalcProofs.G3.smul_smul,
      one_div_mul_cancel ha, GacalcProofs.G3.one_smul]

/-- **Hestenes rejection onto a vector equals the projection-complement:** `(b ∧ a) a⁻¹ = b − proj_a b`
    (for `a·a ≠ 0`). Confirms the direct `(A∧B)B⁻¹` form matches the vector-projection construction
    (`(b∧a)a⁻¹ + (b·a)a⁻¹ = (ba)a⁻¹ = b`). -/
theorem reject_vec_eq_coord (a1 a2 a3 b1 b2 b3 : ℝ)
    (ha : normSq (vec a1 a2 a3) ≠ 0) :
    reject (vec a1 a2 a3) (vec b1 b2 b3)
      = sub (vec b1 b2 b3) (proj (vec a1 a2 a3) (vec b1 b2 b3)) := by
  -- Structural (Hestenes): `b∧a = ba − (b·a)·1`, so `(b∧a)a⁻¹ = b(a a⁻¹) − (b·a)a⁻¹ = b − proj_a b`.
  have hsplit : wedge (vec b1 b2 b3) (vec a1 a2 a3)
      = sub (mul (vec b1 b2 b3) (vec a1 a2 a3)) (smul (dot (vec b1 b2 b3) (vec a1 a2 a3)) one) := by
    rw [vec_mul_eq_dot_add_wedge]; simp only [sub, add, smul, one]; ext <;> ring
  rw [reject, hsplit, GacalcProofs.G3.sub_mul, GacalcProofs.G3.mul_assoc,
      mul_vec_inverse_self a1 a2 a3 ha, GacalcProofs.G3.mul_one, GacalcProofs.G3.smul_mul,
      GacalcProofs.G3.one_mul]
  -- Left with `b − (b·a)a⁻¹ = b − proj_a b`; the two rejection terms agree once `a⁻¹`'s scalar is folded.
  congr 1
  rw [proj, inverse, reverse_vec, GacalcProofs.G3.smul_smul]
  congr 1
  rw [dot_self_vec_eq_normSq_coord]; ring

/-- **Hestenes rejection onto a vector equals the projection-complement** (object form):
    `reject_a b = b − proj_a b`, for a nonzero vector `a` (`|a|² ≠ 0`) and a vector `b`. -/
theorem reject_vec_eq {a b : G3} (ha_isv : IsVector a) (hb_isv : IsVector b) (ha : normSq a ≠ 0) :
    reject a b = sub b (proj a b) := by
  have h := reject_vec_eq_coord a.c1 a.c2 a.c3 b.c1 b.c2 b.c3
    (by rw [← eq_vec_of_isVector ha_isv]; exact ha)
  rwa [← eq_vec_of_isVector ha_isv, ← eq_vec_of_isVector hb_isv] at h

/-- **Projection of `c` ONTO the `a∧b` plane** (the book's construction): project `c` away
    from the plane's normal `n = dual(a∧b)` (a vector projection) and subtract — what's
    left lies in the plane. -/
noncomputable def proj_plane (a b c : G3) : G3 := sub c (proj (dual (wedge a b)) c)

/-- The plane-projection lies in the plane: it is ⊥ the normal `dual(a∧b)` — for a
    nondegenerate plane (`dual(a∧b) · dual(a∧b) ≠ 0`). This is exactly `reject_perp_dot`
    applied to the normal. -/
theorem proj_plane_perp_normal_dot (a b c : G3)
    (hn : dot (dual (wedge a b)) (dual (wedge a b)) ≠ 0) :
    dot (proj_plane a b c) (dual (wedge a b)) = 0 := by
  rw [proj_plane]; exact reject_perp_dot (dual (wedge a b)) c hn

/-! ### Hestenes projection onto a plane, via the graded inner product -/

/-- **Hestenes inner product, grade-1 case** `⟨A B⟩₁` — for a vector `A` and a bivector `B`, the
    grade-1 (vector) part of the geometric product `A B`. This is Hestenes' inner product `A · B` for
    this grade pair (*Clifford Algebra to Geometric Calculus*, 1984) — the "vector into the plane"
    component. It is **not** the scalar `dot` (which is `⟨A B⟩₀`, identically 0 here) and **not** the
    later "contraction." Correct as an inner product only for the vector·bivector grade pair. -/
noncomputable def inner_vb (a b : G3) : G3 := vec (mul a b).c1 (mul a b).c2 (mul a b).c3

/-- **Hestenes projection onto a bivector (plane):** `project_B A = (A · B) B⁻¹` — the in-plane
    component of the vector `A` (gacalc `project`, base.py; H&S p.18), using the grade-1 inner
    product `inner_vb` and the blade inverse. The bivector counterpart of `proj` (onto a vector). -/
noncomputable def project_onto (onto a : G3) : G3 := mul (inner_vb a onto) (inverse onto)

/-- **Projection + rejection = identity**, for a vector onto a plane (bivector `B = p·e₁₂ + q·e₁₃ +
    r·e₂₃`, `|B|² ≠ 0`): `(A·B)B⁻¹ + (A∧B)B⁻¹ = A`. Because `(A·B) + (A∧B) = A B` (the grade-1 and
    grade-3 parts are the whole product for a vector·bivector) and `B B⁻¹ = 1`. This validates the
    Hestenes `project`/`reject` pair — the in-plane part plus the perpendicular part reconstruct the
    vector. -/
theorem project_add_reject_coord (a1 a2 a3 p q r : ℝ)
    (hB : normSq (bivector p q r) ≠ 0) :
    add (project_onto (bivector p q r) (vec a1 a2 a3))
        (reject (bivector p q r) (vec a1 a2 a3))
      = vec a1 a2 a3 := by
  have hd := normSq_biv p q r
  rw [hd] at hB  -- the plane's magnitude in coordinates, for the field_simp step
  simp only [project_onto, reject, inner_vb, inverse, hd]
  simp only [wedge, mul, reverse, smul, add, vec, bivector, zero]
  ext <;> field_simp [hB] <;> ring

/-- **Projection + rejection = identity** (object form): for a vector `a` and a plane bivector `B`
    (`|B|² ≠ 0`), `(A·B)B⁻¹ + (A∧B)B⁻¹ = A`. -/
theorem project_add_reject {B : G3} (hB : IsBivector B) (hBn : normSq B ≠ 0) {a : G3} (ha : IsVector a) :
    add (project_onto B a) (reject B a) = a := by
  have hd : normSq B = B.c12 ^ 2 + B.c13 ^ 2 + B.c23 ^ 2 := by
    rw [← normSq_biv, ← eq_bivector_of_isBivector hB]
  obtain ⟨hBs, hB1, hB2, hB3, hB123⟩ := hB
  obtain ⟨_, ha12, ha13, ha23, _⟩ := ha
  rw [hd] at hBn
  simp only [project_onto, reject, inner_vb, inverse, hd]
  simp only [wedge, mul, reverse, smul, add, vec, hBs, hB1, hB2, hB3, hB123,
             ha12, ha13, ha23]
  ext <;> simp only [ha12, ha13, ha23] <;> field_simp [hBn] <;> ring

/-- `add X Y = Z → X = Z − Y` (componentwise cancellation). -/
theorem add_eq_left_sub (x y z : G3) (h : add x y = z) : x = sub z y := by
  rw [← h]; ext <;> simp only [add, sub] <;> ring

/-- **Rejection from a plane = projection onto its normal** (for a bivector `B = p·e₁₂ + q·e₁₃ +
    r·e₂₃`, `|B|² ≠ 0`): `(c ∧ B) B⁻¹ = proj_{dual B} c`. Both are the perpendicular component of `c`.
    Stated for a literal bivector so the degrees stay low. -/
theorem reject_eq_proj_normal_coord (p q r c1 c2 c3 : ℝ)
    (h : normSq (bivector p q r) ≠ 0) :
    reject (bivector p q r) (vec c1 c2 c3)
      = proj (dual (bivector p q r)) (vec c1 c2 c3) := by
  have hd1 := normSq_biv p q r
  rw [hd1] at h  -- the plane's magnitude in coordinates, for the field_simp step
  have hd2 : dot (dual (bivector p q r)) (dual (bivector p q r))
      = p ^ 2 + q ^ 2 + r ^ 2 := by
    simp only [dot, dual, I_inv, mul, bivector, zero]; ring
  simp only [reject, inverse, proj, hd1, hd2]
  simp only [dual, I_inv, wedge, mul, reverse, smul, dot, vec, bivector, zero]
  ext <;> field_simp [h] <;> ring

/-- **Rejection from a plane = projection onto its normal** (object form): for a vector `c` and a plane
    bivector `B` (`|B|² ≠ 0`), `(c ∧ B) B⁻¹ = proj_{dual B} c`. -/
theorem reject_eq_proj_normal {B : G3} (hB : IsBivector B) (hBn : normSq B ≠ 0) {c : G3} (hc : IsVector c) :
    reject B c = proj (dual B) c := by
  have hd1 : normSq B = B.c12 ^ 2 + B.c13 ^ 2 + B.c23 ^ 2 := by
    rw [← normSq_biv, ← eq_bivector_of_isBivector hB]
  obtain ⟨hBs, hB1, hB2, hB3, hB123⟩ := hB
  obtain ⟨hcs, _, _, _, _⟩ := hc
  have hd2 : dot (dual B) (dual B) = B.c12 ^ 2 + B.c13 ^ 2 + B.c23 ^ 2 := by
    simp only [dot, dual, I_inv, mul, hBs, hB1, hB2, hB3, hB123]; ring
  rw [hd1] at hBn
  simp only [reject, inverse, proj, hd1, hd2]
  simp only [dual, I_inv, wedge, mul, reverse, smul, dot, hBs, hB1, hB2, hB3, hB123,
             hcs]
  ext <;> field_simp [hBn] <;> ring

/-- `project` onto a plane = `c −` (rejection from the plane), for a literal bivector — a rearrangement
    of `project_add_reject`. -/
theorem project_eq_sub_reject_coord (p q r c1 c2 c3 : ℝ)
    (h : normSq (bivector p q r) ≠ 0) :
    project_onto (bivector p q r) (vec c1 c2 c3)
      = sub (vec c1 c2 c3) (reject (bivector p q r) (vec c1 c2 c3)) :=
  add_eq_left_sub _ _ _ (project_add_reject_coord c1 c2 c3 p q r h)

/-- `project` onto a plane = `c −` (rejection from the plane) (object form) — a rearrangement of
    `project_add_reject`, for a vector `c` and a plane bivector `B` (`|B|² ≠ 0`). -/
theorem project_eq_sub_reject {B : G3} (hB : IsBivector B) (hBn : normSq B ≠ 0) {c : G3} (hc : IsVector c) :
    project_onto B c = sub c (reject B c) :=
  add_eq_left_sub _ _ _ (project_add_reject hB hBn hc)

/-- **The normal-based plane projection equals the Hestenes form:** `proj_plane a b c =
    project_onto (a∧b) c`. Both are the in-plane component of `c` — `proj_plane` builds it as
    `c −` (projection onto the normal), Hestenes as `(c·(a∧b))(a∧b)⁻¹`; they agree (for a
    nondegenerate plane, `|a∧b|² ≠ 0`). Verifies gacalc's `project` onto a plane against the geometric
    construction. Assembled from the two literal-bivector lemmas above (instantiated at `a∧b`), so it
    is just rewrites — no re-expansion. -/
theorem proj_plane_eq_project_onto {a b c : G3} (ha : IsVector a) (hb : IsVector b) (hc : IsVector c)
    (hn : normSq (wedge a b) ≠ 0) :
    proj_plane a b c = project_onto (wedge a b) c := by
  rw [eq_vec_of_isVector ha, eq_vec_of_isVector hb, eq_vec_of_isVector hc]
  have hw := wedge_vec_eq_biv a.c1 a.c2 a.c3 b.c1 b.c2 b.c3
  -- The two literal-bivector `_coord` lemmas take `normSq B ≠ 0` (the plane's squared magnitude),
  -- exactly `hn` once the wedge is rewritten to its bivector literal — no coordinate sum anywhere.
  have hn' : normSq (wedge (vec a.c1 a.c2 a.c3) (vec b.c1 b.c2 b.c3)) ≠ 0 := by
    rw [← eq_vec_of_isVector ha, ← eq_vec_of_isVector hb]; exact hn
  rw [hw] at hn'
  simp only [proj_plane]
  rw [hw, ← reject_eq_proj_normal_coord _ _ _ c.c1 c.c2 c.c3 hn',
      project_eq_sub_reject_coord _ _ _ c.c1 c.c2 c.c3 hn']

end GacalcProofs.G3
