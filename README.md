# geometricalgebra

A small, readable **Geometric (Clifford) Algebra** library in Python, built as a
companion to Hestenes & Sobczyk, *Clifford Algebra to Geometric Calculus*. It
runs both **numerically and fully symbolically** (coefficients may be plain
numbers or `sympy` expressions).

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
src/geometricalgebra/
  base.py          AbstractMultiVector (the abstract base) + type aliases
  gn.py            Gn (general 𝒢ₙ) + e_1.. constants + transforms + `MultiVector` alias
  g1.py g2.py g3.py   one specialized class each (generated, not in git -- run `make generate`)
```

Import just the algebra you need:

```python
from geometricalgebra.g2 import G2, e_1, e_2

a = 3 * e_1 + 4 * e_2
a.magnitude_squared()   # 25  (a vector squared is its magnitude squared)
a * a == G2.from_scalar(25)   # True
e_1 * e_2               # the unit bivector e_12
a.dual()                # the dual; n defaults to this algebra's dimension (2)
```

Each `g*` module exports its own basis constants (`zero`, `one`, `e_1`, …, and the
pseudoscalar `e_12` / `e_123`), each of that module's type — so `g2.e_1 * g2.e_2`
is a `G2`, and 2D vs 3D `e_1` are simply in different modules.

## Graded subtypes (Vector, Bivector, Rotor, …)

Besides the full multivector classes, each algebra has **graded subtypes** that hold
only one grade's components — the way mathematicians usually work:

| dimension | graded types |
| --- | --- |
| shared | `Scalar` (grade 0) |
| 𝒢₁ | `Vector1` |
| 𝒢₂ | `Vector2`, `Bivector2`, `Rotor2` (the even subalgebra, ≅ ℂ) |
| 𝒢₃ | `Vector3`, `Bivector3`, `Trivector3`, `Rotor3` (≅ the quaternions ℍ) |

**The product decides the return type** — resolved when the classes are generated, so it
never depends on (float-fuzzy) coefficient *values*:

```python
from geometricalgebra.g2 import Vector2

e_1, e_2 = Vector2.basis_vector(1), Vector2.basis_vector(2)
a, b = 3 * e_1 + 4 * e_2, 1 * e_1 + 2 * e_2

type(a * b)               # Rotor2     (a·b scalar  +  a∧b bivector)
type(a ^ b)               # Bivector2  (the wedge — ask for a blade with ^)
type(a.inner_product(b))  # Scalar
```

Return-type table for the geometric product `*` (𝒢₂ shown):

| `*` | Scalar | Vector2 | Bivector2 | Rotor2 |
| --- | --- | --- | --- | --- |
| **Scalar** | Scalar | Vector2 | Bivector2 | Rotor2 |
| **Vector2** | Vector2 | Rotor2 | Vector2 | Vector2 |
| **Bivector2** | Bivector2 | Vector2 | Scalar | Rotor2 |
| **Rotor2** | Rotor2 | Vector2 | Rotor2 | Rotor2 |

A result that spans grades no single type covers widens to the full `G_n`
(e.g. `Vector3 * Bivector3 -> G3`). Build values by linear combination of the basis
(`3*e_1 + 4*e_2`; a bivector via `e_1 ^ e_2`; a rotor via `scalar + bivector` — `+`/`-`
also narrow to the tightest type). Rotors carry `plane_of_rotation()`, and
`rotor_from_vectors(from, to)` builds the rotor whose sandwich `R v R.inverse()` equals
`rotate(from, to)(v)`. A full walkthrough is in `notebooks/displaygraded.py`.

## Develop

```bash
pip install -e .            # or: pip install -r requirements.txt
python -m pytest            # run the test suite
bash entrypoint/format.sh   # ruff check --fix, ruff format, ty check
```

### Updating the vendored Emacs packages

The Emacs packages are vendored in git under `entrypoint/dotfiles/.emacs.d/elpa`,
but are **not** baked into the image (excluded via `.dockerignore`; the build no
longer installs them). To refresh them to the latest from MELPA:

```bash
make update-emacs-packages   # rebuild image, wipe+reinstall elpa, strip *.elc, git add -f
git commit                   # vendor the freshly staged tree
```

It rebuilds the image with `USE_EMACS=1`, runs Emacs in the container with the
elpa tree bind-mounted read-write (so freshly installed packages land back on the
host), removes compiled `*.elc`/`*.eln` artifacts (regenerated, machine-specific),
and force-stages the tree with `git add -A -f` (the `-f` overrides the repo
`.gitignore`'s `*.elc`/`*.eln`/… patterns so the full vendored tree is committed).
Just review and `git commit`.

To *use* the vendored packages in an interactive session, start the shell with
`USE_EMACS=1` (the default is off), which bind-mounts the tree in:

```bash
make shell USE_EMACS=1
```

## Generating the specialized classes

`g1.py` / `g2.py` / `g3.py` / `scalar.py` are **generated** — do not edit them by
hand (they carry an `AUTO-GENERATED` header). The generator derives each
closed-form geometric product (and other per-dimension code) from the general
`Gn` symbolic product, runs `sympy.cse`, and writes one module per algebra.

**They are not checked into git.** Generate them into the working tree before
running tests / your IDE / `bench` (run from the repo root — the script adds
`src/` to its own path):

```bash
make generate          # = python tools/gen_specialized.py
```

`make shell` does this automatically inside the container, and `make dist` bakes
the generated code into the published sdist + wheel — so `pip install
geometricalgebra` gives you the readable closed-form source with no generation
step on your end. (See "Building & publishing" below.)

To check the generator is deterministic (regenerates byte-identically), run:

```bash
make check-generated   # regenerates twice and compares the output
```

## Building & publishing

The build/publish tools (`build`, `twine`) live in a `dev` extras group — install
them once with:

```bash
pip install -e ".[dev]"        # or:  uv pip install -e ".[dev]"
```

Then:

```bash
make dist       # regenerate, then build sdist + wheel into dist/ (generated code baked in)
make upload     # twine check + twine upload dist/* to PyPI (irreversible)
make release    # like upload, but refuses unless you bumped `version` in pyproject.toml
                # (guards against PyPI's permanent rejection of a re-used version), then git-tags it
```

`make dist` works on any platform with `python` + `sympy` + `build`; the wheel is
pure-Python (`py3-none-any`), so the same artifact installs everywhere. Building
relies on the `numpy`+`sympy` build-requires in `pyproject.toml` (the `setup.py`
`build_py` hook runs the generator if the modules are missing).

### Adding a new algebra (worked example: `G4` for 𝒢₄)

1. Open `tools/gen_specialized.py` and add one entry to the `ALGEBRAS` list:

   ```python
   ALGEBRAS = [
       (1, "G1", "g1.py"),
       (2, "G2", "g2.py"),
       (3, "G3", "g3.py"),
       (4, "G4", "g4.py"),   # <-- (dimension, class name, output file)
   ]
   ```

2. Regenerate. This writes `src/geometricalgebra/g4.py` (and rewrites the others
   identically):

   ```bash
   python tools/gen_specialized.py
   ```

3. Tidy formatting (the repo pins these tools in `requirements.txt`):

   ```bash
   ruff check src/geometricalgebra/g4.py --fix
   ruff format --line-length=88 src/geometricalgebra/g4.py
   ```

That's it — `from geometricalgebra.g4 import G4, e_1, e_2` now works. The
docstring, the `DIMENSION`, the basis constants, and all the dimension-fixed
methods (`dual()`, `unit_pseudoscalar()`, …) are generated automatically; you do
**not** need to touch `base.py` or `gn.py`.

Optional: to include the new algebra in the conformance tests, add it to the
`SPECIALIZED` map in `tests/test_conformance.py`:

```python
SPECIALIZED = {1: G1, 2: G2, 3: G3, 4: G4}
```

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

## License

GPL v2 or later. See `LICENSE`.
