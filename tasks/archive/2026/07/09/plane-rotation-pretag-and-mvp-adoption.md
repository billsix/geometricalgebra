# plane_rotation: pre-tag fixes + mvp facade adoption plan

**Created:** 2026-07-09 · **Completed:** 2026-07-09

A review the maintainer requested before tagging gacalc v0.0.8. It found a numeric leak in
`plane_rotation` and a missing label hook, fixed both in gacalc before the tag (the maintainer: "that
sounds great to me, and document it in comments at the call site"), and relocated the mvp-side
adoption to modelviewprojection.

## Findings (mvp demos, mvpvisualization, cayley layer — 2026-07-09)

- `mathutils`' facades (`rotate`, `rotate_90_degrees`, `rotate_x/y/z`) each hand-built
  `to_vector = cos(θ) * a + sin(θ) * b` and called
  `rotor_rotation(a, to_vector, …, interpolate=lambda t: rotate(θ * t))`, inlining exactly the job
  `plane_rotation` does in the library.
- Interpolation was where it hurt: nothing called `interpolate` directly; `cayleyscene.py` called
  `edge.fn.at(t)` per edge **per animation frame**, and `.at(t)` re-ran the facade — fresh cos/sin,
  fresh `rotor_from_vectors`, fresh `normalize`, every frame.
- **Numeric leak (measured)**: the basis constants carry exact `int` coefficients, so
  wedge→`normalize` routed through sympy for exactness (a unit blade normalizes to `Rational`s) and
  the rotor's coefficients came out sympy — a numeric-θ `plane_rotation` returned vectors with
  **sympy Float** coefficients. Downstream arithmetic on a contaminated vector: 3.71 µs/add vs
  0.60 µs clean, **~6×**. Every animated demo frame paid it, and ctc kinetix's `_turn` paid it too (a
  regression shipped with Task 2, fixed by pre-tag change 1).

## Cost model ("all we want is a new theta, correct?")

Correct — and that separation is the design:

- **Once, at factory time** (`plane_rotation(a, b)`): grade checks, wedge, zero test, normalize. The
  only place `rotor_from_vectors`-class work happens.
- **Per θ** (`rotation(θ)`, also what `.at(t)` calls via the closure): two trig calls + one small
  rotor from the cached unit bivector + two closures wrapped in an `InvertibleFunction`.
- **Per application** (`f(v)`): one sandwich, the generated closed form on `Rotor2`/`Rotor3`.

No caching layer was added: animation θ varies continuously, so a θ-keyed cache can't hit
(kinetix-style fixed angles are the exception, and `functools.cache` at the call site covers those).
The only remaining fat was the sympy contagion.

## Pre-tag gacalc changes (both backwards-compatible for `plane_rotation(a, b)(θ)`)

1. **Numeric preservation** (base.py's own convention: float in → float out). `plane_rotation`
   keeps TWO copies of the unit bivector — exact, and float-coerced when every coefficient is a
   numeric value — and picks per θ: numeric θ → float plane → float rotors/results; symbolic θ →
   exact plane, so notebooks show `cos(θ)`, not `1.0 * cos(θ)`; a symbolic plane never coerces. The
   why is documented in comments at the coercion site in `transforms.py`, per the maintainer.
2. **LaTeX label hooks** (additive API): `plane_rotation` had hardcoded `R_{θ}`; mvp's facades need
   `R_{<θ>}` / `RX_{<θ>}` / `RY` / `RZ`. Optional keyword-only `latex_repr` / `latex_repr_inv`
   callables mapping θ → label were added (mirroring `rotor_rotation`'s hooks), defaulting to the
   unchanged `R_{θ}`.

## Verification (2026-07-09)

Three new regression tests (numeric-stays-float, symbolic-stays-exact, label hooks); 280
in-container tests passed, `make check-generated` deterministic, `format.sh` clean; kinetix's `_turn`
pattern verified float again. v0.0.8 was then tagged by the maintainer.

## mvp adoption (relocated)

The remaining work was mvp-side and moved to github.com/billsix/modelviewprojection
`tasks/archive/2026/07/09/plane-rotation-mathutils-adoption.md`: mathutils facades become
module-level `plane_rotation` factories (labels via the new hooks); mvpvisualization/cayleyscene/demos
need no changes (`.at(t)` serves from the cached plane); book prose folds into the gacalc-math
migration's Phase 4; kinetix needs nothing.

## Related

`tasks/archive/2026/07/18/generated-dispatch-fast-paths.md` — the broader dispatch-cost work.
