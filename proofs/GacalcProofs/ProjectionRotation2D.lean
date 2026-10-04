import GacalcProofs.G2
import GacalcProofs.AlgebraLaws
import GacalcProofs.Versor2D
import GacalcProofs.Projection2D
import GacalcProofs.Sandwich

/-! # A general rotation defined from project/reject — the 𝒢₂ parallel

    The 2D companion of `ProjectionRotation3D.lean` (the 𝒢₃ step 3 of the reduce-to-standard-position
    bootstrap arc, `tasks/reference/reduction-to-standard-position.md`). It mirrors that file exactly:
    define a *general* rotation "from `f` to `t`" out of **projection / rejection**, split `v` into its
    in-plane part (turned through the from→to angle by `· f̂ · t̂`) and its perpendicular part (left
    fixed), then show it carries `f ↦ t`, is an isometry, and agrees with the versor sandwich.

    **2D is the degenerate base case of the 3D construction.** In 𝒢₂ the `f ∧ t` plane *is* the whole
    space, so a vector has no component outside it: the rejection `reject (f∧t) v` is `0`
    (`reject_plane_eq_zero`, the general form of `Projection2D.reject_from_I_eq_zero`) and the projection
    onto the plane is the identity. The rotation therefore collapses to the pure rotor action
    `v ↦ v · f̂ · t̂` (`projRotation_eq_vec_mul`) — exactly what `Versor2D.lean` means by "in 𝒢₂ the plane
    is the whole space, so the sandwich is purely the rotation, nothing is left fixed." Reading this file
    beside `ProjectionRotation3D.lean` shows the same three theorems, with the ⊥ term present but provably
    zero. Nothing new is proven here that the existing 𝒢₂ lemmas did not already give; this is the named,
    side-by-side 3D↔2D parallel. -/
namespace GacalcProofs.G2

open Real

/-- Normalize a vector to unit length: `v̂ = (1/|v|)·v` (the 𝒢₂ twin of `Normalize.lean`'s `normalizeVec`). -/
noncomputable def normalizeVec (a : G2) : G2 := smul (1 / magnitude a) a

/-- A vector squares to its squared magnitude: `a a = |a|²·1` (2D twin of `G3.mul_vec_self`). -/
theorem mul_vec_self_coord (a1 a2 : ℝ) :
    mul (vec a1 a2) (vec a1 a2) = smul (normSq (vec a1 a2)) one := by
  rw [normSq_vec]; simp only [mul, one, smul, vec]; ext <;> ring

/-- **The rejection of a vector from the `f∧t` plane is zero** (2D): the plane is the whole space, so a
    vector has no perpendicular component. Generalizes `Projection2D.reject_from_I_eq_zero` from `I₂` to
    an arbitrary plane `f∧t` (which in 𝒢₂ is a scalar multiple of the pseudoscalar). -/
theorem reject_plane_eq_zero_coord (f1 f2 t1 t2 v1 v2 : ℝ) :
    reject (wedge (vec f1 f2) (vec t1 t2)) (vec v1 v2) = (⟨0, 0, 0, 0⟩ : G2) := by
  rw [reject]
  have hz : wedge (vec v1 v2) (wedge (vec f1 f2) (vec t1 t2)) = (⟨0, 0, 0, 0⟩ : G2) := by
    simp only [wedge, vec]; ext <;> ring
  rw [hz]; simp only [mul]; ext <;> ring

/-- **General rotation from projection/rejection** (mirrors `G3.projRotation` and
    `transforms.projection_rotation`): `projRotation f t v = (project_{f∧t} v) · f̂ · t̂ + reject_{f∧t} v`.
    The projection onto the plane is written `v − reject_{f∧t} v` (so `project + reject = v` by
    construction, the 2D echo of `project_add_reject`); the ⊥ term is kept explicit even though it is
    `0` in 𝒢₂, to make the parallel with 3D visible. -/
noncomputable def projRotation (f t v : G2) : G2 :=
  add (mul (mul (sub v (reject (wedge f t) v)) (normalizeVec f)) (normalizeVec t))
      (reject (wedge f t) v)

/-- **The rotation collapses to the rotor action** `v ↦ v · f̂ · t̂` in 𝒢₂ — the perpendicular term is
    zero (`reject_plane_eq_zero`) and the projection is `v`. This is the degenerate base case of the 3D
    construction. -/
theorem projRotation_eq_vec_mul_coord (f1 f2 t1 t2 v1 v2 : ℝ) :
    projRotation (vec f1 f2) (vec t1 t2) (vec v1 v2)
      = mul (mul (vec v1 v2) (normalizeVec (vec f1 f2))) (normalizeVec (vec t1 t2)) := by
  rw [projRotation, reject_plane_eq_zero_coord]
  simp only [sub, add, mul, normalizeVec, smul, vec]; ext <;> ring

/-- **The rotation collapses to the rotor action** (object form): `projRotation f t v = v · f̂ · t̂` for
    vectors `f`, `t`, `v`. Shared coordinate leaf `_coord` (used by the carries/isometry/sandwich proofs). -/
theorem projRotation_eq_vec_mul {f t v : G2} (hf : IsVector f) (ht : IsVector t) (hv : IsVector v) :
    projRotation f t v = mul (mul v (normalizeVec f)) (normalizeVec t) := by
  have h := projRotation_eq_vec_mul_coord f.c1 f.c2 t.c1 t.c2 v.c1 v.c2
  rwa [← eq_vec_of_isVector hf, ← eq_vec_of_isVector ht, ← eq_vec_of_isVector hv] at h

/-! ### The magnitude of `f`/`t` is nonzero where `normSq` is -/

theorem magnitude_ne_zero_of_normSq {a1 a2 : ℝ} (h : normSq (vec a1 a2) ≠ 0) :
    magnitude (vec a1 a2) ≠ 0 := by
  have hpos : (0 : ℝ) ≤ normSq (vec a1 a2) := by rw [normSq_vec]; positivity
  simp only [magnitude]; exact Real.sqrt_ne_zero'.mpr (lt_of_le_of_ne hpos (Ne.symm h))

theorem magnitude_sq_of_normSq_coord (a1 a2 : ℝ) :
    magnitude (vec a1 a2) ^ 2 = normSq (vec a1 a2) := by
  have hpos : (0 : ℝ) ≤ normSq (vec a1 a2) := by rw [normSq_vec]; positivity
  simp only [magnitude]; exact Real.sq_sqrt hpos

/-! ### Carries from → to -/

/-- **The rotation carries `from` to `to`:** `projRotation f t f = (|f|/|t|)·t` — the defining property.
    `f` is in the plane so its ⊥ part is zero and its in-plane part is `f`; then `f · f̂ · t̂ = |f|·t̂`.
    Mirrors `G3.projRotation_carries_from_to`. -/
theorem projRotation_carries_from_to {f t : G2} (hf : IsVector f) (ht : IsVector t)
    (hfn : normSq f ≠ 0) (htn : normSq t ≠ 0) :
    projRotation f t f = smul (magnitude f / magnitude t) t := by
  rw [eq_vec_of_isVector hf, eq_vec_of_isVector ht, projRotation_eq_vec_mul_coord]
  simp only [normalizeVec, GacalcProofs.G2.mul_smul, GacalcProofs.G2.smul_mul,
    GacalcProofs.G2.smul_smul]
  rw [mul_vec_self_coord, GacalcProofs.G2.smul_mul, GacalcProofs.G2.one_mul,
    GacalcProofs.G2.smul_smul]
  congr 1
  have hsq : magnitude (vec f.c1 f.c2) ^ 2 = normSq (vec f.c1 f.c2) := magnitude_sq_of_normSq_coord f.c1 f.c2
  have hmf : magnitude (vec f.c1 f.c2) ≠ 0 :=
    magnitude_ne_zero_of_normSq (by rw [← eq_vec_of_isVector hf]; exact hfn)
  have hmt : magnitude (vec t.c1 t.c2) ≠ 0 :=
    magnitude_ne_zero_of_normSq (by rw [← eq_vec_of_isVector ht]; exact htn)
  rw [← hsq]; field_simp

/-! ### Isometry -/

/-- **A triple product of vectors is norm-multiplicative** (2D): `|v f t|² = |v|²|f|²|t|²` — the
    Brahmagupta–Fibonacci identity applied twice (the product of three 2D vectors is again a vector). -/
theorem normSq_mul_three_vec_coord (v1 v2 f1 f2 t1 t2 : ℝ) :
    normSq (mul (mul (vec v1 v2) (vec f1 f2)) (vec t1 t2))
      = normSq (vec v1 v2) * normSq (vec f1 f2) * normSq (vec t1 t2) := by
  simp only [normSq, mul, reverse, vec]; ring

/-- **The rotation is an isometry:** `|projRotation f t v|² = |v|²`. The rotation is `v · f̂ · t̂` with
    `f̂`, `t̂` unit, so its squared length is `|v|²·1·1`. Mirrors `G3.projRotation_isometry` (in 2D the
    √ dissolves the same way — `|f̂|² = |t̂|² = 1`). -/
theorem projRotation_isometry {f t v : G2} (hf : IsVector f) (ht : IsVector t) (hv : IsVector v)
    (hfn : normSq f ≠ 0) (htn : normSq t ≠ 0) :
    normSq (projRotation f t v) = normSq v := by
  rw [eq_vec_of_isVector hf, eq_vec_of_isVector ht, eq_vec_of_isVector hv,
    projRotation_eq_vec_mul_coord]
  simp only [normalizeVec, GacalcProofs.G2.mul_smul, GacalcProofs.G2.smul_mul,
    GacalcProofs.G2.smul_smul, normSq_smul]
  rw [normSq_mul_three_vec_coord]
  have hmf2 : magnitude (vec f.c1 f.c2) ^ 2 = normSq (vec f.c1 f.c2) := magnitude_sq_of_normSq_coord f.c1 f.c2
  have hmt2 : magnitude (vec t.c1 t.c2) ^ 2 = normSq (vec t.c1 t.c2) := magnitude_sq_of_normSq_coord t.c1 t.c2
  have hmf : magnitude (vec f.c1 f.c2) ≠ 0 :=
    magnitude_ne_zero_of_normSq (by rw [← eq_vec_of_isVector hf]; exact hfn)
  have hmt : magnitude (vec t.c1 t.c2) ≠ 0 :=
    magnitude_ne_zero_of_normSq (by rw [← eq_vec_of_isVector ht]; exact htn)
  rw [← hmf2, ← hmt2]; field_simp

/-! ### Route-equivalence: projection-formula route P = versor-sandwich route V

    The 2D twin of `G3.projRotation_eq_sandwich`. The versor `R = versorFromVectors f t = t·f + |f||t|`
    (`Versor2D.lean`) is even, so `R v = v R̃` for any vector `v` (`versorFromVectors_mul_vec_eq`); then
    `R v R⁻¹ = v (R̃ R⁻¹) = v (f̂ t̂)` once `R̃ R⁻¹ = f̂ t̂` (`fhat_that_eq_reverse_mul_inverse`), which is
    `projRotation`. The `√` lives only inside `R`'s scalar `|f||t|`; it is handled structurally (the key
    identity `|f||t|·R̃² = |R|²·(f t)`, `key_reverse_sq`, reduces by the one fact `(|f||t|)² = |f|²|t|²`),
    never expanded per-coordinate. -/

/-- `R v = v R̃` for the even versor `R = versorFromVectors f t` and any vector `v` — a pure identity
    (true of every even element in 𝒢₂). -/
theorem versorFromVectors_mul_vec_eq_coord (f1 f2 t1 t2 v1 v2 : ℝ) :
    mul (versorFromVectors (vec f1 f2) (vec t1 t2)) (vec v1 v2)
      = mul (vec v1 v2) (reverse (versorFromVectors (vec f1 f2) (vec t1 t2))) := by
  simp only [versorFromVectors, mul, reverse, add, smul, one, vec]; ext <;> ring

/-- **The key √-bearing identity**, proven structurally: `|f||t|·R̃² = |R|²·(f t)`. The only analytic
    input is `(|f||t|)² = |f|²|t|²`; the per-coordinate residue is pure `ring`
    (Brahmagupta–Fibonacci, `|f|²|t|² = (f·t)² + (f∧t)²`). -/
theorem key_reverse_sq_coord (f1 f2 t1 t2 : ℝ) :
    smul (magnitude (vec f1 f2) * magnitude (vec t1 t2))
         (mul (reverse (versorFromVectors (vec f1 f2) (vec t1 t2)))
              (reverse (versorFromVectors (vec f1 f2) (vec t1 t2))))
      = smul (normSq (versorFromVectors (vec f1 f2) (vec t1 t2)))
             (mul (vec f1 f2) (vec t1 t2)) := by
  have hK2 : (magnitude (vec f1 f2) * magnitude (vec t1 t2)) ^ 2
      = (f1 ^ 2 + f2 ^ 2) * (t1 ^ 2 + t2 ^ 2) := by
    rw [mul_pow, magnitude_sq_of_normSq_coord, magnitude_sq_of_normSq_coord, normSq_vec, normSq_vec]
  -- Expose the versor's internal magnitudes, then abstract them so unfolding `vec` can't
  -- rewrite them into a form `hK2` no longer matches.
  simp only [versorFromVectors]
  set Mf := magnitude (vec f1 f2)
  set Mt := magnitude (vec t1 t2)
  simp only [reverse, mul, add, smul, one, normSq, vec]
  ext
  · linear_combination (Mf * Mt + (f1 * t1 + f2 * t2)) * hK2
  · ring
  · ring
  · linear_combination (f1 * t2 - f2 * t1) * hK2

/-- `f̂ t̂ = R̃ R⁻¹`: the one-sided unit-vector product equals the reverse-times-inverse of the versor.
    Derived from `key_reverse_sq` by clearing the two nonzero scalars `|f||t|` and `|R|²`. -/
theorem fhat_that_eq_reverse_mul_inverse_coord (f1 f2 t1 t2 : ℝ)
    (hf : normSq (vec f1 f2) ≠ 0) (ht : normSq (vec t1 t2) ≠ 0)
    (hr : normSq (versorFromVectors (vec f1 f2) (vec t1 t2)) ≠ 0) :
    mul (normalizeVec (vec f1 f2)) (normalizeVec (vec t1 t2))
      = mul (reverse (versorFromVectors (vec f1 f2) (vec t1 t2)))
            (inverse (versorFromVectors (vec f1 f2) (vec t1 t2))) := by
  have hmf : magnitude (vec f1 f2) ≠ 0 := magnitude_ne_zero_of_normSq hf
  have hmt : magnitude (vec t1 t2) ≠ 0 := magnitude_ne_zero_of_normSq ht
  have hK : magnitude (vec f1 f2) * magnitude (vec t1 t2) ≠ 0 := mul_ne_zero hmf hmt
  -- `R̃² = (nR/|f||t|)·(f t)` — divide `key_reverse_sq` through by the nonzero scalar `|f||t|`.
  have hXeq : mul (reverse (versorFromVectors (vec f1 f2) (vec t1 t2)))
                  (reverse (versorFromVectors (vec f1 f2) (vec t1 t2)))
      = smul (1 / (magnitude (vec f1 f2) * magnitude (vec t1 t2))
                * normSq (versorFromVectors (vec f1 f2) (vec t1 t2)))
             (mul (vec f1 f2) (vec t1 t2)) := by
    have hc := congrArg (smul (1 / (magnitude (vec f1 f2) * magnitude (vec t1 t2))))
      (key_reverse_sq_coord f1 f2 t1 t2)
    rw [GacalcProofs.G2.smul_smul, GacalcProofs.G2.smul_smul, one_div_mul_cancel hK,
      GacalcProofs.G2.one_smul] at hc
    exact hc
  rw [normalizeVec, normalizeVec, inverse]
  simp only [GacalcProofs.G2.smul_mul, GacalcProofs.G2.mul_smul, GacalcProofs.G2.smul_smul]
  rw [hXeq, GacalcProofs.G2.smul_smul]
  congr 1
  field_simp

/-- **Route-equivalence (2D):** `projRotation f t v = sandwich (versorFromVectors f t) v` — the
    projection-formula rotation (route P) equals the versor sandwich (route V). The 2D twin of
    `G3.projRotation_eq_sandwich`. -/
theorem projRotation_eq_sandwich {f t v : G2} (hf : IsVector f) (ht : IsVector t) (hv : IsVector v)
    (hfn : normSq f ≠ 0) (htn : normSq t ≠ 0) (hr : normSq (versorFromVectors f t) ≠ 0) :
    projRotation f t v = sandwich (versorFromVectors f t) v := by
  rw [eq_vec_of_isVector hf, eq_vec_of_isVector ht, eq_vec_of_isVector hv,
    projRotation_eq_vec_mul_coord, GacalcProofs.G2.mul_assoc, sandwich, versorFromVectors_mul_vec_eq_coord,
    GacalcProofs.G2.mul_assoc,
    fhat_that_eq_reverse_mul_inverse_coord f.c1 f.c2 t.c1 t.c2
      (by rw [← eq_vec_of_isVector hf]; exact hfn)
      (by rw [← eq_vec_of_isVector ht]; exact htn)
      (by rw [← eq_vec_of_isVector hf, ← eq_vec_of_isVector ht]; exact hr)]

/-! ### Object-form wrappers for the scaffold lemmas (statements over vector objects) -/

theorem mul_vec_self {a : G2} (ha : IsVector a) :
    mul a a = smul (normSq a) one := by
  obtain ⟨has, ha12⟩ := ha
  simp only [mul, normSq, reverse, smul, one, has, ha12]
  ext <;> ring

theorem reject_plane_eq_zero {f t v : G2} (hf : IsVector f) (ht : IsVector t) (hv : IsVector v) :
    reject (wedge f t) v = (⟨0, 0, 0, 0⟩ : G2) := by
  have h := reject_plane_eq_zero_coord f.c1 f.c2 t.c1 t.c2 v.c1 v.c2
  rwa [← eq_vec_of_isVector hf, ← eq_vec_of_isVector ht, ← eq_vec_of_isVector hv] at h

theorem magnitude_sq_of_normSq {a : G2} (ha : IsVector a) :
    magnitude a ^ 2 = normSq a := by
  have h := magnitude_sq_of_normSq_coord a.c1 a.c2
  rwa [← eq_vec_of_isVector ha] at h

theorem normSq_mul_three_vec {v f t : G2} (hv : IsVector v) (ht : IsVector t) :
    normSq (mul (mul v f) t) = normSq v * normSq f * normSq t := by
  obtain ⟨hvs, hv12⟩ := hv
  obtain ⟨hts, ht12⟩ := ht
  simp only [normSq, mul, reverse, hvs, hv12, hts, ht12]
  ring

theorem versorFromVectors_mul_vec_eq {f t v : G2} (hf : IsVector f) (ht : IsVector t)
    (hv : IsVector v) :
    mul (versorFromVectors f t) v = mul v (reverse (versorFromVectors f t)) := by
  have h := versorFromVectors_mul_vec_eq_coord f.c1 f.c2 t.c1 t.c2 v.c1 v.c2
  rwa [← eq_vec_of_isVector hf, ← eq_vec_of_isVector ht, ← eq_vec_of_isVector hv] at h

theorem reverse_versorFromVectors_mul {f t : G2} (hf : IsVector f) (ht : IsVector t) :
    mul (reverse (versorFromVectors f t)) (versorFromVectors f t)
      = smul (normSq (versorFromVectors f t)) one := by
  obtain ⟨hfs, hf12⟩ := hf
  obtain ⟨hts, ht12⟩ := ht
  simp only [versorFromVectors, reverse, mul, add, smul, one, normSq, hfs, hf12, hts, ht12]
  ext <;> ring

theorem key_reverse_sq {f t : G2} (hf : IsVector f) (ht : IsVector t) :
    smul (magnitude f * magnitude t)
         (mul (reverse (versorFromVectors f t)) (reverse (versorFromVectors f t)))
      = smul (normSq (versorFromVectors f t)) (mul f t) := by
  have h := key_reverse_sq_coord f.c1 f.c2 t.c1 t.c2
  rwa [← eq_vec_of_isVector hf, ← eq_vec_of_isVector ht] at h

theorem fhat_that_eq_reverse_mul_inverse {f t : G2} (hf : IsVector f) (ht : IsVector t)
    (hfn : normSq f ≠ 0) (htn : normSq t ≠ 0) (hr : normSq (versorFromVectors f t) ≠ 0) :
    mul (normalizeVec f) (normalizeVec t)
      = mul (reverse (versorFromVectors f t)) (inverse (versorFromVectors f t)) := by
  have h := fhat_that_eq_reverse_mul_inverse_coord f.c1 f.c2 t.c1 t.c2
    (by rw [← eq_vec_of_isVector hf]; exact hfn)
    (by rw [← eq_vec_of_isVector ht]; exact htn)
    (by rw [← eq_vec_of_isVector hf, ← eq_vec_of_isVector ht]; exact hr)
  rwa [← eq_vec_of_isVector hf, ← eq_vec_of_isVector ht] at h

end GacalcProofs.G2
