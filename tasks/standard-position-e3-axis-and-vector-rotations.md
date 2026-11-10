# Standard-position project/reject: defined on the e_3 axis, built from 2-D vector-to-vector rotations

**Status:** parked — the 2-D rotation design is on hold (see Decisions)
**Priority:** 7
**Difficulty:** 5
**Created:** 2026-11-10 (William Emerison Six <billsix@gmail.com>)
**Branch:** `sp-rotations-guards-enums-examples`

## BLUF

`project_sp`/`reject_sp` (`src/gacalc/standardposition.py`) raise `ValueError` when `b` lies along
`e_3`, because the first alignment step divides by `|xy-part of b| = 0`. The maintainer wants them
**defined there**, by giving the elementary rotation a rule for the zero vector:

- a rotation **from the zero vector to the zero vector is the identity**;
- a rotation **from the zero vector to a nonzero vector** (or nonzero to zero) is a `ValueError`.

With that rule, aligning `b = b_z e_3` takes the xy-part `0` onto `|0|·e_1 = 0` (identity), then the
xz step does the rest. Second, the two hand-written `(cos, sin)` coordinate rotations should be
replaced by a **2-D rotation from a vector to a vector** applied in a coordinate plane (the book's
"rotate from direction a to direction b", `book/docs/proof-rotate-from-a-to-b.rst`,
`proofs/GacalcProofs/RotateFromTo2D.lean`), so the code reads as "rotate this onto that" rather
than as cosines read off coordinates. The maintainer still wants coordinates here. Done means:
`project_sp(a, 1 * e_3)` works and equals `a.projected_onto(e_3)`, the 0→0 / 0→a rule is in place
and doctested, the Lean `StandardPosition.lean` transcription matches the new Python, and the gate
(`make test`, `make type-check`, the Lean build) is green.

## Context (read first)

- `tasks/reference/reduction-to-standard-position.md` — the theme and the **non-circular bootstrap**
  (elementary plane rotations → project/reject → `projection_rotation`). The module docstring says no
  versors / geometric product / matrices, so the 2-D vector-to-vector rotation used here must itself
  be elementary (built from coordinates), **not** `transforms.projection_rotation`, which is defined
  from project/reject. On hold (Decisions).
- `proofs/GacalcProofs/StandardPosition.lean` (`projectSP_eq_proj`, `rejectSP_eq_reject`) transcribes
  the current `(cos, sin)` formulas; it must follow the change.
- `transforms.projection_rotation` already treats parallel same-direction vectors as the identity and
  opposite ones as a `ValueError`; whether the zero rule also applies to the public rotation factories
  is decided: yes, all of them (Decisions).

## Plan

1. Add an elementary 2-D "rotate `u` onto the direction of `w`" in a coordinate plane (with the zero
   rule), next to the existing book/Lean `rotateFromTo` form.
2. Rewrite `_project_via_standard_position` with it; drop the e_3 `ValueError`; add simple + e_3-axis
   doctests.
3. Update the Lean transcription and proofs; update the reference doc and the book page if it quotes
   the old formulas; CHANGELOG entry (behavior change: no longer raises on the e_3 axis).

## Decisions

- Whether the 2-D vector-to-vector rotation inside `project_sp` is built from coordinates or from `projection_rotation` (circularity, Lean proof): **on hold for the 2026-11-10 night** (William Emerison Six <billsix@gmail.com>, 2026-11-10). This task stays parked until that is decided.
- The zero-vector rule (0 → 0 is the identity, 0 → nonzero and nonzero → 0 raise `ValueError`) applies to **all the public rotation factories** too (William Emerison Six <billsix@gmail.com>, 2026-11-10). That part does not depend on the hold, so it was split into `tasks/rotation-factories-zero-vector-rule.md`.
