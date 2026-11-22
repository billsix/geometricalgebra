# Lean proofs: fit to the book and the Python (review record)

**Date:** 2026-11-22 (William Emerison Six <billsix@gmail.com> asked for it). **Frozen:** this is a
dated snapshot; do not edit it. Act on it through `tasks/lean-proofs-fit-cleanup.md`, which
cites its sections.

## The question

> take a look at all lean proofs that we made, and tell me if you think they are written as
> they should be, or if there are any extraneous ones, from your understanding of the book, and
> python code. read everything in the repo.

## Method and limits

- Three readers, one per slice, each read every line of its Lean files (37 files, about 7,700
  lines in all) and the Python modules, book pages and notebooks those files mirror. Their
  reports are sections A, B and C below, unedited except for heading levels and two scratch
  paths. Each states what it read in full and what it skimmed.
- **Nothing was compiled.** Every "could be proved structurally", "can be deleted" and "the
  hypothesis follows from another" is a lead from reading, to be confirmed by a build.
- "Dead" claims rest on `git grep` over `proofs`, `book`, `notebooks`, `src`, `tests`, `tools`.
  The main thread re-ran the grep for a sample and it held: the six theorems of
  `RotateComponents.lean` have no mention outside the file; `Rotation3D.vec_mul_mul_self` has
  none; `notebooks/proof-projection.py` carries the 𝒢₃ twin tag though
  `StandardPosition2D.lean` has the 𝒢₂ theorem; `proofs/README.md` says 34 modules;
  `Contractions.leftContraction` subtracts in ℕ; `notebooks/defining-g2.py` says "every
  dimension".
- Not read: the parts of the repo no proof mirrors (the GL toolkit, the ePiX scene helpers,
  the generator, most tests), and `entrypoint/`.
- The usage counter `tasks/adhoc/lean-proofs-fit-review/lean_usage.py` matches short names, so
  a 𝒢₂ theorem and its 𝒢₃ namesake hide each other; it undercounts unused theorems. The readers'
  namespace-aware counts supersede it.
- Earlier records this one builds on: `tasks/review/2026/11/08/repo-review.md` §7 and
  `tasks/lean-proofs-remove-extras.md`. Each slice says which of their findings are fixed and
  which remain.

## Summary

**The mathematics is right.** Definitions agree with the Python in sign, side, inverse versus
reverse and half versus full angle; the 𝒢₃ product, wedge and reverse were re-derived from
`tools/derive_lean_algebra.py` with no mismatch; every Lean name the book cites exists.

**The corpus is not written the way its own rules say, in the older files.** It is several
developments written at different times. The files from the last few weeks (`Bootstrap2D`,
`Rotor`, `PlaneRotation3D`, `ProjectionRotation2D`, the reciprocal frames) are in house form.
`ProjectionRotation3D`, `RotateFromTo2D`, `RotateComponents`, parts of `G1`/`G3` and
`CrossStandardPosition` still take free reals, keep one-consumer `_coord` leaves, and prove by
`ring` identities whose stated reason is a two-line chain.

**There is extraneous material.** Whole-file candidates: `RotateComponents.lean`,
`Lagrange.lean`, `Normalize.lean`. Large unused blocks: the 13 object wrappers at the end of
`ProjectionRotation3D.lean`, the `IsScalar` apparatus, 13 of the 14 `StudentTrigForms`
theorems (the book cites the `_dot` forms), nine lemmas in `CrossStandardPosition.lean` with no
capstone. The same fact is proved up to four times (`R * R̃ = |R|²` for the from-vectors versor).

**Three places differ from the book or the Python with no theorem between them:** Lean's `dot`
is Python's `scalar_product`, not the Hestenes `dot`; `Contractions.leftContraction` returns the
scalar part where Python returns zero; the standard-position rejection and the frame's peel
inverse are defined by different formulas than the book's and Python's.

**The book has outrun Lean in a few places:** reflection (the sandwich form, the involution,
all of 2D), `exp(−(θ/2) * i)` as the rotor, the bridges between the rotation developments, and
`e₁ * e₁₂ = e₂`.

## A. The algebra core

Reviewed 2026-11-22, read-only. Nothing in the repo was edited, staged or built. No `lake build`,
no `make`.

### What was read, and how

**Read in full (every line, statements + doc comments + proof bodies):** `G1.lean`, `G2.lean`,
`G3.lean`, `Lagrange.lean`, `GradeProjection.lean`, `Contractions.lean`, `GeneralInverse.lean`,
`Measures.lean`, `Cross.lean`, `Predicates2D.lean`, `Predicates3D.lean`, `GeometryObjects2D.lean`,
`Normalize.lean`, `MathlibBridge.lean`.

**House rules read in full:** `tasks/reference/lean-ga-proof-architecture.md` (all 877 lines),
`algebra-teaching-order.md`, `lean-python-notebook-workflow.md`, `tasks/lean-proofs-remove-extras.md`,
`tasks/review/2026/11/08/repo-review.md` section 7, and the named `CLAUDE.md` sections.

**Python:** `measure.py`, `vectorcalc.py`, `tools/derive_lean_algebra.py` in full. `base.py`: read in
full the parts these proofs mirror (`pseudoscalar_squared_sign`, `magnitude`/`magnitude_squared`/
`normalize`, `inner_product` … `r_vector_part`, the `is_*` predicates, `is_orthogonal_to`,
`is_parallel_to`, `reverse`, `inverse`, `dual`, `even_part`/`odd_part`, the `area`/`volume`/
`signed_*`/`cross` pass-throughs); **skipped** the LaTeX helpers (lines 58-512), the operator
dunders, `cosine`/`abs_sin`, `project`/`reject`/`reflect`, the versor/rotor/`exp` methods and
`isclose` (other slices' subject). `gn.py`: **skimmed** (definition list + a grep for Lean citations;
it has none).

**Book:** all eleven `.rst` pages read in full, except the middle of `cheat-sheet-3d.rst`
(projection/reflection/rotation/frames rows: skimmed). **Notebooks: skimmed, not read in full** —
headings, every line mentioning Lean/theorem/"every"/identity, and the claim-bearing sections of
`defining-g2.py`, `levels-of-abstraction.py`, `vector-addition.py`, `three-dimensions.py`. The code
cells were not read line by line.

**Mechanical checks run (outputs in the scratchpad, repo untouched):**

- `tools/derive_lean_algebra.py 2` by eye against `G2.mul`/`G2.wedge`/`G2.reverse`: identical.
- `scratchpad/cmp3.py`: parses `G3.mul` and `G3.wedge` out of `G3.lean` and subtracts the oracle's
  `derive_lean_algebra.py 3` output with sympy: 16 fields compared, 0 mismatches.
- `scratchpad/usageA.py` + `filterA.py`: a **namespace-aware** mention table for every declaration
  in these 14 files. The supplied `lean_usage.txt` matches short names across namespaces, so
  `G2.wedge_antisymm` looks "used" because `G3.wedge_antisymm` is. The namespace-aware table finds
  many more consumer-less theorems than the 27 the supplied report lists for these files. Every
  "unused" claim below was then confirmed with a direct `grep -n` over `proofs/GacalcProofs/*.lean`
  and over `book/docs notebooks src tests tools README.md proofs/README.md`.

Confidence words: **certain** = read the theorem and grepped; **lead** = a claim that needs a build to
confirm (I could not build).

---

### 0. Prior findings for these files: still present or fixed

From `tasks/review/2026/11/08/repo-review.md` §7 and `tasks/lean-proofs-remove-extras.md`.

| Prior finding | Status now |
|---|---|
| §7.1 `Predicates3D` proves only one direction of `a∧b=0 ⟺ a∥b` | **FIXED** — `parallel_of_wedge_eq_zero` and `wedge_eq_zero_iff_parallel` exist in `Predicates3D` and `Predicates2D`; `base.py` `is_parallel_to` cites them correctly |
| G1: `vec_mul`, `wedge_vec`, `vec_mul_eq_dot_add_wedge`, `mul_vec_inverse_self` take free reals; `G1.IsVector` defined and never used | **STILL PRESENT** (all four; `IsVector` still has zero uses in `G1.lean`) |
| G2 `dual_vec_perp` unused; `Predicates2D` doc wrongly says `dual_perp_dot` rests on it | **STILL PRESENT** (both the theorem and the two doc sentences) |
| G3 `vec_mul_perp` unused | **FIXED** (removed) |
| Measures: `signedArea` defined over four reals | **STILL PRESENT** |
| Duplicates inside G3: `wedge_self_vec_coord`, `mul_vec_self_coord`, `dot_self_vec_eq_normSq_coord`, `vec_mul_eq_dot_add_wedge` twins | **STILL PRESENT** — and the consumers still call the `_coord` twin, see §1 |
| `normalize` (Rotor) vs `normalizeVec` (Normalize) | **STILL PRESENT** |
| Teaching order: `G2.sub_mul` outside G2; G3 `zero_mul`/`add_zero`/`zero_add` outside G3 | **FIXED** (all in their algebra file) |
| Teaching order: no addition laws; distributivity before identity | **FIXED** in G2/G3 (not in G1, see §1) |
| Teaching order: G3 defines `dot` after the laws | **FIXED** |
| Doc: G3 `vec_anticomm_perp` names the wrong lemma | **FIXED** (doc matches the proof) |
| Doc: `Predicates2D` says `dot` is defined in `Versor2D.lean` | **STILL PRESENT** (module doc) |
| Doc: `Predicates3D` cites a note that does not exist | **STILL PRESENT** — `wedge_parallel_smul`'s doc still says "See the module note on the Python `is_parallel_to`'s narrower `cosine == 1`"; no such note, and Python no longer does that |
| Doc: G2 malformed "`mul e_1*e_2`" | **STILL PRESENT** (`e_12`'s doc comment) |
| `area_sq_vec`'s `IsVector` hypotheses look unneeded (lead) | **STILL PRESENT, now certain** — see §3 |
| remove-extras #1: `G2.eq_scalar_of_isScalar` ends in a no-op `<;> ring` | **STILL PRESENT** |

---

### 1. Written as they should be?

#### 1.1 Definitions against the Python — the good news first

- **`mul`, `wedge`, `reverse` (G1/G2/G3)** match the `Gn` oracle exactly (checked mechanically, above).
- **`dual := mul a I_inv`** with `I_inv = −I` matches `base.dual` (`A * I⁻¹`), including signs: Lean
  `G2.dual_vec (x,y) = (y,−x)` ↔ doctest `e_1.dual(2) == -e_2`; `G3` `dual_vec (x,y,z) =
  bivector (−z) y (−x)` ↔ `e_1.dual(3) == -(e_2*e_3)`; `e_12.dual(3) == e_3`.
- **`cross := dual (wedge a b)`** matches `vectorcalc.cross`; `cross_vec` is term for term the
  docstring's coordinate formula (right-handed).
- **`normSq = ⟨A Ã⟩₀`** vs Python `⟨Ã A⟩₀`: equal (scalar part is symmetric), and the doc says so.
- **`area`/`volume`** = magnitude of the wedge, same fold order `(a∧b)∧c` as `outer_product_of_vectors`.
- **`rVectorPart`/`evenPart`/`oddPart`**, **`normalizeVec`**, **`I_sq_eq_sign`** (the same closed form
  as `pseudoscalar_squared_sign`, r = 1, 2, 3) all match.

#### 1.2 Definitions that do NOT match what the Python/book compute

1. **Lean `dot` is Python's `scalar_product`, not Python's `dot`.** `base.dot` is
   `inner_product`: the Hestenes product `Σ_{r,s≥1} ⟨A_r B_s⟩_{|r−s|}`, a *multivector*, with grade 0
   excluded (the cheat sheets say "a scalar part contributes 0"). Lean `dot a b := (mul a b).s` is
   `⟨AB⟩₀ : ℝ`. They agree only for two vectors. Examples where they differ: `dot (scalar 2)
   (scalar 3)` is 6 in Lean, 0 in Python; vector·bivector is 0 in Lean, a vector in Python and on
   both cheat sheets. The `def`'s own doc comment is honest ("The scalar product ⟨A B⟩₀ … for two
   vectors the Euclidean dot"), but other text is not:
   - `GradeProjection.dot_eq_rVectorPart_zero` (G2 and G3): "**The dot product is the grade-0 part
     of the geometric product** … Holds for all multivectors." For Python's and the book's dot that
     sentence is false; it is true of the scalar product.
   - `G3.lean` header "Inner-product (dot) leaf lemmas".
   - `Contractions.lean` contrasts the contraction with "the Hestenes dot (`inner_product`)" while
     the only `dot` in Lean is the other thing.
   Not a wrong theorem. It is a name that means something different from the same name one layer up.
   Cheapest fix: reword those comments to "scalar product" and state at the `def` that it equals
   `a.dot(b)` only for vectors. (The general Hestenes product is the known PARTIAL row.)

2. **`Contractions.leftContraction k m a b := rVectorPart (m − k) (mul a b)` is not Python's
   `left_contraction`.** Three gaps:
   - `m − k` is `ℕ` subtraction, so for `k > m` it is `0` and the definition returns the **scalar
     part**, where Python (and Taylor) return **zero** ("zero whenever m − k < 0"). For genuinely
     homogeneous operands of different grades the scalar part happens to vanish, so the values agree,
     but that is an unproved fact the definition leans on, and no theorem states it.
   - `k`, `m` are free arguments tied to `a`, `b` by nothing; Python reads the grades off the
     operands and sums over all grade pairs.
   - Only vector⌋vector and scalar⌋vector are proved. The two cases the Python docstring leads with
     — `e_1 ⌋ (e_1*e_2) = e_2` (a vector out of a plane) and `(e_1*e_2) ⌋ e_1 = 0` — have no theorem.
   𝒢₃ only; no 𝒢₂. Nothing else in the corpus uses these definitions.

3. **`Measures.G2.signedArea (a1 a2 b1 b2 : ℝ) := (mul (vec a1 a2) (vec b1 b2)).c12`** — four reals
   in, built from `mul` not `wedge`. Its 3D sibling `Cross.signedVolume (a b c : G3) := (wedge (wedge
   a b) c).c123` takes objects and uses the wedge. Python's `signed_content` is
   `(a₁∧…∧aₙ).dual(n).scalar_part()`. Consequences: `MathlibBridge.G2.wedge_eq_det` has to say
   `(wedge a b).c12 = det` because it cannot name `signedArea`, while the 3D bridge says
   `signedVolume a b c = det`; and no theorem connects either Lean definition to the dual form Python
   actually computes (see §4).

4. **`area` exists only in 𝒢₃.** Every doctest of `measure.area`/`signed_area` is 𝒢₂, and
   `cheat-sheet-2d.rst` lists "area = |a∧b|" and "signed area = a₁*b₂ − a₂*b₁". There is no
   `G2.area`, and no `|signed area| = area` in either dimension except the squared 3D
   `volume_sq_vec`.

#### 1.3 Statements that take free reals and build `vec …` inside

Leaving aside the definitional unfold leaves the rules allow (`normSq_vec`, `dot_vec`, `cross_vec`,
`dual_vec`, `wedge_vec_eq_biv`, `normSq_wedge_vec`, `reverse_vec`, `lagrange_2d/3d`, `signedArea_eq`):

- **`G3.lean` — object theorem exists, consumers still use the scalar leaf.** This is the inverted
  shape the rule removes, and none of the four is "fragile" (each is a one-line `ring`):
  | scalar leaf | its object twin | who uses which (grep) |
  |---|---|---|
  | `wedge_self_vec_coord` | `wedge_self_vec` | leaf: `Projection3D` ×1. Object twin: **nobody** |
  | `mul_vec_self_coord` | `mul_vec_self` | leaf: `Projection3D`, `StandardPosition`, `ProjectionRotation3D`. Object twin: **nobody** |
  | `dot_self_vec_eq_normSq_coord` | `dot_self_vec_eq_normSq` | leaf: `Projection3D` ×2, `StandardPosition` ×2. Object twin: `ReciprocalFrame3D` ×1 |
  | `vec_mul_eq_dot_add_wedge` | `mul_eq_dot_add_wedge` | leaf: `Projection3D` ×1. Object twin: 3 files + 2 book pages |
  `mul_vec_self_coord` also still concludes `smul (normSq …) one`, against the "embed a scalar with
  `scalar`, not `smul k one`" rule its object twin follows.
- **`G2.vec_mul (u1 u2 v1 v2)`** — RHS is a raw struct literal `⟨u1*v1+u2*v2, 0, 0, u1*v2−u2*v1⟩`;
  no Lean use (one doc mention in `TrigEquiv`). It is the module doc's headline bullet, restating
  `mul_eq_dot_add_wedge` + `dot_vec`.
- **`G2.dual_vec_perp (x y)`** — reals in, concludes on `.s` not `dot`; dead (see §2).
- **`G1`**: `vec_mul`, `wedge_vec`, `vec_mul_eq_dot_add_wedge`, `dual_vec`, `mul_vec_inverse_self`
  take a real and build `vec x`; `G1.IsVector` is defined and never used. G1 has no consumers, so
  this costs nothing downstream, but G1 is billed as "the teaching twin" and it teaches the shape the
  other two files were converted away from.
- **`Measures.G2.signedArea`** and its two theorems (§1.2 item 3).

#### 1.4 Raw coordinates leaking into statements

- **`⟨0, 0, 0, 0⟩` where `G2.zero` exists.** `G2.wedge_self_vec`, `G2.wedge_isVector_isBivector_eq_zero`,
  all three `Predicates2D` wedge theorems, and the default arm of `G2.rVectorPart` write the literal.
  `G2.zero` was added 2026-11-09 and the G3 twins all say `zero`. `GeometryObjects2D` (newer) uses `zero`.
- **`G2.dot_eq_coord_sum`** concludes about `(mul a b).s`, not `dot a b` — the file's own definition
  of `dot` is 260 lines above it.
- **`I_sq_eq_sign`** (G1/G2/G3) is stated on `(mul I I).s`; the object statement `mul I I = neg one`
  is `I_sq`. Tolerable (it exists to display the formula), noted for completeness.

#### 1.5 Brute `ext <;> ring` where a structural chain would show the reason

Ordered by how much the reason matters to the book.

1. **`Predicates2D.dual_perp_dot`** — `simp only [dot, dual, I_inv, mul, hs, h12]; ring`. The book
   page `dual.rst` exists *to make the point that this needs no coordinates*: "Nothing in the
   argument used coordinates: only associativity, the square of a vector, and which part of a product
   is the plain number." Every leaf that chain needs is already in `G2.lean` (`mul_assoc`,
   `mul_vec_self`, `scalar_mul`). The Lean proof is the one thing on that page's trio that does not
   follow the page. (Same remark for `dual_wedge_perp_*_dot` in `Projection3D`, not my file.) The
   statement also has the operands the other way round from the page (`dot (dual v) v` vs
   `a · (a * I⁻¹)`); harmless, but the twin is not literal.
2. **`G2.vec_anticomm_perp`** — `obtain`, unfold, `linear_combination 2 * h`. Its G3 twin is the
   three-`rw` structural proof (`mul_eq_wedge_of_perp` twice + `wedge_antisymm`). G2 has all three
   lemmas, stated above it. The two "twins" should have the same proof; G2's doc even describes the
   structural argument.
3. **`dot_is_sym_part` / `wedge_is_antisym_part` (G2 and G3)** — full unfold + `ring`. Both follow
   from `mul_eq_dot_add_wedge`, `dot_comm` and `wedge_antisymm`, which is *why* they are true. As
   written, `G2.wedge_antisymm` and `G2.wedge_self_vec` have no consumer at all.
4. **`wedge_parallel_smul` (2D and 3D)** — is `wedge_smul_right` then `wedge_self_vec`.
5. **`Cross.cross_anticomm`** — is `wedge_antisymm` under `dual` (needs a `mul (neg x) y` lemma that
   does not exist yet). `cross_perp_left_dot`/`_right_dot` are brute too, but there the brute form is
   defensible.
6. **`Measures.area_sq_vec`, `volume_sq_vec`, `Normalize.normSq_normalizeVec`** each re-derive
   `√x² = x` by hand (`Real.sq_sqrt` on a freshly proved nonnegativity). `magnitude_sq_eq_normSq` and
   `normSq_nonneg` have been in `G3.lean` since 2026-10-05 for exactly this.
7. **`GeneralInverse.G3.gradeInvolution_conjProduct_comm`** — the module doc gives the reason ("a
   scalar plus a pseudoscalar … commutes with everything") and the file proves the grade fact
   (`conjProduct_grades`), then proves the commutation by expanding a cubic in 8 variables and never
   uses `conjProduct_grades`. A `mul I a = mul a I` lemma (also missing for the 3D cheat sheet, §4)
   would let it be the stated argument. Lower priority: the rest of that file is a model of the
   structural style.
8. Small: `G2.I_sq` re-proves `e_12_sq` (`I` is `e_12` by definition; `G1.I_sq := e_1_sq` does it
   right). `G3.I_sq_eq_sign`'s doc says "read off `I_sq`" but the proof re-unfolds `mul`.

Not complaints: the algebra laws, the multiplication table, bilinearity, `GeometryObjects2D` and
`MathlibBridge` are genuine coordinate facts and `ext <;> ring` is right for them.

#### 1.6 `rw [eq_vec_of_isVector …]` instead of `obtain`

The architecture doc calls this the lighter, less preferred form ("it re-mentions `vec a.c1 a.c2
a.c3`; prefer `obtain`"). Still used in: `G2.wedge_antisymm`, `G3.wedge_antisymm`,
`Measures.area_sq_vec`, `Normalize.normSq_normalizeVec`, `MathlibBridge.G3.toF_cross`,
`MathlibBridge.G3.signedVolume_eq_det`. The two Mathlib ones are reasonable (they reuse
`cross_vec`); the other four are not needed.

#### 1.7 File order against `algebra-teaching-order.md` and the architecture doc

The architecture doc says "all three share one top-to-bottom shape". They do not:

- **G2 is the outlier.** After the laws it goes: multiplication table → `vec_mul` alone under a
  header named "Dot and wedge as the parts of the geometric product" → all grade predicates → the
  dot/wedge leaves and object facts → `I_sq` under "Duals and the pseudoscalar" → `I_inv`/`dual`
  under a second dual header → reverse facts → `mul_vec_self`. G3 (and the doc) put `I_inv`/`dual`
  right after the laws, the dot and wedge leaves before the predicates, and the object facts last.
  In G2 `e_12_sq` is in the table and the identical fact `I_sq` is 220 lines later.
- **Magnitude facts sit under "### The algebra laws"** in both G2 and G3 (`normSq_eq_sum_sq`,
  `normSq_nonneg`, `magnitude_sq_eq_normSq`, `magnitude_ne_zero_of_normSq_ne_zero`, and in G2 also
  `normSq_vec`, `eq_smul_basis`, `vec_eq_smul`). The doc's order has "magnitude (+ its √ facts)"
  *before* the laws. G2 has no "### Magnitude" header at all.
- **G1 was left behind by the 2026-11-09 pass.** No `sub`/`neg`; no addition laws (`add_comm` …); no
  `mul_one`/`add_mul`; the laws come after the multiplication table; `dot` is defined after
  magnitude, not with the product. If G1 is the warm-up a reader meets first (teaching-order
  principle 6), it is the file that least follows the order.
- `mul_zero` is absent from G2 and G3 (only `zero_mul`); every other law has both sides.
- G3 has `IsVector.smul`/`IsVector.sub`; G2 has neither, and `Bootstrap2D.lean` grew its own
  `isVector_smul_of_isVector` under a different name.
- `Measures.lean` puts `namespace G3` before `namespace G2`; every other two-dimension file goes 2D
  first.
- `Cross.lean` holds `G3.dual_vec` (the 3D twin of `G2.dual_vec`, which is in `G2.lean`) and
  `signedVolume` (a measure; `Measures.lean` imports `Cross` to get it).

#### 1.8 Stale or wrong doc comments (beyond the three carried over in §0)

- **`GeneralInverse.lean` module doc:** "for a vector each equals the `Ã / |A|²` inverse." Only 𝒢₂
  has `generalInverse_eq_inverse_of_isVector`. There is no 𝒢₃ theorem.
- **`Predicates2D.lean` imports `Versor2D`** and uses nothing from it (`dot`, `dual`, `wedge`, `smul`
  are all `G2.lean` since 2026-10-28). **`MathlibBridge.lean` imports `Projection2D`**, apparently
  for the same historical reason. Both are **leads**: I read the files, I could not build.
- **`G2.lean` module doc** says the dot "equals the coordinate sum (`dot_eq_coord_sum`), i.e. …
  Mathlib's inner". The theorem that actually proves that is `MathlibBridge.G2.dot_eq_inner`, which
  does not use `dot_eq_coord_sum`.
- **`G2.dual_vec_perp` doc** cites `dot_eq_coord_sum` as if it defined the dot.
- **`MathlibBridge.lean` module doc:** "the umbrella task's decisions 4 and 6". In the current
  "Program decisions" list, 4 is the bridge and 6 is rotor-vs-versor. **Lead** (the numbering may be
  the archived umbrella's; I did not open it).
- **`MathlibBridge.toC_rot_rot` doc:** "(`rot_add` ↔ `Orientation.rotation_rotation`)". The proof is
  `rw [toC_rot, toC_rot]`; it uses neither and proves nothing about angle addition.
- **History in module docs** (the "comments describe the present" rule): `Cross.lean` ("Promotes
  three symbolic-unit-test identities … see `tasks/archive/…`"), `Normalize.lean` and
  `Predicates3D.lean` ("From the coverage-map gap audit"), `MathlibBridge.lean` ("decision
  2026-09-28"), `GeneralInverse.lean` (a dated, signed decision). All cited paths exist.
- `Normalize.lean` and `Predicates3D.lean` never close their namespace; the other files do.

#### 1.9 Twin tags

`notebooks/dual.py` carries `twin: GacalcProofs.G2.dual_perp_dot`; the theorem in `Predicates2D.lean`
does not. By the workflow doc's own orphan check (a tag that appears once) it is an orphan. The
`GeometryObjects2D` six and `G2.mul_assoc`/`mul_add` are correctly paired.

---

### 2. Extraneous

"Dead" = no proof uses it and no reader-facing file names it (grep over `proofs book notebooks src
tests tools` and the READMEs found only the declaration, or only doc-comment mentions).

#### 2.1 Dead, and I would delete or fold (high confidence)

| Declaration | Why |
|---|---|
| `Lagrange.lagrange_2d`, `lagrange_3d` (the whole file) | No proof uses either. `Trig.lagrange_property` (2D and 3D, object form, the one other proofs use: 9 mentions outside its declarations) is proved without them. Only mentions: `CLAUDE.md`, the architecture doc, a doc comment in `Trig.lean` ("reference: `Lagrange.lean`") and one in `RotateComponents.lean` ("from `lagrange_3d`", which is not how that file proves it). The file's doc says "the identity the book uses"; no book page or notebook cites it. Counter-argument: `CLAUDE.md` names it as the model C1 "pure scalar identity" and Program decision 2 is about it. If kept, `Trig.lagrange_property` should be *proved from it* so it earns its place. |
| `G2.dual_vec_perp` | Reals in, `.s` out, zero uses; superseded by `Predicates2D.dual_perp_dot`, whose doc wrongly claims to rest on it. |
| `Normalize.normSq_normalizeVec`, `magnitude_normalizeVec` | Superseded: `Rotor.G3.normalize` has the **same definition** as `G3.normalizeVec` (`smul (1 / magnitude a) a`) and `Rotor.G3.normSq_normalize` proves `= 1` for **any** multivector with no `IsVector` hypothesis. Neither Normalize theorem has a consumer (the 26 uses of `normalizeVec` in `ProjectionRotation3D` use the *definition* only). Keep one definition, one theorem. |
| `Measures.area_sq_vec` | It is `magnitude_sq_eq_normSq (wedge a b)` with two hypotheses it does not need (§3). No consumer. |
| `Measures.normSq_wedge_eq_lagrange` | `Trig.lagrange_property` rearranged by `linarith`. No consumer. |
| `G2.vec_mul` | Struct-literal restatement of the split; no consumer. |
| `G2.normSq_wedge_vec` | No consumer — `ReciprocalFrame2D` declared its own copy `normSq_wedge_vec'` instead (prior finding). One of the two should go. |
| `G2.dot_eq_coord_sum` | The object form of `dot_vec`, stated on `.s`; no consumer (the two 2D files that need the fact call `dot_vec`). Its advertised role, the bridge to `inner`, is done by `MathlibBridge.dot_eq_inner` without it. |
| `MathlibBridge.toC_rot_rot` | `toC_rot` applied twice; no consumer, no citation. |

#### 2.2 Consumer-less scaffolding (medium confidence — a judgment call for the maintainer)

The `IsScalar` apparatus has **no consumer anywhere** in either algebra: `G2`/`G3` `IsScalar`,
`eq_scalar_of_isScalar`, `isScalar_scalar`, `isScalar_one`, `isScalar_mul_self_of_isVector`. Likewise
`G2.eq_smul_e12_of_isBivector`, `G2.isBivector_e12` (the same fact as `isBivector_I`, which *is*
used), `G2.isBivector_wedge_of_isVector`, `G3.isBivector_bivector`, `G3.isTrivector_trivector`,
`G3.eq_trivector_of_isTrivector`. That is 2 definitions and 14 theorems.

They were added on purpose (2026-10-28, "mirror Python's `is_*`"). My read: the *predicates* are
worth having because Python has them. The recognizers and bridges are an API built ahead of any
caller. The two grade-of-result lemmas are the interesting ones and are not extraneous at all — they
are uncited (§4, category c).

#### 2.3 Leaves used only through an avoidable path

`G3.wedge_self_vec_coord`, `mul_vec_self_coord`, `dot_self_vec_eq_normSq_coord`,
`vec_mul_eq_dot_add_wedge`: live (9 call sites in `Projection3D`, `StandardPosition`,
`ProjectionRotation3D`), but each call site could use the object twin, after which all four are dead.

#### 2.4 "Mentioned nowhere else" in the supplied report — one verdict each

(a) = worth stating in its own right; (b) = extraneous; (c) = should be cited and is not.

| Theorem | Verdict |
|---|---|
| `Contractions.leftContraction_vec_vec`, `rightContraction_vec_vec` | (a) — they are the docstring line "For two vectors it is the dot product" of `left_contraction`/`right_contraction`. But see §1.2 item 2 on the definitions. |
| `Cross.cross_anticomm` | (a)/(c) — the `vectorcalc.cross` doctest "`cross(a, b) == -cross(b, a)` … any a, b" and `tests/test_vectorcalc.py`; deserves a twin tag when next touched. |
| `Cross.signedVolume_eq_rVectorPart_three` | (b), low stakes — proof is `simp only [signedVolume, rVectorPart]`, i.e. it says `x.c123 = ⟨0,…,0,x.c123⟩.c123`. Recorded as a deliberate "bridging lemma" (2026-10-28), so it is extraneous by content, not by accident. Same for `Measures.signedArea_eq_rVectorPart_two`. |
| `G1.wedge_vec`, `G1.magnitude_vec` | (a) — two of the three "lessons" in G1's module doc (every pair of 1D vectors is parallel; `|x e₁| = |x|`). |
| `G2.eq_smul_e12_of_isBivector`, `G2.isBivector_e12` | (b), §2.2. |
| `G2.isBivector_wedge_of_isVector` | (c) — `defining-g2.rst` "A vector times a vector is a versor (the dot product plus the wedge)". |
| `G3.e_3_sq`, `e_1_mul_e_3`, `e_2_mul_e_3`, `e_12_mul_e_3` | (a) — the multiplication table; `cheat-sheet-3d.rst` lists exactly these. The table is incomplete, §4. |
| `G3.isBivector_bivector`, `G3.isTrivector_trivector` | (b), §2.2 (one-line `rfl` recognizers, harmless). |
| `GeneralInverse.generalInverse_eq_inverse_of_isVector` | (a) — promised by the module doc; the 𝒢₃ half of the promise is missing. |
| `GeneralInverse.conjProduct_grades` | (a) — the fact the 𝒢₃ construction rests on; ironically unused by the proof that needs it (§1.5 item 7). |
| `MathlibBridge.wedge_eq_det`, `wedge_c12/c13/c23_eq_det`, `signedVolume_eq_det`, `rotor_sandwich_eq_rotation` | (a) — Program decision 4; end results by design. |
| `MathlibBridge.toC_rot_rot` | (b), §2.1. |
| `Measures.area_sq_vec`, `normSq_wedge_eq_lagrange` | (b), §2.1. Note the coverage map lists these two as *the* coverage of `measure.area`. The theorem that actually says what the docstring says (`= |a|*|b|*sin(θ)`) is `StudentTrigForms.area_eq_mag_mul_sin`. |
| `Measures.signedArea_eq` | (a) — `measure.signed_area`'s "the 2-D determinant `a_1*b_2 − a_2*b_1`"; restate on objects. |
| `Normalize.magnitude_normalizeVec` | (b), §2.1. |

Consumer-less but plainly (a), needing no action: the addition laws and `zero_mul` (stated as laws),
the G2 multiplication table, `eq_smul_basis`, `vec_eq_smul`, `I_mul_I_inv`, `I_sq_eq_sign`, the unused
halves of dot/wedge bilinearity, `rVectorPart_idem`/`_complete`/`even_add_odd`, all of
`GeneralInverse`, all of `GeometryObjects2D`, the `dot_eq_inner`/`norm_toE`/Cauchy–Schwarz bridges.

---

### 3. Duplicates

| Fact | Proved as | Notes |
|---|---|---|
| `magnitude x ^ 2 = normSq x` | `G3.magnitude_sq_eq_normSq` (any `x`) and `Measures.area_sq_vec` (`x = a∧b`, plus two unneeded `IsVector` hypotheses) | Certain without a build: the general lemma has no hypotheses, so the instance cannot need any. `volume_sq_vec` re-derives it inline too. |
| a normalized element has `normSq = 1` | `Normalize.G3.normSq_normalizeVec` (vectors) and `Rotor.G3.normSq_normalize` (anything) | Two definitions with identical bodies: `normalizeVec` and `normalize`. |
| Lagrange | `Lagrange.lagrange_3d`/`_2d` (reals), `Trig.lagrange_property` (objects, both dims), `Measures.normSq_wedge_eq_lagrange` (rearranged) | Three statements, no proof sharing between the first two. |
| `e₁₂² = −1` in 𝒢₂ | `G2.e_12_sq` and `G2.I_sq` | `I := e_12`; separate identical proofs. |
| `IsBivector e₁₂` in 𝒢₂ | `G2.isBivector_e12` and `G2.isBivector_I` | Same. |
| the dot is symmetric | `dot_comm` (all multivectors) and `MathlibBridge.dot_comm_of_inner` (vectors, via Mathlib) | **Deliberate** — the bridge's demonstration that a Mathlib theorem transfers. Fine; say "also `dot_comm`" in its doc. |
| the split `ab = a·b + a∧b` in 𝒢₂ | `G2.vec_mul` (struct literal) and `G2.mul_eq_dot_add_wedge` | |
| `a·b = Σ aᵢbᵢ` in 𝒢₂ | `G2.dot_vec` and `G2.dot_eq_coord_sum` | Leaf and its object form; only the leaf is used. |
| the four G3 self-product facts | each `_coord` leaf + object twin (§1.3) | Separate proofs; the object twin does not call the leaf. |
| `|a∧b|²` in 𝒢₂ | `G2.normSq_wedge_vec` and `ReciprocalFrame2D.normSq_wedge_vec'` | Prior finding; the G2 one is the unused one. |
| wedge = determinant in 𝒢₂ | `Measures.signedArea_eq` (`= a₁b₂−a₂b₁`) and `MathlibBridge.G2.wedge_eq_det` | Same number through two unconnected definitions (§1.2 item 3). |
| `private smul_inv_scalar` | once per namespace in `GeneralInverse` | Fine (two algebras). |

---

### 4. Missing

#### 4.1 Citations that claim more than Lean proves

- **`notebooks/defining-g2.py`** (the associativity section): "That this holds in every dimension is
  a theorem, proved in the Lean files and in `tasks/reference/geometric-product-associativity.md`."
  Lean proves `mul_assoc` for 𝒢₁, 𝒢₂ and 𝒢₃ only; the general-n algebra is the deferred task. That
  cell is also the natural second twin of `GacalcProofs.G2.mul_assoc` and carries no tag.
- **`GeneralInverse.lean`'s own module doc** — the 𝒢₃ "equals `inverse` on a vector" claim (§1.8).

Every Lean name cited on the eleven pages and their notebooks exists and says what the citation
says: `vec_mul_fullAngleRotor`, `rot_add_vec`, `rot_smul`, `rot_basis_decomp`, `fullAngleRotor`,
`rotor` (`Rotation2D`), `dual_perp_dot`, `dual_perp`, `dual_wedge_perp_left_dot`/`_right_dot`, the
`GeometryObjects2D` five, and `wedge_eq_zero_iff_parallel` in `base.py`.

#### 4.2 Lean theorems that exist and the page does not cite (category c)

| Page | States | Lean theorem it should name |
|---|---|---|
| `blade-square-sign.rst` (the whole page) | `I_r² = (−1)^{r(r−1)/2}` | `G1`/`G2`/`G3.I_sq_eq_sign`, `I_sq`. The page cites no Lean at all; these three theorems exist for exactly this formula. |
| `vector-addition.rst` | "addition commutes" | `G2.add_comm` |
| `defining-g2.rst` | associativity; "a vector times itself is its squared length"; `e₁₂*e₁₂ = −1`; the three rules | `G2.mul_assoc`, `mul_vec_self`, `e_12_sq`, `e_1_sq`/`e_2_sq`/`e_2_mul_e_1` |
| `defining-g2.rst` "The kind of a product" | vector·vector has a scalar and a bivector part | `isScalar_mul_self_of_isVector`, `isBivector_wedge_of_isVector`, `mul_eq_dot_add_wedge` |
| `dual.rst` | "multiplying out gives a* = a₂e₁ − a₁e₂" | `G2.dual_vec` (uncited and unused) |
| `geometry-from-vectors.rst` eq-triangle-closed | sides sum to zero | `triangle_sides_sum_zero` (tagged in the notebook, not named on the page; the other four are) |
| `levels-of-abstraction` (page + notebook) | dot = grade-0 part, wedge = grade-2 part, their sum is the product | `GradeProjection.dot_eq_rVectorPart_zero`, `wedge_eq_rVectorPart_two`, `mul_eq_dot_add_wedge` — the page cites only a test file |
| `three-dimensions.py` | the same two parts in 3D | the G3 versions of the same three |

Per `CLAUDE.md` this is not a backfill order; it is the list for whenever those pages are next touched.

#### 4.3 Stated in the book / notebooks / Python, with no Lean theorem

1. **`e₁*e₁₂ = e₂`, `e₂*e₁₂ = −e₁`.** Used by name in `geometric-product.rst`, `dual.rst`,
   `defining-g2.rst` and listed in `cheat-sheet-2d.rst`. `G2.lean`'s table has `e_1_sq`, `e_2_sq`,
   `e_1_mul_e_2`, `e_2_mul_e_1`, `e_12_sq` and stops. Two one-line theorems.
2. **𝒢₃'s table is partial.** `cheat-sheet-3d.rst`: "`e_ij * e_ij = −1`" (no `e_12_sq`/`e_13_sq`/
   `e_23_sq` in `G3.lean`), anticommutation for every pair (only `e_2_mul_e_1`), and **"`I` commutes
   with every multivector"** (no theorem; also the lemma §1.5 item 7 wants).
3. **The dual of a 2D vector is a vector of the same length** (`dual.rst`, "First, the dual is a
   vector … Its length is |a|" — the page's precondition for talking about an angle at all). Only the
   coordinate leaf `dual_vec` exists; no `IsVector (dual v)`, no `normSq (dual v) = normSq v`. The 3D
   bivector versions exist in `Reflect.lean`.
4. **The cross product of two vectors is a vector.** `vectorcalc.cross` is typed `Vector -> Vector`
   on 𝒢₃ and the book calls it a vector; Lean has only `cross_vec`. (`G3` has no
   `isBivector_wedge_of_isVector`; the architecture doc records it as skipped for lack of a consumer.
   This is the consumer, with `Reflect.isVector_dual_of_isBivector`.)
5. **The rest of `defining-g2`'s "kind of a product" list:** vector × `e₁₂` is a vector; bivector ×
   bivector is a scalar; versor × vector is a vector; versor × versor is a versor. Also "every
   nonzero scalar-plus-bivector is a product of two vectors" (stated on the page and in the
   notebook). None has a theorem.
6. **`signed_content` as Python computes it:** `(a∧b∧c) * I⁻¹` is the scalar `signedVolume a b c`
   (and the 2D twin). The Lean definitions read a coordinate; nothing proves that equals the dual.
7. **Contraction's defining cases** (§1.2 item 2): vector ⌋ bivector, and "zero when the left grade
   is higher".
8. **`blade-square-sign.rst`'s note:** `Ĩ_r = (−1)^{r(r−1)/2} I_r` and `I_r * Ĩ_r = 1`. Lean has
   `I_sq`, not `reverse I = neg I` or `mul I (reverse I) = one`.
9. **Subtraction** (`vector-addition`): `(a − b) + b = a` (shown in the notebook), "subtracting is
   adding the opposite", and translate's inverse. `G2` has `sub`, `neg`, `add_neg_cancel` and no law
   relating `sub` to `add`/`neg`.
10. **Distance formula** (`geometry-from-vectors.rst` eq-distance): `|b − a| = √((b₁−a₁)² +
    (b₂−a₂)²)`. No theorem; one line from `normSq_vec`.
11. **2D `area`** and `|signed area| = area` (§1.2 item 4).
12. **`generalInverse` agrees with `inverse` on 𝒢₃ vectors** (promised by its own file).

Known and already tracked, not re-reported: general `content`, the general Hestenes `inner_product`,
`gn.py` (the deferred general-n task).

---

### 5. Overall judgment

The slice is mathematically sound and the foundations are right: the three products match the Python
oracle exactly (checked mechanically), the dual, cross and measure signs match the doctests, the
teaching-order and one-direction-only problems from the November 8 review are fixed in G2/G3, and
`GeneralInverse.lean` and `GeometryObjects2D.lean` are good examples of the house style. What is not
in good shape is the layer between "the fact is proved" and "the proof and its statement look like
the book": 75 of the 247 theorems in these files are named nowhere but their own declaration (namespace-aware count; many of those are laws and table entries that are fine alone), the object-form
sweep stopped at stating the object theorems without moving the callers onto them, and several
proofs are brute `ring` exactly where the book page's whole point is a coordinate-free argument.
Roughly ten theorems are dead outright and another fourteen are API built ahead of any caller.
Nothing here is wrong; a good deal of it is unused, duplicated or uncited.

The five changes most worth making:

1. **Prove `dual_perp_dot` the way `dual.rst` proves it** (associativity → `mul_vec_self` → grade),
   and give it its twin tag. It is the one place where the Lean, the page and the notebook are meant
   to be the same argument and are not. Do `G2.vec_anticomm_perp` and the `dot_is_sym_part`/
   `wedge_is_antisym_part` pair the same way, which also gives `G2.wedge_antisymm` a reason to exist.
2. **Finish the G3 self-product conversion:** move the 9 call sites onto `wedge_self_vec`,
   `mul_vec_self`, `dot_self_vec_eq_normSq`, `mul_eq_dot_add_wedge` and delete the four `_coord`
   twins.
3. **Delete or fold the superseded results:** `Normalize.lean`'s two theorems (into `Rotor.normalize`),
   `area_sq_vec` and `normSq_wedge_eq_lagrange`, `G2.dual_vec_perp`, `G2.vec_mul`,
   `G2.dot_eq_coord_sum`, `toC_rot_rot`; and decide `Lagrange.lean` (delete, or make
   `Trig.lagrange_property` rest on it).
4. **Make `signedArea` an object-level definition on the wedge** (parallel to `signedVolume`), add
   `G2.area`, and restate `wedge_eq_det` through it; reword the `dot` comments to "scalar product";
   and either fix `leftContraction`'s grade arithmetic and add the vector⌋bivector case, or mark the
   file as covering two special cases only.
5. **Close the small book gaps:** the two missing 𝒢₂ table entries, `I` commutes in 𝒢₃, "the dual of
   a vector is a vector of the same length", and the false "every dimension … proved in the Lean
   files" sentence in `notebooks/defining-g2.py`. Bring `G1.lean` and the section order of `G2.lean`
   in line with `G3.lean` at the same time, and replace `⟨0,0,0,0⟩` with `zero` in the 2D statements.

## B. Rotations and versors

Reviewed 2026-11-22, read-only (no build, no edits). Every "unused" claim below was checked with
`git grep -n '<name>' -- proofs book notebooks src tests tools`; the per-declaration usage table I
built is (a session scratch file, not kept)
(one row per declaration: uses in its own file, other Lean files, reader-facing files).
Claims that a proof "could be structural" are from reading, not from a build.

### What I read

**In full (every line, statements + doc comments + proof bodies):** `Versor2D`, `Sandwich`,
`RotateComponents`, `Rotation2D`, `Rotation3D`, `Trig`, `TrigEquiv`, `StudentTrigForms`, `Exp`,
`Rotor`, `PlaneRotation3D`, `RotateFromTo2D`, `Bootstrap2D` (all in `proofs/GacalcProofs/`).
Book pages in full: `rotate`, `geometric-product`, `rotation-graph-paper`, `rotation-from-vectors`,
`trigonometry` (a placeholder), `proof-rotate`, `proof-rotate-from-a-to-b`, `bootstrap-rotation`,
`bootstrap-rotation-from-projection`, `bootstrap-product`, `bootstrap-rotation-from-product`.
House rules in full: the four `CLAUDE.md` sections + `make lean` bullet,
`tasks/reference/lean-ga-proof-architecture.md`, `teaching-order-and-dependencies.md`,
`lean-python-notebook-workflow.md`, `tasks/lean-proofs-remove-extras.md`,
`tasks/review/2026/11/08/repo-review.md` §7.

**Read, with drawing/boilerplate lines filtered out:** the notebooks `rotate`, `geometric-product`,
`rotation-from-vectors`, `proof-rotate-from-a-to-b`, `bootstrap-rotation`,
`bootstrap-rotation-from-projection`, `bootstrap-product`, `bootstrap-rotation-from-product`,
`displayrotations`, `displayproofs` (all Markdown and all computing cells; ePiX figure cells
skipped). There is no `notebooks/rotation-graph-paper.py`, `trigonometry.py` or `proof-rotate.py`.

**Python:** `base.py` — `versor_from_vectors`, `rotor_from_vectors`, `plane_of_rotation`, `angle`,
`conjugate`, `bivector_from_vectors`, `sandwich`, `exp`, `magnitude`, `magnitude_squared`,
`normalize`, `inverse` in full; `cosine`/`abs_sin` docstring heads and return lines only.
`transforms.py` — lines 1–620 and 750–1085 in full (`projection_rotation`, `versor_rotation`,
`_unit_bivector_rotor_factory`, `bivector_rotation`, `plane_rotation`); the rest (scale, matrix
code) outlined only. `functions.py` — outline + grep only (it cites no Lean and carries no math).
`g2.py` — `rotate_90_degrees`, `rotate`, `sine`. Also `standardposition.rotation_from_to`, because
it, not anything in `transforms.py`, is the Python that `RotateFromTo2D`/`Bootstrap2D` mirror.

**Skimmed for definitions only:** `G2.lean`, `G3.lean`, `StandardPosition2D.lean`,
`ProjectionRotation2D.lean`, `Projection2D.lean` (declaration lines and the defs my files use).

### Status of the prior findings that concern these files

`tasks/review/2026/11/08/repo-review.md` §7.2 — all **STILL PRESENT** (none fixed):

| Prior finding | Now |
|---|---|
| `Sandwich.sandwich_fixes_orthogonal`, `sandwich_plane_invariant`: free reals, unused, uncited | STILL PRESENT |
| `Sandwich.normSq_mul`, `inverse_mul` take versor components | STILL PRESENT |
| `Exp.expBivectorGeneral p q r` takes reals | STILL PRESENT |
| `RotateFromTo2D.rotateFromTo_collapse`, `_carries` take reals | STILL PRESENT |
| one-consumer `_coord` leaves: `versor_mul_from_eq_bisector_coord`, `from_mul_versor_eq_bisector_coord` (2D + 3D), `sandwich_comp_coord`, `rotation_fixes_normal_coord` | STILL PRESENT |
| duplicates: `normSq_uvec`/`magnitude_uvec` (Rotor) vs `uvec_magnitude` (TrigEquiv); `normalize` (Rotor) vs `normalizeVec` | STILL PRESENT |
| `rotor_unit'` unused; `Rotation3D.vec_mul_mul_self` dead | STILL PRESENT (each appears only at its declaration) |
| `rotation_preserves_dot` re-derives `isEvenVersor_versorFromVectors` inline | STILL PRESENT |
| stale docs: `Rotation3D` header plan + "References (for when this is picked up again)"; `RotateComponents` "currently carries Stage 1"; `Sandwich` "Object-form wrappers for the scaffold lemmas" header | STILL PRESENT |
| `from_mul_versor_eq_bisector` (2D, 3D) multiplies by the *to*-vector | STILL PRESENT |
| `rotateFromTo_carries`: nothing ties `mb` to `\|b\|`; middle pair not shown unit | STILL PRESENT |
| `uvec_dot`/`uvec_wedge` state `.s`/`.c12`, not `dot`/`wedge` | STILL PRESENT |

`tasks/lean-proofs-remove-extras.md`: #4 (`G3.sandwich_preserves_wedge` `hr`) and #5
(`inverse_mul`, both `≠ 0`) STILL PRESENT in the signatures. #3's theorem
(`G2.sandwich_preserves_wedge`) has moved from `Projection2D.lean` to `Sandwich.lean`, `hr` still
there, so the task's file name for #3 is stale. I did not re-run the `clear` test.

Everything below is in addition to those.

---

### 1. Written as they should be?

#### 1a. Do the definitions match what the Python computes? Yes.

I checked sign, side, and half/full angle for every definition; no mismatch.

- `versorFromVectors a b = b*a + |a|*|b|`, applied as `sandwich R v = R*v*R⁻¹`: same as
  `base.versor_from_vectors` and `base.sandwich` (`self * x * self.inverse()`).
- `rotor θ = cos(θ/2) − sin(θ/2)*e₁₂` and `planeRotor θ i = cos(θ/2) − sin(θ/2)*i`: same as
  `transforms._unit_bivector_rotor_factory`. `R*e₁*R̃ = cos(θ)*e₁ + sin(θ)*e₂`, i.e. positive θ
  turns `e₁` toward `e₂`, as `plane_rotation(e_1, e_2)` documents.
- `rot θ` is the coordinate formula in `g2.Vector.rotate`'s doctest; `rot90` is
  `rotate_90_degrees`; `expBivector*` is `base.exp`'s closed form; `normalize`, `inverse`,
  `cos_between`, `sin_between` (unsigned), `signed_sin_between` match `normalize`, `inverse`,
  `cosine`, `abs_sin`, `g2.Vector.sine`. (`normSq` puts the reverse on the right, Python on the
  left; the scalar part is the same.)
- One difference of *form*, not value: Python and the book define the rotation as the blend
  `cos(θ)*v + sin(θ)*v.rotate_90_degrees()`; Lean's `rot` is defined by coordinates, and the blend
  identity is proved only for `rotPlane` (`StandardPosition2D.rotPlane_vec_eq_blend`), never for
  `rot`. See §4.

#### 1b. Proofs that are brute `ext <;> ring` where the stated reason is a short structural chain

Each of these has a doc comment (or a book sentence) giving a reason the proof does not use.

1. **`RotateFromTo2D.rotPlane_conj_collapse`.** The doc comment and
   `book/docs/proof-rotate-from-a-to-b.rst` ("built on `rotPlane_conj_collapse`, which rests on
   `rotPlane_comm` above") say the collapse is "commute, then cancel". The proof is
   `simp only [rotPlane]; ext; linear_combination …`. `rotPlane_comm` is used by no proof in the
   corpus. The book's argument is two rewrites: `rotPlane_comm`, then
   `StandardPosition2D.rotPlane_inv`. As written, the book's "rests on" is false of the Lean.
2. **`versor_mul_from_eq_bisector` / `from_mul_versor_eq_bisector` (Versor2D, Rotation3D).**
   `R*a = |a|*h` is, in the Python docstring and the book, "multiply it out, using `a*a = |a|²`":
   `add_mul`, `(b*a)*a = |a|²*b`, `magnitude_sq_eq_normSq`. The lemma for the middle step,
   `Rotation3D.vec_mul_mul_self`, was written and is used by nothing. Instead there are four
   scalar-taking `_coord` leaves with `set`/`clear_value`/`linear_combination`, each with one
   consumer. Proving the object theorems structurally removes all four leaves and gives
   `vec_mul_mul_self` its use. (`Rotor.normSq_versorFromVectors` already shows the getter-native
   form of the same `√` fact works without a `_coord` leaf.)
3. **`Sandwich.sandwich_fixes_own_bivector_coord`, `sandwich_fixes_own_normal_coord`,
   `sandwich_fixes_orthogonal`.** Each doc comment says "it commutes with `R`, so it rides
   through `R*R⁻¹ = 1`"; each proof is `ext <;> field_simp [hr] <;> ring`. A commutation lemma
   plus `mul_inverse_self_of_isEvenVersor` (which is otherwise unused, see §2) is the reason.
4. **`Rotor.normSq_versorFromVectors`** (2D, 3D). The doc comment says "by Lagrange's identity
   (`Trig.lagrange_property`)". The proof never calls `lagrange_property`; it is one
   `linear_combination` on unfolded coordinates.
5. **`Rotation2D.rot_add_vec`.** Doc: "true because the geometric product … distributes over
   `+`". Proof: `ext <;> ring` on coordinates. Fine as a leaf, but then the doc should not claim
   the reason.
6. **`TrigEquiv.signed_sin_between_uvec`.** Doc: "ties the signed 2D sine to the angle form
   `uvec_wedge`". The proof re-derives it with `sin_sub`; `uvec_wedge` is used by no proof.
7. **`Bootstrap2D.mul_proj_eq_dot`, `mul_reject_eq_wedge`, `mul_reject_antisymm`.** The book's
   derivation is `a * ((x/|a|)*a) = (x/|a|) * (a*a)`; the proofs are
   `ext <;> simp only <;> ring_nf <;> field_simp <;> ring`. `mul_reject_antisymm` ends by
   re-proving `a∧b = −(b∧a)` in coordinates although `G2.wedge_antisymm` exists.
   (`mul_eq_mul_proj_add_mul_reject` and `mul_proj_symm` in the same file are structural — the
   model.)
8. **`Sandwich.versorFromVectors_mul_reverse` (2D, 3D) and `…_coord` (3D).** These are
   `mul_reverse_self_of_isEvenVersor` applied to `isEvenVersor_versorFromVectors`, re-proved by
   `ext <;> ring`; see §3.

#### 1c. Statements that take free reals and build objects inside (beyond the prior list)

- `RotateFromTo2D.bprime_coords (a1 a2 b1 b2 ma)` and `cs_a_unit (a1 a2 ma)`. With
  `rotateFromTo_collapse`/`_carries` (prior list), **every `a`/`b` theorem in this file is
  scalars-in**, with `ma`, `mb` free reals standing in for `|a|`, `|b|` and
  `hma2 : a1^2 + a2^2 = ma^2` as a hypothesis. `StandardPosition2D` already has `alignSP`,
  `unalignSP`, `cs_unit`, `magnitude_sq_of_isVector`; restated on those, the file needs no free
  real. `rotateFromTo_collapse` is also weaker than it looks: `b1 b2 mb` play no role (it is
  `rotPlane_conj_collapse` at a particular middle pair), and nothing proves the middle pair is the
  `(b'₁/|b'|, b'₂/|b'|)` the book's Step 2 reads off.
- `Sandwich.versorFromVectors_eq_evenVersor (a1 … b3)`, `versorFromVectors_mul_reverse_coord`,
  `versorFromVectors_mul_inverse_coord`: scalar-taking, with object twins in the same file.
- `Exp.normSq_expBivectorGeneral` / `isRotor_expBivectorGeneral`: the guard is the raw sum
  `p^2 + q^2 + r^2 ≠ 0`. The architecture doc's versor-hypothesis convention says "never the raw
  coordinate sum"; the object form is `{B} (hB : IsBivector B) (hBn : normSq B ≠ 0)`.
- Conclusions that leak coordinates ("objects out"): `sandwich_fixes_own_bivector` concludes about
  `bivector R.c12 R.c13 R.c23`; `sandwich_fixes_own_normal` and
  `PlaneRotation3D.rotorSandwich_planeRotor_fixes_normal` about `vec i.c23 (-i.c13) i.c12` rather
  than the dual of the bivector.
- `Bootstrap2D.rotPlane_fromTo_eq_vec_mul` / `rotPlane_fromTo_eq_rotateFromToProj` spell the
  cosine and sine as `dot a b / (|a|*|b|)` and `(wedge a b).c12 / (|a|*|b|)`. Those are exactly
  `Trig.cos_between a b` and `TrigEquiv.signed_sin_between a b`. Stating them as
  `rotPlane (cos_between a b) (signed_sin_between a b) v` is the "prefer sine/cosine" form and
  matches the book's equation `eq-bootstrap-rotation-from-to`.

#### 1d. `_coord` leaves that fail "fragile AND shared by ≥2" (beyond the prior list)

- `Sandwich.versorFromVectors_mul_reverse_coord`: one consumer
  (`versorFromVectors_mul_inverse_coord`), and an object twin with its own duplicate proof.
- `Sandwich.versorFromVectors_mul_inverse_coord`: used only in `ProjectionRotation3D` (two
  rewrites), while its object twin `versorFromVectors_mul_inverse` is used by nothing.
- `Sandwich.sandwich_fixes_own_normal_coord`: the `_coord` leaf is the one in use
  (`RotateComponents`); the object form `sandwich_fixes_own_normal` is used by nothing. Inverted.
- `TrigEquiv.sin_between_eq_abs_signed_vec_coord`: two consumers, but the second
  (`sin_between_uvec`) round-trips through `uvec_eq_vec` only to reach the leaf;
  `sin_between_eq_abs_signed_vec (isVector_uvec α) (isVector_uvec β)` is direct.

#### 1e. StudentTrigForms: the "meaning gate" does not do what the header says for most theorems

The header says the nonzero guard "excludes the `0/0` case and makes `cos(θ) = 0 ⟺ dot = 0`",
so each theorem is "exactly as strong as the dot primitive". That holds for `dual_perp` only.

- `cross_perp_left/right`: guard `a ≠ 0`, `b ≠ 0`; but `cos_between (cross a b) a` is `0/0`
  whenever `a ∥ b` (then `cross a b = 0`). Same for `dual_wedge_perp_left/right` (needs
  `a ∧ b ≠ 0`), `reject_perp` (needs the rejection nonzero), `proj_plane_perp_normal` (needs the
  projection nonzero), `parallel_smul` (needs `k ≠ 0`).
- The guards are spelled three ways in one file: `normSq a ≠ 0`, `magnitude a ≠ 0`,
  `dot a a ≠ 0`. The header says `normSq`.
- The header says "each theorem takes vectors (`IsVector`)"; `reject_perp`, `area_eq_mag_mul_sin`,
  `proj_plane_perp_normal`, `dot_eq_zero_of_cos_between` do not.
- `dual_wedge_perp_right` is documented "for … ANY `a`" yet carries `_ha0 : normSq a ≠ 0`.

#### 1f. Stale or wrong doc comments (beyond the prior list)

- `Sandwich.lean` header: titled "(𝒢₂ pilot)", says "the 𝒢₃ versions follow the same shape (see
  tasks/…)". The file holds the complete 𝒢₂ and 𝒢₃ developments.
- `Sandwich.lean`: `mul_biv_reverse_self`, `mul_biv_inverse_self`, `G3.versorFromVectors_mul_reverse`,
  `versorFromVectors_mul_inverse` have no doc comment (leftovers of the "wrappers" block).
- `Rotation2D.lean` header and `rot_from_to`: "the book's exact framing" for
  `b = (|b|/|a|)*rot (φb − φa) a` in polar form. The book no longer frames from-a-to-b that way
  (`proof-rotate-from-a-to-b.rst` is standard position, no polar angles).
- `Rotation3D.lean` header: says proving `h` bisects the angle "first needs the (deferred) map
  into `EuclideanSpace`… or a local `angle`". `Trig.cos_between` and `MathlibBridge` both exist now.
- `Rotor.rotorFromVectors_uvec`: "`cos(θ/2) > 0`, i.e. the directions not antiparallel". Not
  antiparallel is `cos(θ/2) ≠ 0`. For the rotor equality the sign matters; for
  `rotorSandwich_rotorFromVectors_uvec` it does not (`−R` gives the same sandwich), so that theorem
  is stated narrower than it is true.
- `RotateComponents.lean` header describes a result the file never proves ("acts as the 2D rotation
  matrix `[[c, −s], [s, c]]` … prove the explicit rotated-vector equation with `c² + s² = 1`").
- `TrigEquiv.lean` header: "the fixed-grade = graded-part half of Phase 4" is task history; and
  `import GacalcProofs.Versor2D` is unused.
- `PlaneRotation3D.lean`: `rotorSandwich_planeRotor_fixes_normal` sits under "Corollaries" but is
  an independent coordinate proof, not derived from `rotorSandwich_planeRotor`.
- `Trig.cos_sq_add_sin_sq` shares its name with Mathlib's, the trap recorded in the architecture
  doc; inside `GacalcProofs.G2`/`G3` it shadows `Real.cos_sq_add_sin_sq`. A rename removes the trap.
- No Lean file in this slice carries a `-- twin:` tag, although two notebooks tag theorems here
  (§4).

#### 1g. Name vs statement

- `TrigEquiv.sin_between_eq_abs_signed_vec`: the `_vec` suffix is on the *object* form; elsewhere
  `_vec` marks a coordinate-literal leaf.
- `Bootstrap2D.isVector_smul_of_isVector` is the 𝒢₂ twin of `G3.IsVector.smul` under a different
  name, in a Part III file; `magnitude_smul_of_nonneg` and `normalizeVec_smul_of_pos` are likewise
  general 𝒢₂ facts living in `Bootstrap2D`.
- `Bootstrap2D`'s header says it holds "the steps of Part III that had no theorem", but
  `mul_proj_eq_dot`/`mul_reject_eq_wedge` are what Part I's `projection.rst` and
  `notebooks/projection.py` cite.

---

### 2. Extraneous

"Dead" = no proof uses it and no reader-facing file names it. "Endpoint" = no proof uses it, but
it states a result the Python or book relies on (keep). The usage report's "mentioned nowhere
else" list misses names declared in both `G2` and `G3` namespaces; those are marked †.

#### Dead, high confidence

| Declaration | Why |
|---|---|
| `Rotation3D.vec_mul_mul_self` | only its declaration (unless §1b.2 is done, which uses it) |
| `Rotation2D.rotor_unit'` | equals `reverse_mul_self_of_isRotor (isRotor_rotor θ)`; never used |
| `Sandwich.sandwich_fixes_orthogonal`, `sandwich_plane_invariant` | the `e₁₂`-plane special cases of `sandwich_fixes_own_normal` and `sandwich_evenVersor_vec_isVector` |
| `Sandwich.versorFromVectors_mul_inverse` (object) | unused; the `_coord` twin is the one consumed |
| `Sandwich.IsRotor.isEvenVersor`, `IsRotor.normSq_eq_one` † | proofs use `hR.1`/`hR.2` |
| `Sandwich.mul_reverse_self_of_isRotor`, `reverse_mul_self_of_isRotor` † | declared 2D + 3D, used nowhere |
| `Sandwich.sandwich_sub` | unused (`sandwich_add`, `sandwich_smul` are used) |
| `Sandwich.reverse_mul3_vec`; `G3.reverse_mul_vec` † | only their declarations |
| `RotateFromTo2D.cs_a_unit` | third copy of the unit-pair lemma (§3); dies if the file goes object-form |

#### Dead, medium confidence: whole-file candidates

- **`RotateComponents.lean` (all six theorems).** Nothing in the book, notebooks, Python, tests or
  any other proof file names any of them (`git grep` hits are all inside the file).
  `rotation_preserves_dot`, `rotation_fixes_plane_bivector`, `rotation_fixes_normal(_coord)` are
  the general `Sandwich` theorems specialized to `R = versorFromVectors a b`;
  `rotation_fixes_perp` handles only multiples of the normal. The file's goal ("in-plane part
  turned, perpendicular part fixed, for the a→b rotation") is now proved for every vector by
  `ProjectionRotation3D.projRotation_eq_sandwich`, and by angle by
  `PlaneRotation3D.rotorSandwich_planeRotor`. Only `sandwich_ahat` (`â ↦ b̂`) says something not
  said elsewhere in 3D, and it is a two-line corollary of `sandwich_carries_from_to`. ~75%
  confident the file can go (keeping `sandwich_ahat` in `Sandwich.lean` if wanted).
- **`Rotation2D.rot_from_to`** (and `polar` if `rot_polar` is not cited, but see §4: `rot_polar`
  should be). Uncited; the book's from-a-to-b no longer uses polar form; superseded by
  `rotateFromTo_carries` / `sandwich_carries_from_to` / `rotateFromToProj_normalize`. ~70%.
- **`Sandwich.mul_biv_reverse_self`, `mul_biv_inverse_self`.** A bivector is an even versor, so
  these are `mul_reverse_self_of_isEvenVersor` / `mul_inverse_self_of_isEvenVersor`. They do back
  one sentence of `base.inverse`'s docstring ("machine-checked for the vector, versor, bivector and
  trivector cases"), so either keep them as one-line corollaries of the versor lemma or drop them
  and let the versor lemma carry the sentence. `mul_triv_reverse_self`/`mul_triv_inverse_self`
  back the "trivector" word of the same sentence: endpoint, keep.

#### Endpoints, uncited — keep (the "mentioned nowhere else" names in this slice)

| Theorem | Backs |
|---|---|
| `Exp.isRotor_expBivector`, `isRotor_expBivector12`, `isRotor_expBivectorGeneral` | `base.exp` ("automatically unit"); the `displayrotations` exp section. Thin, see §3 |
| `PlaneRotation3D.cos_between_rotorSandwich_planeRotor`, `rotorSandwich_planeRotor_fixes_normal` | `transforms.plane_rotation` / `bivector_rotation` ("rotates by θ", "perpendicular part fixed") |
| `Rotor.rotorSandwich_rotorFromVectors_uvec` | the only bridge from the from-vectors rotor to `rot (β − α)`; `base.rotor_from_vectors` docstring; `displayrotations` first computation |
| `Sandwich.sandwich_comp` | "rotations compose by multiplying versors" (`compose` of two `versor_rotation`s) |
| `Sandwich.sandwich_evenVersor_vec_isVector` | `base.sandwich` docstring ("a vector goes to a vector"); `displayrotations` ("which is *why* a versor sandwich of a vector is always a vector") |
| `Sandwich.sandwich_fixes_own_normal` | `base.sandwich` doctest (`R.sandwich(1 * e_3) == 1 * e_3`) — but see §1d: make this the used form |
| `Sandwich.mul_triv_inverse_self` | `base.inverse` docstring (trivector case) |
| `TrigEquiv.cos_between_uvec`, `sin_between_eq_abs_signed_vec`, `sin_between_uvec` | `base.cosine`, `base.abs_sin`, `g2.Vector.sine`; `tests/test_signed_sine.py` (`abs(sine) == abs_sin`) |
| `sandwich_inverse_sandwich` †, `sandwich_preserves_cos`/`_sin` †, `Trig.cos_sq_add_sin_sq` † | `versor_rotation`'s `backward`; `cosine`/`abs_sin` docstrings |
| `Rotor`: `isRotor_rotorFromVectors` †, `rotorSandwich_preserves_dot`/`_normSq` †, `normSq_versorFromVectors_ne_zero` †, `…_eq_projRotation`, `…_carries_from_to` | `base.rotor_from_vectors` docstring (cites the file, names only `rotorSandwich_normalize`) |
| `Rotation2D.sandwich_rotor_eq_rot`, `sandwich_rotor_eq_vec_mul_fullAngleRotor`, `rotor_mul` | `geometric-product.rst` ("prove them equal in effect", unnamed); `plane_rotation` in 2D |

#### StudentTrigForms: 13 of 14 theorems are read by nothing

Only `G2.dual_perp` is cited (`dual.rst`, `notebooks/dual.py`). `cross_perp_left/right`,
`parallel_smul`, `area_eq_mag_mul_sin`, `dual_wedge_perp_left/right`, `proj_plane_perp_normal`,
`vec_anticomm_cos_perp`, `cos_perp_iff_mul_eq_wedge`, `volume_eq_mag_mul_cos`,
`mul_eq_wedge_of_cos_perp` †, `reject_perp` †, `dot_eq_zero_of_cos_between` † (used only inside
the file) appear nowhere else. The house naming rule says the cosine form is "the theorem a reader
cites", but the book cites the `_dot` forms: `dual-3d.rst` and the `twin:` tags in
`notebooks/dual-3d.py` name `dual_wedge_perp_left_dot`/`_right_dot`. So this file exists for a
rule the book does not follow. Not dead by the rule; by use, it is the largest block in the slice
that nothing needs. Either cite the cosine forms on the pages that state the facts, or cut the
file to the theorems that have a page. Given §1e (most of them are vacuous in the degenerate
case), I would cut.

---

### 3. Duplicates

1. **Two unconnected developments of "rotation by a cosine and a sine".** `Rotation2D.rot θ`
   (angle) and `StandardPosition2D.rotPlane c s` (pair) each prove the same four facts, with no
   theorem relating them (`git grep` for `rotPlane (cos`/`rotPlane (Real.cos` finds nothing):

   | Fact | angle form | pair form |
   |---|---|---|
   | keeps length | `rot_normSq` | `rotPlane_preserves_dot` |
   | compose = add angles | `rot_add` | `rotPlane_comp` |
   | commute | `rot_comm` | `rotPlane_comm` |
   | homogeneous / additive | `rot_smul`, `rot_add_vec` | `rotPlane_smul`, `rotPlane_sub` |

   `bootstrap-rotation.rst` cites both families side by side for one set of claims, and
   `proof-rotate-from-a-to-b.rst` says Lean states commutativity "twice". One bridge,
   `rot θ v = rotPlane (cos θ) (sin θ) v` for a vector `v`, would make the `rot_*` column
   one-line corollaries (or removable).
2. **`Exp.G2.expBivector` and `Rotation2D.fullAngleRotor` are the same definition**
   (`add (smul (cos θ) one) (smul (sin θ) e_12)`), in two files, with no theorem saying so.
3. **`R*R̃ = |R|²*1` for the from-vectors versor, four times:**
   `mul_reverse_self_of_isEvenVersor` (general), `G2.versorFromVectors_mul_reverse`,
   `G3.versorFromVectors_mul_reverse`, `G3.versorFromVectors_mul_reverse_coord`.
   **`R*R⁻¹ = 1`, three times:** `mul_inverse_self_of_isEvenVersor`,
   `versorFromVectors_mul_inverse_coord`, `versorFromVectors_mul_inverse`. Note the general
   `mul_inverse_self_of_isEvenVersor` † is itself used by nothing — the special cases are consumed
   instead. Cause: `isEvenVersor_versorFromVectors` lives in `Rotor.lean`, downstream of
   `Sandwich.lean`. Moving it into `Sandwich.lean` lets the general lemmas serve everywhere,
   deletes five special cases, and removes `rotation_preserves_dot`'s inline re-derivation.
4. **`|a|² = a₁² + a₂²` for a vector:** `Versor2D.magnitude_sq_vec` (reals),
   `StandardPosition2D.magnitude_sq_of_isVector` (object), and inline twice in
   `Rotor.normSq_versorFromVectors` (`hA`, `hB`). Same in 3D (`Rotation3D.magnitude_sq_vec`,
   `StandardPosition.magnitude_sq_of_isVector`, `Rotor` inline).
5. **The unit-pair lemma, three times:** `StandardPosition2D.cs_unit`,
   `Bootstrap2D.cs_unit_unalign` (same with `+b₂`), `RotateFromTo2D.cs_a_unit` (reals).
6. **"Carries `a` to `b`'s direction" in 𝒢₂, seven statements:** `rot_from_to`,
   `fullAngleRotorFromTo_carry`, `rotateFromTo_carries`, `rotateFromToProj_normalize`,
   `G2.sandwich_carries_from_to`, `ProjectionRotation2D.projRotation_carries_from_to`,
   `rotorSandwich_rotorFromVectors_carries_from_to`. The last three are legitimately linked
   (`projRotation_eq_sandwich`, `rotorSandwich_rotorFromVectors`). `rotateFromTo_carries` and
   `rotateFromToProj_normalize` are the same fact about the same map
   (`rotPlane_fromTo_eq_rotateFromToProj`), once in coordinates and once in objects.
   `rot_from_to` is the dead one.
7. **`Rotor.sandwich_eq_rotorSandwich_of_isRotor`** restates
   `Sandwich.sandwich_eq_reverse_sandwich_of_isRotor` through the `rotorSandwich` abbreviation
   (by design; harmless). `Rotation2D.sandwich_rotor` and the `Sandwich` reverse-sandwich leaves
   spell `mul (mul R v) (reverse R)` inline, so the corpus has two spellings of one operation.
8. `PlaneRotation3D.rotorSandwich_planeRotor_fixes_normal` is close to
   `Sandwich.sandwich_fixes_own_normal` at `R = planeRotor θ i` (whose own normal is
   `−sin(θ/2)` times `i`'s), and is derivable from `rotorSandwich_planeRotor`. Not a strict
   duplicate.

The prior list's `normalize`/`normalizeVec` and `uvec` magnitude duplicates stand.

#### The parallel developments of rotation: what each backs

| Chain (files) | Book pages | Python | Verdict |
|---|---|---|---|
| Angle form: `rot`, `fullAngleRotor`, `rotor`, `uvec` (`Rotation2D`) | `proof-rotate`, `geometric-product`, `rotation-graph-paper` (via `rot_basis_decomp`), `rotation-from-vectors`, `bootstrap-rotation`, `bootstrap-product`; one line of `proof-rotate-from-a-to-b` | `g2.Vector.rotate`, 2D `plane_rotation` | Well backed. Dead: `rot_from_to`, `rotor_unit'` |
| Cosine/sine form: `rotPlane`, the three turns (`RotateFromTo2D`) | `proof-rotate-from-a-to-b`; `bootstrap-rotation-from-projection` ("coordinate counterparts") | `standardposition.rotation_from_to` (docstring cites no Lean) | Backed, but scalars-in, and duplicates the angle form's basic facts (§3.1) |
| From scratch, object form (`Bootstrap2D`) | `bootstrap-rotation-from-projection`, `bootstrap-product`, `bootstrap-rotation-from-product`, `bootstrap-projection-from-product`; also Part I `projection` | `standardposition.rotation_from_to`, `project`/`reject` | Well backed; the best-cited file in the slice. Overlaps `RotateFromTo2D` (§3.6) |
| Versor from two vectors (`Versor2D`, `Rotation3D`, `Sandwich`) | `bootstrap-rotation-from-product` (sandwich section), `rotation-from-vectors` ("Vectors of any length", prose only) | `versor_from_vectors`, `sandwich`, `inverse`, `versor_rotation` | Backed by Python; the book cites only `versor_mul_from_eq_bisector` |
| …its 3D "three goals" (`RotateComponents`) | none | none directly | No page, no function, superseded (§2) |
| Reverse-sandwich rotor chain (`Rotor`) | none (only the 2D cheat sheet's row) | `rotor_from_vectors` (cites `rotorSandwich_normalize`), `tests/test_rotor_from_vectors.py` | Backed by Python only. Not a second proof of the versor chain: it transfers it through one bridge, as designed |
| Plane rotor by angle in 3D (`PlaneRotation3D`) | none (cheat-sheet rows only) | `plane_rotation`, `bivector_rotation` | Backed by Python only; cited by nothing reader-facing |
| Exponential (`Exp`) | none (cheat-sheet rows; `displayrotations` section) | `base.exp` | Thin: because `exp` is *defined* as the closed form, the theorems are `cos² + sin² = 1` three times. The fact the Python docstring and notebook actually state is missing (§4) |

No two chains prove the same theorem about the same object twice, with the exceptions in §3.1,
§3.3 and §3.6. What is missing is the *bridges* between them (§4), which is why they read as
parallel rather than as one development.

---

### 4. Missing

#### 4a. Citations that do not say what the page claims

1. `proof-rotate-from-a-to-b.rst`: "`rotPlane_conj_collapse`, which rests on `rotPlane_comm`". It
   does not (§1b.1).
2. `notebooks/rotation-from-vectors.py`, last cell: "the versor route, the projection route, and
   the angle-free three-turn construction … are one and the same rotation, a fact the Lean proofs
   state directly (`fullAngleRotorFromTo_carry`, `projRotation_carries_from_to` /
   `projRotation_eq_sandwich`)". None of those mentions the three-turn construction, and
   `fullAngleRotorFromTo_carry` is about `uvec α`, not about the routes agreeing. The theorems that
   do it are `Bootstrap2D.rotPlane_fromTo_eq_vec_mul` + `ProjectionRotation2D.projRotation_eq_vec_mul`
   + `projRotation_eq_sandwich`.
3. `rotation-from-vectors.rst`: the page's point is "no angle was named anywhere", and for
   `â * (â * b̂) = b̂` it cites `fullAngleRotorFromTo_carry`, a theorem parameterized by the angles
   `α`, `β`. The angle-free object-form statements exist:
   `Bootstrap2D.rotateFromToProj_eq_vec_mul` + `rotateFromToProj_normalize`.
4. `bootstrap-rotation.rst`: "`rot_vec` (the formula)". `rot_vec` is `rfl`, the definition
   unfolded. The page's derivation (write `v` by length and angle; rotating adds the angle) is
   `Rotation2D.rot_polar`, which no page cites; the blend formula `eq-bootstrap-rotation` is
   `rotPlane_vec_eq_blend`, for the other family.
5. `tests/test_sandwich_grades.py`: "the runnable twin of `Sandwich.lean`'s … grade coverage".
   Lean covers only vector → vector (`sandwich_evenVersor_vec_isVector`, 𝒢₃).

Every Lean name cited by the eleven pages and ten notebooks exists, in the file named.

#### 4b. `twin:` tags

- `notebooks/projection.py` tags `GacalcProofs.G2.mul_proj_eq_dot` and
  `GacalcProofs.G2.mul_reject_eq_wedge`; `Bootstrap2D.lean` has no `-- twin:` line above either.
- `notebooks/dual.py` tags `GacalcProofs.G2.dual_perp`; `StudentTrigForms.lean` has no tag.
  (By the doc's own orphan rule: a tag that appears once has lost its other side.)
- None of the rotation notebooks carries a tag. Not required (no backfill), noted only.

#### 4c. Results the book, notebooks or docstrings state that have no Lean theorem

Ordered by how much they would tie the slice together.

1. **`rot θ v = rotPlane (cos θ) (sin θ) v`** (vector `v`), and with it
   **`rot θ v = cos(θ)*v + sin(θ)*rot90 v`** and **`rot (π/2) v = rot90 v`** — the book's
   `eq-rotate-formula` / `eq-bootstrap-rotation` and base case, and literally what
   `g2.Vector.rotate` computes. Stated for `rotPlane` only.
2. **The angle of the from-to rotation:** `notebooks/rotate.py` checks
   `v.rotate(θ) == rotation_from_to(a, b)(v)` with `θ` the angle from `a` to `b`. No Lean theorem
   connects `rotPlane (cos_between a b) (signed_sin_between a b)` to `rot (β − α)` (e.g. on
   `uvec α`, `uvec β`).
3. **`exp(−(θ/2)*i)` is the half-angle rotor** — `base.exp`'s docstring ("exactly the half-angle
   rotor that `plane_rotation` / `bivector_rotation` build") and the last section of
   `displayrotations`. Missing in 2D (`expBivector (−θ/2) = rotor θ`) and 3D (`planeRotor`).
4. **The un-normalized versor in angle form:**
   `sandwich (versorFromVectors (uvec α) (uvec β)) v = rot (β − α) v`. This is the first
   computation of `displayrotations` and what `versor_rotation` does; Lean has it only for the
   normalized rotor with the reverse sandwich (two rewrites away).
5. **Step 3's rotation equals `projRotation`** — `bootstrap-rotation-from-projection.rst` and its
   notebook's "gacalc agrees" cell. Lean has both sides equal to `v*(â*b̂)` in two files, up to
   `mul_assoc`; no theorem joins them.
6. **`plane_rotation(a, b)`: "positive θ turns from `a` toward `b`"**, and that at the angle
   between `a` and `b` it is `versor_rotation(a, b)`. `rotorSandwich_planeRotor` needs
   `IsBivector i`, `normSq i = 1`, and nothing shows `normalize (a ∧ b)` satisfies them (𝒢₃ has
   no `isBivector_wedge_of_isVector`). So the 3D plane rotor is linked neither to the Python's
   actual argument nor to the versor chain; `rotorFromVectors_uvec` does this in 2D only, though
   `rotor_from_vectors`'s docstring states it in general.
7. **`h` bisects the angle** — stated by `versor_from_vectors`'s docstring and by
   `bootstrap-rotation-from-product.rst`; `Rotation3D`'s header says "not done here".
   `cos_between a h = cos_between h b` is now statable. Also the docstring's own identity
   `h * a = |a| * R` (Lean has the companion `R * a = |a| * h`).
8. **`base.angle`, `plane_of_rotation`:** `R == r * (cos(θ) + sin(θ) * I)` has no Lean statement
   (`tests/test_versor_extraction.py` checks it numerically/symbolically).
9. Smaller: the sandwich keeps a bivector a bivector (`base.sandwich` docstring and doctest); a 𝒢₂
   twin of `sandwich_evenVersor_vec_isVector`; `(â*b̂)*v` turns the other way
   (`bootstrap-rotation-from-product.rst`, "The order matters"); `reverse (planeRotor θ i) =
   planeRotor (−θ) i` (the `backward` of `plane_rotation`); `rotPlane` additivity (only `_sub` and
   `_smul` exist) for "it is linear" on Step 3; `rot90` of a polar vector is the vector a quarter
   turn further (`bootstrap-rotation` notebook); `exp` of the 𝒢₃ pseudoscalar.

#### 4d. Theorems that exist and should be cited

`rot_polar` (from `proof-rotate.rst` and `bootstrap-rotation.rst`);
`sandwich_rotor_eq_vec_mul_fullAngleRotor` and `sandwich_rotor_eq_rot` (from
`geometric-product.rst`, which says "prove them equal in effect" without a name);
`G2.sandwich_carries_from_to`, `rotorSandwich_normalize`, `rotorFromVectors_uvec` (from
`rotation-from-vectors.rst`, "Vectors of any length"); `sandwich_evenVersor_vec_isVector` and
`rotorSandwich_rotorFromVectors_uvec` (from `displayrotations`); `rotorSandwich_planeRotor` (from
`transforms.plane_rotation`/`bivector_rotation` — `transforms.py` cites no Lean at all); a Lean
name in `standardposition.rotation_from_to`'s docstring (`rotPlane_fromTo_eq_rotateFromToProj`,
`rotateFromToProj_normalize`).

---

### 5. Overall judgment

The mathematics in this slice is right: every definition matches the Python in sign, side and
half-versus-full angle, every cited name exists, and the newer files (`Bootstrap2D`, `Rotor`,
`PlaneRotation3D`, the reverse-sandwich part of `Sandwich`) are in the house form — objects in,
structural where there is a reason. The slice is not in good shape as a *whole*, for one reason:
it is seven developments of rotation written at different times, and the older ones
(`Versor2D`/`Rotation3D`, the tail of `Sandwich`, `RotateComponents`, `RotateFromTo2D`, `Exp`)
still have the pre-sweep shape, while the bridges that would make them one development were never
written. None of the earlier review's findings for these files has been applied. About a quarter
of the declarations are read by nothing outside their own file; most of those are legitimate
endpoints behind a Python docstring, but `RotateComponents.lean` and thirteen of
`StudentTrigForms.lean`'s fourteen theorems have neither a page nor a function behind them.

The changes most worth making, in order:

1. **Write the three bridges** (§4c.1–3): `rot` ↔ `rotPlane` (with the blend and the quarter
   turn), the from-to rotation's angle, and `exp(−(θ/2)*i) = rotor`. They turn the angle form, the
   cosine/sine form and the exponential into one chain and let a column of duplicate lemmas go.
2. **Prove `versor_mul_from_eq_bisector` structurally and move `isEvenVersor_versorFromVectors`
   into `Sandwich.lean`.** That deletes four `_coord` leaves and five special-case lemmas, uses the
   two lemmas written for the purpose and never used, and makes the proof read like the docstring.
3. **Restate `RotateFromTo2D` on `alignSP`/`unalignSP` in object form**, prove
   `rotPlane_conj_collapse` by `rotPlane_comm` + `rotPlane_inv` so the book's sentence is true,
   and state Step 3's rotation with `cos_between`/`signed_sin_between`.
4. **Delete `RotateComponents.lean`** (keep `sandwich_ahat` if wanted) and the dead list in §2;
   decide whether `StudentTrigForms` is cited by the book or cut to what is, and fix its guards
   either way.
5. **Fix the five citations in §4a and the two orphan `twin:` tags**, and cite `rot_polar`.

## C. Projection, standard position and frames

Reviewed 2026-11-22, read-only. Nothing was built: every "this proof could be restated as …" below is
a LEAD from reading, not a compiled proof. Every "unused"/"dead" claim was checked with
`git grep -w <name> -- proofs book notebooks src tests tools` (table saved at
(a session scratch file, not kept); note its
`lean:` column over-counts, because G2 and G3 share short names).

### What was read

Read in full (every line): `proofs/GacalcProofs/` `Projection2D`, `Projection3D`, `Reflect`,
`StandardPosition`, `StandardPosition2D`, `CrossStandardPosition`, `ProjectionRotation2D`,
`ProjectionRotation3D`, `ReciprocalFrame2D`, `ReciprocalFrame3D`; `proofs/README.md`,
`proofs/GacalcProofs.lean`, `proofs/check.sh`, `proofs/scripts/CheckAxioms.lean`,
`proofs/lakefile.toml`; `tasks/reference/lean-ga-proof-architecture.md`,
`tasks/reference/lean-python-notebook-workflow.md`; `src/gacalc/standardposition.py`; the
`project`/`reject`/`reflect`/`projected_onto`/`rejected_away_from`/`reflected_across` methods of
`base.py`; `projection_rotation`, `require_on_line`, `coordinate_along`, the four
`line_to_*`/`line_from_*` factories of `transforms.py`; `frame.py` from `kronecker_delta` to the end
plus `make_orthogonal_frame`'s body; the twelve book pages (`projection`, `product-from-projection`,
`reflection`, `projection-rejection-3d`, `reflection-3d`, `proof-projection`, `proof-projection-3d`,
`proof-cross`, `frames-qr`, `proof-reciprocal-frame`, `bootstrap-projection`,
`bootstrap-projection-from-product`); `tasks/review/2026/11/08/repo-review.md` §7;
`tasks/lean-proofs-remove-extras.md`.

Skimmed (definitions or targeted greps only): `G2.lean`, `G3.lean`, `Bootstrap2D.lean` (statements
of its first six theorems), `Rotor.lean` (`normSq_versorFromVectors*`), `Sandwich.lean` (theorem
names), `StudentTrigForms.lean` (three theorems); `tasks/reference/reduction-to-standard-position.md`
(the base-case table and the whole "What is proven" section, not the rest);
`tasks/reference/frames-qr-and-reciprocal-frames.md` (grep for Lean/peel only).

Notebooks: read through a filter that kept every Markdown line and every line computing a
projection, rejection, reflection, cross product, rotation or check, and dropped the ePiX drawing
code: `projection`, `product-from-projection`, `reflection`, `reflection-3d`,
`projection-rejection-3d`, `proof-projection`, `proof-projection-3d`, `proof-cross`,
`bootstrap-projection`, `bootstrap-projection-from-product`. Headings and Lean/`twin:` greps only:
`proof-reciprocal-frame.py`, `frame-qr-2d.py`, `frame-qr-3d.py`. Not read: `frame.py` lines 1-270
and 353-468 (independence tests, `prefix_blades`, the two Hestenes orthogonalizations), the rest of
`base.py` and `transforms.py`, `entrypoint/`.

### Status of the prior findings that concern these files

Prior record: `tasks/review/2026/11/08/repo-review.md` §7.2 and `tasks/lean-proofs-remove-extras.md`.

| Prior finding | Status now |
|---|---|
| `Projection2D`: `vec_wedge_I_eq_zero`, `reject_from_I_eq_zero` take free reals | FIXED: now `wedge_I_eq_zero {a} (ha : IsVector a)` and `reject_from_I_eq_zero {a} (ha)` |
| `Projection3D`: `wedge_reject`, `plane_eq_wedge`, `mul_vec_inverse_self` take free reals | FIXED (objects + `IsVector`); their proofs still rebuild `vec a.c1 a.c2 a.c3` and call G3 `_coord` leaves, see §1 |
| `Projection3D`: `reject_eq_proj_normal_coord`, `project_eq_sub_reject_coord` serve only `proj_plane_eq_project_onto`, with duplicate object twins | STILL PRESENT |
| `ProjectionRotation3D`: 16 `_coord` leaves, one wrapper each | STILL PRESENT (counted 16) |
| Dead wrappers `wedge_vec_wedge_self`, `reject_in_plane_self`, `project_onto_in_plane_self`, `inner_vb_mul_reverse_self` | STILL PRESENT, and the list was short: see §2 |
| `G2.reject_vec_eq_coord` has one consumer | STILL PRESENT (`StandardPosition2D.lean`) |
| `normSq_wedge_vec'` (`ReciprocalFrame2D`) duplicates `G2.normSq_wedge_vec` | STILL PRESENT |
| `normSq_wedge_vec3`/`crossSq`/`det3` (`ReciprocalFrame3D`) restate `G3.normSq_wedge_vec` and `signedVolume` | STILL PRESENT |
| `G2.sub_mul` lives in `StandardPosition2D`; G3 `zero_mul`/`add_zero`/`zero_add` live in `ProjectionRotation3D` | FIXED: all four are in `G2.lean`/`G3.lean` |
| `Projection3D` header "Still to come: …" | STILL PRESENT (module docstring, the paragraph ending "…3D sandwich as a corollary of the G2 `sandwich_rotor`") |
| `Projection2D` header claims a result no theorem proves ("projecting it onto `I₂` recovers the vector") | STILL PRESENT; there is no 2D `project_onto` at all |
| `CrossStandardPosition` capstone comment says the angles are introduced inside, "exactly as `projectSP_eq_proj` hides its angles in `alignSP`" | STILL PRESENT; `cross_via_reduction` takes six angle reals as parameters |
| `rejectSP_eq_reject` (2D and 3D) takes both `magnitude b ≠ 0` and `normSq b ≠ 0` | STILL PRESENT in both |
| `cross_via_reduction_of_vectors` takes seven reals | STILL PRESENT |
| remove-extras #2: `field_simp <;> ring` whose `ring` never runs (`ProjectionRotation3D`) | STILL PRESENT, last line of `projRotation_carries_from_to_coord` |
| remove-extras #6: four `hn` "not referenced" false positives (`rw … at hn`) | STILL PRESENT: `inplane_perp_reject_coord`, `project_perp_reject_coord`, `versor_mul_project_eq_coord`, `versor_mul_reject_comm_coord` |
| remove-extras #7: `cross_reduced` `ext <;> ring` falls back to `ring_nf` | STILL PRESENT |
| remove-extras #8: `vec_mul_bisector_eq_coord` `try ring` | STILL PRESENT |
| remove-extras #3: `sandwich_preserves_wedge` (𝒢₂) "in `Projection2D.lean`" | The theorem is no longer in `Projection2D.lean` (out of this slice now) |

### 1. Written as they should be?

#### 1.1 Definitions against the Python

**`projectSP`/`rejectSP` (3D) against `standardposition.project_sp`/`reject_sp`: faithful.** Checked
step by step.

- Python's first turn is `rotation_from_to(shadow, |shadow| * e_1)`, cosine `b_x/k`, sine `-b_y/k`,
  the identity when the shadow is zero. Lean: `xyCos`/`xySin` with the same `if k = 0` branch.
- Second turn: `rotation_from_to(tilt, |b| * e_1)` with `tilt = (k, b_z)`, cosine `k/m`, sine
  `-b_z/m`. Lean `alignSP` uses `xyMagnitude b / magnitude b` and `-b.c3 / magnitude b`.
- `in_plane` copies a coordinate pair into 𝒢₂, rotates, writes back. Lean `rotXY`/`rotXZ` are
  defined exactly so, through `G2.rotPlane` on `G2.vec v.c1 v.c2`.
- `rotate_back` undoes the xz turn first, then the xy turn, each with the sine negated: `unalignSP`.
- "Keep the x-component": `e_1 * align(a).coefficient(e_1)` is `vec (alignSP b a).c1 0 0`.
- `reject_sp = a - project_sp` is `rejectSP = sub a (projectSP a b)`.
- Hypotheses: Python raises on `b = 0`; Lean takes `magnitude b ≠ 0`. Lean allows any multivector
  `a` (Python requires a vector); harmless.

**`rejectSP` does not match the BOOK's definition of the rejection.**
`book/docs/bootstrap-projection.rst` (`eq-bootstrap-projection-definition`) and the notebooks
`proof-projection.py`, `bootstrap-projection.py` and `proof-projection-3d.py` define the rejection
as "rotate, keep the y-coordinate (3D: the rest), rotate back".
`tasks/reference/reduction-to-standard-position.md`'s base-case table cites that formula as "Lean
`rejectSP`". Lean's `rejectSP` is `a − projectSP`, the Python `reject_sp`. No theorem says
`unalignSP b (vec 0 (alignSP b a).c2) = reject b a`. The pieces exist and are otherwise unused:
`reject_onto_x_axis`, `rotPlane_sub`, `vecReject_rotPlane_equivariant`, `unalignSP_alignSP`.

**2D `projectSP`/`rejectSP` have no Python counterpart**, and their doc comments say
"(`project_sp a b`)" as if they did. Python's `project_sp` is 𝒢₃ only. The honest 2D twin is the
notebook's `inverse(R)(Scalar(x) * e_1)` with `R = rotation_from_to(b, e_1)`; the formulas agree
(cosine `b₁/|b|`, sine `−b₂/|b|`).

**`proj` against `base.project`: equal for vectors, but only 2D proves it is the Python formula.**
Python computes `(A · B) * B⁻¹`. Lean `proj a b := smul (dot b a / dot a a) a`. The bridge
`proj a b = mul (scalar (dot b a)) (inverse a)` exists in 2D (`Bootstrap2D.proj_eq_dot_mul_inverse`)
and not in 3D, although `notebooks/proof-projection-3d.py` writes the projection as
`(a · b) * b⁻¹`.

**Lean has two projection definitions where Python has one formula.** `proj` (onto a vector) and
`project_onto` (onto a bivector, through `inner_vb`). `project_onto` is wrong for a vector `onto`
(`inner_vb` of two vectors is 0), which its doc comment does say. `reject` is uniform, as in Python.
There is no `project_onto` in 𝒢₂, so `ProjectionRotation2D.projRotation` spells the projection onto
the plane as `sub v (reject (wedge f t) v)`. Python's `projection_rotation` calls
`cls.project(plane)`, that is `(v · B) * B⁻¹`. No 2D theorem shows the Hestenes projection onto the
plane is the identity, the claim in `Projection2D.lean`'s header.

**`projRotation` (3D) against `transforms.projection_rotation`: the same expression on its
non-parallel branch only.** Python returns the identity for parallel same-way vectors and raises
for opposite ones. Lean's definition gives `0` when `f ∧ t = 0`, and every 3D theorem excludes that
case with `hpn`, so nothing false is claimed.

**`reflectVec`/`reflectPlane` against `base.reflect`: faithful** (projection minus rejection, vector
and bivector cases).

**`recip1/2/3`, `frameMap`, `invReciprocal` against `frame.py`: faithful to eq 3.7 and to the forward
map.** Python reads each coordinate as `coordinate_along(P_m(y), along=P_m(v))`, which is
`(m·y)/(m·v)`; Lean reads `dot (recip_i) y` directly, and `coord*_of_perp` is the bridge. Fine.

**The peel inverse is not a step-by-step mirror, in two ways.**

1. Python divides by `w·v` (the coordinate of `P_w(y)` along `P_w(v)`); Lean's
   `peelLast`/`peelMid` divide by `|w|²`, the book's formula. The bridge `w·v = |w|²` is proven in
   3D (third conjunct of `reject_plane_facts`, second of `reject_line_facts`) and is not stated in
   2D.
2. Python's `orthogonal_vectors()` is `make_orthogonal_frame`: iterated vector rejections, so
   `w₃ = rej_{w₂}(rej_{v₁}(v₃))`. Lean's `peelLast` uses `reject (wedge a1 a2) a3`, rejection from
   the plane bivector. They are equal, but no Lean theorem says so, and the coverage map lists
   `Frame.to_invertible_function` (both methods) as HAS.

#### 1.2 Statement shape (free reals that build `vec …`)

- `StandardPosition2D.rotPlane_vec_eq_blend (c s x y : ℝ)` builds `vec x y`. It is cited by
  `book/docs/bootstrap-rotation.rst`. Should be `{v} (hv : IsVector v)`; `c`, `s` are genuine
  scalars.
- `StandardPosition.rotate_b_to_e1` and `rotate_b_to_e1_magnitude` take `b1 b2 b3`. The object form
  already exists: `alignSP_self`, which does not use them. Their only consumer is
  `CrossStandardPosition.reduceToPlane_a_on_e1`.
- `CrossStandardPosition.reduceToPlane_a_on_e1`, `reduceToPlane_b_in_plane`,
  `cross_via_reduction_of_vectors` (seven reals; prior finding). The capstone also excludes `a` on
  the `e₃` axis (`hk`), a case `projectSP_eq_proj` handles through `xyCos`/`xySin`. LEAD: define the
  reduction through `alignSP a` plus a third turn with its cosine and sine read off
  `alignSP a b`, and state `cross a b = …` for `IsVector a`, `IsVector b`. That removes the
  seven-real theorem, `rotate_b_to_e1`, `rotate_b_to_e1_magnitude` and the `hk` restriction.
- `rotXY_aligns_xy`, `rotXZ_aligns_xz`, `rotYZ_aligns_yz`, `rotPlane_aligns`: coordinate leaves with
  free `k`, `m`. Acceptable as computed-coordinate leaves; `rotPlane_aligns` has one consumer.
- `proj_onto_x_axis (m) … : proj (vec m 0 0) v = vec v.c1 0 0`, `reject_onto_x_axis`,
  `proj_reduced`, `vecReject_reduced`, `cross_reduced`: literal evaluations; acceptable as base
  cases.
- `wedge_I_eq_zero`, `reject_from_I_eq_zero`, `reject_plane_eq_zero` conclude `= ⟨0, 0, 0, 0⟩`.
  `G2.zero` exists (`G2.lean`); the architecture doc's remark that "G2 has no `zero`" is stale.
- `ReciprocalFrame2D/3D` `_vec` leaves take reals. Allowed by the house rule (the right side is a
  computed coordinate vector) and the header says so.

#### 1.3 `smul k one` where the house rule says `scalar k`

`StandardPosition.mul_proj_eq_dot` concludes `smul (dot b a) one`, and
`mul_eq_proj_dot_add_reject_wedge` concludes `add (smul (dot b a) one) (wedge a b)`. The
architecture doc ("Embed a scalar with the `scalar` constructor") says all such conclusions now read
`scalar (…)`. Their 2D namesakes do: `Bootstrap2D.mul_proj_eq_dot : mul a (proj a b) = scalar (dot a b)`.
So two theorems with the same name, both carrying notebook `twin:` tags, differ in form and in the
order of the dot's arguments.

#### 1.4 `_coord` leaves with one consumer

- `ProjectionRotation3D`: all 16 (see §1.6 for which are fragile).
- `Projection3D`: `reject_eq_proj_normal_coord` and `project_eq_sub_reject_coord` (one consumer:
  `proj_plane_eq_project_onto`); `project_add_reject_coord` (consumers are three other `_coord`
  proofs). All three duplicate the proofs of their object twins.
- `StandardPosition2D.reject_vec_eq_coord` (one consumer, `reject_vec_eq`).

#### 1.5 Brute computation where a structural proof would show the reason

- `ProjectionRotation3D.project_perp_reject_coord` (`maxHeartbeats 4000000`, `field_simp; ring` on
  nine variables). LEAD: it is `reject_perp_dot`. By `project_eq_sub_reject` and
  `reject_eq_proj_normal`, `project = c − proj_n c` and `reject = proj_n c` with `n = dual B`; the
  reverse of a vector is itself; so the scalar part is `dot (c − proj_n c) (k * n) = k * 0`.
- `versor_mul_project_eq_coord` and `versor_mul_reject_comm_coord` (`maxHeartbeats 8000000` each)
  are stated on `wedge (vec …) (vec …)`, whose entries are quadratic. The architecture doc's own
  "literal-then-instantiate" technique says to state such facts for a bivector with three free
  components. LEAD: two object lemmas for `{B} (hB : IsBivector B)`, "the in-plane part
  anticommutes with `B`" and "the perpendicular part commutes with `B`", then split
  `versorFromVectors f t` into its scalar and its bivector part with `add_mul`/`mul_add`. The
  second lemma also has a reason: `reject B c` is a multiple of `dual B`, which is perpendicular
  to `f` and `t` (`dual_wedge_perp_left_dot`/`_right_dot`), so it anticommutes with each
  (`vec_anticomm_perp`) and commutes with `t * f`.
- `ReciprocalFrame2D.dot_reject_self` and `ReciprocalFrame3D.reject_line_facts` re-derive in
  coordinates what `reject_vec_eq` + `reject_perp_dot` give in two rewrites. `reject_line_facts`
  also takes `a3`, `ha3` and the volume hypothesis although it is about `a1`, `a2` only; a
  nondegenerate `a1 ∧ a2` suffices.
- `ReciprocalFrame3D.reject_plane_facts` (first two conjuncts) follows from `reject_eq_proj_normal`
  and `dual_wedge_perp_left_dot`/`_right_dot`.
- `ReciprocalFrame2D` is coordinates throughout (the architecture doc says so), while 3D proves the
  peel structurally (`invPeel_comb`) and derives `recip*_eq_normal_div` from `reconstruct_dual`. 2D
  has neither `invPeel_comb` nor `reconstruct_dual`, and its `recip1/2_eq_normal_div` close with a
  `first | ring1 | linear_combination q * hm2 | linear_combination (-q) * hm2 | …` guess list. The
  3D method works unchanged in 2D. The book proves theorem 4 from theorem 3 by linearity; neither
  dimension's `reconstruct` does.
- `Projection3D.plane_eq_wedge`, `mul_vec_inverse_self`, `reject_vec_eq`,
  `StandardPosition.mul_proj_eq_dot`, `mul_eq_proj_dot_add_reject_wedge`: object statements whose
  proofs `rw [eq_vec_of_isVector …]` and then use `dot_self_vec_eq_normSq_coord`,
  `mul_vec_self_coord`, `wedge_self_vec_coord`. The object forms `G3.dot_self_vec_eq_normSq` and
  `G3.mul_vec_self` exist. For example `plane_eq_wedge`'s `hdaa` is
  `rw [dot_self_vec_eq_normSq hav]; exact ha`.
- `projectSP_eq_proj` (2D and 3D) unfolds `alignSP`/`unalignSP` and replays `rot*_inv`, instead of
  using `unalignSP_alignSP`, which no proof uses (the 2D one is cited by the book).

#### 1.6 How much of `ProjectionRotation3D` could be written in the 2D file's style

All of it, by reading. Per leaf:

| `_coord` leaf | Proof today | Verdict |
|---|---|---|
| `wedge_vec_wedge_self_coord` | `ext <;> ring` | delete: the object `wedge_vec_wedge_self` is already getter-native, with its own proof |
| `reject_in_plane_self_coord` | 1-line `rw` | fold into the object theorem |
| `inner_vb_mul_reverse_self_coord` | `ext <;> ring` | getter-native, easy |
| `project_onto_in_plane_self_coord` | `rw` chain | object-native as is |
| `projRotation_carries_from_to_coord` | `rw` chain + 8 lines re-deriving `|f|² = normSq f`, `|f| ≠ 0` | object-native exactly like the 2D proof: `G3.mul_vec_self`, `magnitude_sq_eq_normSq`, `magnitude_ne_zero_of_normSq_ne_zero` exist |
| `normSq_mul_vec_coord` | `ring` | getter-native, easy |
| `plane_pythagorean_coord` | `rw` chain | object-native |
| `projRotation_isometry_coord` | `set` + `rw` chain + 12 lines of √ boilerplate | object-native; not fragile |
| `normalizeVec_to_mul_versor_eq_bisector_coord` | `rw` chain that calls the OBJECT theorem `from_mul_versor_eq_bisector` with `isVector_vec` | inverted layering; object-native |
| `normalizeVec_mul_versor_eq_reverse_coord` | `rw` chain | object-native |
| `projRotation_eq_sandwich_coord` | `calc` + `rw`, no coordinate arithmetic of its own | object-native |
| `vec_mul_bisector_eq_coord` | `set`/`clear_value`/`linear_combination` | genuinely delicate (√), one consumer; same shape as the 2D `key_reverse_sq`, which is getter-native |
| `project_perp_reject_coord` | heavy | fragile as written; structural proof available (§1.5) |
| `inplane_perp_reject_coord` | heavy (8M heartbeats) | fragile; one consumer |
| `versor_mul_project_eq_coord`, `versor_mul_reject_comm_coord` | heavy (8M each) | fragile as written; restate over `IsBivector B` (§1.5) |

So 11 of 16 have no coordinate content worth a leaf, 1 is √-delicate, 4 are heavy. None is shared
by two object theorems, so none meets the rule "fragile AND shared by ≥2". The object-form
conversion needs one missing lemma: `G3.isBivector_wedge_of_isVector` (the architecture doc records
it as skipped for want of a consumer; this is the consumer).

Two shortcuts worth a decision:

- **The 3D hypotheses are redundant.** `normSq (wedge f t) ≠ 0` implies `normSq f ≠ 0`,
  `normSq t ≠ 0` (`ReciprocalFrame3D.sumSq_ne_zero_of_crossSq` proves that shape) and, by Lagrange
  (`Rotor.normSq_versorFromVectors`), `normSq (versorFromVectors f t) ≠ 0`. So
  `projRotation_carries_from_to`, `projRotation_isometry` and `projRotation_eq_sandwich` (3D) need
  only `hpn`. Not proven in Lean; a LEAD. `Rotor.lean` imports this file, so the Lagrange closed
  form would have to move below it.
- **The 3D isometry could be one line** once that holds: rewrite with `projRotation_eq_sandwich`,
  then `sandwich_preserves_normSq`. That would retire `normSq_add`, `normSq_add_of_orthogonal`,
  `normSq_mul_vec(_coord)`, `inplane_perp_reject(_coord)`, `project_perp_reject(_coord)`,
  `plane_pythagorean(_coord)` and `projRotation_isometry_coord`: about 130 lines and 12M heartbeats.
  The cost: the isometry would rest on the versor route. Nothing in the book uses the independent
  3D isometry (the book cites the 2D file only).

#### 1.7 Do the 2D and 3D files prove the same chain twice?

- **Standard position.** `G2` and `G3` are separate structs with no embedding, so
  `projectSP_eq_proj` is proven twice with the same skeleton (about 80 lines). A transfer would
  need an embed/restrict layer larger than the duplication. Acceptable, and the book wants 2D
  first.
- **Within 3D the plane rotations are proven three times.** `rotXY`/`rotXZ`/`rotYZ` are defined
  through `G2.rotPlane`, but no 3D lemma uses a `G2.rotPlane_*` lemma: `_smul`, `_sub`,
  `_preserves_dot`, `_inv`, `_aligns_*`, `isVector_*`, `proj_*_equivariant`,
  `vecReject_*_equivariant`, `cross_*_equivariant` each appear three times (27 lemmas). Two cheap
  shares: (1) one generic lemma "a map that commutes with `smul` and preserves `dot` commutes with
  `proj`" (and with `sub`, with `vecReject`) replaces the four `proj_*_equivariant` and four
  `vecReject_*_equivariant` proofs in each algebra; (2) `rot*_inv` and `rot*_aligns_*` can be read
  off `G2.rotPlane_inv`/`rotPlane_aligns` componentwise, since the 3D definitions are the 2D
  rotation on a pair. Modest gain; the proofs are short.
- **Projection rotation.** The two files prove `f̂ * t̂ = R̃ * R⁻¹` by different methods: 2D through
  a new √ identity (`key_reverse_sq`), 3D through the bisector identities of `Rotation3D`.
  `Versor2D` has the same bisector identities, so 2D could use the 3D route and drop
  `key_reverse_sq`. In 3D the fact is an anonymous `have hAt` inside the capstone, while 2D names
  it `fhat_that_eq_reverse_mul_inverse` and the book cites it. Naming the 3D one would give the
  dead wrapper `normalizeVec_mul_versor_eq_reverse` a consumer.
- `ProjectionRotation2D.versorFromVectors_mul_vec_eq` ("`R v = v R̃` … true of every even element
  in 𝒢₂", its own doc comment) is stated only for `versorFromVectors f t`. It should be
  `{R} (hR : IsEvenVersor R) {v} (hv : IsVector v)` in `Sandwich.lean`.
- `G2.normalizeVec` is defined in `ProjectionRotation2D`, `G3.normalizeVec` in `Normalize.lean`.
- `G2.reject_vec_eq` lives in `StandardPosition2D`; its 3D twin lives in `Projection3D`. That is
  why `ReciprocalFrame2D` (which imports only `Projection2D`) re-derives rejection facts in
  coordinates.

#### 1.8 Stale or wrong doc comments (new; the prior ones are in the status table)

- `rejectSP_eq_vecReject` (2D and 3D) carries the doc comment "**`reject_sp = reject`:** …", and
  `rejectSP_eq_reject`, the theorem the book and Python cite, has no doc comment.
- `Projection3D.proj_plane`: "(the book's construction)". The Geometry 2 book has no such
  construction; `reflection-3d.rst` states the fact, not this definition.
- `ProjectionRotation3D.normalizeVec_to_mul_versor_eq_bisector_coord`: "From `t R = |t|*h`
  (`from_mul_versor_eq_bisector`)" inherits the misnamed lemma (prior finding on `Rotation3D`).
- `ProjectionRotation3D.projRotation_isometry` and friends: "Thin bridge over the (delicate)
  `_coord` leaf"; per §1.6 the leaf is a `rw` chain.
- `ProjectionRotation2D` header: "Nothing new is proven here that the existing 𝒢₂ lemmas did not
  already give". `key_reverse_sq` and `fhat_that_eq_reverse_mul_inverse` are new.
- `CrossStandardPosition` header: "The same 3-rotation reduction serves `project`, `reject`, AND
  the `cross` product". Only cross has a capstone (§2).
- `ProjectionRotation3D.projRotation_perp`: the doc promises "a fully-perpendicular `v` is fixed";
  the theorem concludes `= reject (wedge f t) v` from the hypothesis `project_onto … = zero`.

### 2. Extraneous

**Dead (no proof uses them, no reader-facing file cites them). High confidence.**

- `ProjectionRotation3D`, the whole "Object-form wrappers" block. Not 4 but all 13 are unused as
  terms: `wedge_vec_wedge_self`, `reject_in_plane_self`, `inner_vb_mul_reverse_self`,
  `project_onto_in_plane_self`, `plane_pythagorean`, `project_perp_reject`, `inplane_perp_reject`,
  `normSq_mul_vec`, `normalizeVec_to_mul_versor_eq_bisector`, `vec_mul_bisector_eq`,
  `normalizeVec_mul_versor_eq_reverse`, `versor_mul_project_eq`, `versor_mul_reject_comm`. (The
  usage report shows some with two mentions; the second is a doc comment.) The capstones call the
  `_coord` forms. Converting the file to object form (§1.6) makes these the live theorems;
  otherwise delete them.
- `ProjectionRotation2D.reverse_versorFromVectors_mul`: unused, and a special case of
  `Sandwich.reverse_mul_self_of_isEvenVersor`.
- `CrossStandardPosition`, the projection/rejection half: `rotYZ_smul`, `rotYZ_sub`, `rotXZ_sub`,
  `rotYZ_preserves_dot`, `proj_rotYZ_equivariant`, `vecReject_rotXZ_equivariant`,
  `vecReject_rotYZ_equivariant`, `proj_reduced`, `vecReject_reduced`. They feed only each other.
  There is no theorem "project (or reject) = reduce, do it in the plane, rotate back", so the
  "uniform tool" the header and the reference doc describe is finished for cross only. Finish it
  (one capstone each) or delete the nine. `StandardPosition.vecReject_rotXY_equivariant` belongs
  to the same unused set.
- `CrossStandardPosition.rotYZ_fixes_e1`: unused; `reduceToPlane_a_on_e1` redoes it inline with
  `ext <;> ring`. It states a sentence of `proof-cross.rst` ("a rotation about `e₁` fixes a vector
  already on it"), so use it there and cite it.
- `StandardPosition2D.vecReject_rotPlane_equivariant`: unused. It is the lemma the missing
  "rejection by rotation" theorem needs (§4).

**Superseded.**

- `StandardPosition.rotate_b_to_e1`, `rotate_b_to_e1_magnitude`: superseded by `alignSP_self`;
  kept alive only by `reduceToPlane_a_on_e1` (§1.2). Medium confidence, depends on restating the
  cross capstone.
- `vecReject` (2D and 3D definitions): a third spelling of the rejection beside `reject` and the
  inline `sub b (proj a b)` of `Projection3D`. Its live uses are `rejectSP_eq_vecReject`, a
  stepping stone. Medium confidence.
- `Projection3D.proj_plane`, `proj_plane_perp_normal_dot`, `proj_plane_eq_project_onto`, and with
  them `reject_eq_proj_normal_coord`, `project_eq_sub_reject_coord` and
  `StudentTrigForms.proj_plane_perp_normal`. Nothing reader-facing cites any of them. The fact
  itself is worth keeping, in object form: `project_onto B c = sub c (proj (dual B) c)` for
  `IsBivector B`, two rewrites from `project_eq_sub_reject` and `reject_eq_proj_normal`.

**Leaves used by others (not dead):** `Projection3D.add_eq_left_sub`, `project_add_reject_coord`;
`ReciprocalFrame2D.sumSq_ne_zero_of_area`, `area_ne_zero_vec`, the `_vec` leaves;
`ReciprocalFrame3D.det3`, `crossSq`, `comb`, `frame_nonzero`, `comb_basis_dot`, `dot_comb_basis`,
the `_vec` leaves; `ProjectionRotation2D.reject_plane_eq_zero`, `normSq_mul_three_vec`,
`key_reverse_sq`; `StandardPosition.xyMagnitude_sq`, `cs_xy_unit`, `cs_xz_unit`,
`rotXY_aligns_xy_SP`, `magnitude_sq_of_isVector`.

**The "mentioned nowhere else" theorems of this slice, one by one.**

| Theorem | Verdict |
|---|---|
| `Projection3D.proj_plane_eq_project_onto` | (c) in content: it is `proj_B(v) = rej_n(v)` of `reflection-3d.rst` and its notebook. Restate in object form (above) and cite it there |
| `Reflect.normSq_reflectVec` | (c): `reflection.rst` and both reflection notebooks state "a reflection keeps every length"; `base.reflect`'s docstring has the example. Cite it. Also cited by the coverage map |
| `StandardPosition2D.vecReject_rotPlane_equivariant` | (b) as it stands; becomes (a) if the rejection-by-rotation theorem is added |
| `CrossStandardPosition.rotYZ_fixes_e1` | (c): use and cite in `proof-cross` |
| `CrossStandardPosition.vecReject_rotXZ_equivariant`, `vecReject_rotYZ_equivariant`, `vecReject_reduced` | (b): unfinished half, no capstone |
| `ProjectionRotation2D.reverse_versorFromVectors_mul` | (b): duplicate of `reverse_mul_self_of_isEvenVersor` |
| `ProjectionRotation3D.projRotation_perp` | (a) in intent (Python docstring: "leave the perpendicular part fixed"), but restate: for a vector `v` with `dot v f = 0` and `dot v t = 0`, `projRotation f t v = v`. Then cite it from `transforms.projection_rotation` |
| `ProjectionRotation3D.wedge_vec_wedge_self`, `reject_in_plane_self`, `inner_vb_mul_reverse_self`, `project_onto_in_plane_self`, `normalizeVec_to_mul_versor_eq_bisector`, `vec_mul_bisector_eq`, `normalizeVec_mul_versor_eq_reverse`, `versor_mul_project_eq`, `versor_mul_reject_comm` | (b) today: dead wrappers. `project_onto_in_plane_self` ("a vector of the plane is its own projection") and `versor_mul_project_eq`/`versor_mul_reject_comm` are results worth stating once they are the proofs' own form |

`ProjectionRotation3D.lean` as a whole is cited by no book page, notebook or Python docstring; the
book cites `ProjectionRotation2D.lean` only. It backs `transforms.projection_rotation` in 3D, whose
docstring says "both agree" without naming `projRotation_eq_sandwich`.

### 3. Duplicates

- `StandardPosition.mul_eq_proj_dot_add_reject_wedge` states `a * b = (b·a) + a∧b`. That is
  `G3.mul_eq_dot_add_wedge` with an extra hypothesis (`normSq a ≠ 0`), the dot's arguments swapped
  and `smul … one` for `scalar`. Projection and rejection appear only in its name and proof. The
  2D counterpart states the real split: `Bootstrap2D.mul_eq_mul_proj_add_mul_reject :
  a * b = a * proj_a b + a * rej_a b`, which is also what `projection-rejection-3d.py` checks.
- `Projection3D.plane_eq_wedge` (`a * (b − proj_a b) = a ∧ b`) is the 3D twin of
  `Bootstrap2D.mul_reject_eq_wedge` (`a * reject a b = a ∧ b`) under another name and without
  `reject`.
- `project_add_reject_coord` / `project_add_reject`; `reject_eq_proj_normal_coord` /
  `reject_eq_proj_normal`: each pair proves the same statement twice with the same tactic script.
- `wedge_vec_wedge_self_coord` / `wedge_vec_wedge_self`: two independent proofs of one fact.
- `ProjectionRotation2D.reverse_versorFromVectors_mul` vs `Sandwich.reverse_mul_self_of_isEvenVersor`.
- `Projection2D.reject_from_I_eq_zero` vs `ProjectionRotation2D.reject_plane_eq_zero`: the second
  is the general form (any plane `f ∧ t`); neither is derived from the other, and the first has no
  consumer.
- `ReciprocalFrame2D.dot_reject_self` and the first conjunct of
  `ReciprocalFrame3D.reject_line_facts` vs `reject_perp_dot` + `reject_vec_eq`.
- `ReciprocalFrame3D.reject_line_vec` is `reject_vec_eq` written in coordinates.
- `magnitude_sq_of_isVector` (2D and 3D) is `magnitude_sq_eq_normSq` + `normSq_eq_sum_sq` + the
  grade zeros.
- `proj_onto_x_axis` (3D) and `CrossStandardPosition.proj_reduced`: the second is the first with
  `v = vec b1 b2 0`.
- `ProjectionRotation3D` re-derives `magnitude² = normSq` and `magnitude ≠ 0` inline four times
  (`hmf`, `hmt`, `hmf2`, `hmt2`, `hsq`); `G3.magnitude_sq_eq_normSq` and
  `magnitude_ne_zero_of_normSq_ne_zero` exist.
- Prior, still present: `normSq_wedge_vec'`, `normSq_wedge_vec3`/`crossSq`/`det3`.

### 4. Missing

**Stated by a book page or notebook in this slice, with no Lean theorem.**

1. **Reflection as a sandwich**: `ref_b(a) = b * a * b⁻¹` (`reflection.rst` `eq-reflect-sandwich`,
   `reflection-3d.rst`, both notebooks). `git grep reflect -- proofs` finds only `Reflect.lean`
   and two unrelated prose mentions.
2. **Reflection in 𝒢₂ at all.** `Reflect.lean` is 𝒢₃ only; `reflection.rst` cites no theorem and
   `reflection.py` has no `twin:` tag. Missing in 2D: the definition, `proj − rej`, the
   rotate / flip / rotate-back construction (`eq-reflect-e1`, `eq-reflect-vector`), length kept.
3. **A reflection is an involution** (reflect twice = identity): `reflection.rst`, both notebooks,
   `base.reflect`'s docstring. No theorem in either dimension.
4. **The plane mirror keeps length**, and `B * v * B⁻¹ = n * v * n⁻¹` (`reflection-3d.rst` and its
   notebook). The first is a corollary of `reflectPlane_eq_neg_reflectVec_dual` +
   `normSq_reflectVec`; not stated.
5. **Rejection by rotation** (§1.1): `rej_a = (R)⁻¹ ∘ rej_{e₁} ∘ R`, in 2D and 3D.
6. **Step 2's formulas**: `eq-bootstrap-rejection`
   (`rej_a(b) = ((a₁*b₂ − a₂*b₁)/|a|²) * r(a; π/2)`), "projecting twice changes nothing" (no
   idempotence theorem for `proj`), and "the two parts add back to `b`" in 2D (only through
   `reject_vec_eq`; no 2D `project_add_reject`).
7. **`a * a⁻¹ = 1` for a 𝒢₂ vector** (`bootstrap-projection-from-product.rst`, "The inverse of a
   vector"; its notebook checks it). `G1` and `G3` have `mul_vec_inverse_self`; `G2` has it only as
   an inline `have hinv` inside `reject_vec_eq_coord`.
8. **The rejection from a plane is perpendicular to both spanning vectors**
   (`projection-rejection-3d.rst` and notebook) under the plane hypothesis alone.
   `ReciprocalFrame3D.reject_plane_facts` has it only with a third vector and a nonzero volume.
9. **3D: `proj a b = (b·a) * a⁻¹`** (§1.1), and **3D `mul_reject_eq_wedge`** with `reject` (§3).
10. **𝒢₂: `dot (reject a1 a2) a2 = normSq (reject a1 a2)`**, used by the prose proof of theorem 6
    in `proof-reciprocal-frame.rst`; 3D has it.
11. **`w₃` by iterated rejection equals `w₃` by rejection from the plane** (§1.1).
12. **`transforms.coordinate_along`, `line_to_line_projection`, `line_to_line_rejection`,
    `line_to_plane_projection`, `line_from_plane_rejection`**: no theorem, and no row in the
    coverage map. `coord*_of_perp` is the nearest fact.
13. Helper: `G3.isBivector_wedge_of_isVector` (§1.6).

**Citations that exist but do not say what the citing page claims.**

- `notebooks/proof-projection.py` is the 2D construction (`g2`, `rotation_from_to(b, e_1)`). It
  cites "`projectSP_eq_proj` in `proofs/GacalcProofs/StandardPosition.lean`" and carries
  `twin: GacalcProofs.G3.projectSP_eq_proj`. Its theorem is `GacalcProofs.G2.projectSP_eq_proj` in
  `StandardPosition2D.lean`, which `proof-projection.rst` cites correctly.
  `tasks/reference/lean-python-notebook-workflow.md` repeats the mismatch in its worked-example
  table. `notebooks/proof-projection-3d.py`, the real 3D twin, has no `twin:` tag.
- `book/docs/proof-projection-3d.rst`: "you can run it with `gacalc.standardposition.project_sp`;
  the last section of the companion notebook of `proof-projection` does so symbolically". No
  notebook calls `project_sp` or `reject_sp` (`git grep` over `notebooks/` is empty).
- `tasks/reference/reduction-to-standard-position.md` cites `rejectSP` for the rotate/keep-y
  definition (§1.1).
- `projection-rejection-3d.rst` attributes "`a * rej_a(b)` is the wedge" to `mul_proj_eq_dot` and
  `mul_eq_proj_dot_add_reject_wedge`; the theorem that says it is `plane_eq_wedge`, uncited.
- All other cited names in this slice exist in the file named, including `mul_reject_eq_wedge` and
  `proj_eq_dot_mul_inverse` (`Bootstrap2D`), `isVector_recip` (3D) / `isVector_recip1`,
  `isVector_recip2` (2D).

**`twin:` tags with one side missing** (the workflow doc's own orphan test: a tag that appears
once). Notebook tag present, no `-- twin:` line in Lean: `G3.mul_proj_eq_dot`,
`G3.mul_eq_proj_dot_add_reject_wedge`, `G3.project_add_reject`, `G3.reflectVec_eq`,
`G3.reflectPlane_eq_neg_reflectVec_dual`, `G3.dual_wedge_perp_left_dot`,
`G3.dual_wedge_perp_right_dot`. Cited in prose with no tag at all: `reject_eq_proj_normal`
(`projection-rejection-3d.py`), the cross theorems (`proof-cross.py`),
`mul_eq_magnitude_smul_alignSP` (the headline of `product-from-projection`, whose notebook's only
tag is `wedge_sides_eq_surveyor`), every reciprocal-frame theorem (`proof-reciprocal-frame.py`,
`tests/test_frame.py`, `tests/test_frame_class.py`).

**`proofs/README.md` against the 37 files.**

- Says "34 modules"; there are 37, all imported by `proofs/GacalcProofs.lean`.
- Not mentioned at all: `Bootstrap2D.lean`, `GeneralInverse.lean`, `RotateFromTo2D.lean`,
  `StandardPosition2D.lean`.
- "What's planned: … the general multivector inverse": done (`GeneralInverse.lean`).
- "`Projection2D.lean` / `Projection3D.lean` (Hestenes `proj`/`reject`/`project_onto` …)": there is
  no 2D `project_onto`.
- "`Reflect.lean` (… 𝒢₃, across a vector)": omits `reflectPlane` and
  `reflectPlane_eq_neg_reflectVec_dual`.

**`tasks/reference/lean-ga-proof-architecture.md`.**

- Status line: "34 as of 2026-11-09"; now 37.
- Inventory has no entry for `GeometryObjects2D.lean` or `Rotor.lean` (Rotor is described in a
  prose section, not in the inventory).
- Inventory, `Reflect.lean`: "(across a vector only)"; stale.
- Inventory tail, "Remaining: … the general multivector inverse": landed.
- "Hestenes projection / rejection": "`proj`/`reject`/`project_onto` cover vector- and
  bivector-blades in 3D … and 2D": no 2D `project_onto`.
- Leaf index, "G2's split lives in `Projection2D.lean`": contradicted by the same doc's "relocated
  into `G2.lean`, 2026-10-28" paragraph, and by the source.
- "Scalars into the algebra": "G2 has no `zero`" (it has), and "all grade-0 embeddings … now read
  `scalar (…)`" (not `StandardPosition.mul_proj_eq_dot`/`mul_eq_proj_dot_add_reject_wedge`).
- Coverage map row "`standardposition.rotate_in_xy_plane` / `_xz_plane`": those functions no longer
  exist; the module has `rotation_from_to` and `in_plane`.
- Coverage map row `reflect`: lists `reflectVec` only.
- Coverage map row `Frame.to_invertible_function` HAS: see §1.1 on the peel.
- No rows for the five `transforms` functions of item 12.

### 5. Overall judgment

The slice is sound where it matters most: the definitions the book and Python lean on
(`projectSP`, `reflectVec`, `recip*`, `frameMap`) transcribe the Python faithfully, every cited
theorem exists, and the public statements are almost all objects-in. `StandardPosition`,
`StandardPosition2D`, `Reflect`, `ProjectionRotation2D` and `ReciprocalFrame3D` are in good shape.
The weak file is `ProjectionRotation3D.lean`: 16 single-consumer `_coord` leaves, 13 unused object
wrappers, three 8M-heartbeat brute proofs that the corpus's own techniques would shrink, redundant
hypotheses, and no reader-facing citation. `CrossStandardPosition` carries a half-built
projection/rejection track with nine unused lemmas and a capstone stated over seven reals. The
book has outrun Lean on reflection (the sandwich form, the involution, all of 2D) and on the
rejection-by-rotation definition, and the 2D and 3D twins have drifted apart in naming and form
(`mul_proj_eq_dot`, `plane_eq_wedge` vs `mul_reject_eq_wedge`, where `reject_vec_eq` lives).

The changes most worth making:

1. Rewrite `ProjectionRotation3D` in the 2D file's object style: delete the 16 leaves and the
   wrapper block, state the plane facts over `IsBivector B`, add `G3.isBivector_wedge_of_isVector`,
   and decide whether the isometry keeps its independent proof.
2. Add the missing reflection theorems (`reflectVec d v = d * v * d⁻¹`, involution, a 𝒢₂ section)
   and cite `normSq_reflectVec` from the reflection pages.
3. Make the 3D product-from-projection theorems match their 2D twins: `scalar`, `reject`, the real
   split statement; drop `mul_eq_proj_dot_add_reject_wedge` as a restatement of
   `mul_eq_dot_add_wedge`.
4. Finish or delete the projection/rejection half of `CrossStandardPosition`, and restate the
   cross capstone over vector objects through `alignSP`.
5. Fix the citations and counts: the `proof-projection.py` twin tag, the `project_sp` claim in
   `proof-projection-3d.rst`, `rejectSP` in the reference doc's table, the README's 34 and its four
   missing files, the coverage map's stale rows.

