# Add Hestenes math notation to method docstrings (G1/G2/G3/Gn)

**Created:** 2026-06-04 · **Completed:** 2026-06-05

The math-notation docstrings already on the geometric/inner/outer products were extended to the
other public methods (`r_vector_part`, scalar product, `reverse`, `dual`,
`project`/`reject`/`reflect`, `magnitude`, `inverse`, …) across `base.py`, `gn.py` and the
generated `g1/g2/g3.py`. Each method for which Hestenes & Sobczyk (*Clifford Algebra to Geometric
Calculus*) give a notation got that notation plus a short explanation; methods with no Hestenes
notation were left as prose.

## Decisions (2026-06-05)

- **Single source of truth = the `base.py` docstrings.** The glyph notation was written into the
  shared `AbstractMultiVector` method docstrings, and the generator copies each base docstring onto
  its generated override via `inspect.getdoc(AbstractMultiVector, <name>)`, so `G1`/`G2`/`G3` carry
  identical notation and cannot drift. No notation strings are hand-maintained in the generator.
  (Before this, generated methods were emitted with no docstrings at all.) `emit_docstring` is a
  no-op for an override whose base has no docstring, so pure plumbing stays clean.
- **Citation convention:** the existing house style ("from Hestenes and Sobczyk, Clifford Algebra to
  Geometric Calculus, page X, equation Y") was kept verbatim, with a one-line notation + description
  prepended. Only page/equation numbers already committed in `base.py` were reused; methods without
  a confident page got notation + definition and no citation.
- **No-notation methods** were left untouched, with no "(no standard notation)" noise.
- **Vocabulary:** geometric product `A B`, inner `A · B`, outer `A ∧ B`, scalar product
  `A ∗ B = ⟨A B⟩`, grade-r part `⟨A⟩ᵣ`, scalar part `⟨A⟩ = ⟨A⟩₀`, reverse `Ã`, magnitude `|A|`,
  inverse `A⁻¹`, dual `A* = A I⁻¹`, even/odd parts `A⁺`/`A⁻`, unit pseudoscalar `i`, unit `Â`,
  projection `P_B(A)`, rejection `P_B^⊥(A)`.
- Generated methods that pick up base docstrings: `_geometric_product`, `inner_product`,
  `outer_product`, `scalar_part`, `r_vector_part`, `reverse`, `even_part`, `odd_part`, `dual`,
  `unit_pseudoscalar`.

## Verification

`g1/g2/g3.py` were regenerated from `tools/gen_specialized.py`; ruff, ty and the full suite were
run clean and green.
