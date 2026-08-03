# Port the rotation explanation (and its SVGs) from the mvp book

**Status:** proposed — **needs go-ahead**; not started.
**Priority:** 4
**Difficulty:** 4
**Created:** 2026-08-03 (Bill)

## Goal

Bring the **gist of the rotation explanation** Bill wrote in the *modelviewprojection*
(mvp) book — the high-school-trig **derivation of 2D rotation**, with its SVG
walkthrough — into the gacalc book ("Plotting On Crappy Graph Paper"), adapted to
gacalc's coordinate-free / geometric-product framing.

**These are two separate works, both Bill's** — copying between them is expected and
fine; they are **not** meant to be a single related work, so no derivative-work
gymnastics. (Licensing note under "Assets".)

Maps onto the outline's rotate/geometric-product spine: see
`tasks/reference/book-outline.md` › Part I §E–F and the `rotate` / `geometric-product` /
`proof-rotate` pages.

## Source material (mvp)

Repo: **github.com/billsix/modelviewprojection** (book under `book/docs/`). The rotation
arc is three chapters:

- **`book/docs/ch07.rst` — "Rotations - Demo 07"** — *the one Bill likes, and the whole
  scope of this task.* Its first part derives **rotation about the origin (0,0)** from
  high-school trig using a change-of-frame trick, illustrated by nine of Bill's own SVGs.
  **Port only that part** — it needs no translate.

**Out of scope — anything involving translate (Bill, 2026-08-03).** ch07's closing "Why
it is Wrong" section and all of **ch08** ("Fix Attempt 1") and **ch09** ("Sequence of
Transformations") are about rotating a paddle **around its own center**, which requires
translating to the center first — and gacalc's book isn't dealing with translate yet, at
least not the way Bill envisions it. So **skip** them, and skip the `rotate_around` /
`translate ∘ rotate ∘ translate⁻¹` mapping entirely. Revisit only once translate lands in
the book.

## The explanation to port (ch07's derivation — the gist, step by step)

Faithful summary so the doer knows the pedagogical flow and which figure goes where.
Rotating a point **a** by angle **θ** about the origin:

1. Any point `a = (a_x, a_y)` has a length `r` and an angle `β`, so
   `a = r·(cos β, sin β)`. (fig `rotate-goal.svg` states the goal `r(a; θ)`; `rotate1.svg`
   the length/angle description.)
2. Sine/cosine are preserved under scaling a right triangle, so work on the unit circle
   but remember `r`. Call `a`'s angle `β`; we want to rotate by a *different* angle `θ`.
   (`rotate2.svg`)
3. **First learn to rotate by 90° (π/2).** Rotating `(cos β, sin β)` by π/2 gives
   `(cos(β+π/2), sin(β+π/2))`. (`rotate3.svg`)
4. **Rename** the original unit direction `x'` and the 90°-rotated one `y'` — defer their
   values. (`rotate4.svg`)
5. **Change frame:** in the `x'`/`y'` axes, rotating by θ looks like ordinary unit-circle
   rotation — "turn your head slightly." (`rotate5.svg`, `rotate6.svg`)
6. So `r(a; θ) = r·(cos θ · x' + sin θ · y')`, then re-lengthen to `r`. (`rotate7.svg`,
   `rotate8.svg`)
7. **Now switch from geometry to algebra.** Substitute `x' = (cos β, sin β)`,
   `y' = (cos(β+π/2), sin(β+π/2))`; use the identities `cos(β+π/2) = −sin β`,
   `sin(β+π/2) = cos β`, and `cos β = a_x/r`, `sin β = a_y/r`. The `r`'s cancel and it
   collapses to:
   > **`r(a; θ) = cos θ · a + sin θ · (−a_y, a_x)`**, i.e.
   > **`r(a; θ) = cos θ · a + sin θ · r(a; π/2)`**, where `r(a; π/2) = (−a_y, a_x)`.

That final identity is the whole payoff: a rotation is a blend of the point and its
90°-rotated self.

### The GA bridge gacalc should add (mvp doesn't)

`r(a; π/2) = (−a_y, a_x)` **is multiplication by the unit bivector** `e₁e₂` (the 90°
rotation / dual in 2D). So the derivation lands exactly on
`r(a; θ) = (cos θ + sin θ · e₁e₂)` acting on `a` — **the rotor**. This is the natural
lead-in to gacalc's **geometric product producing a rotation as an action** (outline §E):
mvp stops at the coordinate formula; **gacalc should take the extra step and identify the
90°-rotation with the geometric product by `e₁e₂`.** This is the single most important
adaptation — it turns Bill's trig derivation into the motivation for the geometric
product.

## Where it maps in the gacalc book

- **`book/docs/proof-rotate.rst`** — the full coordinate derivation above (steps 1–7).
  This is precisely the outline's "precalculus-level proof of rotate," and the outline
  says proofs live in their own `.rst`. The SVG walkthrough belongs here.
- **`book/docs/rotate.rst`** — the prose/use: rotate from vec 1 → vec 2 (gacalc's
  headline framing), pointing at the proof. Some hero SVGs (`rotate-goal`, a couple of the
  frame-change figures) can live here for intuition.
- **`book/docs/geometric-product.rst`** — pick up the GA bridge: the 90° rotation *is*
  `× e₁e₂`, so `cos θ + sin θ·e₁e₂` is the rotor; this defines the geometric product as
  the rotation operator (outline §E).
- Companion notebook `book/docs/notebooks/rotate.py` (already stubbed) — verify the
  coordinate formula and the rotor agree, symbolically, in gacalc (the "show it's
  equivalent in coordinates" step).

## Assets to copy

Copy the SVGs into gacalc's `book/docs/_static/` (mirror mvp's `cc0/<author>/` layout).
gacalc's `conf.py` already has `sphinx.ext.imgconverter` (inkscape), so SVGs render into
the **PDF** as well as HTML — no new tooling.

**Core (ch07 derivation — Bill's own work):**
`_static/cc0/williamesix/rotate-goal.svg`, `rotate1.svg` … `rotate8.svg` (9 files,
confirmed present on disk).

**Unit-circle (third-party, CC0 — keep attribution):**
`_static/cc0/Stephan_Kulla/Sinus_und_Kosinus_am_Einheitskreis_1.svg` (Stephan Kulla,
CC0; the `_static/cc0/` path is the attribution convention mvp uses — preserve it).

**Skip (out of scope):** the "why wrong" / fix figures
(`_static/incorrectrotate-forwards-*.svg`, `_static/rotate-sloppy-forwards-*.svg`) — they
illustrate the translate-dependent "rotate around a center" story. Also skip the demo
screenshots (`_static/screenshots/demo0{7,8,9}.png`, `_static/demo07.png`) — mvp's paddle
app, irrelevant to gacalc.

## Adaptation notes (where the two books differ — read before porting)

1. **No `inlinetex` in gacalc.** mvp's ch07 uses **37** `:inlinetex:` / `.. inlinetex::`
   directives; gacalc deliberately dropped inlinetex (see
   `tasks/reference/book-and-docs-pipeline.md`). **Convert every one to standard
   `:math:` (inline) / `.. math::` (block)** — mathjax renders them in HTML and native
   LaTeX renders them in the PDF. The `align*`/`bmatrix` blocks in ch07 port directly
   into `.. math::`.
2. **Coordinate-free is the destination; coordinates are the scaffold.** Per the outline,
   the coordinate derivation is *appropriate* here because it's a teaching proof — keep
   it in `proof-rotate.rst`, and make the coordinate-free rotor the headline in
   `rotate.rst`/`geometric-product.rst`.
3. **gacalc's rotate is from vec 1 → vec 2, not an angle.** ch07 derives the θ-based
   formula; frame it as the *proof of what rotation is*, then connect to the from→to API
   (`plane_rotation`, `rotor_from_vectors`).
4. **Prose license.** ch07 carries a GFDL-1.3 header; gacalc's code is LGPL-2.1 and its
   **book-prose license isn't decided yet** — see Open question 2. Bill's own figures are
   his to relicense; the CC0 Stephan Kulla asset stays CC0 with attribution regardless.
5. `figure`/`figclass`/`no-scale` directives port over unchanged; drop the mvp `:term:`
   cross-references (gacalc's glossary, if any, differs) or re-point them.

## Steps (when green-lit)

1. Copy the SVG assets into `book/docs/_static/cc0/...` (preserve the author subdirs).
2. Draft `proof-rotate.rst`: port ch07 steps 1–7 with the `rotate*.svg` walkthrough,
   converting all inlinetex → `.. math::`/`:math:`.
3. Add the GA bridge to `geometric-product.rst` (90° = `×e₁e₂` → rotor), and the from→to
   framing + hero figures to `rotate.rst`; wire the `proof-rotate` link.
4. Fill `notebooks/rotate.py`: symbolically confirm `cos θ·a + sin θ·(a·e₁e₂)` equals the
   coordinate formula and the gacalc rotor.
5. Build (`make docs`), verify the SVGs render in **both** HTML and PDF, and the math
   renders (mathjax HTML / native LaTeX PDF).

## Open questions

1. **gacalc book-prose license?** Undecided. Needed before publishing ported prose (code
   is LGPL-2.1). What should the book prose carry — GFDL (matching mvp), CC-BY, or other?
2. **Proof placement:** coordinate derivation in `proof-rotate.rst` with the rotor bridge
   in `rotate.rst`/`geometric-product.rst` (my recommendation), or keep the whole thing in
   `rotate.rst`?
