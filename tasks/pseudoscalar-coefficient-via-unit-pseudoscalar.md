# Read the pseudoscalar coefficient via `unit_pseudoscalar`, not a hand-built blade

**Status:** proposed — needs go-ahead. Created 2026-08-25 (William Emerison Six <billsix@gmail.com>)
**Priority:** 4
**Difficulty:** 1

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
