# Redo `exp()` from scratch, book-referenced — and add a rotor-builder `i(a, b)`

**Status:** in progress. **Subtask 1 DONE (2026-08-14):** `bivector_from_vectors` (on
`MultiVectorBase`), `i(a, b)` classmethod (Gn/G2/G3/Vector), and `.i()` instance method
(Bivector/Rotor) implemented + verified — ruff/ty clean, 9 new tests + 358 total pass,
generator deterministic, doc-regions OK (`tests/test_unit_bivector_i.py`; generator emit in
`tools/gen_specialized.py` `i_classmethod`/`i_extractor`). All return a bivector; `Vector.i`
even narrows to `Bivector` at runtime. **Subtasks 4 (precise `i` typing + call-site audit) + 5
(explicit parallel-vector guard) DONE 2026-08-14** — `i` / `bivector_from_vectors` / `.i()` /
`plane_of_rotation` narrow to `Bivector_n` (and `rotor_from_vectors → Rotor_n`), done in the
precise-typing task ([[precise-typing-remaining-methods]]); `i` now raises an explicit `ValueError`
on parallel vectors. ty clean, 358 tests, deterministic, regions OK — container gate (ruff 0.16.3 +
ty + pytest) also green. **Note (corrected 2026-08-14):** the earlier "deferred: `plane_rotation`
reuse of `bivector_from_vectors`" is **not** unblocked by this — `plane_rotation` is generic over
`V`, so a classmethod returning concrete `Bivector` would widen `V`; it stays inline (see subtask 2).
**Subtask 2 (rotor-from-`i`) — DONE 2026-08-15:** `bivector_rotation(i)` shipped in `transforms.py`
(direct `cos(θ/2) − sin(θ/2)·i`, normalize-internally after grade-2 check, operand-agnostic
`InvertibleFunction[MultiVectorBase]`); `plane_rotation` rewritten onto a shared private rotor factory
(coefficient-identical, `V` typing preserved). 8 new tests, container gate green.
**Subtask 3 (exp slim-down) — DONE 2026-08-15:** the `A² > 0` (vector) hyperbolic branch removed; a
vector's `exp` raises; only scalar + `A² < 0` (rotor) remain, cited Dorst §7.4. 367 pass, ty clean,
container gate green.

**ALL SUBTASKS DONE.** Remaining loose ends before archiving: (1) the exp docstring **citation is
provisional** pending Bill's own book reading (one-line swap if he lands elsewhere); (2) `README.md`
/ `CLAUDE.md` mention of `bivector_rotation` deferred to Bill (the exp CLAUDE.md bullet was already
correctness-fixed). Once Bill confirms the citation, harvest the durable design rationale into
`tasks/reference/` and archive.
**Priority:** 3
**Difficulty:** 7
Created 2026-08-01 (Bill). This is a deliberate **redo** of already-landed work:
Bill has read the current `exp()` implementation, does not understand it, does not
like it, and wants it rebuilt from a foundation he can check against books.

## Why we're redoing this (Bill, 2026-08-01)

- Bill read the current `exp()` and **does not understand the implementation at
  all**, and **doesn't like it**. He wants an implementation he can **reference
  against books** (Hestenes & Sobczyk, and whatever else he reads).
- The **hyperbolic sine / cosine** (`sinh`/`cosh`) part is the specific sore
  point: it is **not something Bill knows about**, and he suspects it was **lifted
  from galgebra** rather than derived from a source he trusts. Treat the whole
  vector-case (`A² > 0 → cosh|A| + sinh|A|·Â`) as **suspect and up for removal or
  re-derivation** — do not assume it stays.
- Bill will **also investigate in books himself**. So this task is an
  **investigation** to be done *with* him, not a change to make and report. Do the
  research, write up findings, and **wait** — do not rewrite `exp()` until he's
  had his say.

## The `i(a, b)` idea to investigate (Bill's words, paraphrased)

Bill wants to add a function called **`i`** that:

- takes in **two vectors**, and
- makes a **unit `Rotor2`** (his phrasing) —
- **open question he flagged himself:** whether it should be the **full angle** or
  the **half angle** version, "for use with `exp`".

**Investigate, don't decide.** Things to pin down before proposing anything:

1. **What does `i` return — a unit *bivector* (the oriented plane) or a unit
   *rotor*?** These are different objects. The thing you feed to `exp` to get a
   rotor is a **bivector** (`exp(−(θ/2)·i)` where `i` is a unit bivector). Bill
   said "unit rotor2" *and* "for use with exp" — those pull in different
   directions, so clarify which he means (or whether he wants both: a plane
   builder and a rotor builder). Name collision alert: a **unit bivector is
   conventionally written `i`** in this codebase's docstrings (the "oriented
   plane"), so `i` as a *function name* returning a *rotor* would be confusing —
   raise this.
2. **Full-angle vs half-angle.** A rotor is a half-angle object
   (`R = cos(θ/2) − sin(θ/2)·i`). If `i(a, b)` is meant to plug into `exp`, work
   out whether Bill wants it to hand back the half-angle argument already, or the
   full-angle plane and let `exp` / a caller halve it.
3. **Overlap with what already exists** — do not reinvent:
   - `transforms.plane_rotation(a, b)` (`src/gacalc/transforms.py:278`) already
     takes two vectors, verifies they're grade-1, and forms **the plane's unit
     bivector `i` from their normalized wedge** (`a ∧ b`), then returns
     *angle → InvertibleFunction* building `R = cos(θ/2) − sin(θ/2)·i`. Bill's
     `i(a, b)` overlaps heavily with the *plane* half of this — decide whether
     `i` should be extracted from / share code with `plane_rotation`, or is a
     distinct public helper.
   - `MultiVectorBase.rotor_from_vectors(from, to)` (`src/gacalc/base.py:848`)
     already builds a (half-angle) rotor `R = |a||b| + b·a` directly from two
     vectors — **this may already be most of what `i` is supposed to be.** Compare
     the two constructions and figure out what `i` adds that `rotor_from_vectors`
     doesn't (unit normalization? a different sign/orientation convention? a
     bivector rather than a rotor?).
   - the "no hand-built rotor" convention (CLAUDE.md › Rotations & rotors): any
     new builder must fit it, not fight it.

## What exists today (so nothing is lost)

- **Current implementation:** `MultiVectorBase.exp()` at
  `src/gacalc/base.py:943` (roughly lines 943–1015). Grade-structural dispatch:
  scalar → `exp(s)`; grade-2 blade / 𝒢₃ pseudoscalar (`A² < 0`) → `cos + sin·Â`;
  grade-1 vector (`A² > 0`) → `cosh + sinh·Â` **(the part Bill distrusts)**;
  `raise ValueError` when `A²` isn't scalar. Numeric-preservation convention
  (`math.*` for float, `sympy.*` otherwise). Built via dispatching arithmetic
  (`Â·k + c`), never `from_blade_dict`.
- **Generated narrowing override:** `Bivector_n.exp() -> Rotor_n` in
  `tools/gen_specialized.py` (cast-and-delegate, like the `dual` override).
  `Vector_n.exp()` / `Trivector3.exp()` widen to `G_n`.
- **Tests:** `tests/test_exp.py` (properties + two `plane_rotation` agreement
  gates), `tests/test_conformance.py::test_exp`,
  `tests/test_graded.py::test_exp_narrows_bivector_to_rotor`, plus doctests in
  the `exp` docstring and an exp-map section in
  `notebooks/displayrotations.py`.
- **Original design record & full history of the first implementation:**
  `tasks/archive/2026/07/29/exp-for-rotors.md` — read this first; it documents
  every decision, including the "no `hint`, sign is structural" rationale and the
  `A² = (−1)^(r(r−1)/2)|A|²` grade formula that produced the sinh/cosh branch.
- **Git history to reconstruct what was done:** `b807f46` ("starting implementing
  exp") is the initial commit; subsequent touches to `src/gacalc/base.py` /
  `tests/test_exp.py` are `ae568f0`, `7f8f06d`, `76a4036`. Use
  `git show b807f46` / `git log -p -- tests/test_exp.py src/gacalc/base.py` to
  see the full evolution and the review comments Bill referred to.
- **Caveat on citations:** the archived task explicitly notes **no Hestenes &
  Sobczyk page number was ever located** for `exp` — the current docstring cites
  only the power series, not a book. Finding a real, checkable book citation is a
  **core goal** of this redo, not a footnote.
- **galgebra — suspicion confirmed.** The galgebra checkout is at
  **`/foo/opt/galgebra`** (a sibling of this repo, `v0.6.1rc1`, HEAD `ff0a938`),
  the exact version the archived task cited. Its `Mv.exp` is at
  **`galgebra/mv.py:1218`**, and it **does** use `cosh(norm) + sinh(norm)·value`
  for the positive-square case (lines 1242, 1247, 1260) — with the `hint='+'/'-'`
  parameter to pick trig vs hyperbolic when the square's sign is symbolically
  undecidable. So Bill's read is right: **gacalc's vector/hyperbolic branch
  mirrors galgebra's**, just with the sign made structural-by-grade instead of
  `hint`-driven. Re-read `mv.py:1218–1270` when deciding whether that branch has
  any book justification or should be dropped.

## Scope of the redo (to confirm with Bill)

- **Re-derive `exp` from a book Bill trusts**, with a real citation, in a form he
  can follow line-by-line. The scalar and bivector (rotor) cases are the ones he
  cares about ("rotor = exp(bivector)"); the **vector/hyperbolic case is the open
  question** — keep it only if it can be book-justified, otherwise drop it (and
  tighten the `ValueError` domain accordingly, updating tests + docstring).
- **Add `i(a, b)`** per the investigation above, once its shape (bivector vs
  rotor, full vs half angle, standalone vs shared with `plane_rotation`) is
  settled with Bill.
- Keep the four gates green throughout: `make test`, `make check-generated`,
  `make check-regions`, `make format` (ruff + ty).

## Investigation findings (2026-08-14 — research pass; still needs the maintainer's decisions)

All code anchors verified against the working tree; book section numbers verified against source
TOCs/PDFs except two flagged below.

- **galgebra confirmed.** `Mv.exp` (`/foo/opt/galgebra/galgebra/mv.py:1218-1270`) is the power
  series split by the sign of `A²`: `cosh(n)+sinh(n)·Â` for `A²>0`, `cos(n)+sin(n)·Â` for `A²<0`,
  `hint='+'/'-'` only for the **symbolic-undecidable** case (which gacalc doesn't have — Euclidean
  makes the sign structural by grade). It **cites no book**, and galgebra has **no** unit-bivector-
  from-two-vectors builder (only `rotate_multivector(itheta)`, which takes a bivector the *user*
  supplies). So gacalc's `cosh/sinh` grade-1 branch mirrors galgebra's `A²>0` branch — Bill's read
  is right.
- **`i(a,b) = normalize(a∧b)` is a unit bivector with `i²=-1`** (any Euclidean 2-blade: factor
  `B=|B|e₁e₂` orthonormal → `B²=-|B|²`; equivalently the grade-r formula `A²=(-1)^{r(r-1)/2}|A|²` at
  `r=2`). So `i` acts like the imaginary unit and `exp(-（θ/2)i)=cos(θ/2)-sin(θ/2)i` is the half-angle
  rotor. **A unit bivector is NOT a rotor** — the object `exp` consumes to make a rotor is the
  *bivector*; Bill's "unit Rotor2 … for use with exp" conflated the two.
- **`i(a,b)` already exists — unexposed — inside `plane_rotation`** (`transforms.py:337-343`):
  `plane = a.outer_product(b); … ; i = plane.normalize()`, with the grade-1 checks and the
  parallel-vectors guard. The local variable is even named `i`. `rotor_from_vectors` (`base.py:868`)
  is a **different** object (a rotor `|a||b|+b·a`, angle locked to a↔b), so it is *not* "most of what
  `i` is". Recommend extracting the plane-builder as a **public classmethod on `base.py` beside
  `rotor_from_vectors`**, which `plane_rotation` then calls (house "extract when >1 caller" rule; no
  duplicated parallel-guard).
- **Naming:** don't call it `i` — one-letter name (violates house style), collides with the
  unit-bivector-in-docstrings convention AND with `identity()`'s inner `i` (`base.py:856`), and
  would mislead if it returned a rotor. Recommend **`bivector_from_vectors(a, b)`** (mirrors
  `rotor_from_vectors`); keep `i` as the *value* name in docstrings.
- **Book citations (checkable):** primary = **Dorst, Fontijne & Mann, *GA for Computer Science*
  §7.4** ("Exponential Representation of Rotors"; §7.4.1 rotors as exp of 2-blades, §7.4.3 exp of
  bivectors, §7.4.2 the trig/hyperbolic split) — its structure *is* gacalc's `exp`. Free secondary =
  **Macdonald, *Survey of GA & GC*, Eq. (2.3)/(2.4)** (`R = e^{-iθ/2}`, unit bivector `i`). Doran &
  Lasenby ~§2.7 and Hestenes & Sobczyk: covered but **exact eq/page not pinned — don't invent** (H&S
  page was never found, consistent with the archived task).
- **The vector/hyperbolic `exp` branch → recommend DROP.** The `cosh/sinh` formula *is* book-backed
  (Dorst §7.4.2; Macdonald survey §4.1) — but **only for Minkowski boosts** (spacetime bivectors,
  `A²=+1` in a Lorentzian metric). No standard text treats "`exp` of a *Euclidean vector*" as
  meaningful; gacalc's grade-1 branch applies the boost formula to a Euclidean vector only because it
  *happens* to have positive square, with **no Euclidean geometric interpretation**. Dropping it
  restricts `exp` to the one clean idea "rotor = exp(bivector)", matches Bill's distrust, and is the
  branch that came from galgebra without a book. (Keep-option: leave it only with a docstring saying
  it's the boost formula, no Euclidean meaning, cite Dorst §7.4.2. Agent's vote, and mine: drop.)

**Recommendations on the 5 open questions:** (1) `i`/`bivector_from_vectors` returns a **unit
bivector**, not a rotor. (2) **Angle-free** — a unit bivector carries no angle; θ enters at the call
site as `exp(-（θ/2)*i)`. (3) **Share** — extract from `plane_rotation`, don't duplicate. (4) **Drop**
the hyperbolic vector case. (5) Cite **Dorst §7.4** + Macdonald survey Eq (2.3)/(2.4). These are
recommendations from the research pass — **Bill decides** (he's reading books in parallel).

## Refined plan — start with `i` (William Emerison Six <billsix@gmail.com>, 2026-08-14)

Bill's direction after the findings: build this in subtasks, starting with `i` alone; **name it
`i`** (his call — `i` *is* the mathematical name for the unit bivector, so he accepts the terse
one-letter name over the research's `bivector_from_vectors`; this overrides that rec). Get `i`
working, then update this task and move to the next subtask.

**Subtask 1 (do first) — LAYERED (William Emerison Six <billsix@gmail.com>, refined 2026-08-14): `bivector_from_vectors` + `i`.**
The maintainer's call, and it's the right one (agreed): a descriptive builder makes the *raw* bivector, and
`i` normalizes it — better than a pass-through alias, because the two names then serve two genuinely
different things, it lands the parallel-vectors guard in one sensible place, and it keeps the
descriptive name the research wanted *alongside* the terse mathematical `i`. Full math + rationale +
book citations live in the reference doc **`tasks/reference/unit-bivector-and-rotors.md`**.

- **`bivector_from_vectors(a, b)` → the (un-normalized) bivector `a ∧ b`** — the oriented plane the
  two vectors span (magnitude = the parallelogram's area). A **classmethod on the base**,
  paralleling `rotor_from_vectors` (`base.py:867`, also a `@classmethod` using `cls`): validate
  grade-1, return `a.outer_product(b)`. Does **not** guard parallel — the wedge of parallel vectors
  is legitimately the *zero* bivector.
- **`i(a, b)` → the UNIT bivector of that plane (`i² = −1`)** = `bivector_from_vectors(a, b).normalize()`.
  The parallel guard lands **here** (normalizing the zero bivector raises — gacalc 0.0.16 raises
  `ZeroDivisionError`). One place for the wedge, one place for the guard.
- **`.i()` → get the unit plane out of a value**, an **instance method on the graded `Bivector`
  and `Rotor` types**. Rotor already has it as **`plane_of_rotation()`** (`g2.py:3211` /
  `g3.py:5192`, `r_vector_part(2).normalize()`) — expose as `.i()` (alias/rename); `Bivector.i()`
  = `self.normalize()`.
- **`plane_rotation` (`transforms.py:337-343`) refactors to reuse these** — it currently inlines
  exactly `a.outer_product(b)` + parallel guard + `.normalize()`, so it should call the new
  `bivector_from_vectors` / `i`, leaving one implementation.

**Placement — avoids the classmethod-vs-instance `i` name clash.** The full types (`Gn`/`G2`/`G3`)
and graded types (`Bivector`/`Rotor`) are **siblings, not parent/child** (all `@typing.final`
subclasses of `MultiVectorBase`), so: `bivector_from_vectors` on the **base** (like
`rotor_from_vectors` — harmless to inherit); the **classmethod `i(a, b)` on the full classes**; the
**instance `.i()` on the graded `Bivector`/`Rotor`**. Two rules: (1) keep `i(a,b)` **off**
`MultiVectorBase` (else the graded `.i()` shadows the inherited classmethod); (2) don't add `.i()`
to the full `G` classes. (The earlier "`i` collides with `identity()`'s inner `i`" flag is a
non-issue — that `i` is a *local* function inside `identity()` at `base.py:856`, not a class
member.)

**Decided (William Emerison Six <billsix@gmail.com>, 2026-08-14):**
- **`i` — and `bivector_from_vectors` and `.i()` — return a BIVECTOR, never a rotor** (settles open
  question #1). `i` is the unit *bivector* (the plane), which is what you feed `exp` to get a rotor;
  a rotor-returning `i` would contradict the `i`=unit-bivector notation and duplicate
  `rotor_from_vectors`.
- **`i(a, b)` classmethod is on `Gn`, `G2`, `G3`, AND `Vector`;** `.i()` stays on the graded
  `Bivector`/`Rotor` **only**. `Gn` gets the classmethod (not `.i()` — a class can't hold both the
  `i(a,b)` classmethod and the `.i()` instance method); get the plane out of a general `Gn` bivector
  value with `.normalize()`, which `.i()` is just the named shortcut for.

**Subtask 2 — DONE 2026-08-15 (William Emerison Six <billsix@gmail.com>).** `bivector_rotation(i)`
shipped in `transforms.py` (exported there + re-exported from `gn.py`); 8 new tests
(`tests/test_bivector_rotation.py`) + the docstring doctest, 367 total pass; ruff + ty clean; **container
gate green** (ruff 0.16.3, ty, pytest). Implementation notes vs the plan below:
- **Shared private `_unit_bivector_rotor_factory(i)`** holds the half-angle rotor construction +
  numeric-preservation; **both** `bivector_rotation` and `plane_rotation` call it. `plane_rotation`
  is rewritten onto **this shared factory**, not by literally calling `bivector_rotation` — because
  `bivector_rotation` returns `InvertibleFunction[MultiVectorBase]` (operand-agnostic; see next),
  and delegating to it would **regress** `plane_rotation`'s precise `InvertibleFunction[V]` return (a
  breaking change for mvp, which relies on `Vector3 → Vector3`). The shared factory gives the real
  dedup (the subtle numeric-preservation lives in one place) while each keeps its own typed closure.
- **`bivector_rotation` is operand-agnostic (`InvertibleFunction[MultiVectorBase]`)** — unlike
  `plane_rotation`, which ties the operand type to the input vectors, there's nothing in `i` alone to
  infer the operand type from (you rotate *vectors* with a *bivector* plane — different types). Making
  it generic over `i`'s type would wrongly force you to rotate bivectors. Runtime still preserves the
  operand's concrete type via the grade-preserving sandwich; only the static type is widened.
- Coefficient-identical `plane_rotation` confirmed: the pinned exact-form test
  (`test_exp_agrees_with_plane_rotation_symbolic`) + `test_plane_rotation.py` still pass unchanged.
- **`README.md` / `CLAUDE.md` mention deferred to Bill** (he reserved the right to add later).

_Original direction notes (2026-08-14):_ A rotation builder that takes a **unit bivector `i`** (instead of two
vectors) and returns a **θ-parametrized sandwich**, exactly mirroring `plane_rotation`'s curried
shape: `f = rotate_in(i)` once, then `f(θ)` builds `R = cos(θ/2) − sin(θ/2)·i` and returns the
sandwich `x ↦ R x R⁻¹` (an `InvertibleFunction`, like `plane_rotation`). This is Bill's idea —
"something like `plane_rotation`, just taking `i` as the parameter instead of two vectors." (Naming
TBD — e.g. `rotate_in` / `rotation_in_plane`; it's the `i`-first sibling of `plane_rotation`.)

- **Build the rotor the DIRECT way — `cos(θ/2) − sin(θ/2)·i` — NOT via `exp(−(θ/2)·i)`.** This is
  the crux, and it's why the codebase already keeps `plane_rotation` off `exp`: `exp` works through
  the magnitude `|−(θ/2)·i| = sqrt(θ²)/2`, which only collapses to `θ/2` under a positivity
  assumption on θ, so for an unrestricted **symbolic** θ, `exp` yields `cos(√(θ²)/2) − …` — not
  syntactically `cos(θ/2)`, a symbolic-render regression. The direct half-angle form never computes
  a magnitude, so it stays clean. (Documented in `test_exp.py` + `tasks/reference/design-decisions.md`.)
- **`plane_rotation(a, b)` then rewrites in terms of THIS builder** — `plane_rotation(a, b) =
  rotate_in(i(a, b))` — real dedup, symbolic form preserved. **Do NOT rewrite `plane_rotation` onto
  `exp()` itself** (that's the regression above). The builder and `exp` stay two parallel routes to
  a rotor that agree numerically; the builder is the clean route for "explicit angle in a known
  plane", `exp` is the general primitive for "exponentiate an arbitrary bivector."
- **Scope is Euclidean 𝒢ₙ only** (early Hestenes — no conformal / projective / spacetime), which is
  already the project's hard signature constraint. Nothing here needs a non-Euclidean metric.
- **Docs (Bill reserves the right to add later, not now):** when this lands, mention the `i`-first
  rotation builder and the "rotor = exp(bivector)" story in `README.md` and `CLAUDE.md` (alongside
  the existing rotations/rotors convention). Deferred to Bill's discretion.

**Decided (William Emerison Six <billsix@gmail.com>, 2026-08-14):**
- **Name: `bivector_rotation(i)`** — the `i`-first free-function factory, fitting the existing
  `plane_rotation` / `projection_rotation` / `rotor_rotation` family in `transforms.py`. Reads as
  "rotation in the plane of this bivector."
- **Normalize `i` internally** (agreed — Bill: "especially given that floating point may be in
  play"). A bivector meant to be unit but drifted by float rounding would otherwise silently scale
  the rotation angle; normalizing is a clean no-op when `i` is already unit (exact → identity; float
  → ~identity). **Validate grade-2 first** (`i.is_bivector()`, else `TypeError`), then normalize —
  same shape as `plane_rotation` validating grade-1 inputs.
- **Assumes a *simple* (blade) bivector** — the plane interpretation requires `i² = −1`, true for
  every 𝒢₂/𝒢₃ bivector. A *non-simple* bivector (only possible in 𝒢₄₊, e.g. `e₁₂ + e₃₄`) has
  `i² ≠ −1` and no single plane; that's **out of scope** here (early-Hestenes Euclidean, and the
  generated algebras are g1/g2/g3). Note it; don't guard it now unless 𝒢₄ lands.

**The direct construction is confirmed** (William Emerison Six <billsix@gmail.com>, 2026-08-14):
once `i` exists the rotor is trivial — `R = cos(θ/2) − sin(θ/2)·i`, automatically **unit** because
`cos² + sin² = 1` (`R R̃ = c² + s² = 1` for `R = c + s·i`). The `1/√2`-scalar-and-coefficient idea
is exactly the **θ = 90°** case (`c = s = 1/√2 ⇒ θ/2 = 45°`, and `½ + ½ = 1`). Any `(c, s)` with
`c² + s² = 1` is a unit rotor turning by `θ = 2·atan2(s, c)`. Full derivation + the sign/orientation
note: `tasks/reference/unit-bivector-and-rotors.md` §3.

**Subtask 3 — DONE 2026-08-15 (William Emerison Six <billsix@gmail.com>): the `exp()` slim-down.**
`MultiVectorBase.exp` (`base.py`) now handles only the scalar and negative-square (`A² < 0`) cases —
`cos|A| + sin|A|·Â`, the rotor case. The positive-square (`A² > 0`, vector) branch — the
galgebra-derived `cosh/sinh` — was **removed**; a vector's `exp` now raises `ValueError`. The `match`
collapsed to a single guarded return (no more grade-sign dispatch), so the implementation is legible.
`Bivector_n.exp() → Rotor_n` (generated override) and `Trivector.exp` (𝒢₃ pseudoscalar, `A² < 0`)
still work. Tests updated: `test_exp_of_a_vector_is_rejected` (was `..._is_hyperbolic`), conformance
`test_exp` (vector now rejected across all representations), module docstrings; docstring cites Dorst,
Fontijne & Mann §7.4. ty clean, 367 pass, container gate green. Docs reconciled: `CLAUDE.md` exp
bullet + `tasks/reference/design-decisions.md` line 93 (both said "hyperbolic for a vector" — now
corrected).

**CITATION IS PROVISIONAL — pending Bill's book reading.** The code change (the drop) is settled and
done; the docstring/CLAUDE.md cite **Dorst §7.4** (the research recommendation). If Bill's reading
lands on a different anchor (a specific Hestenes & Sobczyk page), it's a one-line docstring swap — the
implementation does not change.

_Original direction notes (2026-08-14):_ The `exp()` redo itself. The shape agreed:

- **Slim, don't delete.** Bill raised deleting `exp` entirely ("I don't understand it"). Decision:
  **keep `exp`, but strip it to ONLY the bivector case** — `exp(bivector) = cos|B| + sin|B|·B̂ → a
  rotor`. That removes the distrusted code, makes the implementation legible (the current opacity is
  the generic grade-dispatch, not the bivector math), and keeps "rotor = exp(bivector)", the one
  identity the rotation work leans on. Full deletion would force hand-inlined trig at every rotor
  site and throw away a standard GA operation.
- **Drop the vector/hyperbolic (`sinh`/`cosh`) branch** — reinforced by the **Euclidean-only scope**:
  that branch is the Minkowski *boost* formula (Dorst §7.4.2), meaningful only in a Lorentzian
  metric. In early-Hestenes Euclidean 𝒢ₙ it has no geometric interpretation, so dropping it is
  correctness for the project's scope, not just cleanup. Tighten `exp`'s `ValueError` domain to
  scalar + bivector/pseudoscalar; update tests + docstring.
- **Cite Dorst §7.4** (+ Macdonald survey), pending whatever text Bill settles on from his reading.

**Subtask 4 — DONE 2026-08-14 (William Emerison Six <billsix@gmail.com>): precise return typing for
`i` / `.i()` + call-site audit.** Implemented in the precise-typing task
([[precise-typing-remaining-methods]], Tier 2) since it's the same mechanism: `i` /
`bivector_from_vectors` / `.i()` / `plane_of_rotation` now narrow to `Bivector_n`, and
`rotor_from_vectors` to `Rotor_n`, via two new generator helpers
(`classmethod_narrowing_overloads` + `inherited_classmethod_narrowing`), gated on n≥2. `test_exp.py`'s
two hand-rolled `(e_1 ^ e_2).normalize()` sites are rewritten to `Vector.i(e_1, e_2)`.
**Correction to the original plan below: this does NOT unblock `plane_rotation` reuse** —
`plane_rotation` is a free function generic over `V`, so a classmethod returning the concrete
`Bivector` would widen `V`; it stays inline (and has its own numeric-preservation reason). The
narrowing helps only concrete-typed call sites. Original investigation notes retained below.

**Subtask 5 — DONE 2026-08-14: explicit parallel-vector guard in `i`.** `i(a, b)` (both the generated
classmethods and hand-written `Gn.i`) now raises `ValueError("the two vectors are parallel (their
wedge is zero): they span no plane of rotation")` — matching `plane_rotation` — instead of leaking
`normalize`'s `ZeroDivisionError`. Guard lives in `i`, not `bivector_from_vectors` (which legitimately
returns the zero bivector). `test_i_of_parallel_vectors_raises` updated to expect `ValueError`.

---

_Original subtask-4 investigation notes (kept for the record):_ The shipped subtask 1 emits **both** the
`i(a, b)` classmethod and the `.i()` instance method returning **`MultiVectorBase`** — the imprecise
base type (generator `i_classmethod` / `i_extractor`, `tools/gen_specialized.py:475,505`; e.g.
`g3.py:842` `def i(cls, a: MultiVectorBase, b: MultiVectorBase) -> MultiVectorBase`, `g2.py:530`, and
the `.i()` at `g2.py:2557`/`g3.py:3488`). But `i` **always yields a grade-2 unit bivector**, so the
precise return is knowable per type and should be resolved at generation time (the same way the
generated products narrow via the type registry / `resolve`):

- `Gn.i(a, b)` → `Gn` is already correct (dimension-agnostic, no graded subtypes).
- `G2.i` / `G3.i` / `Vector.i` → could narrow to that algebra's **`Bivector`** type.
- `.i()` on `Bivector` → `Bivector` (really `Self`); on `Rotor` → that algebra's `Bivector`.
- The params `a`, `b` are also typed `MultiVectorBase`; whether to tighten them to grade-1 `Vector`
  is part of this.

**This is the same imprecision that blocks reuse elsewhere.** `plane_rotation`
(`transforms.py:337-348`) deliberately keeps its wedge **inline** (`a.outer_product(b)` + parallel
guard + `.normalize()`) *instead of* calling `bivector_from_vectors` / `i`, with a comment saying so:
routing through the base helper would widen the precise generic `V` to `MultiVectorBase` and break the
downstream numeric-preservation code. So **couple this to the precise-typing task**
(`precise-typing-remaining-methods.md`) — if `bivector_from_vectors` / `i` gain a precise per-type
return, the typing here **and** the deferred `plane_rotation` reuse (noted under subtask 1) unlock
together.

Then **audit the codebase for hand-rolled unit bivectors that should call `i` instead** (found in the
research pass, anchors verified against the tree 2026-08-14):

- `transforms.plane_rotation` (`transforms.py:348`, `i = plane.normalize()`) — the canonical case;
  blocked on the typing above (has its own numeric-preservation reason too — re-read that block).
- `tests/test_exp.py:93` (`i: g3.Bivector = (g3.Vector.e_1 ^ g3.Vector.e_2).normalize()`) and `:108`
  (the g2 twin) — these hand-build exactly the unit bivector `i` now names; rewrite as
  `g3.Vector.i(e_1, e_2)` **once the return type is precise** (so the `g3.Bivector` annotation still
  holds without a cast).
- Re-sweep the notebooks (`displayrotations.py` exp-map section) when doing this — the 2026-08-14
  grep found only prose/comments there, no code site, but recheck after any `exp` redo (subtask 3).

_Original subtask-5 design note (implemented as summarized above):_ Today `i(a, b)` guards parallel
vectors only **implicitly**: the
wedge of parallel vectors is the zero bivector, and normalizing zero raises a low-level
**`ZeroDivisionError`** (gacalc 0.0.16) — `test_i_of_parallel_vectors_raises`
(`tests/test_unit_bivector_i.py:68`) pins exactly that exception. Meanwhile `plane_rotation` raises an
explicit, readable **`ValueError`**: *"the two vectors are parallel (their wedge is zero): they span
no plane of rotation"* (`transforms.py:344-347`). The two entry points to the same math disagree.

Make `i`'s guard **explicit and consistent with `plane_rotation`** — detect the zero wedge and raise
the same meaningful `ValueError`, instead of leaking `ZeroDivisionError`. The guard belongs in **`i`**,
**not** `bivector_from_vectors` — the design (subtask 1) is that `bivector_from_vectors` legitimately
returns the *zero* bivector for parallel inputs (the wedge really is zero), and only the
*normalization* step (`i`) is undefined there. Update `test_i_of_parallel_vectors_raises` (change the
expected exception) and the `i` docstring. Bonus: once `plane_rotation` is refactored onto `i`
(subtask 4), this removes the duplicated guard, leaving one implementation and one message.

**Upshot of relating this to the code:** the plane-builder, the plane-extractor, and the
half-angle rotor Bill described **all already exist inside `plane_rotation` / `plane_of_rotation`**
— this work is mostly *exposing and naming them as `i`*, plus the `exp` cleanup, not new
mathematics.

## Open questions (for Bill)

1. **`i(a, b)` return type:** unit **bivector** (the oriented plane, for feeding
   `exp`) or unit **Rotor2**? Or both (a plane builder *and* a rotor builder)?
   Note the name clash: `i` already denotes the unit bivector in docstrings.
2. **`i(a, b)` angle:** **full angle** or **half angle**? If it's "for use with
   `exp`", should it hand back the already-halved argument, or the plane and let
   `exp` do the halving?
3. **`i` vs the existing builders:** should `i` be built from / share code with
   `transforms.plane_rotation` and/or `rotor_from_vectors`, or be a new
   independent public helper? What does it add that those two don't already give?
4. **The vector (hyperbolic) case of `exp`:** keep it (with a book citation) or
   **remove it** and restrict `exp`'s domain to scalar + bivector/pseudoscalar?
5. **Which book(s)** are the reference for the redo (Hestenes & Sobczyk section?
   another text)? Bill is researching this in parallel — align before writing
   code.
6. **(Subtask 4) Precise `i` typing:** ✅ RESOLVED/DONE 2026-08-14 — narrowed to
   `Bivector_n` (`Gn.i → Gn` unchanged) in the precise-typing task. Params kept as
   `MultiVectorBase` on the impl with a precise `Vector` `@overload` (that's what makes
   the narrowing sound). Correction: it did **not** unblock `plane_rotation` reuse (generic
   over `V`); only concrete call sites.
7. **(Subtask 5) Parallel guard:** ✅ RESOLVED/DONE 2026-08-14 — `i` now raises the same
   `ValueError` as `plane_rotation`; guard lives in `i`.
