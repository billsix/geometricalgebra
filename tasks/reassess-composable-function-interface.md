# Reassess the composable-function interface now that non-invertible functions exist

**Status:** core landed 2026-07-17 (gacalc 0.0.9); two follow-ups still open (module naming, animation-layer placement)
**Created:** 2026-07-16

## Implemented (2026-07-17) — core hierarchy + `labeled` removal

- New leaf `src/gacalc/functions.py` (unbounded `TypeVar`): `ComposableFunction` base +
  `InvertibleFunction` subtype, `Linearity`, `NotInvertibleError`, `compose`/`inverse`/`identity`.
  `base.py` imports it; `transforms.py` keeps the GA-specific factories + `to_matrix` and re-exports
  the `functions` names for back-compat. Layering rule relaxed + documented in `CLAUDE.md`.
- `project`/`reject` return `ComposableFunction`; `reflect`/`identity` return `InvertibleFunction`
  (auto-derived labels `P_{…}` / `P^{\perp}_{…}` / `\mathrm{refl}_{…}` / `I`). `compose` returns
  `InvertibleFunction` iff all parts are (overloads); `inverse()` raises `NotInvertibleError` on a
  non-invertible. `InvertibleFunction` constructor reordered to keyword-friendly
  `(func, latex_repr, inverse, latex_repr_inv, *, linearity/interpolate/components)`.
- **`Self` typing was decided *against*** (reversed the 2026-07-17 morning decision): returns are
  typed at `MultiVectorBase`, keeping `base` cast-free; a caller wanting the concrete parameter casts
  at the use site. Net: 0 casts in the core, ~0 in real callers (measured). See the "why did this
  cost so much" discussion — the cost was the invertible/composable *distinction*, not the module split.
- **`labeled` removed** — callers construct `ComposableFunction`/`InvertibleFunction` directly.
- **mvp**: 2 constructor sites (`perspective`/`ortho` in `mathutils.py`) → keyword args; `requirements.txt`
  pin `gacalc>=0.0.9`. Verified against new gacalc by host smoke test (perspective round-trips,
  `plane_rotation` works). Full mvp *container* gate needs gacalc 0.0.9 published to PyPI first.
- Gates: gacalc containerized `make test` **285 passed** (fresh generation, pinned toolchain); host
  ty + ruff clean.

## Decisions (Bill, 2026-07-17)

## Decisions (Bill, 2026-07-17)

- **`project` / `reject` / `reflect` will return the new `ComposableFunction` type** (not a bare
  `MultiVectorFn`). This commits to the *hierarchy* design below — a base `ComposableFunction`
  (compose + LaTeX label, no inverse) with `InvertibleFunction` as its invertible subtype — over
  the lighter one-type-plus-`Invertibility`-flag alternative.
- Cross-repo breakage is acceptable: this may be an **API-breaking** change to gacalc, pushed with
  a version bump, and mvp's dependency bumped to match. So enforce the Cayley invariant properly
  rather than trade it away to avoid churn.
- **Housing — Option A (new leaf module), confirmed.** The function-composition abstraction moves
  into a **new domain-agnostic leaf module** (`src/gacalc/functions.py`): `ComposableFunction` (base:
  call + `latex_repr` + `@`/`compose` + `linearity` + `at`/`steps`, **no** inverse),
  `InvertibleFunction(ComposableFunction)` (+ `inverse` + `latex_repr_inv`), `Linearity`,
  `NotInvertibleError`, `compose`, `inverse`, `identity`, `labeled`. `base.py` imports this leaf so
  `project`/`reject`/`reflect` can return `ComposableFunction`. `transforms.py` keeps only the
  GA-specific factories (`translate` / `uniform_scale` / `scale_non_uniform` / `projection_rotation` /
  `rotor_rotation` / `plane_rotation` / `to_matrix`) and **re-exports** the moved names, so
  `from gacalc.transforms import InvertibleFunction` and `gn.py`'s re-exports keep working unchanged.
    - **Critical constraint that makes A acyclic:** `functions.py` must import **nothing internal**
      (it must NOT import `base`, or the cycle returns). So `ComposableFunction`'s `TypeVar` is
      **unbounded** (`V = TypeVar("V")`), not bound to `MultiVectorBase`. That's the whole cost of A;
      it's fine, the abstraction is genuinely domain-agnostic (its doctest runs on plain `int`s).
    - This chooses A over B2 (whole hierarchy defined *in* `base`, keeping the `MultiVectorBase`
      bound) for separation of concerns: `base` stays the multivector contract; the generic
      function algebra is its own file. The layering rule is relaxed + documented (see CLAUDE.md
      module-layout note, updated 2026-07-17) rather than silently broken.
- **Kill the erasure via `Self`.** Type the algebra methods `-> ComposableFunction[Self]` (instead of
  the erased `-> MultiVectorFn`), so `Vector3.project(B)` is `ComposableFunction[Vector3]` and mixed
  pipelines (`P @ translate(Vector3.e_3)`) type-check with no casts. `Generic[V]` stays **invariant**
  (correct for a func+inverse holder); removing the erasure is the fix, not fighting variance. This
  folds the "secondary issue" into this task — do not split it out.

## Landing plan (once implementation starts)

1. Add `src/gacalc/functions.py` (leaf, unbounded `TypeVar`) with the full hierarchy; move the
   classes/helpers out of `transforms.py`; have `transforms.py` import + re-export them for compat.
2. `base.py` imports from `functions`; retype `project`/`reject`/`reflect`/`identity` to return
   `ComposableFunction[Self]` / `InvertibleFunction[Self]`; auto-derive their labels
   (`P_{B}` / `P^{\perp}_{B}` / `\mathrm{refl}_{B}`) from the argument's own `latex_repr`.
3. Keep Cayley `Step.fn`/`Edge` typed `InvertibleFunction` → projection-as-edge is a compile error.
4. Update tests/notebooks (the `labeled` tests can drop their two-erased-functions workaround once
   `project` is concretely typed); bump gacalc version; bump mvp's dependency.

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

## Follow-up (Bill, 2026-07-17)

- **Reassess the `functions` vs `transforms` module names from a newcomer's view.** The
  leaf-vs-consumer split is an *internal* layering concern; a newcomer just wants good names and
  shouldn't need to know about leaves/import-acyclicity to find things. Since `transforms`
  re-exports everything from `functions` (`ComposableFunction`, `InvertibleFunction`, `labeled`,
  `compose`, …), a user can already `from gacalc.transforms import …` and never touch `functions`.
  Assess: (a) is "transforms" still the right public name, or should the public surface be renamed
  (e.g. `functions`/`morphisms`/`maps` as the user-facing module, with the GA-specific *factories*
  under a clearer name)?; (b) should `functions` be treated as private/internal (underscore-prefixed
  or just "don't import directly — use `transforms`") so there's **one** obvious public entry point?
  Goal: a newcomer sees good names and one place to import from, with the leaf split invisible.

- ~~**Investigate removing `labeled` entirely.**~~ **DONE 2026-07-17** — removed. No caller needed
  it (mvp never used it); the gacalc tests + `displaygraded` notebook now construct
  `ComposableFunction(fn, latex, …)` / `InvertibleFunction(func=…, latex_repr=…, inverse=…,
  latex_repr_inv=…)` directly. The two `labeled` overloads went away with it.

## Open questions (remaining)

*Resolved:* hierarchy vs. flag → **hierarchy** (see Decisions); housing → **Option A leaf module**;
erasure → **`Self` typing**.

- **Naming.** `ComposableFunction` is the working name (vs `LabeledFunction` / `Transform` /
  `DisplayableFunction`) — confirm before implementing, since it's the public type name.
- Should the animation layer (`interpolate`/`components`/`at`/`steps`) sit on the base
  `ComposableFunction` (interpolating a projection for display is reasonable) or only on
  `InvertibleFunction`? (Lean: base — it's display, not inversion.)
- Migration sequencing so mvp's Cayley engine + demos never break mid-flight (add the leaf +
  re-exports first, retype `base`, migrate consumers, then land the version bumps together).
- Resolve the generic-variance/erasure wart here, or split it into its own task?
