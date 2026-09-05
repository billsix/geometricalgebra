# Define `signed_content` on `Gn` (and simplify its guards) via the dual-is-scalar test

**Status:** DONE 2026-08-26 (William Emerison Six <billsix@gmail.com>) — see Outcome.
**Priority:** 4
**Difficulty:** 3

## Outcome (2026-08-26)

Implemented in `signed_content` (`src/gacalc/measure.py`); **409 tests green** (4 new), ruff + ty
clean (src and tests). `signed_content` now works on `Gn` (`n = max basis index`) as well as the
fixed types (`n = DIMENSION`), requires **exactly `k = n`** (else raises — too few or over-determined),
and returns the pseudoscalar **dual**'s scalar part (`0` for a right-count degenerate/parallel set).

- **No `Gn` import needed** — `wedge.dual(n)` self-dispatches (Gn wedge → `Gn.unit_pseudoscalar`;
  graded wedge → its own, locked to `DIMENSION`), so the old lazy `from gacalc.gn import Gn` is gone.
- Added the private `_max_basis_index(vectors)` helper (`default=0` for all-zero).
- New tests: `Gn` full-space (numeric, matches g2/g3), the symbolic 2×2 determinant, parallel/coplanar
  `k=n` → `0`, and the raise cases (too-few, over-determined, all-zero). Replaced the obsolete
  `test_signed_content_needs_full_space_and_fixed_dimension` (which asserted the old "Gn raises").
- **Discovered a pre-existing fragility (NOT fixed here, flagged):** `max_grade()` does `max([])`
  and **raises on a zero multivector**, so `is_vector()` / `is_homogeneous_of_grade_r()` crash on
  `Gn.zero()` — which is why an all-zero input raises inside `_require_vectors` (a `ValueError`, so
  it still matches decision 2's "raise", and the test is robust to a future fix). A clean
  `max_grade()`/`is_vector()`-on-zero would be a small separate `base.py` task; kept out of scope to
  avoid a signed-content task turning into a grade-methods refactor.

## Goal

`signed_content` (`src/gacalc/measure.py:145`) currently rejects the general `Gn` representation and
leans on two explicit guards:

```python
representation = type(vectors[0])
dimension: int | None = getattr(representation, "DIMENSION", None)
if dimension is None:
    raise ValueError("signed content needs a fixed-dimension type (e.g. g2/g3); ...")
if len(vectors) != dimension:
    raise ValueError(
        "signed content is only defined when the vectors span the full space ..."
    )
...
wedge = MultiVectorBase.outer_product_of_vectors(*vectors)
return wedge.coefficient(Gn.unit_pseudoscalar(dimension))
```

Bill's idea (2026-08-26): **implement it for `Gn` too**, inferring the ambient dimension from the
vectors themselves, and drop the guards that the math makes redundant — wedge the vectors, take the
**dual**, and if the result is a **scalar**, that scalar *is* the signed content; if not, the set
doesn't span the full space.

## Investigation (verified 2026-08-26 — the approach is sound)

For k vectors, `wedge = v₁ ∧ … ∧ v_k` is a grade-k blade. In an n-dim space `dual(A, n) = A·I_n⁻¹`
is grade `n − grade(A)`, so **`dual(wedge, n)` is a scalar iff the wedge is top-grade (k = n and the
vectors span)** — and when it is, that scalar equals `c` in `wedge = c·I_n`, i.e. the signed
content. Dependent sets give `wedge = 0` → `dual = 0` (a scalar) → signed content `0`.

Probed against the current g2/g3 results (all **identical**), inferring `n = max basis index` and
applying the **`k = n`** rule (decision 1). "Result" is the final behaviour *after* the count guard:

| vectors (as `Gn`) | k | n | result |
| --- | --- | --- | --- |
| `e_1, e_2` | 2 | 2 | **1** (= g2) |
| `e_2, e_1` | 2 | 2 | **-1** (= g2) |
| `2e_1+e_2, e_1+3e_2` | 2 | 2 | **5** (= g2) |
| `e_1, e_2, e_3` | 3 | 3 | **1** (= g3) |
| symbolic `a₁e_1+a₂e_2`, `b₁e_1+b₂e_2` | 2 | 2 | **`a_1*b_2 - a_2*b_1`** (2×2 determinant) |
| `e_1+e_2, 2e_1+2e_2` (parallel, k=n) | 2 | 2 | **0** — dual `0`, the canonical "parallel → 0" |
| `e_1, e_3, e_1+e_3` (coplanar, k=n) | 3 | 3 | **0** — dual `0` |
| `e_1, e_3` (too few for its 3-space) | 2 | 3 | **raise** (k ≠ n; dual would be `-e_2`, non-scalar) |
| `e_1+e_3, e_2+e_3` | 2 | 3 | **raise** (k ≠ n) |
| `e_1, 2e_1` (over-determined) | 2 | 1 | **raise** (k ≠ n — 2 vectors reaching only index 1) |

(The last three never reach the dual — the `k != n` guard raises first. Verified 2026-08-26.)

**Critical constraint found:** the *generated* graded types' `dual` is **hard-locked to their
`DIMENSION`** — `g3.Bivector.dual(2)` raises `"Bivector.dual is fixed at dimension 3"`. So the
max-index inference is **`Gn`-only**; a fixed-`DIMENSION` type MUST use its `DIMENSION` for `n`
(which is also the correct semantics — the type *declares* the ambient space, so two `g3` vectors
are genuinely *not* full-space and must be rejected, exactly as today).

## Proposed implementation (unified, one path — updated per Bill's clarifications)

```python
def signed_content(vectors: Sequence[MultiVectorBase]) -> Coef:
    _require_vectors(vectors)
    representation = type(vectors[0])
    dimension: int | None = getattr(representation, "DIMENSION", None)
    # Fixed types (g2/g3) declare the ambient dimension (and their dual is locked to it);
    # the dimension-agnostic Gn takes the smallest space containing the vectors.
    n: int = dimension if dimension is not None else _max_basis_index(vectors)
    # Signed content is the oriented n-volume: defined only for EXACTLY n vectors.
    # k != n raises (too few can't span; too many is over-determined) -- Bill 2026-08-26.
    if len(vectors) != n:
        raise ValueError(
            f"signed content is the oriented n-volume: it needs exactly n vectors for the "
            f"n-dimensional space (k = n); got {len(vectors)} vector(s) for n = {n}. Use "
            f"content() (unsigned) for k != n."
        )
    wedge: MultiVectorBase = MultiVectorBase.outer_product_of_vectors(*vectors)
    oriented: MultiVectorBase = wedge.dual(n)
    # For k = n the dual is PROVABLY grade-0: independent -> nonzero scalar c (wedge = c*I_n);
    # dependent (parallel/coplanar) -> wedge 0 -> 0.  So a degenerate full-rank set is 0.
    # The is_scalar guard is defensive -- it documents the invariant, and won't fire for k = n.
    if not oriented.is_scalar():
        raise ValueError(
            "signed content is a scalar only when the vectors span the full space; got a "
            f"grade-{oriented.max_grade()} orientation."
        )
    return oriented.scalar_part()
```

with a small helper `_max_basis_index(vectors)` = `max((i for v in vectors for blade in
v.to_blade_dict() for i in blade), default=0)` — **`default=0`** so an all-zero set yields `n = 0`;
then `len(vectors) != 0` raises for any actual vectors, and an *empty* list is already rejected by
`_require_vectors`, so the all-zero-and-nonempty case raises as `k != 0` (that's fine — an all-zero
set has no oriented volume). (See decision 2's note.)

**Why the count guard is needed (not just `is_scalar`):** `is_scalar` alone can't separate a
*parallel full-count* set (`k = n`, dependent → wedge `0` → scalar `0`, want **0**) from a
*wrong-count* set that is also dependent (`k ≠ n`, dependent → wedge `0` → scalar `0`, want
**raise**). The explicit `len(vectors) != n` check draws exactly Bill's line: **wrong count (too few
OR too many) → raise**, **right count but degenerate (parallel/coplanar) → 0**. It **removes** the
old `DIMENSION is None` guard (Gn works now) and keeps the `k = n` requirement (now via `!= n`, so
`Gn` is covered by the inferred `n`). g2/g3 behaviour is unchanged (`n = DIMENSION`, `k = n`
required).

## Semantics to document (in the docstring)

- **`Gn`'s ambient dimension `n` = the largest basis index present.** Signed content is the oriented
  **n-volume**, defined only for **exactly `n` vectors**. So `Gn` `[e_1, e_3]` is `k=2` reaching
  index 3 → `n=3`, `k ≠ n` → **raise** (2 vectors can't be a full 3-volume). And `Gn` `[e_1, 2e_1]`
  is `k=2` reaching only index 1 → `n=1`, `k ≠ n` → **raise** (over-determined).
- **Right count, degenerate → `0`.** `k = n` but the vectors are linearly dependent (parallel /
  coplanar) → wedge `0` → dual `0` → **`0`** (a flat parallelotope). This — not `[e_1, 2e_1]` — is
  the "parallel → `0`" case: e.g. `[e_1+e_2, 2e_1+2e_2]` (`k=n=2`, parallel).

## Decisions (Bill, 2026-08-26)

1. **Exactly `k = n`, else raise (updated 2026-08-26).** *Right count but degenerate* (parallel /
   coplanar, `k = n`, dependent) → **`0`**; *wrong count* — **too few (`k < n`) OR too many
   (`k > n`, over-determined)** → **raise**. Drawn by the `len(vectors) != n` guard. **Bill's
   refinement:** over-determined must also raise (not return `0`), so the guard is `!= n`, not
   `< n`. **Consequence to be aware of:** `Gn` `[e_1, 2e_1]` (the earlier "parallel" example) is
   `k=2, n=1` → now **raises** (over-determined); the genuine "parallel → `0`" case is the `k = n`
   dependent one (`[e_1+e_2, 2e_1+2e_2]`).
2. **All-zero input → now raises (updated 2026-08-26).** With `_max_basis_index(..., default=0)`, an
   all-zero (but non-empty) set has `n = 0` and `k > 0`, so `k ≠ n` → **raise** (a clean
   "needs exactly n vectors, got k for n=0" error, not a `max()` crash). This *changes* the earlier
   "all-zero → `0`" answer, because the stricter `k ≠ n` rule from decision 1 now catches it. (An
   *empty* list is already rejected upstream by `_require_vectors`.) **Flag for Bill:** if you'd
   rather all-zero return `0` than raise, say so — it'd be a small special-case.
3. **No explicit `n` parameter** for now (Bill: "whatever you recommend"). The inferred
   minimal-space rule (`n = max basis index`) is the default; add an override only if a real caller
   needs it.
4. **Switch fully to `dual`** (Bill: "sure if you recommend"). It both validates and computes, so it
   replaces the `wedge.coefficient(unit_pseudoscalar(dimension))` line — one self-validating path,
   verified to give identical values; one extra geometric product vs a dict lookup, negligible.
5. **Pass condition is `is_scalar()`, NOT `max_grade() == 0`.** They agree for a *nonzero* scalar,
   but the parallel/degenerate case yields a *zero* dual (empty blade dict), and `max_grade()` does
   `max(self.grades())` with `grades() == []` → **raises `ValueError`** on zero, exactly the case
   that must return `0`. `is_scalar()` (`self == self.r_vector_part(0)`) returns `True` for zero.
   (Confirmed empirically 2026-08-26.) The `max_grade()` used only in the *raise* branch's message
   is safe there — that branch runs only when the result is non-scalar, hence non-empty.

## Verify

- `make test` green — existing `tests/test_measure.py` signed-area/volume cases (fixed types) must be
  **unchanged**; add `Gn` cases mirroring them (numeric + the symbolic 2×2 determinant `a_1*b_2 -
  a_2*b_1`), the parallel-at-`k=n` → `0` case (`[e_1+e_2, 2e_1+2e_2]`), and the **raise** cases:
  too-few (`[e_1, e_3]`, `[e_1+e_3, e_2+e_3]`), over-determined (`[e_1, 2e_1]`), and all-zero.
- `make format` clean (`ruff` + `ty check src`).
- Confirm `signed_area` / `signed_volume` (the fixed-arity g2/g3 wrappers) are untouched in behaviour.

## Cross-links

- `src/gacalc/measure.py:145` — `signed_content` (and its `signed_area`/`signed_volume` aliases).
- `src/gacalc/base.py:712` — `dual(self, n)`; `:596` `is_scalar`; `:657` `scalar_part`; `:192`
  `unit_pseudoscalar`.
- The generated graded `dual` being fixed to `DIMENSION`: `tools/gen_specialized.py` (emits the
  per-type `dual`); relevant if a future task wants graded types to accept a smaller `n`.
- Adjacent recent work: `tasks/archive/2026/08/25/pseudoscalar-coefficient-via-unit-pseudoscalar.md`
  (the current `coefficient`-based line this would replace).
