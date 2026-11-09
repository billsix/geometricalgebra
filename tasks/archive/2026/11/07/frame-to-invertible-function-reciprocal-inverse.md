# `Frame.to_invertible_function`: a reciprocal-frame inverse, chosen by keyword, as the default 

**Completed:** 2026-11-07

Requested by William Emerison Six <billsix@gmail.com>, 2026-11-07:

> implement in Frame the to_invertible_function, make that one have two ways of doing it, specified by
> a keyword argument and a default value. I want an option to use the reciprocal frame as a way to do the
> inverse function as well, and I want it to be the default option. … unit tests to cover both methods,
> and to show that they are equivalent, symbolically.

The math is in `tasks/reference/frames-qr-and-reciprocal-frames.md`, under "The relation to Hestenes'
reciprocal frame" ("Both inverses, chosen by keyword").

## What was done

- **The keyword:** `Frame.to_invertible_function(*, inverse_method: Literal["reciprocal", "peel"] =
  "reciprocal")`.
  - It is keyword-only. It names the inverse because the forward map is the same either way.
  - A `match` chooses the inverse, and its default branch raises `ValueError` for an unknown name.
- **`"reciprocal"` (the default):**
  - the reciprocal vectors (`Frame.reciprocal_vectors()`, from
    `tasks/archive/2026/11/07/reciprocal-frame-hestenes.md`) are computed once, when the map is built;
  - the inverse is the map `x = Σ_i (vⁱ · y) * e_i`, with no recursion.
- **`"peel"`:** the earlier back-substitution from the last frame vector, unchanged.
- The docstring explains both methods with the same worked example, and has a doctest for each.
- **A bug that predates this work, fixed on the way:** `prefix_blades`, and therefore
  `make_orthogonal_frame_hestenes` and its inverse variant, returned all-zero blades on the graded
  `g2`/`g3` types.
  - The cause: they seeded the wedge with `type(v).one()`, which for a graded `Vector` is the zero
    vector (the type has no scalar slot).
  - It surfaced when the reciprocal default ran the existing graded-type tests through
    `reciprocal_frame`, which had the same seed.
  - The fix is a private `_scalar_one(v)`, `type(v.dot(v)).one()`: `Scalar_n.one()` on the graded types,
    and `Gn.one()` on `Gn` as before. It is used in all three places.
  - `tests/test_frame.py` gained a graded-type test for `prefix_blades` and one for `reciprocal_frame`.
- **Tests (`tests/test_frame_class.py`):**
  - the round trips run under both methods: 2D and 3D symbolic, concrete graded frames with symbolic
    input, and float;
  - the two inverses are equal on a general symbolic vector, for general 2D and 3D frames;
  - `"reciprocal"` is the keyword-only default (checked through `inspect.signature`);
  - an unknown method raises `ValueError`;
  - the first task's two "reciprocal coordinates equal the peel" tests were replaced by the equivalence
    tests, which cover them.
- `CHANGELOG.md` `[Unreleased]` entries: Added (the keyword; float results may differ in the last bits,
  because the default now takes a different path) and Fixed (the graded `prefix_blades`).
- `tasks/frame-inverse-head-first-recursion.md` records the maintainer's choice of both methods, with
  the reciprocal as the default. That task's remaining question is whether to rewrite the `"peel"`
  method head-first.

## Not done

Per the three-forms rule (`CLAUDE.md`), the request was for code and symbolic tests. No Lean theorem and
no book page were written.
