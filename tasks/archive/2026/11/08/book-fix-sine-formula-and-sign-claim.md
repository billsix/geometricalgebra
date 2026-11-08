# Book: fix the sin(θ) formula and the `pseudoscalar_squared_sign` claim

**Created:** 2026-11-08 · **Completed:** 2026-11-08
**Source:** `tasks/review/2026/11/08/repo-review.md` §3.3

## What was wrong

1. **`book/docs/rotation-from-vectors.rst` › "The angle was scaffolding"** displayed
   `\sin(\theta) = \frac{\vec{a} \wedge \vec{b}}{|\vec{a}| * |\vec{b}|}`. The right-hand side is a
   bivector, not the number sin(θ).
2. **`book/docs/blade-square-sign.rst` › "Where this shows up"** said `pseudoscalar_squared_sign(r)`
   "returns precisely the count of flips". It returns the sign `(−1)^(r * (r−1)/2)` (±1); the flip
   count is the exponent.

## What changed

1. The sine half of the display is now the wedge identity,
   `\vec{a} \wedge \vec{b} = |\vec{a}| * |\vec{b}| * \sin(\theta) * e_{12}`, next to the unchanged
   cosine half. A one-sentence note says the wedge is a multiple of `e_{12}`, whose number is the
   signed area.
2. The sentence now says the function returns the sign itself, +1 or −1, and that the flip count is
   the exponent.

Both edits follow `CLAUDE.md`'s notation rules (an explicit `*`, named angles).

The pages' maintainer voice pass, and the review's wider §3.2/§3.4 book findings, remain separate.

## Verification

Both files parse with docutils. The only errors were for Sphinx-only roles and directives (`:doc:`,
`:meth:`, `toctree`). `make docs` was not run: the session's nested image is the lean one, without
the Sphinx/TeX stack.
