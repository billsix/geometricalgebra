# Express grade projection as basis-blade combinations in the Lean proofs

**Status:** done. **Priority:** 7. **Difficulty:** 5.
**Completed:** 2026-10-03 (William Emerison Six <billsix@gmail.com>).

Rewrote G2's `rVectorPart` (`proofs/GacalcProofs/GradeProjection.lean`) from positional coordinate
struct-literals to **linear combinations of the basis blades** — the Lean mirror of gacalc's "build
from the basis constants" rule:
`0 => smul a.s one`, `1 => add (smul a.c1 e_1) (smul a.c2 e_2)`, `2 => smul a.c12 e_12`,
`_ => ⟨0,0,0,0⟩`. Proof cost was modest and localized: `rVectorPart_idem` lost its one-line
`rcases … <;> rfl` (now `… <;> simp only [rVectorPart, add, smul, one, e_1, e_2, e_12] <;> ext <;>
ring`), and `rVectorPart_complete`/`even_add_odd` gained those constants in their `simp` sets — no new
lemmas or bridge machinery.

**G3's `rVectorPart` was deliberately kept as a struct-literal** (per-case decision, maintainer
approved): its grade-2 arm would be a noisier nested three-term `add`, and the basis form would push
proof churn into `Contractions.lean` — readability would drop while proof cost rose. So the basis form
was applied only where it reads better (G2). Verified `make lean` green (full `lake build`, no
`sorry`/`admit`). Convention recorded in `tasks/reference/lean-ga-proof-architecture.md`
("Grade-projection form").
