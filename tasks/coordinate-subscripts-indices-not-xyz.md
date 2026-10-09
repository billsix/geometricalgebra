# Write coordinates as `a_1`, `a_2`, not `a_x`, `a_y` — and introduce the notation for high-school readers

**Status:** proposed — needs go-ahead; the pedagogy half needs the maintainer's high-school-text
consult (see Plan step 1). API question decided 2026-10-09 (keep `.x`/`.y`/`.z`).
**Priority:** 4
**Difficulty:** 4
**Created:** 2026-10-08 (William Emerison Six <billsix@gmail.com>)

## BLUF

Use **indexed** coordinate subscripts in the book — `a_1`, `a_2` (and `a_3` in 3D) — instead of
the axis-letter form `a_x`, `a_y`, `a_z`, and **introduce that notation** where the book first
meets coordinates, for a reader whose last contact was high-school geometry / Algebra 2 /
precalculus (`(x, y)` points, `⟨a, b⟩` or `a i + b j` vectors). Maintainer, 2026-10-08: *"Use
things like `a_1` instead of `a_x`, introduce the notation for students familiar with high school
geometry. Bill will likely need to consult a high school text book for more context of what they
would know."* "Done" = zero `_x`/`_y`/`_z` coordinate subscripts in `book/docs/*.rst`, the ePiX
figure labels, and the book notebooks; an explicit "how we write coordinates" passage early in
Part I; `make docs` green.

## Why indices

- The subscript names **which basis vector** the coefficient multiplies: `a = a_1 e_1 + a_2 e_2`.
  With `e_1`, `e_2`, `e_{12}` already the book's basis notation, `a_x` is an orphan letter system.
- It survives the move to 3D and 𝒢ₙ (`a_1 … a_n`; there is no fourth axis letter), matching the
  code and the proofs, which **already** use indices: generated docstrings `a₁b₂ − a₂b₁`
  (`tools/gen_specialized.py` `CUSTOM_METHOD_DOCS`), Lean getters `a.c1`/`a.c2`
  (`proofs/GacalcProofs/*.lean`), the basis constants `e_1`/`e_2`. The book is the outlier.

## Current state (discovery 2026-10-08)

| Where | `_x`/`_y`/`_z` hits | Notes |
|---|---|---|
| `book/docs/proof-rotate-from-a-to-b.rst` | 22 | `\vec{a}_x`, `\vec{b}'_y`, … |
| `book/docs/proof-rotate.rst` | 16 | the derivation matrices |
| `book/docs/proof-projection.rst` | 12 | incl. the 3D `\vec{b}_z` |
| `book/docs/geometric-product.rst` | 8 | `(-\vec{a}_y, \vec{a}_x)` |
| `book/figures/epix/sp4.py` | 2 | labels `$a'_x$`, `$a'_y$` |
| `book/docs/notebooks/proof-projection.py` | ~4 | markdown `b_x`, code locals `b_x`/`b_y` |

Out of scope (public API, not prose): the generated `Vector.x`/`.y`/`.z` **attribute views**
(`AXIS_NAMES` in `tools/gen_specialized.py`; `v = Vector(-v.x, v.y)` in `CLAUDE.md`). Renaming
those is a SemVer-breaking change, and the maintainer decided (2026-10-09) to **keep them as-is**.
The book uses `.x`/`.y` in *code cells* and writes `a_1`/`a_2` in math — say so once where the
notation is introduced ("in code, the first coordinate is `.x`").

## Plan

1. **Pedagogy (maintainer-gated):** consult a high-school/precalculus text for what the reader
   already writes. Lead to check first: the OpenStax *Precalculus 2e* vectors section (component
   form `⟨a, b⟩`, unit vectors `i`, `j`, `v = a i + b j`) and *Algebra 1*'s `(x, y)` coordinate
   plane — both are in the maintainer's impo OpenStax ports (`tasks/reference/openstax-math-pedagogy.md`
   has the repo map and the regeneration command). Verify the exact section numbers in the
   source before citing them. The bridge sentence then writes itself: *you wrote `a i + b j`; we
   write `a_1 e_1 + a_2 e_2` — same thing, and the subscript tells you which axis, so it keeps
   working when there are three, or `n`.*
2. **Where to introduce it:** `book/docs/relative-graph-paper.rst` (placeholder: "coordinates,
   the natural basis") is the natural home — it is where two vectors become graph paper and a
   point gets coordinates on it; `vectors-as-number-lines.rst` and `trigonometry.rst` (both
   placeholders) precede it and may foreshadow. Add the passage there and a one-line pointer in
   `tasks/reference/book-outline.md` › "Notation & prose conventions" (new bullet: *coordinates
   are `a_1, a_2`, never `a_x, a_y`; introduced in Relative Graph Paper*).
3. **Sweep** (`tasks/adhoc/coordinate-subscripts-indices-not-xyz/discover.sh` — the grep in the
   table, logged to `data/`): `\vec{a}_x` → `a_1` style across the four `.rst` pages, the `sp4`
   figure labels (re-render), the `proof-projection` notebook markdown. Primes carry over
   (`\vec{b}'_y` → `b'_2`). Read every hit — a `_x` inside an ePiX `Point(x=…, y=…)` keyword
   argument is Python, not notation. **Run after `tasks/math-notation-parens-star-named-angles.md`**
   (same lines; that sweep changes `\cos\theta`/`r\,(…)` on the same equations) or in the same pass
   with its own commit.
4. Verify: re-grep = zero; `make docs`; read `proof-rotate` (densest page) in the PDF.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-10-09)

1. **Keep the generated `Vector.x`/`.y`/`.z` attribute views as the public API.** The book's
   math says `a_1`, `a_2`; its code cells say `.x`, `.y`; the mismatch is named once where the
   notation is introduced. No `.c1`/`.c2` aliases.

## Open questions

None.
