# Lean 4 for gacalc — a beginner's orientation

**What this is:** a from-zero introduction to the Lean 4 theorem prover, aimed at a reader who has
never used a proof assistant, written specifically for the gacalc project's goal of *machine-checking
the mathematics behind the geometric-algebra derivations*. It states what is true about Lean and how
we intend to use it; the live plan and open decisions are in the task
`tasks/archive/2026/10/04/investigate-lean-proofs-for-ga.md` (archived), not here.

**Status:** living document, updated in place. Written 2026-09-27 (William Emerison Six
<billsix@gmail.com>) during the learning spike; reconciled 2026-10-04 after the proof program completed.
Sections marked *(spike-confirmed)* were run in this repo's container; the rest is general Lean 4
knowledge.

## The one thing to understand first: what a Lean proof does and does NOT check

A Lean proof checks that a piece of **mathematics** is correct — that a statement follows, by pure
logic, from definitions and previously-proved results. When Lean accepts a proof, a small trusted
program (the **kernel**) has verified every step down to the axioms; there is no "probably right."

What a Lean proof does **not** do: it says nothing about whether gacalc's **Python** code implements
that mathematics. Lean checks the *idea* (e.g. "the wedge magnitude squared equals
‖a‖²‖b‖² − (a·b)²"); the Python tests (`Gn` vs the generated `G`, ~650 of them) check the *code*.
For gacalc, Lean is a **second, independent source of truth for the derivations** — a way for the
author to check his own math on paper — sitting alongside, not replacing, the test suite. Verifying
that the Python matches the Lean is a much larger, separate effort and is out of scope.

## The pieces of the toolchain (and how they nest)

- **Lean** — the language and its checker. You write `.lean` files; `lean Foo.lean` elaborates and
  kernel-checks them. *(spike-confirmed: Lean 4.34.1 in this repo's container.)*
- **elan** — the *version manager* for Lean (think `pyenv`/`rustup`). It installs toolchains and
  picks the right one per project. Installed here at `~/.elan/bin` by `entrypoint/install-lean.sh`.
- **lake** — Lean's *build tool and package manager* (think `cargo`/`pip`+`make` in one). It reads a
  `lakefile.toml` (or `lakefile.lean`), fetches dependencies, and builds your `.lean` files in order.
  *(spike-confirmed: Lake 5.0.0.)*
- **`lean-toolchain`** — a one-line file in a project pinning the exact Lean version. elan reads it
  and auto-selects that toolchain, so everyone (and CI) builds with the same compiler. **Pin it**;
  Mathlib in particular only builds against the exact Lean version it was released for.
- **Mathlib** — the community mathematics library (over 1.7M lines). You add it as a lake dependency
  to get thousands of *already-proved* theorems to build on (see "Reusing others' work" below).

In this repo, all of the above is gated behind the **`USE_LEAN`** build flag: the full image
installs it; `make image MINIMAL_IMAGE=1` drops it. So Lean work needs an image built with
`USE_LEAN=1` (the default full image, or `make image MINIMAL_IMAGE=1 USE_LEAN=1` for a lean image
that still has Lean).

## How a proof is actually written

A Lean file is a sequence of **declarations**. The two that matter at the start:

- `def` — a *definition* (a value, a function). E.g. `def double (n : Nat) : Nat := 2 * n`.
- `theorem` (or `lemma`) — a *statement plus its proof*. The type IS the statement; the body IS the
  proof. E.g. `theorem two : 1 + 1 = 2 := rfl`.

There are two styles for the proof body:

- **Term mode** — you write the proof as a direct expression. `rfl` ("reflexivity") proves `a = b`
  when both sides compute to the same normal form; `1 + 1 = 2` is `rfl` because both reduce to `2`.
- **Tactic mode** — opened with `by`, you give a *script* of steps that build the proof
  interactively. Common starter tactics:
  - `rfl` — close a goal true by computation.
  - `decide` — let Lean *compute* a decidable proposition to `True` (great for concrete finite facts
    like `(-1 : Int) ^ 2 = 1`).
  - `simp` — simplify using a large set of tagged rewrite lemmas (the workhorse; often finishes a
    goal after the real work).
  - `ring` — prove equalities in a commutative ring by normalizing both sides (invaluable for the
    algebraic identities gacalc cares about, e.g. expanding `(a·b)² + ‖a∧b‖²`).
  - `intro`, `apply`, `exact`, `rw` (rewrite), `calc` (chained equational reasoning) — the
    structural basics.

The mental model: you start with a **goal** (the statement to prove) and a **context** (hypotheses
you may use), and each tactic transforms the goal until nothing is left. In an editor (VS Code +
the Lean extension) you *see* the goal update after each tactic — that interactivity is most of how
you learn.

## How you KNOW a proof is complete (this is also the CI gate)

This is the crux for "run it in the build so a bad proof fails like a unit test."

- **`sorry`** is Lean's "admit this goal without proving it." It lets a file compile so you can work
  incrementally — **but Lean reports it only as a *warning*, and the build still exits 0.** So a
  naïve `lake build` can "pass" with unproved holes. You must gate against this deliberately.
- **`#print axioms <name>`** reports exactly which axioms a proof depends on. A genuinely complete
  proof rests only on Lean's three standard axioms — `propext`, `Classical.choice`, `Quot.sound` —
  or a subset. If the output includes **`sorryAx`** (or a user-declared `axiom`), the proof is
  **incomplete** (or is assuming something unproved). This is the reliable, version-stable signal.
- **The two gate mechanisms** (either or both — the spike verifies the exact spelling):
  1. Build with warnings-as-errors so a `sorry` warning fails the build (e.g.
     `lake build -DwarningAsError=true`, or `set_option warningAsError true` in-file).
  2. A `#print axioms` check that fails if any target theorem's axiom set contains `sorryAx` or an
     unexpected axiom. `lean4checker` is an extra kernel re-check for the paranoid.
- In gacalc this becomes a **`make lean`** target (with `: image` as a prerequisite, like `make
  test`) that returns non-zero on any hole, wired into CI **on a `v*` release tag** (not every push,
  to keep the fast `format`/`test`/`generated` checks quick). See the task doc for the CI wiring
  decision.

### What the spike actually showed *(spike-confirmed, 2026-09-27, Lean 4.34.1 / Lake 5.0.0)*

Running the one-shot spike harness `spike-pure-lean.sh` (deleted at archive 2026-10-04; in git history
under `tasks/adhoc/investigate-lean-proofs-for-ga/`) in the container confirmed:

- A complete proof checks, and `#print axioms` reported **`'two' does not depend on any axioms`** —
  a proof by pure computation (`rfl`/`decide`) rests on *zero* axioms, an even cleaner result than
  the three-standard-axioms baseline.
- A `sorry` proof produced **`warning: declaration uses 'sorry'`** and
  **`'bogus' depends on axioms: [sorryAx]`**, yet **`lean` still exited 0** — the gap, demonstrated.
- The **`#print axioms` + grep-for-`sorryAx`** gate worked exactly: it failed the broken file and
  passed the clean one. **This is the gate to use** for `make lean` — it is reliable and
  version-stable.

Three gotchas the spike surfaced (all folded into the plan):

1. **Use a `lib` target, not an `exe` target.** `lake init` defaults to an *executable*, whose build
   ends in a clang **link** step; the spike hit `clang: error: linker command failed` building
   `spike:exe`. Proof code is a **library** (produces `.olean`, no linking), which sidesteps it. If
   we ever build a Lean *executable* the lean image would need a full C toolchain (`gcc`/`binutils`)
   added — not needed for proofs.
2. **`-DwarningAsError=true` is not valid in Lake 5.0.0** (`error: unknown short option '-D'`). Set
   warning-as-error via `leanOptions` in the lakefile if wanted; but prefer the `#print axioms` gate
   above, which is what actually worked.
3. **Don't pipe the build through `tail` when you need its exit status** — the pipe reports `tail`'s
   exit (0), masking a real `lake`/`lean` failure. This is the repo's own "a multi-step check script
   must propagate every step's failure" rule (`~/.claude/reference/shell-and-gate-scripts.md`); the
   `make lean` gate must capture `$?` of the command itself (`status=0; cmd || status=1`), not a pipe
   tail.

## Reusing others' work — is the dot product an axiom, or proved?

A common beginner worry: "if I build on Mathlib, am I just trusting *their* axioms?" No. Mathlib is
**not** a pile of axioms — it is a tower of **definitions and proved theorems** built up from the
same three standard axioms above. The dot product in arbitrary finite dimension is a *definition*
(`inner`, on an `InnerProductSpace` / `EuclideanSpace`, in `Mathlib.Analysis.InnerProductSpace.*`)
with its properties (bilinearity, symmetry, positive-definiteness, Cauchy–Schwarz) available as
*proved theorems* you cite by name. When your proof `apply`s one, `#print axioms` on your result
still shows only the standard axioms — Mathlib's theorems carry their proofs with them. So building
on Mathlib is *reuse of proof*, not *assumption*.

How reuse works in practice:
- Add Mathlib as a lake dependency; run `lake exe cache get` to download Mathlib's **prebuilt**
  binaries (it is huge — compiling it from scratch takes hours; the cache makes it minutes). This
  needs network at setup time; budget for it.
- `import Mathlib` (or a specific module like `import Mathlib.Analysis.InnerProductSpace.Basic`) at
  the top of your file, then use its names.
- Find names with the Mathlib4 docs search, the `exact?`/`apply?`/`rw?` tactics (which search the
  library for a lemma that closes the goal), and `loogle` (search by shape).

### What phase 2 actually showed *(spike-confirmed, 2026-09-28, Lean 4.34.1 / Mathlib via `cache get`)*

Running the one-shot `spike-mathlib.sh` harness (same deleted directory) in the container confirmed the
reuse story end to end:

- `import Mathlib` + `lake exe cache get` works; after the one-time download, rebuilding a proof file
  that imports all of Mathlib took **3.1s** (`✔ Built Mathspike`, `Build completed successfully`).
- **The 2D Lagrange identity (<https://en.wikipedia.org/wiki/Lagrange%27s_identity>)** `(a₁²+a₂²)(b₁²+b₂²) = (a₁ * b₁+a₂ * b₂)² + (a₁ * b₂−a₂ * b₁)²` is proved outright
  by Mathlib's **`ring`** tactic — this is gacalc's first real target, done in one line.
- **The dot product is proved, not assumed.** `#print axioms real_inner_comm` (symmetry of the dot
  product on `EuclideanSpace ℝ (Fin n)`, arbitrary dimension) reported only
  `[propext, Classical.choice, Quot.sound]` — the three standard axioms, no `sorryAx`, no user axiom.
  Our own `lagrange_2d` and `dot_symm` reported the same. So citing Mathlib is reuse of *proof*.
- **Gotcha — lemma direction:** `real_inner_comm x y : ⟪y, x⟫ = ⟪x, y⟫`, so proving
  `⟪x, y⟫ = ⟪y, x⟫` needs `(real_inner_comm x y).symm` (or `real_inner_comm y x`). Expect to check a
  lemma's exact statement direction; `exact?`/`apply?` find the right orientation for you.

Two environment facts the spike forced out, both important for the real `proofs/` setup:

- **`git` must be installed in the image.** This container ships no git on purpose (git is a host
  concern here), but `lake` needs git to clone Mathlib. Added to `entrypoint/install-lean.sh` under
  `USE_LEAN`. Without it, `lake new … math` / `cache get` fail with
  `could not execute external process 'git'`.
- **Offline-convention gap.** The spike fetched Mathlib at *runtime* (git clone + `lake exe cache
  get` over the network), which violates gacalc's rule that all third-party deps are baked at
  build time so an exported image runs offline (see the personal overlay's "Self-contained images").
  The real `proofs/` setup must **bake Mathlib into the image at build time** under `USE_LEAN`
  (clone + `cache get` + build in the Dockerfile, into a committed layer), so an exported image has
  Mathlib offline and only the project's own `.lean` proofs rebuild at runtime.

Geometric algebra specifically:
- Mathlib has **`CliffordAlgebra`** (`Mathlib.LinearAlgebra.CliffordAlgebra.*`) — the general
  Clifford/geometric algebra over a quadratic form, with exterior-algebra and even-subalgebra
  machinery. This is the closest match to what gacalc computes.
- **`pygae/lean-ga`** (from the same group as **galgebra**, gacalc's comparison baseline) is a
  partial GA formalization (versors, CGA, ℝ/ℂ/ℍ isomorphisms) — **but it is Lean 3 / mathlib3**, and
  much of it graduated into Mathlib. Read it for ideas; do not depend on it.

## The gacalc policy: from-scratch first, reference second

Decided by the author (2026-09-27): each gacalc proof is written **from scratch and as standalone as
possible** — proving, e.g., the 2D and 3D dot-product / Lagrange / pseudoscalar facts directly,
*even when* a general Mathlib theorem exists — and then **adds a note pointing at** the general
result. Learning from and citing others' Lean proofs is welcome; *depending* on external GA
formalizations is not. Mathlib as the ambient library (rings, reals, basic algebra) is fine to use.
The point is pedagogical and self-checking: the author wants to have *done* the proof.

The first proof planned is the pseudoscalar square sign `Iᵣ² = (−1)^(r(r−1)/2)` (2D, 3D, then
general) — the on-paper proof already exists in `tasks/reference/pseudoscalar-square-sign.md`, which
makes it a good first target. Then the Lagrange identity `‖a‖²‖b‖² = (a·b)² + ‖a∧b‖²` (the squared
form, which the notebooks already use to derive sin/cos) and projection correctness.

## The gacalc proofs project (`proofs/`) — scaffolded 2026-09-28

The real project lives at `proofs/` (generated by `lake init GacalcProofs math`, so the Mathlib
version resolution is lake's own, not hand-picked):

- **Pins:** `proofs/lean-toolchain` → `leanprover/lean4:v4.34.1`; `proofs/lakefile.toml` requires
  mathlib `rev = "v4.34.1"`; `proofs/lake-manifest.json` records the exact Mathlib commit +
  transitive deps. `.lake/` (build output + the multi-GB Mathlib) is gitignored.
- **Gate:** `make lean` (from the repo root) runs `proofs/check.sh` in the container —
  `lake build` **plus** an axioms gate that auto-discovers every `theorem`/`lemma` under
  `GacalcProofs/` and fails if any depends on `sorryAx`. The script runs both checks and propagates
  either failure (never `set -e`), and is portable (container + host). It assumes declarations live
  in `namespace GacalcProofs`.
- **Landed proofs:** `GacalcProofs/Lagrange.lean` (Lagrange 2D + 3D, by `ring`),
  `GacalcProofs/G2.lean` (a from-scratch 𝒢₂: geometric product, dot = symmetric part, wedge =
  antisymmetric part, dot ≡ coordinate sum, pseudoscalar `I₂² = −1 = (−1)^(r(r−1)/2)`, the basis
  multiplication table `e_1_sq`/`e_1_mul_e_2`/`e_2_mul_e_1`/`e_12_sq`, and `eq_smul_basis`), and
  `GacalcProofs/Rotation2D.lean` (2D: `rot` from sin/cos; the geometric product enacts rotation; the
  product of two unit vectors is the rotor of the angle; rotation "from a to b" for general vectors,
  `b = (|b|/|a|) * rot(φb−φa)a`, and the rotor from a's direction to b's carrying a to b).
  This list is only the earliest landmarks and drifts — for the **current full inventory** (which now
  also includes the reverse anti-automorphism, the sandwich/rotation suite, projection/rejection,
  `Cross.lean` (cross/dual/scalar-triple), and `StandardPosition.lean` (reduction to standard position
  via elementary plane rotations), and the per-grade `bivector`/`trivector`/`scalar` builders) see the
  "Inventory" section of `tasks/reference/lean-ga-proof-architecture.md`.
- **Representation (decided 2026-09-28, standalone):** 𝒢ₙ is modelled concretely by a coordinate
  `structure` whose fields are the real *coefficients* on the basis blades (`s`/`c1`/`c2`/`c12` in
  `G2`) — a field is a coefficient, so it is an `ℝ`. But the basis blades themselves are **elements**
  of the algebra, so they are defined as genuine values `one`/`e_1`/`e_2`/`e_12 : G2` (e.g.
  `e_1 : G2`, a vector — NOT a real), with the GA multiplication table proved from the product, and
  `rotor`/`uvec` written as linear combinations of them. This mirrors the standard GA-in-Lean
  formalizations — Mathlib's `CliffordAlgebra` and pygae/lean-ga — where a basis vector `eᵢ` maps into
  the algebra via the linear map `ι Q : M →ₗ[R] CliffordAlgebra Q`, so `ι Q eᵢ : CliffordAlgebra Q` is
  an *element of the algebra* (not a scalar) and coefficients enter via `algebraMap R _`. Those use a
  basis-free tensor-algebra quotient; gacalc stays with the concrete coordinate model (standalone
  policy) and reserves the abstract `CliffordAlgebra` for the *equivalence* direction. Inspiration:
  Wieser & Song, *Formalizing Geometric Algebra in Lean* (2021, arXiv:2110.03551).
- **Offline:** Mathlib is **baked into the image** at build time under `USE_LEAN` (Dockerfile →
  `/opt/gacalc-proofs/.lake`), and `check.sh` copies it into the mounted `proofs/.lake` when absent —
  so `make lean` runs with no network. It adds several GB to a Lean image (only `USE_LEAN` images pay
  it). The bake lives *outside* the mount because a bind-mount would shadow a baked `proofs/.lake`.
- **Nested sandbox gotcha:** `make lean` depends on `image`, which nested re-runs the whole 16 GB
  `podman build`; run `check.sh` directly against the existing image instead (recipe in
  `lean-ga-proof-architecture.md`, "Build discipline").
- **CI:** `.github/workflows/lean.yml` runs `make lean` on `v*` tags only (heavy Mathlib build kept
  off the per-push checks).
- **The original program is complete** (umbrella archived 2026-10-04,
  `tasks/archive/2026/10/04/investigate-lean-proofs-for-ga.md`): every from-scratch result is bridged to its
  Mathlib counterpart in `proofs/GacalcProofs/MathlibBridge.lean` (dot ↦ `inner`, wedge ↦ `det`/
  `crossProduct`, rotation ↦ `Orientation.rotation`), and the pseudoscalar sign is proved for n = 1, 2, 3.
  Still open, as their own tasks: the general-n algebra (and the general pseudoscalar sign with it), the
  general multivector inverse, the Lean→notebook pipeline, frames.

## Where to learn more

- **Mathematics in Lean** (the standard tutorial book) and **Theorem Proving in Lean 4** — the two
  official long-form introductions.
- **The Natural Number Game** — a browser-based first hour with tactics, no install needed; the
  fastest way to feel what a proof *is*.
- **Mathlib4 docs** (searchable) — to find the name of a theorem you want to reuse.
- **The Lean Zulip chat** — where beginner questions get answered quickly.

(Add exact URLs after verifying them; per repo convention, don't cite a link you haven't opened.)
