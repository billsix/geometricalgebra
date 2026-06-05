# geometricalgebra

A from-scratch **Geometric (Clifford) Algebra** library in Python, written as a faithful,
pedagogical implementation of Hestenes & Sobczyk, *Clifford Algebra to Geometric Calculus*.
Many methods cite the page/equation number they implement. The same code runs both
**numerically and fully symbolically** (coefficients may be Python numbers or `sympy` expressions).

The algebra of *n*-dimensional Euclidean space is written 𝒢ₙ (Hestenes' notation). User-facing
docs live in `README.md` (quick-start + how to generate a new algebra); this file is the
contributor/architecture overview.

## Module layout

The library is split one-concept-per-file so a newcomer can import just the algebra they need:

- `src/geometricalgebra/base.py` — `AbstractMultiVector` (the abstract base) + the type aliases
  `BladeCoef`, `MultiVectorFn`. Imports nothing internal.
- `src/geometricalgebra/gn.py` — `Gn`, the general dimension-agnostic representation, plus the
  `e_1..e_10` / `zero` / `one` constants, the symbolic vectors (`sym_vec2_1`, …), the
  `InvertibleFunction` + transform layer (`translate`/`rotate`/…), and the `MultiVector = Gn` alias.
- `src/geometricalgebra/g1.py`, `g2.py`, `g3.py` — **generated** specialized classes `G1`/`G2`/`G3`
  for 𝒢₁/𝒢₂/𝒢₃ (named-field dataclasses with closed-form operations). Do not edit by hand.
- `src/geometricalgebra/nbplotutils.py` — matplotlib/LaTeX plotting helpers for notebooks.
- `notebooks/displaymv.py` — jupytext (percent-format) demo notebook.
- `tests/test_multivector.py` — original `Gn` tests; `tests/test_conformance.py` — parametrized
  conformance suite over `[Gn, G1, G2, G3]`. **118 tests total.**
- `tools/gen_specialized.py` — the code generator; `tools/bench.py` — `Gn`-vs-specialized benchmark.
- `entrypoint/` — container build/run scripts and **a large vendored Emacs `.emacs.d/elpa/` tree**.
  **The vendored Emacs tree is intentional and off-limits.** It is committed on purpose so the author
  has a reproducible, consistent Emacs environment in the container; do **not** read it, edit it,
  reformat it, gitignore it, or factor it into any analysis. It is not project source and is none of
  Claude's concern. (Tooling that walks the repo — e.g. `format.sh` — should be scoped away from it;
  see Dev workflow.)

## Architecture

**Abstract base + interchange protocol.** `AbstractMultiVector` (in `base.py`) holds every
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

**`G1`/`G2`/`G3` — specialized fast paths.** Named-field dataclasses (`scalar`, `e_1`, …, and the
pseudoscalar `e_12`/`e_123`) whose `_geometric_product`, `inner_product`, `outer_product`, and the
linear/grade ops (`__add__`, `reverse`, `r_vector_part`, `even_part`, …) are **closed-form code
generated from the `Gn` symbolic ops** — so they are provably consistent with the reference. They do
**not** eagerly simplify (lazy, on equality), and they carry `DIMENSION` so `dual()` /
`unit_pseudoscalar()` default to the class's dimension. Each `g*` module also exports basis constants
of its own type, so `from geometricalgebra.g2 import G2, e_1, e_2` then `3*e_1 + 4*e_2` builds a `G2`.
Mixing a specialized value with a `Gn` value coerces to `Gn`.

**Terminology:** 𝒢ₙ denotes the *algebra*; an instance is an *element of* 𝒢ₙ. Classes are named
after their algebra. The dimension parameter is `n` (it was once misleadingly called `grade`).

**Transforms.** `InvertibleFunction` (in `gn.py`) wraps a function + inverse + LaTeX labels,
composable via `@`, with `translate` / `uniform_scale` / `rotate` / `rotate_around` factories. This
layer is shared with the author's *modelviewprojection* book project. Jupyter display via
`_repr_latex_`.

## Operators

- `*` geometric product · `^` wedge (outer) product · `@` composition of `InvertibleFunction`s
- `abs(mv)` → magnitude · inverse via `.inverse()`

## Code generation

`g1.py`/`g2.py`/`g3.py` are generated by `tools/gen_specialized.py`, which derives each closed form
by running the general symbolic geometric/inner/outer products in `Gn`, factoring with `sympy.cse`,
and emitting one module per algebra. Regenerate with `python tools/gen_specialized.py` (run from the
repo root; it adds `src/` to its own path). It **formats its own output** (runs `ruff` on the files it
writes), so a regen needs no separate format pass. **Adding a new algebra is a one-line edit** to the
`ALGEBRAS` list — see the worked `G4` example in `README.md`. Generation cost grows fast (it runs
`Gn`'s symbolic ops): sub-second for 𝒢₁/𝒢₂, tens of seconds for 𝒢₃, minutes for 𝒢₄.

Two presentation details, both driven from the generator so they stay consistent across algebras:
the additive terms in each generated component are **ordered by grade** (scalar → vector → bivector
→ …) via `term_grade_key`; and each generated method's docstring is **copied from the matching
`AbstractMultiVector` method** (`base.py`) via `inspect.getdoc`, so the Hestenes notation on the
specialized classes never drifts from the shared base.

## Dev workflow

- Tests: `python -m pytest -q` (`pytest.ini` sets `pythonpath = src`).
- Lint/format/typecheck: `entrypoint/format.sh` runs `ruff check --fix`, `ruff format`, `ty check`.
  Ruff rules in `pyproject.toml`. **`ty check src` and `ty check tests` are clean; keep them so.**
- After editing the generator, regenerate (`python tools/gen_specialized.py`, which auto-formats its
  output) and re-run the suite (the conformance tests guard correctness of the generated code).
- Containerized dev (podman): `make image` then `make shell`; Jupyter on port 8888.
- Packaging: `pyproject.toml` (setuptools, `src/` layout, deps pinned in `requirements.txt`).
  License: GPL v2+.

## Performance

Profiling showed eager `sympy.simplify` in `Gn.__post_init__` is ~100% of `Gn`'s cost. Rather than
weaken the reference, the specialized classes provide the speed: vs `Gn`, the geometric product is
~15–35× faster numerically and **thousands of times** faster symbolically; `reverse` ~100–170×,
`inner_product` ~40–60×. Run `python tools/bench.py` to reproduce.

## Assessment / known issues (updated 2026-06-04)

Strengths: faithful, legible translation of the textbook with equation citations; the dict-of-blades
`Gn` works in any dimension; symbolic + numeric unified via sympy; strong conformance coverage; the
specialized classes give large speedups while staying provably consistent with `Gn`.

Open issues (most are in the shared/reference code, inherited from the original single file):

1. ~~Eager-simplify performance~~ — **resolved by design**: intentionally scoped to `Gn` (accepted
   slowness for the reference); `G1`/`G2`/`G3` are the fast, lazy-simplify path.
2. **`InvertibleFunction` doctests are broken/misleading** (`gn.py`): they import from
   `modelviewprojection.mathutils` (a different package) and show `Vector2D`/`Vector1D` returns that
   don't exist here. Would fail under `--doctest-modules` (not enabled).
3. **Latent bug in `reject`/`reflect` sequence handling** (`base.py`): both call
   `cls.outer_product(*sequence)`, but `outer_product` is an instance method `(self, rhs)` — only
   works for exactly 2 elements. `project` does it correctly via `outer_product_of_vectors`.
4. **Suspicious `__rmul__` negation** (`base.py`): fall-through returns `-self._geometric_product(lhs)`;
   the geometric product isn't anticommutative in general (likely dead code).
5. **Fixed Euclidean signature**: eᵢeᵢ always reduces to +1. No spacetime/null/conformal signatures.
   Now documented (the classes are explicitly 𝒢ₙ over ℝⁿ), but still a hard limit.
6. **Self-flagged uncertainty**: `inverse`, `is_parallel_to`, `component` carry "not sure if I'm
   doing this correctly" comments; not all verified against known results.
7. ~~Repo hygiene: `__pycache__/` not gitignored~~ — **resolved 2026-06-05**: Python artifacts
   (`__pycache__/`, `*.py[cod]`, `.pytest_cache/`, `.ruff_cache/`, egg-info, build/dist) are now in
   `.gitignore`. The vendored `entrypoint/dotfiles/.emacs.d/elpa/` tree still dwarfs the source but is
   **intentional and off-limits** (see Module layout). `format.sh` still walks the whole repo, so it
   reformats vendored/notebook files — scope it to `src tools tests` (open).
8. **Minor**: typos (`excuted`, `sortedBladeDictionyEntriy` in `gn.py`'s `decrease_grade`; `Note
   invertible`); malformed `\\\frac` in `scale_non_uniform_2d` LaTeX; `_repr_latex_` round-trips
   coefficients through `sympy.sympify(str(x))` (fragile); test copy-paste bug — `i15` uses
   `unit_pseudoscalar(14)` instead of 15 in `test_multivector.py`.
