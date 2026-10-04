# Reduction to standard position: define project/reject from trusted simpler ops via change-of-frame

**Status:** done — archive owed (the book voice pass continues in
`tasks/proof-projection-book-voice-pass.md`)
**Priority:** 6
**Difficulty:** 7
**Created:** 2026-09-30 **Updated:** 2026-10-04 (William Emerison Six <billsix@gmail.com>)

> **Naming:** "bootstrap" was rejected; the theme is **reduction to standard position** (synonym:
> *frame reduction*). Derived-operation variants carry an **`SP` / `_sp` suffix** in both languages —
> Lean `projectSP`/`rejectSP`, Python `project_sp`/`reject_sp` — the stand-in for the prime that
> `crossproduct.tex` puts on its transformed vectors (`a'`, `a''`, `b''`…): "the same object, reached by
> the derived route." (The note originally said Lean would use primes; the suffix was chosen when the
> Lean definitions were written, 2026-10-04 — primed names read badly inside `simp only` lists.)

## BLUF

This established **reduction to standard position** — defining or justifying a hard operation from
already-trusted simpler ones by a change-of-frame (rotate the figure into a standard frame, do the
easy version, rotate back) — as a named theme of the project, and delivered it for **`project` and
`reject`**: Lean (the justification, the explicit alignment, the product from project/reject, and the
single theorem `projectSP_eq_proj` that the derived route equals the Hestenes one), Python
(`project_sp`/`reject_sp`), a reference doc, a `CLAUDE.md` pointer, and a drafted book page + notebook.
The rotations are **elementary coordinate-plane rotations, not versors** — a versor is itself a
geometric product, so using one would make the bootstrap circular. The arc it opens is **3 elementary
plane rotations → project/reject (+ product/cross/dot/wedge via reduce-to-2-D) → a general rotation
defined from project/reject** (`transforms.projection_rotation`). "Done" = all of that gate-verified
(`make lean` green, tests passing, the notebook executes); the maintainer's voice pass on the book
draft is its own task.

## Context

The durable account — what the theme is, why it is sound and non-circular, the archetype, the naming
convention, and the per-lemma "what is proven" — is `tasks/reference/reduction-to-standard-position.md`;
this file is the work record. The archetype is `multivariate-math/proofs/crossproduct.tex`
(github.com/billsix/multivariate-math), a hand-written derivation of the cross product by composing
plane rotations, computing in the aligned frame, and composing the inverse rotations back.

## Decisions (William Emerison Six <billsix@gmail.com>)

1. **Lean first** (2026-09-30) — the definitions and justification were proven in Lean before the book
   or code, so Lean certifies the equivalence to the Hestenes formula.
2. **Scope = `project` and `reject` only** (2026-09-30). They suffice: `a∥` ∥ `b` gives `a∥ b = a·b`
   (scalar), `a⊥` ⊥ `b` gives `a⊥ b = a∧b` (bivector), hence `ab = a·b + a∧b` — the grade-1×grade-1
   product; the arbitrary-multivector product needs bilinear extension on top.
3. **Name = "reduction to standard position"**; derived variants carry the suffix (naming note above).
4. **Scan everything** (Lean, book, code, notebooks); the Sphinx book is the exemplar of the
   reduce-to-coordinates style.
5. **Elementary plane rotations, not versors** (2026-09-30, maintainer correction — see History).
6. **A uniform 3 rotations, generality over minimality** (2026-10-01). project/reject minimally need
   only 2 rotations (bring the target vector onto `e₁`, read off a component); the cross product needs
   both vectors in a full 2-D frame, a 3rd rotation (`rotYZ`). Every operation runs through the one
   3-rotation `reduceToPlane` tool rather than per-operation rotation counts, as `crossproduct.tex`
   already does.
7. **The in-frame step is "keep the x-component", literally** (2026-10-04). The first `projectSP` and
   `project_sp` projected in the aligned frame by calling the Hestenes `proj`/`projected_onto` — so the
   "no geometric product" claim in the docstrings and book draft was not true of the code. Both now
   keep the aligned `a`'s x-component; the one new lemma `proj_onto_x_axis` (`proj (m·e₁) v =
   (v₁,0,0)`, any multivector `v`) plus `alignSP_self` close `projectSP_eq_proj` as before.

## What was delivered

Machine-checked across four Lean files (`make lean` green, `sorry`-free), with the per-lemma account in
the reference doc's "What is proven" — this is a pointer, not a copy.

- **Base** (`StandardPosition.lean`): `rotXY`/`rotXZ` and their linearity, dot-preservation and
  inverses; projection/rejection equivariance; the `b ↦ |b|·e₁` alignment (`rotate_b_to_e1`,
  `rotate_b_to_e1_magnitude`); the product from projection/rejection
  (`mul_eq_proj_dot_add_reject_wedge`), versor-free; and — 2026-10-04 — `projectSP`/`rejectSP`
  (`alignSP` → keep the x-component → `unalignSP`) with **`projectSP_eq_proj`** and
  `rejectSP_eq_reject`, the single theorem that the derived route equals the Hestenes one (closing the
  corpus review's "proven by ingredients only" finding).
- **Uniform 3-rotation tool** (`CrossStandardPosition.lean`): `rotYZ` + `reduceToPlane` bring both
  vectors into the e₁e₂ plane; equivariance of proj/reject/cross under all three rotations; the
  reduced-frame evaluations. The cross *capstone* (equality assembled) is
  `tasks/lean-cross-standard-position-capstone.md`.
- **Step 3 — a general rotation from project/reject** (`ProjectionRotation3D.lean`): `projRotation`
  carries from→to, fixes ⊥, is an isometry, and equals the versor sandwich (`projRotation_eq_sandwich`);
  the 𝒢₂ degenerate base case in `ProjectionRotation2D.lean`.
- **Python** `src/gacalc/standardposition.py` (`project_sp`/`reject_sp`, the procedure `projectSP`
  transcribes) + `tests/test_standardposition.py` (5 tests, numeric + symbolic equality to
  `projected_onto`/`rejected_away_from`).
- **Docs:** `tasks/reference/reduction-to-standard-position.md`; the `CLAUDE.md` module bullet and the
  "accepted duplicate-definition theme" rule; `proofs/README.md`.
- **Book (DRAFT):** `book/docs/proof-projection.rst` + `book/docs/notebooks/proof-projection.py`
  (executes; registered in `projection.rst`'s toctree; figures left as `.. TODO`; not yet built with
  `make docs`). Voice pass → `tasks/proof-projection-book-voice-pass.md`.

## History — the versor detour (why decision 5)

The first Lean cut justified standard position with the **versor sandwich** (reusing the existing
`Sandwich`/`versorFromVectors` machinery). The maintainer flagged this as circular for the bootstrap
goal — a versor is a geometric product, so it cannot be used to *build* the geometric product — and
asked for elementary coordinate-plane rotations instead. The versor version was replaced with the
`rotXY`/`rotXZ` construction; the versor-specific round-trip lemmas were removed (`sandwich_sub` and
`mul_sub` were kept as generally-useful lemmas).

## Harvested ideas list (from the 2026-09-30 repo scan, deleted with this archive)

The scan's done items are the deliverables above. Still-open ideas, each now owned elsewhere:

- **B2** a 3D projection-rejection book page by the literal e₁-alignment chain, **B3** cross-link
  `rotate.rst` as the trusted 2D building block, **N1** a `notebooks/`-side `show_mult` demo of `a`
  rotating to standard position → `tasks/proof-projection-book-voice-pass.md` (follow-ons).
- **C2** a standard-position `cross` in Python (the most faithful port of `crossproduct.tex`) →
  `tasks/lean-cross-standard-position-capstone.md`, open question 2.

## Overlap (cross-referenced, not duplicated)

- `tasks/archive/2026/10/04/lean-proof-rotation-from-scratch.md` — reduces 3D to 2D via the versor
  sandwich; product-based, so complementary to (not a bootstrap like) this route.
- `tasks/notebook-dot-wedge-projection-demo.md` — dot = projected product, wedge = rejected (proved in
  `tasks/reference/dot-wedge-projection-rejection.md`); a related display task.
