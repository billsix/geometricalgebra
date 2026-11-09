# Investigate making the generated value types `frozen` (immutable)

**Created:** 2026-07-23 (requested by the maintainer) · **Completed:** 2026-07-23

## Question

The generated value types were `@dataclass(slots=True)` but deliberately not `frozen`
(`dataclass_decorator(eq=False, slots=True)` in `tools/gen_specialized.py`; CLAUDE.md carried a
"Generated value types are MUTABLE" note). In-repo, the `x`/`y`/`z` coordinate property setters let
`vec.x = -vec.x`; downstream, mvp's Code-the-Classics ports mutated vectors in place and the book
taught the idiom, with the aliasing hazards CLAUDE.md documented. This task revisited the decision.
The maintainer's preference: frozen if feasible, aware that some callers (notably mvp) would have
to change.

## Findings (spike: `frozen=True` on all three `dataclass_decorator` calls, regenerated, ran)

1. **No inheritance blocker.** `MultiVectorBase` is a plain `abc.ABC` (`__slots__ = ()`), not a
   dataclass, and every generated value type (`Scalar_n`/`Vector_n`/`Bivector_n`/`Trivector3`/
   `Rotor_n` and the full `G_n`) inherits directly from it, so the "can't inherit a frozen dataclass
   from a non-frozen one" rule never fires.
2. **The gacalc side was nearly free.** The full suite passed except one test,
   `tests/test_vector_ergonomics.py::test_coordinate_write` (`v.x = 9.0`). The only in-repo blocker
   was the `x`/`y`/`z` property setters (`coordinate_property_defs`). The generated classes have no
   `__post_init__`.
3. **Hashability is NOT gained.** The generated classes have a custom `__eq__` (`eq=False` +
   hand-written), which already forces `__hash__ = None` independent of `frozen`. A value-hash over
   `sympy.Expr`/`float` coefficients would be fragile, so the benefit is immutability +
   footgun-removal (shared basis constants like `Vector2.e_1`, mutable default args), not hashing.
4. **`Gn` (`gn.py`) was out of scope**: hand-written, and its `__post_init__` writes
   `self.coefficient_of_blade` (the eager simplify), so frozen would need `object.__setattr__`.
5. **The real cost was downstream: ~150 in-place `.x/.y/.z` mutation sites in mvp** (Python only;
   the 166-hit raw count was mostly GLSL swizzles), concentrated in the Code-the-Classics game ports
   (`self.dir.x = -self.dir.x`, `self.dir.y += …`, tuple-unpack `self.vpos.x, self.vel.x =
   ball_physics(...)`) plus demos 04/19/20/21 and `util/cameracontrols.py`. These are
   behaviour-faithful ports; frozen forces each to rebind (`self.dir = Vector2(-self.dir.x,
   self.dir.y)`), the tuple-unpack sites being the trickiest.

The go/no-go put to the maintainer: is immutability + footgun-removal worth ~150 mvp rebinds? The
maintainer said go.

## Implemented (2026-07-23)

- **Generator (`tools/gen_specialized.py`)**: `frozen=True` on all three
  `dataclass_decorator(eq=False, slots=True)` calls (scalar / graded / full `G_n`);
  `coordinate_property_defs` emits **getter-only** `x`/`y`/`z` (setters dropped).
- **Tests**: `tests/test_vector_ergonomics.py` `test_coordinate_write` became
  `test_frozen_immutable_rebind_not_mutate` (a field write raises `FrozenInstanceError`; a property
  write is blocked; the rebind idiom works). All **297 tests pass**.
- **`CLAUDE.md`**: the "MUTABLE … do not add frozen" note was rewritten to "FROZEN (immutable) …
  rebind, don't mutate", incl. the slots-property caveat below.
- **`Gn` left mutable.**

### Known wart (kept `slots`, documented): frozen+slots property-write error

A **field** write (`v.coeff_e_1 = …`) raises a clean `FrozenInstanceError`. A **property** write
(`v.x = …`) raises a confusing `TypeError: super(type, obj)…`, a Python 3.14 frozen+slots+property
internals interaction (frozen *without* slots gives a clean `FrozenInstanceError` but loses the
`__dict__`-free memory benefit). It is still blocked, just with an ugly message. **`slots` was
kept** for the memory benefit; dropping `slots` from the three decorator calls is the one-line
alternative if clean errors are preferred (instances would gain a `__dict__`).

## Downstream and release

This was breaking for consumers that mutate in place. The mvp conversion was its own task,
github.com/billsix/modelviewprojection `tasks/archive/2026/07/23/frozen-vectors-rebind-migration.md`,
gated on a gacalc release. The release was a minor (breaking) bump, batched by the maintainer with
the other gacalc typing/generator tasks from the same request; the `CHANGELOG.md` records frozen
types under `[0.0.14]`.

## Related

- `tasks/archive/2026/06/27/graded-subtypes-slots-true.md` (the `slots=True` adoption).
- `tasks/reference/design-decisions.md` (the frozen/slots entry).
- mvp's CLAUDE.md note on gacalc vectors and in-place mutation (github.com/billsix/modelviewprojection).
