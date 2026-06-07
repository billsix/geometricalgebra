# gacalc

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
src/gacalc/
  base.py          AbstractMultiVector (the abstract base) + type aliases
  gn.py            Gn (general 𝒢ₙ) + e_1.. constants + transforms + `MultiVector` alias
  g1.py g2.py g3.py   one specialized class each (generated, not in git -- run `make generate`)
```

Import just the algebra you need:

```python
from gacalc.g2 import G2, e_1, e_2

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
from gacalc.g2 import Vector2

a, b = 3 * Vector2.e_1 + 4 * Vector2.e_2, 1 * Vector2.e_1 + 2 * Vector2.e_2

type(a * b)               # Rotor2     (a·b scalar  +  a∧b bivector)
type(a ^ b)               # Bivector2  (the wedge — ask for a blade with ^)
type(a.inner_product(b))  # Scalar
```

Each class exposes its **basis blades as class constants of its own type** — `Vector2.e_1` /
`Vector2.e_2` (vectors), `Bivector2.e_12`, `G3.e_123`, etc. — equivalent to `cls.basis_vector(n)` but
named. They live on the class (`Vector2.e_1`); because the stored coefficient fields are named
`coeff_e_1` … (not `e_1`), an *instance* `v.e_1` resolves to the same basis constant, while
`v.coeff_e_1` is that component's value. Read a component back out with `v.component(Vector2.e_1)`.
(`Gn`, being dimension-agnostic, has no fixed class constants — use the module-level `gn.e_1 …` or
`Gn.basis_vector(n)`.)

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
gacalc` gives you the readable closed-form source with no generation
step on your end. (See "Building & publishing" below.)

To check the generator is deterministic (regenerates byte-identically), run:

```bash
make check-generated   # regenerates twice and compares the output
```

## Building & publishing

Releases are **built inside the container** (using the image's pinned toolchain —
`python`, `build`, `numpy`/`sympy`) and **pushed from the host** (so the
irreversible, credential-bearing upload stays under your control):

```bash
make dist       # BUILD inside the container -> sdist + wheel in ./dist on the host
                #   (regenerates the closed forms, then `python -m build`; the dist
                #    dir is bind-mounted as the container's /output)
make upload     # (host) twine check + twine upload ./dist/* to PyPI  -- irreversible
make release    # build (container) -> then (host) twine upload + git tag the version
                #   refuses unless `version` in pyproject.toml is bumped (PyPI permanently
                #   rejects a re-used version); push the tag with `git push origin vX.Y.Z`
```

The wheel is pure-Python (`py3-none-any`), so the same artifact installs
everywhere, with the generated closed-form modules baked in (`pip install gacalc`
needs no generator). Requirements:

- **Build** needs the image: `make image` first. (`make dist` mounts the live
  source and writes artifacts to `./dist`; override the location with
  `make dist DIST_DIR=/path`.)
- **Upload** runs on the host and needs `twine` there — e.g. `pipx install twine`
  (or `pip install -e ".[dev]"`, which also pulls `build`). Authenticate with a
  PyPI token (`TWINE_USERNAME=__token__`, `TWINE_PASSWORD=pypi-…`).

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

2. Regenerate. This writes `src/gacalc/g4.py` (and rewrites the others
   identically):

   ```bash
   python tools/gen_specialized.py
   ```

3. Tidy formatting (the repo pins these tools in `requirements.txt`):

   ```bash
   ruff check src/gacalc/g4.py --fix
   ruff format --line-length=88 src/gacalc/g4.py
   ```

That's it — `from gacalc.g4 import G4, e_1, e_2` now works. The
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

## Releasing

Cutting a release **builds inside the container** (reproducible toolchain) and
**pushes from the host** (the irreversible, credential-bearing step). End users
then `pip install gacalc` and `import gacalc` — the generated closed-form modules
are baked into the wheel, so they need no generator and no `sympy` at build time.

One-time host setup:

```bash
pipx install twine                      # upload runs on the host
export TWINE_USERNAME=__token__         # PyPI API token auth
export TWINE_PASSWORD=pypi-XXXXXXXX...
make image                              # the gacalc image must exist (builds the toolchain)
```

Each release:

```bash
# 1. bump the version (PyPI permanently rejects a re-used version) and commit
$EDITOR pyproject.toml                  # e.g. version = "0.1.0"
git commit -am "release 0.1.0"

# 2. build + publish + tag, all via the Makefile
make release                            # builds sdist+wheel in the container -> ./dist,
                                        # then (host) twine check + upload, then git tag vX.Y.Z

# 3. push the tag
git push origin v0.1.0
```

Or do it in two explicit steps: `make dist` (container build → `./dist/`), inspect
the artifacts, then `make upload` (host push). To rehearse without touching the
real index, upload `./dist/*` to TestPyPI first
(`twine upload --repository testpypi dist/*`).

Notes:
- `make dist` writes to `./dist` by default; override with `make dist DIST_DIR=/path`.
- The wheel is `py3-none-any` (pure Python) — one artifact installs on every OS/Python ≥ 3.13.
- `make release` aborts if a `vX.Y.Z` tag already exists, to stop accidental re-releases.

## License

GPL v2 or later. See `LICENSE`.
