# Define a `frame` (a set/basis of vectors) as a first-class concept

**Status:** proposed — needs a **representation decision from Bill** before implementation (see below).
**Priority:** 4
**Difficulty:** 7
Created 2026-07-22. Prerequisite for reciprocal frames / outermorphisms / geometric calculus — see
`tasks/reference/galgebra-comparison.md` (Findings 1, 3b, 5).

## Goal

Introduce a **frame** — an ordered set of vectors `{a_1, …, a_k}` spanning a subspace (a basis when
`k = n`) — as a named concept gacalc can build, orthogonalize, and (later) take the reciprocal of.
Today gacalc has only the *implicit* standard basis (`basis_vector(i)` and the class constants
`Vector2.e_1` …); there is no object for "an arbitrary set of vectors" you can operate on as a unit.

## Motivating example (Bill)

Create a frame from a set of vectors and **orthogonalize / orthonormalize** it *the Hestenes way* —
Gram–Schmidt expressed with the **rejection** operator, not coordinates: each new vector has the
span of the previous ones rejected out of it (`reject`), optionally then `normalize`d.
gacalc already has the pieces: `base.reject` (orthogonal component), `base.normalize`,
`base.is_orthogonal_to`, `base.outer_product_of_vectors` (the span as a blade,
`a_1 ∧ … ∧ a_k`, and its `== 0` linear-dependence test). So `Frame.orthogonalize()` is essentially
"fold `reject` over the vectors." (Pin the exact Hestenes & Sobczyk page for the orthogonalization
when implementing — do not cite a page unverified.)

## The representation decision (OPEN — Bill's call; blocks everything else)

How should a frame be represented? Sketch of the options, trade-offs to weigh:

- **A plain `tuple[Vector, …]`** — no new type; lightweight; but nowhere to hang
  `orthogonalize`/`reciprocal`/`is_orthonormal`, and no distinction from "just some vectors."
- **A dedicated `Frame` class** — holds the ordered vectors; carries `orthogonalize()` /
  `orthonormalize()` / (later) `reciprocal()` / `pseudoscalar()` (`= a_1 ∧ … ∧ a_k`). Most room to
  grow toward reciprocal frames + linear operators. Question: generated per-algebra (like the value
  types) or one representation-agnostic class over `MultiVectorBase` vectors?
- **The span blade `a_1 ∧ … ∧ a_k` alone** — compact and natural for "the subspace," but **loses the
  individual vectors and their order**, which the reciprocal frame and any coordinate/linear-map use
  need. So a blade can be *derived from* a frame but probably can't *be* the frame.

**Recommendation to seed the discussion (not a decision):** a `Frame` class holding the vectors,
because the downstream goals (reciprocal frames, linear operators, easier inverses) all need the
individual vectors + metric, which a bare blade throws away.

## Subtask — codebase sweep (BLOCKED on the representation decision above)

**Once the representation is chosen, read the whole codebase to see what should change or integrate
with it** — do not start this before the decision, since the answers depend on the representation.
Things to look at (non-exhaustive, to be filled in during the sweep):

- Should the existing **class constants / `basis_vector`** be reframed as (or produce) a standard
  `Frame`?
- Do **`project` / `reject` / `reflect`** (which already accept a `[*sequence]` of vectors →
  `outer_product_of_vectors`) gain a frame overload, or subsume that sequence handling?
- Does the **transform layer** (`transforms.py`, rotors, `to_matrix`) want to express itself via
  frames?
- Where does **orthogonalization** belong (on `Frame`, or a free function), and does anything already
  do it ad hoc?
- Naming/typing consistency with the rest of the library (generated vs base, `Self` vs
  `MultiVectorBase`, doc-regions if generated).

Produce the sweep findings as a checklist here (or promote big ones into their own tasks).

## How galgebra does it (design reference only — NOT code to lift)

Read from galgebra 0.6.0 source for *ideas*, to adapt to gacalc's style — not to copy:

- **A frame is just a bare `Sequence[Mv]`** — galgebra has **no standalone `Frame` class**. It's a
  Python list of vector multivectors; the operations live on the algebra object (`Ga`), not on a
  frame type. (A data point for the representation decision above: galgebra chose "plain tuple +
  methods elsewhere," and it works — though it means the frame carries no behaviour of its own.)
- **Reciprocal frame via the pseudoscalar** (`Ga.ReciprocalFrame(basis, mode='norm')`) — exactly the
  "inverse without RREF" idea. It builds the frame's pseudoscalar `E = v_1 ∧ … ∧ v_n`, then each
  reciprocal vector `vⁱ = (−1)ⁱ (v_1 ∧ … skip i … ∧ v_n) · E`, normalized by `E²` so
  `vⁱ · v_j = δⁱ_j`. `mode='append'` returns `E²` separately instead of dividing (keeps things exact
  / factored). `Ga.mvr()` is the same for the algebra's own basis. **This is the mechanism Bill's
  "better than RREF" intuition points at** — coordinates/inverses come from wedges and the
  pseudoscalar, no row reduction.
- **Linear transform = outermorphism, defined by a frame** (`lt.py`, `class Lt`) — stored as
  `lt_dict = {basis vector eᵢ → image vector}`, i.e. *a linear map is fixed by where it sends a
  frame*, then extended to the whole algebra by `f(a ∧ b) = f(a) ∧ f(b)`. (A rotor/reflection is the
  special "versor" case: `f(a) = V a V⁻¹`.) The GA payoffs galgebra exposes and gacalc lacks:
  **det = how the map scales the pseudoscalar** (`f(I)/I`), **adjoint** via the reciprocal frame, and
  the **inverse** built from those — no matrices, no RREF. This is the concrete shape of "linear
  operations, my own way," and it sits directly on top of frames + reciprocal frames.

## Future directions (Bill's side notes — downstream, NOT in this task's scope)

- **GA-native linear operators** — "linear operations like matrix algebra, but my own way." This is
  the **outermorphism / `Lt`** territory (`galgebra-comparison.md` Finding 3b, roadmap #4): a linear
  map defined on vectors, extended to the whole algebra by `f(a ∧ b) = f(a) ∧ f(b)`. Frames +
  reciprocal frames are the substrate (`f(x) = Σ f(a_i) (a^i · x)`).
- **Inverses without RREF** — Bill's intuition that GA gives a cleaner inverse than reduced-row-
  echelon. In GA a linear map's inverse comes from its **adjoint and how it scales the pseudoscalar**
  (`det = f(I)/I`; `f⁻¹` via the reciprocal frame / outermorphism), no row reduction. Worth its own
  task once frames + reciprocal frames + outermorphisms exist; capture the "better than RREF" idea
  then. A `tasks/reference/` domain note on frames/reciprocal-frames/outermorphisms may be worth
  creating at that point.

## Relationships

- `tasks/reference/galgebra-comparison.md` — Findings 1 (frames/metric), 3b (outermorphisms), 5;
  roadmap rows "reciprocal frames" and "outermorphisms / general linear transforms."
- Building blocks already present: `base.reject`, `base.normalize`, `base.outer_product_of_vectors`,
  `base.is_orthogonal_to`, `base.basis_vector`.
