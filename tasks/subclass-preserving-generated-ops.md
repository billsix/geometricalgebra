# Make generated ops subclass-preserving (construct via type(self))

**Status:** proposed — needs go-ahead
**Created:** 2026-07-09

## Problem (found 2026-07-09, mvp ctc-vector2-deferral experiment)

Subclassing a generated graded type loses the subclass on every operation::

    class ShimV2(gacalc.g2.Vector2): ...
    type(ShimV2(...) + ShimV2(...))   # -> Vector2, NOT ShimV2

The generated closed-form ops (`__add__`, `__sub__`, `__neg__`, scalar
`__mul__`, ...) construct the concrete result class by name, so any
subclass's added API vanishes from arithmetic results. The base
`MultiVectorBase` methods already build results via
`type(self).from_blade_dict()` on purpose ("so they stay polymorphic" —
CLAUDE.md); the fast paths don't honour that contract.

This blocks modelviewprojection's plan to back the Code-the-Classics
pygame-`Vector2` work-alike with `gacalc.g2.Vector2` (Bill approved the
direction 2026-07-09 after making the games' dot products explicit).

## Fix sketch (in tools/gen_specialized.py — never hand-edit g*.py)

The generator resolves each op's RESULT TYPE at generation time (grade
support → smallest covering registered type, else widen). Emit
`type(self)(...)` **only where the resolved result type equals the
operand's own class** (e.g. `Vector2 + Vector2 -> Vector2`,
`__neg__`, scalar `__mul__`); keep the named concrete class where the
result widens or changes grade (`Vector2 + Bivector2 -> G2`,
`Vector2 * Vector2 -> Rotor2`) — a subclass of Vector2 has no say over a
Rotor2 result. Mixed-operand ops (Sub + base Vector2) should also produce
`type(self)` of the LEFT operand, matching Python conventions.

## Gates

- `make generate` + the conformance suite (`make test`) — the generated
  code must stay provably consistent with `Gn`.
- `make check-generated` (determinism).
- A new unit test: subclass each graded type, assert `type(a + b) is`
  the subclass for same-type ops and the registered type for widening ops.
- Downstream check: mvp's shim-Vector2 experiment from 2026-07-09 rerun.
