# Lean GA proofs — architecture, techniques, and what's proven

**What this is:** the durable "how it's built" companion to `tasks/reference/lean-for-gacalc.md` (the
beginner orientation). It records the *architecture* of the from-scratch Lean proofs in
`proofs/GacalcProofs/`, the techniques that keep them tractable, and an inventory of what is proven.
Read this before extending the proofs. Updated in place (never archived).

**Status:** written 2026-09-29 (William Emerison Six <billsix@gmail.com>), harvesting the versor /
projection / algebra-law session. `make lean` green.

## The representation (settled)

- Each algebra `G2`/`G3` is a **coordinate struct** (`@[ext]`, one `ℝ` field per basis blade), with the
  basis blades exposed as genuine **elements** (`one`/`e_1`/…), NOT as real fields — a basis vector is
  a vector, not a real. (Inspiration: Mathlib `CliffordAlgebra` / pygae `lean-ga`; Wieser & Song,
  arXiv:2110.03551. See `lean-for-gacalc.md`.)
- **Correct-by-construction product:** `G3`'s `mul`/`wedge`/`reverse` were NOT hand-derived — they were
  emitted by running gacalc's `Gn` oracle on symbolic multivectors and transcribed verbatim. The
  derivation harness is **`tools/derive_lean_algebra.py [n]`** (promoted from an adhoc script; parallels
  `tools/gen_specialized.py`, which generates the *Python* specialized classes). The multiplication-table
  lemmas (`e_1_sq`, anticommutation, `I_sq`) then independently confirm the transcription.

## The key technique: leaf vs structural (the maintainer's "magnitude-squared" insight)

The proofs split into two layers, and keeping the split clean is what makes them short:

- **Leaf lemmas** connect a definition to the 8-field coordinate representation. Proved *once* by
  `ext <;> ring` (or `field_simp`): the multiplication table, `mul_assoc`/distributivity/`smul` laws
  (`AlgebraLaws.lean`), the `dot`/`wedge` bilinearity lemmas, `normSq_evenVersor`, `versorFromVectors_mul_reverse`
  (`R R̃ = normSq·1`), `normSq_mul` (multiplicative). These are the bridge; there is nothing below them.
- **Structural layer** — everything built on the leaves — is **coordinate-free `rw` chains**:
  `inverse` (`R̃/normSq`), `versorFromVectors_mul_inverse` (`R R⁻¹ = 1`), `sandwich_carries_from_to`,
  `sandwich_comp`, `sandwich_add`/`_smul`, `project_eq_sub_reject`, `reject_perp` (both dims).

The **squared magnitude** `normSq = ⟨A Ã⟩` (NOT the `√` magnitude — proofs stay squared to avoid `√`)
and the `dot`/`wedge` **bilinearity lemmas** are what enable this. Concrete example: G2 `reject_perp`
went from a `vec`-form `field_simp` bash to `rw [dot_sub_left, proj, dot_smul_left]; field_simp; ring`
— coordinate-free and general in `a, b`. **Write proofs structurally; let only the leaves touch
coordinates.** (Follow-up audit: `tasks/archive/2026/09/30/lean-proofs-make-coordinate-free.md`.)

**Coordinates only when needed — and this governs the STATEMENT, not just the proof
(2026-10-03).** State a theorem over **objects** — a vector/multivector `(a b : G3)` with an
`IsVector` hypothesis — rather than over its real coefficients `(a1 a2 a3 : ℝ)`, *unless coordinates
are genuinely required*. Coordinates are fine when they are what's needed (a leaf/bridge lemma proved
by `ext <;> ring`; a fact that is inherently about components); they are not a default. An
object-level theorem is proved by dropping to its coordinate leaf once (`eq_vec_of_isVector`), so the
reader cites the object form while a single coordinate leaf underneath carries the computation. The
test: *do we need the coordinates here?* If not, don't expose them in the statement. (Mirror of
gacalc's Python side; see `CLAUDE.md`.)

**The per-theorem judgment (A/B/C) when a theorem takes `ℝ` arguments.** Ask what each `ℝ` arg *is*:

- **A — coordinate-free object.** The fact is structural (holds by algebra — bilinearity, assoc,
  `IsVector`). State it `{a b : G_n} (ha : IsVector a) …` and prove it with `rw`/property lemmas, no
  field access. Best. (E.g. `G3.mul_eq_dot_add_wedge`, the `sandwich_*` properties.)
- **B — object-in, pull-coords.** The fact is geometric but the proof needs the coordinate
  computation. Take the object + `IsVector`, then `obtain ⟨hs, …⟩ := ha` and
  `simp only [defs, those field-zeros]; ring` — the *statement* speaks objects; only the proof touches
  coordinates. (E.g. the perp/parallel `_dot` lemmas; `G2.dot_is_sym_part`/`wedge_is_antisym_part`.)
  **This is THE form: geometric objects in, scalars in the body, geometric objects out** (in = the
  theorem's parameters, out = its conclusion, in-the-body = the proof). The theorem takes the object and
  concludes about objects; only the body `obtain`s it to the getters and computes. Do **NOT** take free scalars `(a1 a2 a3 : ℝ)` and *construct*
  `vec a1 a2 a3` inside — that inverted "scalars in, build the object" shape is the thing being removed
  (maintainer, 2026-10-03). So **do not mint a separate scalar-taking `_coord` leaf** (`foo_coord (reals) :
  P (vec reals)` bridged by `foo {obj} := by have h := foo_coord …; rwa [← eq_vec] at h`); fold the
  computation into the object theorem via `obtain`. **Share through OBJECT theorems, not scalar leaves** —
  a composite (`sandwich_preserves_cos`) composes the object `dot`/`magnitude` isometries directly (zero
  coords), which is also why the "sharing" that made `_coord` leaves look load-bearing dissolves once the
  whole chain is object-form. A named `_coord` leaf is justified ONLY for a genuinely fragile coordinate
  proof (`set`/`calc`/big `field_simp`) kept verbatim AND shared by ≥2 object theorems; otherwise inline.
  (`rw [eq_vec_of_isVector ha]` to reuse an existing vec-literal proof is a lighter alternative to `obtain`,
  but it re-mentions `vec a.c1 a.c2 a.c3`; prefer `obtain` so no object is reconstructed.) Corpus-wide
  conversion record + per-file inventory + reusable recipes:
  `tasks/archive/2026/10/04/lean-object-in-getters-out-proof-style.md` (DONE for the polynomial tier
  2026-10-04; the sqrt/`magnitude`/degree-blowup/delicate tier keeps its coordinate core by decision).
- **C — genuine `ℝ`, keep.** (c1) a *pure scalar identity* with no GA object in the statement
  (`Lagrange.lean`'s `lagrange_2d`/`lagrange_3d`); or (c2) the `ℝ` is an irreducible scalar
  *parameter* — a rotation's `cos`/`sin`, a scalar multiple `k` — not a vector coordinate (lift only
  the vector args, if any; keep the scalar). A *coordinate-computation leaf* whose RHS is an explicit
  computed coordinate-vector (`rotXY_vec`-style `= vec (c*x−s*y) …`) also stays coordinate.

**Versor components are NOT a C-keep — they lift (B), 2026-10-03.** The `ℝ` tuple `(s c12 c13 c23)` of a
`sandwich (evenVersor s c12 c13 c23) …` theorem is the *versor's own coordinates*, and an even versor is a
geometric object, so these lift exactly like vector coordinates: state `{R : G_n} (hR : IsEvenVersor R)
(hr : normSq R ≠ 0)` and bridge with `eq_evenVersor_of_isEvenVersor` (the versor twin of
`eq_vec_of_isVector`). `IsEvenVersor R` = the grade-0+2 predicate (`R.c1 = … = 0`, pseudoscalar too in G3);
it does **not** fix the magnitude — a *rotor* is a unit versor, tracked in
`tasks/lean-unit-versors-rotors-sandwich-with-reverse.md`. The whole `sandwich_preserves_*` family is in
object-versor form, getter-native (`tasks/archive/2026/10/04/lean-object-in-getters-out-proof-style.md`).
(This revises the earlier note that listed "a versor component" under C.)

**Grade-structure predicates (the general pattern).** The same lift applies to any coordinate tuple that is
really a *grade-pure object's* own components. Three predicates now exist, each with an `eq_…_of_is…` bridge
(the `eq_vec_of_isVector` analogue) and an `is…_…` companion: **`IsVector`** (grade 1), **`IsEvenVersor`**
(grades 0+2, `Sandwich.lean`), **`IsBivector`** (grade 2, `G3.lean`). So a `bivector p q r` plane argument
lifts to `{B : G3} (hB : IsBivector B) (hBn : normSq B ≠ 0)` exactly as a versor does (the `Projection3D`
plane-projection cluster, Increment 16). Reach for a new such predicate whenever a theorem's reals are a
grade-pure object's coordinates.

Prefer A, then B; fall to C only for genuine scalars. The corpus-wide application is **DONE for the
polynomial tier** (2026-10-04) and recorded in
`tasks/archive/2026/10/04/lean-object-in-getters-out-proof-style.md` (which absorbed the earlier
statement-lift task). It was a cascade-aware, bottom-up incremental sweep (converting a signature breaks
its callers, so `make lean`-verify each step). **Final outcome:** every *polynomial*-proof theorem is now
object-in / getters-in-body (Sandwich, Reflect, G3 self-products, Projection2D, Projection3D 3/4, Trig
`lagrange_property`, RotateComponents `rotation_preserves_dot`, the pure-poly ProjectionRotation scaffold);
the **coordinate core is retained by decision** for the non-polynomial tier — sqrt/`magnitude`/
`normalizeVec` proofs, the divide-by-`normSq(a∧b)` degree-blowup plane projections, the cos/sin/angle and
literal-then-instantiate exceptions, and the delicate `calc`/`set` capstones (`projRotation_eq_sandwich`/
`_isometry`, bisector machinery, `reject_vec_eq`, `cos_sq_add_sin_sq`, `sin_between_eq_abs_signed_vec`,
CrossStandardPosition) — those public statements are already object-in, only their private scaffold stays
coordinate. Pushing that tier (optional) is `tasks/push-delicate-coordinate-core-tier.md`.

**Nonzero guard for angle/trig theorems (2026-10-03).** A theorem stated through `cos_between` /
`sin_between` (or any `/ (|a| |b|)` quotient) carries nonzero hypotheses — `magnitude a ≠ 0`,
`magnitude b ≠ 0` (equivalently `normSq a ≠ 0`, or `a ≠ zero`). This is what makes the trig form
**faithful**: with a nonzero denominator `cos = 0 ⟺ dot = 0` (and `sin = 0 ⟺ wedge = 0`), so the
`0/0` junk case (Lean's `x/0 = 0`) is excluded and the cosine/sine statement is exactly as strong as
the dot/wedge primitive — not the weaker claim it would be without the guard. The `cos = 0` proof
often closes by `zero_div` without consuming the hypothesis, so the guard is a "gate for meaning"
(name it `_`-prefixed to keep the unused-variable linter quiet); it still prevents the theorem from
being applied to a zero vector. The Python angle methods mirror this by **raising** on a zero operand
(the angle is undefined), rather than returning `0/0 → 0`.

## File organization & naming (convention, 2026-10-03)

The proofs are organized **by topic** (one concept per file: projection, rotation, sandwich, cross,
measures, grade projection, …), mirroring the Python library's one-concept-per-file layout and the
book — NOT by algebra. `G2.lean`/`G3.lean` hold only each algebra's from-scratch core (struct, `mul`,
basis, leaf lemmas); concept files build on them and keep both dimensions together where the concept
is small/cross-dimensional (`AlgebraLaws`, `Measures`, `Trig`, `Exp`, `GradeProjection`, `Lagrange`).

Naming rule: a dimension-specific file is suffixed `2D`/`3D`; a bare name means "both dimensions" or a
concept that exists in only one dimension (no sibling to confuse it with). **Paired** concepts are
both suffixed — `Projection2D`/`Projection3D`, `Rotation2D`/`Rotation3D`,
`ProjectionRotation2D`/`ProjectionRotation3D`, `Predicates2D`/`Predicates3D`. Solo-dimension files stay
bare (`Cross`, `Reflect`, `Normalize`, `StandardPosition`, … are 3D-only; `TrigEquiv`, `Versor2D` are
2D-only). The root `GacalcProofs.lean` imports every topic file; renaming one means updating that
import list, any sibling `import`, **and any prose pointer in these reference docs**.

**G2 `dot`/perpendicularity:** `G2.dot` (and its bilinearity algebra) lives in `Versor2D.lean`, not
`G2.lean` (which imports only Mathlib). The `dot`-form perpendicularity lemmas over `IsVector` objects
go in `Predicates2D.lean` (the 2D twin of `Predicates3D.lean`): e.g. `dual_perp_dot` —
`dot (dual v) v = 0` — the object form of the coordinate leaf `G2.dual_vec_perp` (which stays in
`G2.lean` as the bridge it rests on).

**Naming: the geometric name is the student-facing (cosine/sine) theorem; the dot/wedge form carries a
`_dot` suffix (2026-10-03).** Cosine is an implementation detail, so the theorem a reader cites is
named for the geometry — `dual_perp`, `cross_perp_left`, `reject_perp`, `parallel_smul`, … (stated as
`cos_between … = 0` / `sin_between … = 0`, in `StudentTrigForms.lean`) — and the underlying
scalar-product fact it rests on is the `_dot` lemma (`dual_perp_dot`, `reject_perp_dot`,
`cross_perp_left_dot`, …). NOT a `_cos`/`_sin` suffix on the geometric theorem.

**Student-facing sine/cosine forms (`StudentTrigForms.lean`) rest on, never replace, dot/wedge.**
`cos_between a b = dot a b / (|a| |b|)`, and the division carries a subtlety: in Lean/Mathlib
`x / 0 = 0` (junk value), so for a zero vector `cos_between = 0/0 = 0` — true but meaningless (the
angle is undefined). Thus `dot a b = 0 → cos = 0` always, but `cos = 0 → dot = 0` only for nonzero
`|a|, |b|` — **`cos = 0` is logically weaker than `dot = 0`** (same for `sin = 0` vs `wedge = 0`). So
the `cos`/`sin` corollaries in `StudentTrigForms.lean` are each proved FROM their dot/wedge lemma
(`simp only [cos_between, <lemma>, zero_div]`), inheriting the primitive's full strength; the dot/wedge
form is kept as the robust underlying fact. This is also why the Python predicates (`is_orthogonal_to`
/ `is_parallel_to`) keep their dot/wedge *implementation* and only present cosine/sine in prose —
reimplementing as `cos == 0` would import the `0/0` degeneracy. (`CLAUDE.md` › "Presenting to
students".)

**Grade-projection form:** G2's `rVectorPart` is written as a linear combination of the basis blades
(`add (smul a.c1 e_1) (smul a.c2 e_2)`, …, the Lean mirror of gacalc's "build from the basis
constants"); G3's stays a coordinate struct-literal — its grade-2 arm would be a noisier nested
three-term `add`, and the basis form would push proof churn into `Contractions.lean`. Per-case per the
"spike decides each case" rule: basis form only where it reads better and doesn't cost proof health.

## Leaf-node index (the coordinate bridge — reuse these, don't re-derive inline)

Every proof should reach for a *named* leaf, not a fresh `ext <;> ring`. The leaves, by category
(2D `G2` + 3D `G3` unless noted):

- **Multiplication table:** `e_1_sq`/`e_2_sq`/`e_3_sq`, `e_1_mul_e_2`/…, `e_2_mul_e_1` (anticommute),
  `e_12_mul_e_3`, `I_sq` (`I² = −1`), `reverse_reverse`.
- **Algebra laws** (`AlgebraLaws.lean`): `mul_assoc`, `mul_add`/`add_mul`, `one_mul`/`mul_one`,
  `smul_mul`/`mul_smul`, `smul_smul`, `one_smul`, `vec_anticomm_perp`.
- **Inner product `·`:** `dot_comm` (symmetry); **full bilinearity** — `dot_add`/`dot_sub`/`dot_smul`
  in both `_left` and `_right` forms; `dot_vec` (`a·b = a₁b₁+…`); `dot_self_vec_eq_normSq`
  (`a·a = |a|²` — the bridge that reads a `dot a a` hypothesis as the `normSq` primitive).
- **Outer product `∧`:** **full bilinearity** — `wedge_add`/`wedge_sub`/`wedge_smul` in both `_left` and
  `_right` forms; `wedge_antisymm` (`a∧b = −(b∧a)`), `wedge_self_vec` (`a∧a = 0`), `wedge_vec_eq_biv`
  (`a∧b` = the plane-bivector literal in coordinates).
- **The split:** `vec_mul_eq_dot_add_wedge` (`ab = a·b + a∧b`, coordinate-literal form) and its
  arbitrary-vector form `mul_eq_dot_add_wedge` (over the `IsVector` grade-1 predicate, with
  `eq_vec_of_isVector` the bridge to a literal); the orthogonal corollaries `vec_mul_perp` /
  `mul_eq_wedge_of_perp` (`a⊥b ⟹ ab = a∧b`). G2 + G3 (G2's split lives in `Projection2D.lean`, where
  `dot` and `wedge` are both in scope). `IsVector` is closed under the operations used to build a
  rejection: `isVector_vec`, `IsVector.smul`, `IsVector.sub`.
- **Blade inverse (vectors):** `reverse_vec` (`reverse` fixes a vector), `mul_vec_self` (`a a = |a|²·1`),
  and `mul_vec_inverse_self` (`a a⁻¹ = 1` for `|a|² ≠ 0`) — the `B B⁻¹ = 1` identity that turns a
  Hestenes `(…)a⁻¹` proof structural. With these, `plane_eq_wedge` (`a (b − proj_a b) = a∧b`) and
  `reject_vec_eq` (`(b∧a)a⁻¹ = b − proj_a b`) are now structural `rw`-chains on the split, not
  `field_simp` bashes.
- **Magnitude (squared is the primitive):** `normSq_vec` (`|a|² = a₁²+…`), `normSq_wedge_vec`
  (`|a∧b|² = …`), `normSq_evenVersor`, `versorFromVectors_mul_reverse` (`R R̃ = |R|²·1`), `normSq_mul`
  (multiplicative); `magnitude_sq_vec` (`|a|² = a₁²+…` via `normSq_vec` under the `√`). There is **one**
  magnitude concept — `magnitude = √normSq`, all grades; the old vector-only `mag = √(a·a)` was deleted
  and unified into `magnitude` (2026-09-29).
- **Sin/cos & Lagrange** (`Trig.lean`): `lagrange_property` (`(a·b)²+|a∧b|² = |a|²|b|²`),
  `cos_between`/`sin_between`, `cos_sq_add_sin_sq` (`cos²+sin²=1`), and `sandwich_preserves_cos` /
  `sandwich_preserves_sin` — a rotation preserves the cosine AND sine, hence the whole angle,
  coordinate-free (G2 + G3).
- **Sandwich isometry leaves** (`Sandwich.lean`): `sandwich_preserves_dot`; the outermorphism
  `sandwich_preserves_wedge` (`(RuR⁻¹)∧(RvR⁻¹)=R(u∧v)R⁻¹`); `normSq_smul`; the pure-`ring` cores
  `normSq_reverse_sandwich` (`|RvR̃|²=|R|⁴|v|²`) and `normSq_reverse_sandwich_wedge` (grade-2 twin);
  the isometries `sandwich_preserves_normSq_of_vec` (`|RvR⁻¹|²=|v|²`) and
  `sandwich_preserves_normSq_of_wedge` (`|R(u∧v)R⁻¹|²=|u∧v|²`); `magnitude_sandwich_vec`.
- **Duals / pseudoscalar:** `I_inv`, `I_mul_I_inv`, `dual`, `dual_wedge_perp_left`/`_right`.

**Note:** the squared magnitude `normSq_vec` is *the* "|a|²" primitive — "a vector dotted with itself"
is not its own leaf; route it through `normSq` (and phrase nondegeneracy as `normSq (vec a) ≠ 0`).

**Note (versor-hypothesis convention, 2026-09-29; object-form update 2026-10-03):** every sandwich lemma
states its nondegeneracy as the versor's squared magnitude — "R is invertible" — **never** the raw
coordinate sum `s²+c12²+… ≠ 0`. The object form is `normSq R ≠ 0` (for `{R} (hR : IsEvenVersor R)`); the
coordinate `_coord` leaf states `normSq (evenVersor …) ≠ 0`, and the coordinate sum is recovered inside a
proof only where `field_simp` needs it (`rw [normSq_evenVersor] at hr`). Likewise the grade-2 isometry
leaves are stated on `wedge u v`, not a bivector-coordinate literal. This is the interface half of the
"carry the meaningful quantity, not a coordinate sum" rule.

## Other techniques worth reusing

- **The even-versor bridge.** `versorFromVectors_eq_evenVersor` proves the a→b versor `= evenVersor …`
  (it is even: scalar + bivector). This lets the *general* `evenVersor` results (isometry
  `sandwich_preserves_dot`, `sandwich_fixes_own_bivector`/`_normal`) apply to the *actual* rotation
  `versorFromVectors a b` by instantiation — no re-proof.
- **Literal-then-instantiate, to avoid degree blow-up.** A coordinate proof about `a∧b` blows up
  (`field_simp` cross-multiplies degree-4 denominators → timeout) because `a∧b`'s entries are quadratic
  in `a,b`. Fix: prove the fact for a **literal bivector** `⟨0,0,0,0,p,q,r,0⟩` (free `p,q,r`, low degree),
  then instantiate at `a∧b`. Used in `proj_plane_eq_project_onto` (via `reject_eq_proj_normal`,
  `project_eq_sub_reject`).
- **Matrix-free rotation.** "Rotates the oriented angle correctly" = *oriented isometry*: preserves the
  dot (angle magnitude) AND fixes the plane bivector (orientation). With "carries a→b" that pins the
  rotation — **no rotation matrix, no double angle** needed. (`RotateComponents.lean`.)
- **`field_simp` gotchas.** (1) Provide the nonzero denominator in the form `field_simp` normalizes to
  (usually `^2` sums); it matches up to `ring`-normalization but not always across two different
  denominators — **unify denominators first** (e.g. `dot(dual B)(dual B) = normSq B`) to avoid a
  degree-8 blow-up. (2) `reverse` emits `-0` in negated slots; `simp` won't reduce `√(…-0…) = √(…0…)`,
  so peel with `congr 1; ring`. (3) A `G3`/`G2` algebra-law lemma name (`mul_smul`, `smul_smul`,
  `mul_one`, `one_smul`, `mul_assoc`) **clashes with Mathlib's ℝ version** — fully-qualify the G3/G2 one
  (`GacalcProofs.G3.mul_smul`) in `rw` chains.

### Converting coordinate proofs to object/getter form — paths that DON'T work (2026-10-03)

Lessons from the "geometric objects in, scalars in the body, geometric objects out" refactor (take
`{a : G3} (ha : IsVector a)`, `obtain ⟨…⟩ := ha`, compute on `a.c1`, `a.c12`, … — not scalar args +
`vec`/`evenVersor` reconstruction). Three dead ends, each with the fix that does work:

- **DON'T reference an object leaf that is defined textually below its consumer.** A composite's object
  proof `rw [leaf hR hv]` fails with *"Unknown identifier `leaf`"* if the object `leaf` sits lower in the
  file (e.g. in an end-of-namespace wrapper block). Lean resolution is top-down; the DAG being acyclic is
  not enough. **Fix:** convert each `_coord` leaf **in place** — rewrite its body to `obtain`-getters and
  rename it (drop `_coord`) where it already sits — and delete the end-block duplicate. Because the
  `_coord` definitions are already ordered leaf-before-composite, in-place conversion keeps the order
  correct for free; no leaf needs moving.

- **DON'T prove a divide-by-`normSq` fact by a direct getter unfold.** For anything with `inverse` in it
  (dot/normSq/wedge preservation under the *full* `sandwich R v R⁻¹`), the tactic
  `obtain …; simp only [normSq, mul, reverse, <zeros>] at hr ⊢; field_simp [hr]; ring` leaves
  **`unsolved goals`**: the sandwich contributes `(normSq R)²` in the denominator, the getter unfold
  **expands** it (`s⁴+2s²c²+c⁴`), and `field_simp` can't match the expansion to `hr : normSq R ≠ 0`. The
  old `_coord` proofs only worked because `normSq_evenVersor` keeps `normSq R` *grouped* (`s²+c²`) and
  never expands it. **Fix (the atomic-`normSq` leaf recipe):** state a leaf on the *reverse* sandwich
  `R v R̃` (no inverse) whose RHS keeps `normSq R` **atomic** — e.g. `normSq_reverse_sandwich`
  (`|R v R̃|² = normSq R ² · |v|²`), `dot_reverse_sandwich` (`(R u R̃)·(R v R̃) = normSq R ² · (u·v)`),
  `wedge_reverse_sandwich`. Prove the leaf by `obtain`-getters + pure `ring`/`ext` (no division). Then the
  composite pulls the inverse's `1/normSq R` out (`mul_smul`), collects it through the bilinear op
  (`normSq_smul`, `dot_smul_left/right`, `wedge_smul_left/right`), rewrites by the leaf, and `field_simp
  [hr]` cancels the now-**atomic** `normSq R`. No "fighter" class remains — every division proof reduces
  this way.

- **For a divide-by-`dot d d` / `normSq d` proof where `d` is a vector argument**, the clean
  denominator-nonzero hypothesis is `have hdd : d.c1^2 + d.c2^2 + d.c3^2 ≠ 0 := by rw [← normSq_vec,
  ← eq_vec_of_isVector hd_isv]; exact hd` — this gives the **grouped `^2` form** `field_simp` normalizes to.
  Do **not** derive it by `simpa only [normSq, mul, reverse, <zeros>] using hd`: that yields the raw
  `d.c1*d.c1 - 0*-0 - … ` form, which neither matches a stated `^2` goal (a `have` type-mismatch) nor
  `field_simp`'s normalized `^2` denominator (leftover `(…)⁻¹`, `ring` then fails). Worked:
  `Reflect.normSq_reflectVec`.
- **DON'T assume an operation's helper lemmas live in the grade's main file.** `dot` for `G2` is defined
  in `Versor2D.lean`, not `G2.lean`, and so are `G2.dot_smul_left/right` — a `grep … G2.lean` falsely
  concluded "G2 lacks them." **Fix:** grep the whole `proofs/GacalcProofs/` tree (or `rg`), never a single
  file, before concluding a lemma is missing.

## Hestenes projection / rejection (uniform, all grades)

gacalc's `project`/`reject` (base.py; Hestenes & Sobczyk p.18 eqs 2.9) are two formulas, uniform for a
vector or bivector blade `B`:

- `project_B A = (A · B) B⁻¹` — the component of `A` in `B`.
- `reject_B A = (A ∧ B) B⁻¹` — the component of `A` orthogonal to `B`.

Lean status: `proj`/`reject`/`project_onto` cover vector- and bivector-blades in 3D
(`Projection3D.lean`) and 2D (`Projection2D.lean`); `project_add_reject` (`(A·B)B⁻¹ + (A∧B)B⁻¹ = A`) is
the validating decomposition; `proj_plane_eq_project_onto` shows the normal-based plane projection
equals the Hestenes form. The blade inverse `B⁻¹` is `Sandwich.inverse` (`B̃/(B B̃)`, works for a simple
bivector: `B · inverse B = 1`).

**Terminology (maintainer, 2026-09-29):** the `·` here is **Hestenes' inner product**
`A·B = ⟨AB⟩_{|r−s|}` (defined for all grades in *Clifford Algebra to Geometric Calculus*, 1984) — for a
vector·bivector it is the grade-1 part (`inner_vb`, a vector), NOT the scalar `dot` (grade 0, which is
0 here). It is **not** the "left/right contraction," a later, slightly different notion (Lounesto;
Dorst–Fontijne–Mann); the two coincide for vector·bivector, hence are easy to conflate. gacalc's `<`/`>`
*are* genuine contractions (Taylor 2021) — a separate, intentional part of the library.

## Magnitude (Hestenes)

- `normSq A = ⟨A Ã⟩₀` — the **squared magnitude** `|A|²` (H&S p.13 eq 1.49, gacalc `magnitude_squared`;
  `⟨AÃ⟩ = ⟨ÃA⟩` as the scalar part is symmetric). The workhorse of the versor layer.
- `magnitude A = √(normSq A)` — the magnitude, correct for **all** grades. This is the **single**
  magnitude concept: the older vector-only `mag = √(A·A)` (wrong sign for a bivector) was deleted and its
  uses folded into `magnitude` (2026-09-29). `normSq`/`magnitude` live in `G2.lean`/`G3.lean` (below the
  algebra, above every consumer).

## Inventory (files in `proofs/GacalcProofs/`, 2026-09-29)

- `Lagrange.lean` — Lagrange identity 2D/3D (`|a|²|b|² = (a·b)² + |a∧b|²`).
- `G2.lean` / `G3.lean` — the algebras: product/wedge/reverse, basis elements, multiplication table,
  `I² = −1`, dot, dual, `I⁻¹`; `normSq`/`magnitude` (+ `normSq_vec`, and `normSq_wedge_vec` in `G3`);
  `G3` also the fundamental identity `ab = a·b + a∧b` (`vec_mul_eq_dot_add_wedge`) and `vec_mul_perp`.
- `AlgebraLaws.lean` — associativity, distributivity, identity, scalar compatibility, `smul_smul`,
  `one_smul`, ⊥-anticommutation, for both algebras.
- `Sandwich.lean` — `inverse`/`sandwich` (`normSq`/`magnitude` moved down to `G2`/`G3`); the sandwich is an isometry
  (`sandwich_preserves_dot`, length); fixes its own plane bivector and normal; the versor is invertible
  (`R R̃ = |R|²`, `R R⁻¹ = 1`); rotations compose (`sandwich_comp`); the even-versor bridge. Also the
  **reverse anti-automorphism** `reverse_mul` (`(ab)~ = b~ a~`, general) and its vector corollaries
  `reverse_of_isVector`, `reverse_mul_vec` (`(ab)~ = ba`), `reverse_mul3_vec` (`(abc)~ = cba`); the G2
  twins (`reverse_mul`/`reverse_vec`/`reverse_of_isVector`/`reverse_mul_vec`) live in `G2.lean`.
- `Rotation2D.lean` (2D angle-parameterized), `Rotation3D.lean` / `Versor2D.lean` (angle-free
  versor-from-vectors: bisector, `R·a = |a|·h`, `b·R = |b|·h`; the carries-a→b capstone
  `R a R⁻¹ = (|a|/|b|)·b`).
- `RotateComponents.lean` — the three matrix-free rotation goals for the actual a→b rotation (in the
  plane, oriented isometry, perpendicular fixed) + `sandwich_ahat` (â↦b̂).
- `Projection3D.lean` / `Projection2D.lean` — Hestenes `proj`/`reject`/`project_onto`, `project_add_reject`,
  `proj_plane = project_onto`, and the 2D cases.
- `StandardPosition.lean` — elementary coordinate-plane rotations `rotXY`/`rotXZ` (NOT versors),
  their `preserves_dot`, projection/rejection equivariance under them, the explicit `b ↦ |b|·e₁`
  alignment (`rotate_b_to_e1` + magnitude form), and the product-from-projection payoff
  (`mul_eq_proj_dot_add_reject_wedge`). This is the base of the **bootstrap arc** (3 elementary plane
  rotations → project/reject/product/cross via reduce-to-2-D → a general rotation from project/reject;
  see `tasks/reference/reduction-to-standard-position.md`). The uniform 3-rotation tool is in
  `CrossStandardPosition.lean` (below).
- `CrossStandardPosition.lean` — the uniform reduce-both-to-2-D tool: `rotYZ` (the 3rd plane rotation,
  e₂e₃ about `e₁`) + toolkit; `reduceToPlane` (`reduceToPlane_a_on_e1` / `reduceToPlane_b_in_plane` —
  both vectors into the e₁e₂ plane); equivariance of proj/reject/cross under all three rotations
  (`proj_rotYZ_equivariant`, `vecReject_rotXZ/YZ_equivariant`, `cross_rotXY/XZ/YZ_equivariant`); and the
  2-D evals `proj_reduced`/`vecReject_reduced`/`cross_reduced` — project/reject/cross all through the one
  3-rotation frame.
- `ProjectionRotation3D.lean` — the arc's **step 3**, a general rotation from project/reject:
  `projRotation f t v = (project_{f∧t} v)·f̂·t̂ + reject_{f∧t} v` (mirrors Python
  `transforms.projection_rotation`; non-circular — project/reject + the product, no versor), with
  `projRotation_carries_from_to` (carries from→to) and `projRotation_perp` (⊥ part fixed). Its two deep
  properties: **isometry** `projRotation_isometry` (`normSq (projRotation f t v) = normSq v`), with
  scaffold `normSq_add`/`normSq_add_of_orthogonal`/`normSq_mul_vec`/`inplane_perp_reject`/
  `project_perp_reject`/`plane_pythagorean` (`magnitude² = normSq` squares the √'s away, the cross term
  dies by orthogonality, no Lagrange); and **route-equivalence** `projRotation_eq_sandwich`
  (`projRotation f t v = sandwich (versorFromVectors f t) v`, route P = route V), with lemmas
  `versor_mul_project_eq` (in-plane `R P = P R̃`), `versor_mul_reject_comm` (⊥ `R Rⱼ = Rⱼ R`),
  `normalizeVec_mul_versor_eq_reverse`/`vec_mul_bisector_eq`/`normalizeVec_to_mul_versor_eq_bisector`
  (`f̂ t̂ = R̃ R⁻¹`). √-free: `R`'s scalar `|f||t|·1` is handled abstractly via `R R⁻¹ = 1`, never expanded.
- `ProjectionRotation2D.lean` — the **𝒢₂ specialization** of step 3: the same `projRotation` triple
  (`projRotation_carries_from_to` / `projRotation_isometry` / `projRotation_eq_sandwich`) in 2D, the
  degenerate base case where the `f∧t` plane is all of 𝒢₂, so `reject_plane_eq_zero` (`reject = 0`)
  collapses it to the rotor action `v·f̂·t̂` (`projRotation_eq_vec_mul`). Reuses
  `Versor2D`/`Sandwich`/`Projection2D`/`AlgebraLaws` lemmas; the one √ stays confined to `key_reverse_sq`.
  The 2D isometry needs only `normSq f, normSq t ≠ 0` (from `normSq_mul_three_vec` + unit `f̂`/`t̂`,
  independent of route-equivalence). Registered via `import` in the root `GacalcProofs.lean`.
- `Cross.lean` — the 𝒢₃ `cross a b = (a∧b) I₃⁻¹`: `cross_vec` (coordinate formula), `cross_anticomm_vec`,
  `cross_perp_left`/`_right`, `dual_vec` (3D vector dual = ⊥ bivector), and `dot_cross_eq_signedVolume`
  (scalar triple = signed volume = `det[a,b,c]`). Plus `Sandwich.sandwich_evenVersor_vec_isVector`
  (the even-versor sandwich of a vector stays a vector — grade-preserving).

Remaining (see the umbrella `tasks/investigate-lean-proofs-for-ga.md`): the Mathlib-rotation
*equivalence* proofs, the dot/wedge/pseudoscalar step-tasks' 3D from-rotation derivations.

## Coverage map (public method → Lean coverage)

Every public math method in `src/gacalc/{base,vectorcalc,measure}.py` against the theorems in
`proofs/GacalcProofs/*.lean` (audited 2026-10-01, William Emerison Six <billsix@gmail.com>, from
reading the actual theorems — not grep substrings). HAS = a theorem states the operation's defining
property; PARTIAL = only a special case or an adjacent fact; NONE = no theorem. The "→ task" column
names the `lean-proof-*` task filed for a genuine gap (or the existing task that already owns it).
Counts (updated 2026-10-02): **29 HAS, 2 PARTIAL, 1 NONE** (32 methods). The 7 gap tasks this audit
filed were all proven in Lean and archived 2026-10-02 (`tasks/archive/2026/10/02/lean-proof-*.md`),
flipping 10 NONE→HAS and 3 PARTIAL→HAS; only general `content` remains NONE (blocked on the general-`Gn`
layer). (Originally 16/5/11 at the 2026-10-01 audit.)

**Correction to the earlier menu:** `vectorcalc.cross` and the 3D vector `dual` were wrongly listed
as gaps — `Cross.lean` proves both (`cross`/`cross_vec`/`cross_anticomm_vec`/`cross_perp_left`/`_right`
and `dual_vec`). Both are HAS.

| Method (`base.py` unless noted) | Coverage | Theorem(s) / file — or task |
| --- | --- | --- |
| `magnitude` / `magnitude_squared` | HAS | `magnitude`, `normSq`, `normSq_vec`, `magnitude_sq_vec`, `normSq_wedge_vec`, `normSq_mul`, `magnitude_sandwich_vec` (G2/G3, Sandwich) |
| `normalize` | HAS | `normalizeVec`, `magnitude_normalizeVec`/`normSq_normalizeVec` (= 1) (Normalize.lean) |
| `inner_product` (general graded) | PARTIAL | only vector·bivector `inner_vb` (Projection:132); general `⟨AB⟩_{\|r−s\|}` owned by existing `lean-general-gn-product-and-hestenes-dot-wedge` |
| `dot` | HAS | G3 `dot`/`dot_vec`/`dot_comm` + bilinearity; G2 `dot` (Versor2D), `dot_is_sym_part`, `dot_eq_coord_sum` (in-progress `lean-proof-dot-product`) |
| `outer_product` / `wedge` | HAS | `wedge`, `wedge_vec_eq_biv`, `wedge_antisymm`, full bilinearity (G2/G3) |
| `scalar_product` | HAS | the scalar part `⟨AB⟩₀`; vector case via `dot` / `dot_is_sym_part` |
| `left_contraction` | HAS | `leftContraction_vec_vec` (= dot), `leftContraction_scalar_vec` (grade-0 inclusion) (Contractions.lean) |
| `right_contraction` | HAS | `rightContraction_vec_vec` (Contractions.lean) |
| `r_vector_part` | HAS | `rVectorPart`, `rVectorPart_idem`, `rVectorPart_complete` (GradeProjection.lean) |
| `is_orthogonal_to` | HAS | `perp_iff_mul_eq_wedge` (`a·b=0 ⟺ ab=a∧b`) (Predicates3D.lean) |
| `is_parallel_to` | HAS | `wedge_parallel_smul` + the wedge-zero criterion (Predicates3D.lean); Python `is_parallel_to` fixed to the wedge-zero form |
| `reverse` | HAS | `reverse_reverse`, `reverse_mul` (anti-automorphism), `reverse_vec`, `reverse_of_isVector`, `reverse_mul_vec` |
| `inverse` | PARTIAL | blade/versor cases: `mul_vec_inverse_self`, `mul_biv_inverse_self`, `mul_triv_inverse_self`, `versorFromVectors_mul_inverse`, `inverse_mul`; general mixed-grade owned by existing `lean-general-multivector-inverse` |
| `dual` | HAS | G2 `dual_vec`; G3 `dual`, `dual_vec` (Cross:50), `dual_wedge_perp_left`/`_right` |
| `even_part` | HAS | `evenPart`, `even_add_odd` (GradeProjection.lean) |
| `odd_part` | HAS | `oddPart`, `even_add_odd` (GradeProjection.lean) |
| `cosine` | HAS | `cos_between`, `cos_sq_add_sin_sq`, `sandwich_preserves_cos`, `cos_between_uvec` (TrigEquiv) |
| `abs_sin` | HAS | `sin_between`, `sin_between_eq_abs_signed_vec`, `signed_sin_between`(`_uvec`) (TrigEquiv), `sandwich_preserves_sin` |
| `project` / `projected_onto` | HAS | `proj`, `project_onto`, `project_add_reject`, `proj_plane_eq_project_onto` (Projection/Projection2D) |
| `reject` / `rejected_away_from` | HAS | `reject`, `reject_perp`, `reject_vec_eq`, `project_add_reject` |
| `reflect` / `reflected_across` | HAS | `reflectVec` (= proj − reject), `reflectVec_eq`, `normSq_reflectVec` (isometry) (Reflect.lean) |
| `versor_from_vectors` | HAS | `versorFromVectors`, `versorFromVectors_mul_reverse`/`_inverse`, `sandwich_carries_from_to`, `bisector` (Rotation3D/Sandwich) |
| `bivector_from_vectors` | HAS | the raw wedge `a∧b`: `wedge`, `wedge_vec_eq_biv` |
| `sandwich` | HAS | `sandwich`, `sandwich_preserves_dot`/`_normSq`/`_wedge`/`_cos`/`_sin`, `sandwich_comp`, isometry (Sandwich/RotateComponents) |
| `exp` | HAS | `expBivector`/`expBivectorGeneral` (= `cos\|B\|+sin\|B\|·B̂`), `normSq_expBivectorGeneral` = 1 (unit versor/rotor) (Exp.lean) |
| `vectorcalc.cross` | HAS | `cross`, `cross_vec`, `cross_anticomm_vec`, `cross_perp_left`/`_right` (Cross) |
| `measure.area` | HAS | `area_sq_vec` (= `normSq (a∧b)`), `normSq_wedge_eq_lagrange` (Measures.lean) |
| `measure.volume` | HAS | `volume_sq_vec` (= `signedVolume²`) (Measures.lean) |
| `measure.signed_area` | HAS | `signedArea` (= a₁b₂−a₂b₁), `signedArea_sq` (`\|signed_area\| = area`) (Measures.lean) |
| `measure.signed_volume` | HAS | `dot_cross_eq_signedVolume` (= `det[a,b,c]`) (Cross) |
| `measure.content` (general `n`) | NONE | deferred — needs the general-`Gn` layer (`lean-general-gn-product-and-hestenes-dot-wedge`); k=2,3 are the proven `area`/`volume` |

Gaps already owned by an existing task (NOT re-filed): general graded `inner_product`
(`lean-general-gn-product-and-hestenes-dot-wedge`), general mixed-grade `inverse`
(`lean-general-multivector-inverse`); `dot`/`wedge`/pseudoscalar 3D-from-rotation derivations
(`lean-proof-dot-product`, `lean-proof-wedge-product`, `lean-proof-pseudoscalar-square-sign`,
`lean-proof-rotation-from-scratch`). Gap tasks filed from this audit — reflect, contractions, exp,
normalize, measures, grade-projection, predicates — were **all proven and archived 2026-10-02**
(`tasks/archive/2026/10/02/lean-proof-*.md`); only general `content` remains (blocked on the
general-`Gn` task above).
