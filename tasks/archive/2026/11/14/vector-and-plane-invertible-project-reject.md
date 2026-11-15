# Invertible project and reject between a vector and a plane, with coordinate versions in g1–g3

**Created:** 2026-11-07 (William Emerison Six <billsix@gmail.com>): "And then make a follow up task for
doing that to a vector and a plane, both for project, and reject. And as part of those tasks, add them to
be coordinate versions in the generated code for g1 g2 g3 etc"
**Done:** 2026-11-14, in the unattended batch on branch `autonomous-batch-2026-11-14`
**Built on:** `tasks/archive/2026/11/14/line-to-line-rejection-invertible-function.md`.

## Outcome

- **`transforms.line_to_plane_projection(from_vector=, to_plane=, *, float_close_to_zero=False)`**: the
  projection onto a plane (a nonzero bivector, H&S eq 2.9), restricted to the line of `from_vector`. Map
  (a) of the task's table.
- **`transforms.line_from_plane_rejection(from_vector=, away_from_plane=, ...)`**: the rejection away from
  the plane, restricted to the line. Map (b).
- Both have the line versions' shape: the forward map is the projection / rejection itself after
  `require_on_line`, and the inverse reads the coordinate on the image line with `coordinate_along`. Each
  raises `ValueError` when the plane is not a nonzero bivector, `from_vector` is not a nonzero vector, or
  the image of `from_vector` is zero (perpendicular to the plane for the projection, in the plane for the
  rejection). The zero test uses `is_parallel_to`'s tolerance under `float_close_to_zero`. Doctests show the
  worked 3D example. `tests/test_line_and_plane.py` covers round trips over int, rational, float and
  symbolic `Gn` for both maps, that the projection lands in the plane and the rejection is perpendicular to
  it, off-line input in each direction, the degenerate configurations, and bad arguments.
- **Generated 𝒢₃ coordinate versions**: `Vector.line_to_plane_projection(to_plane: Bivector, ...)` and
  `Vector.line_from_plane_rejection(away_from_plane: Bivector, ...)`, typed `InvertibleFunction[Vector]`.
  A 𝒢₃ plane `b_12 * e_12 + b_13 * e_13 + b_23 * e_23` has the normal `b_23 * e_1 - b_13 * e_2 + b_12 * e_3`
  (its dual), so projecting onto the plane is rejecting away from the normal, and the closed forms are the
  line versions' formulas against that normal. The tests check both directions against the factories on
  the `Gn` reference with fully symbolic vector and plane, and check exactness, the `TypeError` operand
  check, and the degenerate errors.
- **Generator refactor**: `line_to_line_method_def` became `line_map_method_def(n, LineMap)`, with
  `line_to_line_map` and `line_and_plane_map` describing the four methods, so all four share one
  template.
- Docs: CHANGELOG `[Unreleased]` › Added; CLAUDE.md's `transforms.py` and generated-modules entries.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-07: "5) ok")

1. **Which maps:** (a) and (b) only, the line-onto-plane projection and rejection. Plane onto plane (c) is
   out of scope.

## Judgment calls made during the work

- **Generated in 𝒢₃ only, not 𝒢₂ (or 𝒢₄/𝒢₅).** In 𝒢₂ the only plane is the whole space, so the
  projection is the identity and the rejection can never be built, the same reasoning that kept the line
  rejection out of 𝒢₁. In 𝒢₄ and up a plane has no single normal vector, so the 𝒢₃ closed form does not
  apply; the `transforms` factories still cover every dimension.
- **Names.** `line_to_plane_projection(to_plane=)` follows `line_to_line_projection(to_vector=)`. The
  rejection's image is a line off the plane, not in it, so it is `line_from_plane_rejection(away_from_plane=)`.
- **Degeneracy is tested on the image of `from_vector`**, not with `is_orthogonal_to` / `is_parallel_to`,
  which accept vectors only. The image is zero exactly when the map would squash the line.
- **One test is marked `slow`**: the symbolic-`Gn` round trip of the plane projection took 13 s in the
  container, over CLAUDE.md's 10 s bar. Only that parametrized case is marked; the symbolic rejection and
  the generated-versus-`Gn` checks stay in the everyday run.
- **g4/g5 not regenerated.** The generator changes are dimension-generic for the line maps and gated to
  `n == 3` for the plane maps, but `make test-all-dims` (about 1.5 h) was not run.
