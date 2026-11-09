# Make `MultiVectorBase`'s return types true: honest overloads, plus a Protocol for transforms

**Status:** proposed — needs go-ahead (parked)
**Priority:** 7
**Difficulty:** 6
**Created:** 2026-11-08
**Source:** `tasks/archive/2026/11/08/test-all-dims-ty-gate.md` (option (a1), parked by William
Emerison Six <billsix@gmail.com>, 2026-11-08, when (a2) was chosen); `tasks/review/2026/11/08/repo-review.md`
§2.1

## BLUF

`MultiVectorBase` declares its products and sums as returning `Self`, which is false for the graded
types (`Vector * Vector` is a `Versor`). The generated graded overrides therefore carry 121
`# ty: ignore[invalid-method-override]` comments. Two changes would make the types true and remove
every suppression:

1. **Overloads in the base** that state what is actually known: a number times `x` is `Self`; a
   sum of two values of the same type is `Self`; anything else is `MultiVectorBase`.
2. **A `LinearSpace` Protocol** that bounds the generic transform factories, because adding and
   scaling (unlike the products) really do keep the type.

Done means:

- the generator stops emitting the suppression;
- `ty` is clean over src, tests, tools and the notebooks;
- the toy model in `tasks/adhoc/typing-base-return-types-redesign/` still passes, as the design
  reference.

## Context

### Why the base's `Self` is false

The base declares 15 methods as `-> typing.Self`: `_geometric_product`, `__mul__`, `__add__`,
`__radd__`, `wedge`/`outer_product`/`__xor__`, `dot`/`inner_product`, the contractions and
`__lt__`/`__gt__`, `r_vector_part`, `plane_of_rotation`. They have been typed that way since the
June typing work.

The graded types return the resolved product type, as `tasks/reference/generated-product-typing.md`
describes. The full class's `-> G` is false too: `G * Gn` returns a `Gn` (the
`test_mixing_with_gn_coerces_to_gn` contract), and the generator's `cast(Self, …)` hides it.

### What was tried (2026-11-08)

Widening the 15 base returns to `MultiVectorBase` cleared the generated modules (121 errors down to
1) but surfaced about 120 errors elsewhere:

- in `base.py`, methods that compose these operations and claim `Self` (`reverse`, `inverse`,
  `__sub__`, `__rmul__`, `__truediv__`);
- in `transforms.py`, whose factories are typed `V → V` with `V` bound to `MultiVectorBase`, false
  in general (`Scalar + Vector` is a `G`);
- in the tests, `x: Gn = a * b`.

The record is in `tasks/archive/2026/11/08/test-all-dims-ty-gate.md` › "Findings".

### Investigation: a Protocol, or `typing.overload`?

Asked by the maintainer on 2026-11-08. Checked with ty 0.0.91 on a toy model; this is a
measurement, not reasoning from memory.

**Python's type system can't compute a result type from two operand types in general.** There are
no type-level functions or associated types. The only way to say "Vector times Vector is a Versor"
is to enumerate overloads per concrete pair, which the generator already does for each algebra.
A Protocol cannot replace that enumeration, so a Protocol that "all multivectors implement" would
not fix the products. Each method in it would still need a return type, and the only true one for
an arbitrary pair is `MultiVectorBase`.

**Overloads in the base fix the contract.** The base states only what holds for every type:

- `__mul__`: `(rhs: Real) -> Self`, and `(rhs: MultiVectorBase) -> MultiVectorBase`;
- `__add__`: `(rhs: Self) -> Self`, and `(rhs: MultiVectorBase | Real) -> MultiVectorBase`;
- the grade-preserving maps (`reverse`, a sandwich) stay `-> Self`, which is true for them.

Every generated graded overload is then a compatible refinement, so ty reports no
`invalid-method-override` and no suppression is needed.

**`Gn` and the full `G` can claim their narrower types without runtime code.** `Gn` declares
`(rhs: MultiVectorBase) -> Gn` overloads in an `if typing.TYPE_CHECKING:` block, so `x: Gn = a * b`
still checks and nothing executes. `G` lists `(rhs: Gn) -> Gn` before `(rhs: MultiVectorBase) -> G`.

**A Protocol is the right tool for the generic code.** `translate(b)` and `uniform_scale(m)` use
only `+` and scalar multiplication. Every graded type is closed under those:
`tasks/reference/graded-subspaces-vs-subalgebras.md` explains that graded types are *subspaces*,
closed under the linear operations, not *subalgebras*, which would also be closed under the
products. So a Protocol

```python
class LinearSpace(Protocol):
    def __add__(self, rhs: Self, /) -> Self: ...
    def __rmul__(self, lhs: Real, /) -> Self: ...
```

with `V: LinearSpace` makes their `V → V` signatures true. The rotation factories go through the
sandwich, which keeps the operand's type, so they can keep `V → V` as well.

**Toy model.** `tasks/adhoc/typing-base-return-types-redesign/design.py` has a base with the
honest overloads, `Gn` with the type-checking-only block, a graded `Vector`, a full `G`, and the
Protocol-bounded `translate`/`uniform_scale`. With these, ty is clean, and:

- `v + v` is a `Vector`, `v * v` a `Versor`, `2 * v` a `Vector`;
- `Gn() * Gn()` is a `Gn`;
- `translate(v)(v)` is a `Vector`, `translate(Gn())(Gn())` a `Gn`.

`design_neg.py` adds three misuses, and ty rejects all three:

- `Vector = v * v` ("Versor is not assignable to Vector");
- `translate(v)(Scalar())` ("Expected Vector, found Scalar");
- `Scalar = Scalar() + v`.

Run `bash tasks/adhoc/typing-base-return-types-redesign/run.sh`.

**Read first:**

- `tasks/reference/generated-product-typing.md`, especially "Graded overrides of the base's
  `-> Self`";
- `tasks/reference/graded-subspaces-vs-subalgebras.md`;
- `tasks/reference/transform-and-composable-function-layer.md`;
- `src/gacalc/functions.py` (the invariant `ComposableFunction`/`InvertibleFunction` generics).

## Plan

- [ ] In `base.py`, replace the 15 `-> Self` signatures with the honest overloads. Re-type the
  composing methods (`__sub__`, `__rmul__`, `__truediv__`, `inverse`, `reverse`) by what each really
  returns: grade-preserving maps stay `Self`.
- [ ] Add the `TYPE_CHECKING` overload block to `Gn` (`gn.py`). Have the generator emit
  `(rhs: Gn) -> Gn` for the full `G`, and drop its `cast(Self, …)`.
- [ ] Add `LinearSpace` (in `functions.py` or `base.py`, respecting the layering rule in
  `CLAUDE.md`). Bound `translate`/`uniform_scale`/`scale_non_uniform`'s `V` by it.
- [ ] Remove `mark_graded_return_overrides` and the `header_comment` sentinel, if nothing else uses
  it. ty must then report no `invalid-method-override` on g1–g5.
- [ ] Gates:
  - `ty check --no-respect-ignore-files src` plus tests/tools/notebooks;
  - `make check-notebooks`;
  - `pytest`;
  - `make test-all-dims` (g4/g5);
  - `make check-generated`.
- [ ] `CHANGELOG.md`: a typing-only change, but a consumer's type checker sees it, so record it.

## Open questions

1. Should `LinearSpace` be public (exported for users' own generic code) or private to
   `transforms.py`? Recommendation: public, in `functions.py`, because the notebooks and users write
   the same generic helpers.
