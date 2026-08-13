# Document `A / B` (`__truediv__`) and frozen-types-aren't-hashable

**Status:** proposed — needs go-ahead
**Priority:** 4
**Difficulty:** 2
**Created:** 2026-08-13
**Origin:** the 2026-08-13 archive gap-analysis sweep (Group A — high-confidence,
near-trivial doc gaps). Siblings: `harvest-api-design-rationale-from-archive.md`,
`harvest-build-and-dev-workflow-gotchas.md`, `harvest-minor-doc-and-notebook-nits.md`,
`blade-dict-interchange-reference.md`.

Two durable facts that live in code but not in the always-read docs. Both are small,
safe edits; verify against current source before writing.

## Items

- [ ] **`A / B` (`__truediv__`) is missing from CLAUDE.md's Operators list.** It is
      implemented on `MultiVectorBase` (`base.py`) with a docstring — `A / B = A *
      B.inverse()`; a bare number's inverse is its reciprocal, so `v / s` divides every
      coefficient — but the CLAUDE.md "Operators" bullet list omits `/`. Add it.
      *Source:* `tasks/archive/2026/07/09/upgrade-rotation-and-ctc-vector-mapping.md`.
      *Home:* CLAUDE.md › Operators.
- [ ] **Frozen generated value types are NOT hashable** — corrects the natural "frozen
      dataclass ⇒ hashable ⇒ usable as a dict key / set member" assumption. The custom
      `__eq__` (`eq=False` + hand-written) forces `__hash__ = None`, and a value-hash is
      impossible regardless because coefficients may be `sympy.Expr`/`float`. Add one
      sentence to the frozen note. *Source:*
      `tasks/archive/2026/07/23/investigate-frozen-generated-classes.md`.
      *Home:* `tasks/reference/design-decisions.md` (frozen/slots entry) + the frozen note
      in CLAUDE.md's Architecture.

## Done-when

Both facts appear in the named live docs; nothing else changes.
