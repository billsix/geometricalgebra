# Lean proof corpus — independent review of the 2026-09-29 → 2026-10-04 work

**What this is:** a read-only audit of the week's Lean commits (branch `leanProofs`, HEAD `c53fd7d`),
a Python → Lean coverage map, and a plain-language explanation of what the proofs' *hypotheses* mean,
written for the maintainer, who does not read Lean fluently. It states what is TRUE of the corpus on
2026-10-04; the actions it recommends are listed at the end as proposals (none applied). Companion
to `lean-ga-proof-architecture.md` (how the proofs are built) and `lean-for-gacalc.md` (orientation).

**Status:** written 2026-10-04 by the agent at the maintainer's request (William Emerison Six
<billsix@gmail.com>: "double check a lot of the work in the git commits over the past few days …
summarize what the lean work has done, how much of the python math code it has proven or not").
Three parallel read-only reviewers (commit audit, coverage map, goals/status) plus one build
experiment; see "Method" at the end.

## BLUF

- **The corpus is sound.** 383 theorems in 27 files; no `sorry`, `admit`, `axiom`, `native_decide`,
  `decide`, or `unsafe`; no theorem statement was weakened in the window. Every statement change was
  coordinate-literal → object form (equivalent), a nonzero guard restated as `normSq … ≠ 0`
  (equivalent), or a hypothesis *removed* (a generalization).
- **It proves the mathematics, not the Python.** Lean has its own `G2`/`G3` structs; `G3.mul`/
  `wedge`/`reverse` were transcribed from the Python `Gn` oracle and match it term for term (re-derived
  this review). Nothing in Lean imports or executes the Python. Two same-name traps: Lean `dot` is
  Python `scalar_product` (grade-0 part), not Python `dot` (Hestenes inner); Lean `cos_between` has no
  `reverse`, so it agrees with Python `cosine` on vectors only.
- **Coverage:** the vector-level core is proven in 𝒢₂ and 𝒢₃ (product laws, dot/wedge, reverse, dual,
  blade inverses, magnitude, project/reject/reflect of a vector, versor-from-vectors, the sandwich
  isometry and composition, the standard-position rotations, cross, area/volume, the student trig
  forms). **Not covered:** anything general-grade (Hestenes `inner_product`, general contractions,
  general `inverse`, `content`), anything general-n (`gn.py`, `g1.py`), `frame.py`, half-angle rotors
  in a general 3D plane, `exp` as a series, reflect across a bivector, the `transforms` plumbing.
- **One false claim in three committed docs.** The "𝒢₂ is more general than its 𝒢₃ twin; the 𝒢₃
  `dot_reverse_sandwich`/`normSq_reverse_sandwich` genuinely use the vector components" sentence
  (task doc, `CLAUDE.md`, architecture doc) is wrong: the identities hold for arbitrary multivectors
  in 𝒢₃ too, and the minimizer log shows those drops were never built (`skip … could not edit
  cleanly`), so "build failed, reverted" was a hand-reasoning error. Build experiment: see §5.
- **Docs drifted:** `proofs/README.md` cites two files that no longer exist and lists 11 of 27 files;
  the umbrella task's checklist and open questions are stale; several Lean module docstrings cite
  renamed files; `Predicates3D.lean` still reports a Python bug fixed on 2026-10-01.

## 1. What a hypothesis is, and when one is "needed" — for the maintainer

A Lean theorem is `theorem name (inputs) (hypotheses) : conclusion := by proof`. The hypotheses are
the preconditions the conclusion is claimed under. In this corpus they come in three kinds:

| Kind | Example | What it says | If dropped |
|---|---|---|---|
| Grade predicate | `(ha : IsVector a)` | "`a` has only grade-1 components" (the other 5 getters are 0) | the theorem claims the identity for *every* multivector `a` — true for some identities (e.g. the reverse-sandwich scalings), false for others (e.g. `a ∧ a = 0` fails for a general multivector) |
| Nonzero guard | `(hr : normSq R ≠ 0)`, `(ha : dot a a ≠ 0)` | "we may divide by this" | Lean defines `x / 0 = 0`, so a division-based statement becomes a junk-value claim; the proof's `field_simp` needs the guard to cancel |
| Meaning gate | `(_ha0 : magnitude a ≠ 0)` in `StudentTrigForms` | "the cosine of the angle is meaningful" — not used by the proof, kept so the *statement* excludes the `0/0` case | nothing breaks; the theorem would then say a vacuous `cos = 0` about the zero vector. The `_` prefix marks "deliberately unused" to the linter and the reader |

Two different questions hide behind "is this hypothesis needed?":

1. **Needed for the statement to be true?** A mathematical question. If the identity holds without it,
   the hypothesis only *weakens* the theorem (fewer callers can use it) — harmless but misleading. Lean's
   `unusedVariables` linter DOES warn ("Variable name `hu` is not explicitly referenced") — the
   committed tree already emits 5 such warnings for the 𝒢₂ composites and `dual_wedge_perp_right`,
   contradicting the task doc's note that it never flags signature hypotheses; read the build's warnings.
2. **Needed for this particular proof script to close?** A tactical question. The getter-style proofs
   do `obtain ⟨zeros⟩ := ha; simp only [defs, zeros]; ring`: the zeros shrink the polynomial that
   `ring` must normalize. A proof can *fail* without a hypothesis the statement does not need, because
   `ring` runs out of its heartbeat budget on the bigger polynomial. So **a failed delete-and-rebuild
   proves only that THIS proof needs it, not that the theorem does.** A heartbeat/timeout error says
   "restructure the proof" (prove the small algebraic reason, e.g. `R R̃ = |R|²·1`, then use
   associativity and the cyclic scalar part); a genuine counterexample-shaped failure ("`ring` failed,
   goal not closed", with a residual polynomial) says "the hypothesis is mathematically required".

The corpus's own rule ("name-absent ≠ unused — decide by delete-and-rebuild") is right as far as it
goes; the missing half is the distinction above. Reading a failed build is part of the method.

A fourth thing that LOOKS like a needed hypothesis but is not: `simp only [...]` silently ignores a
zero-fact that never fires, so a long `simp` list says nothing about what the proof relies on. The
2026-10-04 minimizer (archived task) removed 73 such entries; the
trimmed lists are now honest documentation of what each polynomial proof touches.

## 2. What the Lean work did this week (commit audit, condensed)

Per-commit detail is in the task archive (`tasks/archive/2026/09/29/`, `09/30/`, `10/01–04/`); the audit
checked each proof commit's theorem statements against its task doc's claims. Findings:

- **09-29:** algebra laws (associativity, distributivity, identity, scalar laws), the versor suite
  (bisector, `versorFromVectors`, `R R̃ = |R|²`, sandwich carries a→b, composition, fixes its own plane
  and normal, the three matrix-free rotation goals), Hestenes project/reject/graded inner for vectors,
  magnitude unification. 8 tasks archived.
- **09-30:** coordinate-free property algebra (`IsVector`, bilinearity both sides, `mul = dot + wedge`),
  reverse anti-automorphism, standard-position rotations and alignment, cross/dual/signed volume, the
  Python `standardposition.py`. The maintainer corrected the draft from versors to elementary rotations.
- **10-01:** contractions, exp closed form, grade projection, measures, normalize, predicates, reflect
  ported; **Python `is_parallel_to` fixed** to the wedge-zero criterion; the 3-rotation cross reduction.
- **10-02/03:** file renames by topic with `2D`/`3D` suffixes; student sine/cosine forms; the big
  object-in/getters-in-body lift (~70 signatures, commit `43571f3`, message "more lean claude code
  work" — content recorded in the archived task, not the message).
- **10-04:** `simp` minimizer run (73 drops, build-verified); hypothesis generalizations in 𝒢₂ and for
  the wedge leaves in 𝒢₃; the false asymmetry note (§5).

Nothing suspicious in proof *content*. The `ring` "Try this: ring_nf" messages for
`CrossStandardPosition.lean` (`cross_reduced`, `ext <;> ring`) are info-level: Mathlib's `ring` falls
back to `ring_nf`, which closes the goal; pre-existing, not an error. Two heavy budgets exist (`maxHeartbeats 8000000`/`4000000`,
`maxRecDepth 8000`, four `_coord` theorems in `ProjectionRotation3D.lean`), introduced with the
theorems, sound but fragile; their docstrings describe a structural route that would remove them.
`proofs/lakefile.toml` leaves `autoImplicit` at its default `true`, so a typo'd identifier in a
statement becomes a silently bound variable — `autoImplicit = false` is the safer setting for a proof
corpus. The "axioms gate" in `check.sh` is a `sorry`/`admit` grep; a real `#print axioms` sweep would
also catch `native_decide`/`axiom` (none present today).

## 3. Coverage map — Python math → Lean (vectors unless noted)

| Python | Lean | Verdict |
|---|---|---|
| geometric product, `wedge`, `reverse`, `scalar_product` | `mul`/`wedge`/`reverse`/`dot`, `AlgebraLaws.lean`, bilinearity, antisymmetry | **proven**, 𝒢₂+𝒢₃ |
| `dual`, `inverse` (blades, even versors), `magnitude(_squared)` | `dual`, `inverse`, `normSq`/`magnitude` + `mul_*_inverse_self` | **proven** for n=2,3 |
| `r_vector_part`, `even_part`/`odd_part`, grade predicates | `GradeProjection.lean`, `IsVector`/… | **proven** |
| `project`/`reject`/`reflect` of a vector | `Projection2D/3D.lean`, `Reflect.lean` (𝒢₃, across a vector) | **proven** for vector operand onto vector/bivector; reflect across a bivector and reflect∘reflect = id **not stated** |
| `versor_from_vectors`, `sandwich`, `transforms.projection_rotation` / `versor_rotation` | `Rotation3D`, `Versor2D`, `Sandwich`, `RotateComponents`, `ProjectionRotation2D/3D` (incl. `projRotation_eq_sandwich`) | **proven** (forward); `backward ∘ forward = id` not stated |
| `standardposition.project_sp` | `StandardPosition.lean` equivariance + alignment | **proven by ingredients**; no single `project_sp = project` theorem although `CLAUDE.md` and the Python docstring say "proven equal" |
| `cross`, `area`, `volume`, signed area/volume, `cosine`/`abs_sin`/`sine` | `Cross`, `Measures`, `Lagrange`, `Trig`, `TrigEquiv`, `StudentTrigForms` | **proven** (𝒢₃; Lagrange also 𝒢₂) |
| `is_orthogonal_to`, `is_parallel_to` | `Predicates2D/3D` | proven / **half** (`a ∧ ka = 0` only; the converse "wedge zero ⇒ dependent" unstated) |
| `exp` | `Exp.lean` closed form is a unit versor | **partial** (no series, no scalar or pseudoscalar case) |
| `transforms.bivector_rotation`/`plane_rotation` (half-angle rotor) | `Rotation2D.sandwich_versor` | **𝒢₂, plane e₁₂ only**; no 𝒢₃ general-plane angle theorem; `at(t)` law unstated |
| Hestenes `inner_product`/`dot`, `left_/right_contraction` (general grades) | vec·vec, vec·biv, scalar·vec cases only | **partial**; owned by `tasks/lean-general-gn-product-and-hestenes-dot-wedge.md` |
| general `inverse`, `content`, `pseudoscalar_squared_sign(r)` general r | — | **none** (tasks exist) |
| `gn.py`, `g1.py`, `frame.py`, `normalize` of non-vectors, `translate`/scales/`to_matrix`/`compose` | — | **none** (`Gn` is the oracle Lean was derived from, not a theorem) |

The architecture doc's "29 HAS / 2 PARTIAL / 1 NONE of 32 methods" tally is accurate only with a
"for vector operands, n ∈ {2,3}" qualifier, and its surface excludes `transforms.py`,
`standardposition.py`, `frame.py`, `gn.py`, `g1.py`, `functions.py`.

What Lean proves that Python does not implement: the algebra laws as theorems (Python only tests
them), the 2D angle-form rotation theory (`rot`, `polar`, `rot_from_to`), `rotYZ` and a uniform
`reduceToPlane`, versor-product composition (`sandwich_comp`, `inverse_mul`, `normSq_mul`),
`dot_is_sym_part`/`wedge_is_antisym_part`, `I_sq_eq_sign` (n=2).

## 4. Goals vs status

| Goal (where stated) | Status |
|---|---|
| A private machine-checked oracle for the *math* behind the derivations, not the Python (umbrella BLUF; archived to `tasks/archive/2026/10/04/investigate-lean-proofs-for-ga.md`) | **met** |
| Fails like a unit test: `make lean` + `check.sh` + CI on `v*` tags | **met** |
| From-scratch proofs, with an equivalence to Mathlib's general machinery per deliverable (umbrella decision 4) | **half**: from-scratch done for 2D+3D; the Mathlib-equivalence half is unstarted in all four step tasks (rotation, dot, wedge, pseudoscalar) |
| Matrix-free rotation (three geometric goals) | **met** 09-29 |
| Coordinate-free proofs, then coordinate-free statements ("objects in, scalars in the body, objects out") | **met** for the polynomial tier; the sqrt/`calc` tier retained by decision (`tasks/push-delicate-coordinate-core-tier.md`) |
| Non-circular bootstrap via standard position | **met in Lean**; book voice pass and cross capstone open |
| Every public Python math method has a Lean theorem | **met for vectors in n ∈ {2,3}** (see §3 qualifier) |
| Students see sine/cosine, not dot/wedge | **met** (first pass) |
| Lean → symbolic tests → student-verifiable proof notebooks | **open**, both tasks `proposed` |

Open Lean tasks, easy wins first: `trim-unused-simp-components` (done, archive owed),
`rename-rotor-to-versor` (done; archived 2026-10-04 with rotation-from-scratch),
`reference-doc-lean-workflow-and-proof-notebooks` (P6/D4, 3 open questions),
`lean-unit-versors-rotors-sandwich-with-reverse` (P6/D6, 3 questions), `reduce-to-standard-position`
(voice pass), `lean-cross-standard-position-capstone` (2 questions), the four P7 step tasks
(dot/wedge/pseudoscalar/rotation — only Mathlib equivalence left), `lean-general-multivector-inverse`,
`investigate-lean-to-python-proof-notebooks`, `push-delicate-coordinate-core-tier` (P8),
`grade-simp-tactic` (P9, maintainer undecided), `lean-general-gn-product` (P9, deferred).

## 5. The "𝒢₃ asymmetry" claim — false, and why

Claim (in `tasks/trim-unused-simp-components.md`, `CLAUDE.md` "Coordinates only when needed", and
`lean-ga-proof-architecture.md` "Mind grade asymmetry"): 𝒢₂'s `dot_reverse_sandwich` and
`normSq_reverse_sandwich` hold for arbitrary `u`, `v` but the 𝒢₃ twins need `IsVector u`/`IsVector v`.

Why it is false. Let `R` be even in 𝒢₃ (`R = s + B`) and `n = normSq R`. A 3D bivector squares to a
scalar, so `R R̃ = s² − B² = n·1`, and `R̃ R` is the same scalar (the leaf `mul_biv_reverse_self` is
already in the tree). The scalar part of a product is cyclic — `dot_comm` in `G3.lean` states
`⟨AB⟩₀ = ⟨BA⟩₀` for arbitrary `A`, `B` with no hypotheses. Then, by associativity alone:

```
⟨(R u R̃)(R v R̃)⟩₀ = ⟨R u (R̃ R) v R̃⟩₀ = n·⟨R (u v) R̃⟩₀ = n·⟨(u v) R̃ R⟩₀ = n²·⟨u v⟩₀
normSq (R v R̃)    = ⟨R v R̃ R ṽ R̃⟩₀    = n·⟨R (v ṽ) R̃⟩₀  = n²·⟨v ṽ⟩₀
```

No step looks at the grade of `u` or `v`. The 𝒢₃ wedge twins (`wedge_reverse_sandwich`,
`normSq_reverse_sandwich_wedge`) were already generalized the same day and built green with full
8-component `u`, `v`, so `ring` closures of this size are known to succeed.

Why the claim arose: the minimizer log (deleted at archive; the lines are quoted in
`tasks/archive/2026/10/04/trim-unused-simp-components.md`, 02:42) recorded every 𝒢₃ `dot_reverse_sandwich` component drop as `skip (could not edit cleanly)` — the tool
never built them — and the task doc's "my first over-eager attempt to drop the G3 ones (build failed,
reverted)" has no corroborating log. Build experiment (this review, direct `proofs/check.sh` against the
existing image with the two 𝒢₃ leaves and their callers generalized): **green** — `[lean] OK`, 0 errors, `Sandwich` rebuilt in 70 s, full gate 4m42s (the generalization was then applied with structural proofs and the cascade, go-ahead given the same day). The only new output was the unused-variable linter flagging the composites' now-vacuous `hu`/`hv` (6 in `Sandwich.lean`, 4 in `Projection2D.lean`, 1 in `StudentTrigForms.lean`).

Consequences once the 𝒢₃ leaves are general: the composites still carrying vacuous vector hypotheses
become droppable in both grades — `sandwich_preserves_dot`, `sandwich_preserves_normSq_of_vec`,
`sandwich_preserves_wedge`, `sandwich_preserves_normSq_of_wedge`, and by cascade
`magnitude_sandwich_vec`, `sandwich_preserves_cos`/`_sin`; the whole isometry chain is grade-agnostic.
Also `StudentTrigForms.dual_wedge_perp_right` still carries an `ha` its body never uses (the 10-04
caller update missed its own signature). The three docs' asymmetry sentences should be deleted, and
the 𝒢₂ docstrings that still say "for an even versor and vectors" (`Sandwich.lean` top of file)
corrected.

## 6. Documentation drift found (verified with `ls`)

- `proofs/README.md`: cites `GacalcProofs/Projection.lean` and `GacalcProofs/Rotation.lean` (renamed
  2026-10-02 to `Projection3D.lean`, `Rotation2D.lean`); "What's here" names 11 of 27 files; "What's
  planned" lists work finished 09-29. `tasks/lean-proof-rotation-from-scratch.md` (since archived to `tasks/archive/2026/10/04/`) had the unchecked
  "[ ] Update `proofs/README.md`".
- Module docstrings citing old names: `G2.lean`, `Versor2D.lean`, `TrigEquiv.lean` (`Rotation.lean`);
  `Projection2D.lean` (`Projection.lean`); `ProjectionRotation2D.lean` (`ProjectionRotation.lean`).
- `Predicates3D.lean` docstring: "Discrepancy reported: the Python `is_parallel_to` instead tests
  `cosine == 1`" — fixed in Python 2026-10-01; the comment now describes history.
- `lean-ga-proof-architecture.md`: cites `cross_anticomm_vec` (now `cross_anticomm`) three times; two
  line-number anchors (forbidden by convention) have rotted; the file inventory (dated 09-29) omits 11
  files the coverage table below it cites; header "Status: written 2026-09-29" though the body carries
  10-03/10-04 material.
- `CLAUDE.md` cites `tasks/prefer-sine-cosine-presentation.md` (archived to
  `tasks/archive/2026/10/03/`); `tasks/reference-doc-lean-workflow-and-proof-notebooks.md` cites
  `tasks/bootstrap-change-of-frame-definitions.md` (never created; the theme became
  `reduce-to-standard-position.md`).
- Umbrella `tasks/investigate-lean-proofs-for-ga.md` (since archived to `tasks/archive/2026/10/04/`): open questions still await "go-ahead to begin the
  spike" (done); G3 marked `[~]` pending projection (done); archives since 09-30 not listed.
- Lean docstrings cite `base.py` line numbers that have rotted (`exp`, `dual`, `even_part`,
  `reflect`, `is_parallel_to`).
- `tasks/trim-unused-simp-components.md` was DONE but unarchived (archived 2026-10-04 to
  `tasks/archive/2026/10/04/`, minimizer deleted, detector promoted to `tools/detect_unused_hypotheses.py`).

## 7. Actions taken (all on 2026-10-04, on the maintainer's go-ahead; `make lean` green)

Items 1–5 below were applied the same day; item 6 became `tasks/lean-coverage-extend-transforms-frame-gn.md`,
which also covered the out-of-scope modules of §3 (𝒢₁, standard position, the sandwich round-trip), with
the 3D rotor angle theorem and frames spun into `tasks/lean-rotor-3d-angle-theorem.md` and
`tasks/lean-frame-coverage.md`.

1. Commit the 𝒢₃ generalization of `dot_reverse_sandwich`/`normSq_reverse_sandwich` (if the build
   experiment is green), then drop the vacuous vector hypotheses from the composites listed in §5, and
   delete the asymmetry sentences from the three docs. One unit, build-verified.
2. Replace the brute `ring` proofs of the two leaves with the 6-line structural proof of §5 (a
   `mul_reverse_self_of_isEvenVersor` leaf + associativity + `dot_comm`) so the proof records the
   *reason*; also removes the risk of heartbeat failure.
3. Fix the drift in §6 (README rewrite from the real file list; docstring renames; the two stale
   `CLAUDE.md`/task pointers; umbrella checklist).
4. Set `autoImplicit = false` in `proofs/lakefile.toml` and rebuild.
5. Qualify the architecture doc's coverage tally ("vector operands, n ∈ {2,3}") and add the
   out-of-scope modules (`transforms`, `standardposition`, `frame`, `gn`, `g1`, `functions`) to it.
6. For the half-angle 3D rotor (gap #4 in §3): file a task for "sandwich by `cos(θ/2) − sin(θ/2)·i`
   rotates by θ in the plane of `i`" in 𝒢₃, since `transforms.bivector_rotation`/`plane_rotation`
   rest on it and only the e₁₂ 𝒢₂ case is proven.

## Method

Three read-only reviewers ran in parallel on 2026-10-04 (commit-by-commit audit with
statement-meaning checks; Python → Lean coverage with definition-parity re-derivation via
`tools/derive_lean_algebra.py`; goals/status/contradictions from the task and reference docs), followed
by the §5 build experiment. No file other than this one was edited; `Sandwich.lean` carried the
experiment's uncommitted edit during the review.
