# Prove 2D rotation is distributive (linear): prose + Lean (+ the symbolic Python form)

**Status:** in-progress
**Priority:** 4
**Difficulty:** 4
**Started:** 2026-10-09 (William Emerison Six <billsix@gmail.com>)

## BLUF

Now that 2D rotation is defined in prose (`proof-rotate.rst` gives `\vec{r}(\vec{a};\theta)`;
`geometric-product.rst` gives the rotor `R = \cos\theta + \sin\theta\, e_{12}`, rotation as
`\vec{v} * R`), add a **prose proof** that rotation is **distributive** — `R(\vec{u} + \vec{v}) =
R(\vec{u}) + R(\vec{v})` (and homogeneous, `R(k\vec{v}) = k\,R(\vec{v})`) — and a **Lean proof** of the
same. This is the key step that lets us rotate the two **natural-basis** vectors and reconstruct any
rotation: `R(\vec{v}) = v_1\,R(\vec{e_1}) + v_2\,R(\vec{e_2})`. Per the project's "three forms" standard
I'll also add the **symbolic Python** check (gacalc), so the result ships as Lean + Python + prose.

## Context (read first)

- **Lean:** `proofs/GacalcProofs/Rotation2D.lean` defines `rot (θ : ℝ) (v : G2)` (the coordinate
  rotation map) with `rot_vec`, `rot_add` (composition = angle addition), `rot_comm`, `rot_normSq`
  (isometry), `rot_polar`, `rot_uvec`, and the `fullAngleRotor`. **There is no distributivity /
  linearity theorem yet** — add `rot_add_vec : rot θ (G2.add u v) = G2.add (rot θ u) (rot θ v)` and
  `rot_smul : rot θ (G2.smul k v) = G2.smul k (rot θ v)` (both follow from the coordinate formula being
  linear in `c1`/`c2`; short proofs). State them in the house "objects in" style where it reads
  naturally. The `make lean` gate verifies (heavy — Mathlib; run `proofs/check.sh` against the image).
- **Prose:** the natural home is right after the rotor is introduced (`geometric-product.rst`, where
  rotation becomes `\vec{v} * R`), or a short dedicated section/page. The cleanest argument: the
  geometric product distributes over `+`, so `(\vec{u}+\vec{v}) * R = \vec{u} * R + \vec{v} * R`;
  therefore rotation is linear and `\vec{v} * R = (v_1 \vec{e_1} + v_2 \vec{e_2}) * R = v_1(\vec{e_1} *
  R) + v_2(\vec{e_2} * R)` — rotate the basis, get everything. Cite the Lean theorem by name (per
  `tasks/reference/book-outline.md`'s proof-page conventions).
- **Python:** a gacalc symbolic cell/test checking `R(a+b) == R(a) + R(b)` and the basis-reconstruction,
  in a book notebook (`book/docs/notebooks/`) and/or a test.
- The "break a rotation into its components on the natural basis" idea is also the conceptual bridge to
  `tasks/graph-paper-rotation-notebook.md` (rotation as rotating the graph paper).

## Goal

A distributivity/linearity result for 2D rotation in all three forms: Lean (`rot_add_vec` + `rot_smul`
in `Rotation2D.lean`, `make lean` green), prose (a proof in the book, citing the Lean theorem, leading
to the basis-reconstruction), and symbolic Python (a gacalc check). The prose stays in the established
voice; the maintainer can voice-pass later.

## Plan

- [ ] Lean: add `rot_add_vec` and `rot_smul` to `Rotation2D.lean`; `proofs/check.sh` green.
- [ ] Python: a symbolic gacalc check (`R(a+b) == R(a)+R(b)`, basis reconstruction) as a notebook cell
      and/or a test.
- [ ] Prose: add the distributivity proof to the book after the rotor is defined, citing the Lean name,
      ending on `R(\vec{v}) = v_1 R(\vec{e_1}) + v_2 R(\vec{e_2})`.
- [ ] `make lean` + `make docs` + `make test` green.

## Open questions

None blocking — the result and its three forms are clear; prose placement is a discretion call made
during the work (noted in the pre-squash write-up).
