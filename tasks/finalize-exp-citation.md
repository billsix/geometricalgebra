# Finalize the `exp()` book citation

**Status:** proposed — waiting on Bill's own book reading (William Emerison Six
<billsix@gmail.com>). Not to be done now.
**Priority:** 6
**Difficulty:** 1

## Goal

The `exp()` slim-down (subtask 3 of the now-archived
`tasks/archive/2026/08/15/redo-exp-book-referenced.md`) shipped with a **provisional**
citation: the docstring, `CLAUDE.md`, and `tasks/reference/design-decisions.md` all cite
**Dorst, Fontijne & Mann, *Geometric Algebra for Computer Science*, §7.4** — the research
recommendation, not a text Bill has personally verified.

Bill wants to read the geometry himself (Hestenes & Sobczyk especially) and settle which
reference anchors the redo. When he has:

- Confirm **Dorst §7.4** as the anchor, **or** replace it with the text/section/equation he
  lands on (a specific Hestenes & Sobczyk page was never located — see the archived task).
- Update the citation in the **three** places that carry it (grep for `Dorst`): the `exp`
  docstring in `src/gacalc/base.py`, the `exp` bullet in `CLAUDE.md`, and the exp line in
  `tasks/reference/design-decisions.md`.

## Notes

- **Docstring/text only — the implementation does not change.** The code decision (drop the
  `A² > 0` hyperbolic/vector branch, keep scalar + `A² < 0` rotor case) is settled and done;
  this task is purely which book to point at.
- The primary secondary reference already noted: Macdonald, *Survey of GA & GC*, Eq. (2.3)/(2.4).
