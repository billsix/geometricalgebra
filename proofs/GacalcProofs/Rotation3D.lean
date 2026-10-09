import GacalcProofs.G3

/-! # The 3D versor from two vectors — angle-free (no trig)

    The maintainer's own construction of the rotation versor in 𝒢₃, built directly from
    two vectors with **no angle parameter** (mirroring `versor_from_vectors` in `base.py`).
    An earlier attempt parameterized the rotation by an explicit angle θ and defined the
    versor as `cos(θ/2) * 1 − sin(θ/2) * e₁₂`; that dragged in `cos`/`sin` and the double-angle
    identities (and an instance-diamond fight with Mathlib's `sin_sq_add_cos_sq`) for no
    geometric gain. This file follows the maintainer's Python instead: the half-angle is
    *implicit* in the two vectors, so the whole story is polynomial algebra closed by `ring`.

    The pieces (write `a = from`, `b = to`, both vectors):

      * **The half-angle (bisector) vector** `h = |b| * a + |a| * b` (`bisector`): scale each
        input by the *other's* magnitude and add. Both summands have length `|a| * |b|`, so `h`
        sits the same angle θ/2 from each of `a` and `b`.
      * **The half-angle versor** `R = b * a + |a| * |b|` (`versorFromVectors`): the geometric
        product of two vectors θ/2 apart is an even-grade versor — here `h * a = |a| * R`, so
        `R` is the bisector times the from-vector (up to the positive scale `|a|`, which
        cancels in the scale-invariant sandwich `R * v * R⁻¹`).
      * **The nice identity** (`versor_mul_from_eq_bisector`): running that the other way,
        `R * a = |a| * h`. The versor built from `a, b`, multiplied by the from-vector `a`,
        yields the (scaled) half-angle bisector vector. The only analytic fact it touches is
        `|a|² = a·a` (`Real.sq_sqrt`); everything else is `ring`.

    The sandwich `R * v * R⁻¹` itself (record: `tasks/archive/2026/10/04/lean-proof-rotation-from-scratch.md`) —
    that it carries `a` to (a scalar multiple of) `b` and fixes the plane normal
    `dual (a ∧ b)` — as the angle-free 3D analogue of the G2 `sandwich_rotor`. The intended
    finish reduces it to 2D via the plane `a (b − proj_a b) = a ∧ b` (from the proved
    `reject_perp` + `wedge_reject`): the orthogonal frame `{a, r}` normalizes to G2's
    `{e₁, e₂, e₁₂}` table, so the sandwich is a corollary of the proved G2 `sandwich_rotor`,
    fixing the normal. The one new unlocking lemma is `a r = a ∧ r` for `a ⊥ r`.

    ## References (for when this is picked up again)

    * The construction is gacalc's `versor_from_vectors` (`base.py`) — the source of `h`, `R`,
      and the `R * a = |a| * h` derivation.
    * Basis blades as algebra *elements* (not real fields), used throughout `G2`/`G3`:
      Wieser & Song, *Formalizing Geometric Algebra in Lean* (2021, arXiv:2110.03551); and
      `pygae/lean-ga`.
    * Proving `h` genuinely *bisects* the angle (`angle a h = angle h b`) is optional and not
      done here (our identity is purely algebraic). No packaged Mathlib lemma states it, but the
      ingredients are in `Mathlib/Geometry/Euclidean/Angle/Unoriented/Basic.lean`
      (`angle_smul_left_of_pos`, `angle_smul_right_of_pos`, `angle_normalize_left`/`_right`,
      `angle_smul_smul`): since `h = |a| * |b| * (â + b̂)`, it reduces to `angle â (â+b̂) = angle b̂ (â+b̂)`
      by symmetry (the isosceles/rhombus bisector). External reference to learn from / cite:
      LeanGeo (arXiv:2508.14644), a Lean/Mathlib formalization of competition geometry. Using
      Mathlib's `angle` on this from-scratch `G3` first needs the (deferred) map into
      `EuclideanSpace ℝ (Fin 3)` or a local `angle a b := arccos (a·b / (|a| * |b|))`. -/
namespace GacalcProofs.G3

open Real

/-- The **half-angle (bisector) vector** of `from`/`to`: `h = |to| * from + |from| * to`.
    Scale each vector by the *other's* magnitude and add — the sum bisects the angle
    (`base.py` `versor_from_vectors`, the `h` there). Uses the general `magnitude = √normSq`
    (all grades), which agrees with `√(a·a)` on a vector. -/
noncomputable def bisector (fromV toV : G3) : G3 :=
  add (smul (magnitude toV) fromV) (smul (magnitude fromV) toV)

/-- The **half-angle versor** taking `from` toward `to`, à la gacalc's `versor_from_vectors`:
    the un-normalized even element `R = to * from + |from| * |to|` (scalar + bivector). Applied by
    the scale-invariant sandwich `R * v * R⁻¹`. -/
noncomputable def versorFromVectors (fromV toV : G3) : G3 :=
  add (mul toV fromV) (smul (magnitude fromV * magnitude toV) one)

/-- `|a|² = a₁²+a₂²+a₃²` for a coordinate vector — the one analytic fact the identity below needs.
    `magnitude = √normSq`, so this is `normSq_vec` under the square root. -/
theorem magnitude_sq_vec (a1 a2 a3 : ℝ) :
    magnitude (vec a1 a2 a3) ^ 2 = a1 ^ 2 + a2 ^ 2 + a3 ^ 2 := by
  rw [magnitude, Real.sq_sqrt (by rw [normSq_vec]; positivity), normSq_vec]

/-- **A vector sandwiched by its own square:** `(b a) a = |a|² * b` for vectors `a`, `b`
    (the associativity fact `b(aa) = b|a|²`, since `a a = |a|²`). -/
theorem vec_mul_mul_self {a b : G3} (ha : IsVector a) (hb : IsVector b) :
    mul (mul b a) a = smul (normSq a) b := by
  rw [eq_vec_of_isVector ha, eq_vec_of_isVector hb, normSq_vec a.c1 a.c2 a.c3]
  simp only [mul, vec, smul]; ext <;> ring

/-- **The half-angle versor times the from-vector is the (scaled) bisector**:
    `R * a = |a| * h`, where `R = versorFromVectors a b` and `h = bisector a b`.

    The versor built from `a` and `b`, multiplied (geometric product) by the from-vector
    `a`, yields the half-angle bisector vector `h`, scaled by the positive `|a|` (which
    cancels in the sandwich). Angle-free: the only non-`ring` step is `|a|² = a·a`. -/
theorem versor_mul_from_eq_bisector_coord (a1 a2 a3 b1 b2 b3 : ℝ) :
    mul (versorFromVectors (vec a1 a2 a3) (vec b1 b2 b3)) (vec a1 a2 a3)
      = smul (magnitude (vec a1 a2 a3)) (bisector (vec a1 a2 a3) (vec b1 b2 b3)) := by
  simp only [versorFromVectors, bisector]
  -- Abstract the two magnitudes to opaque atoms; the only fact needed is `sa² = a·a`.
  set sa := magnitude (vec a1 a2 a3)
  set sb := magnitude (vec b1 b2 b3)
  have hsa : sa ^ 2 = a1 ^ 2 + a2 ^ 2 + a3 ^ 2 := magnitude_sq_vec a1 a2 a3
  clear_value sa sb
  simp only [mul, add, smul, one, vec]
  -- The three vector components need `sa² = a·a`; every other component is 0 = 0.
  ext
  · ring
  · linear_combination -b1 * hsa
  · linear_combination -b2 * hsa
  · linear_combination -b3 * hsa
  · ring
  · ring
  · ring
  · ring

/-- Object form of `versor_mul_from_eq_bisector_coord`, for vectors `fromV`, `toV`:
    `R * from = |from| * h`. -/
theorem versor_mul_from_eq_bisector {fromV toV : G3} (hf : IsVector fromV) (ht : IsVector toV) :
    mul (versorFromVectors fromV toV) fromV = smul (magnitude fromV) (bisector fromV toV) := by
  have h := versor_mul_from_eq_bisector_coord fromV.c1 fromV.c2 fromV.c3 toV.c1 toV.c2 toV.c3
  rwa [← eq_vec_of_isVector hf, ← eq_vec_of_isVector ht] at h

/-- **Companion identity: the to-vector times the versor is the (scaled) bisector**, `b * R = |b| * h`
    (multiplying `R` on the LEFT by `b`). Symmetric to `versor_mul_from_eq_bisector` (`R * a = |a| * h`).
    Together the pair drives the capstone `R * a * R⁻¹ = (|a|/|b|) * b` (the versor carries `a` to `b`): from
    `R a = |a| h` and `b R = |b| h`, associativity, and `R R̃ = |R|²`, `R * a * R⁻¹ = (|a|/|b|) * b`. -/
theorem from_mul_versor_eq_bisector_coord (a1 a2 a3 b1 b2 b3 : ℝ) :
    mul (vec b1 b2 b3) (versorFromVectors (vec a1 a2 a3) (vec b1 b2 b3))
      = smul (magnitude (vec b1 b2 b3)) (bisector (vec a1 a2 a3) (vec b1 b2 b3)) := by
  simp only [versorFromVectors, bisector]
  set sa := magnitude (vec a1 a2 a3)
  set sb := magnitude (vec b1 b2 b3)
  have hsb : sb ^ 2 = b1 ^ 2 + b2 ^ 2 + b3 ^ 2 := magnitude_sq_vec b1 b2 b3
  clear_value sa sb
  simp only [mul, add, smul, one, vec]
  ext
  · ring
  · linear_combination -a1 * hsb
  · linear_combination -a2 * hsb
  · linear_combination -a3 * hsb
  · ring
  · ring
  · ring
  · ring

/-- Object form of `from_mul_versor_eq_bisector_coord`, for vectors `fromV`, `toV`:
    `to * R = |to| * h`. -/
theorem from_mul_versor_eq_bisector {fromV toV : G3} (hf : IsVector fromV) (ht : IsVector toV) :
    mul toV (versorFromVectors fromV toV) = smul (magnitude toV) (bisector fromV toV) := by
  have h := from_mul_versor_eq_bisector_coord fromV.c1 fromV.c2 fromV.c3 toV.c1 toV.c2 toV.c3
  rwa [← eq_vec_of_isVector hf, ← eq_vec_of_isVector ht] at h

end GacalcProofs.G3
