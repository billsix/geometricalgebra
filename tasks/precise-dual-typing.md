# Precise `dual()` return type — drop the last unsound `Self` cast on a generated unary op

**Status:** proposed — needs go-ahead. Created 2026-07-22. The last member of the typing-cleanup
family (`tasks/archive/2026/07/22/retype-even-odd-part-off-self.md`,
`.../overload-r-vector-part.md`, `.../overloads-and-drop-cast-on-product-primitives.md`): `dual` is
the one remaining generated op still declared `-> Self` with an unsound cast.

## Goal

Make `dual()` grade-precise on the graded types and drop the unsound `cast(typing.Self, …)`:
- `Bivector3.dual() -> Vector3`, `Vector3.dual() -> Bivector3`, `Scalar.dual() -> Trivector3`,
  `Trivector3.dual() -> Scalar` (grade r → n−r);
- 2D stays same-type where the grade is preserved (`Vector2.dual() -> Vector2`,
  `Rotor2.dual() -> Rotor2`, since n−1=1 and n−{0,2}={2,0});
- the full class `G_n` keeps `-> Self` (all grades — a valid narrowing once the base loosens).

## What's there now (verified in generated `g3.py`)

```python
def dual(self, n: int | None = None) -> typing.Self:           # Bivector3
    if n is None or n == 3:
        return typing.cast(typing.Self, Vector3(coeff_e_1=self.coeff_e_23, …))  # a Vector3, lied to Self
    return typing.cast(typing.Self, _coerce(self, G3).dual(n))                    # G3, lied to Self
```

So `Bivector3.dual()` returns a `Vector3` at runtime but types as `Bivector3`. Same unsound-`Self`
pattern the others shed — the resolved type is already computed by the generator (`unary_result`).

## The pattern + the wrinkle

The mechanism is the **same as `retype-even-odd-part-off-self`** (no argument to key an `@overload`
on the *result* — the result grade is fixed by the operand grade + dimension): retype
`base.dual` from `-> Self` to `-> MultiVectorBase`, then the generated graded override **declares its
resolved return type** and constructs it with no cast (the generator's `parity_part`-style path with
an identity cast).

**The wrinkle `dual` adds:** it has the `n` (dimension) parameter and a **two-branch body** — the
default-`n` closed form (resolved grade type, e.g. `Vector3`) *and* a non-default-`n` fallback that
`_coerce`s to `G_n` and returns that. A single precise return type can't cover both `Vector3` and
`G_n`. Options to resolve (decide at implementation):

1. **Drop/raise the non-default-`n` fallback** (my lean) — a fixed-dimension type's dual is
   intrinsically at *its own* dimension; `Bivector3.dual(5)` is meaningless. Ignore `n` (always the
   DIMENSION dual, like `dimension_known_methods` treats `unit_pseudoscalar`) or raise on a
   mismatched `n`. Then the graded `dual` has one branch and one precise return type. Cleanest.
2. **Overload on `n`** — `dual(self, n: Literal[<DIMENSION>] | None = None) -> <resolved>` +
   `dual(self, n: int) -> MultiVectorBase`. Keeps the fallback, precise for the common call. More
   machinery (mirrors `r_vector_part`'s literal overloads, but on the dimension).

## The `Gn` decision (same as even/odd)

Retyping `base.dual -> MultiVectorBase` loosens **`Gn.dual`** (the only class inheriting the base) to
`-> MultiVectorBase`. Recommend **let `Gn` inherit it** (no override) — consistent with the
even/odd resolution; check no call site needs `Gn.dual()` statically precise (the even/odd task's
sweep found none for that family). The full class `G_n` and all graded types keep/gain precise
returns via their own overrides.

## Rotor3 → the odd type

`Rotor3` is grades {0,2}; its dual is grades {3,1} = the **odd** part {1,3}, which has **no covering
graded type**, so `unary_result`/`resolve` widens it to `G3` — honest, not a bug. If
`tasks/model-odd-graded-type.md` ever lands an odd {1,3} type, `Rotor3.dual()` would narrow to it.
Cross-link that task.

## Cross-repo payoff (mvp)

Unblocks the one site mvp's `precise-product-types-coefficient-cleanup` had to leave alone:
`mathutils.py:309` `find_normal` does `n = bivector.dual()` (bivector `: Bivector3`) then reads a
coefficient. With `Bivector3.dual() -> Vector3`, that becomes a direct `.coeff_*` field read like the
wedge sites. Re-scan mvp for `.coefficient()` reads on `dual()` results after this ships.

## Verify

Regenerate; `ty` src/tests/tools clean; `reveal_type` precise (`Bivector3.dual() → Vector3`); add
`assert_type` guards to `tests/test_operator_typing.py`; suite/regions/determinism green; runtime
values unchanged (pure static-typing fix).

## Relationships

- Same family/rationale as `tasks/reference/generated-product-typing.md`; the archived
  `retype-even-odd-part-off-self` is the closest sibling (base retype off `-> Self`).
- `tasks/model-odd-graded-type.md` (Rotor_n.dual widening).
- mvp `tasks/precise-product-types-coefficient-cleanup.md` (the `find_normal` residual).
