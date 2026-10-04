# Reduction to standard position (frame reduction) — a construction theme

*Durable knowledge. States what the theme IS and why it's sound; the work that introduced it is
recorded in `tasks/archive/2026/10/04/reduce-to-standard-position.md` (archived 2026-10-04).*

## What it is

**Reduction to standard position** (synonym: *frame reduction*) computes or justifies a hard
operation by three steps:

1. **Rotate** the figure into a convenient ("standard") frame — typically so one vector lands on a
   coordinate axis (`e₁`) or in a coordinate plane (`e₁₂`).
2. **Do the easy version** there, using only operations already trusted in that frame (a 2D
   projection, a known 90° rotation, reading off a coordinate).
3. **Rotate the result back** by the inverse rotation.

It is the geometric-algebra form of the classic "place it in standard position, WLOG" move a
student meets for angles and conics. The primary/canonical definitions in gacalc stay the
Hestenes-derived ones (`project = (A·B)B⁻¹`, etc.); the standard-position versions are **deliberate
duplicates** that build understanding and cross-check the canonical formula.

## The rotations are ELEMENTARY plane rotations — NOT versors (this is the whole point)

The rotate-to-standard-position step uses **elementary coordinate-plane rotations** — the
high-school 2D rotation `(x, y) ↦ (x cosθ − y sinθ, x sinθ + y cosθ)` applied to one coordinate
plane at a time, leaving the perpendicular component alone ("break the vector into its components,
rotate the plane, add the axis component back"). It does **not** use versors or the geometric-product
sandwich `R x R⁻¹`.

This matters: a versor **is** a geometric product, so rotating with a versor and then "bootstrapping"
the geometric product from projection/rejection would be **circular**. An elementary plane rotation is
trusted from precalculus, independently of the GA product, so the bootstrap is genuinely non-circular.
(An earlier draft used versors because that machinery already existed in the Lean tree; the maintainer
corrected it — 2026-09-30.)

## Naming and the prime convention

The theme is "reduction to standard position." The derived-operation variants carry an **`SP` / `_sp`
suffix** in both languages — Lean `projectSP` / `rejectSP` (with `alignSP` / `unalignSP`), Python
`project_sp` / `reject_sp` — the stand-in for a prime (`'` is not a legal Python identifier
character, and primed Lean names read badly inside `simp only` lists). The intent is the prime of the
matrix-math proof `multivariate-math/proofs/crossproduct.tex`, which primes the successively
transformed vectors (`a'`, `a''`, `b''`, …): "the same object, reached by the derived route." The
elementary plane rotations themselves are `rotXY` / `rotXZ` / `rotYZ`. (The theme was informally
called "bootstrapping" during design; that term was dropped. The naming note originally said Lean
would use primes; the suffix was chosen when the Lean definitions were written, 2026-10-04.)

## The archetype (the pattern to imitate)

`multivariate-math/proofs/crossproduct.tex` (hand-written LaTeX, not code) derives the cross product
exactly this way: rotate `a` onto the x-axis by composing plane rotations (`:70-173`), apply the
**same** rotation to `b` (`:177-182`), compute with trusted 2D steps in the aligned frame
(`:228-332`), compose the **inverse** rotations to bring the result back (`:335-417`), and rescale
(`:419-434`). The 2D/3D building blocks (`Rotate2D90`, `Rotate3DToXY`, …) are in
`multivariatebasics.tex`.

## Why it is sound (and not circular)

The method is valid because **projection and rejection commute with a plane rotation** (are
rotation-equivariant). This is machine-checked in `proofs/GacalcProofs/StandardPosition.lean`:

- `proj_rotXY_equivariant` / `proj_rotXZ_equivariant`: `proj (R a) (R b) = R (proj a b)` for a plane
  rotation `R` (`rotXY`/`rotXZ`, when `cos² + sin² = 1`, proved via `rotXY_preserves_dot`).
- `vecReject_rotXY_equivariant`: the same for the vector rejection `b − proj_a b`.

Equivariance is exactly the statement "doing it in the rotated frame and rotating back = doing it in
place," so you may **WLOG** rotate `b` to a coordinate axis, compute, and rotate back. The explicit
alignment `rotate_b_to_e1` composes `rotXY` (zeroing `b_y`) then `rotXZ` (zeroing `b_z`) to send `b`
to `|b|·e₁` — the standard position — with the `(cos, sin)` read off `b`'s coordinates. In that
frame projecting onto `|b|·e₁` is "keep the x-component" (`proj_onto_x_axis`), no product needed —
which is what makes the derived route genuinely elementary, not a rotated copy of the Hestenes formula.

**Non-circular:** the rotations are elementary (precalculus), not the GA product. So one may then
*define* the dot and wedge — and hence the vector geometric product `ab = a·b + a∧b` — from
`project`/`reject`, because `a = a∥ + a⊥` with `a∥` ∥ `b` (⟹ `a∥b = a·b`, scalar) and `a⊥` ⊥ `b`
(⟹ `a⊥b = a∧b`, bivector). The canonical Hestenes formula is proven to agree, so the derived route is
trusted for matching it, not assumed. This yields the grade-1×grade-1 product; the
arbitrary-multivector product needs bilinear extension.

## The full bootstrap arc

Reduction to standard position is not a one-off trick — it is the **non-circular foundation** gacalc's
whole rotation/geometry stack builds on, bottom-up:

1. **Three elementary coordinate-plane rotations** — `rotXY`, `rotXZ`, `rotYZ` — are the base. Each is
   the high-school 2-D rotation applied to one coordinate plane (recombine two components, leave the
   third), trusted from precalculus and **independent of the geometric product** (not a versor, not the
   vector→vector "MVP rotate").
2. **From them, via reduction to standard position, the GA operations are derived.** Rotate the figure
   into the standard frame, do the elementary version there, and — for a *vector* result — rotate it
   back by the inverse rotations (a *scalar* result is rotation-invariant, so it needs no rotate-back).
   This yields project, reject, the geometric product `ab = a·b + a∧b`, and dot/wedge — each proved
   equal to its canonical (Hestenes) form — and the cross product, whose step-lemmas are proven but not
   yet assembled into the equality (`tasks/lean-cross-standard-position-capstone.md`).
3. **Then a GENERAL rotation can be defined from project/reject** — which are themselves derived from
   the three plane rotations in step 1. The Python `transforms.projection_rotation` (rotate "from vec1
   to vec2") is exactly this: a general rotation built from projection, no geometric product
   presupposed. The arc closes: **3 plane rotations → project/reject (+ product/cross/dot/wedge) →
   general rotation**, nothing circular (elementary rotations, not the product or a versor, sit underneath).

**One reduce-to-2-D tool, many operations, a uniform 3 rotations.** Bringing *both* 3-D vectors into the
e₁e₂ plane takes 3 rotations (one vector onto `e₁`, the other swung into the plane), after which *every*
operation is elementary 2-D. This uniform 3-rotation reduction is the general tool — the maintainer's
deliberate choice to run everything through one mechanism. A given operation may need fewer:
**project/reject minimally need only 2 rotations** (the target vector on an axis — the `rotate_b_to_e1`
form proved below). The 3rd rotation is what makes the frame fully 2-D for operations that need *both*
vectors reduced (e.g. the cross product); it is not a requirement of project/reject.

## What is proven

The whole arc is machine-checked across four Lean files, all gate-verified (`make lean` green,
`sorry`-free).

**Base — elementary plane rotations, equivariance, and the product** (`StandardPosition.lean`):

- The plane rotations `rotXY`/`rotXZ` (procedures on the components), their linearity
  (`rotXY_smul`/`rotXY_sub`/`rotXZ_smul`) and orthogonality (`rotXY_preserves_dot`/`rotXZ_preserves_dot`,
  when `cos²+sin²=1`).
- Equivariance — the justification: `proj_rotXY_equivariant`, `proj_rotXZ_equivariant`,
  `vecReject_rotXY_equivariant`.
- Explicit alignment: `rotXY_aligns_xy` (`b ↦ (k,0,b₃)`), `rotXZ_aligns_xz` (`(k,0,b₃) ↦ (m,0,0)`),
  `rotate_b_to_e1` (the composite `b ↦ |b|·e₁`, with `k`,`m` supplied via their squares) and
  `rotate_b_to_e1_magnitude` (the same stated with the actual magnitudes `k = |b's xy-part|`,
  `m = |b|`).
- The product from projection/rejection: `mul_proj_eq_dot` (`a (proj_a b) = (b·a)·1`) and
  `mul_eq_proj_dot_add_reject_wedge` (`a b = (a·b)·1 + a∧b`) — "project+reject build the product,"
  versor-free.
- **The derived route equals the canonical one, as one theorem:** `projectSP a b` (`alignSP` — the
  two rotations with `(cos, sin)` read off `b`, `xyMagnitude` — then keep the aligned `a`'s
  x-component, then `unalignSP`) satisfies `projectSP_eq_proj` (`= proj b a`, for a vector `b` off the
  z-axis and nonzero; `a` any multivector), via `proj_onto_x_axis` (`proj (m·e₁) v = (v₁,0,0)`),
  `alignSP_self` (`alignSP b b = |b|·e₁`), the equivariance lemmas, and the inverses
  `rotXY_inv`/`rotXZ_inv` (negated sine undoes a plane rotation). `rejectSP = a − projectSP` gives
  `rejectSP_eq_vecReject` and `rejectSP_eq_reject` (= Hestenes `reject b a` for vectors).
- The Python twin (`src/gacalc/standardposition.py`, `project_sp`/`reject_sp`) is the procedure
  `projectSP` transcribes — same rotations, same `(cos, sin)`, keep-the-x-component — and is asserted
  equal to canonical `projected_onto`/`rejected_away_from` in `tests/test_standardposition.py`.
- Supporting lemmas in their homes: `AlgebraLaws.mul_sub`, `Sandwich.sandwich_sub`.

**The uniform 3-rotation tool** (`CrossStandardPosition.lean`): `rotYZ` (the third plane rotation,
e₂e₃ about `e₁`) + its toolkit (`rotYZ_smul`/`rotYZ_sub`/`rotYZ_preserves_dot`/`rotYZ_vec`/
`rotYZ_fixes_e1`, and the `rotXZ_sub`/`rotXY_vec`/`rotXZ_vec` companions); `reduceToPlane`
(`rotYZ ∘ rotXZ ∘ rotXY`) with `reduceToPlane_a_on_e1` (`a ↦ |a|·e₁`) and `reduceToPlane_b_in_plane`
(reduced `b` has `.c3 = 0` — so **both** vectors are in the e₁e₂ plane); equivariance of all three
operations under all three rotations (`proj_rotYZ_equivariant`, `vecReject_rotXZ/YZ_equivariant`,
`cross_rotXY/XZ/YZ_equivariant`); and the elementary 2-D evals in the reduced frame — `proj_reduced`,
`vecReject_reduced`, `cross_reduced` (`cross (|a|·e₁) (b₁,b₂,0) = (0,0,|a|·b₂)`). project/reject/cross all
run through the one 3-rotation frame uniformly.

**Step 3 — the general rotation from project/reject** (`ProjectionRotation3D.lean`):
`projRotation f t v = (project_{f∧t} v)·f̂·t̂ + reject_{f∧t} v` (mirrors the Python
`transforms.projection_rotation`) — defined from project/reject + the product (itself from
project/reject), so non-circular; no versor. It carries from→to (`projRotation_carries_from_to`,
`projRotation f t f = (|f|/|t|)·t`) and fixes the ⊥ part (`projRotation_perp`), closing the arc.
Its two deep properties:

- **Isometry** (`projRotation_isometry`, `normSq (projRotation f t v) = normSq v`, for nondegenerate
  `f`, `t`). `magnitude² = normSq` (`normSq_mul_vec`, `|Ma|² = |a|²|M|²`) squares away every
  `1/√(normSq f·normSq t)` once the two unit scalars are pulled out of the in-plane term as one
  `smul (1/(|f||t|))`, and the in-plane×⊥ cross term is killed structurally by orthogonality
  (`inplane_perp_reject`, `project_perp_reject`), not by `ring` — no Lagrange needed. Scaffold:
  `normSq_add` (polarization), `normSq_add_of_orthogonal` (Pythagoras), `normSq_mul_vec`,
  `inplane_perp_reject`, `project_perp_reject`, `plane_pythagorean` (`|project|²+|reject|² = |v|²`,
  on `project_add_reject`).
- **Route-equivalence** (`projRotation_eq_sandwich`, `projRotation f t v = sandwich (versorFromVectors
  f t) v` — route P = route V, the Python docstring's "both agree", for `f`, `t` not antiparallel).
  The √ never appears: the scalar part `|f||t|·1` of `R = t·f + |f||t|` is pulled out abstractly via
  `R R⁻¹ = 1` rather than expanded, so every identity reduces to a √-free rational core about the
  bivector `t∧f`. Three structural lemmas carry it: `versor_mul_project_eq` (in-plane `P` anticommutes,
  `R P = P R̃`), `versor_mul_reject_comm` (the ⊥ part commutes, so the sandwich fixes it), and
  `normalizeVec_mul_versor_eq_reverse` (`f̂ t̂ = R̃ R⁻¹`, from the bisector identities `t̂ R = h`,
  `f̂ h = R̃` in `Rotation3D.lean`).

**2D specialization — the degenerate base case** (`ProjectionRotation2D.lean`): the same
`projRotation` and the identical triple (`projRotation_carries_from_to` / `projRotation_isometry` /
`projRotation_eq_sandwich`) in 𝒢₂. There the `f∧t` plane **is** the whole space, so `reject_{f∧t} v = 0`
(`reject_plane_eq_zero`) and the rotation collapses to the pure rotor action `v·f̂·t̂`
(`projRotation_eq_vec_mul`) — the 3D construction's degenerate base case, side by side with it. The same
structural √-handling applies: the one √-bearing identity stays confined to `key_reverse_sq`
(`|f||t|·R̃² = |R|²·(f t)`, closed by `linear_combination` against `(|f||t|)² = |f|²|t|²`). The 2D
isometry needs only `normSq f, normSq t ≠ 0` (it comes straight from `normSq_mul_three_vec` + unit
`f̂`/`t̂`, independent of route-equivalence).

**Not yet done:** the cross-product capstone (`tasks/lean-cross-standard-position-capstone.md`), and
the maintainer's voice pass on the drafted book page + notebook
(`tasks/proof-projection-book-voice-pass.md`, which also holds the remaining book/notebook ideas).

## Where it belongs

Lean first (it certifies the equivalence), then the "Geometry 2" book (`book/docs/`, the reduce-to-
coordinates exemplar — proof pages in separate `.rst`, calculations in the companion notebooks), then
optionally duplicate suffixed definitions in the code. See `tasks/archive/2026/10/04/reduce-to-standard-position.md` for the decision log and the
harvested per-subsystem ideas list.

## See also

- `tasks/reference/lean-ga-proof-architecture.md` — the sandwich/projection lemmas this builds on.
- `tasks/notebook-dot-wedge-projection-demo.md`, `tasks/reference/dot-wedge-projection-rejection.md`
  — the related "dot = projected product, wedge = rejected" result.
- `tasks/archive/2026/10/04/lean-proof-rotation-from-scratch.md` (archived) — the **other route to a general rotation**: the versor
  sandwich `R v R⁻¹`. It is **product-based** (a versor *is* a geometric product), so it is NOT a
  bootstrap of the product — complementary to, and contrasted with, route P here (general rotation from
  project/reject, which presupposes no product). Both reduce 3-D to 2-D; only the coordinate-frame route
  is non-circular as a foundation.
- `tasks/reference/unit-bivector-and-rotors.md` — rotors as the general rotation (the versor / route-V view).
