# Lean coverage of `frame.py` — linear independence, Gram–Schmidt, the Hestenes closed form

**Status:** proposed — parked by the maintainer ("I'm not ready for frames yet", 2026-10-04); do not
start without a go-ahead. **Priority:** 8 (parked). **Difficulty:** 5.
**Created:** 2026-10-04 (William Emerison Six <billsix@gmail.com>), spun out of
`tasks/lean-coverage-extend-transforms-frame-gn.md`. **Owner:** William Emerison Six <billsix@gmail.com>.
**See also:** `tasks/reference/lean-proof-corpus-review-2026-10-04.md` §3, `tasks/define-frame.md` (the
Python-side frame work), `tasks/reference/lean-ga-proof-architecture.md`.

## BLUF

`src/gacalc/frame.py` has no Lean coverage: `are_linearly_independent`/`is_frame` (`a₁∧…∧a_k ≠ 0`),
`make_orthogonal_frame` (Gram–Schmidt by rejection), `make_orthogonal_frame_hestenes` (`c_k = Ã_{k−1} A_k`),
and their equivalence `c_k = |A_{k−1}|²·w_k` (today only tested, `tests/test_frame.py`). "Done" = a
`Frame.lean` (𝒢₃, k ≤ 3; k = 2 also in 𝒢₂ if cheap) with: dependence ⟺ wedge zero (k = 2: the converse of
`Predicates3D.wedge_parallel_smul`, `a ∧ b = 0 ∧ a ≠ 0 ⟹ ∃ k, b = k·a` — this also closes the
`is_parallel_to` half-gap; k = 3 as `signedVolume ≠ 0`), Gram–Schmidt pairwise orthogonality (compose
`reject_perp_dot`; the k = 3 step rejects from a bivector via `Projection3D.project_add_reject`), and the
Hestenes-form equality for k = 2, 3; `make lean` green; coverage table rows added.

## Context — how to read this cold

- Lean today: `wedge_self_vec`, `wedge_parallel_smul`, `reject_perp_dot`, `project_add_reject`,
  `Cross.signedVolume`/`dot_cross_eq_signedVolume` are the available ingredients. No existential statements
  exist yet in the corpus (`∃ k, …`); the dependence converse will be the first — expect a small
  coordinate case split on which component of `a` is nonzero.
- Style and build: `CLAUDE.md` "Coordinates only when needed"; `lean-ga-proof-architecture.md` (recipes,
  the hypotheses section, build discipline for nested runs).

## Open questions

1. k = 2 in both grades, or 𝒢₃ only? (Recommend both; the 𝒢₂ case is a few lines.)
