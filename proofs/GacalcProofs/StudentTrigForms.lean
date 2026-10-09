import GacalcProofs.Trig
import GacalcProofs.Cross
import GacalcProofs.Projection2D
import GacalcProofs.Projection3D
import GacalcProofs.Predicates2D
import GacalcProofs.Predicates3D
import GacalcProofs.Measures
import GacalcProofs.AlgebraLaws

/-! # Student-facing sine/cosine forms

    Geometric facts proved elsewhere in dot/wedge terms, **restated through `cos_between` /
    `sin_between`** (`Trig.lean`) the way a geometry/trig student meets them: perpendicular ⇒ the
    cosine of the angle is 0; parallel ⇒ the sine is 0; area = |a|*|b|*sin(θ).

    **Stated over objects, with a nonzero guard.** Each theorem takes vectors/multivectors
    (`IsVector`), not coefficient tuples ("use coordinates only when needed" — see `CLAUDE.md` and
    `lean-ga-proof-architecture.md`), and carries a nonzero hypothesis (`normSq a ≠ 0`, i.e. the input
    is not the zero vector). The guard is what makes the trig form **faithful**: see below.

    ## Why the cosine form RESTS ON the dot form, and why the nonzero guard matters

    `cos_between a b = dot a b / (|a|*|b|)`. The dot product is the division-free primitive:
    `dot a b = 0` is the exact orthogonality condition for ALL `a, b`, needing no nonzero assumption.
    Dividing introduces a subtlety — in Lean/Mathlib `x / 0 = 0` (the junk-value convention) — so if
    either vector is the zero vector then `|a|*|b| = 0` and `cos_between a b = 0/0 = 0`: TRUE but
    meaningless, since the angle to a zero vector is undefined. Hence `dot a b = 0 → cos_between a b =
    0` always, but the converse `cos(θ) = 0 → dot = 0` needs `|a|, |b| ≠ 0`; i.e. `cos(θ) = 0` is logically
    WEAKER than `dot = 0` — UNLESS we add the nonzero guard, which excludes the `0/0` case and makes
    `cos(θ) = 0 ⟺ dot = 0`. With the guard the cosine statement is exactly as strong as the dot
    primitive. Each corollary is proved FROM its dot/wedge fact (the robust primitive); the nonzero
    guard gates applicability to real (nonzero) vectors even though the `zero_div` proof does not
    consume it (so it is `_`-prefixed). Same story for `sin_between` and parallelism. The Python angle
    methods mirror this by **raising** on a zero operand.

    Collected in ONE file on purpose: `cos_between`/`sin_between` sit high in the import graph (above
    the lemma files such as `Projection2D`, which `Trig` itself imports), so a trig corollary beside
    its primitive would create an import cycle. This file imports the primitives and the trig defs
    together and is imported only by the root. -/
namespace GacalcProofs.G2

/-- **The dual of a vector is perpendicular to it**, as a student sees it: the cosine of the angle
    between `v*` and `v` is 0. For a nonzero vector `v`. -/
theorem dual_perp {v : G2} (hv : IsVector v) (_hv0 : normSq v ≠ 0) :
    cos_between (dual v) v = 0 := by
  simp only [cos_between, dual_perp_dot hv, zero_div]

/-- **The rejection is perpendicular to what it was rejected from** (cosine 0), 2D — for `a` with
    `a·a ≠ 0` (i.e. `a` nonzero). -/
theorem reject_perp (a b : G2) (ha : dot a a ≠ 0) :
    cos_between (sub b (proj a b)) a = 0 := by
  simp only [cos_between, reject_perp_dot a b ha, zero_div]

/-- **Recover `dot a b = 0` from `cos(θ) = 0`** (2D), for nonzero vectors. The nonzero guard excludes
    the junk `0/0` case (see the header), making `cos(θ) = 0` as strong as the dot primitive. -/
theorem dot_eq_zero_of_cos_between (a b : G2) (ha : magnitude a ≠ 0) (hb : magnitude b ≠ 0)
    (h : cos_between a b = 0) : dot a b = 0 := by
  rw [cos_between, div_eq_zero_iff] at h
  exact h.resolve_right (mul_ne_zero ha hb)

/-- **Perpendicular (cosine 0) ⇒ the product IS the wedge** (2D), stated on the trig side: for
    nonzero vectors with `cos(θ) = 0`, `a b = a ∧ b`. The student-facing entry point to
    `mul_eq_wedge_of_perp` (which takes the dot form). -/
theorem mul_eq_wedge_of_cos_perp {a b : G2} (ha : IsVector a) (hb : IsVector b)
    (ha0 : magnitude a ≠ 0) (hb0 : magnitude b ≠ 0) (h : cos_between a b = 0) :
    mul a b = wedge a b :=
  mul_eq_wedge_of_perp ha hb (dot_eq_zero_of_cos_between a b ha0 hb0 h)

end GacalcProofs.G2

namespace GacalcProofs.G3

/-- **The cross product is perpendicular to its left factor** (cosine 0) — for nonzero vectors. -/
theorem cross_perp_left {a b : G3} (ha : IsVector a) (hb : IsVector b)
    (_ha0 : normSq a ≠ 0) (_hb0 : normSq b ≠ 0) : cos_between (cross a b) a = 0 := by
  simp only [cos_between, cross_perp_left_dot ha hb, zero_div]

/-- **The cross product is perpendicular to its right factor** (cosine 0) — for nonzero vectors. -/
theorem cross_perp_right {a b : G3} (ha : IsVector a) (hb : IsVector b)
    (_ha0 : normSq a ≠ 0) (_hb0 : normSq b ≠ 0) : cos_between (cross a b) b = 0 := by
  simp only [cos_between, cross_perp_right_dot ha hb, zero_div]

/-- **The rejection is perpendicular to what it was rejected from** (cosine 0), 3D — for `a` with
    `a·a ≠ 0`. -/
theorem reject_perp (a b : G3) (ha : dot a a ≠ 0) :
    cos_between (sub b (proj a b)) a = 0 := by
  simp only [cos_between, reject_perp_dot a b ha, zero_div]

/-- **Parallel vectors have sine 0**: `sin(a, k·a) = 0` — the outer product of a (nonzero) vector and
    a scalar multiple of it vanishes, so the sine of the angle between them is 0. -/
theorem parallel_smul {a : G3} (ha : IsVector a) (_ha0 : normSq a ≠ 0) (k : ℝ) :
    sin_between a (smul k a) = 0 := by
  have hm : magnitude (wedge a (smul k a)) = 0 := by
    rw [wedge_parallel_smul ha k]; simp [magnitude, normSq, mul, reverse, zero]
  simp only [sin_between, hm, zero_div]

/-- **Area = |a|*|b|*sin(θ)** — the student's area-of-a-parallelogram formula, from `area = |a∧b|`
    and `sin_between = |a∧b| / (|a|*|b|)` (for nonzero `a`, `b`). -/
theorem area_eq_mag_mul_sin (a b : G3) (ha : magnitude a ≠ 0) (hb : magnitude b ≠ 0) :
    area a b = magnitude a * magnitude b * sin_between a b := by
  simp only [area, sin_between]
  field_simp

/-- **The plane normal `(a ∧ b)*` is perpendicular to each spanning vector** (cosine 0), left — for
    nonzero vectors. -/
theorem dual_wedge_perp_left {a b : G3} (ha : IsVector a) (hb : IsVector b)
    (_ha0 : normSq a ≠ 0) (_hb0 : normSq b ≠ 0) :
    cos_between (dual (wedge a b)) a = 0 := by
  simp only [cos_between, dual_wedge_perp_left_dot ha hb, zero_div]

/-- …and to the right spanning vector (cosine 0) — for a nonzero vector `b` (and ANY `a`). -/
theorem dual_wedge_perp_right {a b : G3} (hb : IsVector b)
    (_ha0 : normSq a ≠ 0) (_hb0 : normSq b ≠ 0) :
    cos_between (dual (wedge a b)) b = 0 := by
  simp only [cos_between, dual_wedge_perp_right_dot hb, zero_div]

/-- **A projection onto a plane is perpendicular to that plane's normal** (cosine 0). -/
theorem proj_plane_perp_normal (a b c : G3)
    (hn : dot (dual (wedge a b)) (dual (wedge a b)) ≠ 0) :
    cos_between (proj_plane a b c) (dual (wedge a b)) = 0 := by
  simp only [cos_between, proj_plane_perp_normal_dot a b c hn, zero_div]

/-- **Recover `dot a b = 0` from `cos(θ) = 0`** (3D), for nonzero vectors. The nonzero guard excludes
    the junk `0/0` case (see the header), making `cos(θ) = 0` as strong as the dot primitive. -/
theorem dot_eq_zero_of_cos_between (a b : G3) (ha : magnitude a ≠ 0) (hb : magnitude b ≠ 0)
    (h : cos_between a b = 0) : dot a b = 0 := by
  rw [cos_between, div_eq_zero_iff] at h
  exact h.resolve_right (mul_ne_zero ha hb)

/-- **Perpendicular (cosine 0) ⇒ the product IS the wedge** (3D), trig side: for nonzero vectors with
    `cos(θ) = 0`, `a b = a ∧ b`. Student entry point to `mul_eq_wedge_of_perp`. -/
theorem mul_eq_wedge_of_cos_perp {a b : G3} (ha : IsVector a) (hb : IsVector b)
    (ha0 : magnitude a ≠ 0) (hb0 : magnitude b ≠ 0) (h : cos_between a b = 0) :
    mul a b = wedge a b :=
  mul_eq_wedge_of_perp ha hb (dot_eq_zero_of_cos_between a b ha0 hb0 h)

/-- **Perpendicular (cosine 0) ⇒ the vectors anticommute** (3D), trig side: for nonzero vectors with
    `cos(θ) = 0`, `a b = −(b a)`. Student entry point to `vec_anticomm_perp`. -/
theorem vec_anticomm_cos_perp {a b : G3} (ha : IsVector a) (hb : IsVector b)
    (ha0 : magnitude a ≠ 0) (hb0 : magnitude b ≠ 0) (h : cos_between a b = 0) :
    mul a b = neg (mul b a) :=
  vec_anticomm_perp ha hb (dot_eq_zero_of_cos_between a b ha0 hb0 h)

/-- **`cos(θ) = 0 ⟺ a b = a ∧ b`** (3D), for nonzero vectors — the trig-side iff of
    `perp_iff_mul_eq_wedge`. Forward needs the nonzero guard (to rule out the junk `0/0`); the reverse
    (`a b = a ∧ b ⇒ cos(θ) = 0`) is free, since `dot a b = 0 ⇒ cos(θ) = 0` always. -/
theorem cos_perp_iff_mul_eq_wedge {a b : G3} (ha : IsVector a) (hb : IsVector b)
    (ha0 : magnitude a ≠ 0) (hb0 : magnitude b ≠ 0) :
    cos_between a b = 0 ↔ mul a b = wedge a b := by
  constructor
  · intro h
    exact mul_eq_wedge_of_perp ha hb (dot_eq_zero_of_cos_between a b ha0 hb0 h)
  · intro h
    have hd : dot a b = 0 := (perp_iff_mul_eq_wedge ha hb).mpr h
    simp only [cos_between, hd, zero_div]

/-- **The scalar triple product as base-area × height**, through the cross product:
    `volume = |a|*|b×c|*|cos(a, b×c)|`. The parallelepiped's volume is `|a|` times the area of the
    b–c face (`|b×c|`, the length of its normal) times the cosine of the angle from `a` to that normal
    — the student's "base times height". For nonzero `a` and nonzero `b×c`. Rests on
    `dot_cross_eq_signedVolume` (`a·(b×c) = signed volume`) and `volume_sq_vec` (`volume = |signed volume|`). -/
theorem volume_eq_mag_mul_cos {a b c : G3} (ha : IsVector a) (hb : IsVector b) (hc : IsVector c)
    (ha0 : magnitude a ≠ 0) (hbc0 : magnitude (cross b c) ≠ 0) :
    volume a b c = magnitude a * magnitude (cross b c) * |cos_between a (cross b c)| := by
  have hp : (0 : ℝ) ≤ magnitude a := Real.sqrt_nonneg _
  have hq : (0 : ℝ) ≤ magnitude (cross b c) := Real.sqrt_nonneg _
  have hvol : volume a b c = |signedVolume a b c| := by
    have hnn : (0 : ℝ) ≤ volume a b c := Real.sqrt_nonneg _
    have hsq : volume a b c ^ 2 = signedVolume a b c ^ 2 := volume_sq_vec ha hb hc
    have habs : |volume a b c| = |signedVolume a b c| := by
      rw [← Real.sqrt_sq_eq_abs, ← Real.sqrt_sq_eq_abs, hsq]
    rwa [abs_of_nonneg hnn] at habs
  rw [hvol, ← dot_cross_eq_signedVolume ha hb hc, cos_between, abs_div,
    abs_of_nonneg (mul_nonneg hp hq)]
  field_simp

end GacalcProofs.G3
