# Rotation factories: from 0 to 0 is the identity; 0 to nonzero is a ValueError

**Status:** in progress
**Priority:** 3
**Difficulty:** 3
**Created:** 2026-11-10 (William Emerison Six <billsix@gmail.com>, 2026-11-10)
**Branch:** `sp-rotations-guards-enums-examples`
**Split from:** `tasks/standard-position-e3-axis-and-vector-rotations.md` (Decisions)

## BLUF

A rotation "from `a` to `b`" built by `transforms.projection_rotation`, `transforms.versor_rotation`,
`MultiVectorBase.versor_from_vectors` and `rotor_from_vectors` follows one rule for the zero vector:
**from the zero vector to the zero vector is the identity**; from zero to a nonzero vector, or from a
nonzero vector to zero, raises `ValueError` (no direction to rotate from or to). Today
`projection_rotation` with a zero vector raises a misleading "opposite directions" message. Done
means: every factory follows the rule, doctests show all three cases, CHANGELOG entry, gate green.
