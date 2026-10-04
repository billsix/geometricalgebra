# Extend Lean coverage to `transforms`, `standardposition`, `functions`, `g1` (and, later, `gn`)

**Status:** done — archived 2026-10-04. Phases 1–3 delivered (`make lean` green); the former phase 4
(`gn.py`) is not this task's to wait on — it depends on a dimension-general algebra and now lives as
scope in `tasks/lean-general-gn-product-and-hestenes-dot-wedge.md` (deferred, P9). Frames and the 3D
rotor angle theorem were split out into their own tasks (`tasks/lean-frame-coverage.md`, parked;
`tasks/lean-rotor-3d-angle-theorem.md`, proposed).
**Priority:** 5 **Difficulty:** 5 (the finished phases were D4–5 each).
**Created:** 2026-10-04 **Updated:** 2026-10-04 (William Emerison Six <billsix@gmail.com>). **Owner:**
William Emerison Six <billsix@gmail.com>.
**See also:** `tasks/reference/lean-proof-corpus-review-2026-10-04.md` (the coverage map that found these
gaps, §3), `tasks/reference/lean-ga-proof-architecture.md` (how proofs are written here; its coverage map
now has a subsection for these modules), `tasks/reference/lean-for-gacalc.md` (orientation),
`tasks/archive/2026/10/01/lean-coverage-gap-audit.md` (the earlier audit, same method).

## BLUF

The Lean corpus (`proofs/GacalcProofs/`) covered the vector-level math of `base.py`, `vectorcalc.py` and
`measure.py` in 𝒢₂/𝒢₃, but six Python modules were never in the audited surface: `transforms.py`,
`standardposition.py`, `frame.py`, `functions.py`, `g1.py`, `gn.py`. This task brings them in: for each
public math function, either a Lean theorem stating its defining property (objects in, scalars in the
body, objects out), or a recorded decision that it is plumbing with no GA content. "Done" = every
function in the tables below has a theorem name or a "plumbing — no theorem" decision, `make lean`
green, and the architecture doc's coverage map extended. Four of the six modules are covered; `frame.py`
moved to its own (parked) task; `gn.py` moved into the deferred general-`Gn` task.

## Context — how to read this cold

- **What Lean models.** `G1`/`G2`/`G3` are coordinate structs with hand-written `mul`/`wedge`/`reverse`
  (𝒢₁'s and 𝒢₃'s transcribed from the Python `Gn` oracle by `tools/derive_lean_algebra.py`). There is no
  dimension-general algebra. Lean proves identities about its own definitions; the Python is matched by
  formula, by hand (the review's §3 coverage map and its Method section — the definition-parity
  re-derivation via `tools/derive_lean_algebra.py` — are the parity evidence).
- **How a theorem is written here.** Take the object and a grade predicate (`{a : G3} (ha : IsVector a)`),
  conclude about objects; in the body either `obtain ⟨zeros⟩ := ha; simp only [defs, zeros]; ring`
  (polynomial tier) or a structural `rw` chain through the leaf lemmas. Rules: `CLAUDE.md` "Coordinates
  only when needed"; recipes, the hypotheses section and build discipline: `lean-ga-proof-architecture.md`.
  A new file is one topic, suffixed `2D`/`3D` when grade-specific, and must be imported from the root
  module `proofs/GacalcProofs.lean` or it is not built.
- **Build.** `make lean` from the repo root. Inside a nested sandbox run `proofs/check.sh` directly
  against the existing image (recipe in the architecture doc), since `make lean` depends on `image` and
  would rebuild it. A full incremental gate takes 2–5 minutes.

## Phase 1 — `standardposition.py` and `functions.py` (done 2026-10-04)

| Python | Lean |
|---|---|
| `standardposition.project_sp a b` (align `b` to `e₁` by `rotate_in_xy_plane` then `rotate_in_xz_plane`, keep the aligned `a`'s x-component, rotate back) | `projectSP` — the same procedure with the same `(cos, sin)` formulas (`alignSP`/`unalignSP`, `xyMagnitude`) — and **`projectSP_eq_proj`**: `projectSP a b = proj b a` for a vector `b` off the z-axis (`xyMagnitude b ≠ 0`) and nonzero; `a` arbitrary. Proof: keep-the-x-component is `proj (|b|·e₁)` (`proj_onto_x_axis`, `alignSP_self`), both plane rotations are projection-equivariant (already proven) and each is undone by its negated-sine twin (`rotXY_inv`, `rotXZ_inv`). `StandardPosition.lean`. |
| `standardposition.reject_sp a b = a − project_sp a b` | `rejectSP`, `rejectSP_eq_vecReject`, `rejectSP_eq_reject` (= Hestenes `reject b a` for vectors, via `reject_vec_eq`). |
| `standardposition.rotate_in_xy_plane` / `_xz_plane` | `rotXY`/`rotXZ`, identical formulas (parity note; no new theorem). |
| `functions.compose` / `inverse` / `identity` / `at` (`ComposableFunction`) | **plumbing — no theorem.** The one GA fact `versor_rotation`'s `backward` relies on: **`sandwich_inverse_sandwich`** (`sandwich (inverse R) (sandwich R v) = v`, any `v`, both grades), on the new `inverse_inverse`, `inverse_mul_self_of_isEvenVersor`, `mul_inverse_self_of_isEvenVersor`, `normSq_reverse`, `reverse_smul` (`Sandwich.lean`). |

## Phase 2 — `transforms.py` (done 2026-10-04, minus the angle theorem)

| Python | Lean |
|---|---|
| `projection_rotation` | already covered: `projRotation_*`, `projRotation_eq_sandwich`. |
| `versor_rotation` (forward / `backward`) | forward already covered (`sandwich_*`); backward = `sandwich_inverse_sandwich` (phase 1). |
| `bivector_rotation` / `plane_rotation` (half-angle rotor by `θ` in a general 3D plane) | **partial**, unchanged here: unit-ness and plane/normal fixed are proven; the angle theorem is `tasks/lean-rotor-3d-angle-theorem.md`. |
| `bivector_rotation(θ).at(t)` | **plumbing — no theorem.** The rotor factory supplies the interpolation law as "rebuild the rotor with `t·θ`", and a composite's `at` interpolates each component (`functions.py`); nothing GA-specific beyond the rotor theorems themselves. |
| `translate`, `uniform_scale`, `scale_non_uniform`, `to_matrix`, `MatrixTemplate`, `to_matrix_template` | **plumbing — no theorem** (affine/matrix bookkeeping); `scale_non_uniform` rests on `proj` onto `e_i`, already covered. |

## Phase 3 — `g1.py` (done 2026-10-04; the maintainer: "modelled, it's good to teach students it as well")

`G1.lean`, registered in the root module: a two-field struct, `mul`/`wedge` transcribed from
`derive_lean_algebra.py 1`, `reverse` (the identity), `I = e₁` with `I_sq : I² = +1` and
`I_sq_eq_sign` (the `(−1)^{r(r−1)/2}` sign at `r = 1` — the contrast with 𝒢₂/𝒢₃'s `−1`), `mul_comm`
(𝒢₁ is commutative), `mul_assoc`, `one_mul`, `mul_add`, `vec_mul` (the product of two vectors is a pure
scalar), `wedge_vec` (= 0: any two 1D vectors are parallel), `vec_mul_eq_dot_add_wedge` (the fundamental
identity with its wedge term vanishing), `dot_vec`, `normSq_vec`, `magnitude_vec` (`|x e₁| = |x|`),
`dual_vec` (a vector's dual is a scalar), `mul_vec_inverse_self`.

## Former phase 4 — `gn.py` (moved out, 2026-10-04)

`Gn`, `bases(n)`, `basis_vector`, `unit_pseudoscalar(n)`, `dual(n)` for `n ∉ {2,3}`,
`symbolic_multivector` need a dimension-general representation, which is the whole subject of
`tasks/lean-general-gn-product-and-hestenes-dot-wedge.md`; once that exists the remaining step is only
"prove `G1`/`G2`/`G3` ≃ the `n = 1, 2, 3` instances", which that task's open question 3 already names.
That scope was moved there at this archive, so this task closes with its own deliverables. `Gn` is the
oracle the Lean algebras were transcribed from, which is why there is nothing to prove about it yet.

## Decisions

- 𝒢₁ is modelled, for teaching (maintainer, 2026-10-04); the 3D rotor angle theorem's statement form and
  the frames scope were deferred into their own tasks rather than decided here.
- "Plumbing — no theorem" is a recorded outcome, not a skip: each such row names the one GA fact it rests
  on, and the architecture doc's coverage map carries the same rows.
- Hypotheses on the new theorems carry only what the proofs use; `projectSP_eq_proj` takes `a` as an
  arbitrary multivector because the equivariance and inverse-rotation lemmas never look at its grade.

## Record (commit trail, newest last; `make lean` green at each step)

- `c74b79e` — the review's follow-through (not this task): 𝒢₃ reverse-sandwich leaves generalized with
  structural proofs, vacuous hypotheses dropped, doc drift fixed, `autoImplicit = false`; this task and its
  two spin-offs filed.
- `78104f2` — phases 1–3: `G1.lean`; `projectSP`/`rejectSP` and their equality theorems; the sandwich
  round-trip in both grades; coverage rows and README. One build iteration was needed: the `𝒢₃ reverse_mul`
  had to move above its first use, and a `field_simp; ring` was first written as `field_simp <;> ring`
  (the linter said so).
- `6c08225` — archive of the preceding trim task (separate lifecycle).
- (The SHAs above are the post-squash commits on `master`; the pre-squash quick-saves this record first
  cited are unreachable from `master`.)

## Open questions

None.
