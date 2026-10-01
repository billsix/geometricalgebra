# Lean proof — grade projection (`r_vector_part`, `even_part`, `odd_part`)

**Part of:** `tasks/investigate-lean-proofs-for-ga.md`
**From:** `tasks/archive/2026/10/01/lean-coverage-gap-audit.md` (the coverage-map gap audit)

**Status:** DONE 2026-10-02 — `proofs/GacalcProofs/GradeProjection.lean` (G2 + G3): `rVectorPart`
(grade-r selector `⟨a⟩_r`), `evenPart`/`oddPart`; proved `rVectorPart_idem` (idempotence),
`rVectorPart_complete` (the parts reassemble the whole), `even_add_odd` (even+odd = whole). `make lean`
green, sorry-free.
**Priority:** 6
**Difficulty:** 4

## BLUF

Prove the defining properties of the three grade-projection operators — `r_vector_part`
(`base.py:985`, `⟨A⟩_r`), `even_part` (`base.py:1277`) and `odd_part` (`base.py:1290`). None has any
Lean theorem. Grouped into one task because all three are grade selection on the coordinate struct.
"Done" = the projection laws below, 2D + 3D, `make lean` green.

## Approach

Define the grade-r selector on the `G2`/`G3` coordinate struct (keep the coefficients of grade `r`,
zero the rest), and `even`/`odd` as the sums of the even/odd grade parts. Prove: **idempotence**
(`⟨⟨A⟩_r⟩_r = ⟨A⟩_r`), **completeness** (`∑_r ⟨A⟩_r = A`, i.e. `A = ⟨A⟩_0 + ⟨A⟩_1 + …`),
**even+odd = whole** (`even_part A + odd_part A = A`) and **orthogonality of the split**
(`even_part` picks grades {0,2,…}, `odd_part` {1,3,…}). All are `ext <;> ring`-style leaf proofs on
the coordinate representation (mechanical). These are "obvious by construction" but worth stating as
the named leaves other proofs (contractions, inner_product) will lean on.

See the coverage map in `tasks/reference/lean-ga-proof-architecture.md`.
