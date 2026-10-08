# Name a's standing angle β in the rotate-from-a-to-b proof (prose + figure)

**Status:** done — 2026-10-08 (gates green)
**Priority:** 6
**Difficulty:** 2
**Created:** 2026-10-08 (William Emerison Six <billsix@gmail.com>)

## What was done (2026-10-08)

- **Prose** (`book/docs/proof-rotate-from-a-to-b.rst`, step 1): named :math:`\beta` as the angle
  :math:`\vec{a}` makes with the x-axis — :math:`\cos\beta = \vec{a}_x/|\vec{a}|`,
  :math:`\sin\beta = \vec{a}_y/|\vec{a}|` — and we swing :math:`\vec{a}` onto the axis by rotating by
  :math:`-\beta` (cosine even, sine odd ⇒ the rotation uses :math:`\cos = \vec{a}_x/|\vec{a}|`,
  :math:`\sin = -\vec{a}_y/|\vec{a}|`), without computing :math:`\beta`. Matches `proof-rotate.rst`'s
  use of :math:`\beta` for a vector's standing angle; :math:`\theta` stays the :math:`\vec{a}\to\vec{b}`
  angle.
- **Figure** (`book/figures/epix/rotate_ab_goal.py`): added a wedge from the x-axis to :math:`\vec{a}`
  labelled :math:`\beta` (radius 0.3), alongside the existing :math:`\theta` wedge (bumped to radius
  0.55 so the two read as nested angles). Verified by render→view; keyword-only, typed
  (`check_epix_keywords` green).
- **Gates** — `make format` and `make docs` green (page renders with :math:`\beta`, figure embeds).

## BLUF

In `book/docs/proof-rotate-from-a-to-b.rst`, step 1 ("swing :math:`\vec{a}` onto the x-axis") writes the
rotation's cosine and sine as :math:`\cos = \vec{a}_x/|\vec{a}|`, :math:`\sin = -\vec{a}_y/|\vec{a}|`
**without naming the angle**. Name it **:math:`\beta`** — the angle :math:`\vec{a}` makes with the
x-axis — in the prose, and **show :math:`\beta` in the figure**. This matches the book's angle
convention (`tasks/reference/book-outline.md`: :math:`\beta` = a vector's own standing angle,
:math:`\theta` = the rotation applied). Here :math:`\theta` stays the :math:`\vec{a}\to\vec{b}` angle;
:math:`\beta` is new, for :math:`\vec{a}`'s own angle. **Not started — this is the spec.**

## What to change

- **Prose** (`book/docs/proof-rotate-from-a-to-b.rst`, step 1): introduce :math:`\beta` as the angle
  :math:`\vec{a}` makes with the x-axis, so :math:`\cos\beta = \vec{a}_x/|\vec{a}|`,
  :math:`\sin\beta = \vec{a}_y/|\vec{a}|`, and we swing :math:`\vec{a}` down to the x-axis by rotating
  **by :math:`-\beta`** (cosine even, sine odd ⇒ the rotation uses :math:`\cos = \vec{a}_x/|\vec{a}|`,
  :math:`\sin = -\vec{a}_y/|\vec{a}|`). Keep it consistent with how `proof-rotate.rst` already uses
  :math:`\beta` for a vector's standing angle.
- **Figure** (`book/figures/epix/rotate_ab_goal.py`, the "goal" plot — it shows the vectors at their
  original positions): add a wedge from the x-axis up to :math:`\vec{a}` labelled :math:`\beta`,
  alongside the existing :math:`\theta` wedge (:math:`\vec{a}` to :math:`\vec{b}`). `A_ANGLE` is in
  `_rotate_ab_scene.py`; use `wedge(start=0.0, finish=A_ANGLE, text=r"$\beta$", radius=...)` with a
  radius that doesn't collide with the :math:`\theta` wedge (which runs `A_ANGLE`→`B_ANGLE`). If showing
  both angles in one figure is too busy, show :math:`\beta` in `rotate_ab_step1` instead (judgment call).

## Conventions / gates

- Figure: every argument by keyword, every binding typed (`check_epix_keywords` gate); place the new
  label cleanly (no overlap with :math:`\theta`, the vectors, or axis labels). Use the render→view loop
  (`tools/render_epix_figures.py rotate_ab_goal` → view the PNG) and iterate.
- `make docs` green (page + figure render); `make format` green. Stage by path.

## Related

- `book/docs/proof-rotate-from-a-to-b.rst` — the page, and `book/figures/epix/rotate_ab_goal.py` /
  `_rotate_ab_scene.py` — the figure + its vectors.
- `tasks/reference/book-outline.md` — the angle convention (β = standing angle, θ = rotation applied).
- `book/docs/proof-rotate.rst` — already uses β for a vector's standing angle (match its usage).
