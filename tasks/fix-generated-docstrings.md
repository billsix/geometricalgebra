# Fix the generated docstrings that state the math wrongly

**Status:** proposed — needs go-ahead (approved in session 2026-11-09; in progress)
**Priority:** 3
**Difficulty:** 3
**Created:** 2026-11-09
**Source:** `tasks/review/2026/11/08/repo-review.md` §5.3

## BLUF

Several docstrings that `tools/gen_specialized.py` emits into g1–g5 contradict what the methods do.
Done means each says what the method returns, the math follows `CLAUDE.md`'s notation rules, the
generator stays deterministic, and the doctests pass.

## Context

Each was checked by running it (review §5.3), and re-checked on 2026-11-09:

- **`scalar|right_contraction`** says "x ⌊ s … the operand scaled". The method computes `s ⌊ x`,
  which is 0 for a vector and `s * x` for a scalar.
- **`bivector|right_contraction`** says "grade |C|−|B|". `B ⌊ C` has grade |B|−|C|
  (`e₁₂ ⌊ e₁ = −e₂`).
- **`scalar|dual`** says "the scalar times the pseudoscalar". It is `s * i⁻¹`
  (`Scalar(1).dual() == −e₁₂` in 𝒢₂).
- **`versor|sandwich`** has `R * x * R⁻¹` in the summary and `R * x * R̃` under Returns. For a
  non-unit versor only the first is right.
- **`I_DOC`/`PLANE_DOC`** say a versor `cos(t/2) − sin(t/2) * i` returns `i`. It returns `−i`: the
  plane `I` of `R = r * (cos(θ) + I * sin(θ))`.
- **Juxtaposition:** `a b = a·b + a∧b`, `R R̃ = 1`, `(a ∧ b) I₃⁻¹`.

`tasks/reference/generated-docstrings.md` describes the `CUSTOM_METHOD_DOCS` machinery.

## Plan

- [ ] Correct each text in the generator. Regenerate g1–g3.
- [ ] Gate: the doctests in `--doctest-modules`; determinism (regenerate twice, `cmp`);
  `tools/check_doc_regions.py`; `ty` with the generated modules.

## Open questions

None.
