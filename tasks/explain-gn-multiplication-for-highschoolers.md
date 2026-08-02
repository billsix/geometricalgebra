# Explain Gn multiplication rules for high schoolers

**Status:** in-progress
**Priority:** 3
**Difficulty:** 3
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

- [x] Read `notebooks/displaymv.py` to match its existing style/structure
- [x] Draft the plain-language multiplication-rules section (blades, the 3 rules, canonicalization)
- [x] Add small worked examples that execute against `Gn` (outputs verified in a REPL first)
- [x] Verify the notebook still parses (`py_compile` OK, jupytext cell markers intact)
- [ ] Render in Jupyter to eyeball the LaTeX/markdown (needs `make shell` / notebooks extra — not done headless)

## Notes / decisions

- "The gn notebook" = `notebooks/displaymv.py` (the general `Gn` jupytext demo, per CLAUDE.md).
- Euclidean signature is hardcoded (eᵢeᵢ = +1) — the explanation should state this as the rule, not gloss over it.
- Added, in order: (1) the three-rules section w/ worked examples; (2) a "longer example"
  `(e_1*e_3)*(e_3*e_1) → 1` with three parenthesizations, as a lead-in to associativity;
  (3) an optional "stated as a recipe" subsection mirroring `decrease_grade` in `gn.py`
  (four cases: base / annihilate / swap+negate / in-order-insert), kept readable rather than
  a literal code transcription. Placed after "Putting the rules together", before the longer example.
- Reworked the formal subsection from a program-like case list into "The same rules, written
  as math" (two identities R1/R2 + sort-with-sign/cancel, chains of equalities) after feedback
  that it read too much like the code.
- Added "Where do the plain numbers go? Scalars first." — scalars commute out to the front and
  multiply together, then the basis-vector reduction proceeds as shown. Placed after the
  written-as-math subsection.
- The associativity *proof* itself is deferred to the follow-up task [[prove-associativity-of-multiplication]].

## Open questions
