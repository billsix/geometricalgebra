# gacalc

A small, readable **Geometric (Clifford) Algebra** library in Python, built as a
companion to Hestenes & Sobczyk, *Clifford Algebra to Geometric Calculus*. It
runs both **numerically and fully symbolically** (coefficients may be plain
numbers or `sympy` expressions) — and numeric stays numeric: a `float` vector's
`magnitude()` is a Python `float`, not a sympy object, while `int` and symbolic
inputs stay exact.

The algebra of *n*-dimensional Euclidean space is written 𝒢ₙ (Hestenes'
notation). This package gives you:

- **`Gn`** — the general, dimension-agnostic representation (any *n*), and
- **`G1` / `G2` / `G3`** — specialized, much faster representations of 𝒢₁ / 𝒢₂ /
  𝒢₃ whose geometric product is a closed form **generated from `Gn`** so it is
  provably consistent with the reference.

> Terminology: 𝒢ₙ denotes the *algebra*; an instance of a class is an *element of*
> that algebra (a multivector). The classes are named after their algebra.

## Layout

```
src/gacalc/
  base.py          MultiVectorBase (the abstract base) + type aliases
  gn.py            Gn (general 𝒢ₙ) + e_1.. constants + transforms + `MultiVector` alias
  g1.py g2.py g3.py   one specialized class each (generated, not in git -- run `make generate`)
```

All representations interoperate through one interchange format: the **blade
coefficient dictionary** (`{(1, 2): 4}` means `4·e₁e₂`; `()` keys the scalar),
read/written by `to_blade_dict()` / `from_blade_dict()`. Its full contract is
documented at `BladeCoef` in `base.py`.

> Installing from a git checkout (not from PyPI)? Run `make generate` once first —
> the specialized `g*.py` modules aren't committed; they're generated from `Gn`
> (and baked into the published wheel, so `pip install gacalc` needs no generator).

Import just the algebra you need:

```python
from gacalc.g2 import G2, e_1, e_2

a = 3 * e_1 + 4 * e_2
a.magnitude_squared()  # 25  (a vector squared is its magnitude squared)
a * a == G2.from_scalar(25)  # True
e_1 * e_2  # the unit bivector e_12
a.dual()  # the dual; n defaults to this algebra's dimension (2)
a.coefficient(e_1)  # 3   (the stored coefficient on a unit blade — a thin
#      reader over to_blade_dict; any grade, e.g.
#      B.coefficient(e_1 ^ e_2))
```

Each `g*` module exports its own basis constants (`zero`, `one`, `e_1`, …, and the
pseudoscalar `e_12` / `e_123`), each of that module's type — so `g2.e_1 * g2.e_2`
is a `G2`, and 2D vs 3D `e_1` are simply in different modules.

## Graded subtypes (Vector, Bivector, Rotor, …)

Besides the full multivector classes, each algebra has **graded subtypes** that hold
only one grade's components — the way mathematicians usually work:

| dimension | graded types |
| --- | --- |
| 𝒢₁ | `Scalar1`, `Vector1` |
| 𝒢₂ | `Scalar2`, `Vector2`, `Bivector2`, `Rotor2` (the even subalgebra, ≅ ℂ) |
| 𝒢₃ | `Scalar3`, `Vector3`, `Bivector3`, `Trivector3`, `Rotor3` (≅ the quaternions ℍ) |

The grade-0 `ScalarN` is **per algebra** (not one shared type), so its dual is precise:
`Scalar1.dual() → Vector1`, `Scalar2.dual() → Bivector2`, `Scalar3.dual() → Trivector3`
(grade 0 → the pseudoscalar).

**The product decides the return type** — resolved when the classes are generated, so it
never depends on (float-fuzzy) coefficient *values*. It is also **precise for a type checker**,
not just at runtime: the operators and products carry `@typing.overload` signatures, so a
static checker knows `a * b` is a `Rotor2` and `a ^ b` a `Bivector2` (and `2 + 3*(a^b)` a
`Rotor2`) — the `type(...)` calls below print the same types the checker infers:

```python
from gacalc.g2 import Vector2

a, b = 3 * Vector2.e_1 + 4 * Vector2.e_2, 1 * Vector2.e_1 + 2 * Vector2.e_2

type(a * b)  # Rotor2     (a·b scalar  +  a∧b bivector)
type(a ^ b)  # Bivector2  (the wedge — ask for a blade with ^)
type(a.inner_product(b))  # Scalar2
type(
    a < (a ^ b)
)  # Vector2   left contraction  a ⌋ B  (grade m−k; a.left_contraction(B))
type(
    (a ^ b) > a
)  # Vector2   right contraction B ⌊ a  (grade k−m; B.right_contraction(a))
```

The contractions follow M.D. Taylor, *An Introduction to Geometric Algebra and Geometric Calculus*
(2021), p. 103; unlike the Hestenes `inner_product`/`dot` they **include grade 0** (a scalar has a
contraction but no Hestenes dot).

Each class exposes its **basis blades as class constants of its own type** — `Vector2.e_1` /
`Vector2.e_2` (vectors), `Bivector2.e_12`, `G3.e_123`, etc. — equivalent to `cls.basis_vector(n)` but
named. They live on the class (`Vector2.e_1`); because the stored coefficient fields are named
`coeff_e_1` … (not `e_1`), an *instance* `v.e_1` resolves to the same basis constant, while
`v.coeff_e_1` is that component's value. Read a coefficient back out with
`v.coefficient(Vector2.e_1)` (a thin reader over `to_blade_dict()`).
(`Gn`, being dimension-agnostic, has no fixed class constants — use the module-level `gn.e_1 …` or
`Gn.basis_vector(n)`.)

**The value types are immutable** (`@dataclass(frozen=True, slots=True)`, and `@typing.final` — not
subclassable). Coefficient fields and the `x`/`y`/`z` coordinate properties are **read-only**: to
"change a coordinate," rebind a new value (`v = Vector2(-v.x, v.y)`) rather than mutating in place.
This makes the basis constants (`Vector2.e_1`, …) safe to share, and a multivector held in a shared
location can't be mutated out from under you.

Iterating a value yields its **coefficient values** in blade order — so `list(v)` / `tuple(v)` /
`np.array([list(v), …])` give the components (a vector reads as its coordinate tuple). To decompose
into one single-blade multivector per term instead, iterate `v.to_blade_dict()`.

Return-type table for the geometric product `*` (𝒢₂ shown):

| `*` | Scalar2 | Vector2 | Bivector2 | Rotor2 |
| --- | --- | --- | --- | --- |
| **Scalar2** | Scalar2 | Vector2 | Bivector2 | Rotor2 |
| **Vector2** | Vector2 | Rotor2 | Vector2 | Vector2 |
| **Bivector2** | Bivector2 | Vector2 | Scalar2 | Rotor2 |
| **Rotor2** | Rotor2 | Vector2 | Rotor2 | Rotor2 |

A result that spans grades no single type covers widens to the full `G_n`
(e.g. `Vector3 * Bivector3 -> G3`). Build values by linear combination of the basis
(`3*e_1 + 4*e_2`; a bivector via `e_1 ^ e_2`; a rotor via `scalar + bivector` — `+`/`-`
also narrow to the tightest type). Rotors carry `plane_of_rotation()`, and
`rotor_from_vectors(from, to)` builds the rotor whose sandwich `R v R.inverse()` equals
`projection_rotation(from, to)(v)` (a free function in `gacalc.transforms`). To separate the plane from the angle, `plane_rotation(a, b)`
(new in 0.0.8) wedge-normalizes the two vectors into a unit bivector once and returns
a factory: each `θ` yields an `InvertibleFunction` doing the half-angle rotor sandwich
(numeric `θ` stays float — no sympy in the result). Rotors can also be built the
exp-map way the textbooks write them: `exp` of a bivector *is* a rotor —
`B.exp()` returns a `Rotor2`/`Rotor3` (unit by construction), and
`exp(-(θ/2) * i)` for a unit bivector `i` equals `plane_rotation`'s half-angle
rotor (`exp` of a vector is hyperbolic, `cosh + sinh`; defined whenever `A²` is
a scalar). A full walkthrough is in
`notebooks/displaygraded.py`; the exp-map section lives in
`notebooks/displayrotations.py`.

Because the specialized/graded classes don't eagerly simplify, a symbolic result can carry
un-reduced coefficients (e.g. terms that should cancel). `v.simplified()` / `v.expanded()` return
the same value with each coefficient `sympy.simplify`'d / `sympy.expand`'d for a clean view.

## Adding a new algebra (worked example: `G4` for 𝒢₄)

The specialized classes are generated from `Gn`, so adding a dimension is a
one-line edit — no new math by hand.

1. Open `tools/gen_specialized.py` and add one entry to the `ALGEBRAS` list:

   ```python
   ALGEBRAS = [
       (1, "G1", "g1.py"),
       (2, "G2", "g2.py"),
       (3, "G3", "g3.py"),
       (4, "G4", "g4.py"),  # <-- (dimension, class name, output file)
   ]
   ```

2. Regenerate. This writes `src/gacalc/g4.py` (and rewrites the others
   identically); it auto-formats its own output:

   ```bash
   make generate          # = python tools/gen_specialized.py
   ```

That's it — `from gacalc.g4 import G4, e_1, e_2` now works. The docstring, the
`DIMENSION`, the basis constants, and all the dimension-fixed methods (`dual()`,
`unit_pseudoscalar()`, …) are generated automatically; you do **not** touch
`base.py` or `gn.py`. (Optional: add it to the `SPECIALIZED` map in
`tests/test_conformance.py` to include it in the conformance suite.)

> **Heads-up — generation cost grows fast.** The generator derives the closed
> forms by running the *general* symbolic geometric, inner, and outer products in
> `Gn`, which has 2ⁿ basis blades, 4ⁿ term pairs, and eagerly simplifies. 𝒢₁/𝒢₂
> generate in well under a second; 𝒢₃ takes tens of seconds; 𝒢₄ takes a few
> minutes; higher dimensions longer still. This cost is paid once, at generation
> time — the generated code itself is fast.

## Benchmarks

`python tools/bench.py` compares `Gn` against the specialized classes. The
specialized geometric product is ~15–34× faster numerically and thousands of
times faster symbolically (the general `Gn` eagerly `sympy.simplify`s every
intermediate; the closed form does a single simplify-free pass).

## Contributing

Coding standards (naming, idioms, the mutate-vs-return rule, type-annotation policy,
function shape) live in **`CLAUDE.md` › "Coding standard (Python)"** — the canonical
source. Most of PEP 8 is enforced mechanically by `ruff` (see `pyproject.toml`); that
section covers the judgment calls ruff can't. Run `make format` (ruff + ty) and
`make test` before sending a change.

## License

LGPL v2.1 (SPDX: `LGPL-2.1-only`). See `LICENSE`.
