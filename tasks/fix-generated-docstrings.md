# Fix the generated docstrings that state the math wrongly

**Created:** 2026-11-09 · **Completed:** 2026-11-09
**Source:** `tasks/review/2026/11/08/repo-review.md` §5.3

## What was wrong, and what changed

Each claim was checked against the method on 2026-11-09 before the text was changed; all edits are in
`tools/gen_specialized.py`.

- **`scalar|right_contraction`** said "x ⌊ s … the operand scaled". The method is `s ⌊ x`
  (`Scalar(2).right_contraction(e_1) == 0`, `Scalar(2).right_contraction(Scalar(3)) == 6`). It now
  says: grade `0 − |x|`, so scalar multiplication for a scalar `x`, and 0 otherwise.
- **`bivector|right_contraction`** said "grade |C|−|B|". It is |B|−|C| (`e₁₂ ⌊ e₁ = −e₂`).
- **The `scalar|dual` builder (`_scalar_dual_doc`)** said "the scalar times the pseudoscalar". It is
  `s * i⁻¹`; its own example, `Scalar(1).dual() == -1 * Bivector.e_12`, shows that.
- **`versor|sandwich`**'s Returns said `R * x * R̃`. It now says `R * x * R⁻¹`, matching the summary
  and correct for a non-unit versor.
- **`PLANE_DOC` and `I_DOC`** said the rotor `cos(t/2) − sin(t/2) * i` returns `i`. It returns `−i`
  (measured: `Versor(cos 0.5 − sin 0.5 * e₁₂).i() == −e₁₂`). Both now state the convention,
  `R = r * (cos(θ) + I * sin(θ))` returns `I`, and give the `−i` case. This also matches `CLAUDE.md`'s
  Operators line.
- **Notation** (`CLAUDE.md` › "Math notation for readers"): `R R̃ = 1` → `R * R̃ = 1`; `a b = a·b + a∧b`
  → `a * b = …` (two docstrings); `(a ∧ b) I₃⁻¹` → `(a ∧ b) * I₃⁻¹`.

## Verification

- Regenerated g1–g3 twice: `cmp` identical.
- `tools/check_doc_regions.py`: OK.
- The generated modules' doctests (`--doctest-modules` on g1–g3): 170 passed.
- `ty check --no-respect-ignore-files src`: clean. `ruff`: clean.
