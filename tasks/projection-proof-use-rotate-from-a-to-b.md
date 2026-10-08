# Follow-up: recast the projection proof to use "rotate from a to b" (once it exists)

**Status:** blocked — on `tasks/book-proof-rotate-from-a-to-b.md` being done AND maintainer-approved
**Blocked on:** the rotate-from-direction-a-to-direction-b proof section + its Lean existing and
approved (the maintainer approves the new section before this starts).
**Recheck:** `ls book/docs/proof-rotate-from-a-to-b.rst` (or the section in `proof-rotate.rst`) exists
and the maintainer has said go; then this is unblocked.
**Priority:** 7
**Difficulty:** 4
**Created:** 2026-10-08 (William Emerison Six <billsix@gmail.com>)

## BLUF

Once the "rotate from the direction of :math:`\vec{a}` to the direction of :math:`\vec{b}`" proof
exists and is approved (`tasks/book-proof-rotate-from-a-to-b.md`), **see whether
`book/docs/proof-projection.rst` can be recast to use it** — i.e. express "rotate :math:`\vec{b}` onto
:math:`e_1`" as an instance of the general rotate-from-a-to-b (with the "to" direction being
:math:`e_1`), so the projection proof *builds on* the rotation proof instead of re-deriving the single
plane rotation inline. This is a **see-if-it-improves-it** task: do it only if it makes the projection
proof clearer; if it adds indirection, leave the projection proof as is and record why.

## Why this is a "maybe", not a given

- The projection proof's rotation is the special case "rotate :math:`\vec{b}` onto :math:`e_1`" —
  exactly `R_{\vec{b}}^{\vec{e}_1}` — which is already what the rotate-from-a-to-b proof's **step 1**
  is. So the projection proof could cite that result rather than re-deriving `R_{\vec{b}}^{\vec{e}_1}`
  from `r(v; θ)`.
- **But** the projection proof is currently self-contained and pedagogically clean; pulling in the
  full from-a-to-b machinery (which is itself a 3-step sandwich) to get its one-rotation special case
  may be *more* indirection, not less. Judge after reading both side by side.

## What to check / do (when unblocked)

- Read `book/docs/proof-projection.rst` "Rotating :math:`\vec{b}` onto the x-axis" against the new
  rotate-from-a-to-b proof. Does citing the general result simplify it (fewer formulas, one shared
  rotation lemma) without making the reader chase a forward reference?
- If yes: recast the section to reference the rotation proof; repoint the Lean citation if the shared
  rotation lemma now lives there; keep the figures.
- If no: leave it; add a one-line cross-reference ("this is the special case `to = e_1` of
  :doc:`proof-rotate-from-a-to-b`") and note in this task why a full recast wasn't worth it.
- Gates: `make docs` (and `make lean` if any Lean citation moved) green.

## Related

- `tasks/book-proof-rotate-from-a-to-b.md` — the prerequisite (must exist + be approved first).
- `book/docs/proof-projection.rst` — the proof to possibly recast.
- `tasks/reference/reduction-to-standard-position.md` — the shared theme both proofs sit under.
