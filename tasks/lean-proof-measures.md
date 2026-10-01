# Lean proof — measures (`area`, `volume`, `signed_area`, `content`)

**Part of:** `tasks/investigate-lean-proofs-for-ga.md`
**From:** `tasks/archive/2026/10/01/lean-coverage-gap-audit.md` (the coverage-map gap audit)

**Status:** proposed — needs go-ahead
**Priority:** 5
**Difficulty:** 5

## BLUF

Prove gacalc's named measures (`measure.py`, Williamson & Trotter 1979) against their geometric
meaning: `area` (`|a∧b|`, line 151), `volume` (`|a∧b∧c|`, 172), `signed_area` (the 2D determinant,
252) and the general `content` (78). Grouped into one task. **`signed_volume` is already covered**
(`dot_cross_eq_signedVolume` in `Cross.lean` = `det[a,b,c]`) — do not re-prove it. "Done" = the area/
volume/signed_area/content characterisations (2D + 3D where applicable), `make lean` green.

## Approach

Much of the scaffolding exists. `area = |a∧b|`: `normSq_wedge_vec` already gives `|a∧b|²` (the squared
form — stay squared to avoid `√`), so state `area² = normSq (wedge a b)` and relate it to the Lagrange
form `|a|²|b|² − (a·b)²` (`lagrange_property`). `signed_area` (2D) = the oriented wedge coefficient
`a₁b₂ − a₂b₁` (`wedge_antisymm`/the G2 `wedge` coefficient) with `|signed_area| = area`. `volume` =
`|a∧b∧c|` where the trivector coefficient is exactly `signedVolume` (`Cross.lean`), so
`volume = |signedVolume|`. General `content` = `|a₁∧…∧aₖ|` — state it where a concrete `G2`/`G3`
instance makes it tractable (full `n` likely waits on the general-`Gn` task). Reuse the wedge leaves;
keep proofs squared and structural.

See the coverage map in `tasks/reference/lean-ga-proof-architecture.md`.
