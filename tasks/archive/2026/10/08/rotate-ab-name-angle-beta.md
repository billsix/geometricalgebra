# Name a's standing angle β in the rotate-from-a-to-b proof (prose + figure)

**Status:** done — 2026-10-08 (gates green; normalized pre-squash)
**Priority:** 6
**Difficulty:** 2
**Created:** 2026-10-08 (William Emerison Six <billsix@gmail.com>)

## BLUF

Step 1 of `book/docs/proof-rotate-from-a-to-b.rst` ("swing `a` onto the x-axis") had written the
rotation's cosine and sine as `cos = a_x/|a|`, `sin = -a_y/|a|` **without naming the angle**. Named it
**β** — the angle `a` makes with the x-axis — in the prose, and **showed β in the goal figure**. Matches
the book's angle convention (`tasks/reference/book-outline.md`: β = a vector's own standing angle, θ =
the rotation applied); here θ stays the `a→b` angle and β is `a`'s own. `make format` + `make docs`
green.

## What was done

- **Prose** (`proof-rotate-from-a-to-b.rst`, step 1): named β as the angle `a` makes with the x-axis —
  `cos β = a_x/|a|`, `sin β = a_y/|a|` — and we swing `a` onto the axis by rotating by `-β` (cosine
  even, sine odd ⇒ the rotation uses `cos = a_x/|a|`, `sin = -a_y/|a|`), without computing β.
- **Figure** (`book/figures/epix/rotate_ab_goal.py`): added a wedge from the x-axis to `a` labelled β
  (radius 0.3) alongside the existing θ wedge (bumped to radius 0.55 so the two read as nested angles);
  verified by render→view, keyword-only and typed (`check_epix_keywords` green).

## History (commit chronology, branch `rotateFromAToB` — for the squash)

1. `ad0fabb` *added task* — filed this task (then proposed).
2. `aa3b563` *implemented name angle beta* — the prose + figure edits; gates green.
3. `4dfe3f0` *archived name angle beta* — `git mv` to `tasks/archive/2026/10/08/` (a proper staged
   rename — the first archive under the corrected "always `git mv`, never leave it untracked"
   convention).

## Related

- `book/docs/proof-rotate-from-a-to-b.rst`, `book/figures/epix/rotate_ab_goal.py` — the edited page + figure.
- `tasks/reference/book-outline.md` — the angle convention (β = standing angle, θ = rotation applied).
- `book/docs/proof-rotate.rst` — uses β for a vector's standing angle (the usage this matched).
