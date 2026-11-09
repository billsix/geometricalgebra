# Make the graded types `@typing.final`, then emit the concrete class (not `type(self)`)

**Created:** 2026-07-21 · **Completed:** 2026-07-22

The maintainer's batch item 9, resolved direction; it superseded the earlier
`concrete-type-vs-type-self.md` (no longer exists). Both phases were done; all gates green (283
tests, `ty` src/tests/tools clean, ruff clean, `check-regions` clean, deterministic).

## Decision (William Emerison Six <billsix@gmail.com>, 2026-07-21)

The graded value types (`Vector1/2/3`, `Bivector2/3`, `Trivector3`, `Rotor2/3`, `Scalar`) **should
not be subclassable**, so they became `@typing.final`. Once final, `type(self)` in their generated
methods is guaranteed to be the exact class, so it can be emitted as the **concrete class name**
(`Vector2(...)`), which was item 9's goal. The **full classes `G1`/`G2`/`G3` stay subclassable**
(the general `Gₙ` representation is the natural extension point) and keep `type(self)(...)`; the
alternative of making everything final was declined.

**Enforcement: `@typing.final` (ty-only)**, no runtime `__init_subclass__` or metaclass. Runtime
subclassing still executes (Python has no runtime `final`), but `ty`, the gate, rejects it.

## Why it was safe

- **Nothing external subclassed any generated type.** modelviewprojection subclasses no gacalc type.
  The archived "mvp backs its pygame `Vector2` work-alike by subclassing `gacalc.g2.Vector2`" use
  case, which is why `type(self)` subclass-preservation was added
  (`tasks/archive/2026/07/08/subclass-preserving-generated-ops.md`), had been superseded by "use
  gacalc's `Vector2` directly".
- **The only subclasses anywhere were gacalc's own `tests/test_subclass_preservation.py`**
  (`MyV2(Vector2)`, `MyG2(G2)`, `MyV3(Vector3)`, `MyScalar(Scalar)`), protecting that gone behavior.

## What shipped

- **Phase 1: `@typing.final` on the graded value types + `Scalar`** (not on `G1`/`G2`/`G3`), via
  `attribute("typing", "final")` in the generator's class decorators. `ty` reports
  `error[subclass-of-final-class]` on any subclass; `@typing.final` + `@dataclass(slots=True)`
  construct fine; `Vector2.__final__ is True`, `G2.__final__` is unset. This also made `type(self)`
  statically precise on the graded types (a final class has no subtypes).
- **Phase 2: the concrete class instead of `type(self)`** in the graded/`Scalar` same-type
  constructions, keyed on `result_spec.kind != "full"` in `result_block_stmts`/`unary_stmt`;
  `scaled_stmt` (graded-only) and `generate_scalar`'s `scalar_const` emit the concrete class
  directly; `return_construct` gained a `final` flag for graded `reverse`. Result: the Vector2 body
  has 0 `type(self)` (e.g. `return Vector2(...)`); G2 keeps 13. `ty` accepts the concrete `return`
  under `-> typing.Self` precisely because the class is final. The rotor **`sandwich` keeps
  `type(x)`**: that is the *operand's* type, polymorphic across `_OperandT`.
- **`tests/test_subclass_preservation.py` reworked**: graded-type subclasses removed (now illegal);
  a finality assertion added (`_FINAL_TYPES` all `__final__`; `G2` not); the full-class (`MyG2`)
  subclass-preservation + mixed-operand tests kept. The graded subclass tests in
  `test_plane_rotation.py` / `test_vector_ergonomics.py` were dropped.

**Files:** `tools/gen_specialized.py`, `tools/astbuild.py` (`return_construct` `final` param),
`tests/test_subclass_preservation.py`, `tests/test_plane_rotation.py`,
`tests/test_vector_ergonomics.py`.

## Related

- Paired with `tasks/archive/2026/07/22/overloads-and-drop-cast-on-product-primitives.md` (items
  7/8): that touched the *grade-changing* arms (drop the `Self` cast); this touched the *same-type*
  arms. Together they finished the product-method construction cleanup.
- This **reversed** the subclass-preservation decision recorded in
  `tasks/reference/design-decisions.md`.
