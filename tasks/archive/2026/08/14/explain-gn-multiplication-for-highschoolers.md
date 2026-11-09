# Explain Gn multiplication rules for high schoolers

**Created:** 2026-07-01 · **Completed:** 2026-08-14

Added a plain-language explanation of the geometric-product rules of `Gn` to the general-`Gn` demo
notebook `notebooks/displaymv.py`, written so a high schooler with only basic algebra can follow
it: what a blade is (a product of basis vectors like e₁e₂); the three rules (eᵢeᵢ = 1, the
hardcoded Euclidean signature, stated as a rule rather than glossed over; eᵢeⱼ = −eⱼeᵢ for i ≠ j;
distributivity over addition); and how those rules canonicalize any product of blades, with small
worked examples that run in the notebook, in the notebook's existing style.

## What was added, in order

1. The three-rules section with worked examples (outputs verified in a REPL first).
2. A "longer example" `(e_1*e_3)*(e_3*e_1) → 1` with three parenthesizations, as a lead-in to
   associativity.
3. A formal subsection, placed after "Putting the rules together". It began as a recipe mirroring
   `decrease_grade` in `gn.py` (base / annihilate / swap+negate / in-order-insert) and was reworked
   into "The same rules, written as math" (two identities R1/R2 + sort-with-sign/cancel, chains of
   equalities) after feedback that it read too much like the code.
4. "Where do the plain numbers go? Scalars first.": scalars commute out to the front and multiply
   together, then the basis-vector reduction proceeds as shown.

The associativity proof itself was deferred to
`tasks/archive/2026/08/25/prove-associativity-of-multiplication.md`.

## Verification

- `py_compile` OK, jupytext cell markers intact.
- Rendered headless 2026-08-14: jupytext → `jupyter nbconvert --to html --execute` (Agg backend,
  local gacalc via `PYTHONPATH=src`). All 12 worked examples matched a `Gn` REPL (`e_1*e_1→1`,
  `e_1*e_2→e_12`, `(3e_1+4e_2)²→25`, `(e_1e_2)²→-1`, `(2e_1)(3e_3)(4e_3)(5e_1)→120`, all three
  parenthesizations of `e_1e_3e_3e_1→1`, …); every code-cell output rendered as valid LaTeX; no
  cell raised. The maintainer also checked it in the browser.
- Gotcha: a *full* `displaymv.py` execute timed out (>300 s) on the pre-existing
  `show_mult(symbolic_multivector(n=8), symbolic_multivector(n=9))` cell (2⁸×2⁹ symbolic blades),
  unrelated to this task, so the added-sections slice (the first 289 lines) was rendered instead.
- Noted, out of scope: gacalc's repr showed a leading coefficient `1`, so `e_1*e_2` rendered as
  `1e₁e₂` where the prose says "e_12".
