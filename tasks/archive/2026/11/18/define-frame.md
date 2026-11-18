# Define a `frame` (a set/basis of vectors) as a first-class concept

**Completed:** 2026-11-18 (William Emerison Six <billsix@gmail.com>; the last two parts were done
in the authorized batch `ready-tasks-batch-2026-11-18`)
**Priority:** 6
**Difficulty:** 5
**Created:** 2026-07-22

## Outcome

Frames are first-class in `src/gacalc/frame.py`. The math, the design facts and the proof are in
`tasks/reference/frames-qr-and-reciprocal-frames.md` ("Hestenes' orthogonalization equals
rejection" and "Design facts about `frame.py`"). `tasks/reference/design-decisions.md` holds the two
"why" bullets: free functions rather than generated methods, and three orthogonalizations kept on
purpose.

The work, in order:

1. **Phase 1 (2026-08-23):**
   - `are_linearly_independent` / `is_frame`: the H&S p. 27 definition, a nonzero wedge;
   - `make_orthogonal_frame` (sequential rejection, the maintainer's method) and
     `make_orthogonal_frame_hestenes` (`c_k = Ã_{k-1} * A_k`, eqs 3.1–3.2), with equivalence tests.

   Decisions (William Emerison Six <billsix@gmail.com>, 2026-08-23):
   - the names above;
   - a non-frame, zero or non-vector input raises `ValueError`;
   - cite H&S p. 27;
   - keep both methods public for teaching;
   - no generated-class copies.

   The symbolic tests were made fully general in 2D and 3D (2026-09-02). Later they became
   parallelism checks, and an exact inverse-based sibling was added
   (`tasks/archive/2026/10/29/hestenes-orthogonalize-test-parallelism.md`, `…-via-inverse.md`).
2. **Representation (2026-11-04):** the `Frame` dataclass, built from a tuple, with the orthogonal
   set, the QR coefficients, the reciprocal frame and `to_invertible_function`
   (`tasks/archive/2026/11/04/frame-class-orthonormal-invertible-function.md` and its follow-ups).
3. **(b) The codebase sweep (2026-11-18).** Each item the task listed, with its finding:
   - **A standard `Frame` from the basis constants:** declined. `Frame((1 * e_1, 1 * e_2))` already
     says it, and nothing needs a constructor.
   - **`project` / `reject` / `reflect` taking a frame:** already work. They accept a sequence of
     vectors and wedge it, so `v.projected_onto(frame.vectors)` projects onto the frame's span.
     There is no `Frame` overload, because `Frame` is not a `Sequence`; `.vectors` is the tuple.
   - **The transform layer:** already integrated. `frame.to_invertible_function()` is an
     `InvertibleFunction` with `Linearity.LINEAR`, so it composes and
     `to_matrix(F, cls)` gives the frame matrix (checked: `Frame((2 * e_1, 1 * e_1 + 3 * e_2))` gives
     `[[2, 1], [0, 3]]`).
   - **Ad hoc orthogonalization elsewhere:** none. `measure.content_by_rejection` calls
     `make_orthogonal_frame` on a plain sequence, and the frame-QR book notebooks use `Frame`.
   - **Naming and typing:** consistent. `Frame` and the free functions are hand-written and
     representation-agnostic, as decided. Precise element typing (`list[Vector]` in and out) remains
     the `TypeVar` follow-up named in `design-decisions.md`.
4. **(c) The prose proof of eqs 3.1–3.2:** written into the reference doc, by induction
   (`A_k = w_1 * … * w_k`, hence `c_k = |A_{k-1}|² * w_k` and `A_{k-1}⁻¹ * A_k = w_k`). The Python
   form is `tests/test_frame.py`. The Lean form is skipped, because frames in Lean are parked
   (`tasks/lean-frame-coverage.md`).

## Left for later (not in this task)

These are downstream, as galgebra shows: GA-native linear operators (outermorphisms defined by
where a frame goes), and inverses from the adjoint and the pseudoscalar scale, without row
reduction. `tasks/reference/galgebra-comparison.md` (Findings 1, 3b and the roadmap) holds the design
notes. `tasks/frame-svd-investigation.md` is the open frame follow-up.
