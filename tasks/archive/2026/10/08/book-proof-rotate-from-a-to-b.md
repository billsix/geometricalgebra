# Book proof: rotate from the direction of a to the direction of b (2D, standard position)

**Status:** done — 2026-10-08 (gates green; normalized pre-squash)
**Priority:** 5
**Difficulty:** 4
**Created:** 2026-10-08 (William Emerison Six <billsix@gmail.com>)

## BLUF

A new Part I book page, `book/docs/proof-rotate-from-a-to-b.rst` (after "Proof: Rotate"), deriving how
to **rotate the direction of `a` onto the direction of `b`** in 2D by **reduction to standard
position** — the same change-of-frame style the projection proof uses — then collapsing it to a closed
coordinate formula with no angle named. Delivered as Lean (machine-checked), the prose page, and four
ePiX diagrams with `a`, `b` **not** unit length. This is the **angle-based** construction (reads cos/sin
off the vectors); the **angle-free** geometric-product version (`â b̂` *is* the rotor) stays a separate
later payoff (`tasks/book-rotation-from-vectors-no-angle.md`). The follow-up —
reusing this in the projection proof — is `tasks/projection-proof-use-rotate-from-a-to-b.md`, blocked on
the maintainer's approval. Durable account: `tasks/reference/reduction-to-standard-position.md` ("2D —
rotate from direction `a` to direction `b`").

## The construction

Rotate from `a` to `b` in three steps, written in order of application (right to left):

`R_a^b = (R_a^{e₁})⁻¹ ∘ R_{e₁}^{b'} ∘ R_a^{e₁}`

1. `R_a^{e₁}` — swing `a` onto `e₁` (cos = a_x/|a|, sin = −a_y/|a|, read off `a`); it carries `b` to
   `b' = R_a^{e₁}(b)`.
2. `R_{e₁}^{b'}` — in that frame, rotate `e₁` onto `b'` (cos = b'_x/|b'|, sin = b'_y/|b'|, read off `b'`).
3. `(R_a^{e₁})⁻¹` — undo step 1.

**The collapse (the punchline):** in 2D rotations commute, so steps 1 and 3 cancel around the middle and
the sandwich equals its middle rotation — a single rotation by the `a→b` angle, with cos/sin as
coordinate formulas, no angle named:

`cos θ = (a·b)/(|a||b|)`, `sin θ = (a_x b_y − a_y b_x)/(|a||b|)`,

so `R_a^b(v) = cos θ · v + sin θ · r(v; π/2)`. The two numerators are the dot product and the signed
area. Applied to `a`, it lands on `(|a|/|b|)·b` — `b`'s direction with `a`'s magnitude.

## What was done

- **Lean** — new `proofs/GacalcProofs/RotateFromTo2D.lean` (𝒢₂), registered in `GacalcProofs.lean`,
  built on `StandardPosition2D.lean`'s `rotPlane`: `rotPlane_comp` (composition = angle addition, so
  rotPlanes commute), **`rotPlane_conj_collapse`** (conjugation by a unit `(cos,sin)` = the middle
  rotation), `bprime_coords`, `cs_a_unit`, **`rotateFromTo_collapse`** (3-step sandwich = the single
  coordinate rotation), **`rotateFromTo_carries`** (`a ↦ (|a|/|b|)·b`). `make lean` → `[lean] OK`,
  `sorry`-free. The audit confirmed no prior proof matched the 3-step `rotPlane` sandwich (`Rotation2D`
  had `rot_from_to`/`fullAngleRotorFromTo`, `ProjectionRotation2D` had `projRotation` — different
  routes), so this was new.
- **Book page** `proof-rotate-from-a-to-b.rst` — in `rotate.rst`'s toctree after `proof-rotate`; the
  3-step method as the right-to-left composition with the explicit inverse, then the collapse to the
  coordinate formula; cites the Lean. Conventions: `θ`, `R_{from}^{to}`, compose-don't-nest,
  symbols-match-diagrams.
- **Figures** — `book/figures/epix/_rotate_ab_scene.py` (`a` outside the unit circle, `b` inside —
  non-unit) + `rotate_ab_goal`/`_step1`/`_step2`/`_step3`; rendered, label-placed cleanly, keyword-only
  and typed (`check_epix_keywords` green).
- **Verification** — `make lean`, `make docs` (HTML + PDF, page + four figures embed), `make format`
  all green.

## Decisions (maintainer, 2026-10-08)

1. **New page**, not an appended section (`proof-rotate-from-a-to-b.rst`, parallel to
   `proof-rotate`/`proof-projection`).
2. **Show the 3-step method, then collapse to a simple coordinate-based formula** (the collapse is the
   punchline).
3. **Distinct from the angle-free geometric-product version** — keep both; that one is the later payoff.

## History (commit chronology, `origin/master..HEAD` on branch `rotateFromAToB` — for the squash)

1. `2704af1` *added tasks to rotate from a to b* — filed this task (then proposed) + the follow-up
   `projection-proof-use-rotate-from-a-to-b.md`, cross-linked to the angle-free task.
2. `bc5b32f` *updated tasks* — recorded the two maintainer decisions (new page; show-then-collapse).
3. `59763ee` *implemented rotate from a to b* — the Lean file, the book page + toctree, the four
   figures, the reference-doc harvest; and removed this task doc from its working path (archiving).

## Related

- `book/docs/proof-rotate.rst` — the rotation-by-an-angle this builds on (comes right before).
- `book/docs/proof-projection.rst` — the change-of-frame proof whose style this mirrors.
- `tasks/reference/reduction-to-standard-position.md` — the theme + the harvested account.
- `tasks/book-rotation-from-vectors-no-angle.md` — the complementary angle-free version.
- `tasks/projection-proof-use-rotate-from-a-to-b.md` — the follow-up, blocked on approval.
