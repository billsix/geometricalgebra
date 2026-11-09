# Upgrade gacalc from its uses: plane+angle rotation factory, then GA vectors directly in CTC

**Created:** 2026-07-08 · **Completed:** 2026-07-09

An umbrella task, cross-project: gacalc was the driver; mvp demos, mvpvisualization and the
Code-the-Classics (ctc) ports were the consumers. It was tracked here because the library work led.
Task 1 was committed as gacalc `a0bedea` ("make a plane of rotation", 2026-07-08); Task 2 was done on
2026-07-09 (the maintainer: "go ahead and implement task 2") in both repos, with gacalc's version
bumped to 0.0.8 and mvp's requirements pinned to `gacalc>=0.0.8`. All mvp verification ran with the
local gacalc tree bind-mounted into the mvp container, nothing persisted. Task 2 deliberately undid
the shim `Vector2` subclass staged in mvp the day before, as the maintainer expected.

## Motivation (the maintainer)

Upgrade the library — `Gn` and the generated classes — from how it is actually used. mvp's
`rotate(from_vector, to_vector)` locked the angle to the two vectors, which is exactly what
animation/interpolation fights: there was no way to say "same plane, varying angle."

## Task 1 — plane+angle rotation factory (2026-07-08)

The design (the maintainer's sketch, math verified 2026-07-08) separated the **plane** from the
**angle**: two vectors only define the plane; they are checked to be grade-1, wedged, and normalized to
the unit bivector `i = B / |B|` (`i² = −1`); `a ^ b == 0` errors, since parallel or zero vectors span no
plane (the wedge-is-zero test IS the linear-dependence test). For independent `a`, `b`,
`cos(θ/2) − sin(θ/2) * i` is a unit rotor whose sandwich rotates the in-plane component by θ and fixes
the perpendicular one, in any dimension and representation. Positive θ turns **from a toward b**, so
argument order matters (documented).

Implemented as `plane_rotation(a, b)` in `src/gacalc/transforms.py` (re-exported from `gn.py`):

- Both args are checked `is_vector()` (TypeError naming the grades); a zero wedge raises ValueError.
- It returns `rotation(θ) -> InvertibleFunction` (the maintainer's call, composable via `@` in mvp's
  Cayley-graph style): forward = the half-angle rotor sandwiched; inverse = the reversed rotor (unit
  rotor: inverse == reverse, no division); `interpolate=lambda t: rotation(θ * t)` so `.at(t)` works;
  `linearity=LINEAR`; sympy trig for symbolic θ, math trig for numeric.
- **base.py**: `__add__` accepted bare numbers as the scalar part (matching the generated classes) and
  gained `__radd__`, so the rotor expression works in `Gn` too.
- **Generator** (found by the new tests): the closed-form `Rotor2/3.sandwich` arms construct via
  `type(x)(...)` (astbuild `construct_type_of`; `result_block_stmts(via_var=...)` threaded through
  `dispatch_method`), so operand subclasses survive the grade-preserving sandwich.
- `tests/test_plane_rotation.py` (13 tests: orientation, trig sweep incl. 180°, non-unit and
  non-orthogonal plane vectors, perpendicular fixed in 𝒢₃, representation + subclass preservation,
  zero, inverse, angle-adding composition, interpolation, symbolic θ, agreement with `rotor_rotation`,
  both rejection paths), a sandwich-subclass test in `test_subclass_preservation.py`, docstring
  doctests. CLAUDE.md's never-hand-build-a-rotor convention named `plane_rotation` as the sanctioned
  plane+angle API.
- `rotate(from, to)` was kept for its from→to pedagogy; reimplementing it on the factory was deferred.
  A generated closed-form fast path was left to profiling.
- Verification 2026-07-08, in container: `make test` 268 passed, `make check-generated`
  deterministic, `format.sh` ruff + ty clean.

## Task 2 — GA vectors directly in CTC (2026-07-09)

The goal: map every pygame `Vector2`/`Vector3` feature the ctc shim exposed to an existing GA concept,
rewrite the games to use `gacalc.g2.Vector2` / `gacalc.g3.Vector3` **directly** (no subclass, no shim
type), and add to gacalc whatever had no GA home. It superseded the shim-subclass of
github.com/billsix/modelviewprojection `tasks/archive/2026/07/08/ctc-vector2-deferral.md`, keeping that
work's subclass-preserving generator ops and tests, the explicit `.dot()` call sites, and the benchmark
harness. The games stayed behaviour-faithful (same RNG and update/draw order; spelling changes only).

**gacalc side (version 0.0.8):**

- `x`/`y`/`z` read-write coordinate properties on the grade-1 generated types only (Vector1/2/3) —
  a vector's coordinates ARE its basis coefficients (new emitter `coordinate_property_defs`).
  Deliberately not on rotors, bivectors or full types.
- `__truediv__` on `MultiVectorBase`, defined **via the inverse** (the maintainer's call, 2026-07-09):
  `A / B = A * B.inverse()`, the GA quotient; a bare number's inverse is its reciprocal. An earlier
  coefficient-wise generated version was replaced.
- Not added, per the uses: `__getitem__`/`__len__` (no game indexes a vector), `cross` (zero call
  sites), zero-safe `normalize` (real pygame raises on zero too; the old shim's `(0,0)` was
  over-defensive, and every game site is guarded or unreachable). Tuple-operand arithmetic and
  constructor polymorphism were handled by rewriting call sites, not by widening gacalc.
- `tests/test_vector_ergonomics.py` (9 tests, incl. the quotient recovering the factor, subclass and
  representation preservation).

**mvp side:**

- `pgzero_gl/geometry.py`: Vector2/Vector3 deleted (Rect/ZRect remain); shim position params unpack
  (`x, y = pos`) so Actor's pos setter and both `screen.blit`s accept gacalc vectors.
- 7 games rewritten (boing, soccer, avenger, beatstreets, eggzy, kinetix, leadingedge; bunner, cavern
  and myriapod use no vectors): `length`→`magnitude`, `length_squared`→`magnitude_squared` (~40);
  `dot`→`scalar_product` (2); copy/tuple constructors → `Vector2(*x)` (~25); Actor-pos tuple mixing →
  `Vector2(*self.pos)` wraps; `self.pos += vel` → `self.pos = tuple(Vector2(*self.pos) + vel)` (ty
  can't see Actor's `__setattr__` routing); `velocity[0]`→`.x`; `normalize_ip`/`scale_to_length` →
  rebinding (aliasing checked); kinetix `rotate(i*120)` → a module-level
  `_turn = plane_rotation(Vector2.e_1, Vector2.e_2)` + `_turn(math.radians(...))(dir)`; ~35 `float(...)`
  coercions where coefficient reads feed float-typed game contracts.
- `requirements.txt`: `gacalc>=0.0.8`; the CLAUDE.md ctc section was rewritten.

**Verification (2026-07-09):** gacalc 277 in-container tests, check-generated, `format.sh` clean. mvp
(container, local gacalc installed): ty clean on pgzero_gl + vol1 + vol2 (src kept its pre-existing
79), mvp pytest 62 passed, all 10 games compiled, an integration smoke of every rewritten pattern
passed. **Benchmark:** direct gacalc 5.56 µs/actor-frame vs 2.82 (deleted subclass) vs 2.20 (old float
shim), ~6.7% of a 60 fps frame at a deliberately heavy 200-busy-actor load; the follow-up if a game
drags is fast paths in gacalc's generated dispatch
(`tasks/archive/2026/07/18/generated-dispatch-fast-paths.md`), not a shim revival.

**Not verified here:** a real game boot with a display. The maintainer's boot pass was to prioritize
kinetix (rotor turn), soccer (dot, copies, physics writes), avenger (pos-tuple mixing, velocity clamp)
and leadingedge (Vector3 + z reads).
