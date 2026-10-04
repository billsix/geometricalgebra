# Sine/cosine presentation — deferred candidates (two SKIPs await the maintainer's confirmation)

**Status:** proposed — needs the maintainer's confirmation of the two SKIPs below. **Priority:** 7.
**Difficulty:** 4. **Created:** 2026-10-03 (William Emerison Six <billsix@gmail.com>).
**Updated:** 2026-10-04 (William Emerison Six <billsix@gmail.com>) — BLUF reconciled with Progress;
theorem names corrected to the ones in the corpus; line numbers dropped.
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
- **Hypothesis-side `(h : dot a b = 0)` entry points — SKIPPED** (use-your-discretion opt-out): a
  trig-phrased variant would take `cos_between a b = 0` and have to recover `dot a b = 0` (needs
  `|a|,|b| ≠ 0` to divide back), which is friction for a hypothesis callers already hold in dot form.
  Still available if the maintainer wants it.
- **Volume-in-trig — SKIPPED**: a `|a||b||c|`·(trig) form for the scalar triple product is less
  standard than area = |a||b|sinθ and reads as noise; left as `|a∧b∧c|`.

## Open questions

1. Confirm the two SKIPs above (hypothesis-side entry points, volume-in-trig), or do you want either
   after all? My recommendation: leave both skipped.
