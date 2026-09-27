# Investigate Lean 4 as a proof-checking layer for the GA derivations

**Status:** proposed — investigation done and all design questions answered by the author
(2026-09-27); needs an explicit go-ahead to start the learning spike / scaffold the Lean project
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

- [ ] **Learning spike, no repo changes yet:** stand up a throwaway Lake project in the container,
      pull Mathlib, and prove one trivial lemma end-to-end so the author can watch how a proof is
      made and how a Mathlib result is imported/cited. Write up "how proofs are made / how reuse
      works" in a short reference doc (`tasks/reference/lean-for-gacalc.md`).
- [ ] **Scaffold the real Lean project** under the repo at **`proofs/`** (decision Q2): `lakefile`,
      `lean-toolchain` pin, Mathlib dependency, one committed proof file.
- [ ] **First real proof — pseudoscalar square sign** (`I_r² = (−1)^(r(r−1)/2)`, decision Q5 — the
      `I²` form **only**, not `I·reverse(I)`): do the 2D and 3D cases from scratch, plus the general
      case, and add a note pointing at the Mathlib/general result if one exists.
- [ ] **Build gate:** add a **`make lean`** target (`: image` prereq) that fails on any
      `sorry`/extra axiom (warnings-as-errors and/or a `#print axioms` guard); verify a
      deliberately-broken proof turns it red.
- [ ] **CI wiring (decision Q3 — on tagged releases, not every push):** have GitHub Actions call
      `make lean` **on a `v*` tag**, NOT in the per-push `checks.yml`. Note: a tag-triggered workflow
      does **not exist yet** — releases are currently manual and a tag-triggered PyPI publish is only
      *proposed* in `tasks/github-actions-pypi-publish-on-tag.md`. So this step either adds a
      tag-triggered workflow or folds `make lean` into that proposed release workflow; coordinate with
      it. (The author said "gitlab" but this repo uses **GitHub Actions**.)
- [ ] **Go/no-go checkpoint with the author.** If go, split the remaining proofs into step-tasks:
  - [ ] Rotation from scratch (sin/cos → rotate a→b) → derive the geometric product → derive dot &
        wedge as its symmetric/antisymmetric parts.
  - [ ] Lagrange identity in the **squared** form `‖a‖²‖b‖² = (a·b)² + ‖a∧b‖²` (decision Q1 —
        confirmed against the Python: `notebooks/displayg2.py` L470–529 uses exactly this squared
        form, and it *is* the step that yields `sinθ = √(1−cos²θ)` and `|a||b|sinθ`), 2D and 3D
        separately (later higher grades).
  - [ ] Projection correctness, 2D and 3D, vector-onto-vector **and** vector-onto-plane (bivector),
        via the general formula (in 2D, deducible from the rotation-derived geometric product).
  - [ ] Each proof: from-scratch 2D/3D version **plus** a noted pointer to the general/Mathlib proof.

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
   general result each time.)
5. **Pseudoscalar statement → `Iᵣ² = (−1)^(r(r−1)/2)` ONLY** (not `Iᵣ·reverse(Iᵣ)`).

## Open questions

None — all five design questions are answered above. Remaining before work starts is only the
author's explicit **go-ahead to begin the spike** (this task is investigation-complete but not yet
approved to implement).
