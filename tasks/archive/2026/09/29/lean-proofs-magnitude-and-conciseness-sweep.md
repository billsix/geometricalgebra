# Lean proofs — collapse self-dot / two-magnitudes into one idea (conciseness sweep)

**Part of:** `tasks/investigate-lean-proofs-for-ga.md` (the Lean-proofs umbrella)
**Related:** `tasks/lean-proofs-make-coordinate-free.md` (the leaf/structural refactor; this was its
"collapse to a simpler idea" companion — same spirit, focused on the magnitude concept).
**Depends on:** the leaf layer (`normSq`, `magnitude`, `normSq_vec`, `normSq_evenVersor`, `dot_vec`)
in `proofs/GacalcProofs/`.

**Status:** done (2026-09-29, William Emerison Six <billsix@gmail.com>) — every collapse applied or
declined-with-reason; `make lean` green (no warnings); one magnitude concept (`magnitude = √normSq`)
throughout, and no raw coordinate sum left in a hypothesis.
**Priority:** 7
**Difficulty:** 5

## BLUF

A readability sweep. The squared magnitude `normSq` (and its root `magnitude = √normSq`) was the one
primitive, and several places in the proofs were longer, redundant restatements of it — the maintainer's
example: *a vector dotted with itself is its magnitude squared*. Every such place was collapsed to the
simple idea (or explicitly declined with a reason). The outcome: one magnitude concept in the code, no
raw coordinate polynomial standing in a lemma's interface, each touched proof no longer than before, and
`make lean` green. Detail lives in git (commits `c07aa63`…`a9321d5` on `leanProofs`) and in
`tasks/reference/lean-ga-proof-architecture.md`.

## What was done

- **Removed the redundant `sandwich_preserves_normSq_vec`.** It stated `dot (RvR⁻¹)(RvR⁻¹) = dot v v` —
  a self-dot on both sides, i.e. `|RvR⁻¹|² = |v|²`, which is exactly `sandwich_preserves_normSq_of_vec`
  (the `normSq` form). The `dot`-form was unused, so it was dropped; the `normSq` statement is the one.

- **Added the `normSq_biv` leaf** (`normSq ⟨0,0,0,0,p,q,r,0⟩ = p²+q²+r²`) and de-duplicated the
  bivector-literal `normSq` re-derivations in `Projection.lean` (`reject_eq_proj_normal`,
  `project_add_reject`).

- **Unified the two magnitudes into one** (the headline; a supervised multifile move). There had been a
  vector-only `mag = √(dot a a)` (in `Rotation3D`/`Versor2D`) and a general `magnitude = √normSq` (in
  `Sandwich`); on a vector they coincide, so the split was pure redundancy. `normSq`/`magnitude`/
  `normSq_vec` (and G3's `normSq_wedge_vec`) moved **down into `G2.lean`/`G3.lean`** (after `dot_vec`) so
  they precede every consumer; the `Sandwich` copies were removed. `mag` and the **unused** `magnitude_vec`
  bridge were deleted. Every `mag` use became `magnitude` (`Rotation3D`/`Versor2D`/`RotateComponents`/
  `Sandwich`), and `mag_sq_vec` became `magnitude_sq_vec`, reproved through `normSq_vec` under the square
  root (`rw [magnitude, Real.sq_sqrt (by rw [normSq_vec]; positivity), normSq_vec]`) — no more inline
  self-`dot` derivation. End state: one concept, `magnitude = √normSq`, correct for all grades.

- **Stated plane nondegeneracy as `normSq B`, not a coordinate sum.** The first pass collapsed the
  *derivation* of `proj_plane_eq_project_onto`'s nondegeneracy via `normSq_wedge_vec`, but that still left
  the raw sum `(a₁b₂−a₂b₁)² + …` standing in a `have`. The real fix was at the interface: the three
  literal-bivector lemmas (`project_add_reject`, `reject_eq_proj_normal`, `project_eq_sub_reject`) now take
  `normSq (⟨0,0,0,0,p,q,r,0⟩) ≠ 0` — the plane bivector's squared magnitude — instead of `p²+q²+r² ≠ 0`,
  and each proof recovers the coordinate form (`rw [normSq_biv] at h`) only where `field_simp` needs it.
  The caller `proj_plane_eq_project_onto` then feeds its own `hn` (`normSq (a∧b) ≠ 0`) straight in once the
  wedge is rewritten to its bivector literal — no coordinate detour, and no coordinate sum anywhere in the
  file. (`normSq_wedge_vec` stayed: still used in `Trig.lean`.)

- **Cleared two `linter.unusedSimpArgs` warnings** (`zero` in `G3.lean`, `reverse` in `Projection.lean`'s
  `reject_eq_proj_normal`), so `make lean` builds with no warnings.

## Declined / kept general (with reason)

- **`proj`'s denominator `dot a a` was left as-is** (and commented). `proj a b := (b·a / a·a)·a` is the
  general vector-projection def; its `dot a a` is the Hestenes self-inner-product, which equals `normSq a`
  **only** for a vector (they have opposite signs on grade ≥ 2, since `normSq` uses the reverse). Rewriting
  it to `normSq a` would narrow the def incorrectly.
- **`reject_perp`'s hypothesis `dot a a ≠ 0` was left as-is** (and commented), for the same reason: it holds
  for any `a`, and tightening it to `normSq a ≠ 0` would break the non-vector case. Comments recording this
  were added at all four sites (G2 + G3).

## Open questions (resolved)

1. ~~`mag` unification: a thin abbreviation or replace-and-delete?~~ **Resolved** — replaced all `mag` uses
   with `magnitude` and deleted `mag` (and `magnitude_vec`). An abbreviation was impossible anyway: `mag`
   lived in `Rotation3D`/`Versor2D`, imported *by* `Sandwich` where `magnitude` lived, so the defs had to
   move down into `G2`/`G3` regardless — once moved, a straight rename read cleanly, so no alias was kept.

## Follow-ups noted (not part of this task)

- The bivector literals `⟨0,0,0,0,p,q,r,0⟩` could read as `{ zero with c12 := p, c13 := q, c23 := r }`
  (Lean structure-update syntax) for clarity, at the cost of a `simp only [zero]` unfold where the
  low-degree `field_simp` needs the literal. Parked for the coordinate-free readability pass
  (`tasks/lean-proofs-make-coordinate-free.md`).
