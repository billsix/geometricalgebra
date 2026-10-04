# Investigate Lean 4 as a proof-checking layer for the GA derivations (umbrella)

**Status:** DONE, archived 2026-10-04 — every step task closed (the last four on 2026-10-04); the
proposed/deferred tasks it listed (`investigate-lean-to-python-proof-notebooks`, `lean-general-multivector-
inverse`, `lean-general-gn-product-and-hestenes-dot-wedge`) stand on their own. **Priority:** 6.
**Difficulty:** 7. **Started:** 2026-09-27 (William Emerison Six <billsix@gmail.com>).
**Durable record:** `tasks/reference/lean-for-gacalc.md` (orientation, the spikes, the gate),
`tasks/reference/lean-ga-proof-architecture.md` (architecture, inventory, coverage map, and the
"Program decisions" section harvested from this umbrella), `tasks/reference/lean-proof-corpus-review-2026-10-04.md`
(the independent audit of the corpus).

## BLUF

Lean 4 + Mathlib was adopted as a private, machine-checked proof layer that verifies the *mathematics*
behind gacalc's derivations — a way for the author to check his own work, not student material, and not a
verification of the Python. It was spiked (2026-09-27/28), scaffolded as `proofs/` with `make lean` and a
completeness gate that fails like a unit test, baked offline into the image, wired to CI on `v*` tags, and
then filled in over 2026-09-28 → 2026-10-04: 29 modules, ~400 theorems, covering the vector-level math of
the library in 𝒢₁/𝒢₂/𝒢₃ with every from-scratch result bridged to its Mathlib counterpart.

## What was done

- **Spikes (2026-09-27/28).** Pure Lean, then Mathlib reuse: the reliable gate is a `sorry`/`admit` check,
  not a bare `lake build`; the dot product is a *proved* Mathlib theorem (`real_inner_comm`), not an axiom;
  `git` had to be added to the image under `USE_LEAN`; Mathlib must be baked at image build to stay
  offline. Harnesses were one-shot (deleted at archive; see `lean-for-gacalc.md` for what they showed).
- **Scaffold + gate + CI (2026-09-28).** `lake init GacalcProofs math`, toolchain `v4.34.1`, Mathlib
  pinned; `proofs/check.sh` (`lake build` + completeness gate) behind `make lean`; Mathlib baked at
  `/opt/gacalc-proofs/.lake` and copied into the mount; `.github/workflows/lean.yml` on `v*` tags.
- **Step tasks, all done and archived** (`tasks/archive/2026/09/29/` … `10/04/`): rotation from scratch;
  dot and wedge as the parts of the product; the pseudoscalar sign for n ≤ 3; the Lagrange identity;
  2D dual ⊥; 2D versor from vectors; from-scratch `G3`; algebra laws; projection; the sandwich preserves
  length and angles; sandwich rotates components (matrix-free); magnitude unification; coordinate-free
  property algebra; blade inverses; the standard-position bootstrap; the object-in sweep; the simp trim;
  the coverage extension (𝒢₁, standard position, the sandwich round-trip); the Mathlib bridges.
- **Follow-ons left open on purpose:** the general-n algebra (and with it the general pseudoscalar sign
  and Hestenes dot/wedge), the general multivector inverse, the Lean→notebook pipeline, the 3D rotor angle
  theorem, frames.

## Decisions (harvested verbatim-in-substance into `lean-ga-proof-architecture.md` "Program decisions")

1. Lagrange identity in the squared form. 2. `proofs/` + `make lean`. 3. CI on tagged releases only.
4. Every proof from scratch; Mathlib only as the ambient library plus an *equivalence* bridge per result.
5. Pseudoscalar statement `Iᵣ² = (−1)^(r(r−1)/2)` only. 6. (2026-10-04) What "equivalence to the general
case" means per result: dot ↦ `EuclideanSpace`/`inner`; wedge ↦ determinant/minors/`crossProduct`;
rotation ↦ `Orientation.rotation`; pseudoscalar n ≤ 3 against each algebra's own `I²`, general n with
the Gn task; "derived from rotation" discharged by `uvec_mul_uvec` + `uvec_dot`/`uvec_wedge`.
