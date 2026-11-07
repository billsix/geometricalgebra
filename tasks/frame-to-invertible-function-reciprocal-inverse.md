# `Frame.to_invertible_function`: a reciprocal-frame inverse, chosen by keyword, as the default

**Status:** in progress (2026-11-07)
**Priority:** 4
**Difficulty:** 3
**Created:** 2026-11-07 (William Emerison Six <billsix@gmail.com>): "implement in Frame the
to_invertible_function, make that one have two ways of doing it, specified by a keyword argument and a
default value. I want an option to use the reciprocal frame as a way to do the inverse function as well,
and I want it to be the default option. … unit tests to cover both methods, and to show that they are
equivalent, symbolically."
**Depends on:** `tasks/archive/2026/11/07/reciprocal-frame-hestenes.md` (`reciprocal_frame`,
`Frame.reciprocal_vectors()`).

## BLUF

Give `Frame.to_invertible_function` a keyword-only argument choosing how its **inverse** recovers the
coordinates:

- `"reciprocal"` (the default): `x_i = vⁱ · y`, one dot product per coordinate with the reciprocal frame;
- `"peel"`: today's back-substitution from the last frame vector.

Done when:

- both methods are implemented, and an unknown method raises `ValueError`;
- the default is `"reciprocal"`;
- the round-trip tests run under both methods;
- symbolic 2D and 3D tests show the two inverses give the same result for a general frame and a general
  vector;
- `make test` and `make format` pass.

## Context (read first)

- `src/gacalc/frame.py`: `Frame.to_invertible_function` (`forward`, and `backward` with its nested
  `peel`), `reciprocal_frame`, `Frame.reciprocal_vectors()`.
- `tasks/reference/frames-qr-and-reciprocal-frames.md`, "The peel inverse, step by step" and "The relation
  to Hestenes' reciprocal frame".
- `tasks/frame-inverse-head-first-recursion.md` (open) asks whether the peel can recurse head-first. Its
  option (B), "use the reciprocal frame, and drop the recursion", is what this task adds as the default
  method. That task's question about the peel itself remains open.

## Design

- **The keyword:** `inverse_method: Literal["reciprocal", "peel"] = "reciprocal"`, keyword-only, so a call
  reads `frame.to_invertible_function(inverse_method="peel")`. It names the half that differs: the forward
  map `f(x) = Σ (x · e_i) * v_i` is the same either way. Dispatch is a `match` with a raising default
  (total dispatch).
- **The reciprocal inverse:** the reciprocal vectors are computed once, when the map is built, not on each
  call. The inverse is then a plain map over them, with no recursion: `x = Σ_i (vⁱ · y) * e_i`.
- **Why the two agree:** `y = Σ_j x_j * v_j`, so `vⁱ · y = Σ_j x_j * (vⁱ · v_j) = x_i` by eq 3.5. The peel
  returns the same `x_i`, because the solution is unique for a frame. The tests check this symbolically.
- **Cost:** the reciprocal method inverts the pseudoscalar once per map. For a 3D symbolic frame that is
  one rational expression per component, the same order as the peel's divisions by `|w_j|²`.

## Plan

1. Add `inverse_method`, a `match` choosing `backward`, and the reciprocal `backward`; update the
   docstring, including a doctest for each method.
2. Tests (`tests/test_frame_class.py`):
   - parametrize the existing round-trip tests over both methods;
   - the two inverses are equal for a general symbolic `y`, on general 2D and 3D frames;
   - the default is `"reciprocal"`;
   - an unknown method raises `ValueError`.
3. `CHANGELOG.md` entry (additive: a new keyword with a default, so the same results); the reference doc
   gets a paragraph; update the head-first task's header (its blocker is gone, and option (B) exists).
4. `make test` and `make format` in the container.
