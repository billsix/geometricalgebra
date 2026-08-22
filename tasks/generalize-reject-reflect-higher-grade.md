# Generalize reject / reflect to higher-grade blades (grade 3+)

**Status:** not started · proposed 2026-06-05 · needs go-ahead (user wants to re-read Hestenes first)
**Priority:** 5
**Difficulty:** 4

## Goal

`MultiVectorBase.reject` and `.reflect` (in `base.py`) currently only implement the case where the
blade argument is a **vector or a bivector**. Any higher-grade blade falls through their `match` to
`case _: raise Exception("TODO - implement project for ...")`. This surfaced while fixing the
sequence-arity bug (see `tasks/archive/2026/06/05/correctness-bugs.md`): a 3-element span
(`reject(away_from=[e_1, e_2, e_3])`) reduces via `outer_product_of_vectors` to the trivector
`e_123`, which then hits the unimplemented branch. Goal: support rejection/reflection across a blade
of **any grade** (at least up to the pseudoscalar of `Gn`/`G3`).

## Reference (Hestenes & Sobczyk, *Clifford Algebra to Geometric Calculus*)

- **Page 18, equations 2.9a / 2.9b / 2.9c** — projection of a vector onto a blade (already cited in
  `base.py` for `project`; rejection is the complementary part, also cited "page 18").
- **Key observation:** the formulas are already grade-general:
  - projection  `P_B(a) = (a · B) B⁻¹`
  - rejection   `P_B^⊥(a) = (a ∧ B) B⁻¹`
  These don't depend on `grade(B)`. `project` already works for any homogeneous blade (its
  `is_r_vector()` branch handles grade r), so it likely needs no change. The restriction lives only
  in `reject`/`reflect`'s `match` arms.
- **Restated 2026-08-22 (William Emerison Six <billsix@gmail.com>):** *"project and reject in G3 and
  above should be able to project onto a bivector, or any r-vector type — look at base."* Two axes,
  both to be covered here: (a) the blade argument (`onto`/`away_from`) may be any r-vector, not just
  vector/bivector — this is the `match`-arm restriction above; and (b) the **value** being
  projected/rejected may itself be any r-vector, not only a grade-1 vector. Today `reject`'s inner
  `r()` and `reflect`'s inner `r()` both `assert value.is_vector()` and narrow via
  `r_vector_part(1)` — that grade-1 hardcoding is the (b) restriction (`base.py` ~lines 814-826,
  864-868). `project`'s `fn` already handles a general r-vector value (it computes
  `r = max(grades)` and narrows to that grade), so (b) is mostly a `reject`/`reflect` gap.
- **To confirm while reading p. 18:** that the `(a∧B)B⁻¹` rejection is valid for an r-blade B of any
  grade, and whether the value being projected/rejected must itself be a vector (current code
  `assert value.is_vector()`) or can be generalized.

## Current behaviour, exercised in G3 (2026-08-22, after `make generate`)

Concrete evidence of exactly what works and what fails today (`value` = the thing being
transformed; `blade` = the `onto`/`away_from`/`across` argument):

| call | result |
|------|--------|
| `project(onto=vector/bivector/trivector)(vector)` | ✓ correct |
| `project(onto=vector)(bivector)`, `project(onto=bivector)(bivector)` | ✓ correct (cross-checked vs `Gn`: `project(e_12)(e_12+e_23) → e_12`) |
| `reject(away=vector)(vector)`, `reject(away=bivector)(vector)` | ✓ correct |
| **`reject(away=trivector)(vector)`** | ✗ `Exception: TODO - implement project for …` — no trivector `match` arm |
| **`reject(away=vector)(bivector)`** | ✗ `AssertionError` — inner `r()` asserts `value.is_vector()` |
| `reflect(...)` | mirrors `reject` (built as `project − reject`): trivector `across` raises, bivector `value` asserts |

**Conclusion — `project` is already done; the gaps are entirely in `reject`/`reflect`:**

- **Axis (a), blade grade** — `reject`/`reflect`'s `match` (`base.py` ~835-845, ~881-889) has arms
  only for `is_vector()` / `is_bivector()`; a trivector (or any grade ≥3) `away_from`/`across` falls
  to `case _: raise`. `project` has no such restriction (its `fn` uses `onto.inverse()` for any
  blade).
- **Axis (b), value grade** — `reject`'s inner `r()` (`base.py` ~814-826) and `reflect`'s inner
  `r()` (~864-868) both `assert value.is_vector()` and narrow via `r_vector_part(1)`, so a bivector
  (or higher) **value** raises. `project`'s `fn` already handles a general r-vector value (computes
  `r = max(grades)` and narrows to that grade — verified correct vs `Gn`).

So the work is: generalize `reject`'s `match` to any homogeneous blade **and** replace its inner
`is_vector()`/`r_vector_part(1)` hardcoding with the value's own grade (mirroring what `project.fn`
already does); `reflect` then follows for free. No `project` code change — only new `project` tests
to lock in the higher-grade cases.

## Plan (to validate against the book)

- [ ] Re-read p. 18 (eq 2.9) and confirm the projection/rejection split holds for an arbitrary blade B.
- [ ] In `reject`: replace the `is_vector()` / `is_bivector()` arms with a single arm accepting any
      homogeneous blade (e.g. `away_from.is_r_vector()`), keeping the `(value.wedge(B)) * B.inverse()`
      body. Drop the `case _:` TODO (or keep it only for non-blade inputs).
- [ ] `reflect` is built as `project - reject`, so it should generalize for free once `reject` does —
      verify, don't assume.
- [ ] Decide whether `assert value.is_vector()` inside the inner functions can be relaxed (does the
      book define projection of a *blade* onto a blade, not just a vector?).
- [ ] Add conformance tests: project/reject/reflect across a trivector (e.g. the `G3` pseudoscalar)
      and across a 3-element vector span; check `project(a) + reject(a) == a` (the decomposition
      identity) for the higher-grade case.
- [ ] `ruff` + `ty check src` + full suite green.

## Notes

- The 2-element (bivector) and 1-element (vector) cases already work and are covered by
  `test_project_and_reject` / `test_reflect` (1-element regression added 2026-06-05).
- `Gn` works in any dimension, but practical tests can use `G3`'s trivector pseudoscalar.

## Open questions

- Should projection/rejection be defined for a general *multivector* value, or only vector values?
  (Current asserts restrict to vectors; the book may define it more broadly.)
- Is there an upper-grade limit worth enforcing, or does it just work up to the pseudoscalar?
