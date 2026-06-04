# Add Hestenes math notation to method docstrings (G1/G2/G3/Gn)

**Status:** in-progress
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

- House style to match: many methods already "cite the page/equation number they implement"
  (per CLAUDE.md). Mirror that exactly.
- Generated docstrings must change in `tools/gen_specialized.py`, never in the `g*.py` output.

## Open questions

- Where do the docstrings for the generated classes' methods originate today — fixed strings in the
  generator, or copied from `Gn`/`base`? (Determines where to edit.)
- Which edition / printing of Hestenes & Sobczyk for page numbers? Confirm the citation convention
  the existing docstrings use (page vs equation number).
- Should methods Hestenes gives *no* notation for get a brief "(no standard Hestenes notation)" note,
  or just be left untouched?
