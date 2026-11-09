# Lean low cleanup: doc-comment notation, history comments, moved-task citations, misplaced lemmas

**Created:** 2026-11-09 · **Completed:** 2026-11-09
**Source:** tasks/review/2026/11/08/repo-review.md §7.3, §2.4

## What changed

- **Notation in doc comments and `proofs/README.md`** (`CLAUDE.md` › "Math notation for readers"; in
  Lean doc comments the star has no spaces):
  - 45 coefficient·basis products such as `x·e₁` became `x*e₁`, replaced by a codemod limited to
    `/- … -/` regions;
  - by hand: `u*v = (u·v) + …`, `½*(u*v + v*u)`, `(−1)^(r*(r−1)/2)`, `eᵢ*eⱼ=−eⱼ*eᵢ`,
    `(b·a / a·a)*a`, `2*sin(θ/2)*cos(θ/2)`, `(R θ₂)*(R θ₁)`, `2*cos(θ/2)`, `cos²(|B|)`/`sin²(|B|)`,
    `|a|*(reduced b).e₂`, `R*R̃` (23 places), `A*I⁻¹`, `sin(θ/2)*i`, and
    `2*|a|*|b|*(|a|*|b| + a·b)`;
  - every dot that is a dot product (`u·v`, `a·b`) stays.
- **History comments** in `G2.lean`, `Rotation3D.lean`, `ProjectionRotation2D.lean` and `Rotor.lean`
  (two) describe the present.
- **Moved-task citations** in `Cross.lean`, `Sandwich.lean` and `RotateComponents.lean` point at their
  `tasks/archive/2026/09/…` paths.
- **Moved lemmas:**
  - the four 2D sandwich-wedge lemmas (`wedge_reverse_sandwich`, `sandwich_preserves_wedge`,
    `normSq_reverse_sandwich_wedge`, `sandwich_preserves_normSq_of_wedge`) went from
    `Projection2D.lean` to `Sandwich.lean`, beside their G3 twins. Their doc comments' juxtaposition
    was fixed on the way.
  - `G2.mul_vec_self` went from `ProjectionRotation2D.lean` to `G2.lean`, beside `G3.mul_vec_self` in
    `G3.lean`.
  - `tasks/reference/lean-ga-proof-architecture.md` says where they live now.

## Tried and reverted

Rewriting G3's `rVectorPart` with the basis constants (`smul a.c1 e_1 + …`), to match G2's, broke eight
`GradeProjection.lean` proofs that unfold the struct-literal form by `rfl`/`simp`. The struct literals
stay; matching G2's style isn't worth reworking those proofs.

## Verification

`make lean`: the build, the `sorry`/`admit` grep, and the axioms gate (1043 declarations rest only on
`propext`, `Classical.choice`, `Quot.sound`) all pass. Trig.lean, which uses the moved lemmas, builds
unchanged.
