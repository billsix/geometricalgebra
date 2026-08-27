# Generalize reject / reflect to higher-grade blades (grade 3+)

**Status:** not started · proposed 2026-06-05 · needs go-ahead (user wants to re-read Hestenes first)
**Priority:** 5
**Difficulty:** 4

## Goal

`MultiVectorBase.reject` and `.reflect` (in `base.py`) currently only implement the case where the
blade argument is a **vector or a bivector**. Any higher-grade blade falls through their `match` to
`case _: raise Exception("TODO - implement project for ...")`. This surfaced while fixing the
sequence-arity bug (see `tasks/archive/2026/06/05/correctness-bugs.md`): a 3-element span
(`reject(away_from=[e_1, e_2, e_3])`) reduces via `outer_product_of_vectors` to the trivector
`e_123`, which then hits the unimplemented branch. Goal: support rejection/reflection across a blade
of **any grade** (at least up to the pseudoscalar of `Gn`/`G3`).

## Reference (Hestenes & Sobczyk, *Clifford Algebra to Geometric Calculus*)

- **Page 18, equations 2.9a / 2.9b / 2.9c** — projection of a vector onto a blade (already cited in
  `base.py` for `project`; rejection is the complementary part, also cited "page 18").
- **Key observation:** the formulas are already grade-general:
  - projection  `P_B(a) = (a · B) B⁻¹`
  - rejection   `P_B^⊥(a) = (a ∧ B) B⁻¹`
  These don't depend on `grade(B)`. `project` already works for any homogeneous blade (its
  `is_r_vector()` branch handles grade r), so it likely needs no change. The restriction lives only
  in `reject`/`reflect`'s `match` arms.
- **Restated 2026-08-22 (William Emerison Six <billsix@gmail.com>):** *"project and reject in G3 and
  above should be able to project onto a bivector, or any r-vector type — look at base."* Two axes,
  both to be covered here: (a) the blade argument (`onto`/`away_from`) may be any r-vector, not just
  vector/bivector — this is the `match`-arm restriction above; and (b) the **value** being
  projected/rejected may itself be any r-vector, not only a grade-1 vector. Today `reject`'s inner
  `r()` and `reflect`'s inner `r()` both `assert value.is_vector()` and narrow via
  `r_vector_part(1)` — that grade-1 hardcoding is the (b) restriction (`base.py` ~lines 814-826,
  864-868). `project`'s `fn` already handles a general r-vector value (it computes
  `r = max(grades)` and narrows to that grade), so (b) is mostly a `reject`/`reflect` gap.
- **To confirm while reading p. 18:** that the `(a∧B)B⁻¹` rejection is valid for an r-blade B of any
  grade, and whether the value being projected/rejected must itself be a vector (current code
  `assert value.is_vector()`) or can be generalized.

## Current behaviour, exercised in G3 (2026-08-22, after `make generate`)

Concrete evidence of exactly what works and what fails today (`value` = the thing being
transformed; `blade` = the `onto`/`away_from`/`across` argument):

| call | result |
|------|--------|
| `project(onto=vector/bivector/trivector)(vector)` | ✓ correct |
| `project(onto=vector)(bivector)`, `project(onto=bivector)(bivector)` | ✓ correct (cross-checked vs `Gn`: `project(e_12)(e_12+e_23) → e_12`) |
| `reject(away=vector)(vector)`, `reject(away=bivector)(vector)` | ✓ correct |
| **`reject(away=trivector)(vector)`** | ✗ `Exception: TODO - implement project for …` — no trivector `match` arm |
| **`reject(away=vector)(bivector)`** | ✗ `AssertionError` — inner `r()` asserts `value.is_vector()` |
| `reflect(...)` | mirrors `reject` (built as `project − reject`): trivector `across` raises, bivector `value` asserts |

**Conclusion — `project` is already done; the gaps are entirely in `reject`/`reflect`:**

- **Axis (a), blade grade** — `reject`/`reflect`'s `match` (`base.py` ~835-845, ~881-889) has arms
  only for `is_vector()` / `is_bivector()`; a trivector (or any grade ≥3) `away_from`/`across` falls
  to `case _: raise`. `project` has no such restriction (its `fn` uses `onto.inverse()` for any
  blade).
- **Axis (b), value grade** — `reject`'s inner `r()` (`base.py` ~814-826) and `reflect`'s inner
  `r()` (~864-868) both `assert value.is_vector()` and narrow via `r_vector_part(1)`, so a bivector
  (or higher) **value** raises. `project`'s `fn` already handles a general r-vector value (computes
  `r = max(grades)` and narrows to that grade — verified correct vs `Gn`).

So the work is: generalize `reject`'s `match` to any homogeneous blade **and** replace its inner
`is_vector()`/`r_vector_part(1)` hardcoding with the value's own grade (mirroring what `project.fn`
already does); `reflect` then follows for free. No `project` code change — only new `project` tests
to lock in the higher-grade cases.

## Plan (to validate against the book)

- [ ] Re-read p. 18 (eq 2.9) and confirm the projection/rejection split holds for an arbitrary blade B.
- [ ] In `reject`: replace the `is_vector()` / `is_bivector()` arms with a single arm accepting any
      homogeneous blade (e.g. `away_from.is_r_vector()`), keeping the `(value.wedge(B)) * B.inverse()`
      body. Drop the `case _:` TODO (or keep it only for non-blade inputs).
- [ ] `reflect` is built as `project - reject`, so it should generalize for free once `reject` does —
      verify, don't assume.
- [ ] Decide whether `assert value.is_vector()` inside the inner functions can be relaxed (does the
      book define projection of a *blade* onto a blade, not just a vector?).
- [ ] Add conformance tests: project/reject/reflect across a trivector (e.g. the `G3` pseudoscalar)
      and across a 3-element vector span; check `project(a) + reject(a) == a` (the decomposition
      identity) for the higher-grade case.
- [ ] `ruff` + `ty check src` + full suite green.

## Reference research (2026-08-22) — galgebra + the literature

The maintainer's memory was right on both counts: **projection is defined for r-vectors / blades**
(and general multivectors), and the *"go re-read Hestenes"* uncertainty is specifically about
**mixed-grade multivector values**, not the homogeneous-higher-grade case.

**galgebra** (`github.com/pygae/galgebra`, local checkout `/mnt/sda1/galgebra/galgebra/mv.py`) is the
concrete precedent:

- **`project_in_blade(self, blade)` (`mv.py:435`)** projects a **general multivector** `self` onto
  any **blade** (any grade): `return (self < blade) * blade_inv` where `blade_inv =
  blade.rev() / blade.qform()`. It uses the **left contraction `<`**, *not* the Hestenes inner
  product. Guard: `blade.is_blade()` and non-null (`qform != 0`); **no restriction that `self` be a
  vector or homogeneous** — mixed grade is fine, because the contraction is linear over grades.
- **`reflect_in_blade(self, blade)` (`mv.py:414`)** reflects a general multivector by
  **grade-decomposing `self`** and applying the graded sandwich per grade: for blade grade `s` and
  value grade `r`, `(-1)^{s(r+1)} · blade · ⟨A⟩_r · blade⁻¹`. It is **not** built as
  `project − reject`.
- **galgebra has no `rejection` method** — only projection and reflection. gacalc's `reject` is its
  own; the rejection `(A ∧ B) B⁻¹` is the complementary part and generalizes the same way
  (contraction/wedge onto an invertible blade).

**Literature:** "Generalized Projection Operators in Geometric Algebra" (arXiv `math/0104159`) gives a
versor-form projection `P_A(X) = ½(X − Ā X A†)` valid for *all* multivectors; standard references
(Dorst/Fontijne/Mann, *GA for Computer Science*) define projection/rejection of a blade onto a blade
via the **contraction**. Consensus: the general operator is well-defined; the clean building block is
the **contraction**, which gacalc already has (`left_contraction` / `<`, see
`tasks/reference/contraction-and-dot-definitions.md`).

### Design decisions this raises (settle before implementing)

1. **Product choice: Hestenes dot vs left contraction.** gacalc's `project.fn` uses `value.dot(onto)`
   (Hestenes inner product), which has the grade-0 quirk and is awkward for scalars/mixed grades.
   galgebra deliberately uses the **left contraction**. For a robust higher/mixed-grade generalization,
   consider switching `project` (and `reject`) to `<` / `wedge` onto an invertible blade — gacalc
   already has both operators. This is the substantive part of the "re-read Hestenes" question.
2. **`reflect` = `project − reject`, or the graded sandwich?** gacalc builds `reflect` as
   `project − reject`; galgebra uses the per-grade sandwich `(-1)^{s(r+1)} B⟨A⟩_r B⁻¹`. These agree
   for a vector across a vector — **verify (don't assume) they agree for general grades**, and if not,
   adopt the graded sandwich (which is the canonical definition).
3. **Blade vs merely-homogeneous guard.** galgebra guards on `is_blade()` (an actual outer product of
   vectors, so invertible), stronger than gacalc's `is_r_vector()` (homogeneous). In 4D+, a
   homogeneous element need not be a blade (e.g. `e_12 + e_34`) and may not be invertible. Decide
   whether the guard should be `is_r_vector` (matches current) or a real blade/invertibility check.

## Related "vectors-only, generalize later" markers (same theme — fold in or spin off)

Beyond `reject`/`reflect`, several methods carry the same `assert …is_vector()` + "probably defined
more generally later in the book" TODO. They belong to this generalization effort (working tree is
otherwise clean — nothing uncommitted was added):

- **`base.is_orthogonal_to` (`base.py:609`)** and **`base.is_parallel_to` (`base.py:633`)** — both
  `assert self.is_vector()` / `assert other.is_vector()` with a `# TODO - defined for vectors only …`
  comment; `is_parallel_to` also carries a `not sure if I'm doing this correctly` note (already listed
  under CLAUDE.md "Assessment / known issues #2"). Orthogonality/parallelism generalize to blades
  (via inner product / wedge being zero).
- **`transforms.projection_rotation`'s inner `r` (`transforms.py:217`)** — `assert value.is_vector()
  # TODO - can this be generalized?`. It's downstream of `reject` (uses `cls.reject(plane)`), so it is
  unblocked once `reject` accepts a general value.

Decision needed: extend this task's scope to cover these (they're the same "vectors-only → r-vector/
blade" change), or spin off a sibling task for the predicate methods. Recommendation: keep
`is_orthogonal_to`/`is_parallel_to` here (same fix shape), and treat `projection_rotation` as a
verify-after step once `reject` generalizes.

## Notes

- The 2-element (bivector) and 1-element (vector) cases already work and are covered by
  `test_project_and_reject` / `test_reflect` (1-element regression added 2026-06-05).
- `Gn` works in any dimension, but practical tests can use `G3`'s trivector pseudoscalar.

## Open questions

- **Homogeneous r-vector value: no book re-read needed** — galgebra + the literature confirm
  projection/rejection onto any blade is standard for a homogeneous value. The genuinely uncertain
  case the maintainer wanted to re-read Hestenes for is the **mixed-grade multivector value** — and
  galgebra shows even that is well-defined via the contraction + grade decomposition. Confirm gacalc
  wants to support mixed-grade values (recommended: yes, matching galgebra), or restrict to
  homogeneous blades for now.
- Product choice, reflect definition, and blade-vs-homogeneous guard — see the three design decisions
  above.
- Is there an upper-grade limit worth enforcing, or does it just work up to the pseudoscalar?

## Folded-in idea (2026-08-27, William Emerison Six <billsix@gmail.com>) — projections line→line / line→plane / plane→plane

A batch triage mapped this maintainer bullet here (same grade-general project/reject code):
*"In generated types, make projections from line to line, line to plane, plane to plane. Check
symbolically. Make examples in graded notebook."* Here "line"/"plane" mean **origin-through** blades
(grade-1 subspace / grade-2 subspace) — so plane→plane is exactly the grade-2-onto-grade-2 case this
task targets (`MultiVectorBase.project` at `src/gacalc/base.py:763` is already grade-general; the
restriction is in `reject`/`reflect`). The symbolic-check + graded-notebook demonstration could live
here or in `displaygraded-geometric-plots.md`.

**New open question (blocks this addition):** confirm "line"/"plane" here mean **origin-through**
subspaces (grade-1/grade-2) — distinct from the *affine/offset* flats in
`affine-flats-lines-planes-from-points.md`, so the two tasks don't collide — and whether the symbolic
checks + graded-notebook demos are tracked here or split into a notebook task.

*(Because this addition carries an unanswered question, treat the "projections" framing as blocked on the
above before implementing, independent of the base grade-generalization that was already proposed.)*
