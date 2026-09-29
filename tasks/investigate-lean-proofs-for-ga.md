# Investigate Lean 4 as a proof-checking layer for the GA derivations

**Status:** in-progress — both learning spikes complete and verified (2026-09-27/28); the author
greenlit scaffolding the real `proofs/` project (2026-09-28). This task is now the **umbrella**; the
individual from-scratch proofs become step-tasks (see the Plan).
**Priority:** 6
**Difficulty:** 7
**Started:** 2026-09-27 (William Emerison Six <billsix@gmail.com>)

## BLUF

Decide whether Lean 4 + Mathlib is worth adopting as a **private, machine-checked proof layer** that
verifies the *mathematics* behind gacalc's derivations (rotation → geometric product → dot/wedge,
projection, the Lagrange identity, the pseudoscalar-square sign) — a way for the author to check his
own work, **not** student-facing material. "Done" for this investigation = a tiny spike proof
builds under `lake`, is wired into `make` + CI so a failed/incomplete proof errors out exactly like
a failing unit test, and the author has seen enough of the workflow (how proofs are made, how to
reuse Mathlib) to decide go/no-go on the fuller proof list. If go, this task spawns step-tasks for
each proof.

## Context — read first

- **The repo already ships the Lean toolchain but has no Lean project yet.**
  `entrypoint/install-lean.sh` installs Lean 4 via `elan` (stable `lean` + `lake`), gated behind the
  `USE_LEAN` build flag (Dockerfile `ARG USE_LEAN=0`; Makefile `USE_LEAN ?= $(if $(filter
  1,$(MINIMAL_IMAGE)),0,1)` — full image only, dropped by `MINIMAL_IMAGE=1`). There is **no**
  `lakefile.lean`/`lakefile.toml`, no `lean-toolchain` pin, and no `.lean` sources. So step one of any
  adoption is scaffolding a Lake project and pinning a toolchain.
- **The book's derivation spine this is meant to check** (`tasks/reference/book-outline.md`,
  §C/§E/§F, and the verbatim appendix): define **sine/cosine from geometry**, define **rotate** as
  "from the direction of vec 1 to vec 2, magnitudes don't matter" (MVP-style), and **from rotate
  define the geometric product**; projection and reflection are built on rotate. Dot and wedge are
  then the **symmetric / antisymmetric parts** of the geometric product (`a·b = ½(ab+ba)`,
  `a∧b = ½(ab−ba)`). (The author's recollection in the request is essentially correct; the one
  refinement is that dot/wedge are *derived as the two parts of the product*, not a separate
  from-scratch construction.)
- **The pseudoscalar-square result already has a hand proof** in
  `tasks/reference/pseudoscalar-square-sign.md`: `I_r² = (−1)^(r(r−1)/2)` in Euclidean 𝒢ₙ, by
  swap-counting (grades 1–5) then induction, plus a `reverse`-based one-liner. A Lean proof of this
  is the natural **first real proof** (small, self-contained, already understood on paper). See
  Open question 5 about the exact statement to formalize.
- **What Lean/Mathlib already provides (the "reuse others' work" answer):**
  - *Dot product in arbitrary dimension is a definition + theorems, NOT an axiom.* Mathlib4 has
    `InnerProductSpace` / `EuclideanSpace` (`Mathlib.Analysis.InnerProductSpace.*`), built up from
    the field/vector-space axioms — you get the dot product and its properties (bilinearity,
    symmetry, Cauchy–Schwarz) as **proved theorems** to cite, not postulates.
  - *Geometric algebra exists in Mathlib* as `CliffordAlgebra` (`Mathlib.LinearAlgebra.CliffordAlgebra.*`),
    with the exterior-algebra and even-subalgebra machinery.
  - `pygae/lean-ga` (same org as **galgebra**, gacalc's comparison baseline) is a partial GA
    formalization (versors, CGA, ℝ/ℂ/ℍ isomorphisms) — **but it is Lean 3 / mathlib3**, and much of
    it has graduated into Mathlib. Treat it as a *reference/reading source*, not a dependency; the
    practical reuse path is **Mathlib4's `CliffordAlgebra` + `InnerProductSpace`**.
- **The crux to internalise before investing (the key distinction):** a Lean proof checks that the
  **mathematics is sound** — it says nothing about whether gacalc's *Python* implements that math.
  It is an *independent* second source of truth (like the existing `Gn`-vs-`G` oracle tests, but for
  the derivations rather than the code), matching the author's stated intent ("a way for me to check
  my work"). Verifying the Python itself against Lean is a much larger, separate undertaking and is
  **out of scope** here.
- **Build/CI gating (the "fail like a unit test" answer):** `lake build` treats an incomplete proof
  (`sorry`) only as a *warning*, so a naïve `lake build` can pass with holes. To make a hole/failed
  proof **error out** (in `make` and therefore CI, per the repo's "multi-step check script must
  propagate every step's failure" and "CI = thin wrapper over make targets" conventions), use one
  (or both) of: `lake build` with warnings-as-errors, and/or a `#print axioms` guard asserting every
  theorem depends only on `[propext, Classical.choice, Quot.sound]` (presence of `sorryAx` or a
  user axiom = incomplete). `lean4checker` is the belt-and-suspenders kernel re-check. This becomes
  a new `make lean` (or `make check-lean`) target with `: image` as a prereq, added to `checks.yml`
  as a fourth check-only job — but see Open question 3 on the CI cost/time trade-off.

## Goal

Determine whether the author can realistically use Lean 4 as part of his gacalc work — first by
*understanding it* (how proofs are constructed, how Mathlib results are reused vs. what is axiomatic)
and then by *proving it out* on a small spike that is wired into the build and CI so a broken proof
fails the build exactly like a unit test. The proofs are **private checks of the author's own
derivations**, never student material. If the spike lands and the author decides to proceed, this
task becomes an umbrella that spawns one step-task per proof on the list below.

## Plan

*(Sequenced; the first two are the real go/no-go gate — do not batch the whole proof list before the
author has seen the workflow.)*

- [x] **Learning spike — phase 1 (pure Lean, no Mathlib), DONE 2026-09-27.** Proved trivial lemmas
      end-to-end in the container; confirmed the reliable CI gate is **`#print axioms` grep for
      `sorryAx`** (a `sorry` proof warns but exits 0, so a bare build is insufficient). Wrote up the
      beginner orientation in `tasks/reference/lean-for-gacalc.md`. Harness:
      `tasks/adhoc/investigate-lean-proofs-for-ga/spike-pure-lean.sh`. Gotchas found: use a `lib` (not
      `exe`) target to avoid a clang link step; `-DwarningAsError` is not valid in Lake 5.0.0; don't
      mask exit status through a `| tail` pipe. See the reference doc's "What the spike actually
      showed".
- [x] **Learning spike — phase 2 (Mathlib reuse), DONE 2026-09-28.** `import Mathlib` + `lake exe
      cache get` works; proved the **2D Lagrange identity** with `ring`, and cited `real_inner_comm`
      (dot-product symmetry, arbitrary dimension). `#print axioms` on all three (incl. Mathlib's own)
      reported only `[propext, Classical.choice, Quot.sound]` — so the dot product is **proved, not an
      axiom**. Harness: `tasks/adhoc/investigate-lean-proofs-for-ga/spike-mathlib.sh`. Findings folded
      into the reference doc; **two carry into the real build (see below).**
      - **git must be in the image** — added to `entrypoint/install-lean.sh` under `USE_LEAN` (lake
        needs it to clone Mathlib). **This is a permanent addition; needs the maintainer's OK to keep**
        (the image otherwise ships no git by design). It is staged.
      - **Offline gap** — phase 2 fetched Mathlib at *runtime* (network), violating gacalc's
        bake-deps-at-build rule. The real `proofs/` setup must clone+`cache get`+build Mathlib **into
        the image** under `USE_LEAN` so an exported image is offline. This is a design item for the
        scaffold step.
- [x] **Scaffold the real Lean project — DONE 2026-09-28.** `proofs/` generated by `lake init
      GacalcProofs math` (so the Mathlib pin is lake's own): `lean-toolchain` = `v4.34.1`,
      `lakefile.toml`/`lake-manifest.json` pin Mathlib, `.lake/` gitignored. First proofs landed and
      `make lean` green — see next.
- [x] **First proofs landed — 2D DONE 2026-09-28; 3D/general moved to step-tasks.** Landed and
      `make lean`-green: `GacalcProofs/Lagrange.lean` (Lagrange 2D **and** 3D by `ring`) and
      `GacalcProofs/G2.lean` — a from-scratch 𝒢₂ with the geometric product, proving **dot =
      symmetric part**, **wedge = antisymmetric part**, dot ≡ the coordinate sum (equivalence to the
      general dot), and the **pseudoscalar** `I₂² = −1 = (−1)^(r(r−1)/2)` (decision Q5). The 3D
      versions, the general pseudoscalar, and the from-*rotation* derivation are the step-tasks below.
- [x] **Build gate — DONE 2026-09-28.** `make lean` (`: image` prereq) runs `proofs/check.sh`:
      `lake build` + a completeness gate that fails on any `sorry`/`admit` in the sources (namespace-
      agnostic; `#print axioms`/`sorryAx` stays the manual gold-standard check). Failure-propagating,
      portable (container + host).
- [x] **Offline-baking — DONE 2026-09-28.** The Dockerfile bakes Mathlib into `/opt/gacalc-proofs/.lake`
      (a committed layer outside the mount, gated on `USE_LEAN`); `check.sh` copies it into the mounted
      `proofs/.lake` when absent, so `make lean` runs offline (the mount would otherwise shadow a baked
      `proofs/.lake`). Adds several GB to a Lean image — only `USE_LEAN` images pay it.
- [x] **CI wiring — DONE 2026-09-28.** `.github/workflows/lean.yml` runs `make lean` on a `v*` tag
      (decision Q3 — not per-push), matching the repo's thin-wrapper CI style. (The author said
      "gitlab"; this repo uses **GitHub Actions**.) Coordinate with the still-proposed
      `tasks/github-actions-pypi-publish-on-tag.md` if a combined release workflow is wanted later.
- [x] **Go/no-go checkpoint — GO (author, 2026-09-28).** The spike answered the feasibility
      questions (proofs check; reliable gate; Mathlib reuse works; dot product is proved not
      axiomatic). Proceeding to scaffold + step-tasks.

**Step-tasks (created 2026-09-28)** — each doc carries the full structure (*special-case 2D then 3D
via the book's rotation methods* + *equivalence to the general case* + *reference to the existing
Mathlib/general proof*; per decisions 4–5). Status is per that doc; the 2D coordinate results already
live in `proofs/` (see above), so several are `in-progress`:

  - [ ] `tasks/lean-proof-rotation-from-scratch.md` — sin/cos → rotate a→b → geometric product →
        dot & wedge as its parts (the shared foundation; hardest, D8). **2D core landed 2026-09-28**
        (`proofs/GacalcProofs/Rotation.lean`: product enacts rotation, product of unit vectors = rotor
        of the angle, dot/wedge read off); 3D + general-vector framing + Mathlib equivalence remain.
  - [ ] `tasks/lean-proof-dot-product.md` — 2D landed (`G2.dot_is_sym_part`/`dot_eq_coord_sum`);
        from-rotation derivation + 3D remain.
  - [ ] `tasks/lean-proof-wedge-product.md` — 2D landed (`G2.wedge_is_antisym_part`); from-rotation
        + 3D remain.
  - [ ] `tasks/lean-proof-pseudoscalar-square-sign.md` — 2D landed (`G2.I_sq`/`I_sq_eq_sign`); 3D +
        general remain.
  - [ ] **Lagrange identity** — 2D **and** 3D already landed (`GacalcProofs/Lagrange.lean`); no
        separate step-task needed (the `ring` proofs are complete; the rotation-derivation framing is
        covered by the rotation step-task).
  - [ ] `tasks/lean-proof-projection.md` — 2D/3D, onto-vector and onto-plane; the projection
        decomposition (`(A·B)B⁻¹`). **Planned as the next 3D work (2026-09-29), sequenced BEFORE the 3D
        versor sandwich** — proving it reduces the 3D sandwich to the (done) G2 sandwich. Its gating
        prerequisite is a from-scratch **`G3`** (see below).
  - [x] `tasks/archive/2026/09/29/lean-proof-2d-dual-perpendicular.md` — **DONE + ARCHIVED 2026-09-29**:
        the dual of a vector is ⊥ the vector, in 𝒢₂ (`G2.dual`/`dual_vec`/`dual_vec_perp`, `make lean`
        green). Warm-up for projection's 3D dual/normal step.
  - [~] **From-scratch `G3`** (8-dim) — the shared prerequisite for the 3D versions of projection, dot,
        wedge, pseudoscalar, and the rotation sandwich. **Core LANDED 2026-09-29**
        (`proofs/GacalcProofs/G3.lean`: product+wedge+reverse transcribed from gacalc's `Gn`, basis
        elements, multiplication table, I₃²=−1; `make lean` green). Remaining: dot/`I₃⁻¹`/`dual`/`project`
        (added as `lean-proof-projection.md` needs them). Unblocks the other 3D step-tasks.

## Notes / decisions

- Investigation performed 2026-09-27 (web + repo read). Sources are cited inline in Context.
- The proof deliverables and the "run in the build / fail CI like a unit test" requirement come
  directly from the author's request; the sequencing (spike first, decide, then fan out) is proposed
  by the agent to keep the learning cost bounded before committing.

## Decisions (author, 2026-09-27 — the five design questions, now settled)

1. **Lagrange-identity form → the squared form** `‖a‖²‖b‖² = (a·b)² + ‖a∧b‖²`. The author's original
   `|a||b| = |a·b| + |a∧b|` phrasing was the non-squared version; verified in Python that the code
   uses the squared form (`notebooks/displayg2.py` L470–529, the `lagrange_residual == 0` cell) and
   that it drives the sin/cos derivation (`sinθ = √(1−cos²θ)`, `|a||b|sinθ = √(‖a‖²‖b‖² − (a·b)²)`).
2. **Location + target → `proofs/` for sources, `make lean` for the gate** (mirrors `make test`).
3. **CI → on tagged releases only, not per push.** `make lean` is its own target, called by GitHub
   Actions on a `v*` tag. Caveat carried into the Plan: the tag-triggered workflow doesn't exist yet
   (releases are manual; tag-triggered publish is only *proposed* in
   `github-actions-pypi-publish-on-tag.md`), so wiring it means adding that workflow or folding into
   the proposed one.
4. **Reuse posture → every proof from scratch, as standalone as possible;** learning from and
   *referencing* others' Lean proofs is welcome, but no proof should *depend* on external GA
   formalizations. (Mathlib as the ambient library is fine; a from-scratch proof + a pointer to the
   general result each time.) **Refined 2026-09-28:**
   - The **dot product** and the **wedge product** each get the author's **own from-scratch proof in
     2D and in 3D**, derived via the **book's rotation-based methods** (dot/wedge as the
     symmetric/antisymmetric parts of the rotation-derived geometric product) — *not* by citing the
     general Mathlib theorem as the proof.
   - Each such proof is explicitly a **special case**, and is paired with a proof that the special
     case is **equivalent to the general case** (i.e. the 2D/3D rotation-derived quantity equals the
     general definition — Mathlib's `@inner`/wedge, or gacalc's general formula). So each deliverable
     = *(special-case proof) + (equivalence-to-general proof) + (reference to the existing general
     proof)*.
5. **Pseudoscalar statement → `Iᵣ² = (−1)^(r(r−1)/2)` ONLY** (not `Iᵣ·reverse(Iᵣ)`); same special-case
   (2D, 3D) + general-case + equivalence structure applies.

## Open questions

None — all five design questions are answered above. Remaining before work starts is only the
author's explicit **go-ahead to begin the spike** (this task is investigation-complete but not yet
approved to implement).
