# Lean proof — measures (`area`, `volume`, `signed_area`, `content`)

**Part of:** `tasks/investigate-lean-proofs-for-ga.md`
**From:** `tasks/archive/2026/10/01/lean-coverage-gap-audit.md` (the coverage-map gap audit)

**Status:** DONE 2026-10-02 (general `content` deferred — see below). **Priority:** 5 **Difficulty:** 5

## Summary

gacalc's named measures (`measure.py`, Williamson & Trotter 1979) lacked Lean theorems.
`proofs/GacalcProofs/Measures.lean` proved, keeping everything squared and structural: G3 `area = |a∧b|`
— `area_sq_vec` (= `normSq (a∧b)`) and `normSq_wedge_eq_lagrange` (`|a∧b|² = |a|²|b|² − (a·b)²`, from
`lagrange_property`); G3 `volume = |a∧b∧c|` — `volume_sq_vec = signedVolume²` (via
`normSq_wedge3_eq_signedVolume_sq`); G2 `signedArea = a₁b₂ − a₂b₁` — `signedArea_sq`
(`|signed_area| = area`). `signed_volume` was already covered (`Cross.dot_cross_eq_signedVolume = det[a,b,c]`).
`make lean` green, sorry-free.

The general `content` (`|a₁∧…∧aₖ|`, arbitrary `k`) was deferred: it needs a dimension-general `Gn` Lean
representation that does not exist (these proofs use concrete G2/G3 structs). Its prerequisite is
`tasks/lean-general-gn-product-and-hestenes-dot-wedge.md` (deliberately deferred); `area` (k=2) and
`volume` (k=3) are its concrete instances, and a `-- TODO` pointing at that task sits in `Measures.lean`.

Coverage map: `tasks/reference/lean-ga-proof-architecture.md`.
