# Use `bivector_from_vectors` / `i` in the notebooks and unit tests

**Status:** proposed — **BLOCKED on a small prerequisite** (narrow `bivector_from_vectors` / `i` for
`Gn`; see Finding). Not cleanly actionable until that lands.
**Priority:** 6
**Difficulty:** 3

## Finding (2026-08-27) — the adoption downgrades typing for `Gn`, so it needs a prerequisite

Attempted the adoption; **reverted, no changes kept.** Verified every candidate site:

- **Most `^` / `.wedge()` uses are teaching the wedge** (asserting its graded type/value, displaying
  the geometric/outer product, the Lagrange-identity / plane-decomposition cells). The task already
  says to keep those — correct, they stay.
- **The genuine "plane/bivector as a means to an end" sites are all in `Gn` / `MultiVector` context:**
  `notebooks/displaymv.py:443` (`biv = vec_a ^ vec_b`, then used across ~8 downstream cells —
  `biv*biv`, `biv.dual(3)`, `biv.dot(biv.dual(3))`, …) and `tests/test_conformance.py:254`
  (`b = vec(n,0) ^ vec(n,10)`, a bivector fed to `exp`). These are the only real scaffolding uses.

**The blocker (root cause):** **`Gn.bivector_from_vectors` / `Gn.i` return `MultiVectorBase`, not
`Gn`** — only the *generated graded* `Vector_n` types got the narrowing overload (Tier 2 of the
archived `precise-typing-remaining-methods.md`, via `classmethod_narrowing_overloads` /
`inherited_classmethod_narrowing`). `Gn` (hand-written in `gn.py`) never got it. So adopting the
helper at those sites **downgrades the type**: the wedge `^` gives a precise `Gn`, the helper widens
to `MultiVectorBase`, and e.g. `b: Gn = Gn.bivector_from_vectors(...)` is a hard **ty error**
(`invalid-assignment: MultiVectorBase is not assignable to Gn`, verified) — and the notebook
`biv: MultiVector = …` fails pyright the same way.

Meanwhile the *graded-Vector* contexts where the helper **is** precise (`→ Bivector_n`) have **no**
hand-built planes: `displayg2`/`displayg3` operate on the full `G`, and the graded tests use
`gn.e_1 ^ gn.e_2` as **expected-value** assertions (wedge-as-subject, keep). So there is currently no
site where adoption is both meaningful and non-regressive.

**The prerequisite (small):** narrow `bivector_from_vectors` / `i` for **`Gn`** itself — a
hand-written override in `gn.py` typing `Gn.bivector_from_vectors(a, b) -> Gn` and `Gn.i(a, b) -> Gn`
(the wedge, and its normalization, of two `Gn` vectors *is* a `Gn`, so `-> Self` is sound; `i` also
raises on parallel vectors, unchanged). That mirrors the Tier-2 graded narrowing, which simply never
covered the non-generated `Gn`. Once `Gn` narrows too, the `displaymv.py:443` / `test_conformance:254`
adoptions are clean (no typing downgrade), and this task can proceed. **Definitional equality is
confirmed** (`Gn.bivector_from_vectors(a, b) == a ^ b`), so the runtime/display is unchanged either
way — this is purely a typing gate.

**Recommendation:** do the `Gn`-narrowing prerequisite first (its own small task), then this one. If
that's declined, this task should be **closed** — there are no clean adoption sites at present.
(Priority dropped 5 → 6 to reflect the block.)

## Goal

Now that the plane helpers ship (subtask 1 of
`tasks/archive/2026/08/15/redo-exp-book-referenced.md`, committed 2026-08-14) — `cls.bivector_from_vectors(a, b)` (raw wedge `a ∧ b`), `cls.i(a, b)`
(the plane's **unit** bivector, `i² = −1`), and `.i()` (a value's own unit plane) —
adopt them in the notebooks and tests **where a plane or unit bivector is currently
built by hand** (`a ^ b`, `(a ^ b).normalize()`, `a.wedge(b)` used as "the plane the
two vectors span"). Design + math: `tasks/reference/unit-bivector-and-rotors.md`.

## The judgment call (do NOT blanket-replace `^`)

The `^` operator and `.wedge()` have two very different roles in this repo, and only
one of them should change:

- **Teaching what the wedge IS** — keep `^` / `.wedge()` verbatim. Any cell whose
  subject is the outer product itself (`a ∧ b = a·b`'s antisymmetric part, the
  Lagrange-identity derivation, `|a ∧ b| = |a||b|sinθ`, dot+wedge = geometric product)
  must keep spelling the wedge out; hiding it behind `bivector_from_vectors` would
  erase the lesson. Most `displayg2.py` wedge uses (≈ lines 132–530) are this kind.
- **Constructing a plane as a means to an end** — adopt the helper. Where two vectors
  are wedged only to *get the plane they span* (then normalized, inverted, or fed to a
  rotation), `bivector_from_vectors(a, b)` / `i(a, b)` names the intent and reads as the
  math. Candidate sites found in a first pass (verify each before editing):
  - `notebooks/displaymv.py:443` — `biv: MultiVector = vec_a ^ vec_b` (a raw bivector
    from two vectors → `bivector_from_vectors`).
  - `notebooks/displaymv.py:327,330,333` — `sym_vec3_1.wedge(sym_vec3_2)` and its
    `.inverse()` (the plane and its inverse).
  - `notebooks/displaymv.py:308–321` — the `e1e2plane(...) ^ e1e2plane(...)` plane
    constructions.
  - Any `(a ^ b).normalize()` used as "the unit plane" → `i(a, b)`.

## Tests

`tests/test_unit_bivector_i.py` already covers the helpers directly (9 tests) — this
task is **not** about that file. It's about the *other* suites (`test_graded.py`,
`test_conformance.py`, notebooks-as-doctests) where a hand-built plane appears as
scaffolding for a different assertion; switch those to the helper so the intent is
named and the helpers get exercised in real use. Keep any test whose *subject* is the
wedge/normalize itself unchanged.

## Verification

- `make test` green (notebooks are imported/doctested), `make format` clean (ruff + ty).
- Re-render any touched notebook and confirm the displayed math is unchanged (helper is
  definitionally equal to the hand-built form — `i(a,b) == (a^b).normalize()`).
- `make check-regions` if any `# doc-region` markers move.

## Open questions

1. Should the notebooks *introduce* `bivector_from_vectors`/`i` pedagogically (a cell
   that shows `i(a,b)` equals the hand-built unit wedge, teaching the helper) — or only
   use them silently as scaffolding? Recommend: **one introductory cell** in the 𝒢₂ or
   𝒢₃ notebook that presents the helper right after the wedge is taught, then silent use
   elsewhere.
