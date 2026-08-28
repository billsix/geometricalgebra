# Branded coordinate-space types — two-parameter `Morphism[A, B]` experiment

**Status:** PARKED — filed to preserve the idea, NOT approved for implementation (William Emerison
Six <billsix@gmail.com>, 2026-08-28). Do not start without a fresh go-ahead.
**Priority:** 9
**Difficulty:** 7
**Created:** 2026-08-28 (spun out of the composable-function naming/patterns investigation)
**See also:** `tasks/archive/2026/08/29/document-composable-function-math-identity.md` (archived — the docs-only sibling — the
investigation that produced both tasks), `tasks/reference/transform-and-composable-function-layer.md`.

## The idea

Give `ComposableFunction` two type parameters — `Morphism[A, B]` for `A → B`, with
`Isomorphism[A, B]` the invertible subtype — **and** brand each coordinate space as a distinct
static type (`WorldVec = typing.NewType("WorldVec", Vector)`, `NDCVec = ...`, per space). Then:

- `translate(...)` used as paddle→world types as `Isomorphism[PaddleSpace, WorldSpace]`;
- mypy/pyright *statically* rejects applying a paddle→world transform to an NDC point, or
  composing transforms whose spaces don't line up — **the type checker enforces the Cayley
  graph's edge discipline**;
- pedagogically, "you can't mix vectors from different spaces" becomes a machine-checked lesson,
  which fits the book's coordinate-space teaching.

Math naming: one parameter = endomorphism/automorphism; two parameters = morphism/isomorphism in
a category (spaces-as-objects, transforms-as-arrows form a groupoid). Prior art for the
two-parameter shape: Haskell's `Control.Category` and the
[`invertible` package's `Bijection a b`](https://hackage.haskell.org/package/invertible),
[lens's `Iso`](https://hackage.haskell.org/package/lens/docs/Control-Lens-Iso.html); the
branding half is the "phantom types for units/frames" pattern (F# units of measure; frame-tagged
vectors in robotics libraries).

## Why it's parked (the cost side, from the 2026-08-28 investigation)

- **Today every use in both repos is `Vector → Vector` of one concrete class** (e.g. mvp
  `demo05.py:135-141` annotates `InvertibleFunction[Vector]` throughout). Without branding,
  two parameters is pure ceremony (`[Vector, Vector]` everywhere); the branding is what carries
  all the value — and all the cost.
- Every transform factory becomes space-parameterized; every vertex literal must be constructed
  *in* a space; `compose(list[...])` over a heterogeneous chain stops being expressible as
  `list[T]` (only chained binary `@` can thread `A→B→C` types).
- `functions.py` is a leaf with an unbounded `TypeVar` on purpose (`functions.py:31-34`); a
  two-parameter redesign must preserve that layering.
- Cross-repo blast radius: mvp imports these types in ~15+ demos, the Cayley layer, framebuffer
  code, and the book's `literalinclude` regions point at `functions.py` signatures — a signature
  change ripples into book prose.
- The Cayley graph already enforces space-correctness *dynamically* (`path()` only composes along
  real edges), so the static version is a refinement, not a gap-fill.

## If ever un-parked — first steps

- [ ] Prototype on a branch: `NewType`-brand two spaces in ONE mvp demo (e.g. demo05's
      paddle/world/NDC) against a minimal `Morphism[A, B]` shim; measure annotation burden vs.
      what mypy actually catches.
- [ ] Decide overlap with the kept single-parameter API: replacement, or a parallel typed façade
      (`Morphism = ComposableFunction[V]` alias world vs. a true two-param generic).
- [ ] Only then scope the gacalc change + mvp migration + book-region impact, and re-rate this
      task's Priority/Difficulty.

## Open questions

(deferred with the task — none blocking while parked)
