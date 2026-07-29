# Drop the dead same-type `case` arm from generated dispatch methods

**Status:** DONE 2026-07-29 — implemented and gate-verified (`make test` 302 passed, `check-generated`, `check-regions`, `format` all green); archived.

**Outcome:** Landed exactly as planned: `dispatch_method` skips the same-type `case` arm when `cast is cast_self` (the early-out's own flag); rationale written at the skip site and in the early-out comment. Verified in the regenerated diff: every Self-returning dispatch lost exactly its same-type arm; `sandwich` kept its arm; `@overload` stubs untouched; full classes unaffected (different emitter). Stale descriptions in `tasks/reference/code-generator-architecture.md` (header-emitted `_coerce`; "falls through to the `case T()` arm") were corrected in the same change.

## The duplication (verified in generated source)

Every Self-returning generated dispatch method (`_geometric_product`,
`__mul__`, `__add__`, `__sub__`, inner/outer/contractions — on the full and
graded classes) emits the same-type closed form **twice**:

```python
def _geometric_product(self, rhs) -> MultiVectorBase:
    if type(rhs) is Vector2:          # exact-type early-out (measured fast path)
        return Rotor2(...closed form...)
    match rhs:
        ...
        case Vector2():               # IDENTICAL closed form -- now dead code
            return Rotor2(...closed form...)
        ...
```

Emitted by `dispatch_method` in `tools/gen_specialized.py`: the early-out is
the deliberate `#1: exact-type early-out` (its comment records it was
**measured** across the CtC + mvp workloads — the dominant operand is the same
concrete type as `self`, and `type(x) is T` reaches the closed form without
walking the match ladder's isinstance chain). The duplicate `case T()` arm
existed for **subclasses** (isinstance-true, `type is`-false), from the
subclass-preserving era (`tasks/archive/2026/07/08/subclass-preserving-generated-ops.md`).

## Why the arm is dead now

All generated value types became `@typing.final` on 2026-07-23 (see
`tasks/reference/design-decisions.md` › frozen/slots entry), so no legal
subclass exists: every exact-type operand takes the early-out, and the
same-type `case` arm is reachable only by a caller who ignores `@final`
(unenforced at runtime).

## The fix

In `dispatch_method`'s loop over operand types, **skip emitting the `case`
arm for `rhs_spec == self_spec` whenever the early-out was emitted** — i.e.
gate on the same `cast is cast_self` flag that already gates the early-out.

- The measured fast path is untouched (do NOT instead drop the early-out and
  hoist the case arm first — that trades a measured decision for an
  unmeasured one).
- `sandwich` keeps its same-type arm: it has no early-out (`cast_operand`;
  same-type operand rare there), so the arm does real work.
- Safety net for a `@final`-violating runtime subclass: it falls to
  `case _:` → `_coerce` to `G_n` — numerically **correct**, just widened
  instead of narrowly typed. Say exactly that in the emitted early-out
  comment, so if finality is ever relaxed the arm's removal is discoverable.
- Payoff: one large duplicated closed-form body removed per method per class
  — a real shrink of `g1/g2/g3.py` and less for a student to read twice.

## Verification

1. `make generate`; diff the generated files — each Self-returning dispatch
   loses exactly its same-type arm; `sandwich` unchanged.
2. `make test` (the conformance suite exercises same-type products on every
   representation, so the early-out path is covered), `make check-generated`,
   `make check-regions` (marker set changes only by the removed arm's
   content, not by names), `make format`.

## Related

`tasks/archive/2026/07/29/extract-generated-coerce.md` — the other generator-output cleanup (also DONE)
(shared `_coerce`); independent changes, but naturally reviewed together.
