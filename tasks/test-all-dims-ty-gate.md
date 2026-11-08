# A `ty` gate for the generated modules (`make test-all-dims`)

**Status:** in progress — blocked on open question 2 (the fix turned out larger than estimated)
**Priority:** 3
**Difficulty:** 3 for the gate alone; ~6 with the fixes it needs to pass
**Created:** 2026-11-08
**Source:** `tasks/review/2026/11/08/repo-review.md` §2.1, §8.1

## BLUF

Three docs say `make test-all-dims` is "the full-dim + full-context ty gate", but it runs no `ty`:

- `CLAUDE.md` › "Dev workflow";
- `tasks/reference/design-decisions.md:172`;
- `tasks/reference/generated-product-typing.md:306`.

So nothing type-checks the generated `g1`–`g5`. On 2026-11-08, `ty` reports **121 errors** in
`g1`–`g3`, which were clean on 2026-08-22.

Done means one of two outcomes:

- a real gate exists and passes;
- or the docs stop claiming one.

## Context

**What the target runs.** `Makefile` `test-all-dims` runs the generator with
`GACALC_DIMS=1,2,3,4,5` and then `python -m pytest`, and nothing else. It also lacks the `: image`
prerequisite that every other container target has, and that `CLAUDE.md` › "Continuous integration"
requires.

**Why nothing else catches it.** `entrypoint/format.sh` runs `ty check src`. That respects
`.gitignore`, which lists the generated `g*.py`, so it never sees them.

**Measured 2026-11-08** (`ty 0.0.91`, sandbox):

- `ty check src/gacalc/g1.py src/gacalc/g2.py src/gacalc/g3.py` gives **121 diagnostics, all
  `error[invalid-method-override]`**.
- They are generated overrides that `ty` finds incompatible with `MultiVectorBase`: `__mul__`,
  `_geometric_product`, `__add__` and others, e.g. `g1.py:814` `__mul__`.
- The count is the same before and after the generator fixes of
  `tasks/archive/2026/11/08/fix-generator-scalar-iter-coercion-sandwich.md`, so those fixes didn't
  cause them.
- `tasks/archive/2026/08/23/generator-ty-clean-high-dim.md` recorded g1/g2/g3 as "fully clean" and
  fixed 179 diagnostics in g4. It also named `invalid-method-override` as a class it handled for
  `__radd__`.
- So either a newer `ty` added the check, or later generator changes reintroduced it. Finding out
  which is part of the fix.

**The manual commands in the docs disagree.** The two reference docs give different file lists;
only one includes `nbplotutils.py`.

Read first: `tasks/reference/generated-product-typing.md` › "High-dimension ty findings", and
`CLAUDE.md` › "Code generation" (generate, read the real output, then fix the generator).

## Plan

Depends on open question 1.

- **If (a) gate and fix:**
  - [ ] Classify the 121 errors by method and cause.
  - [ ] Fix them in `tools/gen_specialized.py` (or in `base.py`'s signatures, if the base is what's
    too narrow).
  - [ ] Add the full-context `ty check` step and `: image` to `test-all-dims`.
  - [ ] Give `make` a fast g1–g3 variant (`make type-check`, the template's standard read-only gate)
    and run that in CI.
  - [ ] Keep one documented command.
- **If (b) gate only, with a baseline:**
  - [ ] Add the step with the 121 known errors recorded as a baseline, so new errors fail and the
    baseline is fixed later.
- **If (c) docs only:**
  - [ ] Correct the three docs to say the full-context check is manual, and give the one command.

## Decisions

1. Open question 1 was answered **(a) add the `ty` step and fix the 121 `invalid-method-override` errors so it passes.** (William Emerison Six <billsix@gmail.com>, 2026-11-08.)

## Findings (2026-11-08)

**What the 121 errors are.**

- They come from 15 methods: `_geometric_product`, `__mul__` and `__add__` (12 each); `r_vector_part`,
  `inner_product` and `dot` (9 each); `wedge`, `outer_product`, `left_contraction`,
  `right_contraction`, `__xor__`, `__radd__`, `__lt__` and `__gt__` (7 each); `plane_of_rotation` (2).
- All of them are generated graded overrides whose **return** type differs from the base.
- `MultiVectorBase` declares every one of these as `-> typing.Self`, and has since the June typing
  work (`git log -L` on `base.py`).
- The graded types legitimately return a different type: `Vector * Vector` is a `Versor`, and
  `Scalar + Vector` is a `G`. ty 0.0.91 reports each as a Liskov violation (e.g. "element `Vector` of
  union `Scalar | Vector | Bivector | Versor | G` is not assignable to `Scalar`").
- The 2026-08-22 cleanup recorded g1–g3 as clean, so this check is newer in `ty`; the code didn't
  change.

**Experiment: widen the 15 base return types to `MultiVectorBase`** (reverted afterwards).

- The generated modules drop from 121 errors to 1.
- But the false `Self` claim moves elsewhere: about 120 new errors.
  - `src/` 14: `base.py`'s `reverse`, `inverse`, `__sub__`, `__rmul__` and `__truediv__` all
    return compositions typed `Self`; `gn.py`; and `transforms.py`, whose generic `translate(b)` is
    typed `V → V`.
  - `tests/` 41, mostly `x: Gn = a * b` assignments in `test_multivector.py`.
  - `tools/` 45, nearly all in `gen_specialized.py`.
- `transforms.py`'s generic typing is the deep one. `V → V` is genuinely false for the graded
  types: `Scalar + Vector` is a `G`.

So option (a) as approved is a typing redesign of the base and transforms layers, not a generator
fix. That is about D8, not the D6 estimated.

## Open questions

1. *(answered: (a), gate and fix; see Decisions.)*
2. **Given the findings above, which fix?**
   - (a1) Widen the 15 base return types to `MultiVectorBase` and fix the cascade: about 120 sites,
     including re-typing `transforms.py`'s generic `V → V` factories and adding `Self`-typed
     overrides on `Gn` (~D8). The type claims become true everywhere.
   - (a2) Keep `-> Self` as the base contract, which holds for the full representations `Gn`/`G`.
     Each generated graded override that returns a narrower or different type gets a narrow
     `# ty: ignore[invalid-method-override]`, with the reason at the site; the graded types return
     the resolved product type on purpose (`tasks/reference/generated-product-typing.md`). Then add
     the `ty` gate, so any *other* error fails it (~D3). Park (a1) as its own task.

   Recommendation: (a2) now, with (a1) parked. The gate starts protecting g1–g5 today, the
   suppression is explicit and explained at each site rather than a hidden baseline, and the
   redesign gets its own decision.
