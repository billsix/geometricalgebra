# Explain Gn multiplication rules for high schoolers

**Status:** in-progress
**Started:** 2026-07-01

## Goal

Add a plain-language explanation of the multiplication (geometric product) rules
of `Gn` to the general-`Gn` demo notebook (`notebooks/displaymv.py`), written so a
high schooler with only basic algebra can follow it. Cover, in accessible terms:
what a blade is (a product of basis vectors like e₁e₂), the three rules that define
the geometric product — eᵢeᵢ = 1 (a basis vector squares to 1, Euclidean signature),
eᵢeⱼ = −eⱼeᵢ for i ≠ j (swapping adjacent distinct factors flips the sign), and
distributivity over addition — and how those rules let you canonicalize/reduce any
product of blades. Keep the tone pedagogical and concrete, matching the notebook's
existing style, ideally with small worked examples that run in the notebook.

## Plan

- [ ] Read `notebooks/displaymv.py` to match its existing style/structure
- [ ] Draft the plain-language multiplication-rules section (blades, the 3 rules, canonicalization)
- [ ] Add small worked examples that execute against `Gn`
- [ ] Verify the notebook still runs / renders

## Notes / decisions

- "The gn notebook" = `notebooks/displaymv.py` (the general `Gn` jupytext demo, per CLAUDE.md).
- Euclidean signature is hardcoded (eᵢeᵢ = +1) — the explanation should state this as the rule, not gloss over it.

## Open questions
