# Refactor `Frame.to_invertible_function`: inline single-use locals, narrow scopes, name the implied dimension

**Status:** ready — questions answered 2026-11-06; the maintainer said not to start yet ("don't start work yet").
**Priority:** 3
**Difficulty:** 3
**Created:** 2026-11-06 (William Emerison Six <billsix@gmail.com>)
**Next:** `tasks/reuse-existing-vector-check.md` (one shared vector check). It depends on this task: it
replaces the nested `require_vector` this task keeps, and the non-vector check inside the new
`implied_minimal_number_of_dimensions()`, so doing this task first avoids editing the same lines twice.

## BLUF

`Frame.to_invertible_function` (`src/gacalc/frame.py`) works, but it does not read the way the
maintainer wants. It binds names that are used only once, spells "the smallest dimension a vector needs"
as an opaque nested `max`, and declares `pairs` and `peel` far wider than where they are used. This task
reshapes it with no change in behaviour. Then, as the last step, it writes the rules learned here into
the shared cross-project standards in github.com/billsix/runClaudeInContainer and
github.com/billsix/runCrushInContainer. Done = the method is refactored, a named public
implied-dimension method replaces all three copies of the dimension-inference logic, `make test` and
`make format` pass, a `CHANGELOG.md` `[Unreleased]` entry exists, and the shared docs are updated in
both sandbox repos. The maintainer has said more issues with this method will follow; add them under
"Later issues" when they arrive.

## Context

- **The code:** `Frame.to_invertible_function` in `src/gacalc/frame.py` (`def to_invertible_function`).
  It has a long docstring (the peel derivation and a doctest), then the body: compute `k` and `n`, raise if
  `k != n`, build `pairs`, then the nested helpers `require_vector`, `forward`, `peel`, `backward`.
  Math background: `tasks/reference/frames-qr-and-reciprocal-frames.md` ("The peel inverse, step by
  step").
- **The governing shared rule today:** "Inline a value used exactly once — unless the name documents an
  otherwise-opaque expression" in the `python-coding-standard.md` reference doc
  (github.com/billsix/runClaudeInContainer `tasks/reference/`, byte-identical mirror in
  runCrushInContainer). Its "documents an opaque expression" exception is exactly what the maintainer
  rejects here (see Decisions). Read it, plus "What earns an extraction", before editing.
- **The dimension-inference logic exists in three places:**
  1. `frame.py`, this method: `getattr(cls, "DIMENSION", None)`, else
     `max(max(blade) for v in … for blade in v.to_blade_dict() if blade)`. That `max` has no `default=`,
     so it would raise on all-zero input. A frame cannot hold a zero vector, so this never fires.
  2. `measure.py`: the private helper `_max_basis_index(vectors)` (`default=0`), used by
     `signed_content` with the same `DIMENSION`-else pattern.
  3. `vectorcalc.py` `cross`: imports `measure._max_basis_index` across modules (a private name) and
     calls it twice.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-06)

1. **A local that is bound once and used once is inlined, even when the name was there for
   readability.** The reader of a declaration scans ahead to see how far it is used. A one-use binding
   wastes that scan, and the waste grows with the length of the method. Instead, put a **comment above
   the inlined subexpression** that quotes or describes it and **gives it its name in the comment**. A
   local used two or more times stays a local.
2. **A declaration goes where it is used, not earlier.** `pairs` is built many lines before its only
   use, inside `backward`.
3. **A helper used by only one function is nested inside that function.** `peel` is used only by
   `backward`, so it moves inside `backward` unless there is a real reason not to. Analysis for the
   maintainer: the only cost is that a nested `def` creates a new function object on each `backward`
   call, which is microseconds next to the sympy and multivector work in each peel step. Recursion
   through the closure cell works the same. There is no performance or correctness reason to keep it at
   the outer level.
4. **The `n` ternary is replaced by a named method.** The `max(max(blade) …)` idea ("the highest
   basis index this vector uses, i.e. the smallest coordinate space that holds it") is extracted into
   `base.py`, `gn.py`, or the generated classes. The working name is `implied_minimal_number_of_dimensions`.
   The method checks that its input is a vector.
5. **Home and shape (Q1, answered yes):** an instance method on `MultiVectorBase` (`base.py`),
   `v.implied_minimal_number_of_dimensions() -> int`. It raises `ValueError` on a non-vector and
   returns the highest basis index `v` uses, or 0 for the zero vector. Callers with several vectors
   take `max(...)` over them. Being a base method, it works for `Gn` and every generated class with no
   generator change.
6. **Name (Q2, answered yes):** exactly `implied_minimal_number_of_dimensions`.
7. **No shared "`DIMENSION` else implied" helper (Q3, left to the agent's discretion; decided no).**
   Only the per-vector method is extracted. Each caller keeps its short `getattr(cls, "DIMENSION",
   None)` check, because `vectorcalc.cross` uses the two halves differently (it rejects a fixed
   dimension other than 3 and, separately, an implied dimension above 3); one helper would hide that
   difference. `measure._max_basis_index` is deleted, and its callers use the new method.
8. **Where the shared rules go (Q4, answered yes):** the full rule with examples goes in
   `python-coding-standard.md` and the language-agnostic `code-style-conventions.md`, plus one
   short line in the shared `CLAUDE.md` (`entrypoint/dotfiles/.claude/CLAUDE.md`, under "What earns
   pulling code into its own function"). All three are edited in github.com/billsix/runClaudeInContainer
   and mirrored byte-identically in github.com/billsix/runCrushInContainer. The rule is portable, so
   it does not go in the personal overlay.
9. **"Used twice" does not by itself earn a name either** (William Emerison Six <billsix@gmail.com>,
   2026-11-06, mid-implementation: "just because some variable is 'used twice' doesn't mean it has to
   be"). Before keeping a multi-use local, check whether one expression can absorb the uses.
   `dimension` was used twice, but only as `d if d is not None else fallback`, which is exactly what
   `getattr(cls, "DIMENSION", fallback)` already does, so the local and the ternary both go away. The
   cost is that the fallback is now always evaluated (a few dict lookups per vector), which is fine here.
   `k = len(self.vectors)` is used twice too, but repeating `len(self.vectors)` costs nothing and reads
   as well, so it is inlined. A name stays only when repeating its expression would be longer or harder
   to read than the name (`n`), or would compute something expensive twice. `n` was reviewed against this rule
   (William Emerison Six <billsix@gmail.com>, 2026-11-06): its second use is only the error message,
   and the alternatives were (a) inline it into the check and drop `n` from the message, losing
   information, or (b) write its three-line expression twice. The maintainer chose to keep `n`, here and
   in `measure.signed_content`. The knowledge-extraction
   step carries this rule along with Decision 1.
10. **When a helper is nested into its only caller, its parameters should shadow the caller's
   variables of the same meaning, and the agent must verify the shadowing is correct** (William
   Emerison Six <billsix@gmail.com>, 2026-11-06: "I prefer shadowing if it works correctly because it
   makes sure the reader knows they don't need to keep track of the outer y"). A shadowing parameter
   tells the reader the outer binding is out of play inside the helper. Correct means the helper never
   needs the outer value, and none of the helper's other names (parameters, pattern captures, locals)
   accidentally capture or hide something it does need. Checked for `peel` inside `backward`: `peel`'s
   `y` shadows `backward`'s `y`, and `peel` reads only its own `y` (each recursive call passes the
   reduced remainder). Its other names (`remaining`, `earlier`, `w`, `v`, `x_last`) bind nothing in the
   enclosing scopes (`to_invertible_function` binds `n`, `require_vector`, `forward`, `backward`; the
   `v` in `forward`'s generator is local to `forward`), so the shadowing is correct and is kept.

## Plan

1. Add `MultiVectorBase.implied_minimal_number_of_dimensions()` (Decisions 5–6), with a doctest and a
   non-vector `ValueError`. Route `measure.signed_content` and `vectorcalc.cross` through it and delete
   `measure._max_basis_index` (Decision 7). Add a `CHANGELOG.md` `[Unreleased]` "Added" entry for the new
   public method.
2. Refactor `to_invertible_function`:
   - Use `self.vectors` directly in place of the `frame_vectors` alias (CLAUDE.md: "No local aliases").
   - Inline `cls` and `dimension`. They disappear once the method from step 2 computes `n`.
   - Inline `k` as `len(self.vectors)` and keep `n` (Decision 9).
   - Move `peel` inside `backward`. Inline `pairs` into the `peel(...)` call there, with a comment naming
     it ("pairs: each orthogonal vector `w_i` with the frame vector `v_i` it came from, in frame order").
   - Inline `x_last` into the recursive call only if it is used once. It is used **twice** (in
     `y - x_last * v` and in the returned list), so it stays.
   - Keep `require_vector` at its current level: both `forward` and `backward` use it.
3. Gates: `make test`, `make format` (ruff + ty), `python tools/check_annotations.py` (no new rows).
4. **Last item: extract the knowledge.** Update the shared docs (Decision 8) in
   github.com/billsix/runClaudeInContainer and mirror the change byte-identically into
   github.com/billsix/runCrushInContainer:
   - Rewrite the inline-once rule: drop the "documents an opaque expression" exception, and replace it
     with "inline it, with a comment above that names the subexpression". Name the cost it avoids (the
     reader's scan for the extent of a declaration).
   - Add "declare at the point of use" and "nest a helper inside its only caller".
   - Replace the gacalc worked examples with this refactor (before/after) in
     `tasks/reference/python-coding-standard-gacalc.md`.
   - Add the shadowing advice (Decision 10): when nesting a helper into its only caller, give its
     parameter the caller's name when it means the same kind of value, so it deliberately shadows the
     outer binding, and verify the helper never needs the outer value and that none of its other
     names capture or hide an enclosing one. Put it beside "nest a helper inside its only caller" in
     both reference docs and the short `CLAUDE.md` line.
   - Add Decision 9 ("used twice" does not by itself earn a name; check whether one expression, such
     as `getattr` with a default, absorbs the uses).
   - Stage both repos by path.

## Open questions

None — all four answered 2026-11-06 (see Decisions 5–8).

## Later issues

(The maintainer has more issues with this method; record them here as they arrive.)
