# Document the new rotor methods; reframe the "future rotation" wording

**Status:** complete
**Completed:** 2026-06-06
**Started:** 2026-06-06

> **Completion note:** done as described, with one correction — the "future rotation" wording the
> plan attributed to `tasks/clarify-2d-only-transforms.md` was **not** present there (only in
> `transforms.py`, now fixed). Instead of reversing nonexistent wording, added a cross-reference in
> that task pointing users to the general `AbstractMultiVector.rotate` for true 3D rotation. No README
> change: `test_rotate` already covers the general method across `[Gn, G1, G2, G3]` (conformance),
> and README's existing rotor coverage isn't contradicted by the new CLAUDE.md text.

## Goal

`AbstractMultiVector` gained two rotation methods that the contributor doc (CLAUDE.md) doesn't
mention, and several places in the codebase still describe a general vector-to-vector rotation as
*future work* even though it now exists. Document the methods where contributors look (CLAUDE.md
"Operators"/Architecture), and reconcile the now-obsolete "future addition" wording in
`transforms.py` and `tasks/clarify-2d-only-transforms.md`. Doc/comment accuracy pass — **no behavior
change.**

## The methods (present in `base.py` today)

- **`AbstractMultiVector.rotate(from_vector, to_vector)`** (`base.py` ~line 554, classmethod returning
  a `MultiVectorFn`). A *general*, representation-agnostic vector-to-vector rotation: normalizes both
  vectors, forms the plane `from ∧ to`, turns the in-plane component through the angle between them
  via `… * from * to`, and leaves the perpendicular component unchanged. Equivalent to the rotor
  sandwich `R v R.inverse()`.
- **`AbstractMultiVector.rotor_from_vectors(from_vector, to_vector)`** (`base.py` ~line 585,
  classmethod returning a multivector). Builds the (un-normalized) rotor `R = |from||to| + to·from`
  (scalar + bivector, the even-subalgebra grade); its sandwich `R v R.inverse()` matches
  `rotate(from, to)(v)`. Docstring already explains the inverse-vs-reverse scaling subtlety and the
  antiparallel degeneracy.

These are distinct from the **2D planar** `rotate(angle)` / `rotate_90_degrees` / `rotate_around`
*factories* in `transforms.py`, which act only in the e₁e₂ plane. Naming collision worth calling out:
`transforms.rotate(angle_in_radians)` (a planar `InvertibleFunction` factory) vs.
`AbstractMultiVector.rotate(from_vector, to_vector)` (a general method on the algebra). The docs
should make the split unmistakable.

## Why

- CLAUDE.md's "Operators" section lists `*`, `^`, `@`, `abs`, `.inverse()` but says nothing about
  rotations or rotors, so a contributor wouldn't know the general rotor path exists or how it relates
  to the planar transform factories.
- README is **ahead** of CLAUDE.md here: its "Graded subtypes" section already documents
  `rotor_from_vectors(from, to)` and `plane_of_rotation()`. The contributor doc should at least match.
- Stale "future work" wording actively misleads:
  - `transforms.py` module docstring (~lines 33–36): "A general vector-to-vector rotation is a
    separate, future addition (see `AbstractMultiVector.rotate`)." — it's no longer future; it's the
    method it points at.
  - `tasks/clarify-2d-only-transforms.md` background says the same ("a general vector→vector rotate is
    a separate future task").

## Plan

- [ ] **CLAUDE.md:** add the two methods to the Operators/Architecture coverage — a short
      "Rotations & rotors" note distinguishing the **general** `AbstractMultiVector.rotate` /
      `rotor_from_vectors` (any plane, any representation) from the **planar 2D** `transforms.rotate` /
      `rotate_90_degrees` / `rotate_around` factories, and flagging the `rotate` name collision.
- [ ] **`transforms.py` module docstring:** change "a separate, future addition" to present tense —
      "implemented as `AbstractMultiVector.rotate` (general, any-plane); the factories here are the
      planar 2D specialization." (Comment-only.)
- [ ] **`tasks/clarify-2d-only-transforms.md`:** reframe. Its core hazard (applying a *planar*
      `transforms.rotate`/`scale_non_uniform_2d` to a G3/Gn value with an e₃⁺ component silently
      produces garbage) is **still valid and still worth doing**. But the "general rotation is future
      work" framing is obsolete — update it to "the general path exists (`AbstractMultiVector.rotate`);
      this task is only about guarding/clarifying the *planar* factories." Adjust its Status note
      accordingly.
- [ ] **Consistency check vs. README:** confirm CLAUDE.md's wording for `rotor_from_vectors` /
      `plane_of_rotation` doesn't contradict the README's graded-subtypes section; align terminology.
- [ ] Verify there's test coverage of the general `AbstractMultiVector.rotate` (`test_multivector.py`
      has a `test_rotate`); if it only covers one representation, note whether a conformance-level
      test belongs in `tasks/transform-type-roundtrip-tests.md` instead (don't expand scope here).
- [ ] `python -m pytest -q` (expect 141; docs/comments don't change it) + `entrypoint/format.sh`.

## Notes / decisions

- Pure documentation/comment task. The only files touched are CLAUDE.md (add), `transforms.py`
  docstring (reword), and a sibling task file (reframe) — no `.py` logic, no regeneration.
- Coordinate with `tasks/refresh-claudemd-known-issues.md` (edits the same CLAUDE.md, adjacent
  sections) — do them together to avoid conflicting edits.
- Don't fold the planar-guard *implementation* into this task; that stays in
  `clarify-2d-only-transforms.md`. This task only fixes the *wording* there.

## Open questions

- Put the rotations note under "Operators" in CLAUDE.md, or as a short subsection under
  "Architecture" (where `rotor_from_vectors`' even-subalgebra rationale fits naturally)?
- Worth a one-line note in README too that the *general* `AbstractMultiVector.rotate` exists (not just
  `rotor_from_vectors`), or is README's current rotor coverage enough?
