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
convention and duplicate `rotor_from_vectors` / `plane_rotation`.

- **`bivector_from_vectors(a, b) → a ∧ b`** (un-normalized) — the area bivector. Classmethod on
  `MultiVectorBase`, paralleling `rotor_from_vectors` (`base.py:867`). Validates grade-1; returns
  `a.outer_product(b)`. No parallel guard — the wedge of parallel vectors is the legitimate zero
  bivector.
- **`i(a, b) → normalize(bivector_from_vectors(a, b))`** — the unit bivector (`i² = −1`). The
  parallel-vectors guard lands here (normalizing zero raises `ZeroDivisionError`, gacalc ≥ 0.0.16).
  Classmethod on the **full** classes `Gn`/`G2`/`G3` (see placement).
- **`.i()`** — instance method on the graded `Bivector`/`Rotor` types, returning the value's unit
  plane. `Bivector.i() = self.normalize()`; `Rotor.i()` = the existing `plane_of_rotation()`
  (`g2.py:3211`, `r_vector_part(2).normalize()`), exposed under the `i` name.

**Placement / the name-clash resolution.** The full types (`Gn`/`G2`/`G3`) and graded types
(`Bivector`/`Rotor`) are **siblings** (all `@typing.final` subclasses of `MultiVectorBase`), so a
classmethod `i(a,b)` on the full classes and an instance `.i()` on the graded types do **not**
collide. Keep `i(a,b)` **off** the shared base (else the graded `.i()` shadows the inherited
classmethod), and don't put `.i()` on the full `G` classes. `bivector_from_vectors` *is* safe on the
base (no instance-method twin). **`plane_rotation` (`transforms.py:337-343`) already inlines exactly
`a∧b` + guard + normalize — refactor it to call these, one implementation.**

**Decided (William Emerison Six <billsix@gmail.com>, 2026-08-14):** the **`i(a,b)` classmethod goes on `Gn`, `G2`, `G3`, *and*
`Vector`** (a,b are vectors, so `Vector.i(a,b)` reads naturally); **`.i()` stays on the graded
`Bivector`/`Rotor` only.** A single class cannot carry both an `i(a,b)` classmethod and an `.i()`
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
galgebra's `Mv.exp` (`/foo/opt/galgebra/galgebra/mv.py:1218`, cosh/sinh for `sq>0`) without a book
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

## Related

- `tasks/archive/2026/08/15/redo-exp-book-referenced.md` — the work (subtasks, status, open questions).
- `tasks/reference/galgebra-comparison.md` — galgebra vs gacalc (records that galgebra has no
  plane/rotor-from-vectors builder).
- `tasks/reference/generated-product-typing.md` — how graded overrides like `.i()` / `plane_of_rotation`
  get their precise return types from the generator.
