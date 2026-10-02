# Reduction to standard position: define project/reject from trusted simpler ops via change-of-frame

**Status:** in progress — Lean + Python + book draft done; the book still needs the maintainer's voice pass
**Priority:** 6
**Difficulty:** 7
**Created:** 2026-09-30 **Updated:** 2026-09-30 (William Emerison Six <billsix@gmail.com>)

> **Naming:** "bootstrap" was rejected; the theme is **reduction to standard position** (synonym:
> *frame reduction*). Derived-operation variants carry a **prime** — Lean would write `proj'`/`reject'`
> alongside canonical `proj`/`reject`, Python uses a `_sp` suffix (`'` is not a legal identifier
> character). The prime echoes `crossproduct.tex`, which already primes the transformed vectors
> (`a'`, `a''`, `b''`…): a prime means "the same object, reached by the derived route."

## BLUF

This established **reduction to standard position** — defining or justifying a hard operation from
already-trusted simpler ones by a change-of-frame (rotate the figure into a standard frame, do the
easy version, rotate back) — as a named theme of the project. Scope for this first pass was
**`project` and `reject` only**: once you have those you can split any vector `a = a∥ + a⊥` relative
to `b`, whence `ab = a·b + a∧b` (the geometric product of two vectors) and thence a **general rotation
defined from project/reject**. This is the bootstrap arc the theme is really for: **3 elementary plane
rotations → project/reject (+ product/cross/dot/wedge via reduce-to-2-D) → general rotation** (step 3 =
e.g. `transforms.projection_rotation`), nothing circular. The
rotations are **elementary coordinate-plane rotations, not versors** — using a versor would be
circular, since a versor is itself a geometric product and the point is to bootstrap the product
from operations trusted independently of it. Delivered in Lean (the justification + explicit
alignment), Python (`project_sp`/`reject_sp`), a reference doc, a `CLAUDE.md` pointer, and a drafted
book page + notebook. What remains is the maintainer's voice pass on the book draft.

## Decisions (2026-09-30, William Emerison Six <billsix@gmail.com>)

1. **Lean first** — the definitions and justification were proven in Lean before the book or code,
   so Lean certifies the equivalence to the Hestenes formula.
2. **Scope = `project` and `reject` only.** They suffice: `a∥ = project(a onto b)` is parallel to `b`
   (so `a∥ b = a·b`, a scalar), `a⊥ = reject(a from b)` is perpendicular (so `a⊥ b = a∧b`, a
   bivector), hence `ab = a·b + a∧b` — the grade-1×grade-1 product; the arbitrary-multivector product
   would need bilinear extension on top.
3. **Name = "reduction to standard position"**; derived variants carry a prime (see the naming note).
4. **Scan everything** (Lean, book, code, notebooks); the Sphinx book is the exemplar of the
   reduce-to-coordinates style.
5. **Elementary plane rotations, not versors** (maintainer correction — see History). The rotate step
   uses the high-school 2D rotation applied to one coordinate plane at a time, so the bootstrap of the
   geometric product from projection/rejection stays non-circular.

## The archetype — multivariate-math/proofs (read-only inspiration)

`/foo/opt/multivariate-math/proofs/crossproduct.tex` (hand-written LaTeX) derives the cross product
by change-of-frame: rotate `a` onto the x-axis by composing plane rotations (`:70-173`), apply the
same maps to `b` (`:177-182`), compute with trusted 2D steps in the aligned frame (`:228-332`),
compose the inverse rotations to bring the result back (`:335-417`), and rescale (`:419-434`). The
2D/3D building blocks (`Rotate2D90`, `Rotate3DToXY`, …) are in `multivariatebasics.tex`.

## What was delivered

**Lean** (`proofs/GacalcProofs/StandardPosition.lean`, gate-verified `sorry`-free):
- `rotXY`/`rotXZ` — elementary plane rotations as procedures on a vector's components (rotate the two
  in-plane components, leave the perpendicular one); their linearity (`rotXY_smul`/`rotXY_sub`/
  `rotXZ_smul`) and orthogonality (`rotXY_preserves_dot`/`rotXZ_preserves_dot`, when `cos²+sin²=1`).
- The justification: `proj_rotXY_equivariant`/`proj_rotXZ_equivariant`/`vecReject_rotXY_equivariant`
  — projection and rejection commute with a plane rotation.
- The explicit alignment: `rotXY_aligns_xy` (`b ↦ (k,0,b₃)`), `rotXZ_aligns_xz` (`(k,0,b₃) ↦ (m,0,0)`),
  `rotate_b_to_e1` (the composite `b ↦ |b|·e₁`), and `rotate_b_to_e1_magnitude`, which states it in
  terms of the actual magnitudes (`k = magnitude (vec b₁ b₂ 0)`, `m = magnitude (vec b₁ b₂ b₃)`) via
  `magnitude² = normSq` — no raw `√` or coordinate sums; the abstract-square `rotate_b_to_e1` is the
  algebra engine underneath.
- The payoff (versor-free): `mul_proj_eq_dot` (`a (proj_a b) = (b·a)·1`) and
  `mul_eq_proj_dot_add_reject_wedge` (`a b = (a·b)·1 + a∧b`), the wedge half reusing `plane_eq_wedge`.
- Supporting general lemmas `AlgebraLaws.mul_sub` and `Sandwich.sandwich_sub`.

**Python** (`src/gacalc/standardposition.py`): `project_sp`/`reject_sp` implement the same elementary
rotations; `tests/test_standardposition.py` (5 tests, passing) assert they equal the canonical
`projected_onto`/`rejected_away_from`, numerically and symbolically.

**Docs:** the reference doc `tasks/reference/reduction-to-standard-position.md` (the theme, the
`crossproduct.tex` archetype, the non-circularity argument, the naming convention); a `CLAUDE.md`
bullet accepting primed standard-position duplicates alongside the canonical Hestenes definitions;
and the repo scan `tasks/adhoc/reduce-to-standard-position/` (`ideas.md` + the raw `data/scan.txt`).

**Book (DRAFT, for the maintainer to refine):** `book/docs/proof-projection.rst` (the proof page, in
the maintainer's voice, modelled on `proof-rotate.rst`) + `book/docs/notebooks/proof-projection.py`
(the calculation notebook, which runs `project_sp` and was verified to execute), both registered in
`projection.rst`'s toctree. Figure spots are left as `.. TODO`; not built with `make docs`.

## History — the versor detour (why the correction)

The first Lean cut justified standard position with the **versor sandwich** (reusing the existing
`Sandwich`/`versorFromVectors` machinery): equivariance under a sandwich, primed `proj'`/`reject'`
via a conjugate-back round-trip. The maintainer flagged this as circular for the bootstrap goal — a
versor is a geometric product, so it cannot be used to *build* the geometric product — and asked for
elementary coordinate-plane rotations instead. The versor version was replaced with the
`rotXY`/`rotXZ` construction above, and the versor-specific round-trip lemmas were removed
(`sandwich_sub` and `mul_sub` were kept as generally-useful lemmas).

## Overlap (cross-referenced, not duplicated)

- `tasks/lean-proof-rotation-from-scratch.md` — reduces 3D to 2D via the versor sandwich, a
  complementary approach.
- `tasks/notebook-dot-wedge-projection-demo.md` — dot = projected product, wedge = rejected (proved
  in `tasks/reference/dot-wedge-projection-rejection.md`); a related display task.

## Remaining

- **FIXED 2026-10-01 — `tests/test_standardposition.py` `ty` failure (was CI RED).** `project_sp`/
  `reject_sp` are typed `-> MultiVectorBase`, but the test typed `_coords`'s param and two `difference`
  locals as `Vector`, giving 5 `ty` diagnostics (`invalid-argument-type` ×3, `invalid-assignment` ×2)
  that slipped past `make test` (pytest only) and failed CI's `make format` (`ty`) job. Fixed by typing
  `_coords(v: MultiVectorBase)` and `difference: MultiVectorBase` (option c — narrowing the API return
  types would have needed narrowing the `MultiVectorBase` inputs too, a bigger change). `make format`
  now green. Unrelated to the per-type-sine work; flagged by the maintainer.
- The maintainer's voice pass on the book draft (and real figures, and a `make docs` build check).
- Optional follow-ons from the ideas list: a 3D projection-rejection book page (B2), cross-links to
  `rotate.rst` (B3). No decisions block them.
- **Full 3-rotation reduction (maintainer, 2026-10-01).** The 3D Lean proof (`StandardPosition.lean`)
  uses only **2** elementary rotations — `rotXY` then `rotXZ` (`rotate_b_to_e1`) — to bring the *onto*
  vector `b` to `|b|·e₁`. That is correct and minimal **for project/reject**: projecting onto the `e₁`
  axis only needs `b` on that axis; you then read `a`'s `e₁` component, and `a`'s `e₂`/`e₃` components
  are irrelevant, so `a` never needs to be brought into the `e₁e₂` plane. The archetype
  `multivariate-math/proofs/crossproduct.tex` uses a **3rd** rotation (`f_{b''}^{xy}`, after 2 that put
  `a` on the x-axis) precisely because the **cross product** reduces *both* vectors to a full 2-D
  (xy-plane) computation — a cross-product need, not a project/reject one.
  The maintainer wants the **uniform 3-rotation reduction** anyway — one reusable tool that brings
  *both* vectors into the `e₁e₂` plane (add `rotYZ`, a rotation in the `e₂e₃` plane about the fixed `e₁`
  axis), after which **every** operation is an elementary 2-D one. The deliberate choice is generality
  over minimality: project/reject keep their 2-rotation form, but the same 3-rotation tool also gives the
  **cross product** and underpins step 3 below. **DONE 2026-10-02** (`proofs/GacalcProofs/CrossStandardPosition.lean`,
  `make lean` green/sorry-free): `rotYZ` + toolkit, `reduceToPlane` (`reduceToPlane_a_on_e1` +
  `reduceToPlane_b_in_plane` — both vectors into the `e₁e₂` plane), equivariance of proj/reject/cross under
  all three rotations, and the 2-D evals `proj_reduced`/`vecReject_reduced`/`cross_reduced` — project,
  reject AND cross all derived through the one uniform 3-rotation frame.
- **The bootstrap arc / step 3 — general rotation from project/reject.** The theme's real payoff:
  **3 elementary plane rotations → project/reject (+ product/cross/dot/wedge via reduce-to-2-D) → a
  general rotation defined from project/reject** (the Python `transforms.projection_rotation`, "rotate
  from vec1 to vec2", is exactly this). Non-circular throughout — the elementary rotations, not the
  geometric product or a versor, sit underneath. Contrast the **versor-sandwich** route to a general
  rotation (`tasks/lean-proof-rotation-from-scratch.md`), which is product-based. **DONE 2026-10-02**
  (`proofs/GacalcProofs/ProjectionRotation.lean`, `make lean` green): `projRotation` defined from
  project/reject, with `projRotation_carries_from_to` (carries from→to, the defining property) and
  `projRotation_perp` (⊥ part fixed). **Isometry DONE 2026-10-02** (`projRotation_isometry`,
  `normSq (projRotation f t v) = normSq v`, `make lean` green/sorry-free): `magnitude² = normSq`
  (`normSq_mul_vec`) squares away every `1/√(|f||t|)` once the unit scalars are pulled out as one `smul`,
  and the in-plane×⊥ cross term dies by orthogonality (`inplane_perp_reject`/`project_perp_reject`), not
  `ring` — Lagrange not needed. Scaffold all sorry-free (`normSq_add`, `normSq_add_of_orthogonal`,
  `normSq_mul_vec`, `inplane_perp_reject`, `project_perp_reject`, `plane_pythagorean`). **Route-equivalence
  DONE 2026-10-02** (`projRotation_eq_sandwich`, `projRotation f t v = sandwich(versorFromVectors f t) v`,
  `make lean` green/sorry-free): the √ never appears — `R`'s scalar part `|f||t|·1` is pulled out abstractly
  via `R R⁻¹ = 1`, so each piece is a √-free core about `t∧f`: `versor_mul_project_eq` (in-plane `R P = P R̃`),
  `versor_mul_reject_comm` (⊥ `R Rⱼ = Rⱼ R`), `normalizeVec_mul_versor_eq_reverse` (`f̂ t̂ = R̃ R⁻¹`, from the
  `Rotation3D.lean` bisector identities). The bootstrap arc + both deep properties are fully machine-checked.
  Full arc: `tasks/reference/reduction-to-standard-position.md`.
