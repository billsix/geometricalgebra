import GacalcProofs.StandardPosition2D

/-! # Rotating the direction of `a` onto the direction of `b` in 𝒢₂ — standard position

    The book's "Proof: Rotate from direction a to direction b" (`book/docs/proof-rotate-from-a-to-b.rst`):
    using only the elementary plane rotation `rotPlane` (a procedure on the components, read off the
    vectors' coordinates — the same tool `StandardPosition2D.lean` uses), rotate `a`'s direction onto
    `b`'s by **reduction to standard position**, in three steps written in order of application (right
    to left):

      1. `R_a^{e₁} = rotPlane (a₁/|a|) (−a₂/|a|)` — swing `a` onto the `e₁` axis.
      2. `R_{e₁}^{b'}` — in that frame, rotate `e₁` onto `b' = R_a^{e₁}(b)`, reading the cosine/sine off
         `b'`'s own coordinates. `b'`'s unit coordinates are `(a·b)/(|a|*|b|)` and `(a∧b)/(|a|*|b|)`
         (`bprime_coords`), so this middle rotation is `rotPlane ((a·b)/(|a|*|b|)) ((a∧b)/(|a|*|b|))`.
      3. `(R_a^{e₁})⁻¹ = rotPlane (a₁/|a|) (a₂/|a|)` — undo step 1.

    **The punchline — the sandwich collapses.** In 2D plane rotations commute, so the align/un-align of
    steps 1 and 3 cancel around the middle and the whole thing is *just the middle rotation*
    (`rotateFromTo_collapse`): a single `rotPlane` by the angle from `a` to `b`, whose cosine and sine
    are the coordinate formulas `(a·b)/(|a|*|b|)` and `(a∧b)/(|a|*|b|)` — **no angle ever named**. Applied
    to `a`, it lands on `(|a|/|b|)*b` — `b`'s direction with `a`'s magnitude (`rotateFromTo_carries`),
    since magnitudes don't set the rotation, only directions do. The engine is `rotPlane_comp` (the
    composition of two plane rotations is the rotation by the angle-sum), its corollary
    `rotPlane_comm` (plane rotations commute — the fact the book's "The collapse" cites by name),
    and `rotPlane_conj_collapse` (a conjugation by a unit `(cos, sin)` leaves the middle rotation
    unchanged). See
    `tasks/reference/reduction-to-standard-position.md`. -/
namespace GacalcProofs.G2

/-- **Composition of plane rotations = rotation-angle addition.** `rotPlane c₁ s₁ ∘ rotPlane c₂ s₂` is
    `rotPlane (c₁*c₂ − s₁*s₂) (s₁*c₂ + c₁*s₂)` — the 2×2 rotation-matrix product. Pure algebra; holds for
    any `(c, s)` (no unit constraint). The result is symmetric in the two pairs, which is why plane
    rotations commute — stated as `rotPlane_comm` below. -/
theorem rotPlane_comp (c1 s1 c2 s2 : ℝ) (v : G2) :
    rotPlane c1 s1 (rotPlane c2 s2 v) = rotPlane (c1 * c2 - s1 * s2) (s1 * c2 + c1 * s2) v := by
  simp only [rotPlane]; ext <;> ring

/-- **Plane rotations commute:** `rotPlane c₁ s₁ ∘ rotPlane c₂ s₂ = rotPlane c₂ s₂ ∘ rotPlane c₁ s₁`.
    By `rotPlane_comp` each side is the single rotation by the angle-sum, and that rotation's
    `(cos, sin)` is symmetric in the two pairs (real multiplication and addition commute). Pure
    algebra — no unit constraint, any `v`. This is the fact `rotPlane_conj_collapse` rests on and the
    one the book's `proof-rotate-from-a-to-b.rst` ("The collapse") cites; the angle form is
    `Rotation2D.rot_comm`. -/
theorem rotPlane_comm (c1 s1 c2 s2 : ℝ) (v : G2) :
    rotPlane c1 s1 (rotPlane c2 s2 v) = rotPlane c2 s2 (rotPlane c1 s1 v) := by
  have hc : c1 * c2 - s1 * s2 = c2 * c1 - s2 * s1 := by ring
  have hs : s1 * c2 + c1 * s2 = s2 * c1 + c2 * s1 := by ring
  rw [rotPlane_comp, rotPlane_comp, hc, hs]

/-- **Sandwich collapse:** conjugating a rotation by a *unit* plane rotation leaves it unchanged —
    aligning with `rotPlane ca (−sa)`, rotating by `(c₂, s₂)` in the aligned frame, then un-aligning
    with `rotPlane ca sa`, is the same as just rotating by `(c₂, s₂)`. (2D rotations commute —
    `rotPlane_comm` — so the align/un-align slide past the middle rotation and cancel.) Needs only
    `ca² + sa² = 1`. -/
theorem rotPlane_conj_collapse (ca sa c2 s2 : ℝ) (h : ca ^ 2 + sa ^ 2 = 1) (v : G2) :
    rotPlane ca sa (rotPlane c2 s2 (rotPlane ca (-sa) v)) = rotPlane c2 s2 v := by
  rw [rotPlane_comm c2 s2 ca (-sa), rotPlane_comp]
  have hc : ca * ca - sa * -sa = 1 := by linear_combination h
  have hs : sa * ca + ca * -sa = 0 := by ring
  rw [hc, hs]
  simp only [rotPlane]
  ext <;> ring

/-- **The transported `b' = R_a^{e₁}(b)`.** Swinging `b` by the same rotation that sends `a` to the
    `e₁` axis (`alignSP a`) gives the vector whose coordinates are `(a·b)/|a|` and `(a∧b)/|a|` — so its
    *unit* coordinates (divide by `|b'| = |b|`) are the `(cos, sin)` that step 2 reads off. -/
theorem bprime_coords {a b : G2} (ha : IsVector a) (hb : IsVector b) :
    alignSP a b = vec (dot a b / magnitude a) ((wedge a b).c12 / magnitude a) := by
  obtain ⟨has, ha12⟩ := ha
  obtain ⟨hbs, hb12⟩ := hb
  simp only [alignSP, rotPlane, vec, dot, wedge, mul, has, ha12, hbs, hb12]
  ext <;> simp only <;> ring

/-- **The three-step construction collapses to a single plane rotation** — the punchline. Align `a`
    to `e₁` (`alignSP a`), rotate by any `(cos, sin)` in that frame, then un-align (`unalignSP a`): the
    align/un-align cancel and only the middle rotation `rotPlane c s` remains. For any `v`. For the
    rotation from `a` to `b` the middle `(c, s)` is `((a·b)/(|a|*|b|), (a∧b)/(|a|*|b|))` (`bprime_coords`
    divided by `|b|`). -/
theorem rotateFromTo_collapse {a : G2} (ha : IsVector a) (hma : magnitude a ≠ 0) (c s : ℝ)
    (v : G2) :
    unalignSP a (rotPlane c s (alignSP a v)) = rotPlane c s v := by
  have h : (a.c1 / magnitude a) ^ 2 + (a.c2 / magnitude a) ^ 2 = 1 := by
    have h := cs_unit ha hma
    rwa [neg_div, neg_sq] at h
  simp only [unalignSP, alignSP, neg_div]
  exact rotPlane_conj_collapse _ _ c s h v

/-- **The construction carries `a`'s direction to `b`'s direction.** The three-step rotation applied to
    `a` is `(|a|/|b|)*b` — `b`'s direction, scaled to `a`'s magnitude (magnitudes don't set the
    rotation). For nonzero `a`, `b`. -/
theorem rotateFromTo_carries {a b : G2} (ha : IsVector a) (hb : IsVector b)
    (hma : magnitude a ≠ 0) (hmb : magnitude b ≠ 0) :
    unalignSP a
        (rotPlane (dot a b / (magnitude a * magnitude b))
          ((wedge a b).c12 / (magnitude a * magnitude b)) (alignSP a a))
      = smul (magnitude a / magnitude b) b := by
  have hma2 : magnitude a ^ 2 = a.c1 ^ 2 + a.c2 ^ 2 := magnitude_sq_of_isVector ha
  rw [rotateFromTo_collapse ha hma]
  obtain ⟨has, ha12⟩ := ha
  obtain ⟨hbs, hb12⟩ := hb
  simp only [rotPlane, smul, dot, wedge, mul, has, ha12, hbs, hb12]
  ext
  · simp
  · field_simp
    linear_combination (-b.c1) * hma2
  · field_simp
    linear_combination (-b.c2) * hma2
  · simp

end GacalcProofs.G2
