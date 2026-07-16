# Give `project`/`reject`/`reflect` (and `projection_rotation`) LaTeX labels so they compose in the pipeline

**Status:** proposed — needs go-ahead
**Created:** 2026-07-16

## Goal

The algebra-derived functions `project`, `reject`, `reflect`, `identity` (on `MultiVectorBase`
in `base.py`) and the new `projection_rotation` (in `transforms.py`) all return a **bare
`MultiVectorFn`** (`Callable[[MultiVectorBase], MultiVectorBase]`) — they carry **no LaTeX
label**. The `transforms.py` factories (`translate`, `uniform_scale`, `scale_non_uniform`,
`rotor_rotation`, `plane_rotation`) instead return an **`InvertibleFunction`**, which holds
`latex_repr` / `latex_repr_inv` and **composes via `@` / `compose`** with the whole pipeline
rendering as one LaTeX expression (`f.latex_repr + r" \circ " + …`, transforms.py L260–269).
So today you *cannot* drop a `project`/`reject`/`reflect` into a `@`-pipeline and get a labeled,
displayable transform. Goal: make these algebra functions first-class pipeline citizens — each
returning something that carries a sensible LaTeX string (e.g. `P_{B}`, `P^{\perp}_{B}`,
`\mathrm{refl}_{B}`) and composes with the rest.

## Why

`InvertibleFunction` is the shared display/compose layer (also used by the mvp book). A rotation
already composes and renders; a projection/rejection/reflection — equally geometric, equally
worth showing in a derivation — falls out of the pipeline because it's just a lambda. Bringing
them in makes `reflect(B) @ project(A) @ translate(...)`-style pipelines render and animate
uniformly.

## Decision (Bill, 2026-07-16) — go with Option 4 (opt-in `labeled` wrapper)

**Chosen approach: Option 4.** Keep `project` / `reject` / `reflect` / `identity` returning a
**bare `MultiVectorFn`** as they do now — change *nothing* about their default return. Add a small
**`labeled(fn, latex_repr, ...)`** helper that you wrap a function with *only when* you want it to
carry a LaTeX label and take part in a display/compose pipeline. Nothing is forced; the label is
opt-in at the call site.

This sidesteps the invertibility question entirely for now: `project`/`reject` are genuinely not
invertible, and Option 4 doesn't pretend otherwise — the wrapper is about *labelling/display*, not
about claiming an inverse. (The richer options — a non-invertible labeled type, or an
`Invertibility` flag mirroring `Linearity`, i.e. the discussed Option 5 — are deferred; see
Deferred alternatives.)

**The one detail Option 4 still has to settle:** `@` / `compose` today are defined only on
`InvertibleFunction`. So decide what `labeled(...)` returns such that it composes for *display*:
either (a) it returns an `InvertibleFunction` whose `inverse` is a stub that **raises** if anyone
inverts through it (compose/label/`_repr_latex_` all work; only `.inverse()` on such a chain
errors), or (b) `compose`/`@` learn to accept a lighter label-only object. Option (a) is the
smaller change and keeps one type — note it edges toward the old "raising inverse" idea, but here
it's confined to the explicit opt-in wrapper, not baked into `project`/`reject` themselves.

## Deferred alternatives (not chosen now)

`InvertibleFunction` requires a forward **and an inverse**. The functions differ:

| function | invertible? | inverse to use |
| --- | --- | --- |
| `identity` | yes (trivially) | itself |
| `reflect(B)` | **yes — involution** | itself (reflecting twice is identity) |
| `project(B)` | **no — idempotent/lossy** | none (a projection discards the rejected part) |
| `reject(B)` | **no — idempotent/lossy** | none |
| `projection_rotation(from,to)` | yes | the reverse rotation (`to→from`) |

So a straight "return `InvertibleFunction`" works for `reflect`, `identity`, and
`projection_rotation`, but **not** for `project`/`reject`. Options for the non-invertible ones:

1. **A labeled-but-not-invertible function type** — a lighter sibling of `InvertibleFunction`
   carrying `latex_repr` + `linearity` but no inverse, that still composes for display (compose
   would need to accept it and degrade gracefully — no `inverse()` on a chain containing one).
2. ~~**`InvertibleFunction` with a sentinel/raising inverse**~~ — **rejected** (see Decision:
   pretending a projection has an inverse is exactly what we won't do).
3. **Only label the invertible ones now** (`reflect`, `identity`, `projection_rotation`) and defer
   `project`/`reject` until the option-1 type exists.

Recommendation: **option 1** (a non-invertible labeled function in the compose layer) is the
honest model — a projection genuinely isn't invertible, and the display layer shouldn't pretend
it is (per the Decision above). It's the larger change; **option 3 is a clean first increment**
that ships labeled `reflect`/`identity`/`projection_rotation` while option 1 lands the
non-invertible type for `project`/`reject`.

## Plan (Option 4)

- [ ] Settle the compose detail above: `labeled(...)` returns an `InvertibleFunction` with a
      raising `inverse` stub (option a) vs. teaching `compose`/`@` a label-only object (option b).
      Recommend (a) for the smaller footprint.
- [ ] Add `labeled(fn, latex_repr, *, latex_repr_inv=None, linearity=Linearity.NONLINEAR,
      inverse=None)` to `transforms.py` and its `__all__`. Default `latex_repr_inv` and the raising
      `inverse` stub when none is supplied; let a caller pass a real inverse when the function does
      have one.
- [ ] Leave `project`/`reject`/`reflect`/`identity`/`projection_rotation` **unchanged** (still
      bare `MultiVectorFn`). The wrapper is applied at the call site when display is wanted.
- [ ] Doctest/tests on `labeled`: it renders its LaTeX (`_repr_latex_`), composes with a real
      factory via `@` into a combined label, and `.inverse()` on a chain through a raising stub
      errors clearly.
- [ ] A notebook cell (displaygraded / displayrotations) wrapping e.g. `Vector3.project(B)` with a
      `P_{B}` label and composing it into a rendered pipeline.
- [ ] `make test` + `ruff`/`ty` clean. (Shared-layer check: nothing here changes existing
      `InvertibleFunction` behaviour, so mvp is unaffected — confirm by grep.)

## Notes / decisions

- **Cross-repo:** `InvertibleFunction` / `compose` are shared with mvp. Option 4 *adds* a wrapper
  and doesn't alter existing `InvertibleFunction` behaviour, so mvp's pipelines are untouched —
  still confirm by grep before landing.
- **No return-type change** under Option 4: `project`/`reject`/`reflect`/`identity` keep their
  `-> MultiVectorFn` annotation. That's the whole appeal — zero churn on the algebra functions;
  the label is added by the caller via `labeled(...)`.
- Because it's opt-in, the "`Invertibility` flag mirroring `Linearity`" idea (Option 5) isn't lost
  — it remains the natural upgrade path if labelling later wants to be automatic rather than
  wrapped by hand.

## Open questions

- The compose detail: `labeled` returns an `InvertibleFunction` with a raising `inverse` stub
  (recommended) vs. a new label-only object `compose` accepts?
- Exact LaTeX conventions: `P_{B}` / `P^{\perp}_{B}` / `\mathrm{refl}_{B}`? Subscript the blade by
  its own `latex_repr`, or a fixed symbol?
