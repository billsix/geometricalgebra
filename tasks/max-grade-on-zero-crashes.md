# `max_grade()` (and the grade predicates) crash on the zero multivector

**Status:** proposed — needs go-ahead. Created 2026-08-26 (William Emerison Six <billsix@gmail.com>)
**Priority:** 4
**Difficulty:** 2

## The bug

`max_grade()` is `max(self.grades())`, and `grades()` returns `[]` for a **zero** multivector
(empty blade dict), so `max([])` raises `ValueError: max() iterable argument is empty`
(`src/gacalc/base.py:664-668`):

```python
def grades(self) -> list[int]:
    return list(set(len(blade) for blade in self.to_blade_dict().keys()))  # [] for zero

def max_grade(self) -> int:
    return max(self.grades())  # max([]) -> ValueError on zero
```

Everything that routes through `max_grade` therefore **crashes on a zero value**:

- `is_r_vector()` (`base.py:604`, `self == self.r_vector_part(self.max_grade())`);
- `is_homogeneous_of_grade_r()` (`base.py:594`, `self.max_grade() == r and self.is_r_vector()`);
- and thus **`is_vector()` / `is_bivector()` / `is_trivector()`** (`base.py:606-613`).

It's in the shared base, so **every representation crashes** — verified `Gn.zero()`,
`g2.Vector.zero()`, `g2.G.zero()` all raise from `.is_vector()` (2026-08-26).

## Blast radius (verified 2026-08-26 — narrower than it looks)

- **Products are SAFE.** `x ^ 0`, `0 ^ x`, `x * 0`, `x.inner_product(0)`, `0.left_contraction(x)`
  all return zero correctly — a zero operand has no blades, so the product loop short-circuits
  before the `max_grade()` calls in `inner_product`/`outer_product`/the contractions
  (`base.py:423,456,512,547`). So this is **not** a silent-wrong-answer bug in the algebra.
- **The predicates are the exposure.** Any code that asks "is this a vector?" of a possibly-zero
  value crashes with the cryptic `max() ... empty` instead of a sensible answer. Real consumers:
  - `measure._require_vectors` → **`content` / `area` / `volume` / `signed_content` crash on a
    zero-vector input** (this is how the signed-content-on-Gn task surfaced it — an all-zero
    `signed_content` raises here rather than at its own `k != n` guard).
  - `frame.py:60` (`if not v.is_vector()`), `transforms.py:208-217,469` (`assert *.is_vector()`).

## The inconsistency that points at the fix

`is_scalar()` (`base.py:596-598`) is `self == self.r_vector_part(0)` — it does **not** use
`max_grade`, and it already returns **`True`** for zero. So today `Gn.zero().is_scalar()` is `True`
but `Gn.zero().is_vector()` **crashes** — the predicates disagree about zero. Making them consistent
is the crux.

## Proposed fix + the one design decision

**Decision — what grade is the zero multivector?** The mathematical convention (and the one
consistent with `is_scalar(zero) == True`) is that **zero is homogeneous of *every* grade** (it lies
in every grade subspace). Recommend adopting that:

- `max_grade()` → stop crashing: `return max(self.grades(), default=0)` (a value, so `is_r_vector`
  and the product paths never blow up; `default=-1` is the alternative if a "no grade present"
  sentinel reads better — decide during implementation).
- `is_homogeneous_of_grade_r(r)` → **True for zero, any `r`**: e.g.
  `grades = self.grades(); return (not grades) or (max(grades) == r and self.is_r_vector())`.
  Then `is_vector(0) == is_bivector(0) == is_scalar(0) == True`, matching the convention and each
  other.

**Alternative (state it, don't silently pick):** treat zero as grade-0 only (or no grade), so
`is_vector(0) == False`. That gives `_require_vectors` a clean "not a vector" rejection of a zero
vector — but it contradicts `is_scalar(0) == True` and the math, and makes `content([0])` raise
rather than return `0`. **Recommend the every-grade option** unless Bill prefers rejecting zero
vectors outright.

Downstream effect of the recommended fix: `content([Gn.zero()])` returns `0` (magnitude of the zero
vector), and an all-zero `signed_content` then raises cleanly at its own `k != n` guard (`n = 0`,
`k != 0`) instead of at the `max_grade` crash — the archived signed-content task's all-zero test
stays green either way (still a `ValueError`).

## Verify

- Add `tests/` coverage: `max_grade` / `is_r_vector` / `is_vector` / `is_bivector` / `is_trivector`
  / `is_homogeneous_of_grade_r` on `.zero()` for `Gn`, a graded `Vector`, and the full `G` — none
  crash, all agree with the chosen convention (and with `is_scalar(zero) == True`).
- Re-confirm products with a zero operand still return zero (regression guard).
- `make test` green; `make format` clean (`ruff` + `ty check src`).
- Spot-check the consumers: `content([Gn.zero()])`, `make_orthogonal_frame` with a zero member.

## Cross-links

- `src/gacalc/base.py:664-668` (`grades`/`max_grade`), `:590-613` (`is_homogeneous_of_grade_r`,
  `is_scalar`, `is_r_vector`, `is_vector`/`is_bivector`/`is_trivector`).
- Discovered by `tasks/archive/2026/08/26/signed-content-on-gn-via-dual.md` (its Outcome flags this).
- Consumers: `src/gacalc/measure.py` (`_require_vectors`), `src/gacalc/frame.py:60`,
  `src/gacalc/transforms.py:208-217,469`.

## Decision (Bill, 2026-08-26)

1. **Zero is homogeneous of *every* grade** — Bill: "go with your recommendation, whatever makes a
   cleaner API." So implement the every-grade option in "Proposed fix" above: `is_vector(0) ==
   is_bivector(0) == is_scalar(0) == True`, `max_grade()` stops crashing (`max(self.grades(),
   default=...)`), and `is_homogeneous_of_grade_r(r)` returns `True` for zero at any `r`. This makes
   the grade predicates consistent with each other and with the existing `is_scalar(0) == True`.
