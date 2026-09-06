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
  (`:558`). Since 0.0.19 the two scalar factories return `InvertibleFunction[V]`, the `V` inferred from the
  caller's annotation (a `typing.cast` at their return bridges what ty cannot see through the grade-general
  scalar product) — so `f: InvertibleFunction[g3.Vector] = uniform_scale(2.0)` type-checks under ty's
  invariance enforcement (`tasks/archive/2026/09/06/ty-invariance-transform-factories-bind-v.md`).

### Rotation factories (the trio + shared rotor factory)
- **`projection_rotation`** (`transforms.py:177`), **`rotor_rotation`** (`:227`), **`plane_rotation`**
  (`:417`), **`bivector_rotation`** (`:336`) — different *specifications* of a rotation, all funnelling
  through the shared **`_unit_bivector_rotor_factory`** (`:280`, used as the default `rotor_for` at
  `:388,:488`). (The naming distinguishes the rotation *spec* from its rotor *formulation*.)
- **`g2.rotate_90_degrees()`** (2026-09-06) — the one rotation factory that lives in a *generated*
  module, not `transforms.py`, because it is 𝒢₂-only: the quarter turn is `v * e_12` in closed form
  (exact; no rotor), wrapped as an `InvertibleFunction[Vector]` with `linearity=LINEAR`, a `TypeError`
  guard on non-`g2.Vector` input, and an `interpolate` law of `plane_rotation(e_1, e_2)(t·π/2)` that
  returns the exact turn at `t >= 1`. This is why `g2.py` imports `gacalc.transforms` — allowed by the
  layering invariant below (`transforms` depends only on `base`/`functions`, never on a generated
  module). Emitter: `generate_quarter_turn` in `tools/gen_specialized.py`; design record
  `tasks/archive/2026/09/06/add-quarter-turn-to-g2.md`.

### `to_matrix` (`transforms.py:611`)
Renders a function as a **homogeneous `(n+1)×(n+1)` matrix**, with numpy/sympy backends. A NONLINEAR
function raises (per its `Linearity` tag); a `Gn` value needs its `n` supplied explicitly (unlike
`G2`/`G3`, whose dimension is fixed). Since 0.0.19 its `fn` parameter is `InvertibleFunction[typing.Any]`
(accepts concrete `[Vector]` functions and representation-agnostic ones alike; since 2026-09-06 typed
`ComposableFunction[typing.Any]` — a matrix needs only the forward map and the `linearity` tag).

### `to_matrix_template` / `MatrixTemplate` (`transforms.py`, right after `to_matrix`; 2026-09-06)
The compile-once / fill-per-frame pattern modelviewprojection's renderers had hand-copied ten times,
lifted into the library. `to_matrix_template(fn, cls, params, n=None)` runs `to_matrix(...,
backend="sympy")` once over a function built over the sympy symbols `params` and classifies every entry:
**constant** (stored in `constants`, an `np.float32` matrix with the varying entries zeroed), **slot**
(an entry that *is* parameter `k`: `(row, col, k)`, filled by plain assignment), or **expression**
(anything else, e.g. `cos(theta)`: all such entries go through ONE `sympy.lambdify` per fill). So the
model matrix `translate(tx e_1 + ty e_2) @ scale_non_uniform(w, h, 1)` fills without touching sympy
(a copy + four assignments), while a template with a symbolic rotation angle pays one lambdified call.
`fill(*values)` (also `__call__`) returns a fresh `(n+1)×(n+1)` `np.float32`, translation in the last
column, bit-identical to `to_matrix(backend="numpy")` of the numeric transform when every varying entry
is a slot (gated in `tests/test_matrix_template.py`, 24 tests: 𝒢₂ and 𝒢₃, linear and affine, `Gn`, the
method forms, the error paths). Design choices and the record:
`tasks/archive/2026/09/06/matrix-template-compile-once.md`.

**Method forms on `ComposableFunction`** (inherited by `InvertibleFunction`): `fn.to_matrix(cls, n=None,
*, backend="numpy")` and `fn.to_matrix_template(cls, params, n=None)` — thin delegations that import
`gacalc.transforms` *inside the method body*. See the layering note below.

## `@` vs `compose([...])` — a formatting rule, not a semantic one (2026-09-06)

`f @ g` and `compose([f, g])` are the same object: `__matmul__` is "`self` after `f2`", and
`compose` applies the *last* listed function first (`compose([f, g])(x) == f(g(x))`), so a chain
`a @ b @ c` is `compose([a, b, c])` verbatim — never reverse the list. The maintainer's rule: use `@`
when the expression fits on one line; the moment it would wrap, use `compose([...])` so each function
sits on its own line (ruff/black render a wrapped `@` chain as a dangling operator with the right-hand
call's arguments exploded, which is what this avoids). Applied 2026-09-06 across gacalc (README, the
`to_matrix_template` doctest, `notebooks/displaygraded.py`, `tests/test_matrix_template.py`) and
modelviewprojection (ten game engines, `demo07`); numpy matrix products written with `@` are not
compositions and were left alone.

## Layering invariant

`functions.py` is an acyclic **leaf** (unbounded `TypeVar`, no gacalc imports); `transforms.py`
re-exports `functions.py` and builds the concrete factories on top. Nothing imports "up" into
`transforms` from `functions`, and `transforms` never imports a generated module — which is what lets
a generated module import `transforms` (`g2.py` does, for `rotate_90_degrees`'s interpolation law)
without a cycle.

The one deliberate exception (2026-09-06): the `to_matrix` / `to_matrix_template` **method forms** on
`ComposableFunction` reach *up* into `transforms` — but only through a **function-local import** (plus
`typing.TYPE_CHECKING`-guarded imports for their annotations), so at module-load time `functions.py`
still imports nothing from gacalc and the graph stays acyclic. The maintainer asked for the matrix
work to be reachable as a method on the function type; this is the cheapest shape that honours both
that and the leaf rule. Do not promote those imports to module level.

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
