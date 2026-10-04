# Extend Lean coverage to `transforms`, `standardposition`, `frame`, `functions`, `g1`, `gn`

**Status:** proposed — needs go-ahead (the maintainer asked for these modules to be in scope,
2026-10-04: "I want those in scope perhaps, make them a separate task, with cold start information").
**Priority:** 5. **Difficulty:** 6 (phases 1–3 are 𝒢₂/𝒢₃ work in the existing style, D4–5 each; phase 4
depends on a dimension-general algebra and inherits that task's D8).
**Created:** 2026-10-04 (William Emerison Six <billsix@gmail.com>). **Owner:** William Emerison Six
<billsix@gmail.com>.
**Depends on:** nothing for phases 1–3; phase 4 on `tasks/lean-general-gn-product-and-hestenes-dot-wedge.md`
(deferred, P9) — do NOT start phase 4 before that one.
**See also:** `tasks/reference/lean-proof-corpus-review-2026-10-04.md` (the coverage map that found these
gaps, §3), `tasks/reference/lean-ga-proof-architecture.md` (how to write a proof in this corpus; its
coverage table covers only `base`/`vectorcalc`/`measure`), `tasks/reference/lean-for-gacalc.md`
(orientation), `tasks/archive/2026/10/01/lean-coverage-gap-audit.md` (the earlier audit, same method).

## BLUF

The Lean corpus (`proofs/GacalcProofs/`) covers the vector-level math of `base.py`, `vectorcalc.py` and
`measure.py` in 𝒢₂/𝒢₃, but six Python modules were never in the audited surface: `transforms.py`,
`standardposition.py`, `frame.py`, `functions.py`, `g1.py`, `gn.py`. This task brings them in: for each
public math function, either a Lean theorem stating its defining property (same style as the rest of the
corpus: objects in, scalars in the body, objects out), or a recorded decision that it is plumbing with no
GA content. "Done" = every function in the table below has a theorem name or a "plumbing — no theorem"
decision, `make lean` green, and the architecture doc's coverage table extended to these modules.

## Context — how to read this cold

- **What Lean models.** `G2`/`G3` are coordinate structs (`G2.lean:50`-ish `structure G2`, `G3.lean`
  `structure G3`) with hand-written `mul`/`wedge`/`reverse` (𝒢₃'s transcribed from the Python `Gn` oracle
  by `tools/derive_lean_algebra.py`). There is **no** dimension-general algebra and no `G1`. Lean proves
  identities about its own definitions; the Python is matched by formula, by hand (the review's §B
  spot-checks are the parity evidence).
- **How a theorem is written here.** Take the object and a grade predicate (`{a : G3} (ha : IsVector a)`),
  conclude about objects; in the body `obtain ⟨zeros⟩ := ha; simp only [defs, zeros]; ring` (polynomial
  tier) or a structural `rw` chain through the leaf lemmas. Rules: `CLAUDE.md` "Coordinates only when
  needed"; recipes and dead-ends: `lean-ga-proof-architecture.md`. Add a new file per topic, suffix
  `2D`/`3D` when grade-specific, and `import` it from `proofs/GacalcProofs.lean` (the root module — a file
  not imported there is not built or checked).
- **Build.** `make lean` from the repo root (depends on `image`; inside a nested sandbox prefer the
  direct form so it does not rebuild the 16 GB image:
  `podman run --cgroups=disabled --rm -v $PWD:/gacalc:Z --entrypoint /bin/bash localhost/gacalc /gacalc/proofs/check.sh`).
  A full incremental gate is ~5 min; `Sandwich` alone ~70 s. Read the warnings: `unusedVariables` flags a
  signature hypothesis the proof never uses — drop it (or `_`-prefix a deliberate meaning gate).
- **Hypotheses.** Carry only what the proof uses; a failed delete-and-rebuild can be a `ring` budget
  problem, not a mathematical need — see the review §1 and the architecture doc's "name-absent ≠ unused".

## The gap table (from the review, with the Python anchors)

Anchors are function names, not line numbers (they rot). "Lean candidate" is the theorem to write.

### Phase 1 — `standardposition.py` and `functions.py` (𝒢₃, cheapest; D4)

| Python | Lean today | Lean candidate |
|---|---|---|
| `standardposition.project_sp` / `reject_sp` (align `b` to `e₁` by `rotate_in_xy_plane` then `rotate_in_xz_plane`, project, rotate back) | `StandardPosition.lean`: `rotXY`/`rotXZ` (same formulas), `*_preserves_dot`, `proj_rot*_equivariant`, `rotate_b_to_e1` — the ingredients | **`project_sp_eq_proj`**: the composed standard-position projection equals `proj b a` (and `reject_sp_eq_reject`), stated over objects with the `k ≠ 0` guard the Python's degenerate z-axis case needs. `CLAUDE.md` and the Python docstring already say "proven equal"; make it literally true with one theorem. |
| `standardposition.rotate_in_xy_plane` / `rotate_in_xz_plane` as Python functions | `rotXY`, `rotXZ` defs match term for term | a one-line parity note in the coverage table (no new theorem) |
| `functions.compose` / `inverse` / `identity` (`ComposableFunction`) | `sandwich_comp`, `inverse_mul` (versor products only) | **decision**: plumbing — no theorem. Record the one GA fact they rely on: `sandwich (inverse R) (sandwich R v) = v` (**`sandwich_inverse_sandwich`**, from `inverse_mul`/`mul_inverse_self`), which is what `versor_rotation.backward` needs. |

### Phase 2 — `transforms.py` (𝒢₃ + 𝒢₂; D5)

| Python | Lean today | Lean candidate |
|---|---|---|
| `projection_rotation` | `projRotation_*` incl. `projRotation_eq_sandwich` | done (record in the table) |
| `versor_rotation` forward | `sandwich_*` | done; backward: `sandwich_inverse_sandwich` (phase 1) |
| `bivector_rotation` / `plane_rotation` (half-angle rotor `R = cos(θ/2) − sin(θ/2)·i`, applied `R v R̃`) | `Rotation2D.sandwich_versor` (𝒢₂, plane `e₁₂` only); `Exp.normSq_expBivectorGeneral` (unit); `sandwich_fixes_own_bivector`/`_normal` | **the 𝒢₃ angle theorem**: for a unit bivector `i` and `R = cos(θ/2) − sin(θ/2)·i`, `R v R̃` rotates the in-plane part of `v` by `θ` (state as `cos_between (R v R̃) v = cos θ` for in-plane `v`, plus the ⊥ part fixed), and `R` is unit. Route: reduce to standard position (`CrossStandardPosition.reduceToPlane` puts `i` in `e₁₂`) and reuse `sandwich_versor`. This is the gap with the most Python resting on it. |
| `bivector_rotation(θ).at(t)` interpolation (`rotation(θ).at(t) = rotation(t·θ)`) | — | **`versor_at`**: `versor (t·θ)` is the rotor of angle `t·θ` (2D: `versor_mul` already gives additivity; 3D after the item above) |
| `translate`, `uniform_scale`, `scale_non_uniform`, `to_matrix`, `MatrixTemplate`, `to_matrix_template` | — | **decision**: affine/plumbing — no theorem, except `scale_non_uniform` rests on `proj` onto `e_i` (already covered). Record. |

### Phase 3 — `frame.py` (𝒢₃, k ≤ 3; D5)

| Python | Lean today | Lean candidate |
|---|---|---|
| `are_linearly_independent` / `is_frame` (`a₁∧…∧a_k ≠ 0`) | `wedge_self_vec`, `wedge_parallel_smul` | **`wedge_eq_zero_iff_dependent`** for k = 2 (the converse of `wedge_parallel_smul`: `a ∧ b = 0 ∧ a ≠ 0 ⟹ ∃ k, b = k·a`) — also closes the `is_parallel_to` half-gap; k = 3 as `signedVolume ≠ 0`. |
| `make_orthogonal_frame` (Gram–Schmidt by rejection) | `reject_perp_dot` (one step) | **`gramSchmidt_orthogonal`** for k = 2, 3: the rejection chain is pairwise ⊥ (compose `reject_perp_dot`; the k = 3 step needs rejection from a bivector, `Projection3D.project_add_reject`). |
| `make_orthogonal_frame_hestenes` (`c_k = Ã_{k−1} A_k`) and its equivalence `c_k = |A_{k−1}|²·w_k` | — (tested in `tests/test_frame.py`) | **`hestenes_frame_eq_rejection`** for k = 2 (`ã₁ (a₁∧a₂) = |a₁|²·reject_{a₁} a₂`) and k = 3. |

### Phase 4 — `g1.py`, `gn.py` (blocked on a general-n algebra; D8 via the Gn task)

| Python | Lean today | Lean candidate |
|---|---|---|
| `g1.py` (𝒢₁ ≅ ℝ ⊕ ℝe₁) | — | cheap on its own: a `G1` struct with `mul`, `I² = +1`, dot/wedge of vectors — OR decide it is trivial and skip (open question 1) |
| `gn.py` (`Gn`, `bases(n)`, `basis_vector`, `unit_pseudoscalar(n)`, `dual(n)` for n ∉ {2,3}, `symbolic_multivector`) | `Gn` is the oracle the Lean `G3` was derived from | a dimension-general representation — owned by `tasks/lean-general-gn-product-and-hestenes-dot-wedge.md`; this phase is only "prove `G2`/`G3` ≃ the `n = 2`/`3` instances" once that exists |

## Plan

1. Phase 1 (half a day): `StandardPosition.lean` gains `project_sp_eq_proj`/`reject_sp_eq_reject`;
   `Sandwich.lean` gains `sandwich_inverse_sandwich`; coverage table rows for `standardposition`/`functions`.
2. Phase 2 (one to two days): new `Rotor3D.lean` (unit bivector `i`, `rotorOf i θ`, unit, angle theorem via
   standard position, `at(t)`); coverage rows for `transforms` with the plumbing decisions.
3. Phase 3 (one day): new `Frame.lean` (𝒢₃): dependence ⟺ wedge zero (k = 2, 3), Gram–Schmidt
   orthogonality, Hestenes closed form = rejection form.
4. Phase 4: after the Gn task, if ever.
5. Each phase: `make lean` green, docstrings name the Python function (no line numbers), the architecture
   doc's coverage table extended, `proofs/README.md` "What's here" updated, stage.

## Decisions

- Phases are sequenced by cost, not dependency; any of 1–3 can be done alone.
- "Plumbing — no theorem" is a recorded outcome, not a skip: it goes in the coverage table with the one GA
  fact it rests on.

## Open questions

1. `g1.py`: add a tiny `G1` struct for completeness, or record "trivial, not modelled"? Recommend: record
   as not modelled unless the book uses 𝒢₁ examples.
2. Phase 2's angle theorem: state it as a `cos_between` fact (student-facing, matches
   `StudentTrigForms`) or as the stronger coordinate rotation of the in-plane part? Recommend `cos_between`
   plus "⊥ part fixed", which is what `plane_rotation`'s docstring promises.
3. `frame.py` for k = 3 only, or also state k = 2 in 𝒢₂? Recommend both grades for k = 2 (cheap), 𝒢₃ for k = 3.
