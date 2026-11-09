# Backlog hygiene: archive the done sandwich task, re-rate `define-frame`, reconcile frame coverage

**Created:** 2026-11-09 · **Completed:** 2026-11-09
**Source:** `tasks/review/2026/11/08/repo-review.md` §9.1

## What changed

- **`generalize-sandwich-other-grades`** was archived to
  `tasks/archive/2026/11/09/generalize-sandwich-other-grades.md`, with a short done header.
  - The 𝒢₂/𝒢₃ work and reflections were done on 2026-10-22. Since 2026-10-23, 𝒢₄/𝒢₅ use the
    inherited, tested base sandwich.
  - Its two optional leftovers moved to `tasks/sandwich-followups-g4-g5-and-reflection-doc.md` (P9):
    the 𝒢₄/𝒢₅ operand tests, and a reflection docstring for `Vector.sandwich`.
- **`tasks/define-frame.md`.** The status now says only the codebase sweep and the optional prose
  proof remain; the representation decision was made on 2026-11-04. It is re-rated P6/D5 (from
  P8/D7, whose reason is gone), and gains a BLUF and a Context section. The sweep subtask no longer
  waits on the decision.
- **Frame coverage, made consistent in three places:**
  - `tasks/lean-frame-class-invertible-function.md`: theorems 5 and 6 are proved. Theorem 1 is proved
    in substance: each rejection is perpendicular to what it was rejected from
    (`G2.dot_reject_self`; `G3.reject_line_facts`, `reject_plane_facts`). Only the `w₃·w₂ = 0`
    corollary is unstated. Its open question 1 is marked mostly moot.
  - `tasks/lean-frame-coverage.md`: its BLUF says what is covered; its Priority/Difficulty are on
    their own lines.
  - `tasks/reference/lean-ga-proof-architecture.md`: the `frame.py` row is PARTIAL, with the same
    split.

## Verification

Every theorem named was checked with `grep` in `proofs/GacalcProofs/ReciprocalFrame2D.lean` and
`ReciprocalFrame3D.lean`, and every path cited exists.
