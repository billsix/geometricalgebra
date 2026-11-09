# Lean proofs for the reciprocal frame and `Frame`'s two inverses

**Created:** 2026-11-07 (William Emerison Six <billsix@gmail.com>) · **Completed:** 2026-11-07

The 2026-11-07 frame work is machine-checked for 𝒢₂ and 𝒢₃ in `proofs/GacalcProofs/ReciprocalFrame2D.lean`
and `ReciprocalFrame3D.lean`: the reciprocal frame of H&S p. 28 (eqs 3.4, 3.5, 3.7), the similar-triangles
reading of a coordinate, the last reciprocal vector as the last rejection, and both inverses of
`Frame.to_invertible_function` undoing the forward map on both sides and agreeing. `proofs/check.sh` is
green with no `sorry`. The Python docstrings and tests cite the theorems by name, and
`tasks/reference/lean-ga-proof-architecture.md` has the inventory entry, the coverage rows, and the proof
techniques this needed.

## Decisions

1. **Scope against the on-hold Lean frame task** (William Emerison Six <billsix@gmail.com>, 2026-11-07:
   "sure"). This task proved rejection orthogonality and took over theorems 5 (round trip) and 6 (last
   reciprocal) of `tasks/lean-frame-class-invertible-function.md`; its theorems 2–4 stayed on hold there, and
   `tasks/lean-frame-coverage.md` stayed parked.
2. **Lean only** (the maintainer's request). The prose + LaTeX book page that CLAUDE.md's three-forms rule
   calls for was not written; its home would be `book/docs/frames-qr.rst`. The symbolic Python form is the
   tests in `tests/test_frame.py` and `tests/test_frame_class.py`.

## The theorems

| # | Statement | 𝒢₂ | 𝒢₃ |
|---|---|---|---|
| 1 | eq 3.7 definitions | `recip1`, `recip2` | `recip1`, `recip2`, `recip3` (with `vol3`) |
| 2 | each `aᵏ` is a vector | `isVector_recip1/2` | `isVector_recip` |
| 3 | eq 3.5, Kronecker delta | `dot_recip_kronecker` (4 cases) | `dot_recip_kronecker` (9 cases) |
| 4 | eq 3.4, reconstruction | `reconstruct` | `reconstruct`, `reconstruct_dual` |
| 5 | similar triangles | `coord1/2_of_perp`, `recip1/2_eq_normal_div` | `coord1/2/3_of_perp`, `recip1/2/3_eq_normal_div` |
| 6 | last reciprocal = last rejection / its length² | `dot_reject_self`, `recip2_eq_reject_div` | `reject_plane_facts`, `reject_line_facts`, `recip3_eq_reject_div` |
| 7 | round trips, both methods | `invReciprocal_frameMap`, `frameMap_invReciprocal`, `invPeel_frameMap`, `frameMap_invPeel` | the same, plus `invPeel_comb` |
| 8 | the inverses agree | `invReciprocal_eq_invPeel` (from 7) | `invReciprocal_eq_invPeel` (via `invPeel_eq_reciprocal_coords`) |

The frame hypothesis is `normSq (a₁ ∧ … ∧ aₙ) ≠ 0`. 2D is proved in coordinates throughout. 3D proves the
reciprocal facts in coordinates (leaves `recip*_vec` over the atoms `det3` and `crossSq`) and the peel
structurally: `invPeel_comb` reads `x₃`, `x₂`, `x₁` back from `x₁*a₁ + x₂*a₂ + x₃*a₃` with `dot`
bilinearity and the rejections' orthogonality, and the round trips follow by rewriting with `reconstruct`.
`aⁱ = m/(m·aᵢ)` in 3D comes from `reconstruct_dual` (`m = Σ (aₖ·m)*aᵏ`, only one term survives).

## What went wrong on the way, and the fixes

- **No Lean in the local image.** It was the lean `MINIMAL_IMAGE=1` build. `make image MINIMAL_IMAGE=1
  USE_LEAN=1` failed nested (buildah's rootless pasta networking on the Fedora 45 sandbox; diagnosed and
  fixed in runClaudeInContainer's `exampleRunClaude.sh` with `BUILDAH_ISOLATION=chroot`); the build ran by
  hand with `--network=host`.
- **`proofs/check.sh` had no executable bit** (mode `100644` since it was added on 2026-09-27), so
  `make lean`, and `lean.yml` on tags, died with `Permission denied`. Fixed in its own commit.
- **The first 2D draft** rewrote vectors in place with `eq_vec_of_isVector`; `field_simp` then could not
  match the nonzero hypothesis to a reordered denominator, and `first | ring | …` stopped at a `ring` that
  fell back to `ring_nf`. Fixed by destructuring into fresh variables, generalizing the denominator, and
  `ring1`. The 3D draft's errors were a binder named like an outer variable, a `simp` that unfolded `comb`
  before a rewrite needed it, and `|w₃|²` reaching `field_simp` as a sum of squared fractions (fixed with
  the leaf `normSq_reject_plane_vec`). These are recorded as techniques in the architecture reference.

## Gates

`proofs/check.sh`: `Build completed successfully`, no `sorry`/`admit`, `[lean] OK`. No warnings in the two
new files. `entrypoint/format.sh` green; `make test`'s frame tests (76, slow ones skipped) passed after the
docstring changes.
