# Per-type fixed-grade dot/wedge (via r_vector_part) and per-type sine/cosine — each proved equivalent to the general form

**Status:** in-progress — Phases 1 & 2 DONE (general unsigned **`abs_sin`**; signed 𝒢₂ **`sine`**,
Decision 8); `make format` (ruff + ty) and `make test` both green 2026-10-01; Phases 3–5 awaiting
go-ahead
**Priority:** 6
**Difficulty:** 7
**Created:** 2026-09-30 **Updated:** 2026-10-01 (William Emerison Six <billsix@gmail.com>)

## BLUF

Add **special-case, per-type** presentations of the core operations — `dot` and `wedge` written the
Hestenes way but with the grade **bound to a literal constant** per grade-pure type pair (via the
existing grade-projection `r_vector_part`), and a `sine` companion to the existing `cosine` for
vectors — as **teaching artifacts that live alongside** the canonical coordinate-free ones, with a
**proof of equivalence** (symbolic test in Python, theorem in Lean) for each. This makes concrete the
project principle that special-case formulas at every level of abstraction — full-coordinate →
coordinate-free/dimension-independent — are *desirable* for students, provided a check pins each to
the general form; **the coordinate-free form stays the default/canonical one.** "Done" = (on
go-ahead) the deliverables + equivalence checks land green (`make test` + `make lean`). The design
questions are now decided (see Decisions); this is **not** yet authorization to implement.

## The idea (maintainer, verbatim, 2026-09-30)

> For each type, make grade operation to get that grade. For each type, define wedge and dot, like
> how hestenes defines it, but call the grade, and bind the grade. Meaning that the grade calls will
> have fixed values. Also, Dedicated, per type definitions for sine and cosine. Make proofs that they
> are equivalent to the general formulas. One thing I want to make clear, is that, for the purposes of
> teaching, I'm perfectly happy with making special case formulas, including using coordinates
> entirely, all the way to coordinate free, indepedent of dimension, versions of the same thing. In
> fact, that's probably desirable. But for that, I would want checks to ensure that they are in fact
> the same, and I've already stated what my preference is for the default - coordinate free. But like
> the sine and cosign ones - clearly, for vectors, we can make special case implementations, same
> thing for dot product and cross product. These are probably helpful for students, but also, put in
> references to the more general cases, and prove that they are equivalent.

## Context — read first (current ground truth, verified 2026-09-30 by file read)

There are already (up to) **three levels** of the same operation in the codebase; this task adds a
missing middle rung and a missing operation, and formalises the "prove they're equal" discipline.

**Dot / wedge — two levels exist, one is missing:**
- **General Hestenes (coordinate-free, any n)** — `MultiVectorBase.inner_product` (`base.py:735`)
  computes `A·B = Σ_{r,s} ⟨AᵣBₛ⟩_|r−s|` and `outer_product` (`base.py:787`) `Σ_{r,s} ⟨AᵣBₛ⟩_{r+s}`,
  with the grade computed **dynamically** as `abs(lg-rg)` / `lg+rg` and selected by `r_vector_part`
  (`base.py:985`). `dot`/`wedge` are aliases (`base.py:772`/`840`). This is the canonical/default.
- **Per-type closed form (full-coordinate)** — the generator emits each grade-pure type's
  `inner_product`/`outer_product`/`dot`/`wedge` as explicit coefficient arithmetic (e.g. g3
  `Vector.inner_product` → `Scalar(coeff = e1·e1+e2·e2+e3·e3)`, `g3.py:2621`), `@typing.overload`-typed
  per rhs, and proved equal to `Gn` by the conformance suite. **This is the "coordinate" rung, and it
  already exists and is verified** — do NOT rebuild it (see "Already done").
- **MISSING (the new middle rung):** the per-type **fixed-grade Hestenes** form — for a grade-`r` ×
  grade-`s` type pair, `dot = (a*b).r_vector_part(|r−s|)` and `wedge = (a*b).r_vector_part(r+s)` with
  the grade written as a **literal constant** (vector·vector: `.r_vector_part(0)` / `.r_vector_part(2)`),
  not the general `abs(r-s)` sum. This is the pedagogical bridge "for two vectors, dot IS the grade-0
  part of the product and wedge IS the grade-2 part."

**Grade operation — already exists (clarified by the maintainer 2026-09-30):**
- "A per-type grade operation" means an `r_vector_part`-style projection that **returns just the
  components of a given grade** — NOT an integer grade-*number* accessor (that was the agent's misread
  in the first draft). That projection already exists: `MultiVectorBase.r_vector_part(r)`
  (`base.py:985`), with per-type generated overrides carrying `@overload` on `Literal[r]`
  (`archive/2026/07/22/overload-r-vector-part.md`). It works on any type — a zero-grade request on a
  grade-pure type returns the `Scalar` zero.
- So **no new grade operation is needed.** What is new is *using* `r_vector_part` with a **bound
  literal grade** inside the per-type `dot`/`wedge` presentation (below) — the "call the grade, bind
  the grade" step. This applies to **grade-pure pairs** (for grade-`r` × grade-`s`: dot picks
  `|r−s|`, wedge picks `r+s`); mixed-grade types (`Versor` {0,2}, `Odd_3` {1,3},
  `archive/2026/09/05/model-odd-graded-type.md`) keep the general grade-summed form, and `r_vector_part`
  already handles them correctly anyway.

**Sine / cosine — original state (before Phase 1): cosine existed, no sine method:**
- `MultiVectorBase.cosine(other)` exists (`base.py:1303`, Hestenes 1.53b, `cos θ = (Ã ∗ B)/(|A||B|)`),
  general multivectors.
- There was **no sine method** in the library core — only a notebook-plot free function `sine(v1, v2)`
  (`nbplotutils.py:309`, vectors only, signed: `v1 * e_12` then dot). So an unsigned `abs_sin` companion
  to `cosine`, and per-type vector trig, were the gap (abs_sin filled in Phase 1).
- **DONE (Phase 1, 2026-10-01):** a general unsigned `MultiVectorBase.abs_sin(other)` now exists
  (`base.py`, right after `cosine`), `|A ∧ B| / (|A| |B|)`, same primitives as `cosine` so it
  preserves numeric input (float→float on the generated classes, int/symbolic exact); tests
  `test_multivector_abs_sin` + `test_abs_sin_cosine_pythagorean` (cos²+abs_sin²==1, numeric and
  symbolic). It is inherited by the generated classes via MRO — `cosine`/`abs_sin` are NOT
  generator-specialized, so no generator change and `check-generated` stays byte-identical. (Named
  `abs_sin`, not `sine`, per Decision 7 — `sine` is reserved for the signed 𝒢₂ form.)

**Prior art in modelviewprojection (reference/validation, 2026-10-01) — github.com/billsix/modelviewprojection:**
`src/modelviewprojection/mathutils.py` already carries the whole sin/cos family that depends on gacalc,
and confirms the design space (gacalc is the lower layer, so these would be *adapted down*, not imported):
- `cosine(v1, v2)` — any dimension; **NaN-guarded on a zero-length operand** (gacalc's
  `cosine`/`abs_sin`/`sine` do NOT guard — they divide and raise, by Decision 6).
- `sine(v1, v2)` — **signed, 𝒢₂ only**: `(v1 ^ v2).coeff_e_12 / (|v1| |v2|)`; the sign is the *turn
  direction* (swapping arguments negates it), used for "which side of an edge a point lies on." This is
  the maintainer's remembered 2D signed sine.
- `abs_sin(v1, v2)` — **unsigned, 𝒢₃**: `|v1 ^ v2| / (|v1| |v2|)` — i.e. exactly gacalc's new general
  `abs_sin` restricted to 3D vectors.
So the **signed 𝒢₂ sine is a genuinely-wanted special case** (Phase 2), analogous to the existing
𝒢₂-only `rotate_90_degrees` and 𝒢₃-only `Vector.cross` closed forms. **Naming (Decision 7): gacalc
adopts mvp's names exactly** — `sine` = signed (𝒢₂), `abs_sin` = unsigned (any-dim) — so the two
libraries agree (Phase 1's general method was renamed `sine`→`abs_sin` on 2026-10-01).

**Lean state (proofs/GacalcProofs, `make lean` green 2026-09-30):**
- dot/wedge as parts of the product are proved **per-dimension**: `G2.dot_is_sym_part`/`wedge_is_antisym_part`
  (`G2.lean:164`/`170`), `G3.mul_eq_dot_add_wedge` (`G3.lean:237`, arbitrary-vector) and the G2 twin
  (`Projection2D.lean:65`). `dot_eq_coord_sum` (`G2.lean:177`) is the archetype special↔general bridge.
- sin/cos exist in **two** characterizations with **no equivalence between them yet**: property form
  `Trig.cos_between`/`sin_between` (`Trig.lean:22`/`25` G3, `:88`/`:91` G2) via Lagrange; and
  angle-parametrized `Rotation.uvec_dot` (dot of unit vectors = `cos(β−α)`, `Rotation.lean:86`) /
  `uvec_wedge` (= `sin(β−α)`, `Rotation.lean:91`). Tying these is new and is exactly the gap.
  **Note `uvec_wedge` (`Rotation.lean:91`) is already the SIGNED 𝒢₂ sine** (`sin(β−α)`, from the e₁₂
  coefficient) — so it is the ready-made Lean target for the signed-2D Python `sine` (mvp's `sine`),
  and `sin_between` (`Trig.lean:91`) is the unsigned one; the 2D equivalence is `|signed| = unsigned`.
- **No abstract grade operator `⟨⟩_k` in Lean, by an explicit decision** — the coordinate-free pass
  (`archive/2026/09/30/lean-proofs-make-coordinate-free.md`, open-Q2 RESOLVED "no") kept per-grade-pair
  forms. This **agrees** with "bind the grade per type," and constrains the Lean side to stay per-type.

**The governing theme:** this is the **"reduction to standard position / duplicate-definition"**
convention (`tasks/reference/reduction-to-standard-position.md`; CLAUDE.md "Reduction to standard
position is an accepted duplicate-definition theme"): a canonical Hestenes definition PLUS a
deliberately-duplicate special-case variant, the variant marked with a prime (Lean) or a suffix
(Python, e.g. `_sp`), proved equal. The default/canonical stays the coordinate-free one.

## Already done — do NOT re-litigate or rebuild

- **Per-type dot/wedge (+ `<`/`>` contractions), closed-form, proved == `Gn`** — shipped via the
  generator's `product_result`/`resolve` + `dispatch_method` + `product_overload_stubs` machinery.
  See `archive/2026/06/06/graded-blade-subtypes.md` (return-type-from-symbolic-support rule),
  `archive/2026/07/22/add-left-right-contraction.md` (fullest end-to-end recipe for a new per-type
  bilinear op), `archive/2026/07/23/scalar-product-typing-overloads.md`,
  `tasks/reference/generated-product-typing.md`. Any new per-type op reuses this, never hand-writes rules.
- **Per-type `Vector.cross` (𝒢₃), closed-form, proved == wedge+dual and == `Gn`** —
  `archive/2026/08/31/generated-vector-cross.md`, `g3.py:3769`. The maintainer's "same thing for …
  cross product" is already realised for the closed form; what's new for cross would only be the
  fixed-grade / dimension-independent *presentation* + a Lean theorem (see `tasks/lean-coverage-gap-audit.md`,
  where `cross` is listed as a cheap Lean win from `dual`+wedge).
- **Special-case dot/wedge = general, proved (Python + Lean)** —
  `archive/2026/08/03/verify-dot-wedge-as-projection-rejection-products.md` (`a∥ b = a·b`, `a⊥ b = a∧b`,
  symbolic 2D/3D + numeric; harvested to `tasks/reference/dot-wedge-projection-rejection.md`), and the
  coordinate-free Lean property algebra (`archive/2026/09/30/lean-proofs-make-coordinate-free.md`).
- **Hestenes dot excludes grade 0; contractions include it** — settled
  (`tasks/reference/contraction-and-dot-definitions.md`); a fixed-grade `dot` must keep the grade-0
  exclusion to stay equal to `inner_product`.

## What is genuinely new (the deliverables)

Per Decision 1, the fixed-grade and coordinate rungs are added as **proved-equal teaching material**
(notebook/book demonstrations + tests + Lean theorems), NOT as competing public `dot`/`wedge` methods;
the only genuinely-missing *API* pieces are the general `abs_sin` (DONE Phase 1) and the signed 𝒢₂ `sine`.

1. **A general unsigned `abs_sin`** on `MultiVectorBase` — the companion the API was missing next to
   `cosine` (`base.py:1303`), unsigned (Decision 4), `|a∧b| / (|a||b|)`. **DONE 2026-10-01**
   (Phase 1): inherited by the generated classes via MRO, numeric-preserving, cos²+abs_sin²==1 tested.
2. **A signed 𝒢₂ `sine` — a per-type generated closed form** (𝒢₂ `Vector` only), `(a ∧ b).coeff_e_12 /
   (|a| |b|)`, the oriented turn-direction sine mvp uses for edge-side tests. Analogous to the existing
   𝒢₂-only `rotate_90_degrees` and 𝒢₃-only `Vector.cross` closed forms. 𝒢₂ only — 3D has no single
   turn direction (mvp's 3D form is the unsigned `abs_sin`). Name `sine`, raises on zero length
   (Decisions 7, 6). mvp `mathutils.py` is the behavioral reference.
3. **A per-type fixed-grade `dot`/`wedge` *demonstration*** — the middle rung, `(a*b).r_vector_part(K)`
   with `K` a **bound literal** per grade-pure pair (vector·vector: `.r_vector_part(0)` for dot,
   `.r_vector_part(2)` for wedge), shown in a notebook/book page and pinned by a symbolic test + a Lean
   theorem — not a new public method (Decision 1).
4. **Per-type vector `cosine` + the fixed-grade/signed sine special cases**, shown the same way
   (demonstration + equivalence check), reusing `abs_sin`/`sine`/`cosine`.
5. **Equivalence checks** for every special case: a **symbolic (and numeric) Python test** that the
   special form equals the canonical general form; and, where the special case is a *derivation* worth
   certifying, a **Lean theorem** — the signed-2D ones have ready targets (`Rotation.uvec_wedge` is the
   signed `sin`, `Rotation.lean:91`; `Trig.sin_between` the unsigned, so 2D equivalence is
   `|signed| = unsigned`), plus `sin_between ↔ uvec_wedge`, `cos_between ↔ uvec_dot`, and the
   fixed-grade dot/wedge = `mul_eq_dot_add_wedge` graded-part form.
6. **Pedagogy surface**: the "levels of abstraction, all proved equal" chain shown in the book /
   percent-notebooks (coordinate → fixed-grade → coordinate-free), ties into
   `tasks/investigate-lean-to-python-proof-notebooks.md` and
   `tasks/reference-doc-lean-workflow-and-proof-notebooks.md` — the "verify, don't derive" method.

## Phases (on go-ahead — single task with a phase list, Decision 5; not an umbrella)

- [x] **Phase 1 — general unsigned `abs_sin` on `base.py`** (companion to `cosine`, Decisions 4/7).
      **DONE + committed 2026-10-01** (initial method `6ff302b`; renamed `sine`→`abs_sin` per Decision 7
      the same day): `|A∧B|/(|A||B|)`, inherited by generated classes via MRO (no generator change;
      `check-generated` byte-identical), numeric-preserving (float→float on g2 verified), tests
      `test_multivector_abs_sin` + `test_abs_sin_cosine_pythagorean` (cos²+abs_sin²==1 numeric &
      symbolic). `make test` green (658 passing).
- [x] **Phase 2 — signed 𝒢₂ `sine`, a per-type generated closed form. DONE 2026-10-01.** Emitted by
      the generator (`tools/gen_specialized.py`, `if n == 2:` vector-role block, next to
      `rotate_90_degrees`) as `g2.Vector.sine(other) -> Coef = (a∧b).coeff_e_12 · |a|⁻¹ · |b|⁻¹` — a
      signed scalar (Decision 8), oriented (swap negates), raises on zero length (Decision 6), 𝒢₂-only
      (g1/g3 `Vector` have none). Dedicated `SINE_METHOD_DOC` with doctests. Tests: `tests/test_signed_sine.py`
      (signed value, swap-negates, parallel=0, `abs(sine)==abs_sin`, symbolic Lagrange `cos²+sin²=1`,
      raises on zero, 𝒢₂-only). `make test` green (666); `make check-generated` byte-identical; `make
      format` (ruff + ty) green. Reference: mvp `mathutils.py` `sine`.
      `make check-generated` byte-identical + `make test`.
- [x] **Phase 3 — the per-type fixed-grade `dot`/`wedge` demonstration. DONE 2026-10-01.** Symbolic
      test `tests/test_fixed_grade_dot_wedge.py` (5 tests, host-green) pins, for the grade-pure vector
      pair (Gn 2D/3D + generated g2/g3), that `dot = (a*b).r_vector_part(0)` and `wedge =
      (a*b).r_vector_part(2)` with the grade a **literal**, equal to the canonical
      `inner_product`/`outer_product`, plus `ab = dot + wedge`. Pedagogy in the Phase-5 notebook.
- [x] **Phase 4 — Lean equivalences. DONE 2026-10-01** (`make lean` green, sorry-free, 8940 jobs).
      `proofs/GacalcProofs/TrigEquiv.lean` (imported in the proofs root): `uvec_magnitude`,
      `cos_between_uvec` (`G2.cos_between` of two unit vectors = `cos(β−α)`, via `uvec_dot`), a Lean
      `signed_sin_between` def (the Python `g2.Vector.sine`) with `signed_sin_between_uvec` = `sin(β−α)`
      (via `uvec_wedge`), `sin_between_eq_abs_signed_vec` (the unsigned `G2.sin_between` = `|signed|` for
      ANY two vectors — the Lean mirror of `abs(sine)==abs_sin`), and `sin_between_uvec = |sin(β−α)|`.
      Fixed-grade dot/wedge = graded-part needed no new theorem (already `G2.vec_mul`/`mul_eq_dot_add_wedge`;
      cross-referenced in the file header).
- [x] **Phase 5 — pedagogy. DONE 2026-10-01.** `book/docs/notebooks/levels-of-abstraction.py` (runnable,
      verified executes) + `book/docs/levels-of-abstraction.rst` (in the index toctree) show the
      coordinate → fixed-grade → coordinate-free chain for dot/wedge (all proved equal), that
      coordinate-free is dimension-independent (𝒢₂ and 𝒢₃), and the sine/cosine family
      (`cosine`/`abs_sin`/signed `sine`, `cos²+sin²=1`). Prose/figures are a draft for the maintainer's
      voice pass (noted in the .rst).

## Decisions (maintainer, 2026-09-30 for 1–5, 2026-10-01 for 6–7; William Emerison Six <billsix@gmail.com>)

1. **Naming / where the extra rungs live → agent's discretion; keep the canonical names.** Decided:
   do NOT mint competing public `dot`/`wedge`/`cosine` methods for the special cases — the canonical
   coordinate-free forms keep those names and stay the default. The fixed-grade and coordinate rungs
   are **proved-equal teaching material** (notebook/book demonstrations + symbolic tests + Lean
   theorems). The genuinely-missing *API* additions are the two trig names in Decision 7.
2. **"Per-type grade operation" = the `r_vector_part`-style projection, which already exists** (the
   maintainer clarified item 2 meant "the thing that returns just the components of that grade," not an
   integer grade-number accessor). No new grade operation is built; the integer-accessor question is
   moot and dropped. `r_vector_part` already works on grade-pure and multi-grade types alike.
3. **Which dims/types → agent's discretion, revisable.** Decided: vectors in g2+g3 first (the
   motivating case); extend to other grade-pure pairs/dims if it proves worthwhile.
4. **The general sine is unsigned** `|a∧b| / (|a||b|)`. (Superseded on naming by Decision 7: this
   function is named `abs_sin`, and `sine` is the signed 𝒢₂ form.) Note for Phase 4: Lean's
   `uvec_wedge` is the *signed* `sin(β−α)`, so the equivalence compares the unsigned `abs_sin` to
   `|uvec_wedge|` and the signed `sine` directly to `uvec_wedge`.
5. **Single task with a phase list** (not an umbrella).
6. **Zero-length guard → keep the raise (no NaN).** gacalc's `cosine`/`abs_sin`/`sine` divide by
   `|A|` and raise on a zero-length operand; do NOT add mvp's NaN guard. This stays consistent with the
   existing `cosine`, and mvp's NaN behavior is an mvp-side choice (not mirrored down into gacalc).
7. **Trig naming follows mvp: `sine` = signed, `abs_sin` = unsigned, used consistently everywhere.**
   `sine` is the **signed** (oriented, 𝒢₂-only) sine — `(a∧b).coeff_e_12 / (|a||b|)`; `abs_sin` is the
   **unsigned**, any-dimension one — `|a∧b| / (|a||b|)`. Applied 2026-10-01: Phase 1's general method
   was renamed `sine`→`abs_sin` (`base.py` + tests, `make test` green). The existing signed plotting
   helper `nbplotutils.sine` already matches (keeps its name). Phase 2 adds the signed `sine` as a
   generated 𝒢₂ `Vector` method. Consequence to watch: mvp also names them `sine`/`abs_sin` the same
   way, so the two libraries are now consistent (if mvp later delegates to gacalc, no rename needed).
8. **`sine` returns a signed scalar `Coef`** (not a bivector) — the "just the numbers" trig family
   alongside `cosine`/`abs_sin`. Full rationale + the bivector alternative considered: Open question 8.

## Open questions

8. **What should `sine` RETURN? → DECIDED: a signed scalar (Decision 8).** The maintainer first
   flagged the scalar return as odd (2026-10-01: "I don't know why sine gives scalar … we may not want
   to follow that"), then resolved it the same day: "maybe I do want scalar … sometimes we just want to
   know the sine and cosine." So `sine` returns a signed `Coef`, matching `cosine`/`abs_sin` — the
   "just the numbers" trig family. The GA-native alternative (a *bivector* `(a∧b)/(|a||b|) = sin θ·î`,
   so `cosine + sine` is the rotor) was considered and **not** chosen: the bivector/rotor view stays
   available directly via the wedge (`a ^ b`) and the geometric product when a caller wants it. No
   change to `abs_sin` (a scalar magnitude, consistent).

## Cross-references (verified to exist 2026-09-30; mvp line added 2026-10-01)

- Prior art (reference/validation): **github.com/billsix/modelviewprojection**
  `src/modelviewprojection/mathutils.py` — `cosine` (any-dim, NaN-guarded), `sine` (signed 𝒢₂),
  `abs_sin` (unsigned 𝒢₃); tests in `tests/test_mathutils.py`. gacalc is the lower layer, so these are
  adapted down, not imported.
- Theme: `tasks/reference/reduction-to-standard-position.md`, CLAUDE.md "Reduction to standard position".
- Dot/wedge: `tasks/reference/contraction-and-dot-definitions.md`,
  `tasks/reference/dot-wedge-projection-rejection.md`,
  `archive/2026/08/03/verify-dot-wedge-as-projection-rejection-products.md`,
  `archive/2026/07/22/add-left-right-contraction.md`.
- Per-type generation: `tasks/reference/generated-product-typing.md`,
  `archive/2026/06/06/graded-blade-subtypes.md`, `archive/2026/09/05/model-odd-graded-type.md`,
  `archive/2026/07/22/overload-r-vector-part.md`; cost caveat `tasks/reference/generated-algebra-generation-cost.md`.
- Lean: `tasks/reference/lean-ga-proof-architecture.md`,
  `archive/2026/09/30/lean-proofs-make-coordinate-free.md` (the "no abstract ⟨⟩_k" decision),
  `tasks/lean-coverage-gap-audit.md` (cross/reflect as cheap Lean wins); umbrella
  `tasks/investigate-lean-proofs-for-ga.md`.
- Pedagogy/notebooks: `tasks/investigate-lean-to-python-proof-notebooks.md`,
  `tasks/reference-doc-lean-workflow-and-proof-notebooks.md`.
- Adjacent/overlap to reconcile: `tasks/lean-general-gn-product-and-hestenes-dot-wedge.md` (deferred
  general-`Gn` Hestenes dot/wedge in Lean — the *opposite* direction from this task's per-type binding;
  keep them cross-linked so a proof isn't double-targeted).
