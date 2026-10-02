# Lean proof — left & right contraction (`left_contraction`, `right_contraction`)

**Part of:** `tasks/investigate-lean-proofs-for-ga.md`
**From:** `tasks/archive/2026/10/01/lean-coverage-gap-audit.md` (the coverage-map gap audit)

**Status:** DONE 2026-10-02. **Priority:** 6 **Difficulty:** 5

## Summary

gacalc's `left_contraction` (`<`, `base.py:862`, grade `m−k`) and `right_contraction` (`>`,
`base.py:907`, grade `k−m`; Taylor 2021 p.103) were entirely absent from the proofs.
`proofs/GacalcProofs/Contractions.lean` (G3) defined `leftContraction`/`rightContraction` as
`⟨AB⟩_{m−k}`/`⟨AB⟩_{k−m}` (operand grades explicit) and proved `leftContraction_vec_vec` /
`rightContraction_vec_vec` (both reduce to the scalar `dot` for two vectors) and
`leftContraction_scalar_vec` (`α ⌋ b = α·b`) — the grade-0 inclusion that distinguishes a contraction
from the Hestenes `inner_product`, per `tasks/reference/contraction-and-dot-definitions.md`. `make lean`
green, sorry-free. The vector·bivector = `inner_vb` equality was not needed to characterise them and was
left as a possible extension.

Coverage map: `tasks/reference/lean-ga-proof-architecture.md`.
