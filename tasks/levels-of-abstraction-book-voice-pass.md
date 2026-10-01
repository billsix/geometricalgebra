# Voice pass + figures for the "Levels of Abstraction" book page

**Status:** proposed — maintainer's own voice pass (not agent-blocked)
**Priority:** 7
**Difficulty:** 3
**Created:** 2026-10-01 (William Emerison Six <billsix@gmail.com>)

## BLUF

The `levels-of-abstraction` book page and its notebook were drafted (and the notebook runs) as
Phase 5 of the now-archived per-type sine/dot/wedge work. The prose and figures are a draft in the
agent's voice; this task is the **maintainer's voice pass** — rewrite the prose in his teaching voice
and add real figures — before the page is considered book-ready. "Done" = the maintainer has revised
the `.rst`/notebook prose and the `.. note:: Draft` banner is removed.

## What exists (drafted 2026-10-01)

- `book/docs/notebooks/levels-of-abstraction.py` — runnable jupytext notebook: dot and wedge of two
  vectors at three rungs (coordinate → fixed-grade `⟨ab⟩₀`/`⟨ab⟩₂` → coordinate-free
  `inner_product`/`outer_product`), all proved equal; coordinate-free shown dimension-independent
  (𝒢₂ and 𝒢₃); and the sine/cosine family (`cosine`, unsigned `abs_sin`, signed 𝒢₂ `sine`,
  `cos²+sin²=1`).
- `book/docs/levels-of-abstraction.rst` — wraps the notebook, in the `index.rst` toctree after
  `geometric-product`. Carries a `.. note::` marking it a draft.

## Remaining (maintainer)

- Voice pass over the `.rst` + notebook markdown (teaching voice, per `tasks/reference/book-outline.md`).
- Real figures where the draft leaves them implicit.
- A `make docs` build check, then remove the `.. note:: Draft` banner.

## Context / cross-refs

- The completed implementation + decisions: `tasks/archive/2026/10/01/per-type-fixed-grade-dot-wedge-sine-cosine.md`.
- Equivalence proofs the page rests on: `proofs/GacalcProofs/TrigEquiv.lean`; tests
  `tests/test_fixed_grade_dot_wedge.py`, `tests/test_signed_sine.py`.
- The theme: `tasks/reference/reduction-to-standard-position.md` (duplicate-definition); the
  "verify, don't derive" pedagogy in `tasks/reference-doc-lean-workflow-and-proof-notebooks.md`.
