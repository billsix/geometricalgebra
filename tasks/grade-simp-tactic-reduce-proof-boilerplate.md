# A `grade_simp` tactic to collapse the getter-native proof boilerplate (exploratory)

**Status:** proposed — **EXPLORATORY; the maintainer is undecided whether to do this at all**
(William Emerison Six <billsix@gmail.com>, 2026-10-04). **Agent: raise this proactively in a future
session to ask whether it's wanted — and DO NOT START IT without the maintainer's explicit
"yes, do it" at that time.** This is a hard gate: the idea is speculative and may be dropped.
**Priority:** 9 (low — nothing depends on it; purely a cleanliness/ergonomics win)
**Difficulty:** 6 (writing a Lean 4 tactic/macro + making it robust across the proof styles)
**Created:** 2026-10-04 (from a design discussion; see Context).

## BLUF

The getter-native proofs repeat a boilerplate shape: `obtain ⟨hs, h12, …⟩ := ha; … ; simp only
[defs, those-zeros]; ring`. The idea is a small custom tactic — call it `grade_simp` — that, given the
grade hypotheses in context (`IsVector`/`IsEvenVersor`/`IsBivector`/`IsTrivector`), **destructures them
and runs the `simp` with exactly the zero-facts in one step**, so a typical leaf proof collapses to a
line. It would **not** change theorem signatures or the "for vectors/versors" precondition framing —
it only removes proof-body boilerplate. "Done" (if ever pursued) = the tactic exists, the converted
proofs use it, `make lean` green. **Not required; may never be done.**

## Context — why a tactic, and why NOT the alternatives we discussed (2026-10-04)

Prompted by the maintainer asking whether a `match`/grade-dispatch or a dedicated per-grade type could
*replace* the current `{a : G3} (ha : IsVector a)` hypothesis method, and whether that'd be cleaner. The
conclusion of that discussion (record it here so the reasoning isn't lost):

- **A grade `match`/`classify`/view is not a substitute for the hypothesis.** The hypothesis is a
  *precondition on a theorem* ("for vectors, `P` holds"); a `match` is *runtime dispatch* on an arbitrary
  value. Stating a theorem as "for any `a`, match its grade…" forces a vacuous/`default` branch for the
  non-matching grades — weaker and clumsier than the precondition. And for `ℝ` components a classifier is
  `noncomputable` (real equality is only classically decidable), so it lives only in proofs anyway.
- **A dedicated per-grade type (`Vec3` struct, or subtype `{a : G3 // IsVector a}`, or a grade-indexed
  `GradedAlgebra`) is probably *not* cleaner here.** GA operations are grade-mixing: `wedge u v` of
  vectors is a bivector, `mul u v` is scalar+bivector, the sandwich routes vector→vector through an even
  versor. A per-grade type zoo therefore inserts coercions/embeddings at nearly every operator — the
  *opposite* of cleaner. The flat `G3` + grade predicate exists precisely so grade-mixing ops compose
  without ceremony, and it mirrors the flat Python multivector that these proofs are *verifying* (a
  stated gacalc goal). A subtype is just the hypothesis method in disguise (`.val`/`.property` noise).
- **So the verbosity is in the proof body, not the signature design.** The right lever is a tactic that
  kills the `obtain … := h; simp only [defs, zeros]` repetition — hence this task.

## Sketch (if pursued)

A macro/elaborator `grade_simp [extra simp lemmas]` that: finds hypotheses of type
`IsVector _`/`IsEvenVersor _`/`IsBivector _`/`IsTrivector _` in the local context, `obtain`s each into its
component `= 0` facts, then runs `simp only [<the operation defs the goal mentions>, <those zero facts>,
extra]`. Open questions to settle at design time: how it picks the def lemmas (explicit arg vs a
curated default set like `normSq, mul, reverse, dot, wedge, smul, add, sub, vec`), whether it finishes
with `ring`/`ext <;> ring` or leaves that to the caller, and how it handles the divide-by-`normSq` proofs
(which also need the grouped-`^2` denominator fact and `field_simp [hr]` — see the recipes doc).

## Relationship to the simp-component trim (`tasks/trim-unused-simp-components.md`)

If this tactic is ever built, the per-proof simp-arg minimization becomes mostly moot — the tactic would
pass only the zero-facts that fire. So consider this a potential *successor* that would supersede the
hand-trimmed simp lists. (That trim is a fine standalone cleanup regardless; this would subsume it.)

## See also

- `tasks/reference/lean-ga-proof-architecture.md` — the getter-native norm, the recipes, the dead-ends
  (the boilerplate this would collapse).
- `tasks/archive/2026/10/04/lean-object-in-getters-out-proof-style.md` — where the proof style came from.
- `tasks/lean-unit-versors-rotors-sandwich-with-reverse.md` / `tasks/push-delicate-coordinate-core-tier.md`
  — other open Lean-proof threads.
