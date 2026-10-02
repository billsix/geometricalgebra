# Lean proof — grade projection (`r_vector_part`, `even_part`, `odd_part`)

**Part of:** `tasks/investigate-lean-proofs-for-ga.md`
**From:** `tasks/archive/2026/10/01/lean-coverage-gap-audit.md` (the coverage-map gap audit)

**Status:** DONE 2026-10-02. **Priority:** 6 **Difficulty:** 4

## Summary

The grade-projection operators — `r_vector_part` (`base.py:985`, `⟨A⟩_r`), `even_part` (`base.py:1277`)
and `odd_part` (`base.py:1290`) — had no Lean theorem; grouped here because all three are grade
selection on the coordinate struct. `proofs/GacalcProofs/GradeProjection.lean` (G2 + G3) defined the
grade-r selector `rVectorPart` (keep the grade-`r` coefficients, zero the rest) and `evenPart`/`oddPart`
(sums of the even/odd grade parts), and proved their laws: `rVectorPart_idem` (idempotence),
`rVectorPart_complete` (the parts reassemble the whole), and `even_add_odd` (even + odd = whole) —
`ext <;> ring` leaf proofs on the coordinate representation. `make lean` green, sorry-free. These are
the named grade-selection leaves the contraction proofs build on.

Coverage map: `tasks/reference/lean-ga-proof-architecture.md`.
