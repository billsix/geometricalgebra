# Investigate per-grade constructors in Lean (bivector/trivector/scalar/versor), mirroring Python

**Created:** 2026-09-30 · **Completed:** 2026-09-30 (work squashed into `3f6e933`)

## Question

The Python side has graded subtypes (`Scalar` / `Vector` / `Bivector` / `Trivector` / `Versor`, plus
`Odd_3`); the Lean side had one flat coordinate struct per algebra (`structure G2 where s c1 c2 c12`,
`structure G3 where s c1 … c123`, both `@[ext]`, the only structures in the tree). A "vector" was a
coordinate literal `vec` plus an `IsVector` predicate (bridge `eq_vec_of_isVector`); basis blades were
plain values; "versor" was the `evenVersor` def; and bivectors/trivectors were written as raw literals
like `(⟨0,0,0,0,p,q,r,0⟩ : G3)` throughout `Sandwich.lean`. Structure-update `{ x with … }` was used
nowhere. Should Lean get per-grade construction ergonomics?

Trade-off weighed: the 8-slot literals are error-prone and unreadable and they recur, and named
builders would match the Python graded-type story; but builders are pure sugar over the flat struct
(nothing new becomes provable), may add `simp` unfolding friction, and the `IsVector` predicates already
carry the grade fact.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-09-30)

1. **Option 3: named builders whose bodies are structure-updates** — "both — the constructor name is
   nice, and the `{ zero with c… }` body makes it clear what's what". Rejected: bare builder defs over
   `⟨…⟩`, bare structure-update at call sites, and leaving the literals as-is.
2. **Sweep the existing literals** to the builders, not just adopt them at new call sites.
3. **Grade predicates `IsBivector` / `IsVersor` deferred:** useful only if a theorem needs to
   hypothesise "this is a bivector", and none did.

## What changed

- `proofs/GacalcProofs/G3.lean`: `def bivector (p q r)`, `trivector (t)`, `scalar (a)`, each
  `{ G3.zero with … }`.
- The recurring raw literals were swept to the builders in `Sandwich.lean` (normSq / mul_biv /
  mul_triv / sandwich_fixes_own_bivector), `G3.lean` (`wedge_vec_eq_biv`), `Projection.lean`
  (project_add_reject / reject_eq_proj_normal / project_eq_sub_reject) and `Cross.lean` (`dual_vec`);
  the proofs' simp sets gained `bivector` / `trivector` / `zero`.
- The `scalar` builder was added but was unused (no pure-scalar literal in the swept proofs).

No other task covered the Lean type representation (the Python side is
`tasks/model-higher-odd-and-mixed-graded-types.md`).

## Verification

`make lean` green.
