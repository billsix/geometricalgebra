# Drop the dead same-type `case` arm from generated dispatch methods

**Completed:** 2026-07-29

## Outcome

`dispatch_method` skips the same-type `case` arm when `cast is cast_self` (the early-out's own
flag); the rationale is written at the skip site and in the early-out comment. Gate-verified:
`make test` 302 passed; `check-generated`, `check-regions`, `format` all green. The regenerated diff
showed every Self-returning dispatch lost exactly its same-type arm; `sandwich` kept its arm;
`@overload` stubs were untouched; full classes were unaffected (different emitter). Stale
descriptions in `tasks/reference/code-generator-architecture.md` (header-emitted `_coerce`; "falls
through to the `case T()` arm") were corrected in the same change.

## The duplication (verified in generated source)

Every Self-returning generated dispatch method (`_geometric_product`, `__mul__`, `__add__`,
`__sub__`, inner/outer/contractions) emitted the same-type closed form **twice**: once in the
`if type(rhs) is Vector2:` exact-type early-out, and again in an identical `case Vector2():` arm of
the following `match`. The early-out is the deliberate `#1: exact-type early-out` in
`dispatch_method` (`tools/gen_specialized.py`); its comment records it was **measured** across the
CtC + mvp workloads: the dominant operand is the same concrete type as `self`, and `type(x) is T`
reaches the closed form without walking the match ladder's isinstance chain. The duplicate arm had
existed for **subclasses** (isinstance-true, `type is`-false), from the subclass-preserving era
(`tasks/archive/2026/07/08/subclass-preserving-generated-ops.md`).

## Why the arm was dead

All generated value types became `@typing.final` on 2026-07-23
(`tasks/reference/design-decisions.md` › frozen/slots entry), so no legal subclass exists: every
exact-type operand takes the early-out, and the same-type arm was reachable only by a caller
ignoring `@final` (unenforced at runtime).

## Decisions

- **The case arm is skipped only where the early-out is emitted**, gated on the same
  `cast is cast_self` flag. The alternative of dropping the early-out and hoisting the case arm
  first was rejected: it trades a measured decision for an unmeasured one.
- `sandwich` keeps its same-type arm: it has no early-out (`cast_operand`; same-type operand rare
  there), so the arm does real work.
- Safety net for a `@final`-violating runtime subclass: it falls to `case _:` → `_coerce` to `G_n`,
  numerically correct, just widened instead of narrowly typed. The emitted early-out comment says
  exactly that, so if finality is ever relaxed the arm's removal is discoverable.
- Payoff: one large duplicated closed-form body removed per method per class, a real shrink of
  `g1/g2/g3.py` and less for a student to read twice.

## Related

`tasks/archive/2026/07/29/extract-generated-coerce.md`, the other generator-output cleanup (shared
`_coerce`); independent changes, reviewed together.
