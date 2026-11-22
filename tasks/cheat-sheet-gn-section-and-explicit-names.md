# Reference cards: a separate 𝒢ₙ section, named values by kind, grade projections for parts

**Status:** ready — decisions made, waiting for the go-ahead to execute
**Priority:** 4
**Difficulty:** 4
**Created:** 2026-11-22 (William Emerison Six <billsix@gmail.com>)

## BLUF

The plane's reference card (`book/docs/cheat-sheet-2d.rst`) mixes the general 𝒢ₙ formulas into
every 𝒢₂ chain, leaves most of its names implied, and writes the parts of a multivector as
subscripted components. Three changes: (1) the 𝒢ₙ formulas get their own section; (2) the card
names its scalars, vectors, bivector and versor explicitly, each built from named things; (3) a
part of a multivector is written with the grade projection, `⟨A⟩_2`, not a subscript, `A_{12}`.
Done = the card reads that way, `make docs` passes its overflow check, and
`tasks/reference/book-outline.md` describes the new layout.

## The request (2026-11-22, the maintainer's words)

> look through the cheat sheet at the beginning. firstly, there should be a gn section, it
> shouldn't be mixed in with g2. secondly, for g2, we have scalars, vectors, bivectors, and
> versors. there's too much implied stuff, like capitil letters for multivectors. that's fine in
> general, but at least define the bivector as like a * (reject_a b), or something, give names,
> even if they aren't used. also, there seems to be subscripts for components, but I'd rather
> explictly see the grade projection symbols.

## Context

- Read first: `book/docs/cheat-sheet-2d.rst` and `cheat-sheet-3d.rst`; the task that built them,
  `tasks/archive/2026/11/20/book-formula-cheat-sheets-2d-3d.md` (each operation is a chain of
  partial bindings: the 𝒢ₙ form, then by kind of argument, then named components, then
  coordinates); `tasks/reference/book-outline.md` ("Reference cards", "Current reading order");
  `CLAUDE.md` "Math notation for readers" and "Book: one name per operation".
- The cards sit in an unnumbered "Reference cards" toctree in `book/docs/index.rst`, whose
  opening text says "Two reference cards come first".
- Both cards carry a "Draft … voice pass is pending" note; the prose is agent-drafted.
- Related: `tasks/spell-out-basis-blades-as-vector-products.md` proposes writing `e_12` as
  `1 * e_1 * e_2` where the blade is a value. If it runs first, this rewrite uses that form.

## What the card does today (line numbers of `cheat-sheet-2d.rst`, 2026-11-22)

**The 𝒢ₙ lines are the first line of nearly every chain.** Geometric product (45–47), grade
projection (67–68), the reverse (80–83), magnitude (96), the inverse (110, for "a vector, a
blade, a versor"), the dot product (123–125), the wedge (142–143), projection and rejection
onto a blade (179–181), reflection (201–202), the dual (252), and all of "Also in gacalc" but
its first two rows (309–312). `cheat-sheet-3d.rst` repeats the same lines word for word.

**The names block (28–38) defines by coordinates only, and leaves these implied:**

- No scalar is named. `m`, `m_1`, `m_2` (scaling) and `θ` appear where they are first used.
- `B = B_{12} * e_12` and `R = r_0 + r_{12} * e_12` are given components but no construction;
  nothing says a bivector is what two vectors span, or that a versor is a product of vectors.
- "Capital letter = multivector" is never said. `A` is "any multivector"; `B` is the named
  bivector in the 𝒢₂ lines and *any second multivector* in the 𝒢ₙ lines (`A · B`, `A ∧ B`,
  "onto a blade `B`").
- `R` is the versor, and `R_a^b(v)` is the rotation it performs; `\vec{r}(v; θ)` is the
  rotation by an angle. `u`, `v` of the reciprocal frame are introduced in its own section.
- In `cheat-sheet-3d.rst`, `T` is both the trivector and the translation `T_b`.

**Subscripted components** stand in for grade parts: `A_0`, `A_1`, `A_2`, `A_{12}` (69–71,
86–87, 256, 305–306), `B_{12}` (35, 98, 113, 132, 255), `r_0`, `r_{12}` (36, 85, 98, 114). The
grade projection section (65–71) defines `⟨A⟩_r` *from* those subscripts, the reverse of what
the request asks.

## Proposed shape

A draft for the maintainer to correct; the names are suggestions.

**𝒢ₙ page** (`book/docs/cheat-sheet-gn.rst`, decision 1). Its own names: `A`, `B` are any multivectors, `⟨A⟩_r` the grade-`r` part, a
*blade* a wedge of vectors, `I` the unit pseudoscalar. Then every 𝒢ₙ line listed above, once.
The 𝒢₂ and 𝒢₃ cards cite it and start each chain at "by kind". The space card gets the same
named-by-kind block, with a trivector `T = a ∧ b ∧ c` (decision 3).

**𝒢₂ names, by kind:**

| kind | name | defined as |
|---|---|---|
| scalars | `m`, `θ`, and the coordinates `a_1, a_2, …` | plain numbers |
| vectors | `a`, `b`, `v` | `a = a_1 * e_1 + a_2 * e_2`, likewise `b`, `v` |
| bivector | `B` | `B = a ∧ b = a * rej_a(b) = (a_1 * b_2 − a_2 * b_1) * e_1 * e_2` |
| versor | `R` | `R = a * b = ⟨R⟩_0 + ⟨R⟩_2`, with `⟨R⟩_0 = a · b` and `⟨R⟩_2 = a ∧ b` |
| any element | `A` | `A = ⟨A⟩_0 + ⟨A⟩_1 + ⟨A⟩_2` |
| unit of area | `I` | `I = 1 * e_1 * e_2` |

`a * rej_a(b) = a ∧ b` is the card's own wedge row (146) and
`book/docs/bootstrap-product.rst`'s `eq-bootstrap-dot-wedge-proj-rej`, so the definition cites
a taught equation. A name is defined even when no formula below uses it.

**Parts by grade projection.** Examples of the rewrite:

| today | proposed |
|---|---|
| `\tilde{R} = r_0 − r_{12} * e_12` | `\tilde{R} = ⟨R⟩_0 − ⟨R⟩_2` |
| `\tilde{A} = A_0 + A_1 * e_1 + A_2 * e_2 − A_{12} * e_12` | `\tilde{A} = ⟨A⟩_0 + ⟨A⟩_1 − ⟨A⟩_2` |
| `|B| = |B_{12}|` | `|B| = |a_1 * b_2 − a_2 * b_1|` |
| `|R| = \sqrt{r_0^2 + r_{12}^2}` | `|R| = \sqrt{⟨R⟩_0^2 + |⟨R⟩_2|^2}` |
| `B^{-1} = −(1 / B_{12}) * e_12` | `B^{-1} = −B / |B|^2` |
| `A^{+} = A_0 + A_{12} * e_12` | `A^{+} = ⟨A⟩_0 + ⟨A⟩_2` |
| `(A_0)^{*} = −A_0 * e_12` | `⟨A⟩_0^{*} = −⟨A⟩_0 * e_1 * e_2` |

The grade projection section then states `⟨A⟩_r` as the primitive and gives the coordinates of
each part through the named vectors, not through `A_{12}`. A vector's coordinates `a_1`, `a_2`
keep their subscripts (decision 2).

**Name clashes to remove on the way:** the generic second multivector in the 𝒢ₙ section
against the bivector `B` (one of them needs another letter if both stay on one page), and in
space the trivector `T` against the translation `T_b`.

## Plan

1. Write `book/docs/cheat-sheet-gn.rst`; cut the 𝒢ₙ lines from the plane card and the space card.
2. Rewrite the plane card's names block and every row that uses a subscripted part.
3. The same for the space card.
4. Update `book/docs/index.rst`'s opening text and toctree, and the "Reference cards" entry of
   `tasks/reference/book-outline.md`.
5. Gate: `make docs` (builds HTML + PDF and runs `tools/check_math_overflow.py`); read the
   rendered cards.

## Decisions

William Emerison Six <billsix@gmail.com>, 2026-11-22:

1. **The 𝒢ₙ formulas get their own page**, `book/docs/cheat-sheet-gn.rst`, first in the
   "Reference cards" toctree and cited by both cards (the agent's recommendation). Why: the
   space card repeats the same 𝒢ₙ lines, and a section on the plane card alone would leave them
   duplicated or make the space card point into the plane card.
2. **A vector's coordinates keep their subscripts** (`a_1`, `a_2`). Only the parts of a
   multivector (`A_0`, `A_{12}`, `B_{12}`, `r_0`, `r_{12}`) become grade projections.
3. **The space card gets the same treatment in this task:** the named-by-kind block (bivector
   `B = a ∧ b`, trivector `T = a ∧ b ∧ c`, versor `R = a * b`) and grade projections for parts.

## History

All on 2026-11-22 (William Emerison Six <billsix@gmail.com>).

1. Asked for together with the blade-spelling task; both cards were read and what they leave
   implied was listed, with a draft of the new shape.
2. Three questions went to the maintainer: where the 𝒢ₙ formulas live, whether vector
   coordinates keep subscripts, and whether the space card is included. The answers are the
   Decisions above; the plan gained the new page and the space card.
