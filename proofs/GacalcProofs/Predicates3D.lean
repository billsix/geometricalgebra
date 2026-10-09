import GacalcProofs.G3

/-! # Orthogonality / parallelism predicates (𝒢₃)

    The geometric content of gacalc's two vector predicates:

    * `is_orthogonal_to` (base.py) tests `a·b = 0`. Its geometric meaning: the product is a pure
      wedge, `a b = a ∧ b` (no scalar part) — proved both ways below (`perp_iff_mul_eq_wedge`).
    * `is_parallel_to` tests `a ∧ b = 0` — the wedge vanishing (linear dependence), so anti-parallel
      vectors count as parallel; a vector is parallel to its scalar multiples, `a ∧ (k·a) = 0`
      (`wedge_parallel_smul`). The converse (`a ∧ b = 0 ⟹ b = k·a` for `a ≠ 0`) is not yet stated here.

    From the coverage-map gap audit (`tasks/archive/2026/10/01/lean-coverage-gap-audit.md`). -/
namespace GacalcProofs.G3

/-- **Orthogonality ⟺ the product is a pure wedge**: for vectors `a`, `b`, `a ⊥ b` (`a·b = 0`,
    gacalc `is_orthogonal_to`) iff `a b = a ∧ b`. Forward is `mul_eq_wedge_of_perp`; backward reads
    the scalar part (`(a b).s = a·b`, `(a ∧ b).s = 0`). -/
theorem perp_iff_mul_eq_wedge {a b : G3} (ha : IsVector a) (hb : IsVector b) :
    dot a b = 0 ↔ mul a b = wedge a b := by
  constructor
  · exact mul_eq_wedge_of_perp ha hb
  · intro h
    have hs : (mul a b).s = (wedge a b).s := by rw [h]
    simp only [dot]
    rw [hs]
    -- (a ∧ b).s = a.s*b.s (the outer product keeps the scalar×scalar part); a.s = 0 for a vector.
    simp only [wedge]
    rw [ha.1, zero_mul]

/-- **A vector is parallel to its scalar multiples**: `a ∧ (k·a) = 0` — the correct geometric
    "parallel" (the outer product / linear dependence vanishes), including the anti-parallel `k < 0`
    case. See the module note on the Python `is_parallel_to`'s narrower `cosine == 1`. -/
theorem wedge_parallel_smul {a : G3} (ha : IsVector a) (k : ℝ) :
    wedge a (smul k a) = zero := by
  obtain ⟨has, ha12, ha13, ha23, ha123⟩ := ha
  ext <;> simp only [wedge, smul, zero, has, ha12, ha13, ha23, ha123] <;> ring
