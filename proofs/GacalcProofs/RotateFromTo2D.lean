import GacalcProofs.StandardPosition2D

/-! # Rotating the direction of `a` onto the direction of `b` in 𝒢₂ — standard position

    The book's "Proof: Rotate from direction a to direction b" (`book/docs/proof-rotate-from-a-to-b.rst`):
    using only the elementary plane rotation `rotPlane` (a procedure on the components, read off the
    vectors' coordinates — the same tool `StandardPosition2D.lean` uses), rotate `a`'s direction onto
    `b`'s by **reduction to standard position**, in three steps written in order of application (right
    to left):

      1. `R_a^{e₁} = rotPlane (a₁/|a|) (−a₂/|a|)` — swing `a` onto the `e₁` axis.
      2. `R_{e₁}^{b'}` — in that frame, rotate `e₁` onto `b' = R_a^{e₁}(b)`, reading the cosine/sine off
         `b'`'s own coordinates. `b'`'s unit coordinates are `(a·b)/(|a| * |b|)` and `(a∧b)/(|a| * |b|)`
         (`bprime_coords`), so this middle rotation is `rotPlane ((a·b)/(|a| * |b|)) ((a∧b)/(|a| * |b|))`.
      3. `(R_a^{e₁})⁻¹ = rotPlane (a₁/|a|) (a₂/|a|)` — undo step 1.

    **The punchline — the sandwich collapses.** In 2D plane rotations commute, so the align/un-align of
    steps 1 and 3 cancel around the middle and the whole thing is *just the middle rotation*
    (`rotateFromTo_collapse`): a single `rotPlane` by the angle from `a` to `b`, whose cosine and sine
    are the coordinate formulas `(a·b)/(|a| * |b|)` and `(a∧b)/(|a| * |b|)` — **no angle ever named**. Applied
    to `a`, it lands on `(|a|/|b|) * b` — `b`'s direction with `a`'s magnitude (`rotateFromTo_carries`),
    since magnitudes don't set the rotation, only directions do. The engine is `rotPlane_comp` (the
    composition of two plane rotations is the rotation by the angle-sum), its corollary
    `rotPlane_comm` (plane rotations commute — the fact the book's "The collapse" cites by name),
    and `rotPlane_conj_collapse` (a conjugation by a unit `(cos, sin)` leaves the middle rotation
    unchanged). See
    `tasks/reference/reduction-to-standard-position.md`. -/
namespace GacalcProofs.G2

/-- **Composition of plane rotations = rotation-angle addition.** `rotPlane c₁ s₁ ∘ rotPlane c₂ s₂` is
    `rotPlane (c₁ * c₂ − s₁ * s₂) (s₁ * c₂ + c₁ * s₂)` — the 2×2 rotation-matrix product. Pure algebra; holds for
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
  simp only [rotPlane]
  ext
  · rfl
  · linear_combination (c2 * v.c1 - s2 * v.c2) * h
  · linear_combination (s2 * v.c1 + c2 * v.c2) * h
  · rfl

/-- **The transported `b' = R_a^{e₁}(b)`.** Swinging `b` by the same rotation that sends `a` to the
    `e₁` axis gives the vector whose coordinates are `(a·b)/|a|` and `(a∧b)/|a|` — so its *unit*
    coordinates (divide by `|b'| = |b|`) are the `(cos, sin)` that step 2 reads off. -/
theorem bprime_coords (a1 a2 b1 b2 ma : ℝ) :
    rotPlane (a1 / ma) (-a2 / ma) (vec b1 b2)
      = vec ((a1 * b1 + a2 * b2) / ma) ((a1 * b2 - a2 * b1) / ma) := by
  simp only [rotPlane, vec]; ext <;> ring

/-- The `(cos, sin)` read off `a` is a unit pair, given `|a|² = a₁² + a₂²` and `|a| ≠ 0`. -/
theorem cs_a_unit (a1 a2 ma : ℝ) (hma : ma ≠ 0) (hma2 : a1 ^ 2 + a2 ^ 2 = ma ^ 2) :
    (a1 / ma) ^ 2 + (a2 / ma) ^ 2 = 1 := by
  rw [div_pow, div_pow, ← add_div, hma2]
  exact div_self (pow_ne_zero 2 hma)

/-- **The three-step construction collapses to a single plane rotation** — the punchline. Align `a` to
    `e₁` (`rotPlane (a₁/|a|) (−a₂/|a|)`), rotate by the coordinate `(cos, sin)` of the `a→b` angle in
    that frame, then un-align (`rotPlane (a₁/|a|) (a₂/|a|)`); the align/un-align cancel and only the
    middle rotation `rotPlane ((a·b)/(|a| * |b|)) ((a∧b)/(|a| * |b|))` remains. For any `v`. -/
theorem rotateFromTo_collapse (a1 a2 b1 b2 ma mb : ℝ)
    (hma : ma ≠ 0) (hma2 : a1 ^ 2 + a2 ^ 2 = ma ^ 2) (v : G2) :
    rotPlane (a1 / ma) (a2 / ma)
        (rotPlane ((a1 * b1 + a2 * b2) / (ma * mb)) ((a1 * b2 - a2 * b1) / (ma * mb))
          (rotPlane (a1 / ma) (-(a2 / ma)) v))
      = rotPlane ((a1 * b1 + a2 * b2) / (ma * mb)) ((a1 * b2 - a2 * b1) / (ma * mb)) v :=
  rotPlane_conj_collapse (a1 / ma) (a2 / ma) _ _ (cs_a_unit a1 a2 ma hma hma2) v

/-- **The construction carries `a`'s direction to `b`'s direction.** The three-step rotation applied to
    `a` is `(|a|/|b|) * b` — `b`'s direction, scaled to `a`'s magnitude (magnitudes don't set the
    rotation). For nonzero `a`, `b` (`ma = |a|`, `mb = |b|`). -/
theorem rotateFromTo_carries (a1 a2 b1 b2 ma mb : ℝ)
    (hma : ma ≠ 0) (hmb : mb ≠ 0) (hma2 : a1 ^ 2 + a2 ^ 2 = ma ^ 2) :
    rotPlane (a1 / ma) (a2 / ma)
        (rotPlane ((a1 * b1 + a2 * b2) / (ma * mb)) ((a1 * b2 - a2 * b1) / (ma * mb))
          (rotPlane (a1 / ma) (-(a2 / ma)) (vec a1 a2)))
      = smul (ma / mb) (vec b1 b2) := by
  rw [rotateFromTo_collapse a1 a2 b1 b2 ma mb hma hma2]
  simp only [rotPlane, vec, smul]
  ext
  · simp
  · field_simp
    linear_combination b1 * hma2
  · field_simp
    linear_combination b2 * hma2
  · simp

end GacalcProofs.G2
