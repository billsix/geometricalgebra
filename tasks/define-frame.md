# Define a `frame` (a set/basis of vectors) as a first-class concept

**Status:** in-progress — **Phase 1 (`is_frame` + `make_frame` free functions) approved by Bill
2026-08-23 and is representation-agnostic, so it proceeds now**; the `Frame`-class representation
decision (below) stays open and only gates the later phases. Phase 1 = `are_linearly_independent` +
`is_frame` pass-through + `make_orthogonal_frame` (Bill's rejection method), then a proof that
Hestenes' (same-page, p. 27) orthogonalization is the same. **Parts 1a + 1b IMPLEMENTED 2026-08-23**
in `src/gacalc/frame.py` (+ `tests/test_frame.py`, 10 tests; full suite 380 passed; ruff + ty clean).
**Part 1c — equivalence TESTS DONE 2026-08-23.** `tests/test_frame.py` proves Hestenes'
`c_k = Ã_{k-1} A_k` equals Bill's rejection via `c_k == |A_{k-1}|² · w_k`, symbolic (exact) and numeric,
in 2D and 3D (12 tests; full suite green; ruff + ty clean). The formal *written* proof (prose) is
optional next. **Both methods are now PUBLIC and kept for teaching (Bill, 2026-08-23):**
`make_orthogonal_frame` (rejection) **and** `make_orthogonal_frame_hestenes` (closed-form blade
product), cross-referencing docstrings, equivalence enforced by the tests — deliberately UNLIKE the
archived blade-square-sign task, where one form was optimal and replaced the other. Zero-vector
question resolved (keep the raise). **Generated-classes question: investigated — NO, keep as free
functions (see "Generated classes?" below).**
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

## Phase 1 — the frame predicate + Bill's orthogonalization, then prove Hestenes' equals it

Free functions over a sequence of vectors, **representation-agnostic** (they work whether or not a
`Frame` class later wraps them — this is galgebra's shape too, a bare `Sequence[Mv]` with operations
elsewhere), so Phase 1 proceeds **without** the `Frame`-class representation decision. All primitives
exist in `base.py`: `outer_product_of_vectors` (574, the `a_1 ∧ … ∧ a_k` blade + its `== 0`
dependence test), `reject` (807), `is_orthogonal_to` (615, already `np.isclose`-based), `normalize`
(349), `scalar_product` (475), `magnitude` (324).

### Definitions (corrected to Hestenes & Sobczyk, *Clifford Algebra to Geometric Calculus*)

Hestenes defines a **frame** as a set of vectors whose **wedge across all of them is nonzero** —
`a ∧ b ∧ c ∧ … ≠ 0` — i.e. **linear independence** (NOT orthogonality; oblique frames are normal,
which is the whole point of reciprocal frames). Bill confirmed this from the book 2026-08-23:
**Hestenes & Sobczyk, *Clifford Algebra to Geometric Calculus*, page 27** — where both the frame
definition (wedge nonzero) and the orthogonalization (Part 1c) appear.

### Part 1a — the predicate

- **`are_linearly_independent(vectors)` → bool** — tests `outer_product_of_vectors(vectors) != 0`
  (the wedge across all is nonzero), the Hestenes frame condition. (The wedge tests *joint* linear
  independence, which is exactly what a frame needs.)
- **`is_frame(vectors)` → bool** — a **pass-through** to `are_linearly_independent`. A frame *is* a
  linearly independent set.

### Part 1b — orthogonalization, Bill's way FIRST

Implement **Bill's** rejection method (not Hestenes' formula — that comes in 1c): keep the first
vector as-is; each subsequent `w_{k+1}` is `v_{k+1}` with the span of the previous vectors rejected
out, as sequential rejection `reject(reject(… reject(v_{k+1}, w_1) …), w_k)` (equals rejecting the
span blade, since the `w_j` are already mutually orthogonal). The function is **`make_orthogonal_frame(vectors)`**.
Precondition: the input **is a frame** (`is_frame` true); a non-frame input **raises** (checked via
`is_frame` / `are_linearly_independent` up front). **Orthogonal, not orthonormal** — original lengths
kept; an `orthonormalize` (`normalize` each result) is a later follow-up. Post-condition, worth a small
`is_orthogonal_frame` helper to state/test: the result is mutually orthogonal AND still a frame.

### Part 1c — prove Hestenes' orthogonalization equals Bill's — UNBLOCKED 2026-08-23 (definition in hand)

**Hestenes' p. 27 orthogonalization, transcribed by Bill (H&S eqs 3.1–3.2):**

- **(3.1)** `A_0 := 1` (scalar), `A_1 := v_1`, `A_2 := v_1 ∧ v_2`, …, `A_k := v_1 ∧ v_2 ∧ … ∧ v_k` —
  the outer product (k-blade) of the first k frame vectors, so `A_k = A_{k-1} ∧ v_k`. (In gacalc:
  `outer_product_of_vectors` of the length-k prefix; the frame condition is `A_k ≠ 0` for every k.)
- **(3.2)** `c_k := Ã_{k-1} A_k` — the **reverse** of the previous blade times the current blade
  (geometric product). The `{c_k}` are the orthogonal frame.

(Equation numbers per Bill's transcription of p. 27, 2026-08-23. H&S 3.3 is a separate result, not
used here.)

**Why this equals Bill's rejection method (the proof crux).** Because `A_k = A_{k-1} ∧ v_k`, and
wedging a blade with a vector keeps only the part of `v_k` *orthogonal* to that blade's subspace — and
for that orthogonal part the wedge equals the geometric product — we have `A_k = A_{k-1} ∧ v_k =
A_{k-1} v_k^⊥`, where `v_k^⊥` is exactly the **rejection of `v_k` from span(v_1…v_{k-1})** — Bill's
`w_k` (what `make_orthogonal_frame` computes). Therefore

>   `c_k = Ã_{k-1} A_k = Ã_{k-1} A_{k-1} v_k^⊥ = |A_{k-1}|² · v_k^⊥`,

since `Ã_{k-1} A_{k-1} = |A_{k-1}|²` is a **positive scalar**. So **`c_k` = Bill's rejection `w_k`
scaled by the positive scalar `|A_{k-1}|²`** (and `c_1 = v_1 = w_1` exactly, as `|A_0|² = 1`). The two
orthogonalizations give the **same orthogonal directions**, identical up to a positive per-vector
length factor `|A_{k-1}|²` — *exactly* equal only after normalization. So the honest theorem is
**"equal up to a positive scalar per vector," with `c_k = |A_{k-1}|² w_k` the exact relation.** Sanity
check, k=2: `c_2 = v_1(v_1 ∧ v_2) = |v_1|² v_2 − (v_1·v_2) v_1 = |v_1|²·(v_2 rejected from v_1)`, factor
`|v_1|² = |A_1|²`. ✓

**Both orthogonalizations are public, kept for teaching (2026-08-23).** `make_orthogonal_frame`
(rejection / Gram–Schmidt) and `make_orthogonal_frame_hestenes` (`c_k = reverse(A_{k-1}) A_k`, blades
via `outer_product_of_vectors` of the prefix + `.reverse()` + grade-1 narrow) both live in
`src/gacalc/frame.py`, with docstrings that reference each other and state the equivalence. Neither is
"better" — rejection reads as the geometric idea, the blade product as a closed formula — so both stay
(contrast the archived blade-square-sign task, which optimized to one). Note they are NOT identical
outputs: `c_k = |A_{k-1}|² w_k`, so only `c_1 = w_1`; the later `c_k` are longer.

**Equivalence tests — implemented 2026-08-23** (`tests/test_frame.py`): assert
`make_orthogonal_frame_hestenes(vs)[k] == |A_{k-1}|² · make_orthogonal_frame(vs)[k]` — general symbolic
vectors in 2D & 3D (exact) and random vectors in 2D & 3D (`isclose`). **Finding worth keeping:** the symbolic check must compare **`(c_k − |A_{k-1}|² w_k)` is
the zero multivector**, NOT `c_k == …` — `Gn.__eq__` is *structural*, and the two constructions yield
mathematically-equal but structurally-different sympy expressions (a bivector·trivector product vs a
scalar·rejection); `==` returns False while the eager-simplifying subtraction reduces to exact zero.
(The general `==`-based symbolic tests elsewhere in the suite work only because both sides come from
the *same* construction; cross-construction equality needs the subtraction form.)

**TODO — make the symbolic tests fully general (Bill, 2026-08-23) — DONE 2026-09-02
(William Emerison Six <billsix@gmail.com>).** The symbolic tests for **both** orthogonalizations now
run on fully-general `symbol * basis` frames of the full dimension:

- **2D** — `test_orthogonal_frame_2d_symbolic` and `test_hestenes_equals_rejection_2d_symbolic` now
  use gn's module constants `sym_vec2_1` / `sym_vec2_2` directly (they were re-declaring local
  `a_*`/`b_*` symbols).
- **3D** — added `test_orthogonal_frame_3d_symbolic` (first-kept + all-pairs-orthogonal + `is_frame`,
  exact symbolic) and `test_hestenes_equals_rejection_3d_symbolic` (`c_k == |A_{k-1}|² · w_k` for
  k = 1,2,3, exact via the eager-simplifying `(c_k − |A_{k-1}|² w_k) == zero` subtraction) on a
  **complete 3-vector** frame: `sym_vec3_1`, `sym_vec3_2`, and a third general
  `sym_vec3_3 = c_1 e_1 + c_2 e_2 + c_3 e_3`. The concrete readable-number 3D tests are kept
  alongside (the symbolic + concrete teaching pair).

Gate: `tests/test_frame.py` 14 → 16 tests; full suite **441 passed**; ruff + `ruff format --check`
+ `ty check tests` clean (host run; the containerized `make test` gate not run this session).

**Decisions made — open to change (William Emerison Six <billsix@gmail.com>, 2026-09-02):**
1. The third 3D vector is defined **test-local** (`sym_vec3_3` in `test_frame.py`), NOT added to
   `gn.py`'s public surface. Promote it to `gn.py` alongside `sym_vec3_1`/`sym_vec3_2` if it should be
   reusable in notebooks / other tests.
2. Kept the concrete readable-number 3D tests rather than replacing them with the symbolic ones.
3. **Cost note:** the two symbolic 3D tests add ~40 s to the suite (the ~9 s rejection-frame build
   over 9 free symbols dominates — gacalc's slow-but-exact `Gn` path). Trim if that's too much for
   `make test`.

(The TODO's original "current state" description named tests — e.g.
`test_orthogonal_frame_is_a_frame_and_orthogonal_symbolic`, a 3D equivalence test with a hand-made
`v3` — that no longer existed in `test_frame.py`; the file had been reworked so its 3D tests were
concrete. The intent — every symbolic case a general full-dimension frame — was applied to the file
as it actually stood.)

**Proof plan (when Bill greenlights writing the prose):** (i) the formal argument above, tightened — justify
`A_k = A_{k-1} v_k^⊥` (wedge-with-a-blade keeps the orthogonal part; geometric = wedge there) and that
`c_k` is grade 1 and orthogonal to all prior `c_j`; (ii) a **computational cross-check** — implement
Hestenes' `c_k = Ã_{k-1} A_k` (via `reverse` + `outer_product_of_vectors` of the prefix), and assert
`c_k == |A_{k-1}|² · w_k` (with `w_k` from `make_orthogonal_frame`) exactly on symbolic 2D/3D frames,
plus numeric spot checks. Cite H&S p. 27, eqs 3.1–3.2.

**What "different means" actually is, and 1c implementation notes (new understanding, 2026-08-23):**

- **Hestenes' method is closed-form / "parallel"; Bill's is recursive / "sequential."** Each Hestenes
  `c_k = Ã_{k-1} A_k` is computed **directly from the original prefix** `v_1…v_k` (build the blades,
  reverse, multiply) — the `c_k` do not reference each other. Bill's `w_k` is built **from the already-
  orthogonalized** `w_1…w_{k-1}` (sequential rejection). That is the "different means"; the proof
  bridges the two, and `c_k = |A_{k-1}|² w_k` is the exact bridge.
- **`c_k` is a vector (grade 1)** — algebraically `|A_{k-1}|² v_k^⊥`. In code the raw geometric product
  `Ã_{k-1} A_k` may carry an identically-zero higher-grade term (the same container-widening `reject`
  guards against), so the cross-check should take `.r_vector_part(1)` of it, exactly as `base.reject`
  narrows.
- **The scalar factor is `A_{k-1}.magnitude_squared()`** (`= Ã_{k-1} A_{k-1}`, gacalc `base.py:~347`) —
  so the cross-check asserts `r_vector_part(1)(reverse(A_{k-1}) * A_k) == A_{k-1}.magnitude_squared() * w_k`.
  Blades come from `outer_product_of_vectors(*vectors[:k])`; reverse from `.reverse()`.
- **After normalization the two frames are *identical*** (the factor `|A_{k-1}|² > 0` preserves
  direction and sign), which is why the honest theorem is "equal up to a positive scalar per vector"
  and why a later `orthonormalize` makes Hestenes' and Bill's frames literally coincide.
- **Recursive volume relation** (falls out, may help the proof): `|A_k|² = |A_{k-1}|² · |v_k^⊥|²`, so
  `|A_k|² = ∏_{j≤k} |w_j|²` — the squared volume of the parallelotope is the product of the orthogonal
  heights, the GA statement of Gram-determinant / Hadamard.

**Note (secondary sources, for context):** GA orthogonalization is rejection-based (perpendicular
component `a∧B / B`, i.e. gacalc's `reject`, already cited to H&S **p. 18**); the section is 1-3
"Frames and Matrices". The exact p. 27 statement above is Bill's transcription (the book is
borrow-walled online, so it could not be fetched — the primary source is Bill's copy).

**Placement:** module-level free functions over `MultiVectorBase` vectors — a new
`src/gacalc/frame.py` (or alongside the vector ops in `base.py`); decide when implementing.

**Verify:** unit tests for `is_frame` on independent vs dependent sets (2D/3D, numeric + symbolic);
`is_frame(make_orthogonal_frame(vs))` and orthogonality of the result; the raise on a non-frame input;
the equivalence cross-check (1c); ty clean (src/tests/tools); generator deterministic; doc-regions OK;
`make format` green.

### Phase-1 decisions (all settled 2026-08-23, Bill)

1. **Independence-predicate name → `are_linearly_independent`** (with `is_frame` a pass-through to it).
2. **Orthogonalizer name → `make_orthogonal_frame`.**
3. **Non-frame input → raise** (precondition `is_frame` violated; Hestenes orthogonalizes frames).
4. **Citation → Hestenes & Sobczyk, *Clifford Algebra to Geometric Calculus*, page 27** — the frame
   definition and the orthogonalization are both there. Cite p. 27 in 1c and the docstrings.

### Implementation notes — Parts 1a + 1b (done 2026-08-23)

`src/gacalc/frame.py` (representation-agnostic free functions over `MultiVectorBase`) + `tests/test_frame.py`.
- **`are_linearly_independent(vectors, float_close_to_zero=False)`** — `outer_product_of_vectors(*vectors) != zero`
  (exact by default; tolerant `np.isclose` on the blade magnitude when `float_close_to_zero`, mirroring
  `is_orthogonal_to`). **`is_frame`** is a one-line pass-through.
- **`make_orthogonal_frame(vectors)`** — **iterative** rejection (`reject` one prior vector at a time),
  chosen over blade rejection because gacalc's `reject` only implements grade-1/grade-2 spans, so
  rejecting from a 3-vector (trivector) span would hit its `raise`; the pairwise chain only ever rejects
  from a single vector and is equal since the priors are mutually orthogonal. First vector returned
  unchanged; orthogonal, not orthonormal. Raises `ValueError` on a dependent (non-frame) input.
- **Refinements made while implementing:** a **non-vector** member (e.g. a bivector) **raises `ValueError`**
  (a category error, not "a dependent frame" — Bill's steer 2026-08-23); an **empty** sequence returns
  `False`. Tests cover independent/dependent 2D & 3D, oblique frames, symbolic exact orthogonality,
  numeric 3D orthogonality, first-vector-unchanged, and both raises.
- Gates: 10 new tests pass; full suite **380 passed**; ruff + `ruff format --check` + ty all clean.

**Zero-vector handling — RESOLVED (Bill, 2026-08-23): keep the raise.** A zero vector in a frame is
almost certainly a bug worth surfacing loudly; a caller expecting possibly-zero vectors checks first.
So a zero member (not `is_vector()` in gacalc) raises `ValueError` like any other non-vector — matching
the current implementation.

### Generated classes? — investigated 2026-08-23 (Bill asked): NO

Should any of Phase 1 be added to the **generated** per-algebra classes (`g1`/`g2`/`g3`, via
`tools/gen_specialized.py`)? **No — keep them as representation-agnostic free functions in `frame.py`.**

- **The generator specializes single-multivector arithmetic, not collection algorithms.** It *runs `Gn`
  on sympy symbols* and compiles the closed-form formula for a per-type operation (`a*b`, `a.reject(B)`,
  result-type overloads). The frame functions take a **`Sequence` of vectors** and return a **`list`** —
  a control-flow algorithm (loop of rejections), not a closed-form arithmetic method the generator can
  partial-evaluate. Wrong shape for codegen.
- **They add no per-class capability — they compose primitives that already exist.**
  `outer_product_of_vectors`, `reject`, `reverse`, `magnitude_squared`, `is_vector`, `is_orthogonal_to`
  are already on base/the generated types. Generating a `g2`- and a `g3`-specific copy of `is_frame` /
  `make_orthogonal_frame` would be pure duplication with zero speed or type benefit; one implementation
  over `MultiVectorBase` already works for `Gn`, `g2`, and `g3`. This matches the settled Phase-0
  decision (representation-agnostic free functions) and galgebra's shape.
- **The one real adjacent improvement is TYPE precision, and it is NOT a codegen task.**
  `make_orthogonal_frame(list[Vector3])` currently returns `list[MultiVectorBase]` statically (runtime
  elements *are* `Vector3`, since `reject` narrows to `type(value)`). Making it return `list[Vector3]`
  would be a plain `TypeVar`-generic signature — but it can only be *sound* once `reject`/the transform
  layer report the concrete type, which is exactly `tasks/precise-typing-remaining-methods.md` /
  [[generated-product-typing]]. So park frame type-precision under that task, not here, and not as
  generated code.

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
