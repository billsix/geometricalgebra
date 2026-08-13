# Minor doc / notebook-convention nits (low priority — mostly optional)

**Status:** ARCHIVED 2026-08-13 — not pursued. These P8 nits were judged low-value and set
aside (Bill, 2026-08-13); archived to keep the active backlog clean, with the items preserved
here for reference. Reopen a focused task if any becomes relevant. (Note: the
`from_sympy_expr → from_coef` item is a historical fact already true in the code, not a to-do.)
**Priority:** 8
**Difficulty:** 2
**Created:** 2026-08-13
**Origin:** the 2026-08-13 archive gap-analysis sweep (Group D — minor / low-re-read-value
items). The sweep's recommendation was to skip most of these; they're filed here so they
are recoverable rather than lost. Siblings: the four other `harvest-*` / blade-dict tasks.

## Items (each optional — decide per item if ever picked up)

- [ ] **Notebook `show()` convention** *(the one most worth keeping)*. A cell ending in a
      bare tuple renders the tuple's `repr`, defeating the classes' `_repr_latex_` (and
      dumping a raw dataclass `__repr__` for a multivector inside it); use a `show(*values)`
      / `display(Math(...))` helper that renders each value as `Type: <latex>`. *Source:*
      `2026/06/06/notebook-display-cells.md`.
- [ ] **Rotation LaTeX-label convention**: subscript = "from", superscript = "to"
      (`R_a^{e_1}` = rotate a→e₁). *Source:*
      `2026/07/17/cross-product-derivation-notebook.md`.
- [ ] **Symbolic-proof gotchas** for the `|a∧b|=|a||b|sinθ` / `|ab|=|a||b|` identities:
      symbols must be `real=True` (else `√(x²)` won't reduce to `|x|`); in 𝒢₂ `factor` the
      radicand for sympy to see the perfect square (𝒢₃ needs no `factor` — its radicand is
      already a sum of squares); `sinθ=√(1−cos²θ)` assumes `sinθ≥0` (θ∈[0,π]). *Source:*
      `2026/06/27/wedge-magnitude-sin-notebook.md`. *Home:* alongside the
      geometric-product-magnitude-proof note.
- [ ] **Zero-scale asymmetry**: `uniform_scale(0)` / `scale_non_uniform(…,0,…)` forward is
      a valid (degenerate) transform; only the *inverse* raises (reciprocal of zero).
      *Source:* `2026/06/06/transform-type-roundtrip-tests.md`.
- [ ] **`from_sympy_expr` → `from_coef` rename** — the old name implied a sympy cast it
      didn't do (it was just `from_blade_dict({(): s})`). Durable "don't reintroduce a name
      implying a cast" note. *Source:* `2026/06/13/magnitude-sympy-cast-to-coef.md`.
