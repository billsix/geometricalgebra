# Trim unused destructured component hypotheses from the getter-native proofs

**Status:** DONE 2026-10-04, archived 2026-10-04 (`make lean` / full `check.sh` green at every step).
**Priority:** 7 (cosmetic/readability; no correctness or performance effect). **Difficulty:** 4.
**Created:** 2026-10-04 (William Emerison Six <billsix@gmail.com>).
**Followed:** `tasks/archive/2026/10/04/lean-object-in-getters-out-proof-style.md` (the conversion these
proofs came from). **Successor (exploratory):** `tasks/grade-simp-tactic-reduce-proof-boilerplate.md`.
**Durable record:** `tasks/reference/lean-ga-proof-architecture.md` — "Trimming vacuous `simp` args and
dropping unused hypotheses", "Hypotheses: what each kind is for, and how to decide", and "Structural
proofs over brute `ring`" — and the independent review
`tasks/reference/lean-proof-corpus-review-2026-10-04.md` (§1, §5).

## BLUF

The getter-native proofs destructured a grade predicate into its component zeros and handed them all to
`simp only`, e.g. `obtain ⟨hR1, hR2⟩ := hR; …; simp only [dot, normSq, mul, reverse, hR1, hR2, hus, hu12, …];
ring`. Some of those components never fired. This task removed the vacuous ones by delete-and-rebuild, so
each proof's `simp` list documents exactly the components it relies on, and then — the finding it
produced — generalized the theorems whose grade hypotheses had become vacuous in the process.

## What was done

1. **The minimizer** (`tasks/adhoc/trim-unused-simp-components/trim.py`, one-shot, deleted at archive)
   snapshotted the eight converted files, asserted the baseline build green, and for every `obtain`+`simp
   only` block tried each component that appeared only in the `simp` list: remove it, rebuild, keep the
   edit iff green, else restore; a failed full gate at the end would have restored every snapshot. Greedy,
   not globally minimal, by decision (a perfect minimum was not worth a combinatorial search). Result: 206
   candidates, 73 components dropped, 103 kept as load-bearing, 14 all-`_` `obtain` lines removed, 30
   skipped as not cleanly editable. Per file: Sandwich 30, Projection3D 20, Projection2D 10,
   ProjectionRotation3D 8, G3 2, ProjectionRotation2D 2, Trig 1.
2. **Why delete-and-rebuild, not reading:** every component name appeared in the `simp` list, so
   name-presence said nothing; `simp only` silently ignores an argument that does not fire; and Mathlib has
   no unused-`simp`-arg linter (checked `Mathlib/Tactic/Linter/` 2026-10-04; only `UnusedTactic`).
3. **Generalization.** Several leaves turned out more general than stated — their `obtain`s vanished,
   leaving unused grade hypotheses in the signatures. Dropped, with call sites, build-verified:
   `wedge_reverse_sandwich` and `normSq_reverse_sandwich_wedge` (both grades), `normSq_mul_three_vec`
   (`hf`), `dual_wedge_perp_right_dot` (`ha`), then the 𝒢₂ `dot_reverse_sandwich`/`normSq_reverse_sandwich`.
   The detection heuristic (`detect.py`, promoted to `tools/detect_unused_hypotheses.py`) listed signature
   grade predicates and `≠ 0` guards never named in the body — a candidate list only, because
   `field_simp`/`simp` consume `≠ 0` guards from context unnamed.
4. **The error, and its correction.** The 𝒢₃ `dot_reverse_sandwich`/`normSq_reverse_sandwich` were left
   with their vector hypotheses on the belief that their proofs "genuinely use the components — a real
   mathematical asymmetry", and that an attempt to drop them had failed to build. The minimizer's log shows
   that attempt never ran:

   ```
   [02:42:14]   skip Sandwich.lean:dot_reverse_sandwich:hR123 (could not edit cleanly)
   [02:42:22]   skip Sandwich.lean:dot_reverse_sandwich:hu12 (could not edit cleanly)
   [02:42:22]   skip Sandwich.lean:dot_reverse_sandwich:hus (could not edit cleanly)
   …  (every hu*/hv* candidate of the 𝒢₃ dot/normSq leaves: skip)
   ```

   The independent review the same day rebuilt without them (green) and showed why: the identity is
   `(R u R̃)(R v R̃) = R u (R̃ R) v R̃ = |R|²·R (u v) R̃` plus the cyclic scalar part, grade-free. Both
   grades were then generalized with structural proofs (`mul_reverse_self_of_isEvenVersor`,
   `reverse_mul_self_of_isEvenVersor`, `dot_reverse_conj`), the vacuous `hu`/`hv` were dropped from the
   composites downstream (`sandwich_preserves_dot/_normSq/_wedge/_normSq_of_wedge`, `magnitude_sandwich`,
   `sandwich_preserves_cos/_sin`, `rotation_preserves_dot`, `dual_wedge_perp_right`; the `_of_vec`/`_vec`
   names lost their suffix), and the "asymmetry" sentence was removed from `CLAUDE.md`, the architecture
   doc, and this task.

## Decisions

- Only `_`-out an `obtain` slot once the name was gone from the whole block (the `unusedVariables` linter
  would otherwise warn, and a bound-unused name was the mess being removed).
- Skip names used outside a `simp` list (`rw`, a `have`, a second `simp`) rather than let the build
  catch them — cheaper and clearer.
- A failed delete-and-rebuild has two readings — needed by the theorem, or only by this proof script's
  tactic budget — and must be classified before a hypothesis is kept. Recorded in the architecture doc.
- Lean's `unusedVariables` linter DOES flag an unused signature hypothesis (contrary to this task's first
  draft); read the build warnings. A hypothesis rewritten in place (`rw … at h`) and then used is flagged
  spuriously.

## Verification

Full `check.sh` green after the minimizer (2026-10-04 02:47), after each generalization, and after the
structural rewrite (`[lean] OK`, 0 errors; unused-variable warnings 11 → 4, the 4 being the spurious
`rw … at hn` kind in `ProjectionRotation3D.lean`).
