# Make generated ops subclass-preserving (construct via type(self))

**Status:** DONE 2026-07-08 (authorized by Bill: "go ahead and do the
subclass-preserving generated ops task in gacalc"). Changes staged,
uncommitted — Bill commits.
**Created:** 2026-07-09

## Problem (found during mvp ctc-vector2-deferral experiment)

Subclassing a generated graded type lost the subclass on every operation::

    class ShimV2(gacalc.g2.Vector2): ...
    type(ShimV2(...) + ShimV2(...))   # -> Vector2, NOT ShimV2

The generated closed-form ops (`__add__`, `__sub__`, `__neg__`, scalar
`__mul__`, ...) constructed the concrete result class by name, so any
subclass's added API vanished from arithmetic results — while the base
`MultiVectorBase` methods already build results via
`type(self).from_blade_dict()` on purpose.

This blocked modelviewprojection's plan to back the Code-the-Classics
pygame-`Vector2` work-alike with `gacalc.g2.Vector2`.

## What was done (tools/ only — generated g*.py are gitignored artifacts)

- `tools/astbuild.py`: new `construct_type_self(pairs)` node builder
  (`type(self)(field=value, ...)` — no cast needed, `type(self)` is
  `type[Self]`); `return_construct(name_, pairs, owner=None)` grew an
  `owner` param and emits `type(self)(...)` when `owner == name_`.
- `tools/gen_specialized.py`:
  - `result_stmts` — every caller passes the owning class (linear ops,
    reverse, even/odd/r_vector parts), so it now emits
    `return type(self)(...)` unconditionally (the `result:` local is gone).
  - `scaled_stmt` (scalar `__mul__`/`__rmul__`/`__neg__`) — same.
  - `result_block_stmts` / `unary_stmt` — new `owner` param;
    `type(self)` only when the resolved result type equals the owning
    class AND the cast is `cast_self` (the rotor sandwich keeps its
    `cast_operand` path). Widening/grade-changing results keep the
    concrete class (`Vector2 * Vector2 -> Rotor2`,
    `Vector2 + Bivector2 -> G2`) — a subclass has no say over a
    different grade's class.
  - `generate_scalar`'s `scalar_const` helper — `Scalar`'s same-type ops
    (`*`, `+`, `-`, `reverse`, grade parts) now also `type(self)(...)`.
- New `tests/test_subclass_preservation.py` (7 tests): subclasses of
  `Vector2`/`G2`/`Vector3`/`Scalar` keep their type through same-type
  ops (incl. mixed sub+base → left operand's type, matching Python
  convention); grade-changing results stay the registered types; values
  identical to the base-class path.

## Gates (all green, 2026-07-08, in container)

- `make test` — 253 passed (incl. conformance suite + the new tests).
- `make check-generated` — deterministic.
- `make format` — ruff + ty all-checks-passed (3×). NB: the image's ruff
  also rewrapped three long comment lines in `notebooks/displaymv.py` —
  unrelated formatter drift, left unstaged for Bill to take or drop.
- Downstream: mvp's shim-Vector2 experiment rerun against this tree —
  all 10 checks pass (`type(sub+sub) is ShimV2`, scalar mul both sides,
  neg, property access on results, mutation, iteration order,
  magnitude, `normalize()` preserves type).

Unblocks mvp `tasks/ctc-vector2-deferral.md` Phase B (its remaining
gacalc blocker is the relicense task, [[relicense-to-lgpl]] here).
