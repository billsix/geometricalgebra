# Remove the extra hypotheses and no-op tactics from the Lean proofs, then gate on warnings (done)

**Created:** 2026-11-05 (William Emerison Six <billsix@gmail.com>). **Done:** 2026-11-25.

The maintainer asked whether the Lean proofs carry hypotheses or tactics their goals do not need. A 2026-11-05 audit (all 571 theorems, extra linters plus a `clear` test) found little: four statement hypotheses, two no-op `ring`s, two cosmetic `ring`→`ring_nf` spellings and four false-positive warnings. The audit method and the list of hypotheses that look unused but are consumed by `field_simp`/`simp`/`linarith` are in `tasks/reference/lean-for-gacalc.md` ("Reading a theorem's hypotheses, and spotting what is extra") and `tasks/reference/lean-ga-proof-architecture.md` ("Hypotheses: what each kind is for").

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-25)

1. Drop the unneeded `≠ 0` guards: each theorem becomes strictly stronger (the identities hold at `|R|² = 0` because `1/0 = 0`).
2. Gate `make lean` on warnings with `lake build --wfail` in `proofs/check.sh`.

## Result

- **Guards dropped:** `normSq R ≠ 0` from both `sandwich_preserves_wedge` (𝒢₂, 𝒢₃; two callers in `Trig.lean` updated) and both `≠ 0` hypotheses from `inverse_mul`. That cascaded to `sandwich_comp_coord` and `sandwich_comp`, whose only use of those guards was `inverse_mul`. `inverse_mul`'s `congr 1; field_simp` proof needed no change.
- **Already gone by 2026-11-25:** findings #1 and #2 (the no-op `<;> ring`s); a default build emitted none of the 8 warnings the task listed. The two warnings that remained were new since the audit: four `tac1 <;> tac2` warnings in `Bootstrap2D.lean` (two chains) and the unreferenced `hb_isv` in `StandardPosition.lean` (`mul_proj_eq_dot`).
- **Fixed:** `Bootstrap2D.lean`: `ext <;> simp only <;> (ring_nf; try (field_simp; ring))` (`ring_nf` closes some goals outright, so a plain `;` chain fails with "no goals"). `hb_isv` renamed `_hb_isv`: it is a meaning gate the proof consumes implicitly. `CrossStandardPosition.lean` `cross_reduced`: `ext <;> ring_nf`. `ProjectionRotation3D.lean` `vec_mul_bisector_eq_coord`: `try ring_nf` (finding #7 and #8).
- **Gate:** `proofs/check.sh` runs `lake build --wfail`. Proved to fail: a temporary `by simp <;> ring` appended to `GacalcProofs.lean` made the build fail on the unreachable-tactic warning; the file was restored. The gate catches what the compiler warns about, not extras that only the `clear` test finds.
- **Verification:** `lake build --wfail` exits 0 (8960 jobs) on the Lean v4.34.1 toolchain; the full `proofs/check.sh` passed: no `sorry`/`admit`, and 1123 declarations rest only on `propext`, `Classical.choice`, `Quot.sound`.
- **Docs:** `proofs/README.md`, `CLAUDE.md` and `tasks/reference/lean-ga-proof-architecture.md` (gate wording, and the guard-free `sandwich_preserves_wedge`).

## Not done

Promoting the `clear`-test script to `tools/` (plan step 7, optional) was not done; the audit's method stays described in the reference docs.
