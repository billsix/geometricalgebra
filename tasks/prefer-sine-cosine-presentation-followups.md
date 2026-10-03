# Sine/cosine presentation — deferred candidates (NOT yet reviewed by the maintainer)

**Status:** proposed — needs the maintainer's review of the candidate list below. **Priority:** 7.
**Difficulty:** 4. **Created:** 2026-10-03 (William Emerison Six <billsix@gmail.com>).
**Part of:** the "present in sin/cos" initiative — the first pass is
`tasks/prefer-sine-cosine-presentation.md` (perpendicularity / parallelism / area families);
principle in `CLAUDE.md` › "Presenting to students".

## BLUF

The first-pass task converted the three clear families (perpendicularity `cos=0`, parallelism
`sin=0`, area `|a||b|sinθ`). This task holds the **remaining candidates the maintainer has not looked
at yet** — mainly the *hypothesis-side* `(h : dot a b = 0)` entry points and a few niche
perpendicularity lemmas. They are lower-value / more churn (restating a hypothesis in trig terms
forces a nonzero-magnitude side condition and extra plumbing), so they were deferred for a fresh
decision rather than swept in.

**The maintainer has NOT reviewed these — do not start until he has picked which (if any) to do.**

## Candidates (deferred from the first-pass inventory)

- **Hypothesis-side `(h : dot a b = 0)` → offer a `cos_between a b = 0` entry point:**
  `AlgebraLaws.lean:53/:109` `vec_anticomm_perp` (perpendicular ⇒ vectors anticommute),
  `Projection2D.lean:73` / `G3.lean:246` `mul_eq_wedge_of_perp`, `Predicates3D.lean:22`
  `perp_iff_mul_eq_wedge`. These take `dot a b = 0` as a hypothesis; a trig-phrased variant would take
  `cos_between a b = 0` and recover `dot a b = 0` (needs `magnitude a, b ≠ 0` to divide back), which is
  extra friction for a hypothesis the caller already has in dot form.
- **Niche perpendicularity facts** (clean `cos=0` corollaries, just lower-priority than the headline
  ones done in the first pass): `Projection3D.lean:46/:51` `dual_wedge_perp_left/right`, `:120`
  `proj_plane_perp_normal`. (Decide whether these are "student-facing" enough to warrant the trig
  form.)
- **Volume** (`Measures.lean:38`): a `|a||b||c|`·(trig) form for the scalar triple product is less
  standard than area = |a||b|sinθ; decide whether a trig restatement helps a student or just adds
  noise.

## Progress (2026-10-03)

- **Niche perpendicularity corollaries — DONE** (maintainer said "continue"): added
  `dual_wedge_perp_left_cos`, `dual_wedge_perp_right_cos`, `proj_plane_perp_normal_cos` to
  `StudentTrigForms.lean` (each `cos_between … = 0`, resting on its `dot … = 0` lemma, same trivial
  `zero_div` pattern as the first pass).
- **Hypothesis-side `(h : dot a b = 0)` entry points — SKIPPED** (use-your-discretion opt-out): a
  trig-phrased variant would take `cos_between a b = 0` and have to recover `dot a b = 0` (needs
  `|a|,|b| ≠ 0` to divide back), which is friction for a hypothesis callers already hold in dot form.
  Still available if the maintainer wants it.
- **Volume-in-trig — SKIPPED**: a `|a||b||c|`·(trig) form for the scalar triple product is less
  standard than area = |a||b|sinθ and reads as noise; left as `|a∧b∧c|`.

## Open questions

1. Confirm the two SKIPs above (hypothesis-side entry points, volume-in-trig), or do you want either
   after all? My recommendation: leave both skipped.
