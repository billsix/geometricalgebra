# gacalc

A from-scratch **Geometric (Clifford) Algebra** library in Python, written as a faithful,
pedagogical implementation of Hestenes & Sobczyk, *Clifford Algebra to Geometric Calculus*.
Many methods cite the page/equation number they implement. The same code runs both
**numerically and fully symbolically** (coefficients may be Python numbers or `sympy` expressions).

The algebra of *n*-dimensional Euclidean space is written 𝒢ₙ (Hestenes' notation). User-facing
docs live in `README.md` (quick-start + how to generate a new algebra); this file is the
contributor/architecture overview.

## Module layout

The library is split one-concept-per-file so a newcomer can import just the algebra they need:

- `src/gacalc/functions.py` — the **leaf** composable-function layer: `ComposableFunction` (compose
  + LaTeX label, no inverse) + its subtype `InvertibleFunction` (+ inverse), `Linearity`,
  `NotInvertibleError`, `compose`/`inverse`/`identity`. **Imports nothing internal** (unbounded
  `TypeVar`); this is what `base` is allowed to import (see the **Layering** note below).
- `src/gacalc/base.py` — `MultiVectorBase` (the abstract base) + the type aliases
  `BladeCoef`, `MultiVectorFn`. Imports only the `functions` leaf (so `project`/`reject`/`reflect`
  return `ComposableFunction`/`InvertibleFunction`); see the **Layering** note below.
- `src/gacalc/gn.py` — `Gn`, the general dimension-agnostic representation, plus the
  `e_1..e_10` / `zero` / `one` constants, the symbolic vectors (`sym_vec2_1`, …), and the
  `MultiVector = Gn` alias. (Re-exports the transform layer, which itself re-exports `functions`.)
- `src/gacalc/transforms.py` — the representation-agnostic transform *factory* layer
  (`translate`/`uniform_scale`/`scale_non_uniform`/`to_matrix`, plus the rotation factories
  `projection_rotation` / `rotor_rotation(from, to)` / `plane_rotation(a, b)`); derives any basis it
  needs from the value's own type, so it preserves `Gn`/`G1`/`G2`/`G3`. **Re-exports** the
  `functions` names (`ComposableFunction`, `InvertibleFunction`, `compose`, `inverse`, …) so
  `from gacalc.transforms import InvertibleFunction` and `gn.py` keep working.
- `src/gacalc/g1.py`, `g2.py`, `g3.py` — **generated** modules, **not tracked in git**
  (gitignored). Each holds the full specialized class `G1`/`G2`/`G3` **and** that algebra's **graded
  subtypes** (`Vector_n`, `Bivector_n`, `Trivector3`, `Rotor_n`). Do not edit by hand. They are
  produced into the working tree by `make generate` / `make shell` and baked into the sdist+wheel at
  build time (see Code generation / Dev workflow).
- `src/gacalc/scalar.py` — **generated** (also gitignored): the shared grade-0 `Scalar` type
  used by the graded subtypes of every 𝒢ₙ.
- `src/gacalc/nbplotutils.py` — matplotlib/LaTeX plotting helpers for notebooks.
- `notebooks/displaymv.py` (general `Gn`), `displayg2.py`/`displayg3.py` (specialized classes),
  `displaygraded.py` (graded subtypes) — jupytext (percent-format) demo notebooks.
- `tests/test_multivector.py` — original `Gn` tests; `tests/test_conformance.py` — parametrized
  conformance over `[Gn, G1, G2, G3]`; `tests/test_graded.py` — the graded-subtype suite (return
  type + value per operation); `tests/test_generator.py` — unit tests for the *generator's own*
  logic (blade naming, the type registry / `resolve`, `product_result`/`unary_result` result-type
  resolution, astbuild DSL invariants). **~246 tests** (incl. doctests via `--doctest-modules`).
- `tools/gen_specialized.py` — the code generator (builds each module as Python `ast` nodes, rendered
  with `ast.unparse`); `tools/astbuild.py` — its domain-agnostic node-builder DSL; `tools/bench.py` —
  `Gn`-vs-specialized benchmark.
- `entrypoint/` — container build/run scripts and **a large vendored Emacs `.emacs.d/elpa/` tree**.
  **The vendored Emacs tree is intentional and off-limits.** It is committed on purpose so the author
  has a reproducible, consistent Emacs environment in the container; do **not** read it, edit it,
  reformat it, gitignore it, or factor it into any analysis. It is not project source and is none of
  Claude's concern. (Tooling that walks the repo — e.g. `format.sh` — should be scoped away from it;
  see Dev workflow.)

**Layering (invariant + relaxation, 2026-07-17).** The core dependency graph is **acyclic** — that
is the actual invariant that "`base.py` imports nothing internal" was a proxy for. `base.py` may
import **leaf modules** (modules that import *nothing* internal), but never anything at or above its
layer. A module qualifies as a base-importable leaf only if it: (1) **imports nothing internal**
(keeps the graph acyclic); (2) is **representation-agnostic** (no dependency on `gn`/`g1`/`g2`/`g3`);
(3) is **cheap to import** (no numpy; sympy is already a `base` dep). This documents *why* base may
import such a module and bounds what future additions are allowed, so "leaf" never becomes a loophole
for pulling arbitrary code under `base`. **The first (and only) such leaf is `functions.py`** (landed
2026-07-17): the domain-agnostic function-composition abstraction (`ComposableFunction` base +
`InvertibleFunction` subtype, `Linearity`, `NotInvertibleError`, `compose`/`inverse`/`identity`), so
`base`'s `project`/`reject`/`reflect` return `ComposableFunction`/`InvertibleFunction`. Constraint (1)
is *why* that module's `TypeVar` is **unbounded** rather than bound to `MultiVectorBase` — binding it
would force `functions.py` to import `base` and reintroduce the cycle.

## Architecture

**Abstract base + interchange protocol.** `MultiVectorBase` (in `base.py`) holds every
representation-independent method, written against a tiny interchange protocol so a concrete
representation only implements the primitives. The boundary is *"touches the raw representation"*,
not *"transitively uses the product"* — e.g. `inner_product`/`reverse`/`project` live in the ABC and
call `self * other`, dispatched to the concrete type.

- **Primitives** a concrete class must supply: `from_blade_dict` (classmethod), `to_blade_dict`,
  `_geometric_product`, and `__eq__`. Shared methods build results via `type(self).from_blade_dict()`
  / `type(self).zero()` so they stay polymorphic.
- A *blade* is a tuple of basis-vector indices, e.g. `(1, 2)` ≙ e₁e₂. The geometric product
  canonicalizes concatenated blades via the recursive `decrease_grade` helper (structural `match`):
  bubble-sort adjacent indices with a sign flip, annihilate repeats (eᵢeᵢ = 1 — **Euclidean
  signature is hardcoded**).

**`Gn` — the general reference.** A `@dataclass` wrapping `coefficient_of_blade:
dict[tuple[int,...], coef]`; works in any dimension. Its `__post_init__` **eagerly
`sympy.simplify`s** every coefficient. That is the dominant cost (~100% of runtime, profiled), and
it is kept **on purpose**: `Gn` is the slow-but-obviously-correct reference.

**`G1`/`G2`/`G3` — specialized fast paths.** Named-field dataclasses whose **coefficient fields are
`coeff_scalar`, `coeff_e_1`, … `coeff_e_12`/`coeff_e_123`** (the `coeff_` prefix frees the bare blade
names `e_1` … to denote the basis-vector *constants* below) and whose `_geometric_product`,
`inner_product`, `outer_product`, and the linear/grade ops (`__add__`, `reverse`, `r_vector_part`,
`even_part`, …) are **closed-form code generated from the `Gn` symbolic ops** — so they are provably
consistent with the reference. They do **not** eagerly simplify (lazy, on equality), and they carry
`DIMENSION` so `dual()` / `unit_pseudoscalar()` default to the class's dimension. **Every generated
value type is `@dataclass(slots=True)`** — the full `G1`/`G2`/`G3`, the graded subtypes
(`Vector_n`/`Bivector_n`/`Trivector3`/`Rotor_n`), and the shared `Scalar` — so instances carry no
per-instance `__dict__` (the base `MultiVectorBase` declares empty `__slots__` for this).

**Coefficient-view helpers (`base.py`).** `simplified()` / `expanded()` return the same multivector
with each coefficient `sympy.simplify`'d / `sympy.expand`'d — for the lazy classes, whose raw
coefficients aren't reduced (e.g. a bivector times its dual whose terms should cancel, or a fully
distributed product). They're on `MultiVectorBase` (work on every representation via the
`_map_coefficients` interchange helper); `Gn` already eager-simplifies, so `simplified()` is a no-op
there. **Caveat — these can't force a coefficient *form* on `Gn`:** because they rebuild via
`from_blade_dict`, `Gn.__post_init__` re-runs `sympy.simplify` and re-canonicalizes the result (e.g. a
just-`expanded()` numerator gets re-factored back to `a0*(b0 + c0)`). So for a **display** form that
must hold regardless of representation, transform the **blade dict directly** without rebuilding the
multivector — see `nbplotutils._expand_numerators_dict` (used by `show_mult` to expand numerators but
keep denominators factored, surviving `Gn`'s eager simplify). Reading a single coefficient back out:
`value.coefficient(blade)` (e.g.
`v.coefficient(Vector2.e_1)`, `B.coefficient(Bivector2.e_12)`) — a thin reader that just looks the
value up in `to_blade_dict()` (no product computed, correct for any grade). The old `component`
method, which *computed* `⟨A x̃⟩` to recover a number the object already stores, was retired in its
favour; `scalar_product` remains, but it is the scalar product `⟨A B⟩`, **not** a coefficient reader
(it's sign-flipped vs the stored coefficient for grade ≥2).

**Coefficient type — `Coef = int | float | sympy.Expr`** (defined in `base.py`; `BladeCoef` is
`dict[tuple[int, ...], Coef]`). A multivector coefficient is a plain Python number or a sympy
expression. This is the **concrete** union, deliberately *not* the `numbers.Real` ABC: ty turns
`numbers.Real` arithmetic into `_ComplexLike` and then rejects `+`/`/`/`**` on it, which is what used
to force the `ty.toml` override on the generated rotor sandwich (whose closed form divides by `|R|²`
and squares coefficients). The generated `coeff_*` fields and the scalar-returning methods
(`scalar_part`, `scalar_product`, `component`, `magnitude`, `magnitude_squared`, `cosine`) are all
typed `Coef`. The generator's `cast_coef` (in `tools/astbuild.py`) skips the cast for a bare or
negated field (already `Coef`) and only wraps genuinely compound expressions.

`magnitude()` and `inverse()` **preserve numeric input.** When `|A|²` is a Python
`float` (already inexact) they return a `float` — `math.sqrt` / a plain float
reciprocal — rather than promoting to sympy; an unconditional `sympy.sqrt` /
`sympify` would otherwise turn a purely numeric pipeline symbolic (and downstream
make a `numpy` matrix `dtype=object`, which is how it surfaced — a consumer's
`np.linalg.inv` failing). An `int` `|A|²` still routes through sympy so exactness
holds (`sqrt(25) == 5`; a unit blade normalizes to `Rational`s, not floats), and
symbolic coefficients stay symbolic. **Don't reintroduce an unconditional
`sympy.sqrt` / `sympify` on these paths** (covered by `tests/test_numeric_magnitude.py`).

Two ways to name a basis blade: each `g*` module exports **module-level** constants of its own type
(`from gacalc.g2 import G2, e_1, e_2` then `3*e_1 + 4*e_2` builds a `G2`); and each **class** exposes
its own basis blades as **class constants of that class's type** (`Vector2.e_1`, `Bivector2.e_12`,
`G3.e_123`) — equivalent to `cls.basis_vector(n)` but named. These are emitted by the generator as a
`ClassVar` declaration in the class body plus a post-class `Cls.e_1 = Cls.from_blade_dict(...)`
assignment (a class can't reference itself mid-definition). Because the stored field is `coeff_e_1`,
**both `Cls.e_1` and `instance.e_1` resolve to that one constant** (no instance attribute shadows it),
while `instance.coeff_e_1` is the component value; read a coefficient back out with
`value.coefficient(Vector2.e_1)` (thin reader over `to_blade_dict()`). `Gn` is dimension-agnostic so it has **no** class constants — use the
module-level `gn.e_1 …` or `Gn.basis_vector(n)`. Mixing a specialized value with a `Gn` value coerces
to `Gn`.

**Iteration yields coefficient values, not blade terms.** `iter(value)` / `list(value)` /
`tuple(value)` / `np.array([list(v), …])` yield the coefficient *values* in blade order — so a vector
reads as its coordinate tuple and feeds numpy/plotting directly. This is the generated `__iter__` on
every specialized class (all fields, dense) and `MultiVectorBase.__iter__` on `Gn` (its present
blades). To decompose a value into one single-blade multivector per term instead (e.g. for a
component-by-component product breakdown), iterate `to_blade_dict()` — which is what
`nbplotutils.show_mult` (via its `_blade_terms` helper) does.

**Terminology:** 𝒢ₙ denotes the *algebra*; an instance is an *element of* 𝒢ₙ. Classes are named
after their algebra. The dimension parameter is `n` (it was once misleadingly called `grade`).

**Transforms & the composable-function hierarchy.** The function abstraction (in `functions.py`,
re-exported from `transforms.py` + `gn.py`) is split by *capability*: **`ComposableFunction`** wraps a
function + LaTeX label, composable via `@` / `compose` (+ a `Linearity` class and the `at`/`steps`
animation layer), and **`InvertibleFunction(ComposableFunction)`** adds an `inverse` (+
`latex_repr_inv`). This split exists because the layer serves two consumers with different needs:
mvp's Cayley-graph engine *requires* invertibility (it walks edges backward via `inverse`), while
display/compose pipelines don't. So a non-invertible function simply *is* a `ComposableFunction`, not
an `InvertibleFunction` — a projection-as-Cayley-edge is a **type** error, not a runtime surprise.
`project` / `reject` return `ComposableFunction` (a projection discards information — not invertible);
`reflect` returns `InvertibleFunction` (an involution, its own inverse); `identity`/`translate`/scales/
rotations are `InvertibleFunction`. **`compose` returns an `InvertibleFunction` iff every part is
invertible** (else `ComposableFunction`); `inverse()` raises **`NotInvertibleError`** on a
non-invertible input (the runtime backstop when the type distinction is bypassed). To label a bare
callable, **construct the type directly** (`ComposableFunction(fn, "P_{B}")` /
`InvertibleFunction(func=…, latex_repr=…, inverse=…, latex_repr_inv=…)`) — there is no `labeled`
helper. `project`/`reject`/`reflect` return types are typed at `MultiVectorBase` (not `Self`): a
caller wanting the concrete parameter (`ComposableFunction[Vector3]`) casts at the use site. This
layer is shared with *modelviewprojection*; Jupyter display via `_repr_latex_`. Follow-ups
(module naming, animation-layer placement) live in `tasks/reassess-composable-function-interface.md`.

**Rotations & rotors.** The rotor *builder* lives on `MultiVectorBase` (`base.py`):
`rotor_from_vectors(from, to)` builds the rotor `R = |from||to| + to·from` (scalar + bivector, the
even-subalgebra grade), acting in **any plane, any dimension/representation**. The rotation
*factories* are representation-agnostic **free functions in `transforms.py`** (each derives its basis
from the operand's own type): `projection_rotation(from, to)` returns a function that rotates a vector
through the angle from `from`→`to` *in their plane* (in-plane part turned, perpendicular part left
fixed — the projection formula, equivalent to the rotor sandwich `R v R⁻¹`); `rotor_rotation(from, to)`
packages the same rotation as the rotor sandwich; and `plane_rotation(a, b)` separates plane from
angle (see below). (`projection_rotation` was moved off `MultiVectorBase` — where it was the `rotate`
classmethod — and renamed 2026-07-16, so all three rotation factories live together; `rotor_from_vectors`
stays on the base as it builds a *value*, not a transform.)

**`plane_rotation(a, b)` (transforms.py, 2026-07-08) separates the plane from the angle** — the
concern `projection_rotation(from, to)` / `rotor_rotation(from, to)` conflates (its angle is locked to the two vectors, which is what mvp's
animation/interpolation fought). `a`/`b` are verified grade-1 and only *define the plane*: their
normalized wedge is the plane's unit bivector `i` (`a ∧ b == 0`, i.e. parallel vectors, is an error —
the wedge-is-zero test IS the linear-dependence test). It returns *angle → `InvertibleFunction`*:
`f = plane_rotation(e_1, e_2)` once, then `f(θ)` for any θ builds the half-angle rotor
`R = cos(θ/2) − sin(θ/2)·i` and sandwiches. Positive θ turns from `a` toward `b`; the inverse is
`f(−θ)`; `f(θ).at(t)` interpolates as `f(t·θ)`; symbolic θ stays symbolic, float θ stays numeric.
This is the sanctioned "rotate by an angle in a plane" API — the half-angle trig lives *inside* the
library, so user code never hand-builds a rotor.

`transforms.projection_rotation` is *projection-based* (it splits the operand into in-plane +
perpendicular parts) — it returns the operand's type via a runtime grade projection. The generated
`Rotor` classes additionally carry a **closed-form, type-correct `sandwich(x)`** (`R x R⁻¹`, derived
symbolically by the generator, no projection): grade-preserving, so `Rotor3.sandwich(Vector3) →
Vector3`, `…(Bivector3) → Bivector3`, etc. `projection_rotation` keeps the projection formula for
teaching both; the rotor sandwich is the fast path mvp's rotations run on. (Both agree — see
`notebooks/displayrotations.py`.)

**`project`/`reject` are grade-preserving and stay in the operand's type.** `P_B(A) = (A·B)B⁻¹`
preserves A's grade, so for a homogeneous input the result is the same grade — `base.project`'s
`is_r_vector` branch narrows the result to that grade and rebuilds it as `type(A)`. Without that,
projecting a `Vector3` onto a `Bivector3` would *widen* to `G3` (the geometric product `Vector3 *
Bivector3⁻¹` types as the odd part `{1,3}` even though the grade-3 part is identically zero for a
projection); the narrowing keeps `Vector3.project(onto=Bivector3) → Vector3`. (Same spirit as the
rotor sandwich's grade projection.)

**Convention — express rotations as `plane_rotation` (plane + angle) or `projection_rotation` /
`rotor_rotation` / `rotor_from_vectors` (from/to), never hand-built.**
When writing or reviewing examples, tests, notebooks, or docs, a rotation must read as an explicit
`projection_rotation(from_vector=…, to_vector=…)(v)` (or `rotor_rotation(…)`) or
`cls.rotor_from_vectors(from_vector=…, to_vector=…)`
(keyword args; add `.normalize()` for a unit rotor). **Do not** hand-build a rotor as a data value —
e.g. a `G2`/`Rotor2` instance assigned from `cos(t/2) - sin(t/2)*(e_1*e_2)`. A rotor that "happens to
be" the right data but is constructed by trigonometry is treated as a regression; the whole point of
these methods is that a rotation reads as from→to, not as a derived multivector literal. (Fine:
building a *target vector* at an angle, `to = cos(a)*e_1 + sin(a)*e_2`, then feeding it to
`rotor_from_vectors`; and the rotor *definition* in `plane_of_rotation`'s docstring.)

**Convention — no local aliases for values that have a direct name.** Don't bind locals like
`E1 = Vector2.basis_vector(1)` / `I2 = E1 ^ E2` / `B12 = F1 ^ F2` / `I3 = (F1^F2)^F3` and then use
`E1`/`I2`/`B12`/`I3`. Every basis blade is directly referenceable as a **class constant of its grade's
type** — `Vector2.e_1`, `Bivector2.e_12`, `Trivector3.e_123`, `Vector3.e_3`, etc. (added in this
project; see the class-constant note above). Reference those directly instead of aliasing them.
Genuinely *derived* values with a semantic role (a specific test multivector, a `from`/`to`/`w`
vector) keep their names; the rule targets pure renames of things that already have a canonical name.

## Operators

- `*` geometric product · `^` wedge (outer) product · `@` composition of `InvertibleFunction`s
- `abs(mv)` → magnitude · inverse via `.inverse()`
- rotations: `transforms.projection_rotation(from, to)` / `rotor_rotation(from, to)` /
  `plane_rotation(a, b)` (free-function factories); `MultiVectorBase.rotor_from_vectors(from, to)`
  (the rotor builder) — any plane / representation

## Code generation

**Investigating a question about the generated code? Generate first, study the real files, then fix
the generator — never reason from memory or hand-edit the output.** Because `g1.py`/`g2.py`/`g3.py` +
`scalar.py` are gitignored, they may be absent or stale in the working tree. Whenever a question is
about the *generated* code (a value/type/attribute on `G1`/`G2`/`G3` or a graded subtype, why some
output looks the way it does, etc.): (1) run `make generate` to materialize the current files; (2)
read/poke the actual generated source (and a REPL repro) to understand the behavior; (3) only then
plan and make the change **in `tools/gen_specialized.py` (or `tools/astbuild.py`)** and regenerate —
the generated `.py` are build artifacts, so editing them by hand is always wrong and will be
overwritten.

**Consequence for review: a correct generator change shows up in `git diff` as a `tools/` diff and
*nothing* under `src/gacalc/`.** The regenerated `g1.py`/`g2.py`/`g3.py`/`scalar.py` are gitignored
(`.gitignore`), so they change on disk but never appear in `git status`/`git diff`. A thin diff
touching only `tools/gen_specialized.py` is the *expected, healthy* shape of such a change — not a
sign the work was skipped. To see the actual emitted code, open the files in `src/gacalc/` directly
(they exist on disk after `make generate`), don't look in git.

`g1.py`/`g2.py`/`g3.py` (and `scalar.py`) are generated by `tools/gen_specialized.py`, which derives
each closed form by running the general symbolic geometric/inner/outer products in `Gn`, factoring with
`sympy.cse`. It **builds each module as Python `ast` nodes** — using the domain-agnostic node-builder
DSL in `tools/astbuild.py` — and renders them with `ast.unparse` (the file header of copyright +
imports is the only raw text, since comments can't live in an AST). They are **not checked into git** —
generate them with
`make generate` (or `python tools/gen_specialized.py` directly, run from the repo root; it adds `src/`
to its own path). It **formats its own output** (runs `ruff` on the files it writes), so a regen needs
no separate format pass. **Adding a new algebra is a one-line edit** to the `ALGEBRAS` list — see the
worked `G4` example in `README.md`. Generation cost grows fast (it runs `Gn`'s symbolic ops):
sub-second for 𝒢₁/𝒢₂, tens of seconds for 𝒢₃, minutes for 𝒢₄.

**Where generation happens (the files are gitignored, so something must produce them):**
- `make shell` runs the generator inside the container (`entrypoint/shell.sh`) before the editable
  install, so the bind-mounted tree has real files for tests / `ty` / `ruff` / the IDE.
- `make dist` builds the sdist + wheel **inside the container** (the image's pinned toolchain),
  regenerating first and writing artifacts to `./dist` on the host via a bind mount (container
  `/dist`); the generated `.py` are **baked in**, so a `pip install gacalc` is fully readable without
  the end user running the generator. A `build_py` hook in `setup.py` also regenerates *if missing*
  during any build (belt-and-suspenders; needs the `numpy`+`sympy` build-requires in `pyproject.toml`).
  `make upload` / `make release` then run `twine upload` of `./dist/*` **inside the container** too
  (`twine` is baked into the image via the dev extras) — an interactive `-it` run with
  `TWINE_USERNAME=__token__`, so you just paste your PyPI API token at the prompt; nothing
  credential-bearing is stored in the image. The **only** host-side step is `git tag` in `release`
  (git stays on the host). `release` refuses if a `v<version>` tag already exists — bump `version` in
  `pyproject.toml` first. See "Releasing & PyPI auth" under Dev workflow.
- A fresh non-container checkout must `make generate` once before `pytest` / `ty` / `ruff` / `bench`
  (those import the generated modules; the generator itself does not, so it always bootstraps).

Two presentation details, both driven from the generator so they stay consistent across algebras:
the additive terms in each generated component are **ordered by grade** (scalar → vector → bivector
→ …) via `term_grade_key`; and each generated method's docstring is **copied from the matching
`MultiVectorBase` method** (`base.py`) via `inspect.getdoc`, so the Hestenes notation on the
specialized classes never drifts from the shared base.

## Dev workflow

- **Work happens in the container.** Almost every dev task runs inside the image's pinned toolchain,
  either interactively via `make shell` or through a dedicated `make` target that wraps `podman run`:
  `make test` (suite), `make dist` (build sdist+wheel), `make upload` (interactive `twine upload`),
  `make check-generated` (determinism). Even the PyPI push runs in the container (`twine` is baked in;
  `-it` + `TWINE_USERNAME=__token__` so you paste your token at the prompt). The **only** step that
  runs on the **host** is `git` — `git tag` in `make release`, and commits (the author's job, outside
  the container). When adding a new dev task, prefer a containerized `make` target over a
  "run it on your host" instruction.
- Tests: **`make test`** runs the suite inside the container (regenerates the gitignored
  `g*.py`/`scalar.py` first, then `pytest`); exit 0 on success, nonzero on failure (make reports a
  recipe failure as exit 2, not pytest's exact code — the 0/nonzero contract is what CI needs). For a
  quick host run instead, `python -m pytest -q` after a `make generate`. `pytest.ini` sets
  `pythonpath = src`, `testpaths = src tests`, and `addopts = --doctest-modules` so docstring examples
  run as tests. `nbplotutils.py` is collected (its module-load `set_matplotlib_formats` is now guarded
  by `if get_ipython() is not None:`, so it imports headless) — meaning the suite now imports
  `matplotlib`, so run it with the `notebooks` extra installed (the container has it).
- Lint/format/typecheck: `entrypoint/format.sh` runs `ruff check --fix`, `ruff format`, `ty check`.
  Ruff rules in `pyproject.toml`. **`ty check src`, `ty check tests`, and `ty check tools` are all
  fully clean.** The only ty config is `[tool.ty.environment] extra-paths = ["tools"]` in
  `pyproject.toml` — so the generator modules (`astbuild`/`gen_specialized`) resolve when checking
  `tests/test_generator.py`, which adds `tools/` to `sys.path` at runtime. That is module-resolution
  config, **not** a rule override: every rule still checks every file. (There used to be a scoped
  override disabling
  `unsupported-operator` + `invalid-method-override` on the generated rotor `sandwich`; both were
  resolved by typing coefficients as the concrete `Coef = int | float | sympy.Expr` alias rather than
  the `numbers.Real` ABC — see the coefficient-type note under Architecture — and by emitting
  `sandwich` as a Liskov-compatible override returning the operand type `_OperandT`.)
- After editing the generator, regenerate (`python tools/gen_specialized.py`, which auto-formats its
  output) and re-run the suite (the conformance tests guard correctness of the generated code).
- Determinism guard: `make check-generated` regenerates **twice** and asserts the output is
  byte-identical, catching a non-deterministic generator. (It replaced the old drift guard, which
  `git diff`ed committed generated files — meaningless now that they aren't tracked.) It mutates the
  working tree and is slow (~30s, 𝒢₃ dominates), so it's a make/CI target — **not** part of the default
  `pytest` run.
- Containerized dev (podman): `make image` then `make shell`; Jupyter on port 8888. Refresh the
  vendored Emacs packages (maintainer-only, rarely) with `make update-emacs-packages` — full rationale
  in `tasks/archive/2026/06/07/emacs-package-install-strategy.md`. (The vendored tree itself is
  off-limits; see Module layout.)
- Packaging: `pyproject.toml` (setuptools, `src/` layout). Runtime deps are **only**
  `numpy` + `sympy` (`[project] dependencies`); everything else is an optional extra —
  `notebooks` (matplotlib/ipython/pandas/jupytext), `jupyter` (JupyterLab env), `dev`
  (build/twine/ruff). There is **no `requirements.txt`** — the Dockerfile installs
  `".[dev,notebooks,jupyter]"` from these extras (the single source of truth), and
  `ruff`/`ty` come from `dnf` in the image. License: LGPL-2.1-only.
- Releasing & PyPI auth: `make dist` (build) → `make upload` (PyPI) / `make upload-test` (TestPyPI
  rehearsal) → `make release` (build + upload, then host `git tag`). All run in the container; **bump
  `version` in `pyproject.toml` first** — PyPI *and* TestPyPI permanently reject a re-used version.
  Credentials (token auth; username is always `__token__`) resolve in order: a **`~/.pypirc`** mounted
  read-only when present (`[pypi]`/`[testpypi]` sections), then **`export TWINE_PASSWORD=pypi-…`** on
  the host (passed via `-e TWINE_PASSWORD`), then the interactive `-it` prompt. **A 403 is
  account-side, not a Makefile bug** — most often an **unverified account email** (verify it before
  any upload), a token for the wrong index (`pypi.org` and `test.pypi.org` are separate
  accounts/tokens), or a **project-scoped token for a project that doesn't exist yet** (a new project
  needs an **account-scoped** token; the first successful upload *creates* the project — you don't make
  it on the website). Add `VERBOSE=1` (e.g. `make upload-test VERBOSE=1`) for twine's exact reason.

## Performance

Profiling showed eager `sympy.simplify` in `Gn.__post_init__` is ~100% of `Gn`'s cost. Rather than
weaken the reference, the specialized classes provide the speed: vs `Gn`, the geometric product is
~15–35× faster numerically and **thousands of times** faster symbolically; `reverse` ~100–170×,
`inner_product` ~40–60×. Run `python tools/bench.py` to reproduce.

## Assessment / known issues (updated 2026-06-06)

Strengths: faithful, legible translation of the textbook with equation citations; the dict-of-blades
`Gn` works in any dimension; symbolic + numeric unified via sympy; strong conformance coverage; the
specialized classes give large speedups while staying provably consistent with `Gn`.

Open issues (most are in the shared/reference code, inherited from the original single file):

1. **Fixed Euclidean signature**: eᵢeᵢ always reduces to +1. No spacetime/null/conformal signatures.
   Now documented (the classes are explicitly 𝒢ₙ over ℝⁿ), but still a hard limit.
2. **Self-flagged uncertainty**: `inverse`, `is_parallel_to` carry "not sure if I'm doing this
   correctly" comments; not all verified against known results. (Coefficient read-back is no longer a
   concern — `component` was replaced by `coefficient(blade)`, a thin reader over `to_blade_dict()`
   that's correct for any grade; covered by `test_coefficient_readback`.)

## Future directions (not yet decided)

- ~~**Graded / blade subtypes**~~ — **built** (`Vector_n`/`Bivector_n`/`Trivector3`/`Rotor_n`/
  `Scalar`). Emitted by `tools/gen_specialized.py` alongside the full classes; each bilinear product
  is a `match` on the rhs type whose **return type is resolved at generation time** from the symbolic
  result's grade support (smallest covering registered type, else widen to the full `G_n`) — so the
  type follows the *operation*, never runtime float values. `+`/`-` narrow the same way. See the
  README "Graded subtypes" section (with the return-type table) and `tasks/graded-blade-subtypes.md`.
- **Paravectors** (scalar + vector; the Algebra-of-Physical-Space object that yields a Lorentzian
  norm from Euclidean 𝒢₃): the author does **not yet know this area well enough** to commit to a
  design. Noted here because **future work may use them** (e.g. as one of the graded subtypes, or as
  a route to special-relativity demos within 𝒢₃). Revisit once the author has studied APS; until
  then, do not implement paravector-specific machinery.
