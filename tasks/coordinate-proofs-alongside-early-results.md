# Early in the book, show results in coordinates too — not only the coordinate-free statement

**Status:** proposed — needs go-ahead (a book-outline principle + an audit-and-fill pass)
**Priority:** 5
**Difficulty:** 5
**Created:** 2026-10-08 (William Emerison Six <billsix@gmail.com>)

## BLUF

The maintainer's rule (2026-10-08, verbatim): *"Especially early on in the book, proofs via
coordinates are desirable, rather than let's say, stating just that composition of 2D rotations
is commutative. You can absolutely state that and prove that, but also, show the equivalence by
way of coordinates. Obviously, as the book moves towards coordinate free, that should stop."*

So in **Part I** a result is presented twice: the coordinate-free statement (and its proof, where
the book proves it) **and** a coordinate verification the reader can check by hand or in the
companion notebook. The coordinate half tapers off as the book turns coordinate-free (Part I's
later chapters, all of Part II). "Done" = the principle is written into
`tasks/reference/book-outline.md`, every Part I result currently asserted without a coordinate
check has one (prose, or the page's notebook, or both), **the 2D-rotations-commute claim has a
named Lean theorem the book cites** (maintainer's addition, 2026-10-09), and `make docs` +
`make lean` are green.

## Context

- **This sharpens, not contradicts, an existing principle.** `tasks/reference/book-outline.md` ›
  "Coordinate-free is the destination; coordinates are scaffolding" already says "for teaching and
  proofs we reduce to coordinates" and routes coordinate calculations to notebooks. The new rule
  adds: a coordinate-free *statement* on its own is not enough early on — put the coordinate form
  next to it, and say when to stop. It also matches the outline's §E/§F lines "OK to reduce to
  coordinates for this" and "show **in coordinates** that the geometric-product implementation is
  equivalent".
- **The library-side rule is different and stays.** `CLAUDE.md` › "Coordinates only when needed"
  governs *Lean theorem statements and Python signatures* (objects in, scalars only in the body).
  That is about the code's API shape, not about what the book shows a student; the two coexist.
- **The structural home for the coordinate half:** the book's three-media split (prose / figures /
  notebooks). A coordinate check is naturally a **notebook cell** (sympy, symbolic coordinates,
  both sides simplified to equal) under the page, with the prose giving the by-hand version when
  it is short. `book/docs/notebooks/levels-of-abstraction.py` already does exactly this for dot
  and wedge (coordinate → fixed-grade → coordinate-free, all proved equal) and is the model.

## Audit — Part I claims currently stated without a coordinate check (2026-10-08)

Found by `grep -niE "commut|compos|equivalent|the same"` over `book/docs/*.rst`; extend the audit
when picking this up (the pages are still being written).

1. **"In 2D, rotations commute"** — `book/docs/proof-rotate-from-a-to-b.rst`, section "The
   collapse". Asserted and used (the sandwich collapses to its middle turn), never shown. The
   coordinate version is short: apply the `r(v; θ)` formula of `proof-rotate.rst` twice in each
   order and expand with the angle-addition identities — both orders give
   `cos(θ₁ + θ₂)`, `sin(θ₁ + θ₂)`; the notebook does it with sympy `simplify`.
   **Lean (maintainer, 2026-10-09: make a theorem for it as part of this task).** The proofs
   already hold the *engine* but not the *statement*: `rot_add` in
   `proofs/GacalcProofs/Rotation2D.lean` (`rot θ (rot φ v) = rot (φ + θ) v`, angle form) and
   `rotPlane_comp` in `proofs/GacalcProofs/RotateFromTo2D.lean` (composition of two `(cos, sin)`
   plane rotations is the angle-sum rotation; its doc comment *says* "in particular rotPlane
   rotations commute" but no theorem states it). Add the two one-line corollaries, named so the
   book can cite them:
   - `rot_comm (θ φ : ℝ) (v : G2) : rot θ (rot φ v) = rot φ (rot θ v)` in `Rotation2D.lean`
     (by `rot_add` twice and `add_comm`) — the angle-based form `proof-rotate.rst` teaches;
   - `rotPlane_comm (c1 s1 c2 s2 : ℝ) (v : G2) : rotPlane c1 s1 (rotPlane c2 s2 v) =
     rotPlane c2 s2 (rotPlane c1 s1 v)` in `RotateFromTo2D.lean` (by `rotPlane_comp` twice and
     `ring`, no unit constraint needed) — the `(cos, sin)` form the collapse actually uses; then
     have `rotPlane_conj_collapse`'s doc comment point at it as the reason the sandwich collapses.
   Both follow the house style (objects in: `v : G2`, no `IsVector` needed since both sides read
   only `c1`/`c2` — same as `rot_add`). The book's "The collapse" paragraph then cites
   `rotPlane_comm` by name next to the existing `RotateFromTo2D.lean` citation (line ~125), and
   `tasks/reference/lean-ga-proof-architecture.md`'s what-is-proven list gets the two names.
2. **"Either order lands on the same corner, so addition commutes"** —
   `book/docs/vector-addition.rst` (TODO prose; the `add3` figure). Coordinates:
   `(a_1 + b_1, a_2 + b_2) = (b_1 + a_1, b_2 + a_2)` because real addition commutes — one line,
   and it is the first place a student sees "the picture says it; the coordinates confirm it".
   Coordinate with `tasks/vector-addition-translate-partial-binding.md` (same page).
3. **`geometric-product.rst`** — the rotor `R = cos(θ) + sin(θ) e_12` is shown to equal the
   coordinate formula ("equals both the coordinate formula …"); verify the page actually *expands*
   `a (cos(θ) + sin(θ) e_12)` into components rather than asserting it.
4. **`projection.rst` / `proof-projection.rst`** — the outline (§F) already demands the coordinate
   equivalence of the geometric-product projection and the rotate-then-take-components one;
   check it is present, not just promised.

Pages where the coordinate half should **stop** (taper): `blade-square-sign.rst` (general-`n`
sign argument — inherently coordinate-free), `dual.rst`, `defining-g2.rst`, and all of Part II.
Write that boundary into the outline so the taper is a decision, not drift.

## Plan

1. `tasks/reference/book-outline.md`: under "Pedagogical principles", extend the coordinate-free
   bullet with the rule above (quote the maintainer), name the taper boundary, and point at
   `levels-of-abstraction.py` as the pattern. Also add a line to "Notation & prose conventions
   for proof pages": *a Part I proof page states the result, proves it, and then verifies it in
   coordinates (prose if ≤ a few lines, else the notebook).*
2. Fill the audit items 1–4 (prose + notebook cells), in the page's existing voice; items 1 and 3
   are small, 2 rides with the vector-addition task, 4 is a check.
3. Lean: add `rot_comm` and `rotPlane_comm` (audit item 1), cite them from the book page and the
   proof-architecture reference doc; `make lean` (needs the full image, `USE_LEAN=1`).
4. `make docs`; the notebooks' new cells must execute (`nb_execution_raise_on_error = True`
   already makes a failing cell fail the build).

## Open questions

None — the rule and the taper point are the maintainer's; the audit list is the agent's and
grows as pages are written.
