# Finalize the `exp()` book citation

**Status:** done — 2026-10-22 (William Emerison Six <billsix@gmail.com>).
**Priority:** 6
**Difficulty:** 1
**Created:** 2026-08-14 **Updated:** 2026-10-22 (William Emerison Six <billsix@gmail.com>)

## What this was

The `exp()` slim-down (subtask 3 of the archived
`tasks/archive/2026/08/15/redo-exp-book-referenced.md`) shipped with a **provisional**
citation: the docstring and three reference/proof files cited Dorst, Fontijne & Mann,
*Geometric Algebra for Computer Science*, §7.4 as a *research recommendation* the maintainer
had not personally verified, hedged with "the maintainer may not own it — cite a maintainer-owned
book instead". This task was to settle the anchor once the maintainer had read the geometry.

## Decision (2026-10-22, William Emerison Six <billsix@gmail.com>)

**Keep Dorst, Fontijne & Mann §7.4 as the exp/rotor citation anchor of record** — do **not** swap
to Hestenes & Sobczyk or Macdonald. The code was never in question (the slim-down to scalar +
negative-square/rotor cases, with a vector `exp` raising `ValueError`, was already settled and
machine-checked in `proofs/GacalcProofs/Exp.lean`); this was purely which book to point at.

## What was done

- The four places that carry the §7.4 citation (`git grep -n Dorst`) were reconciled. Three
  already cited §7.4 cleanly and needed no change: `src/gacalc/base.py`'s `MultiVectorBase.exp`
  docstring, `proofs/GacalcProofs/Exp.lean`'s module header, and the `exp()` bullet in
  `tasks/reference/design-decisions.md`.
- `tasks/reference/unit-bivector-and-rotors.md` held all the provisional wording and was updated
  (commit `c43758e`): preamble now states the anchor is settled on §7.4 with the remaining
  ⬜ boxes reframed as optional, non-blocking corroboration; the §5 Dorst item flipped to the
  confirmed anchor of record; and §4 (the vector-branch domain) brought to the present — it says
  the `A²>0` vector branch *was dropped*, not "under review / leaning to drop".

The durable rationale lives in `tasks/reference/unit-bivector-and-rotors.md` (the anchor decision,
§5 Citations checklist) and `tasks/reference/design-decisions.md` (the `exp()` design bullet).

## Leftover flagged to the maintainer (not part of this task)

`unit-bivector-and-rotors.md` §6 (line ~239) still carries a Dorst **versor/operators chapter**
citation hedged "(Reference of record; the maintainer may not own it.)". That is a separate
citation from the §7.4 exp anchor, so this task's decision did not cover it. If the maintainer
wants the same ownership hedge dropped there (now that Dorst is accepted as a reference of record),
it is a one-line follow-up.
