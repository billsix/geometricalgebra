# Redo `exp()` from scratch, book-referenced — and add a rotor-builder `i(a, b)`

**Status:** proposed — **investigation first, needs go-ahead before any code change**.
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

## Investigation findings (2026-08-14 — research pass; still needs Bill's decisions)

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
