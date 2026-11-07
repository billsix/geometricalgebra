# Invertible project and reject between a vector and a plane, with coordinate versions in g1–g3

**Status:** proposed — needs go-ahead
**Priority:** 7
**Difficulty:** 6
**Created:** 2026-11-07 (William Emerison Six <billsix@gmail.com>): "And then make a follow up task for
doing that to a vector and a plane, both for project, and reject. And as part of those tasks, add them to
be coordinate versions in the generated code for g1 g2 g3 etc"
**Depends on:** `tasks/line-to-line-rejection-invertible-function.md` (both line-to-line maps and their
generated coordinate versions; this task extends the same shape to a plane).

## BLUF

Extend the checked, invertible restrictions of `project` and `reject` from "line to line" to "vector and
plane". Each is an `InvertibleFunction` that raises `ValueError` when its input is off its domain or the
inverse's input is off the image, built in `transforms.py` and generated with coordinate (closed-form)
versions into the `g*.py` modules where a plane exists (𝒢₂, 𝒢₃; 𝒢₁ has no plane). Done = the factories
with doctests and tests, the generated versions agreeing with the `Gn` reference, the generated-code
gates green, and the changelog entry.

## Context

- The line versions: `transforms.line_to_line_projection` and `coordinate_along` (built 2026-11-07),
  `transforms.line_to_line_rejection` (the previous task). Same checks, same `float_close_to_zero` flag.
- `MultiVectorBase.project` / `reject` already take a plane (a bivector, or a sequence of vectors wedged
  into one) and use H&S eq 2.9; the vector-against-bivector projection and rejection are machine-checked
  in `proofs/GacalcProofs/Projection3D.lean` (`project_add_reject`, `reject_perp_dot`).
- "On the plane `B`" is `x ∧ B = 0`; "on the line of `a`" is `is_parallel_to`. Generated code:
  `tools/gen_specialized.py`, `tasks/reference/code-generator-architecture.md`.

## The candidate maps (which ones are meant is Open question 1)

| map | domain → image | invertible when |
|---|---|---|
| (a) project a **line onto a plane** | line of `a` → line of `P_B(a)` in `B` | `a` not perpendicular to `B` (`P_B(a) ≠ 0`) |
| (b) reject a **line from a plane** | line of `a` → line of `R_B(a)` (normal to `B`) | `a` not in `B` (`a ∧ B ≠ 0`) |
| (c) project a **plane onto a plane** | plane `A` → plane `B` | the planes are not at a right angle (the projection of `A` onto `B` is not squashed to a line) |
| (d) project a **plane onto a line** / reject a plane from a line | plane → line | never: two dimensions cannot go one-to-one onto one |

(a) and (b) are the line versions with a bivector in place of `n`, and reuse `coordinate_along`. (c) is a
2D-to-2D map: its inverse needs a 2×2 solve (or the reciprocal frame of the two spanning vectors' images),
not a single coordinate. In 𝒢₃ only one plane-to-plane rejection is non-degenerate: rejecting a plane
from a plane lands on a line, so (c) has no rejection counterpart.

## Plan

1. The factories chosen in Open question 1, in `transforms.py`, with doctests and a test file each: round
   trips over int, rational, float with the flag, symbolic `Gn`; off-domain and off-image raise; the
   degenerate configurations raise at construction.
2. Generator: coordinate versions in `g2`/`g3`, in the shape the previous task settles (method on the
   generated `Vector`, or on `Bivector` for (c)). `make generate`, read the output, test against
   `transforms` and `Gn`.
3. `make check-generated`, `make check-regions`, `make format`, full `make test`; `CHANGELOG.md`
   `[Unreleased]` › Added; CLAUDE.md.

## Open questions

1. **Which maps?** Recommended: (a) and (b), the line-onto-plane projection and rejection, since they are
   the direct extension of the line versions and reuse `coordinate_along`. Add (c), plane onto plane, only
   if you want it; it needs a 2D inverse.
