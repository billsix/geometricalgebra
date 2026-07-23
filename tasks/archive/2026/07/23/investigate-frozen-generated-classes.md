# Investigate making the generated value types `frozen` (immutable)

**Status:** **implemented 2026-07-23** (Bill said go) — gacalc value types are now
`@dataclass(frozen=True, slots=True)`. **Release + mvp migration are gated** (breaking; batched with
the other gacalc typing/generator tasks from the same request — Bill won't release until all land).
Created 2026-07-23 (Bill).

## Implemented (2026-07-23)

- **Generator (`tools/gen_specialized.py`)**: added `frozen=True` to all three
  `dataclass_decorator(eq=False, slots=True)` calls (scalar / graded / full `G_n`); made
  `coordinate_property_defs` emit **getter-only** `x`/`y`/`z` (dropped the setters — a setter's
  `self.coeff_e_1 = value` can't run on a frozen instance).
- **Tests**: `tests/test_vector_ergonomics.py` — `test_coordinate_write` → `test_frozen_immutable_
  rebind_not_mutate` (field write raises `FrozenInstanceError`; property write is blocked; the rebind
  idiom works). All **297 tests pass**.
- **`CLAUDE.md`**: the "MUTABLE … do not add frozen" note rewritten to "FROZEN (immutable) … rebind,
  don't mutate", incl. the slots-property caveat below.
- **`Gn` (gn.py) left mutable** — hand-written reference, `__post_init__` writes fields; out of scope.

### Known wart (kept `slots`, documented): frozen+slots property-write error

A **field** write (`v.coeff_e_1 = …`) raises a clean `FrozenInstanceError`. A **property** write
(`v.x = …`) raises a confusing `TypeError: super(type, obj)…` — a Python **3.14 frozen+slots+property**
internals interaction (frozen *without* slots gives clean `FrozenInstanceError`, but loses the
`__dict__`-free memory benefit). It's still *blocked*, just an ugly message on a now-forbidden op.
**Kept `slots`** (the memory benefit CLAUDE.md values); if Bill would rather have clean errors, drop
`slots` from the three decorator calls — a one-line change (tradeoff: instances gain a `__dict__`).

### Downstream + release

- Breaking for consumers that mutate in place. **mvp** has ~150 in-place `.x/.y/.z` sites (mostly the
  Code-the-Classics game ports) → tracked in mvp `tasks/frozen-vectors-rebind-migration.md`, gated on
  a gacalc frozen **release** (version bump + PyPI push).
- On release: bump `version` in `pyproject.toml` (a **minor** bump — breaking), `make release`.

## Findings (below, for reference)

Bill's preference: make them frozen if feasible, aware that some callers
(notably mvp) mutate in place and would have to change.

## Findings (spike: flipped `frozen=True` on all three `dataclass_decorator` calls, regenerated, ran)

1. **Structurally fine — no inheritance blocker.** `MultiVectorBase` is a plain `abc.ABC`
   (`base.py:74`, `__slots__ = ()`), **not** a dataclass, and every generated value type
   (`Scalar_n`/`Vector_n`/`Bivector_n`/`Trivector3`/`Rotor_n` **and** the full `G_n`) inherits
   **directly** from it. So the "can't inherit a frozen dataclass from a non-frozen one" rule never
   fires. `dataclass_decorator(**flags)` already accepts `frozen=True`.
2. **gacalc side is nearly free.** With `frozen=True`: imports fine, constructs fine, and the **full
   suite passes except ONE test** — `tests/test_vector_ergonomics.py::test_coordinate_write`
   (`v.x = 9.0`). So the **only** in-repo blocker is the `x`/`y`/`z` property **setters**
   (`coordinate_property_defs`) — a setter doing `self.coeff_e_1 = value` can't run on a frozen
   instance. Fix: emit **getters-only** (drop the `@x.setter`/`@y.setter`/`@z.setter`) and
   remove/rewrite that one test. No `__post_init__` issue — the generated classes have none.
   (Aside: the frozen+slots+property-setter combo raises a confusing
   `TypeError: super(type, obj)...` rather than `FrozenInstanceError` — another reason the setters
   must simply go, not be "fixed".)
3. **Hashability is NOT gained** (this corrects "What it buys" below). The generated classes have a
   **custom `__eq__`** (`eq=False` + hand-written), which already forces `__hash__ = None` →
   `unhashable` — independent of `frozen`. Frozen doesn't change it. Getting hashing back needs a
   custom `__hash__`, but coefficients can be `sympy.Expr`/`float`, so a value-hash is fragile/blocked.
   **So the benefit of frozen here is immutability + footgun-removal, not hashability.**
4. **`Gn` (the reference, `gn.py`) is out of scope.** It's hand-written and its `__post_init__`
   **writes** `self.coefficient_of_blade` (the eager simplify), so frozen there would need
   `object.__setattr__`. It isn't one of the *generated* value types; leave it mutable (or a separate
   decision).
5. **The real cost is downstream (mvp): ~150 in-place `.x/.y/.z` mutation sites** (Python only; the
   166-hit raw count was mostly GLSL `.vs`/`.fs` swizzles). Concentrated in the **Code-the-Classics
   game ports** (`self.dir.x = -self.dir.x`, `self.dir.y += …`, tuple-unpack `self.vpos.x, self.vel.x
   = ball_physics(...)`) plus a few demos (demo04/19/20/21, `util/cameracontrols.py`). These are
   **behaviour-faithful ports** where in-place mutation *is* the ported gameplay. Frozen forces each
   to **rebind** (`self.dir = Vector2(-self.dir.x, self.dir.y)`); the tuple-unpack sites are the
   trickiest (can't unpack straight into rebinds).

**Bottom line:** the gacalc change is tiny (drop 3 setters, delete 1 test, add `frozen=True`, bump a
version, update the CLAUDE.md "MUTABLE" note). The expense is the **mvp conversion** — ~150 sites,
mostly in the game ports — which would be its **own** task, coordinated with a gacalc release. Whether
it's worth it is a judgment call (immutability + removing the aliasing footguns CLAUDE.md documents,
vs reworking the ports). **Go/no-go: is immutability + footgun-removal worth ~150 mvp rebinds?** If
go: implement the gacalc change here (small), and spin a separate mvp task for the conversion,
coordinated with a gacalc release.

## Goal

The generated value types are `@dataclass(slots=True)` but **deliberately not `frozen`**
(`tools/gen_specialized.py` `dataclass_decorator(eq=False, slots=True)` — scalar `:1603`, graded
`:1964`; the full `G_n` similarly). CLAUDE.md has a whole note ("Generated value types are MUTABLE —
`slots=True`, but deliberately not `frozen`") explaining the current choice. **This task revisits that
decision**: determine what it would take to make them `frozen=True`, and whether it's worth it.

## Why they're mutable today (the thing to overturn)

- **In-repo:** the `x`/`y`/`z` coordinate **property setters** (`coordinate_property_defs`) let
  `vec.x = -vec.x`. Frozen forbids attribute assignment, so these setters (and any in-repo mutation)
  break.
- **Downstream (mvp):** its Code-the-Classics ports mutate vectors in place throughout
  (`self.dir.x = -self.dir.x`, `self.vpos.y = …`) and the book teaches the idiom. CLAUDE.md documents
  the aliasing hazard this creates (shared/default-arg vectors). Frozen would force those to **rebind**
  (`self.dir = Vector2(-self.dir.x, self.dir.y)`) instead of mutate.

## Investigate

1. **What breaks in gacalc if `frozen=True`:** the `x`/`y`/`z` setters/deleters (drop them, or keep
   only getters), any `__post_init__` field writes (e.g. `Gn` eager-simplify writes fields — check),
   `from_blade_dict`/constructors (fine — they set via `__init__`). Note `frozen` + `slots` is
   supported.
2. **What it buys:** immutability removes the aliasing footguns (shared basis constants
   `Vector2.e_1`, mutable default args); frozen dataclasses are **hashable** (usable as dict
   keys / set members / cached), which the current mutable types are not. Weigh these against the
   churn.
3. **`eq`/`hash`:** the generator currently sets `eq=False` (custom `__eq__` via lazy simplify). Frozen
   normally implies `eq=True`+`__hash__`; reconcile with the custom `__eq__` (sympy coefficients aren't
   trivially hashable — may block hashing unless coefficients are numeric).
4. **Downstream blast radius:** enumerate mvp's in-place mutation sites (the ports, `mathutils`,
   `geometry`) and estimate the rebind changes. This is the "aware some callers would change" part —
   size it.
5. **Decision + rollout:** if adopted, it's a breaking release (coordinate setters gone / in-place
   mutation gone); update the CLAUDE.md "MUTABLE" note, bump a minor version, and coordinate the mvp
   changes.

## Verify

Regenerate; `ty`/ruff/suite/regions/determinism green; a frozen-instance mutation raises
`FrozenInstanceError` (add a guard test); confirm hashing works (or is documented as blocked by
symbolic coefficients).

## Relationships

- CLAUDE.md "Generated value types are MUTABLE …" note (the decision this reconsiders).
- `tasks/archive/2026/06/27/graded-subtypes-slots-true.md` (the `slots=True` adoption).
- mvp's CLAUDE.md "gacalc vectors are MUTABLE, and the games mutate them in place" (the downstream
  idiom) — `github.com/billsix/modelviewprojection`.
