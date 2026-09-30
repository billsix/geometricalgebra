# Per-type fixed-grade dot/wedge, a per-type grade operation, and per-type sine/cosine — each proved equivalent to the general form

**Status:** proposed — needs go-ahead (2026-09-30, William Emerison Six <billsix@gmail.com>)
**Priority:** 6
**Difficulty:** 7
**Created:** 2026-09-30 **Updated:** 2026-09-30 (William Emerison Six <billsix@gmail.com>)

## BLUF

Add **special-case, per-type** definitions of the core operations — a fixed grade accessor, `dot`
and `wedge` written the Hestenes way but with the grade **bound to a literal constant** per type
pair, and `sine`/`cosine` for vectors — as **teaching artifacts that live alongside** the existing
canonical coordinate-free ones, with a **proof of equivalence** (symbolic test in Python, theorem in
Lean) for each. This makes concrete the project principle that special-case formulas at every level
of abstraction — full-coordinate → coordinate-free/dimension-independent — are *desirable* for
students, provided a check pins each to the general form; **the coordinate-free form stays the
default/canonical one.** "Done" for THIS task = the design questions below are decided and (on
go-ahead) the operations + equivalence checks land green (`make test` + `make lean`); it is **not**
yet authorization to implement.

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

**Grade operation — missing:**
- General grade **selection** exists (`r_vector_part(r)`, `base.py:985`; graded overrides carry
  `@overload` on `Literal[r]`, see `archive/2026/07/22/overload-r-vector-part.md`). There is **no
  per-type integer `grade` constant/accessor** — only `grades()` (runtime; returns `[]` for a zero
  value, `base.py:1141`) and the generator's `grade_name(k)` naming helper (`gen_specialized.py:2870`).
- A fixed `Vector.grade = 1` / `Bivector.grade = 2` constant is new and small — **but only
  well-defined for grade-pure types.** `Versor` ({0,2}) and `Odd_3` ({1,3}, `archive/2026/09/05/model-odd-graded-type.md`)
  are multi-grade and have no single grade; the fixed-grade dot/wedge applies to **grade-pure pairs
  only** (mixed types keep the general sum).

**Sine / cosine — cosine exists, sine does not:**
- `MultiVectorBase.cosine(other)` exists (`base.py:1303`, Hestenes 1.53b, `cos θ = (Ã ∗ B)/(|A||B|)`),
  general multivectors.
- There is **no `sine`** in the library core — only a notebook-plot free function `sine(v1, v2)`
  (`nbplotutils.py:309`, vectors only, via `v1 * e_12` then dot). So a general `sine` companion to
  `cosine`, and per-type vector `sine`/`cosine`, are new.

**Lean state (proofs/GacalcProofs, `make lean` green 2026-09-30):**
- dot/wedge as parts of the product are proved **per-dimension**: `G2.dot_is_sym_part`/`wedge_is_antisym_part`
  (`G2.lean:164`/`170`), `G3.mul_eq_dot_add_wedge` (`G3.lean:237`, arbitrary-vector) and the G2 twin
  (`Projection2D.lean:65`). `dot_eq_coord_sum` (`G2.lean:177`) is the archetype special↔general bridge.
- sin/cos exist in **two** characterizations with **no equivalence between them yet**: property form
  `Trig.cos_between`/`sin_between` (`Trig.lean:22`/`25` G3, `:88`/`:91` G2) via Lagrange; and
  angle-parametrized `Rotation.uvec_dot` (dot of unit vectors = `cos(β−α)`, `Rotation.lean:86`) /
  `uvec_wedge` (= `sin(β−α)`, `Rotation.lean:91`). Tying these is new and is exactly the gap.
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

1. **A per-type grade accessor** for grade-pure types (`Scalar`.grade=0 … the pseudoscalar), a fixed
   constant, generator-emitted. Decide whether multi-grade types expose `grades` only (no `grade`) or
   raise on `.grade`.
2. **Per-type fixed-grade `dot`/`wedge`** — the middle rung, `(a*b).r_vector_part(K)` with `K` a bound
   literal per grade-pure pair. As a *distinct, marked duplicate* of the existing closed-form
   `dot`/`wedge` (naming in Q3), NOT a replacement.
3. **A general `sine`** on `MultiVectorBase` (companion to `cosine`), plus **per-type vector
   `sine`/`cosine`** special cases.
4. **Equivalence checks** for every special case: a **symbolic (and numeric) Python test** that the
   special form equals the canonical general form; and, where the special case is a *derivation* worth
   certifying, a **Lean theorem** (esp. `sin_between ↔ uvec_wedge`, `cos_between ↔ uvec_dot`, and the
   fixed-grade dot/wedge = `mul_eq_dot_add_wedge` graded-part form).
5. **Pedagogy surface**: the "levels of abstraction, all proved equal" chain shown in the book /
   percent-notebooks (ties into `tasks/investigate-lean-to-python-proof-notebooks.md` and
   `tasks/reference-doc-lean-workflow-and-proof-notebooks.md` — the "verify, don't derive" method).

## Proposed phases (on go-ahead; may split into an umbrella if it grows past ~3 chunks)

- [ ] **Phase 0 — decide the design questions below** (naming, home, scope of grade accessor, how
      many dims/types). This is the go/no-go gate.
- [ ] **Phase 1 — grade accessor** (generator-first: `tools/gen_specialized.py`; grade-pure types get
      a fixed `grade`; verify `make check-generated` byte-identical + `make test`).
- [ ] **Phase 2 — general `sine` on `base.py`** + its symbolic/numeric test against the Lagrange
      relation `|a∧b| = |a||b| sinθ` (cf. `archive/2026/06/27/wedge-magnitude-sin-notebook.md`), keeping
      numeric-in→numeric-out (CLAUDE.md magnitude/inverse rule).
- [ ] **Phase 3 — per-type fixed-grade `dot`/`wedge` + per-type vector `sine`/`cosine`** (generator),
      each with a conformance/equivalence test vs the canonical form.
- [ ] **Phase 4 — Lean equivalences**: `cos_between ↔ uvec_dot`, `sin_between ↔ uvec_wedge`
      (`Trig.lean` ↔ `Rotation.lean`), and the fixed-grade dot/wedge = graded-part characterization;
      `make lean` green, `sorry`-free.
- [ ] **Phase 5 — pedagogy**: the levels-of-abstraction chain in a notebook/book page (coordinate →
      fixed-grade → coordinate-free), each rung annotated with its equivalence check.

## Design questions / decisions to make (BLOCKING — resolve in Phase 0)

Raised inline above; consolidated here so you can answer by number.

1. **Naming of the special-case duplicates.** The canonical `dot`/`wedge`/`cosine` names are taken by
   the coordinate-free forms and must stay the default. What suffix marks the special-case rung? A
   `_sp`-style suffix (echoing standard-position), a `_coord` / `_grade` suffix, or keep the extra
   rungs **out of the API entirely and only in notebooks/book**? (My lean: keep the fixed-grade and
   coordinate rungs as *teaching material in the book/notebooks* + one canonical API method each; add
   only the genuinely-missing API methods — `grade` accessor and a general `sine` — to the code. That
   avoids three near-identical public `dot`s.)
2. **Grade accessor on multi-grade types.** `Versor`/`Odd_3` have no single grade. Does `.grade` exist
   only on grade-pure types (my lean), or exist everywhere and raise on multi-grade, or return the set?
3. **Which dimensions/types for the per-type special cases?** All of g1–g3 (dev-generated), or just the
   vector cases the idea names? (My lean: vectors in g2+g3 first — the motivating case — then decide.)
4. **`sine` sign/branch.** `sin θ = √(1−cos²θ)` is non-negative; the wedge magnitude `|a∧b|/(|a||b|)`
   is also non-negative (unsigned angle). Is the general `sine` the unsigned magnitude form (my lean,
   matches `cosine`'s companion), or do you want an oriented/signed 2D sine (`(a∧b)` coefficient sign)?
   These are different functions; the Lean `uvec_wedge` is the *signed* `sin(β−α)`.
5. **Umbrella or single task?** If Phases 1–5 each want their own commit boundary, promote this to an
   umbrella with step-tasks (per CLAUDE.md step-task convention). My lean: keep it one task with the
   phase list above unless Phase 0 shows it's larger; don't over-scaffold.

## Cross-references (verified to exist 2026-09-30)

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
