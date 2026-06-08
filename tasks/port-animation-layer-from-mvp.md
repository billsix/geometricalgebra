# Port the InvertibleFunction animation layer from mvp into gacalc

Status: **CODE LANDED** 2026-06-08 (working tree, version still 0.0.3) · pending wheel build + mvp consumption

**Landed:** `interpolate`/`components` fields + `at()`/`steps()` methods on
`InvertibleFunction`, factories attach laws, `compose` stores `components`,
`inverse` commutes with `at` — all **in `transforms.py`** (module-shape decided:
on the class, replicating mvp, *not* a separate module). Tests in
`tests/test_transforms.py` (ported mvp interpolation suite + new). `ty`/`ruff`
clean, full suite green (200). **Also restored** `InvertibleFunction` as
`Generic[V]` (bound to `AbstractMultiVector`) — it was generic in mvp but gacalc's
plainer version wasn't; type-preserving ops (`__call__`/`at`/`steps`/`@`/`inverse`/
`compose`/`translate`/`compose_intermediate_fns`) are parameterized.

## Background

The `modelviewprojection` (mvp) project is migrating its math onto gacalc (see
`/mvp/tasks/gacalc-math-migration.md`). mvp's `InvertibleFunction` is a **strict
superset** of gacalc's: mvp added an *animation layer* — the ability to
interpolate a transform from identity (`t=0`) to its full effect (`t=1`) and to
iterate a composite's leaf steps. gacalc's `transforms.InvertibleFunction` is the
older, plainer `(func, inverse, latex_repr, latex_repr_inv)` with none of this.

For mvp to delete its own `InvertibleFunction` and import gacalc's, this layer
must live in gacalc first. Bill wants it in **a new module under `gacalc`** (not
bolted onto `transforms.py` ad hoc).

**This blocks the mvp migration AND requires a PyPI release** — mvp depends on
gacalc from PyPI (currently `0.0.3`), so this lands here, gets released (bump,
e.g. `0.0.4`), and only then can mvp pin `gacalc>=0.0.4`.

## What to port (from mvp `src/modelviewprojection/mathutils.py`)

1. **Two optional fields** on `InvertibleFunction`:
   - `interpolate: Callable[[float], InvertibleFunction] | None` — a primitive's
     law mapping `t∈[0,1]` to the partially-applied function.
   - `components: list[InvertibleFunction] | None` — a composite's constituent
     functions, so interpolation/iteration can recurse without a stored law.
2. **`at(t)`** — three-tier resolution:
   - has an `interpolate` law → use it;
   - else has `components` → `compose([c.at(t) for c in components])`;
   - else (hand-built, neither) → a step: identity until `t≥1`, then itself.
3. **`steps()`** — yield leaf primitives in application order, flattening nested
   composites (`components is None` → yield self; else recurse).
4. **Factories attach laws.** The interpolating factories set `interpolate`:
   - `translate(b)` → `lambda t: translate(b * t)`
   - `uniform_scale(m)` → `lambda t: uniform_scale(1 + (m-1)*t)` (linear 1→m)
   - `scale_non_uniform(*f)` → per-factor linear 1→fᵢ
   - `identity()` → `lambda t: identity()`
5. **`compose(...)` must store `components=list(functions)`.** gacalc's current
   `compose` does **not** — without it, `at`/`steps` can't recurse through a
   composite. This is a change to `transforms.compose`.
6. **The hard part — `inverse` must commute with `at` at *every* t**, not just the
   endpoints (so an against-the-arrow composite edge, e.g. world→camera, animates
   smoothly instead of snapping). Port mvp's logic:
   - if `f.interpolate` set → `f_inverse.interpolate = lambda t: inverse(f.interpolate(t))`
   - if `f.components` set → `f_inverse.components = [inverse(c) for c in reversed(f.components)]`
   This is the inverse-of-a-composition rule applied to the interpolation
   structure. **Bring mvp's guard test across** verbatim:
   `inverse(f).at(t)(p) == inverse(f.at(t))(p)` for all `t`, for both a primitive
   and a 3-deep composite.

## Module-shape decision (Bill's call as gacalc's architect)

Two viable designs — the instruction is "another module under gacalc":

- **(A)** Keep the enriched `InvertibleFunction` (with the two optional fields +
  `at`/`steps`) in `transforms.py` so the factories naturally produce the richer
  type, and put only thin helpers / re-exports in a new `gacalc/animation.py`.
  Pro: no circular import; the type is one thing. Con: the feature isn't really
  "in another module."
- **(B)** Put the animation-capable `InvertibleFunction` (or a subclass / mixin)
  *and* interpolating versions of the factories in a new `gacalc/animation.py`;
  `transforms.py` stays the plain core. Pro: cleanly separated, matches "another
  module." Con: two flavors of factory, and `compose` storing `components` is
  needed in both or pushed down to core.

Recommend deciding this before writing — it shapes imports across gacalc and mvp.
Whatever the choice, the **public import path mvp will use** must be settled (mvp
will `from gacalc.<module> import InvertibleFunction, translate, compose, …`).

## Tests to bring / write

- `at(0)=identity`, `at(1)=full`, midpoint correctness for translate / scale /
  (and on the mvp side) rotations.
- invertibility preserved at every `t` (`inverse(f.at(t))(f.at(t)(p)) == p`).
- composite recurses (no stored law); `steps()` flattens nested composites and
  counts leaves; inverted composite decomposes into inverted leaves.
- **inverse-commutes-with-at** for primitive and composite (the headline guard).
- against-arrow == negated-param for a primitive (`inverse(T.at(t)) == translate(-b*t)`).
- doctest the new module (gacalc runs `--doctest-modules`).

## Open questions

- Module shape: (A) vs (B) above.
- Naming of the new module (`animation.py`? `interpolation.py`?).
- Should `compose` *always* store `components` (tiny memory cost, simplest), or
  only when animation is in play? Leaning always.
- Coordinate with the linearity-tag work (`tasks/classify-functions-linear-affine-nonlinear.md`)
  and the matrix work (`tasks/invertiblefunction-to-matrix.md`) — all three touch
  the same `InvertibleFunction` / `compose` surface; ideally land their field
  additions together to avoid churning the dataclass three times.
- Release: confirm the version bump + that mvp's pin matches the released number.
```
```
