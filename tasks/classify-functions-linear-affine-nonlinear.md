# Tag InvertibleFunctions as linear / affine / non-linear

Status: **CODE LANDED** 2026-06-08 (working tree, version still 0.0.3) · pending wheel build + mvp consumption

**Landed:** `Linearity(IntEnum)` (LINEAR<AFFINE<NONLINEAR) + a `linearity` field on
`InvertibleFunction` in `transforms.py`; factories tag themselves (scales/identity
LINEAR, translate AFFINE), `compose` = `max`(join), `inverse` copies, hand-built
defaults to NONLINEAR. Tests in `tests/test_transforms.py`. `ty`/`ruff` clean,
suite green (200).

## Goal

Give every `InvertibleFunction` (in the transform layer / the animation module) a
classification tag — **linear**, **affine**, or **non-linear** — via an enum, and
have `compose` (and `inverse`) compute the tag of the result from the tags of its
parts, rather than re-deriving it. This makes downstream code (notably the
"InvertibleFunction → matrix" task) able to ask "can this be a pure linear matrix,
an affine homogeneous matrix, or neither?" without inspecting the function body.

## The classification algebra (answering Bill's question)

The three classes form a **total order** under "generality":

```
linear  <  affine  <  non-linear
```

- **linear**: `f(x) = Ax`, fixes the origin (`f(0)=0`), additive + homogeneous.
- **affine**: `f(x) = Ax + b` — linear plus a translation. Linear is the special
  case `b = 0`, so **every linear map is also affine** (the tag is the *tightest*
  class that fits).
- **non-linear**: anything else (e.g. the perspective divide).

**Composition takes the join (max) of the operand tags.** Checking Bill's three
claims:

| `f ∘ g` | g linear | g affine | g non-linear |
|---|---|---|---|
| **f linear** | linear ✓ | affine ✓ | non-linear |
| **f affine** | affine ✓ | affine ✓ | non-linear |
| **f non-linear** | non-linear | non-linear | non-linear |

So:
- *"composition of linear functions is linear"* — **correct, exact.**
  `A(Bx) = (AB)x`.
- *"linear composed with affine is affine"* — **correct, exact** (both orders).
  `A(Cx+d) = ACx + Ad` and `A(Cx)+b = ACx + b`.
- *"a non-linear makes the composed function non-linear"* — **correct as a rule,
  but it's a *conservative* (sound over-approximation), not exact.** A non-linear
  composed with a non-linear *can* collapse to affine/linear — the cleanest
  example is `f ∘ f⁻¹ = identity` (linear), which is exactly the kind of pair an
  `InvertibleFunction` carries. A purely structural tagger can't see that
  cancellation, so it should tag the result **non-linear** and be honest that this
  is an upper bound, not a proof. (If we ever want exactness we'd need symbolic
  analysis of the composite — out of scope; the join rule is the right default.)

`linear`/`affine` are closed and **exact** under composition (they form a monoid);
only the `non-linear` row is an over-approximation.

**`inverse` preserves the tag** for linear and affine (the inverse of an
invertible affine map is affine; of a linear map, linear), and non-linear stays
non-linear (e.g. inverse-perspective). So `inverse(f)` copies `f`'s tag.

## Tags for the existing primitives (for the tests / sanity check)

| factory | tag | why |
|---|---|---|
| `identity` | linear | `f(x)=x` |
| `uniform_scale`, `scale_non_uniform` | linear | `f(x)=Ax`, origin fixed |
| `translate` | **affine** | the canonical affine-but-not-linear map (`f(0)=b≠0`) |
| (mvp-side) `rotate`, `rotate_x/y/z`, `rotate_90` | linear | origin fixed |
| (mvp-side) `rotate_around`, `ortho` | affine | `compose`(translate, …) ⇒ join is affine |
| (mvp-side) `perspective`, `cs_to_ndc_space_fn` | **non-linear** | per-point `* near/z` divide |

(The rotation/projection factories live in /mvp now — see
`/mvp/tasks/gacalc-math-migration.md` — but the tag rules are defined here so both
repos agree.)

## Sketch if yes

- An enum, e.g. `class Linearity(IntEnum): LINEAR = 0; AFFINE = 1; NONLINEAR = 2`
  (int-backed so `max(...)` *is* the join).
- Add a `linearity: Linearity` field to `InvertibleFunction` (default? — see open
  questions). Each factory sets it: scales/rotations `LINEAR`, `translate`
  `AFFINE`, perspective `NONLINEAR`.
- `compose([...])` sets `linearity = max(f.linearity for f in parts)`.
- `inverse(f)` copies `f.linearity`.
- Tests: the table above, plus the lattice laws (compose is join; identity is the
  bottom element; `translate ∘ translate` stays affine; `perspective ∘ anything`
  is non-linear; `inverse` round-trips the tag).

## Open questions

- **Default for a hand-built `InvertibleFunction`** (raw `func`/`inverse`, no
  factory): tag as `NONLINEAR` (safe/conservative) or require the caller to
  declare it? Leaning conservative default = `NONLINEAR`, optional override.
- Enum name/spelling and whether it lives in the same new module as the animation
  layer or its own (`linearity.py`). Coordinate with the animation-layer module
  decision.
- Do we want a `.is_linear()` / `.is_affine()` convenience, or just the field?
- Relationship to the matrix task: this tag should *drive* matrix construction
  (linear → n×n, affine → (n+1)×(n+1) homogeneous, non-linear → projective 4×4 +
  w-divide, or refuse). See `tasks/invertiblefunction-to-matrix.md`.
```
```
