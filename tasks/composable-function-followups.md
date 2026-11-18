# Composable-function layer — follow-ups (naming + animation-layer placement)

**Completed:** 2026-11-18 (William Emerison Six <billsix@gmail.com>; authorized batch
`ready-tasks-batch-2026-11-18`)
**Priority:** 6
**Difficulty:** 4
**Created:** 2026-07-17

## Outcome

The 0.0.9 composable-function refactor (`tasks/archive/2026/07/17/reassess-composable-function-interface.md`)
left two questions open. Both were decided with no rename and no move, so the public API did not
change and there is no changelog entry. The decisions and their reasons are in
`tasks/reference/transform-and-composable-function-layer.md`, "Module names and the animation layer's
place".

1. **Module names.** `gacalc.transforms` stays the public name and is documented as the one entry
   point; its module docstring now says it re-exports the whole `gacalc.functions` leaf. That
   docstring had also placed the animation layer on `InvertibleFunction`, which was wrong, and is
   fixed. Neither module was renamed:
   - modelviewprojection imports `gacalc.transforms`;
   - `base.py`, `frame.py` and the generated modules import `gacalc.functions`, so underscoring it
     would churn the generator for nothing a user sees.

   The type names `ComposableFunction` / `InvertibleFunction` were already settled on 2026-08-28.
2. **Animation layer.** `at` / `steps` stay on `ComposableFunction`, as the task had leaned:
   interpolating a projection is display, not inversion. Moving them would remove only the 4-line
   `InvertibleFunction.at` cast override. The `@` / `compose` overloads exist for composition and
   would stay either way.

## Judgment call

These were the task's own questions, and the batch was authorized without asking them again. Both
answers keep the current API, so nothing breaks for consumers. Undoing either one later means doing
the rename or the move then.

## Verification

ruff passed and `src/gacalc/transforms.py`'s doctests passed (21).
