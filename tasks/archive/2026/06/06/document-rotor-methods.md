# Document the new rotor methods; reframe the "future rotation" wording

**Created:** 2026-06-06 · **Completed:** 2026-06-06

`AbstractMultiVector` had gained two rotation methods that `CLAUDE.md` did not mention, while the
code still described a general vector-to-vector rotation as future work. This was a
documentation/comment pass with no behavior change.

## The methods (in `base.py`)

- **`AbstractMultiVector.rotate(from_vector, to_vector)`** — a classmethod returning a
  `MultiVectorFn`: a general, representation-agnostic vector-to-vector rotation. It normalizes both
  vectors, forms the plane `from ∧ to`, turns the in-plane component through the angle between them,
  and leaves the perpendicular component unchanged; equivalent to the rotor sandwich
  `R v R.inverse()`.
- **`AbstractMultiVector.rotor_from_vectors(from_vector, to_vector)`** — builds the un-normalized
  rotor `R = |from||to| + to·from` (scalar + bivector); its sandwich `R v R.inverse()` matches
  `rotate(from, to)(v)`. Its docstring already covered the inverse-vs-reverse scaling subtlety and
  the antiparallel degeneracy.

These are distinct from the planar 2D factories then in `transforms.py` (`rotate(angle)`,
`rotate_90_degrees`, `rotate_around`), and the name collision `transforms.rotate(angle)` vs
`AbstractMultiVector.rotate(from, to)` was called out.

## What changed

- **`CLAUDE.md`:** a rotations-and-rotors note distinguishing the general
  `AbstractMultiVector.rotate` / `rotor_from_vectors` (any plane, any representation) from the planar
  2D `transforms` factories, flagging the `rotate` collision. This was done together with
  `tasks/archive/2026/06/06/refresh-claudemd-known-issues.md`, which edited adjacent sections.
- **`transforms.py` module docstring:** "a separate, future addition" became present tense, pointing
  at `AbstractMultiVector.rotate` as the general path.
- **`tasks/archive/2026/06/06/clarify-2d-only-transforms.md`:** the "future rotation" wording the plan
  attributed to it was not actually there, so instead a cross-reference was added pointing to the
  general `AbstractMultiVector.rotate` for true 3D rotation. The planar-guard implementation stayed
  that task's job.
- **README:** unchanged. It was already ahead of `CLAUDE.md` (its "Graded subtypes" section covered
  `rotor_from_vectors` and `plane_of_rotation()`), and the new `CLAUDE.md` text did not contradict it.

## Verification

`test_rotate` already covered the general method across `[Gn, G1, G2, G3]` in the conformance suite,
so no test work was split to `tasks/archive/2026/06/06/transform-type-roundtrip-tests.md`. Suite (141)
and `entrypoint/format.sh` unchanged and clean.
