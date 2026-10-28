# Lean: make dot/wedge/measures faithful to Python's grade-projection definitions (the `.s`/`.c12`/`.c123` reads)

**Status:** investigated; catalog below. Part A is **decided** (2026-10-28: add a `scalar` constructor +
`IsScalar` predicate, replace the `smul … one` embedding — ready to implement). Part B still needs a
design decision (Open question 1). Two related threads: (A) the `smul … one` scalar-embedding asymmetry
[root cause: a type necessity; resolution: a `scalar` constructor], (B) coordinate-field grade reads
(`.s`, G2 `.c12`, G3 `.c123`) where the existing `rVectorPart` grade projection — the way the **Python**
code defines these — could be used.
**Priority:** 7
**Difficulty:** 4
**Created:** 2026-10-28 (William Emerison Six <billsix@gmail.com>)
**Updated:** 2026-10-28 (William Emerison Six <billsix@gmail.com>)

## BLUF

In the Python library, dot/wedge/scalar-product are defined as **grade projections of the geometric
product** — `inner_product = (a*b).r_vector_part(|r−s|)`, `outer_product = (a*b).r_vector_part(r+s)`,
`scalar_product = ⟨a*b⟩₀`. The grade (rank) *is the definition*. In the Lean proofs we mostly bypass
that: `dot := (mul a b).s`, `normSq := (mul a (reverse a)).s`, `signedArea := (mul … ).c12`,
`signedVolume := (wedge … ).c123`, and `wedge` is a standalone coordinate formula — each reaching into a
raw coordinate field instead of the grade-projection operator **`rVectorPart`, which already exists**
(`GradeProjection.lean`) and is already used by `Contractions.lean`. The maintainer flagged this as the
proofs "doing weird stuff" / leaking coordinates where a rank/grade would read cleaner and match Python.

This task **catalogs every such site** and poses the one design decision (Open question 1) that gates
any change. It is an investigation record, not yet an edit. The honest finding: only **1-dimensional
grades** (grade 0 everywhere; the **top** grade — G2 grade 2 = `e₁₂`, G3 grade 3 = `e₁₂₃`) are a single
coordinate, so only those reads are cleanly a whole-grade projection; a G3 `.c12` (grade 2 is
3-dimensional there) is *not* a whole-grade read and is out of scope. And `dot`/`normSq` genuinely
*return `ℝ`* (house rule "genuine scalars stay scalar", and Python's `scalar_product -> Real` agrees), so
the win is mostly *definitional faithfulness + connecting lemmas*, not necessarily changing the `: ℝ`
signatures.

## Context (cold-start)

Read first: `src/gacalc/base.py` (`inner_product`/`outer_product`/`scalar_product`/`wedge`, lines ~810–935)
for the Python grade-projection definitions; `proofs/GacalcProofs/GradeProjection.lean` (the Lean
`rVectorPart`); `proofs/GacalcProofs/Contractions.lean` (the one place that *does* define a product via
`rVectorPart`); and the house rule "Coordinates only when needed" / "objects in, scalars in the body,
objects out" in `CLAUDE.md` + `tasks/reference/lean-ga-proof-architecture.md`.

The Lean grade-projection operator that already exists (`GradeProjection.lean`):

- `rVectorPart (r : ℕ) (a : G2) : G2` (G2 lines 18–; G3 lines 51–) — the grade-`r` part, as a
  multivector. Plus `evenPart`/`oddPart` and the proved `rVectorPart_idem`, `rVectorPart_complete`
  (Σ grades = identity), `evenPart_add_oddPart`.
- **Already used** by `Contractions.lean`: `leftContraction k m a b := rVectorPart (m−k) (mul a b)`,
  `rightContraction k m a b := rVectorPart (k−m) (mul a b)` — i.e. the contractions ARE defined the
  Python way (grade projection of the product). dot/wedge/normSq/measures are the inconsistent holdouts.

## Part A — the `smul (dot a b) one` vs bare `wedge a b` asymmetry (ANSWERED: type necessity)

The maintainer first asked why the dot side of the decomposition is `smul (dot a b) one` (a scalar times
the identity — the "`1 *`") while the wedge side is bare `wedge a b`, and whether the `smul … one` can be
removed. **It cannot** — the types force it:

- `dot (a b : G2) : ℝ` returns a **scalar** (`G2.lean:99`); `wedge (a b : G2) : G2` returns a
  **multivector** (`G2.lean:91`); `smul : ℝ → G2 → G2` (`G2.lean:111`); `one : G2` (`G2.lean:61`).
- A theorem whose LHS is a `G2` needs a `G2` RHS. `= dot a b` is ill-typed (`ℝ ≠ G2`); `= smul (dot a b)`
  is ill-typed (partial application, not a `G2`); `= smul (dot a b) one` is the well-typed embedding
  `(dot a b) • 1` of the scalar into the algebra. The wedge needs no wrapper because it is already a `G2`.

### Decision (William Emerison Six <billsix@gmail.com>, 2026-10-28)

Given the ill-typing is real, the maintainer prefers a **`scalar` constructor + `IsScalar` predicate**
(the pairing `vec`/`IsVector` already has) over the `smul … one` "multiply `one` to change the type"
idiom. So the embedding `ℝ ↪ Gₙ` is spelled `scalar r`, with `IsScalar` to test membership.

What this entails:

- **G3 — nothing to add**: already has `scalar (a : ℝ) : G3 := { zero with s := a }` (`G3.lean:66`) and
  `IsScalar`/`isScalar_scalar`/`eq_scalar_of_isScalar`.
- **G2 — add the constructor** (G2 already has `IsScalar`, `G2.lean:203`, but no `scalar`): define
  `def scalar (a : ℝ) : G2 := { s := a, c1 := 0, c2 := 0, c12 := 0 }` (named fields — G2 has no `zero`,
  so mirror how `G2.vec` is written, `G2.lean:75`), and add `isScalar_scalar`/`eq_scalar_of_isScalar`
  for G2 to complete the pair exactly as G3 has them. (This supersedes the `smul a.s one` spelling in
  `eq_smul_one_of_isScalar`, `G2.lean:207` — keep or rename to `eq_scalar_of_isScalar`; match G3.)
- **Replace `smul (<scalar>) one` → `scalar (<scalar>)`** at every grade-0 embedding site (grep
  `smul (dot …) one` / `smul (normSq …) one`): `G2.lean:274,336`; `G3.lean:318,419,451,466`;
  `Projection3D.lean:108`; `ProjectionRotation2D.lean:36`; `StandardPosition2D.lean:195`. `G1.lean:118`
  only if G1 is in scope (G1 has no `scalar` constructor — see Open question 2 on dims scope).
- Proofs: each changed site's `simp only [… , smul, one]` set swaps to `[… , scalar]` (or unfolds
  `scalar` to the same `⟨r,0,…⟩`); re-verify with `make lean`.

This is bounded and ready to implement on go-ahead. It also settles the "how is the scalar grade spelled"
sub-question that Part B option (b) would otherwise raise.

## Part B — coordinate-field grade reads where `rVectorPart` is the principled form

Grouped by whether `rVectorPart` could cleanly apply. **"Candidate"** = a 1-dimensional grade read via a
raw coordinate field; **"Exempt"** = either not a whole-grade read, or a bridge whose job is coordinates.

### B1. Grade-0 reads via `.s` (candidates — grade 0 is 1-dimensional everywhere)

Mirror Python `scalar_product = ⟨a*b⟩₀` / `r_vector_part(0)`:

- `dot := (mul a b).s` — `G1.lean:70`, `G2.lean:99`, `G3.lean:164`.
- `normSq := (mul a (reverse a)).s` — `G1.lean:62`, `G2.lean:123`, `G3.lean:139`.
- Statement-level `.s` reads of a product: `Sandwich.lean:64` & `:314` (`dot (mul R X) (reverse R) =
  normSq R * X.s`), `ProjectionRotation3D.lean:125` & `:130` (`(mul x (reverse y)).s`),
  `Rotation2D.lean:149` (`uvec_dot`: `(G2.mul (uvec α) (uvec β)).s = cos(β−α)`). `Predicates3D.lean:18,27`
  are doc-comment mentions only.
  - Caveat on `X.s` in `Sandwich` `normSq R * X.s`: here `X.s` is just the scalar coordinate of an
    argument `X`, not a grade projection of a *product* — lower priority; include only if the decision
    says to route all grade-0 reads through a `scalarPart`/`rVectorPart 0` abbreviation.

### B2. Top-grade (pseudoscalar) reads — G2 `.c12` (grade 2), G3 `.c123` (grade 3) (candidates)

Each is a 1-dimensional top grade, so a single coordinate = the whole grade; mirror Python
`r_vector_part(top)`:

- `Measures.signedArea := (mul (vec a1 a2) (vec b1 b2)).c12` — `Measures.lean:66` (the 2D pseudoscalar
  coefficient of the product).
- `Cross.signedVolume := (wedge (wedge a b) c).c123` — `Cross.lean:69`.
- `MathlibBridge.lean:65` & `:106` — `(wedge a b).c12 = Matrix.det !![…]`.
- `Rotation2D.lean:154` (`uvec_wedge`: `(G2.mul (uvec α) (uvec β)).c12 = sin(β−α)`).
- `TrigEquiv.lean:42` (`sine := (G2.wedge a b).c12 / (…)`), `:60`, `:62`, and the doc at `:13,:15` — the
  signed 2D sine, Python `g2.Vector.sine = (a∧b).c12 / (|a|*|b|)`. NOTE: the Python `sine` itself reads a
  **coefficient** (`.coefficient(e_12)`), so a coordinate read here may be inherent on both sides; decide
  whether `rVectorPart` buys anything.

### B3. `wedge` defined by a standalone coordinate formula, not as a grade projection (candidate — faithfulness)

Python `outer_product = (a*b).r_vector_part(r+s)`. Lean `wedge (a b : G2/G3) : G2/G3` is a direct
`where`-formula (`G2.lean:91`, `G3.lean:~95`), provably equal but **not derived** from the product. There
is currently **no** lemma `wedge a b = rVectorPart (r+s) (mul a b)` for homogeneous inputs. Adding that
bridging lemma (rather than redefining `wedge`) is likely the cleanest way to record the grade-projection
view without disturbing the many `simp only [wedge]` proofs.

### B4. Exempt — do NOT flag these (recorded so a re-investigation doesn't re-raise them)

- **Operation definitions** building each field: `mul`/`wedge`/`add`/`sub`/`neg`/`smul`/`reverse`
  (`G2.lean:84–116`, G3 equivs) — defining the op, not projecting a grade.
- **Grade predicates** enumerating zero coords: `IsVector`/`IsScalar`/`IsBivector`/`IsTrivector`
  (`G1.lean:102`, `G2.lean:187,216`, `G3.lean:384,…`) — the predicate's nature.
- **`eq_…_of_is…` object-reconstruction bridges** (explicitly exempt by house rule): `eq_bivector_of_isBivector`
  (`G3.lean:388`, `= bivector B.c12 B.c13 B.c23`), `eq_trivector_of_isTrivector` (`G3.lean:404`),
  `eq_smul_e12_of_isBivector` (`G2.lean:220`), `eq_evenVersor_of_isEvenVersor` (`Sandwich.lean:32,258`),
  `eq_smul_basis` (`G2.lean:152`).
- **G3 grade-2 single coords** (`.c12`/`.c13`/`.c23` individually): grade 2 is 3-dimensional in G3, so
  one coord is NOT a whole-grade read — `rVectorPart` cannot replace them. Covers `Projection3D.lean:166,
  200,204` (`normSq B = B.c12² + B.c13² + B.c23²` — sum over the grade, inherent), `PlaneRotation3D.lean:146`
  (`vec i.c23 (-i.c13) i.c12`, the dual/normal construction), and the `Sandwich` `R.c12 R.c13 R.c23`
  bivector/normal reconstructions (`:638,:658,:720`).
- **`normSq_eq_sum_sq`** (`G2.lean:130`, `G3.lean:146`) — sum over all coordinates, inherent.

## Open questions

1. **Decide the policy: define/relate dot, wedge, normSq and the signed measures via `rVectorPart`
   (match Python), or keep the coordinate-field reads and only add bridging lemmas?** The options, named:
   - **(a) Bridging lemmas only (recommended).** Leave every definition as-is (they are correct, fast to
     `simp`, and `dot`/`normSq` rightly return `ℝ`), but add a small set of lemmas tying them to the
     grade projection — `dot a b = (rVectorPart 0 (mul a b)).s`, `wedge a b = rVectorPart (r+s) (mul a b)`
     (homogeneous), `signedArea … = (rVectorPart 2 …).c12`, `signedVolume … = (rVectorPart 3 …).c123`.
     Records the "grade IS the definition" view, mirrors Python, disturbs no existing proof. Lowest risk.
   - **(b) Redefine the products as grade projections** (`dot a b := (rVectorPart 0 (mul a b)).s`, etc.,
     and `wedge` via `rVectorPart`), making Lean structurally match Python. Bigger blast radius: every
     `simp only [dot]` / `simp only [wedge]` proof in the corpus would need its unfold set updated and
     re-verified (`make lean`). Higher fidelity, higher churn.
   - **(c) Leave entirely as-is** — treat the coordinate reads as the natural concrete form in the
     specialized algebras and close this task. (The `Contractions.lean` precedent argues against (c): we
     already use `rVectorPart` for contractions, so dot/wedge are the inconsistent ones.)

   **Recommendation: (a).** It captures the maintainer's point (faithfulness to the rank-based Python
   definitions) at near-zero risk, and can be upgraded to (b) later if desired. Also fold Part A's
   cosmetic `scalar`-constructor question in here: if (b), spell the grade-0 result with a uniform
   `scalar`/`smul _ one` embedding across G2/G3 at the same time.

2. **Scope — all three dims, or G2/G3 only?** `rVectorPart` is defined for G2 and G3, not G1
   (`GradeProjection.lean` has no G1 instance). G1's `dot`/`normSq` use `.s` too. Add a G1 `rVectorPart`
   for uniformity, or leave G1 as coordinate-only (it is the trivial algebra)? **Recommendation: G2/G3
   only** unless (b) is chosen and G1 parity is wanted.

See also: [[lean-g2-object-out-parity]] (lifted the dot/wedge *conclusions* to object form — this task is
the sibling about their *definitions*), `proofs/GacalcProofs/GradeProjection.lean`,
`proofs/GacalcProofs/Contractions.lean`, `tasks/reference/lean-ga-proof-architecture.md`.
