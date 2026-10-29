# Inline `insert_into_canonical` — it is a binary test (identity vs recursion), not a helper

**Status:** done — 2026-10-29. William Emerison Six <billsix@gmail.com> confirmed the spot and chose
form (b) (`(identity() if … else decrease_grade)(…)`). Work commit subject:
"gn: inline insert_into_canonical as a binary test (identity vs recursion)".
**Priority:** 5  (readability of the Gn oracle; nothing was broken)
**Difficulty:** 3  (a few lines in one hand-written method; every test stayed green)
**Created:** 2026-10-29 (William Emerison Six <billsix@gmail.com>)

## BLUF

The 2026-10-27 recursion audit (`tasks/archive/2026/10/27/audit-recursion-and-iteration-design.md`,
commit `95f2779`) had extracted the `a < c` re-insertion step of `_geometric_product`'s
`decrease_grade` into a named local helper **`insert_into_canonical`** (`src/gacalc/gn.py`). That
extraction was unnecessary: the helper was just a **two-way test** — if the re-prepended index is
already in place, keep the blade unchanged (**identity**); otherwise reduce the recombined blade
again (**recursion**, `decrease_grade`). This folded that back into the `a < c` case as a plain
binary expression `(identity() if … else decrease_grade)(prepended)`. Pure readability change —
`Gn` is the slow correct-by-construction oracle, so behaviour is identical and all 690 tests stay
green.

## What was done

Deleted `insert_into_canonical` and inlined its logic into `decrease_grade`'s
`case (a, c, *rest) if a < c:` branch, in the form the maintainer asked for:

```python
sorted_tail: BladeDictionaryEntry = decrease_grade(
    BladeDictionaryEntry(blade=(c, *rest), coefficient=basis_blade.coefficient)
)
return (
    identity() if sorted_tail.blade and a < sorted_tail.blade[0] else decrease_grade
)(
    BladeDictionaryEntry(
        blade=(a, *sorted_tail.blade), coefficient=sorted_tail.coefficient
    )
)
```

The re-prepended blade is built **inline** in the call rather than bound to a single-use
`prepended` local (the maintainer asked for this inlining — the same default as the sibling
`tasks/inline-single-use-rest-orthogonal-variable.md`). `decrease_grade`'s own `match` stays — its cases are genuine *structural* patterns on the tuple
(`()` / `(_,)` / `(a, c, *rest)` guards, plus the total `case _:` ty needs); only the extracted
boolean sub-test collapsed to the inline expression.

**Form note (b):** `gacalc.functions.identity` is a *factory* (`identity() -> InvertibleFunction[V]`,
unbounded `V`), so the literal spelling is `identity()` — it applies cleanly to a
`BladeDictionaryEntry` and ty is happy with the conditional-of-callables.

**Implementation subtlety discovered:** the original form sketches in this task assumed
`sorted_tail.blade` is non-empty and used `a < sorted_tail.blade[0]` directly. That is wrong — a tail
can fully cancel (e.g. blade `(0, 1, 1)` → `decrease_grade((1, 1))` = the empty blade `()`), in which
case the old helper's `case (head, *_)` failed to match and fell through to the recursion branch.
The inline guard `sorted_tail.blade and a < sorted_tail.blade[0]` reproduces that exactly (empty tail
is falsy → recursion), so behaviour matches the old helper on every input.

## Verification

- `python -m pytest` — **690 passed** (the equivalence to the specialized closed forms is the real
  guard; `Gn` is the oracle).
- `ruff` + `ty` clean (via `entrypoint/format.sh`); the comment was reflowed to ≤88 cols.
- `gn.py` is hand-written, not emitted by `tools/gen_specialized.py`, so `make check-generated` is
  unaffected.

## Follow-on — convention-doc updates (pending the maintainer's satisfaction check)

The generalizable lessons are to be recorded in **both** `runClaudeInContainer` and
`runCrushInContainer` (canonical + byte-identical mirror); the maintainer named the recursive-design
doc, the python coding standard, and the personal AI-conventions file in dotfiles as candidate homes:

1. **Prefer a simple `if` expression over `match`** when the test is a two-branch boolean (reinforces
   the existing "match earns its keep on *structural* patterns" note with this worked case).
2. **Functions are expressions too** — select a function with an `if`-expression and apply it
   (`(identity() if cond else f)(x)`), instead of extracting a named procedure to hold the branch.
3. **Look for this pattern:** an extracted helper that is really "identity in one case, a recursive
   call in the other" — collapse it to the inline binary test.

Per the maintainer's framing ("once you implement to my satisfaction, we will update the docs"), this
is deferred to a single cross-repo pass after the four Gn/frame tasks land and the implementations are
accepted. The recursive-design + python-coding-standard docs are at `tasks/reference/` in each
sandbox; the personal file at `~/.claude/ai-coding-conventions.personal.md` (example in
`entrypoint/dotfiles/.claude/`).

## Decision — resolved 2026-10-29 (William Emerison Six <billsix@gmail.com>)

Confirmed `insert_into_canonical` was the extracted helper meant, and chose **form (b)**
(`(identity() if … else decrease_grade)(prepended)`, the "functions are expressions too" form that
uses `identity` literally) over form (a) (the plain `prepended if … else decrease_grade(prepended)`
conditional value).
