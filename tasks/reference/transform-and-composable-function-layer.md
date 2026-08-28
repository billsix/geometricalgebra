# gacalc — the transform & composable-function layer (how it works now)

**Reference document** — a current-state map of the `functions.py` + `transforms.py` subsystem (API
surface + data flow). The *rationale* (why overloads, why `-> MultiVectorBase` not `G2`, etc.) lives in
`tasks/reference/design-decisions.md` and `generated-product-typing.md` — this doc **points** at that,
it doesn't restate it. Not a task; update in place. Created 2026-08-27 (William Emerison Six
<billsix@gmail.com>) from a direct read (all `file:line` verified).

## Two-type capability split (`src/gacalc/functions.py`, a leaf module)

- **`ComposableFunction[V]`** (`functions.py:74`) — a callable `V → V` you can compose, with **no
  inverse**. Generic over an **unbounded** `TypeVar V` (so the module is a dependency leaf — nothing in
  `gacalc` needs to be imported here).
- **`InvertibleFunction[V]`** (`functions.py:187`) — subclass of `ComposableFunction` that **adds an
  inverse**. `inverse(f)` (`functions.py:238`) returns the inverse `InvertibleFunction`; `identity()`
  (`functions.py:353`) is the identity `InvertibleFunction`.
- **`Linearity`** (`functions.py:47`, an `IntEnum` lattice) — tags a function LINEAR / AFFINE /
  NONLINEAR; `to_matrix` (below) uses it to reject NONLINEAR.
- **`NotInvertibleError`** (`functions.py:63`) — raised when an inverse is requested but unavailable.
- **`compose`** (`functions.py:284-287`, **overloaded**) — composing a list of `InvertibleFunction`s
  yields an `InvertibleFunction`; composing `ComposableFunction`s yields a `ComposableFunction` (the type
  degrades correctly). The runtime `composed_fn` is built at `:310`.

## Transform factories (`src/gacalc/transforms.py`, builds on + re-exports `functions.py`)

These return `InvertibleFunction`s and are **representation-preserving** — they late-bind the basis from
`type(vector).basis_vector(i)` (module docstring `transforms.py:14-27`), so the same factory works across
`G2`/`G3`/`Gn`:
- **`translate(b)`** (`transforms.py:148`), **`uniform_scale(m)`** (`:518`), **`scale_non_uniform(*factors)`**
  (`:552`).

### Rotation factories (the trio + shared rotor factory)
- **`projection_rotation`** (`transforms.py:177`), **`rotor_rotation`** (`:227`), **`plane_rotation`**
  (`:417`), **`bivector_rotation`** (`:336`) — different *specifications* of a rotation, all funnelling
  through the shared **`_unit_bivector_rotor_factory`** (`:280`, used as the default `rotor_for` at
  `:388,:488`). (The naming distinguishes the rotation *spec* from its rotor *formulation*.)

### `to_matrix` (`transforms.py:598`)
Renders a function as a **homogeneous `(n+1)×(n+1)` matrix**, with numpy/sympy backends. A NONLINEAR
function raises (per its `Linearity` tag); a `Gn` value needs its `n` supplied explicitly (unlike
`G2`/`G3`, whose dimension is fixed).

## Layering invariant

`functions.py` is an acyclic **leaf** (unbounded `TypeVar`, no gacalc imports); `transforms.py`
re-exports `functions.py` and builds the concrete factories on top. Nothing imports "up" into
`transforms` from `functions`.

## Follow-on

`tasks/composable-function-followups.md` — the naming reassessment (`functions` vs `transforms` public
name; animation-layer placement). That reassessment is much easier to do well against this map, which
lays out the exact public API surface it would rename/relocate.

## Cross-links

- `tasks/reference/design-decisions.md` — the *why* (overloads, return types, factory choices).
- `tasks/reference/generated-product-typing.md` — how the generated types type their products/sums
  (the values these functions transform).
- `tasks/reference/unit-bivector-and-rotors.md` — the rotor math behind the rotation factories.
- `tasks/reference/composable-function-algebraic-identity.md` — the *math names* for this layer
  (endomorphism monoid / automorphism group, the free-word `components` pattern, the
  Cayley-vs-Schreier/groupoid story) and the library comparison behind keeping this shape.
