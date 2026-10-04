# Trim unused destructured component hypotheses from the getter-native proofs

**Status:** DONE 2026-10-04 (`make lean` / full `check.sh` green). **Archive owed** — its own commit after
the maintainer commits the work (the minimizer is a one-shot → `git rm` at archive, or keep if more
getter proofs get added later). The exploratory successor is `tasks/grade-simp-tactic-reduce-proof-boilerplate.md`.
**Priority:** 7 (cosmetic/readability; no correctness or performance effect).
**Difficulty:** 4 (mechanical, but no Lean readout for "which simp arg fired" — delete-and-rebuild only).
**Created:** 2026-10-04 (William Emerison Six <billsix@gmail.com>).
**Follows:** the object-in-getters conversion, `tasks/archive/2026/10/04/lean-object-in-getters-out-proof-style.md`.

## BLUF

The getter-native proofs destructure a grade predicate into its component zeros and hand them all to
`simp`, e.g. `obtain ⟨hR1, hR2⟩ := hR; obtain ⟨hus, hu12⟩ := hu; …; simp only [dot, normSq, mul, reverse,
hR1, hR2, hus, hu12, hvs, hv12]; ring`. Some of those component hypotheses never actually **fire** (the
component doesn't appear in that proof's expansion) — they're present-but-vacuous. This task drops the
vacuous ones: replace the unneeded obtain slot with `_` and remove it from the `simp only [...]` list, so
each proof states exactly which components it relies on. **Purely cosmetic** — `simp only` silently ignores
an argument that doesn't fire, so leaving them is harmless; the value is the proofs reading as precise
documentation. "Done" = each converted proof's `simp` list carries only the components it needs, `make
lean` green.

## Why it needs delete-and-rebuild (not just reading the text)

"Does the name appear in the body?" is the wrong test — every component name **does** appear (it's in the
`simp only [...]` list), so by that test they're all "used." The real question is whether `simp` *does
anything* with `hR1 : R.c1 = 0`: only if `R.c1` survives into the goal when the proof's defs
(`wedge`/`mul`/`reverse`/`dot`/`normSq`) are unfolded. **Lean emits no report of which `simp` rules fired**
(there is no `unusedSimpArgs` linter — checked Mathlib's `Tactic/Linter/` 2026-10-04; only `UnusedTactic`
exists, which flags whole tactics). So the only reliable signal is: drop the candidate, rebuild, and see if
the proof still closes. Hand-reasoning from the `def` expansions works too but is tedious and error-prone
across ~40 proofs.

Worked confirmation: `G3.wedge_self_vec` — from the `wedge` def, `a.c123` only ever appears multiplied by
`a.s` (already 0), so `ha123` is vacuous; dropping it (→ `obtain ⟨has, ha12, ha13, ha23, _⟩`, `simp` minus
`ha123`) rebuilt green (2026-10-04). That one trim is already in the tree.

## Method — the automatic minimizer (`tasks/adhoc/trim-unused-simp-components/trim.py`)

Greedy delete-and-rebuild, run inside the container from `proofs/` (incremental `lake build`):

1. **Snapshot** every target file's content in memory; assert the baseline `lake build` is green.
2. For each theorem block containing `obtain ⟨…⟩ := h` **and** `simp only […]`, the **candidates** are the
   obtain-bound names that appear in a `simp only` list **and nowhere else** in the block (a name used in a
   `rw`/second tactic is skipped — not safe to drop).
3. For each candidate: remove it from the `simp only` list and set its `obtain` slot to `_`; `lake build`;
   **keep** the edit iff green, else **restore** the file. Log every decision.
4. **Safety net:** after all candidates, run the full gate; if not green, **restore ALL snapshots** (tree
   back to the pre-run state) and exit nonzero. So a failed/garbled run leaves the tree unchanged, never
   broken — the maintainer can only ever wake to (a) a cleanly-trimmed green tree or (b) the original tree.

Scope: the converted files `G3, Sandwich, Reflect, Projection2D, Projection3D, Trig, ProjectionRotation2D,
ProjectionRotation3D`. Trimming a genuinely-vacuous arg in any proof there is valid regardless of who wrote
it (build-verified), so the minimizer processes every `obtain`+`simp only` block in them.

## Decisions / rationale

- **Only `_`-out a slot once the name is gone from the whole block** — otherwise Lean's `unusedVariables`
  linter would warn (a warning doesn't fail `lake build`, but a bound-unused name is exactly the mess we're
  removing).
- **Skip names used outside a `simp` list** (in `rw`, a `have`, a second `simp`) — removing them would
  break those uses; the greedy build-check would catch it, but skipping is cheaper and clearer.
- **Keep it greedy, not globally-minimal** — greedy order can in principle keep one redundant arg when two
  are jointly removable; the payoff of a perfect minimum isn't worth a combinatorial search. Build-verified
  either way.

## Result (2026-10-04, full `check.sh` green)

The minimizer ran over all 8 converted files: **206 candidates → 73 components dropped**, 103 kept as
load-bearing (reverted), **14 all-`_` `obtain` lines removed**, 30 skipped (not cleanly editable — left
untouched, harmless). Per-file drops: Sandwich 30, Projection3D 20, Projection2D 10, ProjectionRotation3D
8, G3 2, ProjectionRotation2D 2, Trig 1. **No new warnings** (Lean's `unusedVariables` linter DOES warn on an unused signature hypothesis (the 09aa05a build already
showed five such warnings, and the review's rebuild eleven); the 4 pre-existing `hn` warnings in ProjectionRotation3D are unrelated). Full decision log:
`tasks/adhoc/trim-unused-simp-components/trim.log`.

**Finding worth noting (maintainer's call, not acted on):** several leaves turned out *more general than
stated* — e.g. `dot_reverse_sandwich` needs only `IsEvenVersor R`, not `IsVector u`/`IsVector v` (the
identity holds for arbitrary `u, v`); the minimizer removed their now-vacuous `obtain`s, leaving the
unused `(hu : IsVector u)`/`(hv : IsVector v)` hypotheses in the *signatures* (Lean doesn't warn on
those). **Generalization DONE for the grade-consistent cases (2026-10-04, maintainer: "generalize those", `make
lean` green).** Dropped the unused `IsVector` hypotheses from the signatures + call sites of:
`wedge_reverse_sandwich` (G2 + G3), `normSq_reverse_sandwich_wedge` (G2 + G3) — both hold for arbitrary
`u, v`, needing only `IsEvenVersor R`; `normSq_mul_three_vec` (dropped the unused `hf`, no callers);
`dual_wedge_perp_right_dot` (dropped the unused `ha`; one caller in StudentTrigForms updated). Detection
script: `tasks/adhoc/generalize-unused-hypotheses/detect.py` (grade-predicate hypotheses unreferenced in
the body — a *candidate* list; the build is the judge, because `field_simp`/`simp` use `_ ≠ 0` hyps from
context *without naming them*, so a name-absent `≠ 0` guard is NOT safe to drop; I restricted detection to
`IsVector`/etc. predicates and build-verified).

**Generalization of `dot_reverse_sandwich`/`normSq_reverse_sandwich` — BOTH grades (2026-10-04).** First
only the **G2** pair was generalized to `IsEvenVersor R` alone, on the belief that the **G3** proofs
"genuinely use the vector components — a real mathematical asymmetry". That belief was wrong: the
identity is `(R u R̃)(R v R̃) = R u (R̃ R) v R̃ = |R|²·R (u v) R̃` plus the cyclic scalar part, which never
looks at the grade of `u`, `v`; the minimizer log shows the G3 drops were never built (`skip … could not
edit cleanly`), and the "build failed, reverted" recollection had no log behind it. The independent review
(`tasks/reference/lean-proof-corpus-review-2026-10-04.md`) rebuilt without the hypotheses: green. Both
grades now take only `IsEvenVersor R`, proved **structurally** (`mul_reverse_self_of_isEvenVersor`,
`reverse_mul_self_of_isEvenVersor`, `dot_reverse_conj`, associativity) so the proof records the reason, and
the vacuous `hu`/`hv` were dropped from the composites downstream (`sandwich_preserves_dot/_normSq/
_wedge/_normSq_of_wedge`, `magnitude_sandwich`, `sandwich_preserves_cos/_sin`, `rotation_preserves_dot`,
`dual_wedge_perp_right`; the two `_of_vec`/`_vec` names lost their suffix). Lesson recorded in
`lean-ga-proof-architecture.md`: a failed delete-and-rebuild can mean the *proof script* needs the
hypothesis (tactic budget), not the theorem — read the failure before concluding.

## See also

- `tasks/reference/lean-ga-proof-architecture.md` — the getter-native norm, the recipes, and the dead-ends
  (incl. the `simp`-set gotchas: `vec` must be in the set when a def builds a `vec`; repeat the zeros after
  `ext`).
- `tasks/archive/2026/10/04/lean-object-in-getters-out-proof-style.md` — the conversion these proofs came
  from.
