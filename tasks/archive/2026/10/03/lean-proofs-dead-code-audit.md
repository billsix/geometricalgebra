# Dead-code audit of the Lean proofs (`proofs/GacalcProofs/`)

**Created:** 2026-10-03 · **Completed:** 2026-10-03 (William Emerison Six <billsix@gmail.com>)
**See also:** `tasks/reference/lean-ga-proof-architecture.md`; the trigger was the sine/cosine work
(`tasks/archive/2026/10/03/prefer-sine-cosine-presentation.md`), which surfaced dead coordinate `_dot`
helpers and wired them up.

## Summary

The audit looked for genuinely dead lemmas/defs in the Lean proof corpus and found **none** beyond the
`_dot` helpers already handled by the sine/cosine task. The finding that shaped it: **"zero references"
is not a dead-code signal in a proof library.** Most uncited theorems are the deliberate proven results
(the point of the library). Dead code there means **orphaned helper machinery**: an intermediate lemma or
`def` that a refactor stopped citing. The action for such an item was a judgment per item: **wire it up**
if it is a useful primitive that lost its caller, **remove** it only if it is truly vestigial.

## Method

1. For each top-level `theorem`/`def` in `proofs/GacalcProofs/*.lean`, references outside its own
   definition were counted (`grep -nE '^(noncomputable )?(theorem|def) '` plus a per-name `grep -c`).
   About 60 names came back zero-referenced.
2. Each zero-ref name was triaged by its docstring as a **deliberate result** (a named geometric fact,
   algebra law, identity, or coverage-table entry: keep) or an **orphaned helper** (candidate for action).
   The first-scan candidates were in `CrossStandardPosition` (`reduceToPlane_*`,
   `cross_rotXY/XZ/YZ_equivariant`, `cross_reduced`, `rotYZ_fixes_e1`), `Sandwich` (`sandwich_ahat`,
   `sandwich_plane_invariant`, `sandwich_sub`, `sandwich_comp`), `RotateComponents`, `Normalize`
   (`magnitude_normalizeVec`), `TrigEquiv` (`cos_between_uvec`), `G2`/`G3` (`eq_vec_of_isVector`, a
   documented bridge), and the `expBivector*`/`normSq_expBivector*` helpers.
3. A grep-zero is necessary but not sufficient, since a lemma can be pulled implicitly
   (`@[simp]`/`@[ext]`/aesop). The safe confirmation for a removal was remove → `make lean` → keep removed
   only if still green.

## Findings

- **Unused `def`s: zero.** Every `def` (`mul`/`dot`/`wedge`/`cross`/`proj`, the rotation defs,
  `versorFromVectors`, …) was used.
- **The ~60 zero-reference theorems were all deliberate results.** They were named proven facts
  (`cross_anticomm_vec`, `normSq_reflectVec`, the `sandwich_*` properties, the exp-is-a-unit-versor
  lemmas, `mul_eq_proj_dot_add_reject_wedge`, the area/Lagrange forms, …) or documented construction steps
  (`CrossStandardPosition.lean` is a file of standalone reduction-to-standard-position results that do not
  cite each other by design; cf. `tasks/reference/reduction-to-standard-position.md`). Removing them would
  delete certified GA facts.
- **No `@[simp]`/`@[ext]` tags** were on any candidate, so the grep counts were reliable.
- **The only genuine dead code** was the `_dot` helper orphans created by the sine/cosine rename, already
  lifted to object level and cited under that task.

## Decision

No removals and no "dead" comments: everything in the corpus was an intentional result or machinery; the
default for an uncited result is keep. One adjacent, non-dead observation was flagged to the maintainer
without action: the `CrossStandardPosition` equivariance/reduce steps were proven but not yet assembled
into a single cross-product-via-reduction capstone. That capstone was later done in
`tasks/archive/2026/10/22/lean-cross-standard-position-capstone.md`.
