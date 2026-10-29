# Inline `insert_into_canonical` — it is a binary test (identity vs recursion), not a helper

**Status:** proposed — needs go-ahead. The maintainer asked to confirm the finding (the exact spot
and intended form) before implementation — see §Open questions.
**Priority:** 5  (readability of the Gn oracle; nothing is broken)
**Difficulty:** 3  (a few lines in one hand-written method; must keep every test green)
**Created:** 2026-10-29 (William Emerison Six <billsix@gmail.com>)

## BLUF

The 2026-10-27 recursion audit (`tasks/archive/2026/10/27/audit-recursion-and-iteration-design.md`,
commit `95f2779`) extracted the `a < c` re-insertion step of `_geometric_product`'s `decrease_grade`
into a named local helper **`insert_into_canonical`** (`src/gacalc/gn.py`). That extraction was
unnecessary: the helper is just a **two-way test** — if the prepended index is already in place,
return the blade unchanged (**identity**); otherwise reduce the recombined blade again
(**recursion**, `decrease_grade`). Replace the extracted `match`-based helper with a plain binary
`if` expression inline in the `a < c` case. Pure readability change — `Gn` is the slow
correct-by-construction oracle, so behavior must be identical and all ~690 tests stay green.

## Context (cold-start)

- File: `src/gacalc/gn.py`, inside `Gn._geometric_product` (the reference product). Two nested local
  functions matter: `decrease_grade` (the structural recursion that canonicalizes a concatenated
  blade's index tuple) and `insert_into_canonical` (the extracted helper).
- `insert_into_canonical(first, sorted_tail)` builds `prepended = (first, *sorted_tail.blade)`, then:
  ```python
  match sorted_tail.blade:
      case (head, *_) if first < head:
          return prepended  # already in place  -> identity
      case _:
          return decrease_grade(prepended)  # collides/outranks -> recurse
  ```
  It is called only once, from `decrease_grade`'s `case (a, c, *rest) if a < c:` branch, right after
  that branch canonicalizes the tail.
- **History:** before `95f2779` this test lived **inline** in the `a < c` branch as a `match` with a
  guard + wildcard; the audit *extracted* it to a named helper "so the branch reads plainly". This
  task reverses that call.
- **Conventions it rests on** (`~/.claude/reference/recursive-design.md`, and CLAUDE.md "Prefer
  total dispatch"): a `match` whose every case is a boolean guard "is an `if`/`elif` chain in
  disguise — don't convert every two-branch conditional." A two-branch boolean test is a plain `if`
  expression; extracting it into a named procedure buys nothing here.

## Proposed change

Delete `insert_into_canonical` and inline its logic into the `a < c` case of `decrease_grade`.
Candidate forms (decide with the maintainer — see Open questions):

- **(a) plain conditional value** — `head = sorted_tail.blade[0]` is always present (`sorted_tail` is
  a non-empty canonical blade):
  ```python
  prepended = BladeDictionaryEntry(
      blade=(a, *sorted_tail.blade), coefficient=sorted_tail.coefficient
  )
  return prepended if a < sorted_tail.blade[0] else decrease_grade(prepended)
  ```
- **(b) "functions are expressions too"** — pick the function, then apply it (uses the imported
  `identity`):
  ```python
  reduce = identity if a < sorted_tail.blade[0] else decrease_grade
  return reduce(prepended)
  ```
  This reads literally as the maintainer's description: *a binary test; identity in one case,
  recursion in the other.* (Confirm `gacalc.functions.identity` applies cleanly to a
  `BladeDictionaryEntry` — it is the composable identity; if its typing fights, use form (a).)

Either keeps `decrease_grade`'s existing `match` structure (its cases are genuine *structural*
patterns on the tuple — `()`/`(_,)`/`(a,c,*rest)` guards — so that `match` stays; only the extracted
boolean sub-test collapses to an `if`).

## Verification

- `make test` — all ~690 pytest/doctests green (the equivalence to the specialized closed forms is
  the real guard; `Gn` is the oracle).
- `make format` — ruff + ty clean. Keep `decrease_grade`'s total `case _:` default (ty needs it; the
  audit recorded the exact `invalid-return-type` diagnostic).
- `make check-generated` unaffected — `gn.py` is hand-written, not emitted by `tools/gen_specialized.py`.

## Follow-on (AFTER the code change is accepted — do not do it with the code commit)

Update, in **both** `runClaudeInContainer` and `runCrushInContainer` (canonical + byte-identical
mirror), the generalizable lessons — the maintainer named the recursive-design doc, the python
coding standard, and the personal AI-conventions file in dotfiles as candidate homes:

1. **Prefer a simple `if` expression over `match`** when the test is a two-branch boolean (reinforces
   the existing "match earns its keep on *structural* patterns" note with this worked case).
2. **Functions are expressions too** — you can select a function with an `if`-expression and apply it
   (`(identity if cond else f)(x)`), instead of extracting a named procedure to hold the branch.
3. **Look for this pattern:** an extracted helper that is really "identity in one case, a recursive
   call in the other" — collapse it to the inline binary test.

Confirm the exact doc/paths at that point; the recursive-design + python-coding-standard docs are at
`tasks/reference/` in each sandbox, the personal file at `~/.claude/ai-coding-conventions.personal.md`
(example in `entrypoint/dotfiles/.claude/`).

## Open questions

1. **Confirm the spot and the form.** Is `insert_into_canonical` the extracted local method you meant,
   and is the intended fix to inline it as the binary test above? If so, which form — **(a)** the
   plain `prepended if … else decrease_grade(prepended)` conditional value, or **(b)** the
   `(identity if … else decrease_grade)(prepended)` form that uses the `identity` function literally?
   (Recommendation: (b) if `identity` applies cleanly to a `BladeDictionaryEntry` — it matches your
   "use the identity function" wording; otherwise (a).)
