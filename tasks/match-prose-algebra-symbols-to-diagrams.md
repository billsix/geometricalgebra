# Match prose/algebra variable names to the adjacent diagram (not to a source proof)

**Status:** proposed — needs go-ahead
**Priority:** 4
**Difficulty:** 2
**Created:** 2026-10-08 (William Emerison Six <billsix@gmail.com>)

## BLUF

The algebra and symbols in the book's prose should match the **diagram the reader is looking at**.
When prose explains a figure, its variable names should be the figure's labels — not names carried in
from a source proof (e.g. *Model View Projection*) or an earlier section's proof. A concrete violation
is in the rotation section: `book/docs/rotate.rst` introduces the from→to rotation with
:math:`\vec{v_1}` and :math:`\vec{v_2}`, but the section's diagram (`rotate-goal`) labels the vector
:math:`\vec{a}`, and the **entire rest of the book** uses :math:`\vec{a}`/:math:`\vec{b}`
(`\vec{v_1}`/`\vec{v_2}` appear nowhere else). This task fixes that instance, sweeps the book for any
other prose-vs-diagram symbol mismatch, and records the convention (in
`tasks/reference/book-outline.md`) so future prose is generated this way.

## The finding (the specific mismatch)

- `book/docs/rotate.rst` lines 16–18: *"We will define it the way Model View Projection does … rotate
  so that the direction of* :math:`\vec{v_1}` *is carried onto the direction of* :math:`\vec{v_2}`*."*
- The section's only figure, `rotate-goal` (`book/figures/epix/rotate_goal.py`), labels the vector
  :math:`\vec{a}` and its image :math:`\vec{r}(\vec{a};\theta)`. The derivation it links
  (`proof-rotate.rst`) and its figures `rotate1`–`rotate8` use :math:`\vec{a}`, :math:`r`,
  :math:`\beta`, :math:`\theta`, :math:`\vec{x'}`, :math:`\vec{y'}` — all consistent with each other.
- A book-wide grep confirms `\vec{v_1}`/`\vec{v_2}` occur **only** in `rotate.rst`; `\vec{a}`,
  `\vec{b}`, `\vec{v}` are the book's convention (e.g. `vector-addition`, `projection`,
  `proof-projection`, `geometric-product`).

So `rotate.rst` imported *Model View Projection*'s `v_1`/`v_2` naming instead of matching its diagram
and the book. **Fix:** rename to the book/diagram convention — "rotate so that the direction of
:math:`\vec{a}` is carried onto the direction of :math:`\vec{b}`." (The magnitudes-don't-matter point
is unchanged.)

## Plan

1. **Fix `rotate.rst`** — `\vec{v_1}` → `\vec{a}`, `\vec{v_2}` → `\vec{b}` (two lines). Re-read the
   paragraph so it still flows.
2. **Sweep the book for other prose-vs-diagram symbol mismatches.** For each prose page with a figure,
   compare the figure's drawn labels (`book/figures/epix/<name>.py` `text=` strings, or the `.svg`
   label) against the algebra/prose beside it; flag any symbol that the algebra uses but the figure
   does not (or names differently). Pages to check first: `rotate`, `proof-rotate`, `geometric-product`,
   `projection`, `proof-projection`, `projection-rejection-3d`, `vector-addition`, `reflection`, `dual`.
   - **Judgment call to surface, not auto-change:** `proof-rotate.rst` "Now the algebra" switches from
     the diagram symbols (:math:`\cos\beta`, :math:`\sin\beta`, :math:`r`) to the components
     :math:`\vec{a}_x`, :math:`\vec{a}_y`. This looks **intentional** — the component form
     :math:`\vec{r}(\vec{a};\pi/2)=(-\vec{a}_y,\vec{a}_x)` is exactly what `geometric-product.rst` then
     recognizes as the product :math:`\vec{a}\,e_{12}`, so the names earn their place. Leave it unless
     the maintainer wants the substitution rephrased in :math:`\beta`-terms. (Open question 2.)
3. **Record the convention** in `tasks/reference/book-outline.md` under "Notation & prose conventions
   for proof pages" (new bullet, text below). CLAUDE.md already flags `book-outline.md` as the book
   content guide, so it stays discoverable without bloating CLAUDE.md.
4. **Rebuild + verify.** `make docs` green (the changed pages render); `make format` green if any
   figure file was touched. Stage by path.

### Convention text to add (book-outline.md)

> - **Match the algebra's symbols to the diagram beside it.** When prose or algebra sits next to a
>   figure and explains it, use **the figure's own variable names** — not names carried in from a
>   source proof (e.g. *Model View Projection*) or an earlier section's proof. The reader is looking at
>   the picture; the symbols must line up with it. (Origin: `rotate.rst` had imported *MVP*'s
>   `\vec{v_1}`/`\vec{v_2}` while its diagram and the whole book use `\vec{a}`/`\vec{b}`.) If a diagram
>   and its algebra genuinely need different symbols, change the **diagram** to match, not the reverse.

## Open questions

1. **Confirm this is the mismatch you found** — `rotate.rst`'s `\vec{v_1}`/`\vec{v_2}` vs the diagram's
   `\vec{a}`. If you meant a different spot, say which and I'll retarget.
2. **`proj-rotate`'s `\vec{a}_x`/`\vec{a}_y` in "Now the algebra"** — leave as the deliberate payoff
   (recommended; it feeds `geometric-product`), or rephrase in :math:`\beta`-terms to match the
   diagrams?

## Related

- `tasks/reference/book-outline.md` — the book's structure + the proof-page notation conventions (home
  for the new rule).
- `book/docs/rotate.rst`, `book/figures/epix/rotate_goal.py` — the fix site and its diagram.
- `tasks/book-rotation-from-vectors-no-angle.md` — the future from→to rotation section (would use the
  same `\vec{a}`/`\vec{b}` names).
