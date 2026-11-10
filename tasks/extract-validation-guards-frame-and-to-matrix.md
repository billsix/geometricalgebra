# Pull validation out of `Frame.to_invertible_function` and `to_matrix` into one-line guards

**Status:** in progress — questions answered (see Decisions)
**Priority:** 4
**Difficulty:** 3
**Created:** 2026-11-10 (William Emerison Six <billsix@gmail.com>)
**Branch:** `sp-rotations-guards-enums-examples`

## BLUF

Like `require_vectors`, the checks that open `Frame.to_invertible_function` (`src/gacalc/frame.py`:
the frame must span the space, `k = n`, and the `inverse_method` must be known) and
`transforms.to_matrix` (`fn` must be linear/affine; `n` must be inferable from `cls.DIMENSION`) move
into named guard functions, so each body opens with a one-line call and reads as the task at hand.
Done means: the guards exist with doctests, both bodies call them in one line each, messages are
unchanged in meaning, the gate is green.

## Context (read first)

- Existing guard shape: `MultiVectorBase.require_vector(s)` (`src/gacalc/base.py`),
  `require_frame` (`src/gacalc/frame.py`); after `tasks/require-guards-caller-frame-context.md` they
  take no context string — do that task first and follow its shape.
- `ComposableFunction.to_matrix` / `.to_matrix_template` (`src/gacalc/functions.py`) forward to
  `transforms.to_matrix` / `to_matrix_template`; the layering rule (import `transforms` inside the
  method body only) must hold.
- The `inverse_method` check disappears if `tasks/options-as-enums.md` makes it an enum matched
  exhaustively.
- The request said "update to matrix. Matrix" (resolved in Decisions).

## Decisions

- "update to matrix. Matrix" means: apply the new guards to `to_matrix`, `to_matrix_template`, and the `ComposableFunction.to_matrix` / `.to_matrix_template` methods (William Emerison Six <billsix@gmail.com>, 2026-11-10).
