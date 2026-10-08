# Book proof: rotate from the direction of a to the direction of b (2D, standard position)

**Status:** proposed — needs go-ahead
**Priority:** 5
**Difficulty:** 4
**Created:** 2026-10-08 (William Emerison Six <billsix@gmail.com>)

## BLUF

A **new page** `book/docs/proof-rotate-from-a-to-b.rst`, in the Part I toctree right after
`book/docs/proof-rotate.rst` ("Proof: Rotate"), that derives how to
**rotate the direction of :math:`\vec{a}` onto the direction of :math:`\vec{b}`** in 2D — using what the
reader already has (rotation in the :math:`e_{12}` plane by an angle, from "Proof: Rotate"), by
**reduction to standard position**, exactly the change-of-frame style the projection proof uses for
"rotate :math:`\vec{b}` onto :math:`e_1`". Deliverables: the prose proof, a set of per-step **ePiX
diagrams** (with :math:`\vec{a}` and :math:`\vec{b}` **not** unit length, as in the rotate chapter), and
a **Lean proof** (check for an existing one; if none matches, make it and verify). **Do not start yet —
this task is the write-up spec.**

This is the **angle-based** construction (it reads cosines and sines off the vectors, never naming the
angle — just like `proof-rotate.rst` and `proof-projection.rst`). It is distinct from the **angle-free**
geometric-product version in `tasks/book-rotation-from-vectors-no-angle.md` (where :math:`\hat a\hat b`
*is* the rotor); that is the later "you don't even need the angle" payoff. Keep both.

## The construction (the maintainer's, 2026-10-08)

Given we already know how to rotate in the :math:`e_{12}` plane by an angle (from "Proof: Rotate"),
rotate from :math:`\vec{a}` to :math:`\vec{b}` by **three steps**, written in **order of application —
right to left** (the composition reads right-to-left, per the book's compose-not-nest convention):

1. **Rotate :math:`\vec{a}` onto :math:`e_1`** — the elementary plane rotation whose cosine and sine are
   read off :math:`\vec{a}` (:math:`\cos = \vec{a}_x/|\vec{a}|`, :math:`\sin = -\vec{a}_y/|\vec{a}|`). Call
   it :math:`R_{\vec{a}}^{e_1}`. It carries :math:`\vec{a}` to :math:`|\vec{a}|\,e_1`, and carries
   :math:`\vec{b}` to :math:`\vec{b}' = R_{\vec{a}}^{e_1}(\vec{b})`.
2. **Rotate :math:`e_1` onto :math:`\vec{b}'`** — using :math:`\vec{b}'`'s *relative* cosine and sine
   (:math:`\cos = \vec{b}'_x/|\vec{b}'|`, :math:`\sin = \vec{b}'_y/|\vec{b}'|`). Call it
   :math:`R_{e_1}^{\vec{b}'}`.
3. **Undo step 1** — :math:`\big(R_{\vec{a}}^{e_1}\big)^{-1}` (rotate back).

So the rotation from :math:`\vec{a}` to :math:`\vec{b}` is

.. the composition (right-to-left): first align a to e_1, rotate to b' in that frame, then un-align.

:math:`R_{\vec{a}}^{\vec{b}} = \big(R_{\vec{a}}^{e_1}\big)^{-1} \circ R_{e_1}^{\vec{b}'} \circ R_{\vec{a}}^{e_1}`.

**This is reduction to standard position applied to rotation** (`tasks/reference/reduction-to-standard-position.md`):
align :math:`\vec{a}` to the standard frame, do the easy rotation there (read off :math:`\vec{b}'`),
un-align. Applied to :math:`\vec{a}` it yields a vector of length :math:`|\vec{a}|` in :math:`\vec{b}`'s
direction (magnitudes don't matter — only directions set the rotation, as the rotate chapter says).

**Presentation (decided — maintainer, 2026-10-08): show the 3-step method, then collapse it to a
simple coordinate-based formula.** Present the full 3-step change-of-frame first (it teaches the method
that generalizes to 3D and mirrors the projection proof), then show that in 2D the plane rotations
commute, so the sandwich :math:`\big(R_{\vec{a}}^{e_1}\big)^{-1} \circ R_{e_1}^{\vec{b}'} \circ
R_{\vec{a}}^{e_1}` collapses to a **single rotation by the angle from :math:`\vec{a}` to :math:`\vec{b}`**
(:math:`\beta-\alpha`) — written as a closed coordinate formula with **no angle named**: the cosine and
sine of that angle are read straight off the two vectors,

   :math:`\cos(\beta-\alpha) = \dfrac{\vec{a}\cdot\vec{b}}{|\vec{a}|\,|\vec{b}|}`, &nbsp;
   :math:`\sin(\beta-\alpha) = \dfrac{\vec{a}_x\vec{b}_y - \vec{a}_y\vec{b}_x}{|\vec{a}|\,|\vec{b}|}`

(the dot and the 2-D wedge over the magnitudes), so the whole rotation is
:math:`\vec{v} \mapsto \cos(\beta-\alpha)\,\vec{v} + \sin(\beta-\alpha)\,\vec{r}(\vec{v};\pi/2)` — one
tidy formula in :math:`\vec{a}`'s and :math:`\vec{b}`'s coordinates. (Verify the exact signs/arrangement
when writing; the Lean proof is where to pin them down.) That collapse is the punchline.

## Diagrams (ePiX, a and b NOT unit length)

One per step, mirroring the projection proof's `sp1`–`sp5`. Add figure sources under
`book/figures/epix/` (suggest a shared `_rotate_ab_scene.py` with fixed non-unit :math:`\vec{a}`,
:math:`\vec{b}`, their angles, and :math:`\vec{b}'`), rendered by `tools/render_epix_figures.py`:

1. **Goal** — :math:`\vec{a}` and :math:`\vec{b}` (both non-unit), showing we want to swing
   :math:`\vec{a}`'s direction onto :math:`\vec{b}`'s.
2. **Step 1** — after :math:`R_{\vec{a}}^{e_1}`: :math:`\vec{a}` on the x-axis (:math:`|\vec{a}|\,e_1`),
   :math:`\vec{b}` carried to :math:`\vec{b}'` (faint originals dashed, like `sp3`).
3. **Step 2** — rotating :math:`e_1` onto :math:`\vec{b}'` by its relative angle.
4. **Step 3** — undo step 1; :math:`\vec{a}`'s image lands on :math:`\vec{b}`'s direction (length
   :math:`|\vec{a}|`).
5. **(Optional) Result** — :math:`\vec{a}` rotated onto :math:`\vec{b}`'s direction, in the original
   frame.

Follow the figure conventions: every argument by keyword and every binding typed
(`check_epix_keywords` gate), labels placed cleanly beside their items (see
`tasks/archive/2026/10/08/fix-epix-figure-label-placement.md`), :math:`\theta` for angles.

## Prose conventions to apply (non-negotiable — `tasks/reference/book-outline.md`)

- Build on the already-defined `r(v; θ)` rotation from `proof-rotate.rst`; don't drop new machinery.
- Name the rotations from→to: :math:`R_{\vec{a}}^{e_1}`, :math:`R_{e_1}^{\vec{b}'}`, and the undo as the
  **explicit inverse** :math:`\big(R_{\vec{a}}^{e_1}\big)^{-1}`.
- **Compose, don't nest** (write the composition, read right-to-left), as the maintainer did above.
- **Symbols match the diagrams** — use :math:`\vec{a}`, :math:`\vec{b}`, :math:`\vec{b}'` (the book's
  vector names), :math:`\theta` for the angle.

## Lean (part of this task)

1. **Check first** for an existing proof of this. Relevant 𝒢₂ material (`proofs/GacalcProofs/`):
   - `Rotation2D.lean`: `rot θ`, `rot_add`, `rot_uvec` (`rot θ (uvec α) = uvec (α+θ)`),
     `rot_from_to` (`polar rb φb = (rb/ra)·rot(φb−φa)(polar ra φa)`), `fullAngleRotorFromTo` /
     `fullAngleRotorFromTo_carry` (the full-angle rotor from α to β carries `uvec α` to `uvec β`).
   - `StandardPosition2D.lean`: `rotPlane c s` (the elementary plane rotation read off coordinates),
     `rotPlane_aligns` (`b ↦ |b|·e₁`), `rotPlane_inv`.
   - `ProjectionRotation2D.lean`: `projRotation f t v` (from project/reject) — a *different* route.
   None of these is the exact **3-step `rotPlane` sandwich** `(R_a^{e_1})⁻¹ ∘ R_{e_1}^{b'} ∘ R_a^{e_1}`.
2. **If none matches, make it** (likely in `Rotation2D.lean` or a small new file, 𝒢₂,
   `GacalcProofs.G2`): define the 3-step composition with the `(cos, sin)` read off `a` and `b'`, and
   prove it carries `a`'s direction to `b`'s direction — e.g. that it equals `rot (β−α)` (using
   `rot_add` for the commuting collapse) and/or that it sends `a` to `(|a|)·unit(b)`. Build on `rotPlane`
   / `rot` rather than re-deriving.
3. **Verify:** `make lean` → `[lean] OK`, `sorry`-free. (Run `proofs/check.sh` in the image, not a
   rebuilding make target.) Harvest the result into `tasks/reference/reduction-to-standard-position.md`.

## Decisions (maintainer, 2026-10-08)

1. **New page**, not an appended section — `book/docs/proof-rotate-from-a-to-b.rst`, added to the Part I
   toctree parallel to `proof-rotate.rst` / `proof-projection.rst`.
2. **Show the 3-step method, then collapse it to a simple coordinate-based formula** (see the
   "Presentation" note above — the collapse to a single rotation by the a→b angle, with
   :math:`\cos`/:math:`\sin` read off the vectors, is the punchline).

No open questions remain blocking the write-up.

## Related

- `book/docs/proof-rotate.rst` — the rotation by an angle this builds on; it comes right before.
- `book/docs/proof-projection.rst` — the change-of-frame proof whose style this mirrors (rotate
  `b` onto `e_1`).
- `tasks/reference/reduction-to-standard-position.md` — the theme (align → do the easy op → un-align).
- `tasks/book-rotation-from-vectors-no-angle.md` — the complementary **angle-free** (geometric-product)
  version; keep both.
- `tasks/projection-proof-use-rotate-from-a-to-b.md` — the follow-up (reuse this in the projection
  proof), blocked on this task's completion + approval.
