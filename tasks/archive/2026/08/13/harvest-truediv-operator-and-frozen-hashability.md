# Document `A / B` (`__truediv__`) and frozen-types-aren't-hashable

**Created:** 2026-08-13 · **Completed:** 2026-08-13

Group A of the 2026-08-13 archive gap-analysis sweep (high-confidence, near-trivial doc gaps).
Siblings: `tasks/archive/2026/08/13/harvest-api-design-rationale-from-archive.md`,
`tasks/archive/2026/08/13/harvest-build-and-dev-workflow-gotchas.md`,
`tasks/archive/2026/08/13/harvest-minor-doc-and-notebook-nits.md`,
`tasks/archive/2026/08/13/blade-dict-interchange-reference.md`.

## What was done

Two durable facts that lived in code but not in the always-read docs were added, each verified
against source; nothing else changed.

- **`A / B` (`__truediv__`) was added to CLAUDE.md's Operators list**, which had omitted it. It is
  implemented on `MultiVectorBase` (`base.py`): `A / B = A * B.inverse()`; a bare number's inverse
  is its reciprocal, so `v / s` divides every coefficient. From
  `tasks/archive/2026/07/09/upgrade-rotation-and-ctc-vector-mapping.md`.
- **Frozen generated value types are NOT hashable**, added to CLAUDE.md's frozen note
  (Architecture) and the frozen/slots entry in `tasks/reference/design-decisions.md`. It corrects
  the natural "frozen dataclass ⇒ hashable ⇒ usable as a dict key / set member" assumption: the
  custom `__eq__` (`eq=False` + hand-written) forces `__hash__ = None`, and a value-hash is
  impossible regardless because coefficients may be `sympy.Expr`/`float`. From
  `tasks/archive/2026/07/23/investigate-frozen-generated-classes.md`.
