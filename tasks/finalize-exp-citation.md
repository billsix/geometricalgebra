# Finalize the `exp()` book citation

**Status:** blocked — waiting on the maintainer's own book reading (Hestenes & Sobczyk especially).
Not to be done now.
**Priority:** 6
**Difficulty:** 1
**Created:** 2026-08-14 **Updated:** 2026-10-04 (William Emerison Six <billsix@gmail.com>)
**Blocked on:** the maintainer confirms the book anchor for `exp` — Dorst §7.4 as-is, or a Hestenes &
Sobczyk / Macdonald page/equation to replace it.
**Recheck:** the maintainer names the anchor (maintainer-gated; `/recheck-blocked` surfaces it).

## Goal

The `exp()` slim-down (subtask 3 of the now-archived
`tasks/archive/2026/08/15/redo-exp-book-referenced.md`) shipped with a **provisional**
citation: the docstring and `tasks/reference/design-decisions.md` (and, since, the Lean `Exp.lean`
header and the `unit-bivector-and-rotors.md` citations checklist) cite
**Dorst, Fontijne & Mann, *Geometric Algebra for Computer Science*, §7.4** — the research
recommendation, not a text the maintainer has personally verified.

The maintainer wants to read the geometry himself (Hestenes & Sobczyk especially) and settle which
reference anchors the redo. When he has:

- Confirm **Dorst §7.4** as the anchor, **or** replace it with the text/section/equation he
  lands on (a specific Hestenes & Sobczyk page was never located — see the archived task).
- Update the citation in the **four** places that carry it (`git grep -n Dorst`, 2026-10-04): the
  `MultiVectorBase.exp` docstring in `src/gacalc/base.py`; the `exp()` bullet in
  `tasks/reference/design-decisions.md`; the module header of `proofs/GacalcProofs/Exp.lean`; and the
  §5 "Citations" checklist in `tasks/reference/unit-bivector-and-rotors.md` (its ⬜ "book source …
  for the redo" item is this task). `CLAUDE.md`'s `mv.exp()` bullet no longer cites Dorst (it points
  at the two reference docs) and needs no change.

## Notes

- **Docstring/text only — the implementation does not change.** The code decision (drop the
  `A² > 0` hyperbolic/vector branch, keep scalar + `A² < 0` rotor case) is settled and done;
  this task is purely which book to point at.
- The primary secondary reference already noted: Macdonald, *Survey of GA & GC*, Eq. (2.3)/(2.4).
- The implementation is also machine-checked: `proofs/GacalcProofs/Exp.lean`
  (`normSq_expBivectorGeneral` — exp of any nonzero 𝒢₃ bivector is a unit versor). A citation change
  touches that file's header comment only; no proof changes.
