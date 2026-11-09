# Fix the stale and false claims in the reference docs

**Created:** 2026-11-09 · **Completed:** 2026-11-09
**Source:** `tasks/review/2026/11/08/repo-review.md` §1.1, §1.2, §2.1

## What changed

- **`tasks/reference/lean-ga-proof-architecture.md`:**
  - the module count (34, with the ReciprocalFrame files);
  - the G1/G2/G3 section order, rewritten to the post-2026-10-29 teaching order as the files show it;
  - "Remaining" no longer lists frames as wholly open, and names what landed;
  - `dot_is_sym_part` is the object form in both algebras;
  - "Projection/Projection2D" → "Projection2D/Projection3D";
  - the corpus-review pointer.
- **`tasks/reference/lean-for-gacalc.md`:** ~800 tests; "32 (now 34)" files; the extra linters are
  turned on per run (`lakefile.toml` sets none of them).
- **`tasks/reference/design-decisions.md`:**
  - the notebooks' gate is `make check-notebooks` (in CI since 2026-11-09);
  - `cross` is no longer listed as declined;
  - the `.dockerignore` sentence says what it now excludes.
- **`tasks/reference/book-and-docs-pipeline.md`:**
  - `api.rst`'s actual module list;
  - the nbconvert TeX is gated on `USE_JUPYTER || BUILD_DOCS`;
  - the package set split into dnf (`04-install-docs.sh`) and venv (`sphinx`, `furo`, `nbsphinx`,
    `myst-nb`);
  - the `nb_execution_raise_on_error = True` gate.
- **`tasks/reference/generated-algebra-generation-cost.md`:** g4/g5 have their own grade types
  (`GRADE_NAMES`/`grade_name`); `check-generated` runs on g1–g3.
- **`tasks/reference/symbolic-equality.md`:** `a.symbolically_equal(b, subs=…)`.
- **`tasks/reference/openstax-math-pedagogy.md` §9:** marked as a 2026-08-03 snapshot.
- **`tasks/reference/reduction-to-standard-position.md`:** the angle-free payoff is
  `book/docs/rotation-from-vectors.rst`, with the task's archived path.
- **`proofs/README.md`:** 34 modules; the reciprocal frame covered; the parallel predicate is the
  iff; the corpus review's new path.
- **`tasks/reference/lean-proof-corpus-review-2026-10-04.md`** moved, with `git mv`, to
  `tasks/review/2026/10/04/lean-proof-corpus-review.md`, under the deep-review convention for dated
  records. It has a banner saying what in it is out of date, and is otherwise unedited. Every
  reference was repointed: two live docs (one hunk of `tasks/lean-frame-coverage.md`) and five
  archived ones.

## Verification

- Every path cited in the changed docs exists.
- `git grep lean-proof-corpus-review-2026-10-04` outside the dated records finds nothing.
