# Backlog hygiene: archive the done sandwich task, re-rate `define-frame`, reconcile frame coverage

**Status:** proposed — needs go-ahead (approved in session 2026-11-09; in progress)
**Priority:** 3
**Difficulty:** 2
**Created:** 2026-11-09
**Source:** `tasks/review/2026/11/08/repo-review.md` §9.1

## BLUF

Three backlog problems from the review. Done means each task's status matches the tree:

- `tasks/generalize-sandwich-other-grades.md` is done except for optional pieces;
- `tasks/define-frame.md` is rated by a blocker that is gone;
- three docs disagree about the Lean coverage of the frames.

## Context

- **generalize-sandwich.** Its 𝒢₂/𝒢₃ work and reflections were done on 2026-10-22. Since 2026-10-23,
  𝒢₄/𝒢₅ use the inherited, tested base sandwich. Only optional tests and a docstring remain.
- **define-frame.** The representation decision was made on 2026-11-04, but the task's P8 rests on
  it.
- **Frame coverage.** `tasks/lean-frame-class-invertible-function.md` says theorem 1 is proved;
  `tasks/reference/lean-ga-proof-architecture.md` says NONE; `tasks/lean-frame-coverage.md`'s BLUF
  says `frame.py` has no coverage. `ReciprocalFrame2D/3D.lean` prove each rejection is perpendicular
  to what it was rejected from (`dot_reject_self`, `reject_line_facts`, `reject_plane_facts`).

## Plan

- [ ] Archive generalize-sandwich with a short done header. Move its optional leftovers to
  `tasks/sandwich-followups-g4-g5-and-reflection-doc.md` (P9).
- [ ] Rewrite define-frame's status (P6/D5), and add a BLUF and Context.
- [ ] State, in all three docs, what is proved (rejection orthogonality, in substance) and what is
  not (`w₃·w₂ = 0` as its own theorem, the Hestenes form, `prefix_blades`, the coefficient table).

## Open questions

None.
