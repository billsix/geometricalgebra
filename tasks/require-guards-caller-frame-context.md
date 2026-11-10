# Guards report the caller from the Python frame instead of a `context` string

**Status:** proposed — open questions below
**Priority:** 4
**Difficulty:** 4
**Created:** 2026-11-10 (William Emerison Six <billsix@gmail.com>)
**Branch:** `sp-rotations-guards-enums-examples`

## BLUF

`MultiVectorBase.require_vector(value, context)`, `require_vectors(values, context)` and
`frame.require_frame(vectors, context)` take a hand-written `context` string for the error message.
Replace it with caller information taken from the Python stack (function qualname, file, line), so
the message names the real call site with no string to keep in sync. Cost must stay negligible:
`sys._getframe(1)` (or `inspect.currentframe().f_back`) is a pointer walk; `inspect.stack()` reads
source files and is far too slow for a guard on the hot path — use it never. Read the frame **only
when raising**, so the success path costs nothing. Done means: every guard call site drops its
string, messages name the caller, doctests updated, gate green, CHANGELOG entry (signature change).

## Context (read first)

- Guards: `src/gacalc/base.py` (`require_vector`, `require_vectors`), `src/gacalc/frame.py`
  (`require_frame`); the new guards from `tasks/extract-validation-guards-frame-and-to-matrix.md`
  follow the same pattern, so do this one first.
- Some contexts are not function names (`"a frame's map"` for the closure `forward`); the frame gives
  `Frame.to_invertible_function.<locals>.forward`, which is accurate but less friendly. Pending question.
- The generator may emit guard calls into `g*.py`: grep `tools/gen_specialized.py` for `require_`.

## Plan

1. Implement the frame lookup in one private helper; measure the success-path cost (should be zero).
2. Update every call site (`rg -n 'require_(vector|vectors|frame)\('`), generator included; regenerate.
3. Doctests + messages; CHANGELOG; gate.
