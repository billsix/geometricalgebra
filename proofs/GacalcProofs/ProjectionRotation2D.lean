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
    side-by-side 3D↔2D parallel.

    Getter-native since 2026-10-05: no coordinate `_coord` scaffold — the `√` tier rests on the object
    lemmas `magnitude_sq_eq_normSq` / `magnitude_ne_zero_of_normSq_ne_zero` (`G2.lean`). -/
namespace GacalcProofs.G2

open Real

/-- Normalize a vector to unit length: `v̂ = (1/|v|)*v` (the 𝒢₂ twin of `Normalize.lean`'s `normalizeVec`). -/
noncomputable def normalizeVec (a : G2) : G2 := smul (1 / magnitude a) a

/-- A vector squares to its squared magnitude: `a a = |a|²*1` (2D twin of `G3.mul_vec_self`). -/
theorem mul_vec_self {a : G2} (ha : IsVector a) :
    mul a a = smul (normSq a) one := by
  obtain ⟨has, ha12⟩ := ha
  simp only [mul, normSq, reverse, smul, one, has, ha12]
  ext <;> ring

/-- **The rejection of a vector from the `f∧t` plane is zero** (2D): the plane is the whole space, so a
    vector has no perpendicular component. Generalizes `Projection2D.reject_from_I_eq_zero` from `I₂` to
    an arbitrary plane `f∧t` (which in 𝒢₂ is a scalar multiple of the pseudoscalar). -/
theorem reject_plane_eq_zero {f t v : G2} (hf : IsVector f) (ht : IsVector t) (hv : IsVector v) :
    reject (wedge f t) v = (⟨0, 0, 0, 0⟩ : G2) := by
  obtain ⟨hfs, hf12⟩ := hf
  obtain ⟨hts, ht12⟩ := ht
  obtain ⟨hvs, hv12⟩ := hv
  rw [reject]
  have hz : wedge v (wedge f t) = (⟨0, 0, 0, 0⟩ : G2) := by
    simp only [wedge, hfs, hf12, hts, ht12, hvs, hv12]; ext <;> ring
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
theorem projRotation_eq_vec_mul {f t v : G2} (hf : IsVector f) (ht : IsVector t) (hv : IsVector v) :
    projRotation f t v = mul (mul v (normalizeVec f)) (normalizeVec t) := by
  rw [projRotation, reject_plane_eq_zero hf ht hv]
  simp only [sub, add, mul, normalizeVec, smul]; ext <;> ring

/-! ### Carries from → to -/

/-- **The rotation carries `from` to `to`:** `projRotation f t f = (|f|/|t|)*t` — the defining property.
    `f` is in the plane so its ⊥ part is zero and its in-plane part is `f`; then `f · f̂ · t̂ = |f|*t̂`.
    Mirrors `G3.projRotation_carries_from_to`. -/
theorem projRotation_carries_from_to {f t : G2} (hf : IsVector f) (ht : IsVector t)
    (hfn : normSq f ≠ 0) (htn : normSq t ≠ 0) :
    projRotation f t f = smul (magnitude f / magnitude t) t := by
  rw [projRotation_eq_vec_mul hf ht hf]
  simp only [normalizeVec, GacalcProofs.G2.mul_smul, GacalcProofs.G2.smul_mul,
    GacalcProofs.G2.smul_smul]
  rw [mul_vec_self hf, GacalcProofs.G2.smul_mul, GacalcProofs.G2.one_mul,
    GacalcProofs.G2.smul_smul]
  congr 1
  have hmf := magnitude_ne_zero_of_normSq_ne_zero hfn
  have hmt := magnitude_ne_zero_of_normSq_ne_zero htn
  rw [← magnitude_sq_eq_normSq f]; field_simp

/-! ### Isometry -/

/-- **A triple product of vectors is norm-multiplicative** (2D): `|v f t|² = |v|²*|f|²*|t|²` — the
    Brahmagupta–Fibonacci identity applied twice (the product of three 2D vectors is again a vector). -/
theorem normSq_mul_three_vec {v f t : G2} (hv : IsVector v) (ht : IsVector t) :
    normSq (mul (mul v f) t) = normSq v * normSq f * normSq t := by
  obtain ⟨hvs, hv12⟩ := hv
  obtain ⟨hts, ht12⟩ := ht
  simp only [normSq, mul, reverse, hvs, hv12, hts, ht12]
  ring

/-- **The rotation is an isometry:** `|projRotation f t v|² = |v|²`. The rotation is `v · f̂ · t̂` with
    `f̂`, `t̂` unit, so its squared length is `|v|²*1*1`. Mirrors `G3.projRotation_isometry` (in 2D the
    √ dissolves the same way — `|f̂|² = |t̂|² = 1`). -/
theorem projRotation_isometry {f t v : G2} (hf : IsVector f) (ht : IsVector t) (hv : IsVector v)
    (hfn : normSq f ≠ 0) (htn : normSq t ≠ 0) :
    normSq (projRotation f t v) = normSq v := by
  rw [projRotation_eq_vec_mul hf ht hv]
  simp only [normalizeVec, GacalcProofs.G2.mul_smul, GacalcProofs.G2.smul_mul,
    GacalcProofs.G2.smul_smul, normSq_smul]
  rw [normSq_mul_three_vec hv ht]
  have hmf := magnitude_ne_zero_of_normSq_ne_zero hfn
  have hmt := magnitude_ne_zero_of_normSq_ne_zero htn
  rw [← magnitude_sq_eq_normSq f, ← magnitude_sq_eq_normSq t]; field_simp

/-! ### Route-equivalence: projection-formula route P = versor-sandwich route V

    The 2D twin of `G3.projRotation_eq_sandwich`. The versor `R = versorFromVectors f t = t*f + |f|*|t|`
    (`Versor2D.lean`) is even, so `R v = v R̃` for any vector `v` (`versorFromVectors_mul_vec_eq`); then
    `R*v*R⁻¹ = v (R̃*R⁻¹) = v (f̂ t̂)` once `R̃*R⁻¹ = f̂ t̂` (`fhat_that_eq_reverse_mul_inverse`), which is
    `projRotation`. The `√` lives only inside `R`'s scalar `|f|*|t|`; it is handled structurally (the key
    identity `|f|*|t|*R̃² = |R|²*(f t)`, `key_reverse_sq`, reduces by the one fact `(|f|*|t|)² = |f|²*|t|²`),
    never expanded per-coordinate. -/

/-- `R v = v R̃` for the even versor `R = versorFromVectors f t` and any vector `v` — a pure identity
    (true of every even element in 𝒢₂). -/
theorem versorFromVectors_mul_vec_eq {f t v : G2} (hf : IsVector f) (ht : IsVector t)
    (hv : IsVector v) :
    mul (versorFromVectors f t) v = mul v (reverse (versorFromVectors f t)) := by
  obtain ⟨hfs, hf12⟩ := hf
  obtain ⟨hts, ht12⟩ := ht
  obtain ⟨hvs, hv12⟩ := hv
  simp only [versorFromVectors, mul, reverse, add, smul, one, hfs, hf12, hts, ht12, hvs, hv12]
  ext <;> ring

theorem reverse_versorFromVectors_mul {f t : G2} (hf : IsVector f) (ht : IsVector t) :
    mul (reverse (versorFromVectors f t)) (versorFromVectors f t)
      = smul (normSq (versorFromVectors f t)) one := by
  obtain ⟨hfs, hf12⟩ := hf
  obtain ⟨hts, ht12⟩ := ht
  simp only [versorFromVectors, reverse, mul, add, smul, one, normSq, hfs, hf12, hts, ht12]
  ext <;> ring

/-- **The key √-bearing identity**, proven structurally: `|f|*|t|*R̃² = |R|²*(f t)`. The only analytic
    input is `(|f|*|t|)² = |f|²*|t|²`; the per-coordinate residue is pure `ring`
    (Brahmagupta–Fibonacci, `|f|²*|t|² = (f·t)² + (f∧t)²`). -/
theorem key_reverse_sq {f t : G2} (hf : IsVector f) (ht : IsVector t) :
    smul (magnitude f * magnitude t)
         (mul (reverse (versorFromVectors f t)) (reverse (versorFromVectors f t)))
      = smul (normSq (versorFromVectors f t)) (mul f t) := by
  have hK2 : (magnitude f * magnitude t) ^ 2 = (f.c1 ^ 2 + f.c2 ^ 2) * (t.c1 ^ 2 + t.c2 ^ 2) := by
    rw [mul_pow, magnitude_sq_eq_normSq, magnitude_sq_eq_normSq, normSq_eq_sum_sq, normSq_eq_sum_sq,
      hf.1, hf.2, ht.1, ht.2]; ring
  obtain ⟨hfs, hf12⟩ := hf
  obtain ⟨hts, ht12⟩ := ht
  -- Expose the versor's internal magnitudes, then abstract them so unfolding can't rewrite them
  -- into a form `hK2` no longer matches.
  simp only [versorFromVectors]
  set Mf := magnitude f
  set Mt := magnitude t
  simp only [reverse, mul, add, smul, one, normSq, hfs, hf12, hts, ht12]
  ext
  · linear_combination (Mf * Mt + (f.c1 * t.c1 + f.c2 * t.c2)) * hK2
  · ring
  · ring
  · linear_combination (f.c1 * t.c2 - f.c2 * t.c1) * hK2

/-- `f̂ t̂ = R̃*R⁻¹`: the one-sided unit-vector product equals the reverse-times-inverse of the versor.
    Derived from `key_reverse_sq` by clearing the two nonzero scalars `|f|*|t|` and `|R|²`. -/
theorem fhat_that_eq_reverse_mul_inverse {f t : G2} (hf : IsVector f) (ht : IsVector t)
    (hfn : normSq f ≠ 0) (htn : normSq t ≠ 0) (hr : normSq (versorFromVectors f t) ≠ 0) :
    mul (normalizeVec f) (normalizeVec t)
      = mul (reverse (versorFromVectors f t)) (inverse (versorFromVectors f t)) := by
  have hmf := magnitude_ne_zero_of_normSq_ne_zero hfn
  have hmt := magnitude_ne_zero_of_normSq_ne_zero htn
  have hK : magnitude f * magnitude t ≠ 0 := mul_ne_zero hmf hmt
  -- `R̃² = (nR/(|f|*|t|))*(f t)` — divide `key_reverse_sq` through by the nonzero scalar `|f|*|t|`.
  have hXeq : mul (reverse (versorFromVectors f t)) (reverse (versorFromVectors f t))
      = smul (1 / (magnitude f * magnitude t) * normSq (versorFromVectors f t)) (mul f t) := by
    have hc := congrArg (smul (1 / (magnitude f * magnitude t))) (key_reverse_sq hf ht)
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
  rw [projRotation_eq_vec_mul hf ht hv, GacalcProofs.G2.mul_assoc, sandwich,
    versorFromVectors_mul_vec_eq hf ht hv, GacalcProofs.G2.mul_assoc,
    fhat_that_eq_reverse_mul_inverse hf ht hfn htn hr]

end GacalcProofs.G2
