# geometricalgebra

A from-scratch **Geometric (Clifford) Algebra** library in Python, written as a faithful,
pedagogical implementation of Hestenes & Sobczyk, *Clifford Algebra to Geometric Calculus*.
Nearly every method cites the page/equation number it implements. The same code runs both
**numerically and fully symbolically** (coefficients may be Python numbers or `sympy` expressions).

There is no README; this file is the project overview.

## Layout

- `src/geometricalgebra/multivector.py` (~1080 lines) — the entire core library.
- `src/geometricalgebra/nbplotutils.py` — matplotlib/LaTeX plotting helpers for notebooks.
- `notebooks/displaymv.py` — jupytext (percent-format) demo notebook.
- `tests/test_multivector.py` — pytest suite (23 tests).
- `entrypoint/` — container build/run scripts and **a large vendored Emacs `.emacs.d/elpa/` tree**
  (hundreds of files, not project source — see "Known issues").

## Architecture

- A `MultiVector` is a `@dataclass` wrapping `coefficient_of_blade: dict[tuple[int,...], coef]`.
  A *blade* is a tuple of basis-vector indices, e.g. `(1, 2)` ≙ e₁e₂; the value is its coefficient.
  The representation is **dimension-agnostic** — nothing is hardcoded to 2D/3D.
- `__post_init__` simplifies coefficients (via `sympy.simplify`) and prunes zero terms.
- The geometric product (`__mul__`) concatenates blades and canonicalizes each via the recursive
  `decrease_grade` helper (structural `match`): it bubble-sorts adjacent indices with a sign flip
  and annihilates repeated indices (eᵢeᵢ = 1 — **Euclidean signature is hardcoded**).
- Built on top: inner/outer (wedge `^`) products, reverse, inverse, dual, magnitude/normalize,
  grade projection (`r_vector_part`), even/odd parts, cosine/orthogonality, and transformation
  builders (project, reject, reflect, rotate).
- Module-level conveniences: `e_1..e_10`, `zero`, `one`, and symbolic vectors `sym_vec2_1`, etc.
- A second layer, `InvertibleFunction`, wraps a function + its inverse + LaTeX labels, composable
  via `@`, with `translate` / `uniform_scale` / `rotate` / `rotate_around` factories. This layer is
  shared with the author's *modelviewprojection* book project.
- Jupyter/LaTeX display via `_repr_latex_`.

## Operators

- `*` geometric product · `^` wedge (outer) product · `@` composition of `InvertibleFunction`s
- `abs(mv)` → magnitude · `mv ** -1` style inverse via `.inverse()`

## Dev workflow

- Run tests: `python -m pytest -q` (config in `pytest.ini` sets `pythonpath = src`).
- Lint/format/typecheck: `entrypoint/format.sh` runs `ruff check --fix`, `ruff format`, and
  `ty check`. Ruff lint rules are configured in `pyproject.toml`.
- Containerized dev (podman): `make image` then `make shell`; Jupyter is exposed on port 8888.
- Packaging: `pyproject.toml` (setuptools, `src/` layout, deps pinned in `requirements.txt`).
- License: GPL v2+.

## Assessment (2026-06-04)

All 23 tests pass. Snapshot of strengths and known issues so future sessions don't re-derive them.

### What's good

- Faithful, legible translation of the textbook with equation citations — strong as a teaching tool.
- Dict-of-blades representation is simple and works in any number of dimensions.
- Symbolic + numeric unified for free via sympy.
- Meaningful test coverage: anticommutativity, pseudoscalar squares (grades 1–15), duals, reverse,
  inverse, projection/reflection/rotation, often checked against independent symbolic derivations.
- Tasteful operator overloading and good use of `match` / type hints; ruff configured.

### Known issues / improvement backlog

1. **Performance (biggest issue).** `__post_init__` runs `sympy.simplify()` on *every coefficient of
   every MultiVector ever constructed* (`multivector.py:48`). Because `__mul__` builds one MultiVector
   per blade-pair term and then sums them, `simplify` (very expensive) runs an enormous number of
   times — 23 trivial tests take ~23s. Use `expand`/`nsimplify`, or simplify lazily/on-display.
2. **`InvertibleFunction` doctests are broken/misleading** (`multivector.py:691-816`): they import from
   `modelviewprojection.mathutils` (a different package) and show `Vector2D`/`Vector1D` returns that
   don't exist here. Copy-pasted from the book project; would fail under `--doctest-modules` (not
   enabled, so they silently rot). TODO.org lists "add docstrings" as undone.
3. **Latent bug in `reject`/`reflect` sequence handling** (`multivector.py:531, 557`): both call
   `MultiVector.outer_product(*sequence)`, but `outer_product` is an *instance* method `(self, rhs)` —
   only works by luck for exactly 2 elements. `project` does it correctly via `outer_product_of_vectors`;
   make the three consistent.
4. **Suspicious `__rmul__` negation** (`multivector.py:223`): fall-through returns `-self.__mul__(lhs)`.
   The geometric product isn't anticommutative in general; this branch looks wrong (likely dead code).
5. **Fixed Euclidean signature**: eᵢeᵢ always reduces to +1. No non-Euclidean signatures (spacetime,
   null/conformal/projective GA). Probably intentional scope, but undocumented.
6. **Self-flagged uncertainty**: `inverse`, `is_parallel_to`, and `component` carry "not sure if I'm
   doing this correctly" comments and aren't all verified against known results.
7. **Repo hygiene**: the vendored `entrypoint/dotfiles/.emacs.d/elpa/` tree dwarfs the actual source and
   likely belongs in `.gitignore`. No README.
8. **Minor**: typos (`excuted`, `Dictionyary`, `Note invertible`, camelCase `sortedBladeDictionyEntriy`);
   malformed `\\\frac` in `scale_non_uniform_2d` LaTeX (`multivector.py:1019`); `_repr_latex_` round-trips
   coefficients through `sympy.sympify(str(x))` (fragile); test copy-paste bug — `i15` uses
   `unit_pseudoscalar(14)` instead of 15 (`test_multivector.py:345`).

Highest-impact fixes: #1 (performance) and #2 (doctests); #3 and the #8 test bug are quick correctness wins.
