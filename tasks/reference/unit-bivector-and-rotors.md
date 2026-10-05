# The unit bivector `i`, `bivector_from_vectors`, and rotors

**Reference document** — the math and design behind gacalc's plane/rotor helpers: the unit
bivector `i` of a plane, the `bivector_from_vectors` / `i` builders, the `.i()` extractor, and the
`rotor = exp(bivector)` relationship. Durable domain + design notes; **update in place**, not
archived. Last updated 2026-08-14. Spawned from the task
`tasks/archive/2026/08/15/redo-exp-book-referenced.md` (the `exp()` redo + `i` work); this doc holds the *why*, the
task holds the *work*.

**Citations are the open half of this doc.** The maintainer (William Emerison Six <billsix@gmail.com>) is verifying the rotor/exp material against books
he owns (Hestenes & Sobczyk, Macdonald, Taylor, …). The **Citations** section below is a checklist
with per-claim status — some are verified, some need the maintainer's copy. Do **not** invent a page number;
mark it "needs the maintainer's copy" until confirmed. **The maintainer will populate these over time as he reads —
there is no deadline; leave a ⬜ box open until he confirms a page/equation against his own copy,
then flip it to ✅ here and in the docstring it supports.**

## 1. The unit bivector `i` of a plane, and why `i² = −1`

For two vectors `a, b` in Euclidean ℝⁿ, the **outer product `a ∧ b` is a bivector** — the oriented
plane they span, whose magnitude is the area of the parallelogram on `a, b`. Its **normalization**
`î = (a ∧ b) / |a ∧ b|` is the **unit bivector** of that plane, and it satisfies `î² = −1`. Two
derivations (both worth a docstring line):

1. **Orthonormal factoring.** Any Euclidean 2-blade factors as `B = |B| e₁e₂` with `e₁, e₂`
   orthonormal (Gram–Schmidt on `a, b`). Then `B² = |B|² e₁e₂e₁e₂`; since orthogonal vectors
   anticommute (`e₂e₁ = −e₁e₂`) and each squares to `+1` (Euclidean signature), `e₁e₂e₁e₂ =
   −e₁e₁e₂e₂ = −1`. So `B² = −|B|²`, and the unit bivector `î = B/|B|` has `î² = −1`.
2. **Grade formula.** For a grade-`r` blade, `A² = (−1)^{r(r−1)/2} |A|²` (this is already in
   `base.py`'s `exp` docstring). At `r = 2`, `(−1)^1 = −1` → `A² = −|A|²`. (Same formula: `r = 1`
   vectors → `+|A|²`; the 𝒢₃ pseudoscalar `r = 3` → `−|A|²`.)

Because `î² = −1`, the unit bivector behaves algebraically like the imaginary unit, so the
exponential series splits into cos/sin (§3). This is why the 2D geometric algebra "secretly
contains" the complex numbers, and why a plane's `î` is the natural rotation generator.

## 2. Design: `bivector_from_vectors`, `i`, and `.i()` (2026-08-14)

Two builders + one extractor, layered so each does one thing. (Rationale: the *raw* area bivector
and the *unit* plane are genuinely different objects; separating them lands the parallel-vectors
guard in exactly one place and keeps a descriptive name alongside the terse `i`.)

**All three return a BIVECTOR — never a rotor (William Emerison Six <billsix@gmail.com>, 2026-08-14).**
`bivector_from_vectors` and `i(a,b)` return the plane bivector (raw and unit respectively); `.i()`
extracts the plane bivector from a value. The **rotor is a separate object** built later from the
bivector via `exp(−(θ/2)·i)` (§3) — `i` is what you *feed* `exp`, not the rotor itself. This is why
the return type is a bivector: a rotor-returning `i` would both contradict the "`i` = unit bivector"
convention and duplicate `versor_from_vectors` / `plane_rotation`.

- **`bivector_from_vectors(a, b) → a ∧ b`** (un-normalized) — the area bivector. Classmethod on
  `MultiVectorBase`, paralleling `versor_from_vectors` (`base.py`). Validates grade-1; returns
  `a.outer_product(b)`. No parallel guard — the wedge of parallel vectors is the legitimate zero
  bivector.
- **`i(a, b) → normalize(bivector_from_vectors(a, b))`** — the unit bivector (`i² = −1`). The
  parallel-vectors guard lands here (normalizing zero raises `ZeroDivisionError`, gacalc ≥ 0.0.16).
  Classmethod on the **full** classes `Gn`/`G2`/`G3` (see placement).
- **`.i()`** — instance method on the graded `Bivector`/`Versor` types, returning the value's unit
  plane. `Bivector.i() = self.normalize()`; `Versor.i()` = the existing `plane_of_rotation()`
  (`g2.py`, `r_vector_part(2).normalize()`), exposed under the `i` name.

**Placement / the name-clash resolution.** The full types (`Gn`/`G2`/`G3`) and graded types
(`Bivector`/`Versor`) are **siblings** (all `@typing.final` subclasses of `MultiVectorBase`), so a
classmethod `i(a,b)` on the full classes and an instance `.i()` on the graded types do **not**
collide. Keep `i(a,b)` **off** the shared base (else the graded `.i()` shadows the inherited
classmethod), and don't put `.i()` on the full `G` classes. `bivector_from_vectors` *is* safe on the
base (no instance-method twin). **`plane_rotation` (`transforms.py`) already inlines exactly
`a∧b` + guard + normalize — refactor it to call these, one implementation.**

**Decided (William Emerison Six <billsix@gmail.com>, 2026-08-14):** the **`i(a,b)` classmethod goes on `Gn`, `G2`, `G3`, *and*
`Vector`** (a,b are vectors, so `Vector.i(a,b)` reads naturally); **`.i()` stays on the graded
`Bivector`/`Versor` only.** A single class cannot carry both an `i(a,b)` classmethod and an `.i()`
instance method, so the full/general types (`Gn`/`G2`/`G3`) + `Vector` get the *builder* and the
graded types get the *extractor* — no collision, since they're siblings. `Gn` gets the classmethod
(not `.i()`); to get the plane out of a general `Gn` value that is a bivector, use `.normalize()`
(which `.i()` is just a named shortcut for on the graded types).

## 3. Rotor = exp(bivector): the relationship

A **rotor** `R` (even-grade, `R R̃ = 1`) rotates by angle θ in the plane of unit bivector `i` via
the half-angle exponential:

  `R = exp(−(θ/2) i) = cos(θ/2) − sin(θ/2) i` ,  and `v ↦ R v R̃` rotates `v` by θ (oriented a→b).

This is exactly what `plane_rotation(a, b)(θ)` builds today.

**Building the rotor from `i` directly — no series needed (William Emerison Six <billsix@gmail.com>, 2026-08-14; verified).** Once you
have the unit bivector `i`, the rotor for angle θ is just a scalar plus `i` scaled by the
half-angle sines: **`R = cos(θ/2) − sin(θ/2)·i`**. The one requirement is that `R` be a **unit**
rotor (`R R̃ = 1`), and that is automatic because `cos² + sin² = 1`: with `R = c + s·i`,
`R R̃ = (c + s·i)(c − s·i) = c² − s²·i² = c² + s² = 1`. **The `1/√2` example checks out:**
`R = (1/√2) + (1/√2)·i` has scalar and bivector-coefficient both `1/√2`, so `c = s = 1/√2 ⇒
θ/2 = 45° ⇒ θ = 90°` — a 90° rotor — and `c² + s² = ½ + ½ = 1`, unit. ✓ So the subtask-2 builder is
literally: get `i`, pick θ, return `cos(θ/2) − sin(θ/2)·i`. (Sign/orientation: gacalc's
`plane_rotation` uses the `−` form, `= exp(−(θ/2)·i)`, which turns `a→b` for positive θ; the `+`
form first written by the maintainer is the same rotor family with the opposite orientation — mirror direction. Any
scalar `c` and coefficient `s` with `c² + s² = 1` is a unit rotor rotating by `θ = 2·atan2(s, c)`.)

**A unit bivector is NOT a rotor** —
the bivector is the plane (grade-2, `i²=−1`, angle-free); the rotor is even-grade and carries the
angle in its half-angle trig. `i` is what you *feed* `exp` to get a rotor. (A unit bivector equals
a rotor only at θ = π, a 180° turn.)

## 4. The domain of `exp` (the redo's open question)

`exp` is well-defined when `A²` is scalar. The **scalar** and **bivector** (→ rotor) cases are the
keepers. The **grade-1 vector case** (`A² = +|A|² > 0 → cosh|A| + sinh|A|·â`) is under review:
the cosh/sinh *formula* is standard, **but only for Minkowski boosts** (spacetime bivectors,
`A²=+1` in a Lorentzian metric) — no standard text presents "`exp` of a *Euclidean vector*" as
meaningful. gacalc's grade-1 branch applies the boost formula to a Euclidean vector only because it
*happens* to have positive square; it has no Euclidean geometric interpretation, and it mirrors
galgebra's `Mv.exp` (galgebra's `galgebra/mv.py`, cosh/sinh for `sq>0`) without a book
motivation. **Leaning: drop it**, restricting `exp` to "the exponential map onto the rotors." (Task
subtask 3.)

## 5. Citations — verify against the maintainer's library (checklist)

Priority is books **the maintainer owns**. Status: ✅ verified in this research pass · ⬜ needs the maintainer's copy.

- **`R = exp(−(θ/2) i) = cos(θ/2) − sin(θ/2) i` (rotor as exp of a unit bivector):**
  - ✅ **Macdonald, *A Survey of GA & GC*** (free PDF, faculty.luther.edu/~macdonal): **Eq. (2.3)
    §2.2.1** and **Eq. (2.4) §2.3.2** — `R = e^{−iθ/2}`, `i` the unit bivector. *the maintainer owns Macdonald.*
    Check whether his **textbook *Linear and Geometric Algebra*** carries the same (the survey is the
    verified proxy — the textbook's own section number was not independently confirmed). ⬜
  - ⬜ **Hestenes & Sobczyk, *Clifford Algebra to Geometric Calculus* (1984):** `R = e^{−iθ/2}`
    appears in the spinor/rotation material of Ch. 1–3, but **no exact page was located** (consistent
    with the archived `exp-for-rotors` task). *the maintainer owns it — find the page in his copy; do not
    invent one.*
  - ⬜ **Taylor (2021):** gacalc already cites Taylor for contractions (`p.103`, per CLAUDE.md).
    *the maintainer owns it* — check whether it covers rotor = exp(bivector) and cite if so.
  - ✅ **Dorst, Fontijne & Mann, *GA for Computer Science* (2007) §7.4** ("Exponential Representation
    of Rotors"; §7.4.1 rotors as exp of 2-blades, §7.4.3 exp of bivectors) — the **strongest** and
    the one whose structure *is* gacalc's `exp`. **But the maintainer may not own it** — treat as the reference
    of record for the design, cite a maintainer-owned book in the docstrings if one covers it.
- **The cosh/sinh (`A²>0`) case is a *boost*, not a Euclidean operation:**
  - ✅ **Macdonald survey §4.1** (verbatim): "since `(γ₀v̂)² = +1`, `e^{γ₀v̂ α/2} = cosh(α/2) +
    γ₀v̂ sinh(α/2)`" — applied to a **spacetime bivector**. ✅ **Dorst §7.4.2** ("Trigonometric and
    Hyperbolic Functions"). *Use these to justify dropping the Euclidean-vector branch.*
- **The grade formula `A² = (−1)^{r(r−1)/2}|A|²`:** already in `base.py`'s `exp` docstring; find its
  book source (likely Hestenes & Sobczyk or Macdonald) for the redo. ⬜

**When a citation is confirmed against the maintainer's copy, record author + title + section/equation here
and in the relevant docstring, and flip its box to ✅.**

## 6. Rotor vs versor, and why gacalc rotates with the *inverse* sandwich `R v R⁻¹` (not `R v R̃`)

> **This is the product-based route to a general rotation; it is not the only one.** The versor sandwich
> `R v R⁻¹` here is a **general rotation defined from the geometric product** (a versor *is* a product),
> so it presupposes the product — it is NOT a bootstrap of it. A **general rotation can also be defined
> from project/reject** via reduction to standard position, which presupposes no product and is
> non-circular (the bootstrap arc: 3 elementary plane rotations → project/reject → general rotation; see
> `tasks/reference/reduction-to-standard-position.md`). "Rotors = the general rotation" stays accurate —
> it's just the product-based view, not the foundation.

**Status: settled (vocabulary decided 2026-10-04/05; the Lean rotor chain and its Python mirror landed
2026-10-05 — §7).** Prompted by the maintainer noting that gacalc's sandwich uses `inverse`, not the
textbook `reverse`, and that gacalc's from-vectors "rotors" were not required to be unit — and asking
whether that is wrong or misnamed. Short answer: **it is correct, not a bug**; the terminology was the
only open point, and it is now fixed (below).

### The two sandwiches

For an even element `R` and a vector `v`:

- **Reverse sandwich `v ↦ R v R̃`** — the standard textbook formula (`R̃` = reverse). It is a *pure
  rotation* **only when `R` is a unit rotor** (`R R̃ = 1`). For a general `R` it also *scales* by
  `R R̃ = |R|²`:  `R v R̃ = |R|² · (R v R⁻¹)`.
- **Inverse sandwich `v ↦ R v R⁻¹`** — the *versor conjugation*. Since `R⁻¹ = R̃ / (R R̃)`, we have
  `R v R⁻¹ = (R v R̃) / |R|²` — the reverse sandwich with the `|R|²` scaling divided out. It is a pure
  rotation for **any** invertible even versor `R`, unit or not, and is **scale-invariant**:
  `(λR) v (λR)⁻¹ = R v R⁻¹` for `λ ≠ 0`, so the result depends only on `R`'s *direction*, never its
  magnitude.

For a **unit** rotor the two coincide (`R⁻¹ = R̃`), so the inverse sandwich **generalizes** the
textbook one rather than contradicting it. So the maintainer's proof is not wrong: `R v R⁻¹` is the
right, more general formula; `R v R̃` is its special case at `|R| = 1`.

### What gacalc actually does — and it is correct

- `MultiVectorBase.sandwich` (`base.py`) is `R x R⁻¹` (docstring: "Versor conjugation").
- `versor_from_vectors(a,b)` (`base.py`) deliberately builds the **un-normalized** even versor
  `R = |a||b| + b a` (scalar + bivector) and rotates via `R v R⁻¹`; its docstring already states that
  `R v R̃` would scale by `|R|²` and that `R⁻¹ = R̃/|R|²` divides it out — a pure rotation with **no
  normalization step**. That is a valid, deliberate design choice.
- The **exp / `plane_rotation`** path (§3) is the *other* branch: it builds a *unit* rotor
  `cos(θ/2) − sin(θ/2) i`, so there `R⁻¹ = R̃` and using `reverse` for the backward direction is a
  sound optimization (`transforms.py`). So gacalc uses **both** conventions — unit-rotor +
  reverse on the exp path, un-normalized-versor + inverse on the from-vectors path — with the general
  `sandwich` always using inverse. (§3's "`R R̃ = 1`, `v ↦ R v R̃`" wording describes the *unit* path;
  it is not the definition the general `sandwich` uses. Worth reconciling if §3 is ever revised.)

### Terminology — decided: *versor* = even, any magnitude; *rotor* = unit versor

In the GA literature a **versor** is any geometric product of non-null vectors; a **rotor** is the
special case of an *even, unit* versor (`R R̃ = 1`). The maintainer's decision (William Emerison Six
<billsix@gmail.com>; Python rename 2026-09-28, `tasks/archive/2026/10/04/rename-rotor-to-versor.md`;
Lean aligned 2026-10-05, `tasks/archive/2026/10/05/lean-unit-versors-rotors-sandwich-with-reverse.md`):

- **versor** — even, *any* magnitude. Python: class `Versor`, `versor_from_vectors` (the un-normalized
  `b·a + |a||b|`), `versor_rotation` (its inverse sandwich `R v R⁻¹`). Lean: `IsEvenVersor`,
  `versorFromVectors`, `sandwich`.
- **rotor** — a *unit* versor, the object of the textbook reverse sandwich `R v R̃`. Python:
  `rotor_from_vectors` (= the versor normalized), `_unit_bivector_rotor_factory`'s `rotor_for`
  (the half-angle `cos(θ/2) − sin(θ/2)·i`), `B.exp()`. Lean: `IsRotor`, `rotorFromVectors`, the 2D
  half-angle `Rotation2D.rotor θ`, `isRotor_expBivector*`.
- **full-angle rotor** — the 2D-only one-sided teaching operator `cos θ + sin θ·e₁₂` (§8). Lean:
  `Rotation2D.fullAngleRotor`; the book says "full-angle rotor".

Both notions are kept side by side on purpose; the versor proofs were never replaced by the rotor ones.

### Suggested Lean statements (the sandwich / composition story — written; status 2026-10-05)

Status: **done** in `proofs/GacalcProofs/` — (1) `sandwich_preserves_normSq`/`_dot` (`Sandwich.lean`); (2) scale-
invariance in the normalized form, `Rotor.rotorSandwich_normalize` (`(R/|R|) v (R/|R|)~ = R v R⁻¹`); (3) `IsRotor`,
`inverse_eq_reverse_of_isRotor`, `Rotation2D.sandwich_rotor_eq_rot` (`sandwich (rotor θ) v = rot θ v`); (4)
`sandwich_comp` (𝒢₃) and `Rotation2D.rotor_mul`. Plus the from-vectors link: `Rotor.rotorFromVectors_uvec`
(`versorFromVectors (uvec α) (uvec β)` normalized IS `rotor (β − α)`) and the Lagrange closed form
`normSq_versorFromVectors`. The original plan, kept for the record:

Prove in `G2` (standalone, reusing the landed elements/table), covering both the general and textbook
forms:

1. `sandwich R v := R * v * R⁻¹` is grade-preserving on vectors and **norm-preserving** (a rotation).
2. **Scale-invariance:** `sandwich (λ • R) v = sandwich R v` for `λ ≠ 0` — magnitude is irrelevant.
3. For the **unit** rotor `Rθ = cos(θ/2)·1 + sin(θ/2)·e₁₂`: prove `Rθ⁻¹ = R̃θ` (inverse = reverse when
   unit) and `sandwich Rθ v = rot θ v` — ties the sandwich to `rot`/`rotor` already proved.
4. **Composition:** `sandwich R₂ (sandwich R₁ v) = sandwich (R₂ * R₁) v`, and unit-rotor half-angles
   add (`Rθ₂ * Rθ₁ = R(θ₁+θ₂)`), so rotations compose by multiplying rotors.

This yields the general (inverse) result **and** the textbook (reverse, unit) special case in one file.

### Sources (2026-09-28 research pass)

- **Wikipedia, *Rotor (mathematics)*** — "a rotor is … the product of an even number of unit vectors
  and satisfies `R R̃ = 1`"; "the inverse of a [unit] rotor is its reverse." (Confirms rotor = unit.)
- **Dorst, Fontijne & Mann, *GA for Computer Science* (2007), ch. on versors/operators** — the versor
  sandwich `R x R⁻¹` (with grade involution for odd versors) as the general orthogonal-transform
  operator; rotors as the even, unit case. (Reference of record; the maintainer may not own it.)
- **Hestenes, *GA Primer*, "Rotors and Rotations in the Euclidean Plane"** — unit rotors and `v ↦ R v R̃`.
- **Definition of versor / "unity quasi-norm ⇒ rotor"** — general GA references (e.g. arXiv:1607.04767).
  URLs to be verified against the maintainer's own reading before promoting to docstrings (per §5's rule).

## 7. The rotor chain: the normalized versor IS a rotor, and the two sandwiches agree (2026-10-05)

The question that closed this section (the maintainer, 2026-10-05): "did you prove that the versor sandwich,
using the inverse, is the same as the rotor? like, starting from 'rotate from vector a to b', take the half
angle, the whole thing?" Yes, now — in Lean (`proofs/GacalcProofs/Rotor.lean`) and mirrored in sympy
(`tests/test_rotor_from_vectors.py`), without re-proving the projection-rotation story:

1. **The bridge, for every even `R` (no hypothesis):**
   `(R/|R|) v (R/|R|)~ = R v R̃ / |R|² = R v R⁻¹` — "the versor sandwich, divided by the magnitudes, is the
   rotor sandwich". Lean `rotorSandwich_normalize`; the one `√` fact is `|R|² = normSq R` (`normSq` is a sum
   of squares in both grades). Python: `rotor_from_vectors(a, b) = versor_from_vectors(a, b).normalize()`.
2. **So every versor theorem is a rotor theorem by one rewrite:** `rotorFromVectors a b` is a rotor
   (`isRotor_rotorFromVectors`), its reverse sandwich equals `projRotation` and `transforms.projection_rotation`
   (`rotorSandwich_rotorFromVectors_eq_projRotation`), carries `a` to `b` scaled to `|a|`
   (`…_carries_from_to`), and preserves dot/length (`rotorSandwich_preserves_*`).
3. **Lagrange gives the magnitude in closed form:** with `R = b·a + |a||b| = (|a||b| + a·b) + b∧a`,
   `|R|² = (|a||b| + a·b)² + |a∧b|²`, and Lagrange's `(a·b)² + |a∧b|² = |a|²|b|²` collapses it to

       |R|² = 2 |a||b| ( |a||b| + a·b )

   (`normSq_versorFromVectors`). So the versor is zero exactly when `a`, `b` are antiparallel or one is zero
   (`normSq_versorFromVectors_ne_zero`) — the geometric reading of the chain's `normSq R ≠ 0` guard.
4. **The half angle appears:** for unit vectors at angle θ, `|R|² = 2 + 2cos θ = 4cos²(θ/2)`, and the normalized
   versor is exactly the half-angle rotor `cos(θ/2) − sin(θ/2)·e₁₂` that `plane_rotation` builds. Lean (2D):
   `versorFromVectors (uvec α) (uvec β) = 2cos(θ/2) • rotor θ` and `rotorFromVectors_uvec = rotor (β − α)` for
   `cos(θ/2) > 0`, hence `rotorSandwich_rotorFromVectors_uvec : R̂ v R̂~ = rot (β − α) v`.

**Why the earlier Python attempt stalled, and the fix.** sympy cannot simplify `sqrt(|R|²)` from the raw
polynomial; equating a normalized coefficient to `cos(θ/2)` needs step 3 and the half-angle identity, neither of
which sympy discovers. The working proof parametrizes by the *half* angle — `(c, s) = (cos(θ/2), sin(θ/2))` as
positive symbols, `b = (2c² − 1)e₁ + 2sc·e₂` — and hands sympy the one relation `s² → 1 − c²`; then `|b| → 1`,
`|R|² → 4c²`, `sqrt → 2c`, and the rotor simplifies to `c − s·e₁₂` (`test_rotor_from_unit_vectors_is_the_half_angle_rotor_symbolic`).
See `tasks/reference/symbolic-equality.md` "Square roots".

## 8. The 2D teaching sequence: full-angle one-sided first, half-angle sandwich second (2026-10-05)

The book introduces rotation in 2D as a **one-sided, full-angle** product, `v ↦ v · (cos θ + sin θ·e₁₂)`
(`book/docs/geometric-product.rst`; Lean `Rotation2D.fullAngleRotor`, `vec_mul_fullAngleRotor`). This is
deliberate pedagogy (the maintainer, 2026-10-05): in two dimensions nothing lies outside the plane of
rotation, so no sandwich is needed and the angle is the whole angle — the intuitive first encounter. The
**half-angle sandwich** `R v R̃` with `R = cos(θ/2) − sin(θ/2)·e₁₂` (Lean `Rotation2D.rotor`,
`sandwich_rotor`) is then introduced and *proven equal in effect* (`sandwich_rotor_eq_vec_mul_fullAngleRotor`);
it is the form that survives into 3D, where a vector has a component perpendicular to the plane that a
one-sided product would send to a trivector. Both objects stay; only the names say which is which. The
name "full-angle rotor" was chosen from five candidates (`fullAngleRotor`, `oneSidedRotor`, `rightRotor`,
`complexRotor`, `turn`) as a throwaway label whose one job is to say what differs from the real rotor.

## Related

- `tasks/archive/2026/08/15/redo-exp-book-referenced.md` — the work (subtasks, status, open questions).
- `tasks/reference/galgebra-comparison.md` — galgebra vs gacalc (records that galgebra has no
  plane/rotor-from-vectors builder).
- `tasks/reference/generated-product-typing.md` — how graded overrides like `.i()` / `plane_of_rotation`
  get their precise return types from the generator.
