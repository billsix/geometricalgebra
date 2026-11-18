# Frame peel inverse: reconsider head-first, remove the use-before-binding closures, revise the shared recursion rule

**Status:** proposed — needs go-ahead (open questions below)
**Priority:** 5
**Difficulty:** 3
**Created:** 2026-11-18 (William Emerison Six <billsix@gmail.com>)
**Follows:** `tasks/archive/2026/11/18/frame-inverse-head-first-recursion.md` (made the peel
head-first and wrote the head-first rule into the shared recursion guidance)

## BLUF

The maintainer reviewed the head-first peel in `Frame.to_invertible_function`
(`src/gacalc/frame.py`). Two complaints:
- the inner inverse functions read a variable that is bound only further down, in the `match` that
  picks the method;
- the head-first version may be worse than the tail-first one it replaced.

This task decides three things, then implements them:
1. whether the peel goes back to tail-first;
2. how to remove the use-before-binding;
3. how to revise the shared recursion rule in github.com/billsix/runClaudeInContainer and
   runCrushInContainer, which currently uses this peel as its worked example.

Done means:
- `frame.py` reads top to bottom, with no closure using a name bound later;
- the peel is in the chosen order;
- the frames reference doc, the shared recursion docs and both shared `CLAUDE.md` clauses agree with
  the code;
- the gates pass.

## Context (read first)

- **The code:** `Frame.to_invertible_function` in `src/gacalc/frame.py`:
  - `backward_by_reciprocal` reads `reciprocal_vectors`;
  - `backward_by_peel` reads `backward_orthogonal`;
  - both names are bound in the `match inverse_method:` after the two function definitions.
  It works because a closure looks a name up when it is called, and the match runs before
  `InvertibleFunction` is returned. Comments ("… is bound in the match below, which runs before
  this can be called") paper over it.
- **The pattern predates the head-first change.** It came in with the `inverse_method` keyword
  (commit `3f70ba3`, 2026-11-07, which bound `reciprocal_vectors` and `orthogonal_vectors` that
  way). The head-first change (`116e638`, 2026-11-18) kept it and renamed the peel's name to
  `backward_orthogonal`.
- **Before 2026-11-18 (tail-first, `116e638~1`):** the peel walked the pairs `(w_i, v_i)` of the
  frame's own orthogonal set, `Frame.orthogonal_vectors()`, with `case [*earlier, (w, v)]`, solving
  the last coordinate first and returning `[*peel(earlier, y - term), x_last]`.
- **Now (head-first):** it walks pairs `(u_i, v_i)`, where
  `u = reversed(make_orthogonal_frame(vectors[::-1]))`, the frame orthogonalized from its last
  vector. The match is `case [(u, v), *later]`, returning `[x_first, *peel(later, y - term)]`.
- **The rule written from it, staged on 2026-11-18 and committed by the maintainer** (runClaude
  `54858a5`, runCrush `4f52801`):
  - `tasks/reference/recursive-design.md` "Handle the head first — a strong preference" in
    runClaudeInContainer, with byte-identical copies in runCrushInContainer `tasks/reference/` and
    `client/entrypoint/dotfiles/.config/crush/reference/`. It says that when an algorithm seems to
    need the tail first, you should reorder how its data is built, and it cites this peel;
  - a clause in both shared `CLAUDE.md` files ("Prefer a named recursion scheme"):
    runClaudeInContainer `entrypoint/dotfiles/.claude/CLAUDE.md` and runCrushInContainer
    `client/entrypoint/dotfiles/.config/crush/CLAUDE.md`.
- **Also touched by the head-first change** (to revert if the peel goes back):
  - `tasks/reference/frames-qr-and-reciprocal-frames.md` "The peel inverse, step by step" (and the
    face-normal / line-to-line passages);
  - the `CLAUDE.md` module-layout line for `frame.py`;
  - the docstring's steps and worked example.

## Assessment, before and after (agent, 2026-11-18)

**The head-first version is worse, and I recommend reverting the order.**

- **The recursion got nicer, the data got worse.** `[head, *tail]` reads better than
  `[*earlier, last]`. But the head-first peel needs a second orthogonal set, `u_i`, that exists
  nowhere else:
  - it is not `Frame.orthogonal_vectors()`;
  - the book's frame-QR notebooks do not show it;
  - the reference doc's QR story does not use it;
  - the Lean model does not use it.

  The old peel used the set the whole `Frame` is built on. Its step was "solve the last
  coordinate with the last `w_k`", which is back-substitution against the QR factor `R`.
- **The reversal moved, it did not go away.** The rule I wrote says matching `[head, *tail]` on a
  reversed list "does not count". Building `u` by reversing the frame, orthogonalizing and reversing
  back is that same move, pushed into the data. It is the tail-first algorithm run on the reversed
  frame, as the original task's analysis said under option (C).
- **The Lean twin no longer matches.** `invPeel` in `proofs/GacalcProofs/ReciprocalFrame2D.lean` /
  `ReciprocalFrame3D.lean`, with the theorems `invPeel_frameMap`, `invReciprocal_eq_invPeel` and
  `recip*_eq_reject_div`, peels from the last vector using the last rejection. The results agree
  because coordinates are unique, but the construction no longer mirrors Lean. That is the drift
  `tasks/reference/lean-python-notebook-workflow.md` tells us to avoid.
- **Unchanged either way:** results (tests and docs agree), cost (one orthogonalization per map),
  and the reciprocal default, which is order-free.

**The use-before-binding is a separate problem with a clean fix.** Have each backward function
take its precomputed data as a parameter, and bind it in the `match` with `functools.partial`:

```python
def backward_by_reciprocal(reciprocal: tuple[MultiVectorBase, ...], y: MultiVectorBase) -> MultiVectorBase: ...
def backward_by_peel(orthogonal: tuple[MultiVectorBase, ...], y: MultiVectorBase) -> MultiVectorBase: ...

match inverse_method:
    case InverseMethod.RECIPROCAL:
        backward = functools.partial(backward_by_reciprocal, self.reciprocal_vectors())
    case InverseMethod.PEEL:
        backward = functools.partial(backward_by_peel, self.orthogonal_vectors())
```

Every name is then defined before it is used, the data a function depends on is in its signature,
and the "bound below" comments go. `ty` types `partial` precisely: a probe on 2026-11-18 confirmed
it accepts `Callable[[int], int]` and rejects a wrong `Callable[[str], int]`. Alternatives:
- define each closure inside its `match` arm, after binding its data; this splits the definitions
  into the dispatch and makes it longer;
- a small factory per method that returns the closure; this is more code for the same effect.

**The shared rule overreaches and should be softened, not dropped.** "Handle the head first when
the data allows it" is good advice. "Reorder how the data is built so the head can go first" was
drawn from an example that turned out to be the reversal in disguise. Suggested revision:
- prefer `[head, *tail]` when the data is already in that order;
- when the data's construction makes the last element the one that can be solved (back-substitution
  over a triangular factor, a stack), tail-first is the honest shape; inventing a second
  construction just to recurse from the head is the reversal moved, not removed;
- replace the worked example with this frame as the counter-example, or remove the example.

## Progress

- **Step 1, done 2026-11-18, before the questions, at the maintainer's request:** the
  use-before-binding is gone, with the head-first order kept.
  - `backward_by_reciprocal` and `backward_by_peel` take their vectors as a first parameter;
  - the `match` binds them with `functools.partial(…, self.reciprocal_vectors())` /
    `functools.partial(…, <the backward-orthogonalized frame>)`;
  - the "bound in the match below" comments are gone.

  This is question 2's option (a). It was committed on its own, before the order change.

## Plan

1. Settle the open questions (question 2 is answered by step 1 above).
2. `src/gacalc/frame.py`:
   - remove the use-before-binding (question 2);
   - set the peel order (question 1). If reverting: walk `orthogonal_vectors()` with
     `case [*earlier, (w, v)]`, restore the docstring's tail-first steps and worked example
     (`git show 116e638~1:src/gacalc/frame.py`), and drop the Lean-mismatch sentence.
3. Docs in this repo:
   - `tasks/reference/frames-qr-and-reciprocal-frames.md`: the peel section, face normals and
     line-to-line, recording the head-first attempt and why it was reverted;
   - the `CLAUDE.md` `frame.py` line.
4. The shared rule (question 3):
   - edit the canonical runClaudeInContainer `tasks/reference/recursive-design.md`;
   - re-copy it over both runCrushInContainer copies;
   - edit both shared `CLAUDE.md` clauses;
   - stage by path in both repos.
5. Gates:
   - `tests/test_frame_class.py` including the slow peel cases (about 8 minutes);
   - `tests/test_frame.py`;
   - the `frame.py` doctests;
   - container `make format` and `make test`.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-18)

1. **Peel order: (a)**, revert to tail-first over `orthogonal_vectors()`, aiming for the code that
   reads best, for the reasons in the assessment above.
2. **Use-before-binding: (a)**, `functools.partial`. This was done first and committed on its own
   as `cd73128`.
3. **Shared recursion rule: (a)**, soften it: head-first when the data is in that order,
   tail-first when the construction makes the last element the solvable one, with the frame as
   the counter-example.

## Open questions

None.
