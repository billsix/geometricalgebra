# Investigate per-grade constructors in Lean (bivector/trivector/scalar/versor), mirroring Python

**Status:** DONE 2026-09-30 (committed `43ab4c7`) — builders added + swept, gate-verified

## Outcome (2026-09-30)

Maintainer chose **option 3: named builders whose bodies are structure-updates** ("both — the
constructor name is nice, and the `{ zero with c… }` body makes it clear what's what"). Landed:
- `proofs/GacalcProofs/G3.lean`: `def bivector (p q r)` / `trivector (t)` / `scalar (a)`, each
  `{ G3.zero with … }`.
- Swept the recurring raw literals (`⟨0,0,0,0,p,q,r,0⟩` etc.) to the builders across `Sandwich.lean`
  (normSq/mul_biv/mul_triv/sandwich_fixes_own_bivector), `G3.lean` (`wedge_vec_eq_biv`),
  `Projection.lean` (project_add_reject / reject_eq_proj_normal / project_eq_sub_reject), and
  `Cross.lean` (`dual_vec`). Proofs' simp sets got `bivector`/`trivector`/`zero`. `make lean` green.

**Deferred (optional, not done):** grade predicates `IsBivector`/`IsVersor` (task Q3) — only useful
if a theorem needs to *hypothesise* "this is a bivector"; none does yet. `scalar` builder is provided
but currently unused (no pure-scalar literal in the swept proofs). Both are easy follow-ons if wanted.

## BLUF

The Python side has graded subtypes (`Scalar`/`Vector`/`Bivector`/`Trivector`/`Versor`, plus
`Odd_3`), but the **Lean** side represents everything as one flat coordinate struct per algebra —
there is no `vector`/`bivector`/`versor` *type*, only a `vec` coordinate constructor and an
`IsVector` *predicate*. This task investigates whether to give Lean per-grade construction
ergonomics like the Python side — either dedicated builders/abbreviations
(`bivector`/`trivector`/`scalar`/`versor` defs) or Lean's **structure-update syntax**
`{ x with … }` — and to decide if it's worth it. "Done" = a recommendation (add builders / use
update-syntax / leave as-is) with a worked example; NOT authorization to refactor the proof tree.

## Context — the exact current state in Lean (verified 2026-09-30)

- **One flat struct per algebra:** `structure G2 where s c1 c2 c12 : ℝ` (`proofs/GacalcProofs/G2.lean:49-54`,
  `@[ext]`); `structure G3 where s c1 c2 c3 c12 c13 c23 c123 : ℝ` (`G3.lean:26-35`). These are the
  ONLY structures in the whole tree.
- **A "vector" is not a type**, it is:
  - a coordinate literal: `def vec (x y : ℝ) : G2 := ⟨0, x, y, 0⟩` (`G2.lean:102`); `def vec
    (x y z : ℝ) : G3 := ⟨0, x, y, z, 0, 0, 0, 0⟩` (`G3.lean:116`); and
  - a **predicate**: `def IsVector (a : G3) : Prop := a.s=0 ∧ a.c12=0 ∧ …` (`G3.lean:214`,
    `G2.lean:156`), with bridge `eq_vec_of_isVector` (`G3.lean:219`), closed under smul/sub
    (`G3.lean:245/250`). Docstrings say explicitly "no vector subtype" (`G2.lean:154`, `G3.lean:211`).
- **Other grades: also no types.** Basis blades are plain values (`one`/`e_1`/`e_2`/`e_12`
  `G2.lean:88-98`; `one..e_123` `G3.lean:106-113`; `I`/`I_inv`). "Versor" is a def, not a type:
  `def evenVersor (s c : ℝ) : G2 := ⟨s,0,0,c⟩` (`Sandwich.lean:23`), `evenVersor (s c12 c13 c23 : ℝ) : G3`
  (`Sandwich.lean:105`). Bivectors/trivectors are written as raw anonymous-constructor literals
  inline, e.g. `(⟨0,0,0,0,p,q,r,0⟩ : G3)` (bivector) / `(⟨0,0,0,0,0,0,0,t⟩ : G3)` (trivector)
  throughout `Sandwich.lean`.
- **Structure-update `{ x with … }` is used NOWHERE** — every `with` in the tree is a
  `structure … where` / `def … : T where` keyword or docstring prose, never a record update. So
  this task cannot cite an existing precedent; it would introduce the idiom.

## The two candidate approaches (to evaluate)

1. **Per-grade builder defs / abbreviations** — `def bivector (p q r : ℝ) : G3 := ⟨0,0,0,0,p,q,r,0⟩`,
   `def trivector (t : ℝ) : G3 := ⟨…,t⟩`, `def scalar (s : ℝ) : G3 := ⟨s,0,…⟩`, `versor` (already
   `evenVersor`). Pro: readable call sites (kills the inline `⟨0,0,0,0,p,q,r,0⟩` literals that
   recur in `Sandwich.lean`); trivial, low-risk; mirrors Python's constructors. Con: they're just
   sugar over `⟨…⟩`; adds names.
2. **Structure-update syntax** `{ (0 : G3) with c12 := p, c13 := q, c23 := r }` — Lean's
   record-update. Pro: names the fields you set, zeroes implied by a base value. Con: needs a zero
   base value in scope; less common in this codebase; may read worse than a named builder.

## Why this is worth considering (and why it might not be)

- **For:** the inline `⟨0,0,0,0,p,q,r,0⟩` bivector/trivector literals are error-prone and unreadable
  (which of 8 slots is which?), and they recur. Named builders would make the proofs about
  bivectors/versors self-documenting and match the Python graded-type story a reader already knows.
- **Against:** Lean proofs work on the *flat* struct with `ext <;> ring`; per-grade builders are
  pure sugar and don't change what's provable. If they force extra `simp [bivector]` unfolding
  they could add friction. Predicates (`IsVector`) already carry the "this is grade-k" *fact*;
  builders only help *construction*.

## Overlap check

No existing task covers the LEAN type representation. (Python-side graded subtypes are tracked
separately — e.g. `tasks/model-higher-odd-and-mixed-graded-types.md` — but nothing about Lean.)
Safe to create.

## Open questions

1. **Which approach** — named builder defs (my lean: yes, they're cheap and kill the unreadable
   inline literals), structure-update syntax, or leave the flat `⟨…⟩` as-is?
2. **Scope if we proceed:** just add the builders and *use them at new call sites*, or also sweep
   the existing inline `⟨0,0,0,0,p,q,r,0⟩` literals in `Sandwich.lean` to the builders (a churn +
   re-verify pass)? My lean: add builders now, adopt going forward, sweep opportunistically.
3. **Predicates too?** Add `IsBivector`/`IsVersor` predicates to match `IsVector`, or are builders
   enough? (Predicates matter only if a theorem needs to *hypothesise* "this is a bivector.")
