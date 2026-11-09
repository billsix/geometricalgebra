# Tag InvertibleFunctions as linear / affine / non-linear

**Completed:** 2026-06-08

## What landed

`Linearity(IntEnum)` (`LINEAR < AFFINE < NONLINEAR`, int-backed so `max(...)` is the join) and a
`linearity` field on `InvertibleFunction`, in `transforms.py`. The factories tag themselves (scales and
`identity` LINEAR, `translate` AFFINE); `compose` takes the `max` of its parts; `inverse` copies the tag;
a hand-built `InvertibleFunction` (raw `func`/`inverse`, no factory) defaults to the conservative
NONLINEAR. Tests in `tests/test_transforms.py` cover the tag table and the lattice laws (compose is the
join, identity is the bottom, `translate ∘ translate` stays affine, `inverse` round-trips the tag).
`ty`/`ruff` were clean and the suite passed (200 tests).

mvp consumed it: its `mathutils` re-exports `Linearity` and its rebuilt transforms carry the tag,
confirmed working on 2026-06-08. The formal PyPI wheel release was left to the maintainer as a separate
out-of-container step.

The purpose: downstream code — notably `tasks/archive/2026/06/08/invertiblefunction-to-matrix.md` — can
ask whether a function can be a pure linear matrix, an affine homogeneous matrix, or neither, without
inspecting its body (linear → n×n, affine → (n+1)×(n+1) homogeneous, non-linear → refuse or projective).

## The classification algebra

The three classes form a total order by generality, `linear < affine < non-linear`. Linear is
`f(x) = Ax` (fixes the origin); affine is `f(x) = Ax + b`, so every linear map is affine and the tag is
the tightest class that fits; non-linear is anything else (e.g. the perspective divide).

**Composition takes the join** of the operand tags. Checking the maintainer's three claims:

| `f ∘ g` | g linear | g affine | g non-linear |
|---|---|---|---|
| **f linear** | linear | affine | non-linear |
| **f affine** | affine | affine | non-linear |
| **f non-linear** | non-linear | non-linear | non-linear |

- "Composition of linear functions is linear" — exact: `A(Bx) = (AB)x`.
- "Linear composed with affine is affine" — exact in both orders: `A(Cx+d) = ACx + Ad`,
  `A(Cx)+b = ACx + b`.
- "A non-linear makes the composite non-linear" — sound but conservative: two non-linear maps can
  collapse to linear (`f ∘ f⁻¹ = identity`, exactly the pair an `InvertibleFunction` carries). A
  structural tagger cannot see that cancellation, so the tag is an upper bound, not a proof; exactness
  would need symbolic analysis of the composite, which was out of scope.

Linear and affine are closed and exact under composition; only the non-linear row over-approximates.
**`inverse` preserves the tag:** the inverse of an invertible affine map is affine, of a linear map
linear, and non-linear stays non-linear (e.g. inverse perspective).

## Tags for the primitives

| factory | tag | why |
|---|---|---|
| `identity` | linear | `f(x)=x` |
| `uniform_scale`, `scale_non_uniform` | linear | `f(x)=Ax`, origin fixed |
| `translate` | affine | `f(0)=b≠0` |
| (mvp) `rotate`, `rotate_x/y/z`, `rotate_90` | linear | origin fixed |
| (mvp) `rotate_around`, `ortho` | affine | composed with translate, so the join is affine |
| (mvp) `perspective`, `cs_to_ndc_space_fn` | non-linear | per-point `* near/z` divide |

The rotation and projection factories live in mvp (see github.com/billsix/modelviewprojection
`tasks/archive/2026/07/09/gacalc-math-migration.md`); the tag rules were defined here so both repos
agree.
