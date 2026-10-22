# g4/g5 generation fails: the Versor sandwich arm inverts a generic even element

**Status:** proposed — needs go-ahead (a real, reproduced blocker; likely release-blocking).
**Priority:** 3 **Difficulty:** 5
**Created:** 2026-10-22 (William Emerison Six <billsix@gmail.com>). Surfaced while verifying the
𝒢₄/𝒢₅ half of `tasks/generalize-sandwich-other-grades.md`.

## BLUF

Generating the higher-dimension algebras fails: `GACALC_DIMS=1,2,3,4 python tools/gen_specialized.py`
(and `1,2,3,4,5`, i.e. `make generate-all` / `make dist` / `make test-all-dims`) raises

```
RuntimeError: inverse() supports a blade or versor (where Ã * A is a scalar); the general
mixed-grade multivector inverse is not implemented (see tasks/lean-general-multivector-inverse.md)
```

`g1`/`g2`/`g3` generate fine; `g4` already fails. Because a released wheel bakes `g4`/`g5`
(`make dist` sets `GACALC_DIMS=1,2,3,4,5`), **this blocks the next release** (e.g. 0.2.0, whose
version is already bumped) — confirm before releasing. "Done" = `make generate-all` and
`make test-all-dims` are green again, by maintainer-chosen approach below.

## Root cause (traceback, confirmed 2026-10-22)

`generate_graded_type` → `versor_extras` (`tools/gen_specialized.py:~5371`) → `dispatch_method`
(`:3700`) → `product_result` (`:3010`) → the sandwich result-lambda → `base.py:1264` `inverse()`.

The generated **`Versor.sandwich`** closed form is `R * x * R.inverse()`, computed symbolically over a
**generic** even element `R` (grades {0,2,…}). In 𝒢₂/𝒢₃ a generic even element IS versor-invertible
(`Ã * A` is a scalar: for 𝒢₃, `(s − B)(s + B) = s² − B²` with `B²` scalar), so `inverse()` succeeds.
In **𝒢₄+** a generic even element has a grade-4 part, and `Ã * A` is **not** a scalar (it keeps grade-2
/ grade-4 terms for generic coefficients), so `inverse()` correctly raises. This is genuine math, not a
sympy/host artifact — the container gate fails the same way. (Whether this is a regression since 0.0.20
or has been latent since the Versor sandwich family landed 2026-06-08 is unconfirmed; either way it is
broken now.)

## Options (maintainer's call)

1. **Restrict the generated `Versor.sandwich` closed form to dims ≤ 3**, and for 𝒢₄/𝒢₅ fall back to the
   inherited `MultiVectorBase.sandwich` (runtime `type(x)` projection, which needs no closed-form
   inverse). Smallest change; higher-dim sandwich stays correct, just not a specialized closed form.
2. **Generate the sandwich via the reverse form** `R * x * R̃` (no `inverse()`), valid for a **unit**
   versor; for a general versor divide by `normSq R` symbolically (a scalar for an *actual* versor).
   The obstacle is that the generator works on a generic even element, which is not a versor in 4D —
   so this needs the closed form derived on the versor manifold, not generic coefficients.
3. **Implement the general multivector inverse** (`tasks/lean-general-multivector-inverse.md`) so
   `inverse()` handles the 𝒢₄/𝒢₅ even case — the largest change.

Recommendation: option 1 (restrict + fall back) to unblock releases quickly, with option 2 as the
principled follow-up if a specialized higher-dim sandwich is wanted.

## Reproduce / verify

- Fails: `GACALC_DIMS=1,2,3,4 python tools/gen_specialized.py` (host or container).
- Fixed when `make generate-all` writes `g4.py`/`g5.py` and `make test-all-dims` is green.

## See also

- `tasks/generalize-sandwich-other-grades.md` — its 𝒢₄/𝒢₅ verification half is blocked on this.
- `tasks/lean-general-multivector-inverse.md` — the unimplemented general inverse (option 3).
- `tasks/reference/generated-algebra-generation-cost.md` — why g4/g5 are release-only.
