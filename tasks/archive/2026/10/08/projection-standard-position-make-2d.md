# Make the "projection by reduction to standard position" proof 2D (Lean + book + figures)

**Status:** done — 2026-10-08 (gates green; archived; normalized pre-squash)
**Priority:** 4
**Difficulty:** 5
**Created:** 2026-10-08 (William Emerison Six <billsix@gmail.com>)

## BLUF

The reduction-to-standard-position derivation of **projection** — rotate `b` onto the x-axis, keep
the x-component, rotate back — had been built and machine-checked **only in 𝒢₃** (`StandardPosition.lean`,
two plane rotations), yet the book chapter's prose was written for 3D while its figures `sp1`–`sp5`
were already drawn for 2D. Projection onto a vector is intrinsically planar, so it should have been a
2D proof; the 3D framing was inherited from the archetype (the maintainer's cross-product derivation,
`multivariate-math/proofs/crossproduct.tex`, where three dimensions are genuinely needed). This made it
2D across all three artifacts — a new 𝒢₂ Lean proof (including the rotate-to-standard = Hestenes
equivalence), a 2D-lead rewrite of the book page, and a 2D-primary notebook — keeping the book's
2D-first-then-3D structure and deleting no 3D content. All gates green; the durable account lives in
`tasks/reference/reduction-to-standard-position.md` ("2D — the single-rotation base case").

## What was delivered

- **Lean** — new `proofs/GacalcProofs/StandardPosition2D.lean` (𝒢₂, namespace `GacalcProofs.G2`),
  registered in `GacalcProofs.lean`. A single elementary plane rotation `rotPlane` (no versor):
  linearity, `rotPlane_preserves_dot`, `proj_rotPlane_equivariant` / `vecReject_rotPlane_equivariant`,
  `rotPlane_aligns` (`b ↦ |b|·e₁`), `rotPlane_inv`, `proj_onto_x_axis`, then **`projectSP_eq_proj`**
  (the rotate-to-standard route = Hestenes `proj b a`) and **`rejectSP_eq_reject`** (via a
  division-free structural `reject_vec_eq`). `make lean` → `[lean] OK`, `sorry`-free. The audit
  confirmed no 2D standard-position proof had existed (only `StandardPosition.lean` in 𝒢₃; the 2D
  `Projection2D.lean` proves the Hestenes formula, not the frame-reduction route).
- **Book prose** — `book/docs/proof-projection.rst` restructured 2D-lead (a single rotation to
  standard position, matching figures `sp1`–`sp5`), with the xy/xz two-plane material salvaged into a
  "Stepping up to three dimensions" section. Citations repointed (2D → `StandardPosition2D.lean`, 3D →
  `StandardPosition.lean`); DRAFT/TODO banners removed.
- **Notebook** — `book/docs/notebooks/proof-projection.py` made 2D-primary (explicit `g2`
  single-rotation construction vs `projected_onto`), the 3D `project_sp` example kept as the trailing
  step-up.
- **Figures** — `sp1`–`sp5` were already 2D; verified they match the rewritten captions.
- **Scoping** — Python `gacalc.standardposition` left 𝒢₃-only; a genuine 𝒢₂ `project_sp` is deferred
  with the rest of the 3D/code work (the 2D notebook shows the construction directly against `g2`). The
  3D `StandardPosition.lean`, the page's 3D section, and the notebook's 3D example were all **kept** for
  the later 3D pass.
- **Verification** — `make lean`, `make docs` (HTML + PDF built, notebook executes under
  `raise_on_error=True`, all five figures render and embed), and `make format` all green. No public
  Python surface changed, so no `CHANGELOG` entry.

### Post-archive prose/notation polish (same day, maintainer feedback)

After the archive commit, the maintainer asked for the page prose to be clearer; these changes landed
on top (and their conventions were harvested to `tasks/reference/book-outline.md` §"Notation & prose
conventions for proof pages"):

- **Ground each step in an already-defined function.** The rotation step was rewritten to re-state
  `proof-rotate.rst`'s `r(v; θ)` and substitute `θ = −(b's angle)` into it — no matrix dropped in
  unexplained — reusing that chapter's "never need the angle itself, only its cosine and sine" trick.
- **From→to transform naming.** The rotation is named `R_{\vec b}^{\vec e_1}` (from `b`, to `e₁`),
  matching *Model View Projection*'s `f_{source}^{dest}` (`ch02.rst`); its inverse swaps the labels.
- **Compose, don't nest.** `R⁻¹(P(R(a)))` became `P_b = (R_{\vec b}^{\vec e_1})⁻¹ ∘ P_{\vec e_1} ∘
  R_{\vec b}^{\vec e_1}`, writing the undo step as the **explicit inverse** of the first rotation (not
  the label-swapped `R_{\vec e_1}^{\vec b}`, though they are equal) so it is obvious the last map is the
  first inverted.
- **Default angle symbol θ.** Replaced `φ` (`\varphi`) with `θ` throughout the prose and the figures
  (`sp2` label + `sp2`/`sp3`/`sp5` comments); recorded "default to θ for a rotation angle" in
  `book-outline.md`.
- **Filed `tasks/book-rotation-from-vectors-no-angle.md`** (proposed, not started) — a future book
  section for an angle-free rotate-from-`a`-to-`b`, with the 2D case as the headline (built from the
  geometric product / project / `r(v;θ)`); it records that gacalc already implements this
  (`versor_from_vectors`/`rotor_from_vectors`, `transforms.projection_rotation`/`versor_rotation`; Lean
  `projRotation`) and that modelviewprojection only vendors gacalc's copy.

## Decisions

1. **`projectSP_eq_proj` proven in 𝒢₂** — the rotate-to-standard route equals the Hestenes `proj`, same
   as the 3D proof (maintainer's explicit ask, 2026-10-08).
2. **Elementary plane rotation, not a versor**; the in-frame step keeps the x-component **literally**
   (no call to Hestenes `proj`), or the non-circularity claim is false (inherited from the 3D task).
3. **2D-first, 3D-second, delete nothing 3D** (maintainer, 2026-10-08) — the page leads with the 2D
   derivation and keeps a 3D step-up section; the 3D Lean/prose/notebook all stay for the later 3D pass.
   This is the book's structural principle (`book-outline.md` §"Two halves: 2D first, 3D second").
4. **Python standardposition stays 𝒢₃-only for now** — the 2D library path is deferred with the 3D work.

## History (commit chronology, `origin/master..HEAD` — for the maintainer's squash)

The maintainer squashes these; this is the harvested record.

1. `f85a178` *added task* — filed this task (then proposed) with the finding and plan.
2. `279c84c` *2d projection* — the work: `StandardPosition2D.lean` (the `reject_vec_eq_coord` proof
   first attempted with `ext <;> field_simp <;> ring`, which would **not** clear the summed
   `(a₁²+a₂²)⁻¹` denominator regardless of the hypothesis form; replaced with the division-free
   structural proof via `sub_mul`/`mul_assoc`/`mul_vec_inverse_self`), the 2D-lead `proof-projection.rst`,
   the 2D-primary notebook, and the reference-doc harvest; all gates green.
3. `a518621` *archived* — moved the task doc to `tasks/archive/2026/10/08/`.
4. `6e59f4c` *updated* — post-archive prose: grounded the rotation in `r(v;θ)`, `R_{from}^{to}` naming,
   compose-not-nest.
5. `a23f20b` *updated* — wrote the undo step as the explicit inverse of the first rotation.
6. `d13bb43` *updated* — θ as the default angle (prose + figures), the `book-outline.md` conventions,
   and the new `book-rotation-from-vectors-no-angle.md` task.

## Related

- `tasks/reference/reduction-to-standard-position.md` — the durable account (2D + 3D).
- `tasks/reference/book-outline.md` — the book's structure and the proof-page notation conventions.
- `tasks/proof-projection-book-voice-pass.md` — the maintainer's remaining (pure) voice pass.
- `tasks/book-rotation-from-vectors-no-angle.md` — the follow-on angle-free from→to rotation section.
- `multivariate-math/proofs/crossproduct.tex` (github.com/billsix/multivariate-math) — the archetype.
