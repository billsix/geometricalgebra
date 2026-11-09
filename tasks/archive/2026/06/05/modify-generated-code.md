# Sort generated product terms by grade

**Created:** 2026-06-04 · **Completed:** 2026-06-05

The additive terms in each generated closed-form component of `g1/g2/g3.py` were reordered **by
grade** (scalars, then vectors, then bivectors, …) instead of sympy's roughly lexicographic order,
in which `e_12` sorted before `e_2`. For example the `scalar` component of the geometric product
now reads `self.scalar * rhs.scalar + self.e_1 * rhs.e_1 + self.e_2 * rhs.e_2 - self.e_12 *
rhs.e_12`. This was a presentation-only change: computed values are unchanged.

## Decisions

- **Composite sort key** (decided 2026-06-04): `(grade(left), left_indices, grade(right),
  right_indices)`, so within a grade blades sort by index ascending (`e_1` before `e_2`, `e_12`
  before `e_13`).
- The ordering applies to `_geometric_product`, `inner_product` and `outer_product` alike, since all
  three share `format_assignment`.
- Terms bearing a `cse` temporary (no `a_`/`b_` symbol) sort last; the products produced none at the
  time. Single-term and constant components are unaffected.
- `_repr_latex_` ordering was left as-is, as the maintainer wanted: it lives in `base.py` and
  re-sorts blades itself.

## What changed

- `tools/gen_specialized.py` gained `blade_of_field` (the inverse of `field_name`) and
  `term_grade_key`; `format_assignment` sorts `as_ordered_terms()` by that key for both the inline
  and wrapped forms, keeping the existing sign handling.
- **The generator now self-formats.** Regenerated `g*.py` had needed a separate manual ruff pass,
  and two files were once committed unformatted. `main()` now calls a `ruff_format` helper that runs
  `ruff check --fix` + `ruff format` on the files it writes (best-effort; warns if ruff is absent),
  so a regen is one self-contained step. `CLAUDE.md` (Code generation + Dev workflow) was updated to
  say so and to document the two generator-driven presentation behaviors (grade-ordered terms via
  `term_grade_key`; per-method docstrings copied from `base.py` via `inspect.getdoc`).

## Verification

The regenerated diff was pure reordering (92 insertions / 92 deletions); a second regen was
byte-identical; `_repr_latex_` output was byte-identical before and after; `ruff check`, `ty check
src`, and the full suite (124 = 118 tests + 6 doctests) were green.
