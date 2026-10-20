# Prove the composition of two 2D rotations commutes (Lean + prose), and cite it in the rotate-from-a-to-b collapse

**Status:** done 2026-10-20 — all four deliverables already present in the repo (the 2026-10-08 spec
was implemented since, as part of the rotate-from-a-to-b proof pages); verified and archived.
**Priority:** 5
**Difficulty:** 2
**Created:** 2026-10-08 (William Emerison Six <billsix@gmail.com>)
**Done:** 2026-10-20 (William Emerison Six <billsix@gmail.com>: "I go with your recommendations")

## BLUF

The "rotate from a to b" collapse relies on **2D rotations commuting** (`R₁ ∘ R₂ = R₂ ∘ R₁`). This
task specified backing that in all three forms + citing it. On pickup, **all four deliverables were
already in the repo** (implemented alongside `proof-rotate-from-a-to-b` since the 2026-10-08 spec), so
nothing needed implementing — verified present and correct, then archived. The math: 2D rotations add
their angles and addition commutes, so order doesn't matter.

## Result — already complete (verified 2026-10-20)

1. **Lean** — both theorems exist and are **sorry-free** (`make lean` green, whole corpus, 2026-10-20):
   - `rot_comm` — `proofs/GacalcProofs/Rotation2D.lean:74` — `rot θ (rot φ v) = rot φ (rot θ v)`,
     proved `rw [rot_add, rot_add, add_comm]` (the angle form).
   - `rotPlane_comm` — `proofs/GacalcProofs/RotateFromTo2D.lean:44` — the cosine-and-sine form the
     collapse actually uses, proved from `rotPlane_comp` + `ring`.
2. **Symbolic Python** — `book/docs/notebooks/proof-rotate-from-a-to-b.py` has a
   "## 1. Rotations commute (in 2D)" section running the check with symbolic coordinates.
3. **Prose** — `book/docs/proof-rotate-from-a-to-b.rst` "The collapse" derives it in coordinates
   (rotate by θ₁ then θ₂ = rotate by θ₁+θ₂, and θ₁+θ₂ = θ₂+θ₁).
4. **Citation** — that same section cites both Lean theorems by name (`rot_comm`, `rotPlane_comm`)
   and the companion notebook, so the collapse is justified, not asserted.

Verification this session: `make lean` → `Build completed successfully`, `[lean] no sorry/admit`,
`[lean] OK` (covers both theorems). The notebook + prose + citations are present and were built via
`make docs` at their original commit; not re-run here (this session's image is the lean-only variant
without `BUILD_DOCS`), but they are the committed, already-rendered artifacts.

Note vs the original spec: the prose landed on the collapse page (`proof-rotate-from-a-to-b.rst`)
rather than `proof-rotate.rst` — which is where it is used and cited, so it satisfies both the "prose"
and "reference it in the collapse" items in one place.

## See also

- `proofs/GacalcProofs/Rotation2D.lean` (`rot`, `rot_add`, `rot_comm`) and `RotateFromTo2D.lean`
  (`rotPlane_comp`, `rotPlane_comm`, `rotPlane_conj_collapse`).
- `book/docs/proof-rotate-from-a-to-b.rst` "The collapse" + `book/docs/notebooks/proof-rotate-from-a-to-b.py`.
