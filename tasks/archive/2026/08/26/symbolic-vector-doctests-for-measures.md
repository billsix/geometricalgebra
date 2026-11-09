# Add symbolic-vector doctests (show the full 2D/3D formula), alongside the numeric ones

**Created:** 2026-08-25 · **Completed:** 2026-08-26

## Goal

Keep the concrete numeric doctests in `src/gacalc/measure.py` (the reader sees the answer) and add a
second doctest per function that feeds **symbolic** vectors, so the docstring also shows the general
formula — e.g. the maintainer's model on `content`: with `a_1, a_2, b_1, b_2 = sympy.symbols(...)`,
`content([a_1 * e_1 + a_2 * e_2, b_1 * e_1 + b_2 * e_2])` prints `sqrt((a_1*b_2 - a_2*b_1)**2)`, so
the area is visibly the determinant.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-08-25)

1. **`content_by_rejection`** — show the `== content` identity rather than its raw symbolic form,
   which is unreadable and which `sympy.simplify` does not clean up
   (`sqrt(a_1**2 + a_2**2)*sqrt(a_1**2*(a_1*b_2 - a_2*b_1)**2/(a_1**2 + a_2**2)**2 + …)`). At
   implementation its existing concrete `== content` doctest was judged to show the identity already,
   so no symbolic doctest was added; the symbolic identity is covered by
   `tests/test_measure.py::test_content_two_ways_both_give_the_determinant_symbolic`.
2. **Scope: `measure.py` only.** Symbolic companions for `base`/`transforms`/`g2`/`g3` were left as a
   separate follow-up if wanted.

## What changed

Symbolic doctests, built inline from graded basis constants (`from gacalc.g2 import e_1, e_2` +
`sympy.symbols`, not `gn.sym_vec2_1`, which is `Gn`) with the generator's symbol names `a_1, a_2,
b_1, b_2` (`c_*` in 3D), placed after the numeric Examples:

- `signed_area` → `a_1*b_2 - a_2*b_1` (the 2×2 determinant);
- `signed_volume` → `c_1*(a_2*b_3 - a_3*b_2) - c_2*(a_1*b_3 - a_3*b_1) + c_3*(a_1*b_2 - a_2*b_1)`
  (the 3×3 cofactor expansion);
- `area` and `content` → `sqrt((a_1*b_2 - a_2*b_1)**2)`.

Skipped deliberately: `volume` (its symbolic output is 94 columns, over the 88 limit, with no clean
wrap), `signed_content` (a 2D case duplicates `signed_area`'s), and `content_by_rejection` (decision 1).

Every expected line was captured by running it, never written by hand, since `--doctest-modules`
makes them exact tests. Known trade-off, accepted: these doctests pin sympy's printed form, so a sympy
upgrade that changes term order may require re-capturing them.

## Verification

Verified on the host and in the container gate (the symbolic output matched the container's sympy):
ruff + `ty check src` clean, host suite 411 tests, and the measure doctests green in the nested
`gacalc` image. The measures' math is in `tasks/reference/content-area-volume.md`.
