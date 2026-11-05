# Remove the extra hypotheses and no-op tactics from the Lean proofs, then gate on warnings

**Status:** proposed — needs go-ahead (open questions 1 and 2)
**Priority:** 6
**Difficulty:** 2
**Created:** 2026-11-05 (William Emerison Six <billsix@gmail.com>)

## BLUF

The maintainer asked whether the Lean proofs carry things their goals don't need (hypotheses like `ha`/`hab`
that never seem to be referenced). An audit on 2026-11-05 checked all 32 files and 571 theorems with extra
linters and a `clear` test. **Very little is extra:** most name-absent hypotheses are consumed silently by
`field_simp`/`simp`/`linarith`. What is extra: 4 statement hypotheses, 2 no-op `ring`s, and 2 cosmetic
`ring`→`ring_nf` spellings. There are also 4 false-positive warnings to silence. Done means those are fixed,
`make lean` builds with zero warnings, and (if chosen) a "fail on any warning" gate is on.

## Context (read first)

- `tasks/reference/lean-for-gacalc.md`, section "Reading a theorem's hypotheses, and spotting what is extra".
  It is the plain-language version of this audit and the forward conventions.
- `tasks/reference/lean-ga-proof-architecture.md`, sections "Hypotheses: what each kind is for" and
  "Vacuous `simp` arguments". These cover grade predicates, nonzero guards, meaning gates, and how to read a
  failed delete-and-rebuild.
- `make lean` runs `proofs/check.sh` (`lake build` plus a `sorry`/`admit` grep). The toolchain is Lean and
  Mathlib v4.34.1. The `lake`/`lean` in the sandbox and the cached `proofs/.lake` also work, for a fast loop
  (`lake env lean proofs/GacalcProofs/<File>.lean`).

## Audit method (2026-11-05; reproducible)

1. A copy of `proofs/` with these extra linters turned on in its `lakefile.toml` `[leanOptions]`:
   `weak.linter.unusedTactic`, `unnecessarySimpa`, `unusedSimpArgs`, `unusedVariables.funArgs` /
   `.patternVars`, `unusedRCasesPattern`, `unusedSectionVars`, `unusedDecidableInType`. `lake build` took
   3m34s and exited 0.
2. The `clear` test: for each hypothesis whose name never appears in its proof, insert `clear <name>` as the
   first tactic and compile that file alone. A pass means this proof doesn't need it.
3. Already clean: no `sorry`, no unused `have`, zero unused `simp` arguments (the 2026-10-04 minimizer
   removed 73; `tools/detect_unused_hypotheses.py`).

## Findings to fix

| # | Where (file, declaration) | Extra thing | Evidence | Fix |
|---|---|---|---|---|
| 1 | `G2.lean`, `eq_scalar_of_isScalar` | `<;> ring` after a `simp only` that already closes every goal | `unusedTactic` / `unreachableTactic` | delete `<;> ring` |
| 2 | `ProjectionRotation3D.lean`, the theorem ending `field_simp <;> ring` near the `project_onto_in_plane_self_coord` group | the `ring` never runs | compiler | delete `<;> ring` |
| 3 | `Projection2D.lean`, `sandwich_preserves_wedge` (𝒢₂) | `(hr : normSq R ≠ 0)` | `clear` test passes | see open question 1; callers in `Trig.lean` (two uses) |
| 4 | `Sandwich.lean`, `sandwich_preserves_wedge` (𝒢₃) | `(hr : normSq R ≠ 0)` | `clear` test passes | as #3 |
| 5 | `Sandwich.lean`, `inverse_mul` | both `≠ 0` hypotheses | `clear` test passes | as #3; one caller in `Sandwich.lean` |
| 6 | `ProjectionRotation3D.lean`, `inplane_perp_reject_coord`, `project_perp_reject_coord` and two siblings | `hn` flagged "not explicitly referenced" | false positive: `rw … at hn` shadows the binder | keep `hn`; restructure so the original is used, or silence the linter at the site with a comment |
| 7 | `CrossStandardPosition.lean`, `cross_reduced` | `ext <;> ring` falls back to `ring_nf` on all 8 goals (Lean prints "Try this: ring_nf") | compiler info | write `ext <;> ring_nf` |
| 8 | `ProjectionRotation3D.lean`, `vec_mul_bisector_eq_coord` | `try ring` falls back to `ring_nf` on one goal | compiler info | optional: `ring_nf` there |

Items 3–5 share one proof shape: pull out the `1/|R|²` factors, `congr 1`, `field_simp`. The identity holds
at `|R|² = 0` too, because in Lean `1/0 = 0`, so `inverse R = 0` and both sides are 0.

**Needed even though never named** (the `clear` test fails; no action, at most a "used by field_simp" comment):

- `rotYZ_aligns_yz hk`, `rotXY_aligns_xy hk`, `rotXZ_aligns_xz hm`, `rotPlane_aligns hm`
- `mul_vec_inverse_self hx`, `reject_perp_dot ha` (2D and 3D), `fhat_that_eq_reverse_mul_inverse hr`,
  `sandwich_ahat ha`
- `rotateFromTo_carries hmb`, `rot_from_to h`, `rotorFromVectors_uvec hc` (via `linarith`)
- `inverse_inverse ha` (2D and 3D), `sandwich_carries_from_to hr` (2D and 3D)
- `proj_onto_x_axis hm` (both files), `area_eq_mag_mul_sin ha hb`, `volume_eq_mag_mul_cos ha0 hbc0`

**Intentionally unused, already marked with `_`** (meaning gates in `StudentTrigForms.lean`): `dual_perp`,
`cross_perp_left/right`, `parallel_smul`, `dual_wedge_perp_left/right`. Leave them.

## Plan

1. Fix #1, #2 and #7 (and #8 if wanted).
2. Apply the answer to open question 1 to #3–#5 and update their callers.
3. Resolve #6.
4. `make lean` must report **zero warnings**. Today a default build emits 8: #1, #2 and #6, some twice.
5. If open question 2 says yes, turn on the gate and confirm it fails on a deliberately added `<;> ring`, then
   remove that.
6. Update the inventory or coverage sections of `lean-ga-proof-architecture.md` if a theorem's signature
   changed. Mention a dropped hypothesis in `CHANGELOG.md` only if the Python side cites these theorems in a
   way a reader would notice (the Lean proofs are not a published API).
7. Optional, as a reusable tool: promote the `clear`-test script to `tools/` (e.g.
   `tools/lean_clear_test.py`) next to `tools/detect_unused_hypotheses.py`, and note it in the reference doc.

## Open questions

1. For #3–#5 (the `≠ 0` guards the proofs don't need): (a) drop them, which makes each theorem strictly
   stronger; or (b) keep them renamed `_hr`, as "meaning gates" saying the statement is only interesting when
   `R` is invertible? Recommendation: (a). The architecture doc's rule is "carry only what the proof uses",
   and these are identities, not trig statements whose meaning needs a gate.
2. Add a "fail on any warning" gate to `make lean`: (a) `lake build --wfail` in `proofs/check.sh`, (b)
   `warningAsError = true` in `lakefile.toml`, or (c) no gate? Recommendation: (a). It is one line, and
   `make lean` only runs on `v*` tags in CI, so it adds no per-push cost. Note that it can't catch #3–#5-style
   extras, which only the `clear` test finds.
