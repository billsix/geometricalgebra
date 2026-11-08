# Book: fix the sin(θ) formula and the `pseudoscalar_squared_sign` claim

**Status:** proposed — needs go-ahead (approved in session 2026-11-08; in progress)
**Priority:** 2
**Difficulty:** 1
**Created:** 2026-11-08
**Source:** `tasks/review/2026/11/08/repo-review.md` §3.3

## BLUF

Two statements in the book are wrong in front of a reader. Done means both are corrected, in the
pages' own notation (an explicit `*` on every product, named angles).

## Context

1. **`book/docs/rotation-from-vectors.rst` › "The angle was scaffolding"** displays
   `\sin(\theta) = \frac{\vec{a} \wedge \vec{b}}{|\vec{a}| * |\vec{b}|}`.
   - The right-hand side is a bivector divided by a number, so it is a bivector, not the number
     `sin(θ)`.
   - The faithful statement is `\vec{a} \wedge \vec{b} = |\vec{a}| * |\vec{b}| * \sin(\theta) * e_{12}`.
     `notebooks/levels-of-abstraction.py` defines the signed 𝒢₂ sine the same way, as
     `(a∧b)·e₁₂ / (|a| * |b|)`.
   - The page's point stands: the dot and the wedge *are* the rotation. Its cosine half is right.
2. **`book/docs/blade-square-sign.rst` › "Where this shows up"** says `pseudoscalar_squared_sign(r)`
   "returns precisely the count of flips". The function (`src/gacalc/base.py`, `def
   pseudoscalar_squared_sign`) returns the **sign** `(−1)^(r * (r−1)/2)`, i.e. ±1. The flip count is
   the exponent.

**Rules that apply:** `CLAUDE.md` › "Math notation for readers", and the proof-page conventions in
`tasks/reference/book-outline.md`.

**What this task doesn't do.** These pages still need the maintainer's voice pass, and the wider
§3.2/§3.4 notation and narrative findings are separate. This task fixes only the two errors.

## Plan

- [ ] Restate the sine half of the display as the wedge identity, keeping the cosine half.
- [ ] Say the function returns the sign, with the flip count as its exponent.
- [ ] Check the RST is well-formed. (`make docs` needs the full image; the session image is the lean
  one.)

## Open questions

None.
