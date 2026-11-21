import GacalcProofs.G2

/-! # High-school geometry objects built from vectors (𝒢₂)

    The results stated on the book page `book/docs/geometry-from-vectors.rst` and the
    "Angle, area and perpendicular" section of `book/docs/product-from-projection.rst`.
    A point is a position vector; the segment from `a` to `b` is `a + t*(b − a)` for
    `0 ≤ t ≤ 1`; a polygon is a closed chain of side vectors. The survey pairing each
    object of a high-school textbook with its vector form is
    `tasks/reference/high-school-geometry-objects.md`.

    The vector-space results come first (they use only `add`, `sub`, `smul`), then the one
    result that uses the wedge, in the order `tasks/reference/algebra-teaching-order.md`
    asks for. Every statement takes and returns objects; the proofs drop to coefficients. -/
namespace GacalcProofs.G2

/-- The midpoint of the segment from `a` to `b`: `(a + b)/2`, written `½*(a + b)`. -/
noncomputable def segmentMidpoint (a b : G2) : G2 := smul (1 / 2) (add a b)

-- twin: GacalcProofs.G2.segmentMidpoint_eq_segment_half
/-- **The midpoint is the segment's point at `t = ½`**: `½*(a + b) = a + ½*(b − a)`. -/
theorem segmentMidpoint_eq_segment_half (a b : G2) :
    segmentMidpoint a b = add a (smul (1 / 2) (sub b a)) := by
  ext <;> simp only [segmentMidpoint, smul, add, sub] <;> ring

-- twin: GacalcProofs.G2.segmentMidpoint_halves
/-- **The midpoint cuts the segment into two equal halves**: the vector from `a` to the midpoint
    equals the vector from the midpoint to `b`, `m − a = b − m`, so the two halves have the same
    length and the same direction. -/
theorem segmentMidpoint_halves (a b : G2) :
    sub (segmentMidpoint a b) a = sub b (segmentMidpoint a b) := by
  ext <;> simp only [segmentMidpoint, smul, add, sub] <;> ring

-- twin: GacalcProofs.G2.triangle_sides_sum_zero
/-- **Going around a triangle returns to the start**: its three side vectors sum to zero,
    `(b − a) + (c − b) + (a − c) = 0`. -/
theorem triangle_sides_sum_zero (a b c : G2) :
    add (add (sub b a) (sub c b)) (sub a c) = zero := by
  ext <;> simp only [add, sub, zero] <;> ring

-- twin: GacalcProofs.G2.parallelogram_iff_diagonals_bisect
/-- **The diagonals of a parallelogram bisect each other, and only a parallelogram's do**: for
    four points `a, b, c, d` taken in order, side `ab` equals side `dc` as a vector (`b − a = c − d`,
    the quadrilateral is a parallelogram) exactly when the diagonals `ac` and `bd` have the same
    midpoint. -/
theorem parallelogram_iff_diagonals_bisect (a b c d : G2) :
    sub b a = sub c d ↔ segmentMidpoint a c = segmentMidpoint b d := by
  constructor
  · intro h
    have h_s := congrArg G2.s h
    have h_1 := congrArg G2.c1 h
    have h_2 := congrArg G2.c2 h
    have h_12 := congrArg G2.c12 h
    simp only [sub] at h_s h_1 h_2 h_12
    ext <;> simp only [segmentMidpoint, smul, add] <;> linarith
  · intro h
    have h_s := congrArg G2.s h
    have h_1 := congrArg G2.c1 h
    have h_2 := congrArg G2.c2 h
    have h_12 := congrArg G2.c12 h
    simp only [segmentMidpoint, smul, add] at h_s h_1 h_2 h_12
    ext <;> simp only [sub] <;> linarith

-- twin: GacalcProofs.G2.midsegment_eq_half_side
/-- **The midsegment of a triangle is parallel to the third side and half as long**: the vector
    from the midpoint of `ab` to the midpoint of `ac` is `½*(c − b)`. -/
theorem midsegment_eq_half_side (a b c : G2) :
    sub (segmentMidpoint a c) (segmentMidpoint a b) = smul (1 / 2) (sub c b) := by
  ext <;> simp only [segmentMidpoint, smul, add, sub] <;> ring

-- twin: GacalcProofs.G2.wedge_sides_eq_surveyor
/-- **A triangle's area from its corners (the surveyor's formula)**: for vectors `a, b, c`, the
    wedge of two sides from `a` is the sum of the wedges of consecutive corners,
    `(b − a) ∧ (c − a) = a ∧ b + b ∧ c + c ∧ a`. Half its `e₁*e₂` coefficient is the triangle's
    signed area. -/
theorem wedge_sides_eq_surveyor {a b c : G2} (ha : IsVector a) (hb : IsVector b)
    (hc : IsVector c) :
    wedge (sub b a) (sub c a) = add (add (wedge a b) (wedge b c)) (wedge c a) := by
  obtain ⟨has, ha12⟩ := ha
  obtain ⟨hbs, hb12⟩ := hb
  obtain ⟨hcs, hc12⟩ := hc
  ext <;> simp only [wedge, sub, add, has, ha12, hbs, hb12, hcs, hc12] <;> ring

end GacalcProofs.G2
