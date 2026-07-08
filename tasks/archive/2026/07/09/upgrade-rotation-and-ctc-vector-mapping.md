# Upgrade gacalc from its uses: plane+angle rotation factory, then GA vectors directly in CTC

**Status:** DONE — Task 1 committed by Bill 2026-07-09 (gacalc
237ede7 "phase 1"); Task 2 DONE 2026-07-09 (Bill: "go ahead and
implement task 2"), staged uncommitted in BOTH repos. gacalc's version
is bumped to 0.0.8 in the staging — **Bill: commit both repos, then
`make release` gacalc 0.0.8 before running mvp's normal `make image`**
(mvp's requirements now pin `gacalc>=0.0.8`; all verification ran with
the local gacalc tree bind-mounted into the mvp container, nothing
persisted).
**Created:** 2026-07-08 (Bill's direction, confirmed in conversation)
**Scope:** umbrella task, cross-project (gacalc is the driver; mvp demos,
mvpvisualization, and the Code-the-Classics ports are the consumers), but
tracked HERE because the library work leads. **Task 2 will undo some of
the just-staged mvp ctc work** (the shim Vector2 subclass) — expected,
per Bill.

## Motivation (Bill)

Upgrade the geometricalgebra library — `Gn` and the generated classes —
based off how it is actually used. mvp demos and mvpvisualization use it;
ctc uses it. mvp's `rotate` "may not be defined as nicely as I'd like":
the existing `rotate(from_vector, to_vector)` locks the angle to the two
vectors, which is exactly what animation/interpolation in mvp fights —
there's no way to say "same plane, varying angle."

## Task 1 — plane+angle rotation factory — DONE 2026-07-08

Implemented as `plane_rotation(a, b)` in `src/gacalc/transforms.py`
(re-exported from `gn.py`), next to `rotor_rotation`:

- verifies both args `is_vector()` (TypeError with the offending grades);
  wedges them; `a ^ b == 0` → ValueError ("parallel ... span no plane");
  normalizes to the unit bivector `i`.
- returns `rotation(theta) -> InvertibleFunction` (Bill's call): forward
  = half-angle rotor `i * (-sin(theta/2)) + cos(theta/2)` sandwiched;
  inverse = the reversed rotor (unit rotor: inverse == reverse);
  `interpolate=lambda t: rotation(theta * t)` so `.at(t)` works;
  `linearity=LINEAR`; sympy trig for symbolic theta, math trig for
  numeric (the base.py numeric-preservation convention).
- **base.py**: `__add__` now accepts bare numbers as the scalar part
  (matching the generated classes) + a new `__radd__` — so the rotor
  expression works uniformly in `Gn` too.
- **generator** (found by the new tests): the closed-form `Rotor2/3
  .sandwich` arms now construct via `type(x)(...)` (astbuild
  `construct_type_of`; `result_block_stmts(via_var=...)` threaded through
  `dispatch_method` for the `cast_operand` case) — the sandwich is
  grade-preserving, and base.sandwich documents "returns a value of x's
  own type", so operand SUBCLASSES now survive it (the shim-Vector2 case).
- tests/test_plane_rotation.py (13 tests: orientation a→b, trig-value
  sweep incl. 180°, non-unit/non-orthogonal plane vectors, perpendicular
  fixed in G3, representation + subclass preservation, zero, inverse,
  composition adds angles, interpolation, symbolic theta, agreement with
  rotor_rotation, both rejection paths) + a sandwich-subclass test in
  test_subclass_preservation.py; doctest examples in the docstring.
- CLAUDE.md updated (module layout, Rotations & rotors, the never-hand-
  build convention now names `plane_rotation` as the sanctioned
  plane+angle API).
- Gates 2026-07-08, in container: `make test` 268 passed,
  `make check-generated` deterministic, format.sh ruff+ty all clean.

Original design notes (kept for the record):

Separate the two concerns the current API conflates: the **plane** of
rotation and the **angle**.

Design (Bill's sketch, math verified 2026-07-08):

1. Take two vectors `a`, `b` whose only job is to **define the plane**.
   **Verify both are grade-1 vectors** (reject bivectors / full
   multivectors).
2. **Wedge** them — `B = a ^ b` — and **normalize** to the unit bivector
   `i = B / |B|`, the "imaginary unit" of that plane (`i**2 == -1`).
   **`a ^ b == 0` must error**: parallel (or zero) vectors define no
   plane. (Nice teaching moment: the wedge-is-zero test IS the
   linear-dependence test.)
3. Return a function of theta. **Bill's call: `f(theta)` returns an
   `InvertibleFunction`** (the `gacalc.transforms` type, composable via
   `@` in mvp's Cayley-graph style), whose forward action builds the
   half-angle rotor `R = cos(theta/2) - sin(theta/2) * i` and applies
   the sandwich `R v R~` (unit rotor: inverse == reverse, no division),
   and whose inverse is the same with `-theta`. LaTeX reprs like the
   other transform factories.

Why this works (recorded so the impl doesn't re-derive it): for linearly
independent `a`, `b` the wedge is a simple bivector; its normalization
squares to -1; `cos(theta/2) - sin(theta/2)*i` is a unit rotor; the
sandwich rotates the in-plane component of any vector by theta and fixes
the perpendicular component — any dimension, any representation.
Positive theta turns **from a toward b** (the wedge's orientation), so
argument order is meaningful — document that.

Interpolation falls out: `f` is built once per plane; `f(t * theta)`
for `t in [0, 1]` sweeps the rotation continuously.

Design/impl notes:

- **Placement:** representation-agnostic core on `MultiVectorBase` (or
  `transforms.py`, alongside `translate`/`scale_non_uniform` — it returns
  their type), deriving everything from the operands like the rest of the
  transform layer, so `Gn`/`G2`/`G3`/graded types all work. Consider a
  generated closed-form fast path on `Rotor2`/`Rotor3` (the existing
  `sandwich` machinery) if profiling warrants; not required for v1.
- **Relationship to `rotate(from, to)`:** keep it (its from→to reading is
  the pedagogy), but consider reimplementing it on the new factory —
  plane from `a ^ b`, theta from the angle between them — so there is one
  rotation engine. Task decision at impl time.
- The half-angle trig construction living INSIDE the library finally
  makes the "never hand-build a rotor" convention fully honest: user code
  gets a sanctioned "rotate by theta in this plane" API. CLAUDE.md's
  convention section should point at the factory when this lands.
- Naming: went with `plane_rotation(a, b)`; `rotate(from, to)` kept
  as-is (reimplementing it on the factory deferred — decide with Task 2).
- Consumers to convert once landed (NOT yet done — needs a gacalc
  release first):
  - mvp `mathutils.rotate(theta)` (2D) and `rotate_x/y/z(theta)` (3D)
    facades → `plane_rotation(e_1, e_2)(theta)` etc.
  - ctc `pgzero_gl.geometry._rotation_rotor` (the cached rotor-from-
    e_1-to-cos/sin-target workaround) → the factory directly.
  - mvpvisualization demos that animate rotations.

## Task 2 (subtask) — DONE 2026-07-09: GA vectors directly in CTC

What was done (verify-in-container throughout; local gacalc tree
temporarily pip-installed into the mvp container for gates):

**gacalc side (staged here, version 0.0.8):**
- `x`/`y`/`z` read-write coordinate properties on the grade-1 generated
  types only (Vector1/2/3) — a vector's coordinates ARE its basis
  coefficients; new generator emitter `coordinate_property_defs`.
  Deliberately NOT on rotors/bivectors/full types.
- `__truediv__` on `MultiVectorBase` defined **via the inverse** (Bill's
  call, 2026-07-09): `A / B = A * B.inverse()` — the GA quotient; a bare
  number's inverse is its reciprocal. No generator code; one base method.
  (An earlier coefficient-wise generated version was replaced.)
- NOT added, per uses: `__getitem__`/`__len__` (no game indexes a
  vector), `cross` (zero call sites — leadingedge never crosses),
  zero-safe normalize (real pygame RAISES on zero too — the old shim's
  `(0,0)` was over-defensive; gacalc's ZeroDivisionError is
  contract-correct, and every game site is guarded or unreachable).
- tests/test_vector_ergonomics.py (9 tests incl. quotient recovers the
  factor, subclass + representation preservation).

**mvp side (staged there):**
- `pgzero_gl/geometry.py`: Vector2/Vector3 DELETED (Rect/ZRect remain);
  shim position params unpack (`x, y = pos`) instead of indexing —
  Actor's pos setter and both `screen.blit`s accept gacalc vectors.
- 7 games rewritten (boing, soccer, avenger, beatstreets, eggzy,
  kinetix, leadingedge; bunner/cavern/myriapod use no vectors):
  `from gacalc.g2 import Vector2` (+ g3 Vector3 in leadingedge);
  `length`→`magnitude`, `length_squared`→`magnitude_squared` (~40);
  `dot`→`scalar_product` (2); copy/tuple ctors → `Vector2(*x)` (~25);
  Actor-pos-tuple mixing → `Vector2(*self.pos)` wraps (avenger ~10);
  `self.pos += vel` → `self.pos = tuple(Vector2(*self.pos) + vel)`
  (ty can't see Actor's __setattr__ routing; tuple() keeps its view
  consistent with what reads return); `velocity[0]`→`.x`;
  `normalize_ip`/`scale_to_length` → rebinding (aliasing checked: both
  avenger sites are locals/sole-owner attrs); kinetix `rotate(i*120)` →
  module-level `_turn = plane_rotation(Vector2.e_1, Vector2.e_2)` +
  `_turn(math.radians(...))(dir)`; ~35 `float(...)` coercions where
  `Coef` reads feed the games' float-typed contracts (documents the
  numeric assumption at the algebra boundary).
- requirements.txt: `gacalc>=0.0.8`; CLAUDE.md ctc section rewritten.

**Gates (2026-07-09):** gacalc: 277 in-container tests,
check-generated, format.sh ruff+ty clean. mvp (container, local gacalc
installed): format.sh — ty clean on pgzero_gl+vol1+vol2 (src keeps its
pre-existing 79), mvp pytest 62 passed, all 10 games compile,
integration smoke of every rewritten pattern passes.
**Benchmark:** direct gacalc 5.56 us/actor-frame vs 2.82 (deleted
subclass) vs 2.20 (old float shim) — ~6.7% of a 60 fps frame at a
deliberately heavy 200-busy-actors synthetic load; real games do far
less per frame. If a game ever drags, the follow-up is fast paths in
gacalc's generated dispatch, not a shim revival.
**NOT verified: real game boot with a display** — Bill's boot pass
should prioritize kinetix (rotor turn), soccer (dot/copies/physics
writes), avenger (pos-tuple mixing, velocity clamp), leadingedge
(Vector3 + z reads).

Original scope notes (kept for the record):

After Task 1: audit the pygame API surface the ctc shim `Vector2`/
`Vector3` expose, map each feature to a concept **already existing in
GA**, and rewrite **all 10 games** to use `gacalc.g2.Vector2` /
`gacalc.g3.Vector3` **directly — no subclass, no shim vector type**.
Where a feature has no GA home, **add it to gacalc** (that's the
"upgrade from uses" point).

Feature inventory (from the shim as staged 2026-07-08) and candidate
mappings — verify each against gacalc's actual behaviour at impl time:

| pygame feature | GA mapping |
|---|---|
| `length` / `magnitude` | `magnitude()` |
| `length_squared` | `magnitude_squared()` |
| `dot(o) -> float` | inner product + scalar read-back (`.coefficient(...)` / `scalar_part()`) — needs a decided float-returning spelling |
| `rotate(degrees)` | Task 1 factory (`plane_rotation(e_1, e_2)`), degrees→radians at call sites |
| `cross(o)` (V3) | dual of the wedge in G3 (`(a ^ b).dual()`, check sign) |
| `distance_to(o)` | `(a - b).magnitude()` |
| `normalize()` | `normalize()` — but pygame's zero vector → `(0,0)`; gacalc divides by zero. Decide: caller-side guards in games, or a gacalc behaviour/variant |
| `normalize_ip` / `scale_to_length` (mutating) | gacalc values are mutable dataclasses; rewrite call sites to rebind (`v = v.normalize()`), or add in-place helpers |
| `.x/.y/.z` read+write | MISSING: coordinate accessors (games write `vpos.x` per frame). Add `x`/`y`(/`z`) properties to generated vector types? or rewrite sites to `coeff_e_1` (ugly for games) |
| tuple interop (`v + (1,2)`, `v == (x,y)`, ctor from pair) | MISSING in gacalc; either add tuple acceptance to generated vector ops, or rewrite game call sites to construct vectors (grep says tuple-operand arithmetic is common) |
| `v / s` | MISSING: `__truediv__` — add to generated classes (`* (1/s)` spelling in games is worse) |
| `v[i]` / `len(v)` | MISSING: `__getitem__`/`__len__` — `__iter__` exists (blade-order coefficients); adding indexing is small |
| ctor polymorphism (`V(x,y)`, `V(pair)`, `V(other)`) | gacalc ctor is `coeff_e_1=`/`coeff_e_2=` keywords only — decide: `from_xy`-style factory, ctor widening, or rewrite sites |

Execution notes:

- **This supersedes the staged shim-subclass** (mvp
  `tasks/archive/2026/07/08/ctc-vector2-deferral.md`): geometry.Vector2/
  Vector3 disappear as types; games import gacalc's. Keep from that work:
  the generator's `type(self)` subclass-preserving ops + its tests (good
  library behaviour regardless), the explicit `.dot()` call sites, the
  benchmark harness (rerun it against direct gacalc vectors — no property
  indirection, may well be FASTER than the subclass).
- Behaviour-faithful constraint on the games still holds: same RNG order,
  same update/draw order. API spelling changes only.
- Gates: gacalc suite + conformance + new unit tests for every added
  feature; mvp format.sh (ruff+ty over shim+vol1+vol2); mvp pytest; the
  10-game compile check; Bill boots a few games with a display.
- Feature additions land in gacalc via `tools/gen_specialized.py` (never
  hand-edit generated files) + `base.py`/`transforms.py`; version bump +
  release so mvp's pin picks them up.

## Order

Task 1 first (self-contained, immediately useful to mvp), then the
Task 2 mapping/audit as its own implementation pass — likely several
sessions; slice per game once the gacalc features exist.
