# Audit the source for recursion / iteration to align with the recursive-design pattern

**Status:** DONE 2026-10-27 (William Emerison Six <billsix@gmail.com>). Ready to archive after the
work commit.
**Priority:** 6
**Difficulty:** 4
**Created:** 2026-10-27 **Updated:** 2026-10-27 (William Emerison Six <billsix@gmail.com>)

## BLUF

A full read of every hand-written module in `src/gacalc/` for (a) recursions to align to the
`~/.claude/reference/recursive-design.md` pattern and (b) iterative code that should be recursive.
The code was already largely aligned; the one actionable item was polishing `decrease_grade` (the
geometric product's blade canonicalizer in `gn.py`). Done: its base case split (`case ():` /
`case (_,):`), operation-first comments, and the `a<c` re-insertion extracted as a named
`insert_into_canonical` helper — behavior unchanged (it is the slow `Gn` oracle): 690 pytest passed,
ty + ruff clean. Two long-standing `# type: ignore` suppressions were removed as a side-item. No
"should be recursive but isn't" case was found.

## What was studied

Read in full: `base.py`, `gn.py`, `frame.py`, `functions.py`, `transforms.py`, `measure.py`,
`vectorcalc.py`, `standardposition.py`, `nbplotutils.py`, `__init__.py`. Excluded the generated
`g1`–`g5.py` (build artifacts — any recursion there is authored in `tools/gen_specialized.py` and
regenerated, never hand-edited).

## What was found and done

- **`decrease_grade` (geometric product, `gn.py`) — polished.** It was already a clean `match`-based
  structural recursion (a base case, three `(a, c, *rest)` guard cases, a total default). Split the
  base into `case ():` (the scalar 1) and `case (_,):` (a lone basis vector); rewrote each case
  comment **operation-first** (equal adjacent indices square to 1 and cancel; an out-of-order pair
  swaps and negates; `a<c` canonicalizes the tail then re-inserts `a`); and extracted the intricate
  `a<c` re-insertion as a named `insert_into_canonical` helper so the branch reads plainly.
- **The geometric product itself — left as-is.** It is a `sum`-fold over `itertools.product` of the
  two operands' blade-term pairs — already a named scheme. The recursive-distribution rewrite
  (`(a0 + A')*B = a0*B + A'*B`) was considered and declined; the clarity win was in `decrease_grade`,
  not in replacing the fold.
- **`case _:` kept — required, not cosmetic.** `ty` does not prove the guarded `a==c`/`a>c`/`a<c`
  trichotomy exhaustive; deleting the default makes it report `invalid-return-type: Function can
  implicitly return None`. The comment records this (verified empirically).
- **Two `# type: ignore` removed.** Both wrapped `sympy.simplify(x)` where `x: Real`
  (`int | float | sympy.Expr`); `simplify`'s overloads accept only `Expr`/`Basic`, not `int`/`float`.
  Wrapping the argument in `sympy.sympify(...)` — the conversion `simplify` does internally anyway —
  makes `ty` accept it with no suppression and no behavior change (`gn.py` `__post_init__`'s eager
  simplify, `base.py` `simplified`).

## Left as-is (studied, no change needed)

The bilinear product family (`inner_product` / `outer_product` / the contractions — `sum`-folds over
grade pairs), `frame.prefix_blades` (an `accumulate` scan), `base.outer_product_of_vectors` (a wedge
`reduce`), `functions.compose` (application left-folds), and the dispatch `match`es are already named
schemes / total dispatch. The imperative loops in `nbplotutils` (plotting) and `transforms` (matrix
assembly) iterate over coordinates / artists, not the algebra's data — genuinely iterative, correctly
left alone.

## Follow-on (done)

The general `ty`-exhaustiveness finding — list/tuple patterns **and** guarded cases both need an
explicit `case _`, with the exact `invalid-return-type` diagnostic — was folded into the shared
`recursive-design.md` reference doc (runClaudeInContainer canonical + byte-identical runCrush mirror).
