# Lean low cleanup: doc-comment notation, history comments, moved-task citations, misplaced theorems

**Status:** proposed — needs go-ahead
**Priority:** 7
**Difficulty:** 3
**Created:** 2026-11-09
**Source:** tasks/review/2026/11/08/repo-review.md §7.3, §2.4

## BLUF

Fix the low findings in `proofs/`:
- Lean doc comments that break the notation rules;
- history comments;
- citations of tasks that have moved;
- three declarations that sit in the wrong file.

Done means `make lean` passes (build, `sorry` grep, axioms gate) and a re-grep finds none of the
listed patterns.

## Context

Read first:
- `CLAUDE.md` › "Math notation for readers": in Lean doc comments the star has no spaces (`|a|*|b|`),
  every product is a `*`, and the middle dot is the dot product only;
- `tasks/reference/algebra-teaching-order.md`, for where moved declarations go;
- `tasks/reference/lean-ga-proof-architecture.md`.

Lean *code* is exempt; only doc comments and `proofs/README.md` change.

- **Juxtaposition** (record lines): G2:9-12, G3:6, Sandwich `R R̃`, Rotor:306 `2cos(θ/2)`,
  Rotation2D:244. Re-checked: `proofs/GacalcProofs/G2.lean:9` still reads `u v = (u·v) + (u∧v)*e₁*e₂`.
- **Middle dot used as multiplication:**
  - G1:36;
  - G2:74,170,210,460,464 (e.g. `x·e₁ + y·e₂`, G2.lean:77);
  - G3:58,62,190,227,231;
  - Cross:62; Exp:15,61,144; Projection3D:9,145,179; Rotation2D:273.

  Keep every dot that really is a dot product (`(u·v)` above is one).
- **A spaced star** at CrossStandardPosition:301; **`cos²|B|`** at Exp:152.
- **History comments:** G2:176, Rotor:135,268, ProjectionRotation2D:25, Rotation3D:7-11.
- **Moved-task citations (§2.4, proofs):**
  - Cross → `tasks/lean-candidates-from-symbolic-tests.md`;
  - Sandwich → `tasks/lean-proof-rotation-preserves-length.md` and `-angles.md`;
  - RotateComponents → `tasks/lean-proof-sandwich-rotates-components.md`.

  Repoint each to its archive path.
- **Misplaced code:**
  - the G2 wedge-preservation theorems sit in `Projection2D`;
  - G2's `mul_vec_self` sits in `ProjectionRotation2D`;
  - G3's `rVectorPart` uses struct literals where G2's uses the basis constants.

  Moving a theorem changes import order; follow the teaching order and rebuild.

## Plan

- [ ] Fix the notation and history comments file by file, re-grepping each pattern at the end.
- [ ] Repoint the citations.
- [ ] Move the three misplaced pieces. Update any book page that cites them by file (`grep -rn
  "Projection2D\|ProjectionRotation2D" book/docs tasks/reference`).
- [ ] `make lean` (needs a `USE_LEAN=1` image).

## Open questions

None.
