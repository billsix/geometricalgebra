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
  g1.py g2.py g3.py   one specialized class each (generated)
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

## Develop

```bash
pip install -e .            # or: pip install -r requirements.txt
python -m pytest            # run the test suite
bash entrypoint/format.sh   # ruff check --fix, ruff format, ty check
```

## Generating the specialized classes

`g1.py` / `g2.py` / `g3.py` are **generated** — do not edit them by hand (they
carry an `AUTO-GENERATED` header). The generator derives each closed-form
geometric product (and other per-dimension code) from the general `Gn` symbolic
product, runs `sympy.cse`, and writes one module per algebra.

Regenerate the committed files at any time (run from the repo root — the script
adds `src/` to its own path):

```bash
python tools/gen_specialized.py
```

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
