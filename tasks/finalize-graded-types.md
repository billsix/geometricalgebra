# Make the graded types `@typing.final`, then emit the concrete class (not `type(self)`)

**Status:** proposed — needs go-ahead. Created 2026-07-21. (Bill's batch item 9, resolved
direction 2026-07-21 — supersedes the earlier `concrete-type-vs-type-self.md`.)

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
