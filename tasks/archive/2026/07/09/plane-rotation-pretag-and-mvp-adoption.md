# plane_rotation: pre-tag fixes + mvp facade adoption plan

**Status:** pre-tag gacalc changes DONE 2026-07-09 (Bill: "that sounds
great to me, and document it in comments at the call site") — staged,
uncommitted; **ready to tag v0.0.8 after Bill commits**. The mvp facade
adoption below happens after the release.

Implementation notes: `plane_rotation` keeps TWO copies of the unit
bivector — exact, and float-coerced when every coefficient is a numeric
value — and picks per theta (numeric theta -> float plane -> float
rotors/results; symbolic theta -> exact plane, so notebooks show
``cos(theta)``, not ``1.0*cos(theta)``; a symbolic plane never coerces).
The why is documented in comments at the coercion site in
`transforms.py`, per Bill. Label hooks: optional keyword-only
``latex_repr`` / ``latex_repr_inv`` callables mapping theta -> label
(default unchanged ``R_{theta}``). Three new regression tests
(numeric-stays-float, symbolic-stays-exact, label hooks); gates green
2026-07-09: 280 in-container tests, check-generated, format.sh clean;
kinetix's `_turn` pattern verified float again.
**Created:** 2026-07-09 (review Bill requested before tagging gacalc)

## Findings (mvp demos, mvpvisualization, cayley layer — 2026-07-09)

- `mathutils`' facades (`rotate`, `rotate_90_degrees`, `rotate_x/y/z`)
  each hand-build `to_vector = cos θ·a + sin θ·b` and call
  `rotor_rotation(a, to_vector, …, interpolate=lambda t: rotate(θ·t))`
  — inlining exactly the job `plane_rotation` now does in the library.
- Interpolation is where it hurts: nothing calls `interpolate` directly;
  `cayleyscene.py` calls `edge.fn.at(t)` per edge **per animation
  frame**, and `.at(t)` re-runs the facade — fresh cos/sin, fresh
  `rotor_from_vectors`, fresh `normalize`, every frame.
- **Numeric leak (measured)**: the basis constants carry exact `int`
  coefficients, so wedge→`normalize` routes through sympy for exactness
  (a unit blade normalizes to `Rational`s) and the rotor's coefficients
  come out sympy — a numeric-θ `plane_rotation` returns vectors with
  **sympy Float** coefficients. Downstream arithmetic on a contaminated
  vector: 3.71 µs/add vs 0.60 µs clean — **~6×**. Every animated demo
  frame pays it, and ctc kinetix's `_turn` pays it today (a regression
  shipped with Task 2; fixed for free by pre-tag change 1).

## The slowdown question ("all we want is a new theta, correct?")

Correct — and that separation is the whole design. Cost model:

- **Once, at factory time** (`plane_rotation(a, b)`): grade checks,
  wedge, zero test, normalize. This is the only place
  `rotor_from_vectors`-class work happens, and it never repeats.
- **Per θ** (`rotation(θ)`, which is also what `.at(t)` calls via the
  closure): two trig calls + assembling one small rotor from the cached
  unit bivector + wrapping two closures in an `InvertibleFunction`.
- **Per application** (`f(v)`): one sandwich — the generated closed form
  on `Rotor2`/`Rotor3`.

So after mvp's facades switch to module-level factories, the per-frame
animation cost drops from re-deriving-the-plane to
trig + rotor + sandwich. No caching layer is needed: animation θ varies
continuously, so a θ-keyed cache can't hit (kinetix-style fixed angles
are the exception, and `functools.cache` at the call site covers those).
The only remaining fat was the sympy contagion — pre-tag change 1.

## Pre-tag gacalc changes (both backwards-compatible for `plane_rotation(a, b)(θ)`)

1. **Numeric preservation** (bug-level, base.py's own convention:
   float in → float out): inside `plane_rotation`, coerce the cached
   unit bivector's coefficients to `float` when they are numeric
   (sympy numbers / ints); a symbolic plane or symbolic θ stays
   symbolic. Numeric θ then yields pure-float rotors and rotated
   vectors. Gate: a regression test asserting
   `type(plane_rotation(e_1, e_2)(1.0)(Vector2(1.0, 0.0)).coeff_e_1) is float`.
2. **LaTeX label hooks** (additive API): `plane_rotation` hardcodes
   `R_{θ}`; mvp's facades need `R_{<θ>}` / `RX_{<θ>}` / `RY` / `RZ`.
   Add optional label parameters (mirroring `rotor_rotation`'s existing
   `latex_repr`/`latex_repr_inv` hooks), defaulting to current behavior.

## mvp adoption (after gacalc 0.0.8 releases)

RELOCATED on archival (2026-07-09) to modelviewprojection
`tasks/plane-rotation-mathutils-adoption.md` — the remaining work is
mvp-side and is tracked where it executes. Summary: mathutils facades
become module-level `plane_rotation` factories (labels via the new
hooks); mvpvisualization/cayleyscene/demos need no changes (`.at(t)`
serves from the cached plane); book prose folds into
gacalc-math-migration Phase 4; kinetix needs nothing.

## Related

[[generated-dispatch-fast-paths]] — the broader dispatch-cost work,
metrics to be generated from Code the Classics in 2D.
