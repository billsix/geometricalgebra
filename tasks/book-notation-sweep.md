# Book: the notation sweep

**Status:** proposed — needs go-ahead (approved in session 2026-11-09; in progress)
**Priority:** 4
**Difficulty:** 3
**Created:** 2026-11-09
**Source:** `tasks/review/2026/11/08/repo-review.md` §3.4

## BLUF

Apply `CLAUDE.md`'s "Math notation for readers" rules to every book page and notebook: an explicit
`*` on every product, `\cdot` only for the dot product, named angles, and primes as `b'_1`. Use one
basis-vector spelling, plain `e_1` (decided 2026-11-09, recorded in `book-outline.md`). Done means
every violation listed in review §3.4 is fixed, and a grep for the patterns finds none.

## Context

The list is in review §3.4: juxtaposition in `geometric-product`, `proof-rotate-from-a-to-b`,
`proof-projection`, `proof-cross` and `levels-of-abstraction`; `12 \cdot 6^{-1} \cdot 5`; an unnamed
`\cos^2 + \sin^2`; three basis spellings; the `sp2` alt text; `translate(b)`; the README's
unspaced math.

## Plan

- [ ] Fix each listed case, then a global `\vec{e}_i` / `\vec{e_i}` → `e_i`.
- [ ] Fix the notebooks' markdown and comment math.
- [ ] Gate: the grep patterns from §3.4 return nothing; the notebooks run; `ruff`.

## Open questions

None.
