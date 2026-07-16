# Reassess the composable-function interface now that non-invertible functions exist

**Status:** proposed — needs go-ahead (research + suggestions; nothing implemented)
**Created:** 2026-07-16

## Goal

We just added non-invertible labelled functions (`transforms.labeled` + `NotInvertibleError`,
2026-07-16). That exposed a design question the single `InvertibleFunction` type can no longer
answer cleanly: **it is doing two jobs with conflicting requirements.** Reassess the abstraction —
should there be a *higher-level or separate* type for "a function you can **compose** and **label
with LaTeX**", with invertibility as a *narrower* capability layered on top? This doc researches
how the current type is used across both repos and proposes concrete options.

## What exists today (the abstraction stack, `gacalc/transforms.py`)

- **`MultiVectorFn`** (`base.py`) = `Callable[[MultiVectorBase], MultiVectorBase]` — a bare
  function, no label, no compose. This is what `project` / `reject` / `reflect` / `identity` /
  `projection_rotation` return.
- **`Linearity`** enum — `LINEAR < AFFINE < NONLINEAR`, a *declared, joinable* classification (a
  composite's class is `max` of its parts). A genuine "capability flag" abstraction.
- **`InvertibleFunction`** — the workhorse: `func` + **`inverse`** + `latex_repr` +
  `latex_repr_inv` + `interpolate`/`components` + `linearity`. Composes via `@` / `compose`,
  renders LaTeX, animates via `at` / `steps`. **Invertibility is baked into the type** (name +
  two required fields) — there is *no* `Invertibility` flag paralleling `Linearity`.
- **`labeled` / `NotInvertibleError`** (new) — wraps a bare `MultiVectorFn` into an
  `InvertibleFunction` for labelling/compose; when no real inverse is supplied, the `inverse` slot
  is a **stub that raises `NotInvertibleError`**. This is the stopgap that makes the tension
  visible.

## The two consumers, and why they conflict

`InvertibleFunction` is consumed by two very different clients:

1. **Cayley-graph engine** — `modelviewprojection/.../cayley/cayleygraph.py`. A `Step.fn` and an
   `Edge` are typed `InvertibleFunction`, and the engine **traverses edges backward by calling
   `inverse(s.fn)` / `inverse(efn)`** when a route runs against an edge's orientation
   (`cayleygraph.py:157, 169`). Walking a Cayley graph of a group *requires* every generator to be
   invertible — that's a group axiom. **Invertibility is mandatory here.**
2. **Display / compose / animation pipelines** — the demos, notebooks, `mathutils.py`. These need
   `@`-composition, a LaTeX label, and interpolation. **They do not need an inverse** (except when
   a specific pipeline is explicitly reversed).

`project` / `reject` are legitimate members of consumer 2 (label a projection, compose it, show
it) but **must never** be consumer-1 edges. Today nothing in the type system stops a
`labeled(project)` — an `InvertibleFunction` — from being dropped into a Cayley `Edge`; it would
type-check and then **raise `NotInvertibleError` only when the graph is walked backward**. A
runtime landmine is exactly what a good abstraction should make unrepresentable.

## Suggestions (research output)

### Recommendation: split the capability into a layered hierarchy

Introduce a base "composable + labelable" type and make invertibility a strict extension:

```
ComposableFunction (a.k.a. LabeledFunction / Transform)
    · __call__, latex_repr, @ / compose, linearity, at / steps
    · NO inverse, NO latex_repr_inv
        ▲
        │  (adds the invertible capability)
InvertibleFunction(ComposableFunction)
    · + inverse, + latex_repr_inv
```

- `project` / `reject` labelled → **`ComposableFunction`** (compose + display, never claims an
  inverse). `reflect` (involution), `identity`, rotations, `translate`, `uniform_scale`,
  `scale_non_uniform` → **`InvertibleFunction`**.
- **Cayley `Step.fn` / `Edge` stay typed `InvertibleFunction`** → a non-invertible projection is a
  *compile-time* type error at the Cayley boundary, not a runtime `NotInvertibleError`. The group
  invariant is enforced by the type, which is the whole point.
- `labeled(...)` returns the base type by default, and an `InvertibleFunction` when a real
  `inverse` is supplied. `NotInvertibleError` / the raising stub then largely goes away —
  non-invertibility is modeled by *absence of the capability/type*, not a landmine.

### Alternative: keep one type, add an `Invertibility` flag mirroring `Linearity`

The lighter-touch option (previously "Option 5"): add `Invertibility.{INVERTIBLE, NOT_INVERTIBLE}`
as a joinable field (a composite is invertible iff *every* part is), make `inverse` optional, and
have consumers that require inversion **assert the flag**. Smaller diff, one type, symmetric with
`Linearity` — but it enforces the Cayley invariant only by a runtime check/assert, not by the type
system. Weaker than the hierarchy for catching "projection used as a group generator" early.

### Secondary issue to fold in: type erasure / generic variance

`project`/`reject`/`reflect` are annotated `-> MultiVectorFn` (erased to `MultiVectorBase`), so a
`labeled(Vector3.project(B))` is `InvertibleFunction[MultiVectorBase]`, which will **not `@`-unify**
with a concretely-typed factory (`translate(Vector3.e_3)` → `InvertibleFunction[Vector3]`) under
the invariant `Generic[V]` — runtime is fine, `ty` rejects it (hit while writing the `labeled`
tests; worked around by composing two erased labelled functions). A rethink of the interface should
decide: keep `V` and accept that mixed erased/concrete pipelines need a cast, make the generic
covariant-friendly, or have the algebra functions carry their concrete type through. Worth
resolving in the same pass since it's the same "what should the composable type be" question.

## Constraints / notes for whoever implements

- **Cross-repo, shared layer.** `InvertibleFunction` / `compose` / `inverse` live in
  `gacalc.transforms` and are imported by mvp's Cayley engine, `mathutils.py`, and ~all demos
  (166 references across mvp src). Any hierarchy change must keep mvp's `Edge`/`Step`/`Path`,
  `demoNN.py`, and the animation layer (`at`/`steps`) working — this is a coordinated change, not a
  gacalc-only one.
- The animation layer (`interpolate`, `components`, `at`, `steps`) currently lives on
  `InvertibleFunction`; decide whether it belongs on the base `ComposableFunction` (interpolating a
  projection for display is reasonable) or stays with the invertible layer.
- `to_matrix` (homogeneous matrix of a linear/affine function) is another consumer keyed off
  `linearity`, not invertibility — a data point that "linear/affine" and "invertible" are already
  orthogonal axes, supporting a capability-based design.

## Open questions

- Hierarchy (base `ComposableFunction` + `InvertibleFunction` subtype) vs. one-type-plus-
  `Invertibility`-flag? (Lean: hierarchy — it makes "projection as a Cayley edge" a type error.)
- Should the animation layer and `to_matrix` sit on the base or the invertible layer?
- Naming: `ComposableFunction` / `LabeledFunction` / `Transform` / `DisplayableFunction`?
- How to sequence the cross-repo change so mvp's Cayley engine + demos never break mid-migration
  (add the base type and widen signatures first, migrate consumers, then narrow)?
- Resolve the generic-variance/erasure wart here, or split it into its own task?
