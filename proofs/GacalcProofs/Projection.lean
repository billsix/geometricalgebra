import GacalcProofs.G3
import GacalcProofs.Sandwich

/-! # Projection in 𝒢₃ — the geometric construction

    The chain that builds 3D projection from vector projections + the dual, feeding the
    3D versor sandwich (see `tasks/reference/lean-ga-proof-architecture.md`):

      * `proj a b = (b·a / a·a) · a` — vector projection; the rejection `b − proj_a b` is
        perpendicular to `a` (`reject_perp`).
      * The wedge sees only the rejection: `a ∧ b = a ∧ (b − proj_a b)` (`wedge_reject`).
      * The dual of `a ∧ b` (the plane normal, gacalc's `cross`) is ⊥ both spanning
        vectors (`dual_wedge_perp_left`/`_right`).

    Still to come: projection onto the plane `= (c·B)B⁻¹` (the Hestenes formula), then the
    3D sandwich as a corollary of the G2 `sandwich_versor`. -/
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
theorem reject_perp (a b : G3) (ha : dot a a ≠ 0) :
    dot (sub b (proj a b)) a = 0 := by
  rw [dot_sub_left, proj, dot_smul_left]
  field_simp
  ring

/-- **The wedge sees only the rejection**: for a vector `a`, `a ∧ b = a ∧ (b − proj_a b)`
    (the parallel part `proj_a b` wedges to zero, so only the perpendicular part remains). -/
theorem wedge_reject (a1 a2 a3 : ℝ) (b : G3) :
    wedge (vec a1 a2 a3) (sub b (proj (vec a1 a2 a3) b)) = wedge (vec a1 a2 a3) b := by
  rw [wedge_sub_right, proj, wedge_smul_right, wedge_self_vec]
  simp only [smul, zero, sub]; ext <;> ring

/-- **The dual of `a ∧ b` (the plane normal) is ⊥ `a`** — for vectors `a`, `b`. The dual of
    the wedge is `cross a b` (gacalc), and `(a × b) · a = 0`. -/
theorem dual_wedge_perp_left (a1 a2 a3 b1 b2 b3 : ℝ) :
    dot (dual (wedge (vec a1 a2 a3) (vec b1 b2 b3))) (vec a1 a2 a3) = 0 := by
  simp only [dot, dual, I_inv, wedge, vec, mul]; ring

/-- …and ⊥ `b`. -/
theorem dual_wedge_perp_right (a1 a2 a3 b1 b2 b3 : ℝ) :
    dot (dual (wedge (vec a1 a2 a3) (vec b1 b2 b3))) (vec b1 b2 b3) = 0 := by
  simp only [dot, dual, I_inv, wedge, vec, mul]; ring

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
  -- The rejection is ⊥ `a` (`reject_perp`), so the scalar part dies; and the wedge ignores the
  -- parallel part (`wedge_reject`), so the bivector part is `a∧b`.
  have hdaa : dot (vec a1 a2 a3) (vec a1 a2 a3) ≠ 0 := by
    rw [dot_self_vec_eq_normSq]; exact ha
  have hpv : IsVector (proj (vec a1 a2 a3) (vec b1 b2 b3)) := by
    rw [proj]; exact (isVector_vec a1 a2 a3).smul _
  have hrv : IsVector (sub (vec b1 b2 b3) (proj (vec a1 a2 a3) (vec b1 b2 b3))) :=
    (isVector_vec b1 b2 b3).sub hpv
  have hd0 : dot (vec a1 a2 a3) (sub (vec b1 b2 b3) (proj (vec a1 a2 a3) (vec b1 b2 b3))) = 0 := by
    rw [dot_comm]; exact reject_perp (vec a1 a2 a3) (vec b1 b2 b3) hdaa
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
  rw [inverse, reverse_vec, GacalcProofs.G3.mul_smul, mul_vec_self, GacalcProofs.G3.smul_smul,
      one_div_mul_cancel ha, GacalcProofs.G3.one_smul]

/-- **Hestenes rejection onto a vector equals the projection-complement:** `(b ∧ a) a⁻¹ = b − proj_a b`
    (for `a·a ≠ 0`). Confirms the direct `(A∧B)B⁻¹` form matches the vector-projection construction
    (`(b∧a)a⁻¹ + (b·a)a⁻¹ = (ba)a⁻¹ = b`). -/
theorem reject_vec_eq (a1 a2 a3 b1 b2 b3 : ℝ)
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
  rw [dot_self_vec_eq_normSq]; ring

/-- **Projection of `c` ONTO the `a∧b` plane** (the book's construction): project `c` away
    from the plane's normal `n = dual(a∧b)` (a vector projection) and subtract — what's
    left lies in the plane. -/
noncomputable def proj_plane (a b c : G3) : G3 := sub c (proj (dual (wedge a b)) c)

/-- The plane-projection lies in the plane: it is ⊥ the normal `dual(a∧b)` — for a
    nondegenerate plane (`dual(a∧b) · dual(a∧b) ≠ 0`). This is exactly `reject_perp`
    applied to the normal. -/
theorem proj_plane_perp_normal (a b c : G3)
    (hn : dot (dual (wedge a b)) (dual (wedge a b)) ≠ 0) :
    dot (proj_plane a b c) (dual (wedge a b)) = 0 := by
  rw [proj_plane]; exact reject_perp (dual (wedge a b)) c hn

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
theorem project_add_reject (a1 a2 a3 p q r : ℝ)
    (hB : normSq (⟨0, 0, 0, 0, p, q, r, 0⟩ : G3) ≠ 0) :
    add (project_onto ⟨0, 0, 0, 0, p, q, r, 0⟩ (vec a1 a2 a3))
        (reject ⟨0, 0, 0, 0, p, q, r, 0⟩ (vec a1 a2 a3))
      = vec a1 a2 a3 := by
  have hd := normSq_biv p q r
  rw [hd] at hB  -- the plane's magnitude in coordinates, for the field_simp step
  simp only [project_onto, reject, inner_vb, inverse, hd]
  simp only [wedge, mul, reverse, smul, add, vec]
  ext <;> field_simp [hB] <;> ring

/-- `add X Y = Z → X = Z − Y` (componentwise cancellation). -/
theorem add_eq_left_sub (x y z : G3) (h : add x y = z) : x = sub z y := by
  rw [← h]; ext <;> simp only [add, sub] <;> ring

/-- **Rejection from a plane = projection onto its normal** (for a bivector `B = p·e₁₂ + q·e₁₃ +
    r·e₂₃`, `|B|² ≠ 0`): `(c ∧ B) B⁻¹ = proj_{dual B} c`. Both are the perpendicular component of `c`.
    Stated for a literal bivector so the degrees stay low. -/
theorem reject_eq_proj_normal (p q r c1 c2 c3 : ℝ)
    (h : normSq (⟨0, 0, 0, 0, p, q, r, 0⟩ : G3) ≠ 0) :
    reject (⟨0, 0, 0, 0, p, q, r, 0⟩ : G3) (vec c1 c2 c3)
      = proj (dual (⟨0, 0, 0, 0, p, q, r, 0⟩ : G3)) (vec c1 c2 c3) := by
  have hd1 := normSq_biv p q r
  rw [hd1] at h  -- the plane's magnitude in coordinates, for the field_simp step
  have hd2 : dot (dual (⟨0, 0, 0, 0, p, q, r, 0⟩ : G3)) (dual (⟨0, 0, 0, 0, p, q, r, 0⟩ : G3))
      = p ^ 2 + q ^ 2 + r ^ 2 := by
    simp only [dot, dual, I_inv, mul]; ring
  simp only [reject, inverse, proj, hd1, hd2]
  simp only [dual, I_inv, wedge, mul, reverse, smul, dot, vec]
  ext <;> field_simp [h] <;> ring

/-- `project` onto a plane = `c −` (rejection from the plane), for a literal bivector — a rearrangement
    of `project_add_reject`. -/
theorem project_eq_sub_reject (p q r c1 c2 c3 : ℝ)
    (h : normSq (⟨0, 0, 0, 0, p, q, r, 0⟩ : G3) ≠ 0) :
    project_onto (⟨0, 0, 0, 0, p, q, r, 0⟩ : G3) (vec c1 c2 c3)
      = sub (vec c1 c2 c3) (reject (⟨0, 0, 0, 0, p, q, r, 0⟩ : G3) (vec c1 c2 c3)) :=
  add_eq_left_sub _ _ _ (project_add_reject c1 c2 c3 p q r h)

/-- **The normal-based plane projection equals the Hestenes form:** `proj_plane a b c =
    project_onto (a∧b) c`. Both are the in-plane component of `c` — `proj_plane` builds it as
    `c −` (projection onto the normal), Hestenes as `(c·(a∧b))(a∧b)⁻¹`; they agree (for a
    nondegenerate plane, `|a∧b|² ≠ 0`). Verifies gacalc's `project` onto a plane against the geometric
    construction. Assembled from the two literal-bivector lemmas above (instantiated at `a∧b`), so it
    is just rewrites — no re-expansion. -/
theorem proj_plane_eq_project_onto (a1 a2 a3 b1 b2 b3 c1 c2 c3 : ℝ)
    (hn : normSq (wedge (vec a1 a2 a3) (vec b1 b2 b3)) ≠ 0) :
    proj_plane (vec a1 a2 a3) (vec b1 b2 b3) (vec c1 c2 c3)
      = project_onto (wedge (vec a1 a2 a3) (vec b1 b2 b3)) (vec c1 c2 c3) := by
  have hw := wedge_vec_eq_biv a1 a2 a3 b1 b2 b3
  -- The two literal-bivector lemmas now take `normSq B ≠ 0` (the plane's squared magnitude), which is
  -- exactly `hn` once the wedge is rewritten to its bivector literal — no coordinate sum anywhere.
  rw [hw] at hn
  simp only [proj_plane]
  rw [hw, ← reject_eq_proj_normal _ _ _ c1 c2 c3 hn, project_eq_sub_reject _ _ _ c1 c2 c3 hn]

end GacalcProofs.G3
