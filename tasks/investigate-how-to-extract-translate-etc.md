# Make the transforms (translate/rotate/scale/compose) work with G1/G2/G3

**Status:** implementation complete — pending user review
**Started:** 2026-06-04 · **Implemented:** 2026-06-04

## Goal

The `InvertibleFunction` transform layer in `gn.py` — `translate`, `uniform_scale`,
`scale_non_uniform_2d`, `rotate`, `rotate_around`, `compose`, … — is hardwired to the general `Gn`
representation: the factories close over the module-level `Gn` basis constants, so feeding a `G2`
value in coerces the result back to `Gn`. We want these transforms to be **representation-preserving**
— given a `G2`, return a `G2`; given a `G3`, return a `G3` — so the specialized notebooks (and users
of the fast classes) can use them. Study the code thoroughly, lay out the candidate approaches
(generalize the layer to be representation-agnostic; have the generator emit per-class transforms;
or a better third option), weigh the tradeoffs, and **recommend one choice** with justification.
Deliverable for this task is the plan + decision; implementation is a follow-up.

## Findings (code study, 2026-06-04)

The representation-binding is **much narrower than it looks.** I categorized every function in the
transform layer (`gn.py:190–615`) and verified with a runtime experiment (a `G2` vector through each):

| Function | Bound to `Gn`? | Why |
| --- | --- | --- |
| `InvertibleFunction` (class) | **No** | pure wrapper of func/inverse/latex; type hints only |
| `inverse(f)` | **No** | swaps func/inverse |
| `compose`, `compose_intermediate_fns`, `compose_intermediate_fns_and_fn` | **No** | pure plumbing over `InvertibleFunction`s |
| `identity()` | **No** | returns input unchanged (type-preserving) |
| `uniform_scale(m)` | **No** | `vector * m` — scalar, no basis. **Verified: `G2`→`G2`.** |
| `translate(b)` | **No*** | `vector + b`; type follows `b`. **Verified: `translate(G2)`→`G2`, `translate(Gn)`→`Gn`.** |
| `rotate_90_degrees()` | **Yes** | bakes `rot_90 = e_1 * e_2` from the **module-level `Gn`** constants |
| `rotate(angle)` | **Yes** | built on `rotate_90_degrees()` |
| `rotate_around(angle, center)` | **Yes** | built on `rotate` |
| `scale_non_uniform_2d(mx,my)` | **Yes** | `MultiVector.project(onto=e_1)` with the **`Gn`** `e_1`/`e_2` |
| `is_clockwise` / `is_counter_clockwise` | **Yes** | `project(onto=e_1*e_2)` + `rotate_90_degrees()` (returns bool, lower stakes) |

So the *entire* problem is: **a handful of factories bake in `Gn` basis constants** (`e_1`, `e_2`,
`e_1*e_2`). `translate`/`uniform_scale` already preserve type — the notebook "bug" is only that we
fed them arguments built from `gn.e_1` (a `Gn`) instead of `g2.e_1` (a `G2`).

Separately, there is **already a second, representation-agnostic transform system** on the ABC
(`base.py`): `project`, `reject`, `reflect`, `identity`, and an angle-free `rotate(from_vec, to_vec)`
are classmethods returning a plain `MultiVectorFn` (a bare callable). They preserve the concrete
type, but have **no latex / `compose` / `inverse`** — unlike the `gn.py` `InvertibleFunction` layer.
That duality (rich `InvertibleFunction` in `gn.py` vs. plain `MultiVectorFn` classmethods in
`base.py`) is the main design tension any fix has to reconcile.

~~Constraint from `CLAUDE.md`: the `InvertibleFunction` layer is **shared with the author's
`modelviewprojection` book project**, so the fix should keep that layer portable.~~ **Dropped
(decided 2026-06-04):** the user confirmed `modelviewprojection`'s constraints do not matter for
this work, so we are free to entangle/relocate the layer however is cleanest here. (This removes the
main argument that had counted against Options B/C; we still chose A on its own merits — see below.)

## Options & tradeoffs

### Option A — Generalize: resolve the basis from the input value's type at call time
Keep one shared `InvertibleFunction` layer; change only the ~3 bound factories so they derive their
basis vectors from `type(vector)` (via the interchange protocol, e.g. `type(vector).from_blade_dict(
{(1, 2): 1})` or a basis classmethod) **inside** `f(vector)` instead of closing over module-level
`Gn` constants. `translate`/`uniform_scale`/`compose`/`inverse`/`identity` are untouched (already
generic); the caller just supplies `b` of the desired type for `translate`.
- **Pros:** smallest change (touches `rotate_90_degrees`, `scale_non_uniform_2d`, `is_clockwise`);
  zero duplication; works for `Gn`, `G1/G2/G3`, **and any future `G4`** with no generator changes;
  keeps the shared layer intact and portable; consistent with the existing interchange-protocol
  design philosophy.
- **Cons:** transforms become "basis-late-bound" — slightly less obvious than a baked constant; a
  transform built before it ever sees a value can't know its dimension (fine for these — they defer
  to call time); mixed-type pipelines (e.g. a `Gn` `b` with a `G2` input) still coerce, so it's a
  convention the caller must follow (document it). `scale_non_uniform_2d` is inherently 2D — keep its
  name/scope or generalize to `scale_non_uniform(*factors)`.

### Option B — Generator copies the transforms into each `g*.py`
`tools/gen_specialized.py` emits per-class `translate`/`rotate`/`scale`/… bound to that module's own
basis constants.
- **Pros:** each module fully self-contained; `g2.rotate` uses `g2.e_1` with no indirection.
- **Cons:** **heavy duplication** — `compose`/`inverse`/`InvertibleFunction`/`compose_intermediate_fns`
  have *zero* representation dependence, so copying them per module is pure waste and a maintenance
  hazard; the generator gets materially more complex; the per-class copies drift from the shared
  `modelviewprojection` layer; you'd still only *need* per-class versions of the 2–3 bound functions,
  so most of the copy is dead weight. Worst on DRY.

### Option C — Promote the transforms to ABC classmethods (unify with the existing system)
Add `translate`/`uniform_scale`/`scale_non_uniform`/`rotate(angle)` as classmethods on
`AbstractMultiVector`, alongside the existing `project`/`reflect`/`rotate(from,to)`, so
`G2.translate(...)` returns a type-preserving transform.
- **Pros:** one definition, generic by construction (`cls` gives the right basis); consolidates the
  two transform systems into one; naturally type-preserving.
- **Cons:** the ABC versions today return bare `MultiVectorFn` with **no latex/compose/inverse**;
  to keep the notebook/book ergonomics you'd have to either (a) make the classmethods return
  `InvertibleFunction` — which pulls the book-shared `InvertibleFunction` type into `base.py`,
  entangling the GA core with the shared layer — or (b) accept losing latex/compose for specialized
  use. Bigger surface change; touches the shared-layer boundary.

### Option D — Minimal/pragmatic (subset of A)
Do nothing structural: just **pass the right-typed basis** when building transform arguments
(`translate`), and for the genuinely-bound `rotate`/`scale_non_uniform_2d` either (a) accept they
return `Gn` for now, or (b) use the ABC `rotate(from,to)` classmethod where a rotation is needed.
- **Pros:** near-zero code change; unblocks `translate`/`uniform_scale` immediately.
- **Cons:** leaves `rotate(angle)`/`scale_non_uniform_2d` `Gn`-bound (the actual ask unaddressed);
  perpetuates the two-systems split. A stopgap, not a real fix.

## DECISION (settled 2026-06-04)

**Go with Option A + both refinements.** Confirmed by the user. The `modelviewprojection` portability
constraint is explicitly **dropped** and did not drive the choice.

Why A still wins even without the shared-layer constraint:
- It is the **smallest correct change** — only ~3 factories (`rotate_90_degrees`,
  `scale_non_uniform_2d`, `is_clockwise`/`is_counter_clockwise`) actually bake in `Gn` basis
  constants; everything else (`translate`/`uniform_scale`/`compose`/`inverse`/`identity`) already
  preserves type. We verified this empirically.
- **No duplication and no generator changes** — Option B would copy pure plumbing
  (`compose`/`inverse`/`InvertibleFunction`) into every `g*.py`, which is dead weight regardless of
  the book.
- **Scales to any algebra** (`Gn`, `G1/G2/G3`, future `G4`) for free, because the basis is resolved
  from `type(vector)` via the interchange protocol that already underpins the whole design.
- Option C (unify into ABC classmethods) remains a legitimate larger refactor, but it's a bigger
  surface change and we are deliberately **not** merging the two transform systems in this task.

## Recommendation (now the decision)

**Option A** with two refinements — directly satisfies "given a `G2`, output a `G2`" with the least
code, no duplication, and no generator work, and scales to every present and future algebra.

Refinements (both accepted):
1. **Relocate the representation-agnostic transform layer out of `gn.py`.** `InvertibleFunction`,
   `inverse`, `compose`, `identity`, `translate`, `uniform_scale`, and the generalized
   `rotate`/`scale` don't belong to `Gn` specifically — move them to a new
   `src/geometricalgebra/transforms.py` (or `base.py`) so importing them doesn't drag in `Gn`, and
   re-export from `gn.py` for backward compatibility. (Optional but clarifying; can be a later step.)
2. **Add a basis accessor to the interchange protocol** so the bound factories have a clean way to
   ask a type for its basis vector — e.g. reuse `type(vector).from_blade_dict({(i,): 1})`, or add a
   tiny `cls.basis_vector(i)` / `cls.unit_pseudoscalar()` helper (the latter already exists). This
   keeps `rotate_90_degrees`/`scale_non_uniform_2d` readable.

Keep Option C's ABC `rotate(from,to)` as-is (it's a different, useful rotation); do **not** merge the
two systems in this task — that's a larger refactor and risks the shared-layer boundary.

## Plan

- [x] Study `gn.py` transform layer + `base.py` ABC transforms; categorize representation-binding.
- [x] Verify empirically which transforms already preserve `G2` vs. coerce to `Gn`.
- [x] **Decision: Option A + both refinements** (relocate the layer; add a basis accessor). Settled
      2026-06-04; `modelviewprojection` constraint dropped.
- [x] Add a clean basis accessor on the ABC: `AbstractMultiVector.basis_vector(i)` (base.py); also
      DRYs `unit_pseudoscalar`/`bases` to use it.
- [x] Rewrite the basis-bound factories to resolve basis from `type(vector)` at call time; left
      `translate`/`uniform_scale`/`compose`/`inverse`/`identity` as-is:
  - [x] `rotate_90_degrees` / `rotate` / `rotate_around` — **kept 2D-specific** (planar `e_1∧e_2`),
        now type-preserving for 2D inputs (verified `G2`→`G2`).
  - [x] `scale_non_uniform_2d` → **generalized** to n-D `scale_non_uniform(*factors)`; kept
        `scale_non_uniform_2d` as a thin 2D back-compat wrapper (verified `G3` 3-axis scale).
  - [x] `is_clockwise` / `is_counter_clockwise` — 2D, resolve basis from `type(vector)`.
- [x] Relocated the agnostic layer to **`src/geometricalgebra/transforms.py`**, re-exported from
      `gn.py` (back-compat for `from geometricalgebra.gn import translate, ...`) — **same change.**
- [x] Fixed the broken transform doctests (they imported `modelviewprojection.mathutils`) — rewrote
      to import from `geometricalgebra.transforms` with correct numeric examples; **31 doctests pass.**
      (Addresses `tasks/cleanups-and-hygiene.md` item #1 for these functions.)
- [ ] **TODO (split out): add unit tests** asserting each transform round-trips type + value checks.
      → tracked in **`tasks/transform-type-roundtrip-tests.md`**.
- [ ] **TODO (split out): demo the 2D `rotate` / n-D `scale` in the G2 notebook** → folded into the
      porting plan **`tasks/port-displaymv-2d-to-displayg2.md`** (Tier 1).

### Implementation summary (2026-06-04)

- **New:** `src/geometricalgebra/transforms.py` — the representation-agnostic layer
  (`InvertibleFunction`, `inverse`, `compose`, `compose_intermediate_fns[_and_fn]`, `identity`,
  `translate`, `uniform_scale`, `scale_non_uniform`, `scale_non_uniform_2d`, `rotate_90_degrees`,
  `rotate`, `rotate_around`, `is_clockwise`, `is_counter_clockwise`). Imports only `base`.
- **`base.py`:** added `basis_vector(i)` classmethod; `unit_pseudoscalar`/`bases` now use it.
- **`gn.py`:** removed the transform layer (lines ~188–615) and the now-unused `import math`;
  re-exports the transform names from `transforms`.
- **`nbplotutils.py`:** broadened `cosine`/`sine` to `AbstractMultiVector` (transform results are now
  ABC-typed); dropped the now-unused `MultiVector` import.
- **Verification:** 118 tests pass; `ty check src` + `ty check tests` clean; ruff clean on all source;
  31 transform doctests pass; all three notebooks (`displaymv`, `displayg2`, `displayg3`) execute
  exit 0; smoke test confirms `G2`/`G3` in → same type out for every transform, with correct values
  (e.g. rotate π/2 of 3e₁+4e₂ → −4e₁+3e₂).

## Notes / decisions

- **2026-06-04 — `modelviewprojection` constraint dropped** (user): its constraints don't matter for
  this work. This removed the strongest argument against B/C, but A still won on its own merits
  (smallest change, no duplication, no generator work, scales to all algebras). See DECISION above.
- **2026-06-04 — Decision: Option A + both refinements** (relocate the agnostic layer to its own
  module; add a basis accessor to the interchange protocol). Implementation is the follow-up task.
- Thought process / scope reminder: only `rotate_90_degrees`, `scale_non_uniform_2d`, and
  `is_clockwise`/`is_counter_clockwise` truly need editing; the rest of the layer is already generic.
  Do **not** merge the two transform systems (ABC `MultiVectorFn` vs `InvertibleFunction`) here — out
  of scope, larger refactor.
- **2026-06-04 — relocation in the same change** (user): the move to `transforms.py` ships together
  with the generalization, not as a separate commit.
- **2026-06-04 — rotation stays 2D** (user): `rotate`/`rotate_90_degrees`/`rotate_around` are
  inherently planar; keep them as **2D-assuming** transforms (type-preserving for 2D via
  `type(vector)`), not generalized to n-D. A **general vector-to-vector rotate is a future task**
  the user will add (relates to ABC `rotate(from,to)`). Notebook rotation demo → G2 only.
- **2026-06-04 — generalize scale** (user): turn `scale_non_uniform_2d` into n-D
  `scale_non_uniform(*factors)` (basis from `type(vector)`); keep `scale_non_uniform_2d` as a thin
  2D wrapper for back-compat.

## Open questions (all resolved 2026-06-04)

- ~~Option A vs C?~~ **Resolved: Option A + both refinements.**
- ~~Relocate to `transforms.py`?~~ **Resolved: yes, and do it in the SAME change as the
  generalization** (not a separate commit). Re-export from `gn.py` for back-compat.
- ~~Rotation: generalized `rotate(angle)` vs ABC `rotate(from,to)` in the notebooks?~~ **Resolved:**
  the angle-based `rotate` / `rotate_90_degrees` / `rotate_around` are **inherently 2D** — treat them
  as **2D-specific transforms that assume a 2D type** (they operate in the `e_1∧e_2` plane). They
  should still be representation-preserving for 2D (a `G2` in → a `G2` out, resolving basis from
  `type(vector)`). A **general vector-to-vector rotation is a SEPARATE FUTURE TASK** the user will
  add later (extends/relates to the existing ABC `rotate(from_vec, to_vec)`) — **out of scope here.**
  → In the notebooks: demo the 2D angle `rotate` in the **G2** notebook only; **hold off on rotation
  in the G3 notebook** until the general rotate exists.
- ~~Generalize `scale_non_uniform_2d` to n-D?~~ **Resolved: yes — generalize** to
  `scale_non_uniform(*factors)` resolving basis from `type(vector)`, so it works in any dimension.
  Keep a 2D-compatible entry point (`scale_non_uniform_2d`) as a thin wrapper / back-compat alias.
