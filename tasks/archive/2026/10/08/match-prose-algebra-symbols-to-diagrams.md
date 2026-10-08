# Match prose/algebra variable names to the adjacent diagram (not to a source proof)

**Status:** done — 2026-10-08 (normalized pre-squash)
**Priority:** 4
**Difficulty:** 2
**Created:** 2026-10-08 (William Emerison Six <billsix@gmail.com>)

## BLUF

The algebra and symbols in the book's prose should match the **diagram the reader is looking at** —
when prose explains a figure, its variable names should be the figure's labels, not names carried in
from a source proof or an earlier section. One page violated this: `book/docs/rotate.rst` introduced
the from→to rotation with :math:`\vec{v_1}`/:math:`\vec{v_2}` (imported from *Model View Projection*'s
framing) while the section's diagram `rotate-goal` and the **whole rest of the book** use
:math:`\vec{a}`/:math:`\vec{b}`. Fixed by renaming to the book's convention; a book-wide sweep found no
other mismatch; and the rule was recorded in `tasks/reference/book-outline.md` so future prose follows
it. `make docs` green.

## The finding (the mismatch)

`book/docs/rotate.rst` (then lines 16–18) defined rotation "the way *Model View Projection* does …
rotate so that the direction of :math:`\vec{v_1}` is carried onto the direction of :math:`\vec{v_2}`."
But the section's only figure, `rotate-goal` (`book/figures/epix/rotate_goal.py`), labels the vector
:math:`\vec{a}` (image :math:`\vec{r}(\vec{a};\theta)`), and `proof-rotate.rst` + its figures
`rotate1`–`rotate8` use :math:`\vec{a}`, :math:`r`, :math:`\beta`, :math:`\theta`, :math:`\vec{x'}`,
:math:`\vec{y'}`, all consistent. A book-wide grep confirmed `\vec{v_1}`/`\vec{v_2}` appeared **only**
in `rotate.rst` — it had imported *MVP*'s names instead of matching its diagram and the book.

## What was done

- **`book/docs/rotate.rst`** — the definition now reads "carry the direction of :math:`\vec{a}` onto
  the direction of :math:`\vec{b}`" (`\vec{v_1}`→`\vec{a}`, `\vec{v_2}`→`\vec{b}`); the
  magnitudes-don't-matter point is unchanged. Rendered clean (no `v_1`/`v_2` in the built page).
- **Swept the figure-bearing pages** (`projection`, `projection-rejection-3d`, `vector-addition`,
  `geometric-product`, `proof-rotate`, `proof-projection`, `reflection`, `dual`): **no other
  mismatch** — each uses `\vec{a}`/`\vec{b}`/`\vec{v}` matching its figures; `reflection`/`dual` have
  no diagrams.
- **Recorded the convention** in `tasks/reference/book-outline.md` §"Notation & prose conventions for
  proof pages": *match the algebra's symbols to the diagram beside it; standing vector names are
  `\vec{a}`/`\vec{b}`/`\vec{v}`; if a diagram and its algebra must differ, change the diagram.*
  (CLAUDE.md already flags `book-outline.md` as the book content guide.)

## Decisions (maintainer, 2026-10-08)

1. **Q1 confirmed** — `rotate.rst`'s `\vec{v_1}`/`\vec{v_2}` was the mismatch.
2. **Q2: leave `proof-rotate.rst`'s `\vec{a}_x`/`\vec{a}_y`** (in "Now the algebra") as the deliberate
   payoff — that component form is exactly what `geometric-product.rst` recognizes as
   :math:`\vec{a}\,e_{12}`, so the names earn their place; not rephrased in :math:`\beta`-terms.

## History (commit chronology, `origin/master..HEAD` on branch `proseUpdates` — for the squash)

1. `21e8218` *made task for changing variable names to match diagrams* — filed this task (then proposed)
   with the finding, sweep plan, and the convention text.
2. `635db57` *renamed variable* — the `rotate.rst` rename + the `book-outline.md` convention bullet
   (and removed this task doc from its working path as part of archiving).

## Related

- `tasks/reference/book-outline.md` — the proof-page notation conventions (home of the new rule).
- `book/docs/rotate.rst`, `book/figures/epix/rotate_goal.py` — the fix site and its diagram.
- `tasks/book-rotation-from-vectors-no-angle.md` — the future from→to rotation section (same
  `\vec{a}`/`\vec{b}` names).
