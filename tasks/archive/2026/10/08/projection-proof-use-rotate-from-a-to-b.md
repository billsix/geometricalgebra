# Follow-up: recast the projection proof to use "rotate from a to b"

**Status:** done — 2026-10-08 (approved and recast; gates green; normalized pre-squash)
**Priority:** 7
**Difficulty:** 4
**Created:** 2026-10-08 (William Emerison Six <billsix@gmail.com>)

## BLUF

A "see-if-it-improves-it" follow-up to `book-proof-rotate-from-a-to-b`: the projection proof's rotation
is the special case "rotate `b` onto `e₁`" (`R_b^{e₁}`), which is exactly step 1 of the new
rotate-from-a-to-b proof. The question was whether `proof-projection.rst` reads more clearly citing that
than re-deriving the plane rotation inline. **Verdict: yes** — once the maintainer approved
rotate-from-a-to-b, the recast removed a ~55-line duplicate derivation and made the book cumulative (the
align-to-`e₁` move is established once, in the earlier chapter, and reused). `make docs` green.

## What was done

- **`book/docs/proof-projection.rst`** — the "Rotating `b` onto the x-axis" section no longer re-derives
  the rotation from `r(v; θ)`. It cites :doc:`proof-rotate-from-a-to-b` ("rotating a vector onto the
  x-axis is its step 1"), applied to `b`: names `R_b^{e₁}`, gives the cos/sin read off `b`, the result
  `R_b^{e₁}(b) = |b|·e₁`, and the inverse `R_{e₁}^{b}`. The later "Why we are allowed" / "Now the
  algebra" / 3D sections were untouched — they already used only `R_b^{e₁}`, `R_{e₁}^{b}`, `P_{e₁}`,
  `|b|·e₁`, all still introduced.
- **`book/docs/proof-rotate-from-a-to-b.rst`** — flipped its two **forward-references** to the later
  projection chapter into self-contained grounding: the intro states the standard-position trick without
  depending on projection (a one-line forward *teaser* to :doc:`projection` kept), and **step 1 now
  fully derives** "swing `a` onto `e₁`" from `proof-rotate`'s `r(v; θ)` (cos/sin read off `a`, arithmetic
  to `|a|·e₁`) — making it the authoritative home of the align move that projection cites.
- **Verification** — `make docs` green (both pages render, the cross-reference resolves, figures embed).

## Why it worked out (the judgment)

The chapter order supports it: rotate-from-a-to-b is in the **rotate** chapter (book order #20),
projection is #24, so projection reusing the earlier result is forward-consistent — and the old
back-references in rotate-from-a-to-b were themselves forward-references to a later chapter, now fixed.
The feared downside (pulling in the full 3-step sandwich just for its one-rotation special case) did not
materialize, because projection cites only step 1's align move, not the whole construction.

## History (commit chronology, branch `rotateFromAToB` — for the squash)

1. `2704af1` *added tasks to rotate from a to b* — filed this follow-up (then blocked on
   `book-proof-rotate-from-a-to-b` + approval), alongside that task.
2. `d91837a` *rewrite project proof* — the recast: `proof-projection.rst` cites the align move,
   `proof-rotate-from-a-to-b.rst` made self-contained (forward-refs flipped, step 1 fully derived); and
   removed this task doc from its working path (archiving).

## Related

- `tasks/archive/2026/10/08/book-proof-rotate-from-a-to-b.md` — the prerequisite proof this reuses.
- `book/docs/proof-projection.rst`, `book/docs/proof-rotate-from-a-to-b.rst` — the two recast pages.
- `tasks/reference/reduction-to-standard-position.md` — the shared theme both proofs sit under.
