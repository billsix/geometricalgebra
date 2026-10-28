# Add `/-! ### -/` navigation section headers to the four header-less Lean proof files

**Status:** proposed — needs go-ahead
**Priority:** 8
**Difficulty:** 2
**Created:** 2026-10-28 (William Emerison Six <billsix@gmail.com>)

## BLUF

Four proof files in `proofs/GacalcProofs/` carry **zero** `/-! ### … -/` section headers despite being
100–275 lines, so there are no in-file waypoints when reading or jumping around them. Add headers that
group the existing declarations by phase — a **purely additive** change (new comment lines only, no
reorder, no body touched), so `make lean` must stay green and `git diff` must show only inserted
`/-! ### -/` lines. Spun out of the file-structure sweep
(`tasks/study-and-reorder-lean-file-structure.md`), which found these four while confirming the rest of
the corpus was already sectioned.

## The four files (line counts as of 2026-10-28)

- `proofs/GacalcProofs/Rotation2D.lean` (275) — `rot`, `fullAngleRotor`, `uvec`, `polar`,
  `fullAngleRotorFromTo`, `rotor`, and their lemmas: natural groups are the angle-parameterized rotation
  (`rot` + `rot_add`/`rot_comm`), the full-angle teaching operator, `uvec`/`polar`, and the half-angle
  `rotor` + `isRotor_rotor`.
- `proofs/GacalcProofs/Rotation3D.lean` (145) — `bisector`, `versorFromVectors`, and the versor facts.
- `proofs/GacalcProofs/StudentTrigForms.lean` (177) — the `cos`/`sin` student-facing corollaries; group
  by the geometric relation each presents (perpendicularity, parallelism, …).
- `proofs/GacalcProofs/PlaneRotation3D.lean` (155) — `planeRotor` + the `rotorSandwich_planeRotor` angle
  theorem and its corollaries.

## Method

1. Read each file; decide 2–4 phase boundaries that match the existing top-to-bottom declaration order
   (do **not** reorder — these files are already in good order per the sweep's audit).
2. Insert `/-! ### <phase> -/` lines (blank line before and after) at those boundaries. Match the
   wording/▸style of the headers already used in `G2.lean`/`G3.lean`/`Projection3D.lean`.
3. `make lean` (USE_LEAN image, `proofs/check.sh`) — must stay green. `git diff` must be inserted
   `/-! -/` lines only (no moved declarations).

## Deliverables

- The four files sectioned; `make lean` green; diff = additive header lines only.

See also: `tasks/study-and-reorder-lean-file-structure.md`, `tasks/reference/lean-ga-proof-architecture.md`.
