# Present student-facing facts in sine/cosine, not dot/wedge (Lean proofs + Python)

## BLUF

A durable pedagogical principle (now in `CLAUDE.md` › "Presenting to students"): whenever a result is
**shown to a student** — a Lean proof's *stated* form, a Python docstring, a notebook, the book — and
a faithful **sine/cosine-of-the-angle** phrasing exists, prefer it over the raw **dot/wedge** form,
because the angle is what a geometry-trig student can picture ("the cosine of the angle is 0" ⇒
perpendicular; "the sine is 0" ⇒ parallel; "area = |a||b| sin θ"). The dot/wedge form stays as the
**primitive**; the trig form is layered on top as a corollary — never trade the robust, √/division-free
primitive for a trig form that only adds `√`/`0÷0` noise. This task (1) inventories the proofs (and
the mirrored Python presentations) for dot/wedge statements with a faithful trig equivalent, (2) asks
the maintainer which to convert, (3) adds the trig-form corollaries in Lean, and (4) mirrors the
change into the Python library's student-facing presentation where feasible.

**Status:** in progress — first pass done; **Phase 2 authorized 2026-10-03** (object-level +
nonzero-guarded trig theorems; Python raises on zero). See "Phase 2" at the bottom.
**Priority:** 5. **Difficulty:** 5.
**Created:** 2026-10-03 (William Emerison Six <billsix@gmail.com>).
**See also:** `CLAUDE.md` › "Presenting to students"; `tasks/reference/lean-ga-proof-architecture.md`
(leaf-vs-structural; the trig forms are structural corollaries over the dot/wedge leaves); the
originating example, archived `tasks/archive/2026/10/03/lean-lift-theorem-statements-to-objects.md`
(`G2.dual_perp`, `dot (dual v) v = 0`).

## The targets already exist

`Trig.lean` defines, for **both** algebras, `cos_between a b := dot a b / (magnitude a * magnitude b)`
and `sin_between a b := magnitude (wedge a b) / (magnitude a * magnitude b)` (G3 `:22/:25`, G2
`:88/:91`); `TrigEquiv.lean:41` adds the signed `signed_sin_between` (G2). So a trig-form corollary is
typically a one-liner resting on the dot/wedge lemma (numerator is 0 ⇒ `zero_div`; no extra
hypotheses). Plumbing: a file stating a trig corollary must `import GacalcProofs.Trig` (or the
`cos_between`/`sin_between` defs get relocated to a shared spot).

## Inventory (first pass, 2026-10-03) — dot/wedge facts with a faithful trig phrasing

**Perpendicularity → `cos_between … = 0`:**
- `Predicates2D.lean:14` `dual_perp` (`dot (dual v) v = 0`) — the originating case; corollary
  `dual_perp_cos : cos_between (dual v) v = 0` (`simp only [cos_between, dual_perp hv, zero_div]`).
- `Cross.lean:38/:43` `cross_perp_left/right` (`dot (cross a b) a = 0`) — the cross product is
  perpendicular to each factor.
- `Projection2D.lean:91` / `Projection3D.lean:31` `reject_perp` (`dot (b − proj a b) a = 0`).
- `Projection3D.lean:46/:51` `dual_wedge_perp_left/right`; `:120` `proj_plane_perp_normal`.
- `G2.lean:208` `dual_vec_perp` (the coordinate leaf under `dual_perp`).
- Hypothesis-side (`… (h : dot a b = 0)`): `AlgebraLaws.lean:53/:109` `vec_anticomm_perp`,
  `Projection2D/3D mul_eq_wedge_of_perp`, `Predicates3D.lean:22` `perp_iff_mul_eq_wedge` — these could
  additionally offer a `cos_between a b = 0`-phrased entry point.

**Parallelism → `sin_between … = 0`:**
- `Predicates3D.lean:37` `wedge_parallel_smul` (`wedge a (k·a) = 0`) — parallel ⇒ sine 0.

**Area / measures → `|a|·|b|·sin θ`:**
- `Measures.lean:18` `area := |wedge|`, `:21` `area_sq_vec`; `:38` `volume` — the student formula is
  `area = |a||b| sin θ`; a corollary `area a b = magnitude a * magnitude b * sin_between a b` makes the
  trig identity explicit (rests on the `sin_between` def; needs the magnitudes nonzero only if divided).

**Already trig-stated (models, not candidates):** `Trig.lean` `sandwich_preserves_cos/sin`,
`cos_sq_add_sin_sq`, `TrigEquiv.lean`.

## Plan (after the maintainer selects)

1. **Lean:** for each selected fact, add a trig-form corollary (`cos_between=0` / `sin_between=0` /
   `area=|a||b|sin`) that **rests on** the existing dot/wedge lemma; keep the primitive. Add the
   `import GacalcProofs.Trig` where needed. `make lean` green after each.
2. **Python mirror:** the Lean proofs cite the gacalc methods they verify (`base.py` line refs — e.g.
   `dual` 1217, `is_orthogonal_to` 1064, `is_parallel_to` 1100, measures). The "mirror" is the
   library's **student-facing presentation** of those same facts — method **docstrings**, the
   **notebooks** (`notebooks/display*.py`), and the **book** — which should likewise lead with the
   sin/cos phrasing (e.g. `is_orthogonal_to`'s docstring: "⇔ the cosine of the angle is 0"). This is a
   presentation/docstring/notebook change, **not** an API change — the dot/wedge implementation stays.
   Inventory the exact Python spots once the Lean scope is fixed, reframe where feasible, and verify
   `make test` (docstrings run as doctests) + `make format` green.

## Decisions (resolved 2026-10-03, William Emerison Six <billsix@gmail.com>)

1. **Scope — first pass = the three clear families** (perpendicularity `cos=0`, parallelism `sin=0`,
   area `|a||b|sinθ`). The hypothesis-side `(h : dot a b = 0)` entry points and any other candidates
   are **deferred to a separate follow-up task the maintainer has NOT yet reviewed** —
   `tasks/prefer-sine-cosine-presentation-followups.md`.
2. **Form — add trig corollaries ALONGSIDE** the dot/wedge lemmas (keep the √-free primitive; the
   maintainer's only requirements: the Lean proofs stay correct, and student-facing material uses
   sin/cos where it can).
3. **Python reach — EVERYTHING that mirrors this**: docstrings, notebooks, the book, **and the Python
   implementation code** — subject to the standing discretion (`CLAUDE.md` › "Presenting to
   students"): lead with / expose sin·cos in student-facing spots, but do **not** reimplement a robust
   predicate as a fragile `trig == 0` (keep the dot/wedge computation as the primitive; add/expose the
   trig view on top).

## First pass — done (2026-10-03, `make lean` green, staged)

**Lean (the 3 families, as corollaries alongside the dot/wedge primitives):** new
`proofs/GacalcProofs/StudentTrigForms.lean` (collected in one file because `cos_between`/`sin_between`
sit above the lemma files in the import graph — a corollary beside its primitive would cycle):
- Perpendicular → `cos = 0`: `G2.dual_perp_cos`, `G2.reject_perp_cos`, `G3.cross_perp_left_cos`,
  `G3.cross_perp_right_cos`, `G3.reject_perp_cos`.
- Parallel → `sin = 0`: `G3.parallel_sin` (`sin_between a (k·a) = 0`).
- Area → `|a||b| sin θ`: `G3.area_eq_mag_mul_sin`.
Each rests on the existing dot/wedge lemma; the primitives are untouched. `make lean` green
(`StudentTrigForms` built, no `sorry`/`admit`).

**Python docstrings (library):** reframed `base.py` `is_orthogonal_to` (lead: "perpendicular — the
cosine of the angle is zero", cross-refs `cosine`), `is_parallel_to` (lead: "the sine of the angle is
zero", cross-refs `abs_sin`), and `area` (`= |a||b| sin θ`, cross-refs `abs_sin`) — each keeps the
robust dot/wedge *implementation* and explains why (no `0/0`). `ruff check` clean. Also fixed a stale
`Predicates.lean` → `Predicates3D.lean` pointer in `is_parallel_to`'s docstring (the file reorg had
missed `src/`).

**Python implementation:** reviewed — **no change, by design**. The predicates stay on the
division-free dot/wedge primitive (reimplementing as `cosine == 0` / `sin == 0` would add the `0/0`
trap); the trig view is already exposed as methods (`cosine`, `abs_sin`, `g2.Vector.sine`).

**Notebooks + book:** inventoried — the student-facing material **already prefers sin/cos**
(`notebooks/displayg2.py` has `a·b = |a||b|cos θ`, `|a∧b| = |a||b|sin θ`, `a.cosine(b)`, and the
parallel/perpendicular narrative; `book/docs/notebooks/levels-of-abstraction.py` has a "Sine and
cosine" section; `book/docs/proof-rotate.rst` is built on sin/cos). So there was little existing
dot/wedge text to convert. The remaining sin/cos-first work is in book **placeholders**
(`book/docs/orthogonal.rst` etc.) — that is content to *write*, which belongs in the book's own
content/voice pass (`tasks/levels-of-abstraction-book-voice-pass.md`), not a mirror of existing text.
Optional minor emphasis tweaks (e.g. spelling out `|a||b| sin θ` at `displayg3.py` area) were left
alone to avoid re-executing notebooks for marginal gain.

**Status:** first pass DONE. Remaining threads routed: deferred Lean candidates →
`tasks/prefer-sine-cosine-presentation-followups.md`; book sin/cos-first content → the book voice
pass. Archivable.

## Phase 2 (authorized 2026-10-03) — object-level + nonzero-guarded, and Python raises

Refinement from the follow-up discussion. Two changes, in Lean and Python:

**Lean — trig theorems become object-level AND nonzero-guarded.**
- **Object-level inputs:** the student-facing trig theorems take `{a b : G3}` (or G2) + `IsVector`
  hypotheses, NOT coefficient tuples `(a1 a2 a3 : ℝ)` — proved by dropping to the coordinate leaf once
  (`eq_vec_of_isVector`). (Coordinates stay only in the leaf/bridge; "use coordinates only when
  needed" — now in `CLAUDE.md` and `lean-ga-proof-architecture.md`.) This reopens, correctly, the
  lift scope that `lean-lift-theorem-statements-to-objects` closed too early.
- **Nonzero guard:** each trig theorem carries `magnitude a ≠ 0` / `magnitude b ≠ 0` (or `normSq ≠ 0`).
  This makes the cosine/sine form *faithful* — with a nonzero denominator `cos = 0 ⟺ dot = 0`, so it
  is no longer the weaker claim (the `0/0` case is excluded). The guard gates applicability even
  though the `zero_div` proof may not consume it (name it `_`-prefixed for the linter).
- The cosine/sine form is the **primary stated theorem**; the dot/wedge form stays as the underlying
  lemma it rests on (rewiring resolved).

**Python — raise on a zero operand** (the angle is undefined), matching the Lean guard:
- `MultiVectorBase.cosine`, `abs_sin`, `is_orthogonal_to`, `is_parallel_to`, and the generated
  `g2.Vector.sine` (via `tools/gen_specialized.py`) check for a zero operand and raise.
- `area`/`volume` are **not** guarded (they are `|wedge|`, no division; a degenerate area of 0 is
  meaningful).
- **Breaking change** (methods that returned a value/bool now raise) → `CHANGELOG.md` `[Unreleased]`
  entry; verify no test/notebook feeds a zero vector.

## Phase 2 refinements (2026-10-03) — naming + nbplotutils

- **Naming: cosine is an implementation detail, so the student theorem is named for the geometry.**
  The `StudentTrigForms.lean` theorems are `dual_perp`, `cross_perp_left/right`, `reject_perp`,
  `parallel_smul`, `dual_wedge_perp_left/right`, `proj_plane_perp_normal` (NOT `*_cos`/`*_sin`); the
  underlying scalar-product lemmas they rest on carry a `_dot` suffix (`dual_perp_dot`,
  `reject_perp_dot`, `cross_perp_left_dot`, …), renamed in their home files (`Predicates2D`,
  `Projection2D`, `Projection3D`, `Cross`). Convention recorded in `lean-ga-proof-architecture.md`.
- **`nbplotutils.sine`** also guarded (raises `ValueError` on a zero operand), matching the API
  methods.
- **Audit (your "did every dot-compared-to-zero caller get rewired?"):** yes — in Python the only
  `inner_product == zero` is inside `is_orthogonal_to` itself (now guarded), no stray call sites; in
  Lean the `dot … = 0` occurrences are the perp theorems' own statements, the deferred hypothesis-side
  `(h : dot = 0)` premises (follow-ups task), or steps already wired through `reject_perp_dot`.

`make lean` green; 672 pytest pass; ruff + ty clean.

## Follow-on (2026-10-03) — dead `_dot` helpers wired up (object-level)

The rename left the `_dot` helpers backing the cross/dual-wedge/parallel student theorems as
**coordinate-tuple** `(a1 a2 a3 … : ℝ)` lemmas that nothing cited (the cosine/sine theorems reproved
the fact inline), i.e. dead coordinate code. Fixed by the *appropriate* action — not deletion but
**wiring up**: lifted `cross_perp_left_dot`/`_right_dot` (`Cross.lean`),
`dual_wedge_perp_left_dot`/`_right_dot` (`Projection3D.lean`), and `wedge_parallel_smul`
(`Predicates3D.lean`) to **object-level** (`{a b : G3}` + `IsVector`), and had the student theorems
**cite** them (dropping the inline reproofs). Now every perp/parallel fact is: object-level `_dot`
lemma (no coefficients) ← object-level cosine/sine theorem, consistent across all of them. `make lean`
green. A broader dead-code audit of the whole proof corpus is its own task,
`tasks/lean-proofs-dead-code-audit.md`.

## Open questions

None — Phase 2 complete.
