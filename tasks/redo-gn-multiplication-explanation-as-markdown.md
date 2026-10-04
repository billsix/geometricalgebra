# Redo the "explain Gn multiplication" explanation as markdown, in the swap/annihilate style

**Status:** proposed — needs go-ahead. Created 2026-08-16 (William Emerison Six <billsix@gmail.com>).
**Updated:** 2026-10-04 (William Emerison Six <billsix@gmail.com>) — two cited tasks repointed to their
archives; the overlapping book chapter now exists (see Notes).
**Priority:** 4
**Difficulty:** 3

## Why this task exists

While writing the pseudoscalar-square-sign proof (`tasks/reference/pseudoscalar-square-sign.md`), the
hand-counted **swap / flip / annihilate** presentation — writing a product out as a sequence of basis
vectors, sliding one factor left one adjacent swap at a time (each an `e_i e_j = −e_j e_i` sign flip),
and annihilating `e_i e_i = +1` pairs, with a running sign and an ASCII diagram — is **exactly the
explanation the maintainer wanted** for how `Gn` multiplication works (William Emerison Six
<billsix@gmail.com>, 2026-08-16). The existing
explanation, archived at
`tasks/archive/2026/08/14/explain-gn-multiplication-for-highschoolers.md`, was written into the
notebook `notebooks/displaymv.py` as prose + runnable cells; it's good, but it does **not** show the
move-by-move ASCII canonicalization that makes the mechanism click.

So: revisit that work and **redo the explanation as markdown**, in the same hands-on, count-every-move
style as the pseudoscalar proof doc.

## Goal

Produce a plain-language, high-school / early-college explanation of the geometric product of `Gn`
that teaches the **mechanism by watching the moves**, in markdown (matching
`tasks/reference/pseudoscalar-square-sign.md`'s voice and its ASCII-diagram format):

- The three rules (R1 `e_i e_i = +1`, R2 `e_i e_j = −e_j e_i`, concatenation + distributivity), stated
  once — reuse the framing already in the pseudoscalar doc so the two read as a set.
- **Worked products shown move-by-move in ASCII**, with a running sign, e.g.
  `e_2 e_1 → −e_1 e_2` (one swap); `e_1 e_2 e_1 → −e_1 e_1 e_2 = −e_2` (swap then annihilate);
  `(3e_1 + 4e_2)² = 25` (distribute, then the cross terms cancel by R2); `(e_1 e_3)(e_3 e_1) = +1`
  (annihilate from the middle). Pull the concrete examples from the archived task's verified list
  (they were all checked against a `Gn` REPL) so the numbers are known-good.
- Connect the recipe to `gn.py`'s `decrease_grade` (the four `match` arms: base / annihilate /
  swap+negate / in-order-insert) — the ASCII *is* what that function does, step by step.
- Lead naturally into the two follow-on proofs that reuse the same machinery:
  `tasks/reference/geometric-product-associativity.md` (its work record is archived at
  `tasks/archive/2026/08/25/prove-associativity-of-multiplication.md`) and
  `tasks/reference/pseudoscalar-square-sign.md`.

## Open questions

1. **Where should the markdown live?** Options: (a) a new `tasks/reference/` doc (e.g.
   `gn-multiplication-by-hand.md`) — durable, sits beside the pseudoscalar and (eventual) associativity
   write-ups as a "how the product works, by counting" set; (b) as book/notebook prose that ships to a
   reader; (c) both — reference doc as the source of truth, a trimmed version in the notebook. Lean:
   **(a)** first (fast, and it's the natural sibling of the pseudoscalar doc), then decide about the
   notebook. Needs the maintainer's call.
2. **Keep or retire the existing notebook prose?** The archived task added a multiplication-rules
   section to `notebooks/displaymv.py`. Do we leave that as-is (the runnable, in-notebook intro) and
   add the ASCII markdown alongside, or fold/replace? Lean: **leave the notebook, add the markdown** —
   they serve different readers (runnable demo vs. read-the-moves proof).

## Notes / decisions

- This is a **redo of** `tasks/archive/2026/08/14/explain-gn-multiplication-for-highschoolers.md`
  (that task is DONE/archived for the notebook prose); this task is specifically about the
  ASCII-move-by-move markdown presentation, which that task did not cover.
- Style template: `tasks/reference/pseudoscalar-square-sign.md` (grades 1–5 by hand, ASCII, running
  sign, tally table).
- **Overlaps the book chapter that now EXISTS:** `book/docs/blade-square-sign.rst` ("Squaring a
  Blade: The Sign, by Counting Flips", written 2026-08-16; work record archived at
  `tasks/archive/2026/08/16/prove-blade-square-sign-equals-pseudoscalar-squared.md`, "Book chapter"
  section, William Emerison Six <billsix@gmail.com>, 2026-08-16). It already presents the two rules,
  the slide-and-cancel moves in ASCII literal blocks with a running sign (grades 1–5), and a part 2
  "Numbers and symbols come along for the ride" — exactly the "symbols × bases" mechanism
  (scalars-to-front → blade rules → sign-in-front-of-scalars) — **but only for squaring a blade**.
  This task is NOT done by it: the general-product examples above (`e_1 e_2 e_1`, `(3e_1 + 4e_2)²`,
  the tie to `decrease_grade`) are not in that chapter, and `book/docs/multiplication.rst` is still a
  placeholder. Coordinate so the chapter and this explanation share one canonical treatment of the
  mechanism rather than duplicating it; this task owns the general/reference form and the chapter
  presents the blade-squaring slice.
