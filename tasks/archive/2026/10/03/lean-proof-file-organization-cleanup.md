# Lean proof files: unify the 2D/3D filing rule and fix asymmetric names

**Status:** done. **Priority:** 6. **Difficulty:** 4.
**Completed:** 2026-10-03 (William Emerison Six <billsix@gmail.com>).

The `proofs/GacalcProofs/*.lean` corpus is organized **by topic** (one concept per file), which was
kept — folding topic files into `G2.lean`/`G3.lean` was rejected (it would scatter cross-dimensional
concepts and bloat the core files; `G2.lean`/`G3.lean` stay the per-algebra leaf layer). The real
problem was naming inconsistency: a bare file name meant a *different dimension* depending on topic
(`Rotation.lean` was 2D, `Projection.lean` was 3D).

Applied the approved rule — a dimension-specific file is suffixed `2D`/`3D`; a bare name means both
dimensions or a solo-dimension concept — to the **ambiguous paired** concepts only (solo-dimension
files like `Cross`/`Reflect`/`StandardPosition` stayed bare, having no sibling to confuse them with):

- `Rotation.lean → Rotation2D.lean`, `Projection.lean → Projection3D.lean`,
  `ProjectionRotation.lean → ProjectionRotation3D.lean`,
  `Projection2DRotation.lean → ProjectionRotation2D.lean`.
- Updated the root `GacalcProofs.lean` import list and the 5 sibling `import` lines; later also fixed
  the prose pointers to these files in the reference docs and `CLAUDE.md` (the session-end sweep
  caught those — the rename pass had updated `import`s but not prose).

Pure reorg, no theorem/tactic changes; verified `make lean` green (`lake build`, no `sorry`/`admit`).
Convention recorded in `tasks/reference/lean-ga-proof-architecture.md` ("File organization & naming").
(A later follow-on, the `Predicates2D`/`Predicates3D` split, extended the same rule — see
`lean-lift-theorem-statements-to-objects`.)
