# Read the pseudoscalar coefficient via `unit_pseudoscalar`, not a hand-built blade

**Created:** 2026-08-25 · **Completed:** 2026-08-25

`signed_content` (`src/gacalc/measure.py`) rebuilt the pseudoscalar blade by hand to read off its
coefficient:

```python
wedge: MultiVectorBase = MultiVectorBase.outer_product_of_vectors(*vectors)
pseudoscalar_blade: tuple[int, ...] = tuple(range(1, dimension + 1))
return wedge.to_blade_dict().get(pseudoscalar_blade, 0)
```

`tuple(range(1, dimension + 1))` duplicated knowledge owned by `MultiVectorBase.unit_pseudoscalar(n)`
(`i = e₁e₂…e_n`). The goal was to read the coefficient through the pseudoscalar function so the
construction lives in one place. `grep` confirmed it was the only hand-built pseudoscalar blade in
`src/`; the two `range(1, n + 1)` uses in `base.py` are inside `unit_pseudoscalar` / `from_blade_dict`,
the canonical home.

## The finding: the first proposal was wrong

The first proposal, `wedge.coefficient(representation.unit_pseudoscalar(dimension))` on the operands'
own type, failed. `unit_pseudoscalar` builds `e₁…e_n` by multiplying grade-1 basis vectors through
grade-0/1 intermediates (`math.prod([basis_vector(x) …], start=cls.one())`), so it works only on a
**full representation**. A graded type (the wedge of two 2D vectors is a `Bivector`) can't hold those
intermediates and returns an empty value, which surfaced as `ValueError: not enough values to unpack`
out of `coefficient`.

## What changed

The pseudoscalar is built on **`Gn`** (which holds every grade), and `coefficient` does a pure
blade-key lookup on the possibly graded wedge:

```python
from gacalc.gn import (
    Gn,
)  # lazy import (mirrors base.py's lazy `from gacalc import measure`)

wedge: MultiVectorBase = MultiVectorBase.outer_product_of_vectors(*vectors)
return wedge.coefficient(Gn.unit_pseudoscalar(dimension))
```

- **Type-clean:** `wedge` is statically `MultiVectorBase`, so `coefficient(blade: Self)` accepts any
  `MultiVectorBase`, including `Gn`.
- **Behaviour-identical:** `coefficient(blade)` is `(key,) = blade.to_blade_dict(); return
  self.to_blade_dict().get(key, 0)`, the same lookup as before, so a dependent set still gives `0`; the
  unit coefficient of the pseudoscalar only names the blade.
- The lesson (why `Gn`, not the operand type) was recorded as a code comment at the call site. The
  existing comment explaining why `c` is that blade's coefficient stayed.

## Verification

405 tests green (`tests/test_measure.py` checks `signed_content`/`signed_area`/`signed_volume` on
independent and dependent sets, symbolically and numerically, in 2D and 3D); ty clean.
