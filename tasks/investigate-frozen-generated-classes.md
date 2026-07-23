# Investigate making the generated value types `frozen` (immutable)

**Status:** proposed — needs go-ahead. Created 2026-07-23 (Bill). Bill's preference: **make them
frozen if feasible**, aware that some callers (notably mvp) mutate in place and would have to change.

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
