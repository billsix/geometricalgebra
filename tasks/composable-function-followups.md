# Composable-function layer — follow-ups (naming + animation-layer placement)

**Status:** proposed — not started (spun off from the completed composable-function refactor, 2026-07-17)
**Priority:** 6
**Difficulty:** 4
**Created:** 2026-07-17

## Context

The composable-function interface refactor landed in gacalc 0.0.9 (see the archived
`reassess-composable-function-interface.md`): a leaf `functions.py` with `ComposableFunction` +
`InvertibleFunction`, `project`/`reject` returning `ComposableFunction`, `reflect`/`identity`
returning `InvertibleFunction`, `labeled` removed, `Self` typing dropped. These two items were
deferred out of that work as separate, non-blocking polish.

## 1. Reassess the `functions` vs `transforms` module names (newcomer's view)

The leaf-vs-consumer split is an *internal* layering concern; a newcomer just wants good names and
shouldn't need to know about leaves / import-acyclicity to find things. Since `transforms`
re-exports everything from `functions` (`ComposableFunction`, `InvertibleFunction`, `compose`,
`inverse`, …), a user can already `from gacalc.transforms import …` and never touch `functions`.

Assess:
- (a) Is "transforms" still the right *public* name, or should the user-facing module be renamed
  (e.g. `functions` / `morphisms` / `maps`), with the GA-specific *factories* under a clearer name?
- (b) Should `functions` be treated as private/internal (underscore-prefixed, or just documented as
  "don't import directly — use `transforms`") so there's **one** obvious public entry point?

Goal: a newcomer sees good names and one place to import from, with the leaf split invisible.
(`ComposableFunction` itself is the working type name — vs `LabeledFunction` / `Transform` /
`DisplayableFunction`; confirm it too, since it's now the public type name.)

## 2. Where does the animation layer sit — base or invertible subtype?

The animation layer (`interpolate` / `components` / `at` / `steps`) currently lives on the base
`ComposableFunction`. That's what made `compose` / `at` have to thread the invertible-vs-not return
type through interpolation (the overloads + the `InvertibleFunction.at` override). Decide whether it
belongs on the base (interpolating a projection for display is reasonable — **lean: base, it's
display not inversion**) or only on `InvertibleFunction`. If it moves to the subtype, some of the
overload/override machinery may simplify.

## Notes

- Both are cross-repo-visible if they change public names/imports (mvp imports from
  `gacalc.transforms`); coordinate a version bump + mvp pin as with the core change.
