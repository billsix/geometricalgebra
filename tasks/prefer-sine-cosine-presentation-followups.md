# Sine/cosine presentation — deferred candidates (both deferred items BUILT 2026-10-09)

**Status:** complete
**Completed:** 2026-10-09
**Priority:** 7.
**Difficulty:** 4. **Created:** 2026-10-03 (William Emerison Six <billsix@gmail.com>).
**Updated:** 2026-10-09 (William Emerison Six <billsix@gmail.com>) — maintainer chose "build both"
(2026-10-09), overriding the recommended SKIPs; both items landed in `StudentTrigForms.lean`.
**Part of:** the "present in sin/cos" initiative — the first pass is
`tasks/archive/2026/10/03/prefer-sine-cosine-presentation.md` (perpendicularity / parallelism / area families);
principle in `CLAUDE.md` › "Presenting to students".

## BLUF

The first-pass task converted the three clear families (perpendicularity `cos=0`, parallelism
`sin=0`, area `|a||b|sinθ`). This task held three deferred candidate groups. Of those, the **niche
perpendicularity corollaries are DONE** (2026-10-03, on the maintainer's "continue"; see Progress).
The two that remain — the *hypothesis-side* `(h : dot a b = 0)` entry points and a trig form of
volume — were **SKIPPED** by discretion (restating a hypothesis in trig terms forces a
nonzero-magnitude side condition and extra plumbing; a trig volume reads as noise). "Done" = the
maintainer confirms both SKIPs (Q1), after which this task archives; if he wants either, it becomes
the work.

**Do not start either skipped item until the maintainer has answered Q1.**

## Candidates (deferred from the first-pass inventory)

- **Hypothesis-side `(h : dot a b = 0)` → offer a `cos_between a b = 0` entry point:**
  `vec_anticomm_perp` in `AlgebraLaws.lean` (perpendicular ⇒ vectors anticommute; the file holds
  two theorems of that name — the coordinate-taking one `(u1 u2 v1 v2 : ℝ)` and the object one
  `{a b : G3} (ha : IsVector a) (hb : IsVector b) (h : dot a b = 0)`; the **object** one is the
  candidate), `mul_eq_wedge_of_perp` (in both `Projection2D.lean` for 𝒢₂ and `G3.lean` for 𝒢₃),
  `perp_iff_mul_eq_wedge` in `Predicates3D.lean`. These take `dot a b = 0` as a hypothesis; a
  trig-phrased variant would take `cos_between a b = 0` and recover `dot a b = 0` (needs
  `magnitude a, b ≠ 0` to divide back), which is extra friction for a hypothesis the caller already
  has in dot form.
- **Niche perpendicularity facts** (clean `cos=0` corollaries, just lower-priority than the headline
  ones done in the first pass): the dot-form leaves `dual_wedge_perp_left_dot` /
  `dual_wedge_perp_right_dot` / `proj_plane_perp_normal_dot` in `Projection3D.lean`. (Decide whether
  these are "student-facing" enough to warrant the trig form.) — **DONE, see Progress.**
- **Volume** (`volume` / `volume_sq_vec` in `Measures.lean`): a `|a||b||c|`·(trig) form for the
  scalar triple product is less standard than area = |a||b|sinθ; decide whether a trig restatement
  helps a student or just adds noise.

## Progress (2026-10-03)

- **Niche perpendicularity corollaries — DONE** (maintainer said "continue"): added the trig forms
  `dual_wedge_perp_left`, `dual_wedge_perp_right`, `proj_plane_perp_normal` to
  `proofs/GacalcProofs/StudentTrigForms.lean` (each `cos_between … = 0`, named for the geometry — no
  `_cos` suffix, per the first pass's naming rule), each resting on its renamed `dot … = 0` leaf
  `dual_wedge_perp_left_dot` / `dual_wedge_perp_right_dot` / `proj_plane_perp_normal_dot` in
  `Projection3D.lean`, same trivial `zero_div` pattern as the first pass. (Names verified against the
  corpus 2026-10-04.)
- **Hypothesis-side `(h : dot a b = 0)` entry points — BUILT 2026-10-09** (maintainer chose "build
  both"): added a shared leaf `dot_eq_zero_of_cos_between` (recovers `dot a b = 0` from
  `cos_between a b = 0` under `magnitude a, b ≠ 0`, via `div_eq_zero_iff` + `resolve_right`) in both
  the `G2` and `G3` namespaces of `proofs/GacalcProofs/StudentTrigForms.lean`, and the trig-side
  entry points on top of it: `mul_eq_wedge_of_cos_perp` (G2 and G3), `vec_anticomm_cos_perp` (G3), and
  the iff `cos_perp_iff_mul_eq_wedge` (G3, forward needs the guard, reverse is free). Each wraps the
  existing dot-hypothesis theorem (`mul_eq_wedge_of_perp`, `vec_anticomm_perp`, `perp_iff_mul_eq_wedge`),
  so the nonzero guard is exactly what the header's "why the guard matters" paragraph describes.
- **Volume-in-trig — BUILT 2026-10-09**: `volume_eq_mag_mul_cos` (G3) —
  `volume = |a|*|b×c|*|cos(a, b×c)|`, the parallelepiped's "base area × height" through the cross
  product (`|b×c|` is the b–c face's area, the angle is from `a` to that face's normal). Proved from
  `volume_sq_vec` (`volume = |signed volume|`, via `Real.sqrt_sq_eq_abs`) and
  `dot_cross_eq_signedVolume` (`a·(b×c) = signed volume`), then `abs_div` + `field_simp` under the
  nonzero guards `magnitude a ≠ 0`, `magnitude (cross b c) ≠ 0`.

## Verification

- `proofs/check.sh` (the `make lean` gate) green in-container against the existing image: `lake build`
  completed (8958 jobs), completeness gate "no sorry/admit in sources", "[lean] OK". A targeted
  `lake build GacalcProofs.StudentTrigForms` compiled the new theorems on the first try.
- Pre-existing, unrelated: the build log shows a recovered `ring`-failed note and two `hn`
  unused-variable warnings in `ProjectionRotation3D.lean` (a file this task did not touch; build still
  green).

## Open questions

None — the maintainer answered the one open question (2026-10-09): **build both**, overriding the
recommended SKIPs. Both items are built and gate-verified. Since this is a Lean presentation layer on
results whose Python and prose forms already exist, the other two of the "three forms" are
intentionally not added here.
