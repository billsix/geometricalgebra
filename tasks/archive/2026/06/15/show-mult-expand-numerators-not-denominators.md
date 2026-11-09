# show_mult: expand numerators but not denominators

**Completed:** 2026-06-15

## Why

`nbplotutils.show_mult` ran `.expanded()` (the `MultiVectorBase` coefficient-view helper mapping
`sympy.expand` over every coefficient) before rendering the term-by-term table and the final sum. That
reads well for polynomial coefficients, but for rational ones — e.g. the rotor cross-product
derivation, with `1/‖a‖` and radical `1/c` denominators — expanding the denominator distributed and
denested it into something less readable. The maintainer wanted the numerator expanded and the
denominator left factored.

## What was done

A display-level helper `nbplotutils._expand_numerators_dict(mv)` expands each coefficient's numerator —
`n, d = fraction(together(c)); expand(n) / d` — keeping the denominator factored, and `show_mult` uses it
for both the per-term table and the summed product (the same treatment for consistency). It transforms
the blade dict **directly, with no multivector rebuild**, so the distributed form survives on every
representation, `Gn` included.

How it got there (2026-06-15):

1. First an ABC method `MultiVectorBase.expanded_numerators()` was added (mirroring `expanded()` /
   `simplified()` via `_map_coefficients`), and `show_mult` used it.
2. That was not enough for `displaymv.py`, which uses `Gn`: the method rebuilds via `from_blade_dict`,
   and `Gn.__post_init__` eager-`sympy.simplify`s, re-factoring the distributed numerator back into
   `a0*(b0*c0 + …)` — the same gotcha the old `.expanded()` had on `Gn` (why those helpers' test runs
   over `[G1, G2, G3]`, not `Gn`). So `show_mult` moved to the dict-level helper.
3. The ABC method then had no production caller and silently re-canonicalized on `Gn`, so it was
   removed from `base.py`. Net implementation: `_expand_numerators_dict` plus the two `show_mult` call
   sites. The `Gn` gotcha was also captured in CLAUDE.md's coefficient-view-helpers note.

Caveat: `together` combines a blade's same-denominator term sum into one fraction — more readable, and
it affects only the final-sum line, since per-term cells are single products.

## Verification

`show_mult(g2_1, g2_2*g2_3)` on `Gn` showed 0 un-distributed product cells. The conformance test was
re-pointed from the removed method to `test_expand_numerators_dict_for_display` in
`tests/test_conformance.py` (run by `make test`), which also locks in the `Gn`-survival regression.
