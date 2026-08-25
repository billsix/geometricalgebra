# Read the pseudoscalar coefficient via `unit_pseudoscalar`, not a hand-built blade

**Status:** DONE 2026-08-25 (William Emerison Six <billsix@gmail.com>) — see Outcome.
**Priority:** 4
**Difficulty:** 1

## Outcome (2026-08-25)

Implemented in `signed_content` (`src/gacalc/measure.py`), 405 tests green, ty clean. **The naive
swap I first proposed (`representation.unit_pseudoscalar(dimension)`) was WRONG** and is the
finding worth keeping: `unit_pseudoscalar` builds `e₁…e_n` by multiplying **grade-1 basis vectors
through grade-0/1 intermediates** (`math.prod([basis_vector(x) …], start=cls.one())`), so it only
works on a **full representation** — a graded type (the wedge of two 2D vectors is a `Bivector`)
can't hold those intermediates and returns an empty value, `ValueError: not enough values to
unpack` out of `coefficient`. Fix: build the pseudoscalar on **`Gn`** (which holds every grade) and
let `coefficient` do a pure blade-key lookup on the (possibly graded) wedge:

```python
from gacalc.gn import Gn  # lazy import (mirrors base.py's lazy `from gacalc import measure`)
wedge: MultiVectorBase = MultiVectorBase.outer_product_of_vectors(*vectors)
return wedge.coefficient(Gn.unit_pseudoscalar(dimension))
```

Type-clean because `wedge` is statically `MultiVectorBase`, so the `coefficient(blade: Self)` param
accepts any `MultiVectorBase` (incl. `Gn`); behaviour-identical (`coefficient` reads only the blade
key, returns `0` on a dependent set). The manual `tuple(range(1, dimension + 1))` and its
duplicated pseudoscalar-blade knowledge are gone; the construction now lives only in
`unit_pseudoscalar`. Lesson recorded inline as a code comment at the call site.

## Goal

`signed_content` (`src/gacalc/measure.py:187-189`) reconstructs the pseudoscalar blade by hand to
read off its coefficient:

```python
wedge: MultiVectorBase = MultiVectorBase.outer_product_of_vectors(*vectors)
pseudoscalar_blade: tuple[int, ...] = tuple(range(1, dimension + 1))
return wedge.to_blade_dict().get(pseudoscalar_blade, 0)
```

`tuple(range(1, dimension + 1))` **duplicates knowledge** that the top-grade blade is `(1, 2, …, n)`
— a fact already owned by `MultiVectorBase.unit_pseudoscalar(n)` (`base.py:192`, `i = e₁e₂…e_n`).
Get the coefficient *through the pseudoscalar function* so that construction lives in one place.

## The change (confirmed feasible — this is a "yes")

Use the existing `coefficient(blade)` reader with the unit pseudoscalar as the blade:

```python
representation = type(vectors[0])  # already bound at line 171
wedge: MultiVectorBase = representation.outer_product_of_vectors(*vectors)
return wedge.coefficient(representation.unit_pseudoscalar(dimension))
```

**Why it's behaviour-identical** (verified 2026-08-25 by reading the source):
- `coefficient(blade)` (`base.py:361`) is exactly `(key,) = blade.to_blade_dict(); return
  self.to_blade_dict().get(key, 0)` — the *same* `.get(pseudoscalar_blade, 0)` this code does by
  hand, so the `0`-on-a-dependent-set (blade absent) semantics is preserved with no extra guard.
- `unit_pseudoscalar(n)` returns the **unit** blade `+e₁…e_n`; `coefficient` uses only its blade
  *key*, so the unit coefficient is irrelevant — it names the blade, nothing more.
- `dimension` is non-`None` here (guarded above, lines 172-177), and `representation` is the
  concrete fixed-`DIMENSION` type (`g2`/`g3`), so the `unit_pseudoscalar` classmethod resolves.
- One incidental tidy: call `outer_product_of_vectors` on `representation` (the concrete type) to
  match, rather than the abstract `MultiVectorBase`; the result type is the concrete type either
  way, so this is cosmetic.

The comment at `measure.py:184-186` (why `c` is that blade's coefficient) stays — it explains the
*math*, which the refactor doesn't change.

## Scope

- **Single site.** `grep` confirms `measure.py:188` is the only hand-built pseudoscalar blade in
  `src/`; the two `range(1, n + 1)` uses in `base.py` (197, 213) are *inside* `unit_pseudoscalar` /
  `from_blade_dict` — the canonical home, correctly left alone.

## Verify

- `make test` green — `tests/test_measure.py` already checks `signed_content`/`signed_area`/
  `signed_volume` on both independent and dependent sets, exactly (symbolic) and numerically, in 2D
  and 3D; a behaviour-preserving change keeps them green.
- `make format` clean (`ruff` + `ty check src`).

## Cross-links

- `src/gacalc/measure.py:145` — `signed_content` (the function; `signed_area`/`signed_volume` are
  its fixed-arity aliases).
- `src/gacalc/base.py:192` — `unit_pseudoscalar`; `base.py:361` — `coefficient`.
- CLAUDE.md › Architecture (coefficient read-back: `value.coefficient(blade)` "a thin reader over
  `to_blade_dict()`, correct for any grade") and "no duplicating knowledge" spirit.
