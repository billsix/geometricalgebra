# Add Hestenes math notation to method docstrings (G1/G2/G3/Gn)

**Status:** complete
**Completed:** 2026-06-05
**Started:** 2026-06-04

## Goal

Extend the math-notation docstrings you liked on the geometric/inner/outer products to the *other*
methods across `g1.py`, `g2.py`, `g3.py`, and `gn.py` (and the shared `base.py`). Study every
public method — `r_vector_part`, scalar product, `reverse`, `dual`, `project`/`reject`/`reflect`,
`inner_product`/`outer_product`, `magnitude`, `inverse`, etc. — determine which ones Hestenes &
Sobczyk give explicit notation for in *Clifford Algebra to Geometric Calculus*, and add that
notation (with the page/equation citation, matching the existing house style) into each method's
docstring as part of a short explanation. Methods Hestenes has no special notation for are left as
prose. Keep the generated files (`g1/g2/g3.py`) consistent by adding the notation in the **generator**
(`tools/gen_specialized.py`) where the docstrings originate, not by hand-editing generated output.

## Plan

- [ ] Inventory the math-notation docstrings already present (the products in `gn.py` / generated
      classes) to capture the exact house style and citation format to match.
- [ ] Enumerate every public method in `base.py`, `gn.py`, and the generated `g*.py`.
- [ ] For each, decide whether Hestenes defines a notation (e.g. ⟨A⟩ᵣ for r-vector part, A∗B or
      A·B for scalar/inner product, Ã for reverse, A* for dual, A∧B for outer) and find the
      page/equation.
- [ ] Add the notation + explanation to docstrings: shared methods in `base.py`/`gn.py` directly;
      per-class generated docstrings via `tools/gen_specialized.py`, then regenerate.
- [ ] Regenerate `g1/g2/g3.py`, run ruff + ty + the full suite; confirm clean and green.

## Notes / decisions

- **Design (2026-06-05): single source of truth = `base.py` docstrings.** Hestenes glyph notation is
  written into the shared `AbstractMultiVector` method docstrings in `base.py`. The generator copies
  each base method's docstring onto its generated override via `inspect.getdoc(AbstractMultiVector,
  <name>)` — so the specialized `G1`/`G2`/`G3` methods carry *identical* notation and can never drift.
  No hand-maintained notation strings in the generator.
- House style to match: existing docstrings cite "from Hestenes and Sobczyk, Clifford Algebra to
  Geometric Calculus, page X, equation Y". Keep that verbatim; prepend a one-line notation +
  description above it.
- Notation vocabulary used: geometric product `A B` (juxtaposition), inner `A · B`, outer `A ∧ B`,
  scalar product `A ∗ B = ⟨A B⟩`, grade-r part `⟨A⟩ᵣ`, scalar part `⟨A⟩ = ⟨A⟩₀`, reverse `Ã`,
  magnitude `|A|`, inverse `A⁻¹`, dual `A* = A I⁻¹`, even/odd parts `A⁺`/`A⁻`, unit pseudoscalar `i`,
  unit/normalized `Â`, projection `P_B(A)`, rejection `P_B^⊥(A)`.
- Generated methods that pick up base docstrings: `_geometric_product`, `inner_product`,
  `outer_product`, `scalar_part`, `r_vector_part`, `reverse`, `even_part`, `odd_part`, `dual`,
  `unit_pseudoscalar`. (`emit_docstring` is a no-op for any override whose base has no docstring, so
  pure plumbing stays clean.)

## Open questions (resolved)

- *Where do generated method docstrings originate?* They didn't exist — generated methods were
  emitted docstring-free. Now copied from `base.py` via `inspect.getdoc` (above).
- *Edition / citation convention?* Reuse the page/equation numbers already committed in `base.py`;
  don't invent new ones. Methods without a confident page get notation + definition, no citation.
- *Methods with no Hestenes notation?* Left untouched (prose); no "(no standard notation)" noise.
