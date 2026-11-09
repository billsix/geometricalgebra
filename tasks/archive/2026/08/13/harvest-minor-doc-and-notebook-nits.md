# Minor doc / notebook-convention nits

**Created:** 2026-08-13 · **Completed:** 2026-08-13 (not pursued)

Group D of the 2026-08-13 archive gap-analysis sweep (minor, low re-read value). The sweep
recommended skipping most of these; they were filed so they stayed recoverable. The maintainer
judged them low-value and set them aside (William Emerison Six <billsix@gmail.com>, 2026-08-13);
none was applied, and the doc was archived to keep the active backlog clean. Reopening any of them
would be a new, focused task. (Source docs are under `tasks/archive/`.)

## The items, preserved for reference

- **Notebook `show()` convention** (the one most worth keeping): a cell ending in a bare tuple
  renders the tuple's `repr`, defeating the classes' `_repr_latex_` (and dumping a raw dataclass
  `__repr__` for a multivector inside it); a `show(*values)` / `display(Math(...))` helper renders
  each value as `Type: <latex>`. From `2026/06/06/notebook-display-cells.md`.
- **Rotation LaTeX-label convention:** subscript = "from", superscript = "to" (`R_a^{e_1}` = rotate
  a→e₁). From `2026/07/17/cross-product-derivation-notebook.md`.
- **Symbolic-proof gotchas** for the `|a∧b|=|a||b|sinθ` / `|ab|=|a||b|` identities: symbols must be
  `real=True` (else `√(x²)` won't reduce to `|x|`); in 𝒢₂, `factor` the radicand so sympy sees the
  perfect square (𝒢₃'s radicand is already a sum of squares); `sinθ=√(1−cos²θ)` assumes `sinθ≥0`
  (θ∈[0,π]). From `2026/06/27/wedge-magnitude-sin-notebook.md`.
- **Zero-scale asymmetry:** `uniform_scale(0)` / `scale_non_uniform(…,0,…)` forward is a valid
  (degenerate) transform; only the *inverse* raises (reciprocal of zero). From
  `2026/06/06/transform-type-roundtrip-tests.md`.
- **`from_sympy_expr` → `from_coef` rename:** the old name implied a sympy cast it did not do (it
  was just `from_blade_dict({(): s})`); the lesson is not to reintroduce a name implying a cast.
  This was a historical fact already true in the code, not a to-do. From
  `2026/06/13/magnitude-sympy-cast-to-coef.md`.
