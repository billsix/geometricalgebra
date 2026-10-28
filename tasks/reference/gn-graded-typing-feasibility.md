# Gn graded typing-subtypes — feasibility verdict & design recommendation

**Reference document** — the durable conclusion of the investigation "can `Gn` gain graded typing
subclasses (`Vector`/`Bivector`/`Versor`/`Scalar`) like the generated `G` classes?" (originating task
archived 2026-10-28). States what is TRUE and what is RECOMMENDED; update in place if the decision
changes. Companion to `tasks/reference/generated-product-typing.md` (how the *generated* graded types do
precise typing) and `graded-subspaces-vs-subalgebras.md`.

## The question

`Gn` (`src/gacalc/gn.py`) is the one dimension-agnostic reference representation — a
`@dataclass(slots=True)` wrapping a single `coefficient_of_blade` blade-dict. It has runtime grade
predicates (`is_scalar`/`is_vector`/`is_bivector`/`is_r_vector`, inherited from `base.py`) but **no
graded subtypes**. The generated `g1`/`g2`/`g3` classes do (`Scalar_n`/`Vector_n`/`Bivector_n`/
`Trivector`/`Versor_n`) with `@typing.overload` so products/sums are statically precise. The idea: give
`Gn` a *purely static* typing layer — a `Vector(Gn)` that narrows a value known to be grade 1 — so
dimension-agnostic code could state precise `Gn` signatures.

## Verdict (bottom line)

**Feasible, but NOT worth a full subtype hierarchy on `Gn`.** Precise graded typing already lives where
it belongs — the generated per-dimension `G` classes. `Gn`'s only incremental benefit is *narrowing at a
known-grade point in dimension-agnostic code*, a narrow payoff. Recommendation:

- **Do the narrowing with `TypeGuard`, not a class hierarchy with hand-written overloads.** Add thin
  marker subclasses `Vector(Gn)` / `Bivector(Gn)` / `Scalar(Gn)` (`__slots__ = ()`, no behaviour) and a
  **`TypeGuard`-returning narrowing helper** per grade; wire overloads onto `Gn` methods **only where a
  real call site benefits**, never the whole product table.
- **Operations widen back to `Gn`; re-narrow at the next known-grade step** (the "narrowing-view",
  Open-Q1's recommended cut). Do **not** make products auto-narrow by grade — that re-derives the
  generator's operation-driven typing on `Gn`, which the `G`-side already rejected as a
  value-dependent design (`generated-product-typing.md` → `Odd_3`).
- If no dimension-agnostic call site actually needs it, **do nothing** — `Gn` stays the simple,
  obviously-correct reference (its stated role in `CLAUDE.md`).

## What the investigation established (empirically; spikes under the archived task's adhoc dir)

1. **Cheap subclassing works.** `class Vector(Gn): __slots__ = ()` subclasses the slots-dataclass with no
   new per-instance storage; an instance built from the same blade-dict constructs and operates normally
   (`type(a) == Vector`, `a.is_vector() == True`).
2. **The crux — naive subclassing MIS-TYPES operation results.** Shared `base.py` methods build results
   with `type(self).from_blade_dict(...)` / `type(self).zero()`. So `vector * vector` constructs a
   **`Vector`** at runtime even though the product is scalar+bivector: the spike's `a*a` (for `a = 3e₁ +
   4e₂`) returned a value of class `Vector` holding `{(): 25}` — a scalar, with `.is_vector() == False`.
   A subtype that silently rides `type(self)` is therefore unsound as an operation-preserving type. The
   fix is to **widen**: `Gn.from_blade_dict((a*a).to_blade_dict())` restores class `Gn`.
3. **Both `TypeGuard[Vector]` and `TypeIs[Vector]` narrow under `ty`.** A `-> TypeGuard[Vector]` predicate
   narrows the positive branch to `Vector` and leaves `Gn` after; `-> TypeIs[Vector]` additionally
   narrows the else-branch to `Gn & ~Vector`. `ty` accepts the `TypeIs` declaration (it requires
   `Vector <: Gn`, satisfied by the subclass).

## The design fork, and why the recommendation lands where it does

Two coherent ways to make narrowing *sound*:

- **(A) Static-only narrowing via `TypeGuard` (recommended).** The runtime value stays a plain `Gn`
  (operations keep `type(self) == Gn`, so results are correctly `Gn` — the mis-typing in finding 2 never
  arises because you never construct subtype instances). `is_vector`-style helpers return
  `TypeGuard[Vector]`; a binding narrows to `Vector` statically while the object remains a `Gn`. Cost: a
  mild typing fiction (`TypeGuard` narrows to a type the value isn't an instance of) — benign here, since
  the marker subtypes add no behaviour, so a `Gn` and a "`Vector`" are runtime-identical. **Not `TypeIs`:**
  `TypeIs` semantically asserts the value *is an instance of* `Vector` when true, but a plain grade-1 `Gn`
  is not — so `TypeIs` on a plain-`Gn`-returning predicate is unsound (and `ty` won't catch it).
- **(B) Real instances via `as_vector()` + widening overrides.** `as_vector(v)` validates grade and
  returns a real `Vector(coefficient_of_blade=…)`; to stop operations mis-typing (finding 2), each
  subtype overrides `from_blade_dict`/`zero` to return `Gn`. Sound and `TypeIs`-compatible, but heavier:
  new constructors, per-subtype overrides, and a value-vs-class split to document.

(A) is lighter and sufficient for the stated goal (narrow a known-grade `Gn` so a precise overload
applies), so it is the recommendation; (B) is the fallback if a consumer genuinely needs real
subtype *instances* (e.g. `isinstance` dispatch), which nothing currently does.

**Where the `TypeGuard` target lives matters.** The grade predicates are defined on `MultiVectorBase`
(shared by `Gn` and `G`), so they cannot return `TypeGuard[<the Gn-level Vector>]` without coupling the
base to one representation's subtype (the "vector type" differs: `gn`-level `Vector` vs `g2.Vector_n`).
So the narrowing helper must be **`Gn`-specific** (a free function or a `Gn` method), not a retype of the
inherited base predicate.

## Rejected / out-of-scope

- **Grade-driven `from_blade_dict` auto-narrowing** (products land on the smallest actual grade type):
  rejected — it re-derives the generator's operation-driven typing on `Gn`, and the value-dependent
  variant was already rejected on the `G` side ("the type follows the operation, never runtime values",
  `generated-product-typing.md`).
- **A hand-written full `@overload` product table on `Gn`:** rejected — that is exactly what the code
  generator produces for `G`; duplicating it by hand on the deliberately-simple reference class fights
  `Gn`'s role and doubles the maintenance surface.

## If implemented

Follow-on task `tasks/gn-graded-typing-implement.md` (proposed — needs go-ahead) carries the design
(A): the marker subtypes + `TypeGuard` helpers + overloads only on the specific `Gn` signatures a real
call site needs. Keep house rules (externally-fixed names, `cls`/`n` naming, annotate every binding).
