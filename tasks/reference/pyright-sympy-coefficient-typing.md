# Why pyright (Emacs) types `symbol * vector` as a sympy `Expr`, and what fixes it

Investigated 2026-11-10 with pyright 1.1.414 (the version `entrypoint/01-install-base.sh` pins for
lsp-pyright) and sympy 1.14, over `src/gacalc`, `tests`, `notebooks` and `book/docs/notebooks`.

## What pyright reports

410 errors in all. 215 of them are in the generated `g1.py`–`g3.py` (165 `reportOverlappingOverload`
on the precise product overloads, 38 `reportAttributeAccessIssue`, 12 `reportReturnType`). Of the other
195, **159 are one cause**: a value pyright believes is a sympy `Expr` where a multivector is declared
(101 in `tests/`, 42 in `book/`, 16 in `src/`). Typical:

```python
s_1: sympy.Symbol
s_1, s_2 = sympy.symbols("s_1 s_2")
symbolic: Vector = s_1 * e_1 + s_2 * e_2  # pyright: "Expr" is not assignable to "Vector"
```

`ty` (the CI gate) says nothing here: it types `s_1 * e_1` as `Any`.

## The cause

For `left * right`, a type checker first tries `type(left).__mul__(right)` and only falls back to
`type(right).__rmul__(left)` when that call does not type-check. sympy's `Expr.__mul__` is

```python
@sympify_return([('other', 'Expr')], NotImplemented)
@call_highest_priority('__rmul__')
def __mul__(self, other) -> Expr:
```

`other` is unannotated, so it accepts anything, and the declared return is `Expr`. pyright therefore
never consults our `__rmul__`, although at run time sympy returns `NotImplemented` and our `__rmul__`
is what runs. The same happens for a coefficient typed `Real` (`int | float | sympy.Expr`) that is not
narrowed to a number, e.g. `v.coefficient(e_1) * w` in `frame.py`: the `Expr` member of the union
makes the product `MultiVectorBase | Expr`.

Int and float literals are not affected: typeshed types `int.__mul__(other: int)`, which rejects a
multivector, so pyright falls back to our `__rmul__` and `2 * e_1` is a `Vector`.

Nothing on gacalc's side can change which `__mul__` pyright picks, short of shipping complete sympy
stubs.

## What type-checks (measured, pyright and ty)

| Spelling | pyright | ty |
|---|---|---|
| `s_1 * e_1` | `Expr` → error | `Any` |
| `Scalar(s_1) * e_1` (the graded scalar constructor) | `Vector` | `Vector` |
| `Scalar.from_real(s_1) * e_1` | `Vector` | `Vector` |
| `Gn.from_real(s_1) * gn.e_1` | `Gn` | `Gn` |
| `e_1 * s_1` (multivector on the left) | `Vector` | `Vector` |
| `typing.cast(Vector, s_1 * e_1)` | `Vector` | `Vector` |

Caveat for representation-agnostic code: `cls.from_real(c)` is **not** a safe scalar wrapper when
`cls` is a scalar-less graded type, because `Vector.from_real(3)` is the zero vector
(`tasks/graded-scalar-constructors-silent-drop.md`). Wrap with the algebra's `Scalar`, or
`type(v).one()` (which is that `Scalar` since 2026-11-10), or put the multivector on the left.

## Options for the teaching code

1. **Scalar constructor at each symbolic coefficient**, `Scalar(s_1) * e_1` (graded modules) /
   `Gn.from_real(a_1) * e_1` (`Gn`). Precise for both checkers; longer to read.
2. **Bind the symbolic coordinates as `Scalar`s** where they only ever feed multivectors, so use sites
   stay `s_1 * e_1`. Breaks wherever the same name is also used as a sympy expression (comparing a
   coefficient to `s_1`, `sympy.simplify`).
3. **Multivector on the left**, `e_1 * s_1`. Precise and short, but against the "coefficient times
   basis" convention (`CLAUDE.md`).
4. **Leave the code; accept or silence pyright** in Emacs for this one rule
   (`reportAssignmentType`, or pyright `typeCheckingMode` per directory). No code change; Emacs stays
   noisy or loses that check everywhere.
