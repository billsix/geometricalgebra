# Make the graded types `@typing.final`, then emit the concrete class (not `type(self)`)

**Status:** complete
**Completed:** 2026-07-22
Both phases landed; all gates green (283 tests, `ty` src/tests/tools clean, ruff clean,
`check-regions` clean, deterministic). Created 2026-07-21. (Bill's batch item 9, resolved
direction — supersedes the earlier `concrete-type-vs-type-self.md`.)

## Outcome (2026-07-21)

- **Phase 1 — `@typing.final` on the graded value types + `Scalar`** (not on `G1`/`G2`/`G3`).
  Generator: added `attribute("typing", "final")` to the graded/`Scalar` class decorators.
  Verified: `ty` reports `error[subclass-of-final-class]` on any subclass; `Vector2.__final__ is
  True`, `G2.__final__` is unset. This *also* makes `type(self)` statically precise on the graded
  types (a final class has no subtypes), which is the typing half of item 9 for free.
- **Phase 2 — emit the concrete class instead of `type(self)`** in the graded/`Scalar` same-type
  constructions (item 9's literal ask). Keyed on `result_spec.kind != "full"` in
  `result_block_stmts`/`unary_stmt`; `scaled_stmt` (graded-only) and `generate_scalar`'s
  `scalar_const` emit the concrete class directly; `return_construct` gained a `final` flag for
  graded `reverse`. Result: **Vector2 body has 0 `type(self)`** (all concrete, e.g.
  `return Vector2(...)`), **G2 keeps 13** (`type(self)`, subclassable). `ty` accepts the concrete
  `return` under `-> typing.Self` precisely *because* the class is final.
- **Full classes `G1`/`G2`/`G3` unchanged** — still subclassable, still `type(self)` (the
  extension point; open question 1 answered "keep them open").
- **`tests/test_subclass_preservation.py` reworked** — graded-type subclasses removed (now
  illegal); added a finality assertion (`_FINAL_TYPES` all `__final__`; `G2` not); kept the
  full-class (`MyG2`) subclass-preservation + mixed-operand tests. Also removed the two graded
  subclass tests in `test_plane_rotation.py` / `test_vector_ergonomics.py`.

**Files:** `tools/gen_specialized.py`, `tools/astbuild.py` (return_construct `final` param),
`tests/test_subclass_preservation.py` (reworked), `tests/test_plane_rotation.py` /
`tests/test_vector_ergonomics.py` (dropped a subclass test each).

**Enforcement chosen:** `@typing.final` (ty-only), per open question 2 — no runtime
`__init_subclass__`. Runtime subclassing still *executes* (Python has no runtime `final`), but
`ty` (the gate) rejects it.

## Decision (Bill, 2026-07-21)

The graded value types (`Vector1/2/3`, `Bivector2/3`, `Trivector3`, `Rotor2/3`, `Scalar`) **should
not be subclassable** — make them `@typing.final`. Once they're final, `type(self)` in their
generated methods is *guaranteed* to be the exact class, so it can be emitted as the **concrete
class name** (`Vector2(...)`), which was item 9's goal. The **full classes `G1`/`G2`/`G3` stay
subclassable** (the general `Gₙ`-representation is the natural extension point) → they keep
`type(self)(...)`.

## Research findings (why this is safe now)

- **Nothing external subclasses any generated type.** Verified: modelviewprojection subclasses
  *no* gacalc type. The archived "mvp backs its pygame `Vector2` work-alike by subclassing
  `gacalc.g2.Vector2`" use case (which is *why* `type(self)` subclass-preservation was added —
  `tasks/archive/2026/07/08/subclass-preserving-generated-ops.md`) was **superseded** by the
  "use gacalc's `Vector2` directly" approach. So the consumer that motivated subclass preservation
  no longer exists.
- **The only subclasses anywhere are gacalc's own `tests/test_subclass_preservation.py`**
  (`MyV2(Vector2)`, `MyG2(G2)`, `MyV3(Vector3)`, `MyScalar(Scalar)`) — a test written to protect
  that now-gone behavior.

## Enforcement (verified)

- **`@typing.final`** on the class. Verified: `ty` reports `error[subclass-of-final-class]` on any
  attempt to subclass, and `@typing.final` + `@dataclass(slots=True)` construct fine at runtime
  (it's just a marker). Since **ty is gacalc's gate**, this is statically enforced — the idiomatic,
  sufficient choice.
- Runtime enforcement (Python has no runtime `final`) is *optional* and probably unnecessary: a
  `__init_subclass__` that raises, or a metaclass. My lean: **ty-only via `@typing.final`**, unless
  you want a hard runtime guard.

## Plan (sketch)

1. **Emit `@typing.final`** on each graded value type (add it to the generator's class decorator
   list alongside `@dataclass(eq=False, slots=True)`), and on `Scalar`. **Not** on `G1`/`G2`/`G3`.
2. **Emit the concrete class instead of `type(self)`** in the graded classes' same-type
   constructions — `result_block_stmts`/`unary_stmt`/`scaled_stmt`'s `construct_type_self(...)`
   becomes `construct("<Class>", ...)` when the owner is a final graded type. Full classes keep
   `type(self)`. **Scope note:** this is about `type(self)` (the method's own class, known at gen
   time). The rotor **`sandwich` keeps `type(x)`** — that's the *operand's* type, genuinely
   polymorphic across a `_OperandT`, not statically one class.
3. **Rework `tests/test_subclass_preservation.py`** — the graded-type subclasses (`MyV2`, `MyV3`,
   `MyScalar`) become illegal, so remove/replace those cases; keep the full-class case (`MyG2(G2)`)
   since `G2` stays subclassable; add a check that the graded types are final (a `ty`-checked
   snippet asserting `subclass-of-final-class`, and/or `assert Vector2.__final__` at runtime).
4. Regenerate; gates green (`ty` src/tests/tools, ruff, `check-regions`, determinism, suite).

## Open questions

1. **Should `G1`/`G2`/`G3` also be final?** Nothing subclasses them either (only the test). You
   leaned "keep the full classes subclassable" as the extension point — confirm, or make
   everything final (simpler, and lets *all* same-type arms go concrete). My lean: keep the full
   classes open per your steer.
2. Runtime enforcement too, or `@typing.final` (ty-only)? (My lean: ty-only.)

## Relationships

- Pairs with **`overloads-and-drop-cast-on-product-primitives.md`** (items 7/8): that touches the
  *grade-changing* arms (drop the `Self` cast); this touches the *same-type* arms (concrete class).
  Landing both finishes the product-method construction cleanup.
- **Reverses** the subclass-preservation decision recorded in
  `tasks/reference/design-decisions.md` → update that entry when this lands.
