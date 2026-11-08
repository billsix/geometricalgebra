# Repository review — 2026-11-08

**What this is.** A dated, read-only deep review of the whole repository across all ten dimensions of
the deep-review convention (the `repo-review-conventions.md` reference doc in
github.com/billsix/runClaudeInContainer). It checks everything against each other, against the
code, against this repo's `CLAUDE.md`, and against the maintainer's cross-project conventions. It
records findings and open questions only. No fixes were made while writing it.

**Requested by:** William Emerison Six <billsix@gmail.com>, 2026-11-08. The maintainer will address
the issues, make tasks from them, and answer the open questions later.

**Snapshot warning.** Every finding describes the tree as of 2026-11-08. Findings go stale as they
are fixed. Re-check a finding against the tree before acting on it. **This record is never edited
afterwards**: act on it through tasks that cite its sections (e.g.
`tasks/review/2026/11/08/repo-review.md` §4.1). The next review reports what carried over.

**Baseline:** none. This is the first review.

**How it was produced.** The maintainer's assistant (Claude Opus 5.5) did two kinds of work itself:
it read every book page and notebook in full (dimension 3), and it reviewed the build, container,
CI and packaging layer (dimension 8). Eight fresh readers, each briefed with this repo's
`CLAUDE.md` and the cross-project conventions, ran in two waves:

- wave 1: the reference docs, the open tasks with the 2026-10/11 archive, the 2026-06/07 archive,
  and the 2026-08/09 archive;
- wave 2: the library source, the generator and tools, the tests and demo notebooks, and the Lean
  proofs.

Before recording, the main thread re-ran the check behind every HIGH finding. The readers used about
2.5M subagent tokens in total (wave 1 ≈ 1.17M, wave 2 ≈ 1.31M).

Each finding is labelled:

- **VERIFIED** — checked against the tree with `grep`/`ls`/`git`, or by running the code;
- **LEAD** — plausible but not confirmed; check it before acting.

Book findings come from a direct read and are VERIFIED unless marked otherwise.

## Coverage

| # | Dimension | What was read | By |
|---|---|---|---|
| 1 | Docs ↔ docs | All 37 `tasks/reference/*.md`; `CLAUDE.md`, `README.md`. Large Lean docs read in full. The rest were checked by grepping every backticked identifier, path, target, task, wiki-link and SHA. | reader (reference docs) + main |
| 2 | Docs ↔ code | Every gate/target/file claim the readers met, spot-checked against the tree. | all readers + main |
| 3 | Product content | Every `book/docs/*.rst` page and every `book/docs/notebooks/*.py` in full (frame-qr notebooks: markdown cells only). `README.md` skimmed. Demo `notebooks/*.py` in full (reader). | main; reader (tests + notebooks) |
| 4 | Code quality | All nine hand-written `src/gacalc/*.py` modules in full (~6.9K lines). The generated `g1`–`g3` were only probed. | reader (library) |
| 5 | Generators and tools | `tools/gen_specialized.py`, `tools/astbuild.py` and every other `tools/*.py` in full (~8.3K lines); on-disk `g1`–`g3` sampled and probed (728 overload cases checked). | reader (generator) |
| 6 | Tests | All 35 `tests/` files and `pytest.ini` in full (~6.5K lines); collection run (792 + 11 slow). | reader (tests) |
| 7 | Proofs | All 34 `proofs/GacalcProofs/*.lean` in full (~7K lines), plus the root file, `check.sh`, `lakefile.toml` and `README.md`. `#print axioms` was run on all 628 theorems. | reader (Lean) |
| 8 | Build, container, CI, packaging | All of the following in full: `Makefile`, `Dockerfile`, `.dockerignore`, every `entrypoint/*.sh`, `.github/workflows/*`, `pyproject.toml`, `pytest.ini`, `setup.py`. Also `CHANGELOG.md` headings vs tags, script modes, and `TODO.org`. `book/docs/conf.py` was not read beyond the line a reader cited. | main |
| 9 | Open-task backlog | All 36 `tasks/*.md` in full. | reader (open tasks) |
| 10 | Archive hygiene | `tasks/archive/2026/08`–`11` in full. `2026/06`–`07`: 24 docs read in full, mechanical checks on all 100, plus ~18 more read in full; ~60 July docs were **not** read line by line. | three archive readers |

Not covered:

- the vendored Emacs tree (off-limits by `CLAUDE.md`);
- the generated `g4`/`g5`;
- `book/figures/epix/*.py` figure sources, beyond the one label checked in §3.4;
- the rendered book output (`make docs` was not run);
- the test suite, which was not run in full (collection and a few timings only).

<!-- notation-rule: begin -->  (this whole record quotes rejected spellings on purpose, e.g. in §3.4,
§4, §5 and §7; a notation re-sweep must skip it)

---

## 0. The findings that matter most

Ranked by how much each changes what the maintainer does next. Every item below is VERIFIED.

1. **Library bug:** `project` returns a bivector unchanged when projecting onto a vector. The
   answer should be 0. (§4.1)
2. **Generator bugs:**
   - `Scalar` iterates to itself instead of its coefficient, and yields nothing when it is zero.
   - Full `G` mixed with a graded type returns the slow `Gn`.
   - The closed-form `Versor.sandwich` turns integer input into floats.

   (§5.1)
3. **A claim that overstates the proofs:** `base.py` and `CLAUDE.md` say Lean proves
   `A ∧ B = 0 ⟺ A ∥ B`. Lean proves one direction only. (§7.1)
4. **Gates that silently don't run what the docs say:**
   - `make test-all-dims` runs no `ty`. (§2.1)
   - `proofs/check.sh` has no axioms gate, and its grep can't match `sorryAx`. (§7.1)
   - `tools/check_annotations.py` always exits 0 and nothing runs it. (§5.2)
   - `check-notebooks` is not in CI. (§8.2)
5. **CI builds the full multi-GB image** (Lean + Mathlib + ePiX + TeX) in each of its three per-push
   jobs, because it passes `BUILD_DOCS=0 USE_EMACS=0 USE_SPYDER=0` rather than `MINIMAL_IMAGE=1`.
   (§8.2)
6. **Security:** `make jupyter` publishes an unauthenticated, XSRF-disabled JupyterLab on port 8888 on
   every host interface. (§8.1)
7. **Book:**
   - a math error: sin(θ) is written as a bivector over a scalar (§3.3);
   - two competing stories for where the geometric product comes from (§3.2);
   - four cross-references to content the cited page doesn't contain (§3.2).
8. **`project_sp` returns NaN without raising when `b` lies along e₃.** Two readers found this
   independently. (§4.1, §6.1)
9. **Tests that cannot fail.** (§6.1)
10. **`tools/reorder_lean.py`:** running it would revert the 2026-10-29 teaching-order work. (§5.1)

---

## 1. Docs ↔ docs

### 1.1 Contradictions between docs

- **`tasks/reference/lean-for-gacalc.md:207-211`** describes an axioms gate in `proofs/check.sh`.
  `tasks/reference/lean-ga-proof-architecture.md:804` describes the real grep gate. The script's own
  header and `.github/workflows/lean.yml` repeat the false version (§7.1). VERIFIED.
- **`tasks/reference/lean-ga-proof-architecture.md` contradicts itself.** VERIFIED; the Lean reader
  rechecked every item.
  - **:208-216** gives the pre-2026-10-29 G1/G2/G3 order (`mul`/`wedge`/`add`… → magnitude → `dot`).
    `tasks/reference/algebra-teaching-order.md` Part III and the files themselves put
    add/sub/neg/smul before mul/wedge/dot, as `G2.lean` shows.
  - **:274** puts G2's split in `Projection2D.lean`. It is at `G2.lean:394`/`:402`, as the doc's own
    :196-202 say.
  - **:673** calls `dot_is_sym_part` a coordinate form. `G2.lean:332` is the object form, as the
    doc's own :137 says.
  - **:10** says "31 modules". There are 34.
  - **:653-656** lists frames as remaining work, against its own coverage table at :725-726.
  - **:688** cites "Projection/Projection2D". There is no `Projection.lean`; it should be
    `Projection3D`.
- **`tasks/reference/design-decisions.md`:** VERIFIED.
  - **:83** lists `cross` among the declined features, against :35 and `CLAUDE.md`. `cross` ships.
  - **:160** says a `.dockerignore` "can't fix" the elpa duplication, against :158 and the real
    `.dockerignore`.
- **`tasks/reference/book-and-docs-pipeline.md:276-277`** lists Sphinx as dnf packages, against its
  own "Sphinx lives in the VENV" section. VERIFIED.
- **`tasks/reference/symbolic-equality.md:125`** recommends `_simplify_equal`. Its own :106 says that
  helper is gone (replaced by `symbolically_equal(other, *, subs=…)`). VERIFIED.
- **`CLAUDE.md` contradicts itself on the dot product.** VERIFIED.
  - :146 (the 2026-11-04 rule) says "write `a.dot(b).scalar_part()` … `scalar_product` only where it
    is meant".
  - :60 (`vectorcalc` bullet) and :213 (Operators) still say "dot = `scalar_product`".
  - So does `src/gacalc/vectorcalc.py:19-20`.
  - Code that follows the old wording: `notebooks/displayvectorcalc.py:99,107`,
    `tests/test_vectorcalc.py:64` and `tests/test_rotor_from_vectors.py:46`.
- **Two rules on symbolic test fixtures conflict.** LEAD.
  - The 2026-08-25 rule (`tasks/archive/2026/08/25/explicit-symbolic-tests-and-helper-cleanup.md`):
    write general vectors inline, with no shared `sym_vec_*` fixtures and no parametrize that hides
    the inputs.
  - The 2026-11-07 sanction of the `FRAMES` parametrize in the frame tests.
  - Code on the shared-fixture side: `tests/test_frame.py:53-63` (imports `sym_vec*` from gn),
    `tests/test_measure.py:71-78` (module-level `_A2`/`_B3`) and `tests/test_frame_class.py:45`.
  - The maintainer should decide which rule wins.

### 1.2 Docs out of date or in the wrong place

- **`tasks/reference/book-outline.md` has drifted from the book** (VERIFIED by two readers and the
  main thread):
  - **"File layout" (~:152-184)** never mentions `levels-of-abstraction`, `blade-square-sign`,
    `frames-qr` (or its `frame-qr-2d`/`-3d` notebooks), or `proof-cross` (or its notebook). Its
    "Prose + companion notebook" / "Prose only" lists leave those pages out, and "Filled so far
    (2026-10-09)" leaves out the three newer notebooks.
  - **Part I sections A–I** have no slot for `blade-square-sign` or `levels-of-abstraction`.
  - **Part II** still reads "To be fleshed out much later", yet `projection-rejection-3d`,
    `frames-qr` and `proof-cross` exist.
  - **The "Status:" paragraph** dates from 2026-08-02.
  - **Lines 18–20 are garbled** by an earlier first-name → role sweep ("…split are / The
    maintainer's **explicit** ordering", then a sentence starting with a lower-case "the
    maintainer's").
- **`tasks/reference/lean-proof-corpus-review-2026-10-04.md` is a dated audit sitting in
  `reference/`.** VERIFIED.
  - Line 6 says "none applied"; §7 says "all applied".
  - Its §3 coverage table is now false: `G1.lean`, `ReciprocalFrame*` and `PlaneRotation3D` exist.
  - §2 says `autoImplicit` defaults to `true`; `proofs/lakefile.toml:8` sets it `false`.
  - §4 is a to-do list citing six archived tasks, plus one that was never created.
  - Under the deep-review convention it belongs in `tasks/review/2026/10/04/`, or in the archive as
    a done-record. Fix the inbound pointer at `lean-ga-proof-architecture.md:808` either way.
- **`tasks/reference/openstax-math-pedagogy.md` §9 (:449-468)** is a 2026-08-03 snapshot written in
  the present tense ("only three prose chapters"). It defers to an archived task. VERIFIED.
- **`tasks/reference/reduction-to-standard-position.md:171`** cites the archived
  `tasks/book-rotation-from-vectors-no-angle.md` as future work. VERIFIED.
- **`tasks/reference/lean-for-gacalc.md`:** VERIFIED.
  - :276-278 says extra linters are set in `proofs/lakefile.toml`; none are.
  - :22 says "~650 tests"; `CLAUDE.md` says ~800, and 803 collect.
  - :254 says "32 files"; there are 34.
- **`proofs/README.md`** says "31 modules", omits `ReciprocalFrame2D/3D`, and says `frame.py` is
  uncovered. VERIFIED.
- **Wiki-link labels with no path.** `[[slug]]` references appear in `algebra-teaching-order.md`,
  `openstax-math-pedagogy.md`, `dot-wedge-projection-rejection.md`,
  `gn-multiplication-by-hand.md` and `lean-ga-proof-architecture.md:438`. All resolve, but none
  gives a path, and two point at archived tasks without saying so. VERIFIED.
- **`TODO.org` (repo root) is entirely stale.** All its items are done: "Add docstrings", "Make
  example jupyter notebook", "Make sphinx docs". Nothing points at it. Delete it, or move anything
  live into a task. VERIFIED.

### 1.3 Checked clean

- **SHAs:** the reference docs' SHAs all resolve, except `275adef` (epix-mirror) and `e682de30`
  (modelviewprojection), which are labelled as belonging to those repos.
- **Paths:** every `tasks/archive/…` and `tasks/reference/…` path cited exists.
- **Stamps:** there are no bare-first-name stamps in the reference docs.
- **Docs that match the code:**
  - `emacs-lsp-setup.md` matches `init.el` and `01-install-base.sh`;
  - `hestenes-variable-notation.md` matches `pyproject.toml` (N806 off).

---

## 2. Docs ↔ code

### 2.1 Gates and targets the docs misdescribe

- **No gate runs `ty` over the generated `g1`–`g5`.** VERIFIED; two readers found it.
  - `CLAUDE.md` › "Dev workflow", `tasks/reference/design-decisions.md:172` and
    `tasks/reference/generated-product-typing.md:306` all call `make test-all-dims` "the full-dim +
    full-context ty gate".
  - The target (`Makefile:254-260`) only runs the generator and `pytest`.
  - `entrypoint/format.sh`'s `ty check src` respects `.gitignore`, so it skips the generated
    modules.
  - So the 179 → 0 cleanup from `tasks/archive/2026/08/23/generator-ty-clean-high-dim.md` is
    unguarded.
  - The two reference docs give different manual file lists.
  - The target also lacks the `: image` prerequisite that `CLAUDE.md` › "Continuous integration"
    requires (§8.1).
- **`tools/check_annotations.py` is described as enforcement, but it is report-only and runs
  nowhere.** VERIFIED. Details in §5.2.
  - `CLAUDE.md` › "Coding standard" says notebook annotations are enforced by `ty` plus that tool,
    "so a missing annotation shows up as a row (none expected)". Today it reports **49 rows** against
    the documented floor of 32 (§6.2).
- **`proofs/check.sh` and `make lean`'s help text say the gate catches `sorryAx`.** It doesn't (§7.1).
  VERIFIED.
- **`tasks/reference/design-decisions.md:51`** says the notebooks have no execution gate, citing an
  open task. That task is archived (`tasks/archive/2026/11/04/`), and `make check-notebooks` exists.
  VERIFIED.
- **`tasks/reference/book-and-docs-pipeline.md`:** VERIFIED.
  - **:212-214 and :279** call the nbconvert TeX install unconditional. It is gated by
    `USE_JUPYTER || BUILD_DOCS` (`Dockerfile:124`). The header of
    `entrypoint/03-install-notebook-tex.sh` makes the same false claim.
  - **:11-15 and :296** say `api.rst` covers every module. It omits `standardposition` and
    `nbplotutils` (§3.6).
  - It does not mention the `nb_execution_raise_on_error = True` gate in `book/docs/conf.py:163`,
    decided in `tasks/archive/2026/08/29/gate-book-notebook-execution-errors.md`.
- **`tasks/reference/generated-algebra-generation-cost.md:46-49`** says the type registry stops at
  `Trivector`. `tools/gen_specialized.py:2952-2968` has `GRADE_NAMES`/`grade_name(k)` up to
  `FourVector` and beyond. The ":76" bullet reads as an undone to-do. VERIFIED.

### 2.2 Claims about the code that the code contradicts

- **`src/gacalc/base.py:1336-1340` (`is_parallel_to`) and `CLAUDE.md` › "Assessment" item 2** say
  `A ∧ B = 0 ⟺ A ∥ B` is machine-checked. It isn't; see §7.1. VERIFIED.
- **Generated docstrings that misstate the math** (§5.1, §5.3):
  - `Versor.i` claims to return i for `cos − sin * i`; it returns −i.
  - `sandwich` says `R * x * R⁻¹` in one place and `R * x * R̃` in another.
  - Others are listed in §5.3.

  VERIFIED.
- **`CLAUDE.md` › "Module layout" says `define-frame` is the frames task.** `tasks/define-frame.md`
  exists, but its premise is stale (§9.1). VERIFIED.

### 2.3 Decisions in force but recorded nowhere

Each still applies, but appears in neither `CLAUDE.md` nor `tasks/reference/`:

- **The scope of "build vectors from basis constants."** LEAD.
  - `CLAUDE.md` (~:127-138) states the rule with no scope.
  - The archive (`tasks/archive/2026/07/18/prefer-basis-vector-construction.md`,
    `tasks/archive/2026/06/06/basis-vector-construction.md`) limits it to teaching-facing code.
    Tests may keep the positional constructor, which is public API, and product tests keep dict
    literals to avoid circular ground truth.
  - `design-decisions.md:99` records that scope; `CLAUDE.md` doesn't.
  - `tests/` has 22 `Vector(coeff_…)` uses.
- **`bivector_rotation(i)`** (`src/gacalc/transforms.py:472`, re-exported from `gn.py`) is missing
  from `CLAUDE.md`'s transforms bullet and Operators line. That mention was deferred to the
  maintainer in `tasks/archive/2026/08/15/redo-exp-book-referenced.md`. VERIFIED.
- **The `i, j, k` alias in `notebooks/displayvectorcalc.py:55`** was sanctioned on 2026-08-31
  (`tasks/archive/2026/08/31/custom-symbols-and-vector-calc.md`), but `CLAUDE.md`'s alias carve-out
  names only `displayg2`/`displayg3`. VERIFIED.
- **"Symbolic tests write their vectors inline"** (2026-08-25) is not in
  `tasks/reference/python-coding-standard-gacalc.md`. VERIFIED. (See the conflict in §1.1.)
- **"Notebooks use `display(...)`, not `print`"** (ruff T201;
  `tasks/archive/2026/09/05/fix-make-format-ruff-errors.md`) is recorded nowhere. LEAD.
- **"Keep `|a| * |b|`, never `abs(b * a)`, in the wedge-magnitude sine"**
  (`tasks/archive/2026/06/27/wedge-magnitude-sin-notebook.md`) lives only in the comment at
  `src/gacalc/base.py:2126-2135`. `nbplotutils.sine` breaks it (§4.2). VERIFIED.
- **No CHANGELOG pointer in the README.** This was deferred in
  `tasks/archive/2026/08/13/changelog-for-breaking-api-changes.md`. LEAD.

### 2.4 Source citing tasks that have moved

These docstrings and comments cite `tasks/<slug>.md` paths that now exist only under
`tasks/archive/`. VERIFIED.

- **`src/`:**
  - `base.py:980,1022` → `tasks/investigate-dot-product-grade-0.md`
  - `base.py:2638` → `tasks/validate-blade-dict-keys.md`
  - `vectorcalc.py:25` → `tasks/custom-symbols-and-vector-calc.md`
- **`tests/`:**
  - `tests/test_vector_ergonomics.py:20` and `tests/test_plane_rotation.py:17` →
    `upgrade-rotation-and-ctc-vector-mapping.md`
  - `tests/test_blade_symbols.py:17` and `tests/test_vectorcalc.py:21` →
    `custom-symbols-and-vector-calc.md`
  - `tests/test_numeric_magnitude.py:19` → `magnitude-numeric-for-numeric-input.md`
  - `tests/test_conformance.py:329` → `graded-typed-module-basis-constants.md`
- **`proofs/`:**
  - Cross → `tasks/lean-candidates-from-symbolic-tests.md`
  - Sandwich → `tasks/lean-proof-rotation-preserves-length.md` and `-angles.md`
  - RotateComponents → `tasks/lean-proof-sandwich-rotates-components.md`

---

## 3. Product content (the book, the README, the demo notebooks)

### 3.1 The book's current state

Reading order: the `book/docs/index.rst` toctree, one flat `:numbered:` list:

1. hook
2. canonical-form
3. one-dimension
4. multiplication
5. trigonometry
6. sets
7. vectors-as-number-lines
8. relative-graph-paper
9. vector-addition
10. rotate
11. geometric-product
12. rotation-graph-paper
13. levels-of-abstraction
14. blade-square-sign
15. projection
16. reflection
17. orthogonal
18. dual
19. defining-g2
20. interactive-calculator
21. three-dimensions
22. projection-rejection-3d
23. frames-qr
24. proof-cross
25. api

Proof and companion pages hang off their chapter's own toctree:

- `proof-rotate` and `proof-rotate-from-a-to-b` under `rotate`;
- `rotation-from-vectors` under `geometric-product`;
- `proof-projection` under `projection`.

`proof-cross` is the exception (§3.6).

Status by page:

- **Placeholders** (one line): hook, canonical-form, one-dimension, multiplication, trigonometry,
  sets, vectors-as-number-lines, reflection, orthogonal, dual, defining-g2, interactive-calculator,
  three-dimensions.
- **Stub notebooks** (`1 + 1`): canonical-form, defining-g2, dual, hook, one-dimension, projection,
  projection-rejection-3d, reflection, relative-graph-paper, three-dimensions,
  vectors-as-number-lines.
- **Real content:**
  - proof-rotate, proof-rotate-from-a-to-b, geometric-product, rotation-from-vectors,
    rotation-graph-paper, blade-square-sign, proof-projection, proof-cross;
  - levels-of-abstraction (a short page plus a 136-line notebook);
  - frames-qr (a short page plus the 531/397-line notebooks);
  - partial: vector-addition, relative-graph-paper, projection and projection-rejection-3d (figures
    with the prose still TODO).

### 3.2 Structure and narrative

- **Two competing stories for where the geometric product comes from.**
  - `book/docs/geometric-product.rst` derives it from rotation: the 90° turn is `a * e12`, so
    `r(a; θ) = a * (cos(θ) + sin(θ) * e12)`.
  - `book/docs/proof-projection.rst` comes later in the reading order, but still says it uses "no dot
    product, no geometric product, nothing from later in the book". It promises that "much later" the
    book will "turn everything around and *build* the geometric product out of projection". No
    chapter does.
  - `book-outline.md`'s "Non-circularity note" separates the rigorous order from the presented
    order, but the book's own text never reconciles them. The page also opens "later, once we have
    the geometric product, we throw the coordinates away", which reads as if it was written for an
    older order where projection came first.
  - → Question 1.
- **Cross-references to content the cited page doesn't contain:**
  - `blade-square-sign.rst`: "In geometric-product you met … `e12` squares to −1". It never says so.
  - `rotation-from-vectors.rst`: "From geometric-product, a vector times a vector … is exactly the
    dot and the wedge". It never says so, and the wedge first appears later, in
    `levels-of-abstraction`.
  - `proof-cross.rst`: "In projection-rejection-3d we reduced one vector to the e₁ axis", and later
    "the two rotations of projection-rejection-3d". That page is only figures. The reduction is in
    `proof-projection.rst` › "Stepping up to three dimensions".
  - `proof-projection.rst`: "If you already read projection, you know the slick
    geometric-algebra formula". `projection.rst` has no formula.
  - `proof-rotate-from-a-to-b.rst`: "the same move does the work later in projection". It is in
    `proof-projection`.
  - `geometric-product.rst`: "spelled out in defining-g2". That page is a placeholder.
- **The "2D first half" rule is broken in Part I.**
  - `levels-of-abstraction` has 𝒢₃ cells.
  - `blade-square-sign` works grades 3–5.
  - `proof-projection` has a full 3D section.
  - `frames-qr` (including its 2D notebook) sits in the 3D stretch.
  - The toctree has no Part I / Part II split.
  - → Question 3.
- **`levels-of-abstraction` and `blade-square-sign` sit inside the rotate → product → projection
  spine, with no slot in the outline.**
  - `levels-of-abstraction` uses dot, wedge, Hestenes' `⟨ab⟩₀`/`⟨ab⟩₂`, `abs_sin`, the signed sine
    and Lagrange's identity, all before projection.
  - Its notebook uses floats (`u = 3.0 * g2.e_1 + 4.0 * g2.e_2`,
    `round(cos_squared_plus_sin_squared, 10) == 1.0`), against "canonical form over decimals". So
    does `notebooks/proof-projection.py:70-71`.
  - `blade-square-sign` uses "blade", "grade" and "reverse" before `defining-g2` exists.
  - → Question 2.
- **The rotate chapter is thin and contradicts its notebook.**
  - The book's founding definition ("rotate from a's direction to b's, not by an angle; magnitudes
    don't matter") gets three paragraphs in `rotate.rst`.
  - `notebooks/rotate.py` says "only the directions set the rotation", but then rotates `e_1` by an
    angle (`plane_rotation(e_1, e_2)(π/2)`). It never shows `versor_rotation` or
    `projection_rotation`.
- **`rotation-graph-paper` placement.** It sits between `geometric-product` and
  `levels-of-abstraction`. `tasks/levels-of-abstraction-book-voice-pass.md` still says that page
  sits "after geometric-product".

### 3.3 Errors in front of a reader

- **A math error in `rotation-from-vectors.rst` › "The angle was scaffolding":**
  `sin(θ) = (a ∧ b) / (|a| * |b|)`. The right-hand side is a bivector, not a number. Correct forms:
  `a ∧ b = |a| * |b| * sin(θ) * e12`, or `sin(θ) = ((a ∧ b)·e12) / (|a| * |b|)`. The second is what
  `levels-of-abstraction.py` uses.
- **`blade-square-sign.rst` › "Where this shows up"** says `pseudoscalar_squared_sign(r)` "returns
  precisely the count of flips". It returns the sign, ±1 (`src/gacalc/base.py:201`).

### 3.4 Notation rules (`CLAUDE.md` › "Math notation for readers")

- **Juxtaposition used for a product:**
  - `geometric-product.rst`: `e_1 e_{12} = e_2`, `e_2 e_{12} = -e_1`, and the sandwich
    `R\,\vec{v}\,\tilde{R}`.
  - `proof-rotate-from-a-to-b.rst`: `|\vec{a}|\,\vec{e}_1`.
  - `proof-projection.rst`: `\lvert\vec{b}\rvert\,\vec{e}_1`, `a'_1\,\vec{e}_1`, and the closing
    `\vec{a}\vec{b}`.
  - `proof-cross.rst`: `\lvert\vec{a}\rvert\,\lvert\vec{b}\rvert\sin(\theta)`, `m \, b_2'`,
    `\lvert\vec{a}\rvert\,\vec{e}_1`, and "the `\vec{e}_1\vec{e}_2` plane".
  - `notebooks/levels-of-abstraction.py` (markdown): `⟨ab⟩₀`, `⟨ab⟩₂`, `ab = a·b + a∧b`, and the
    unspaced `a_1*b_1 + a_2*b_2`.
  - `notebooks/geometric-product.py:42` (a comment).
  - `README.md`'s prose uses an unspaced `3*e_1 + 4*e_2`.
- **`\cdot` used as multiplication:** `geometric-product.rst` › "Keep everything exact",
  `12 \cdot 6^{-1} \cdot 5`.
- **Unnamed angle:** `proof-cross.rst` "(for `\cos^2 + \sin^2 = 1`)".
- **Prime placement:** `proof-cross.rst` and `notebooks/proof-cross.py` write `b_1'`. The rule and the
  other proof pages write `b'_1`.
- **Three spellings of the basis vector:** `e_1`, `\vec{e_1}`, `\vec{e}_1`. The outline picks none.
- **Two spellings of the reverse in the sandwich:** `R * v * R~` (`notebooks/geometric-product.py`)
  and `R * v * R^-1` (`notebooks/rotation-from-vectors.py:50`).
- **Alt text out of sync with the figure:** `proof-projection.rst`'s `sp2` figure is alt-texted
  "the angle phi". The figure (`book/figures/epix/sp2.py`) and the prose use θ.
- **`vector-addition.rst`** writes `translate(b)` but says the transform is "called by keyword"
  (`translate(b=...)`).

### 3.5 Author notes showing to readers, and draft marking

- **Text meant for the author, visible to readers:**
  - `index.rst`: "This is the skeleton — prose, graphs, and notebooks fill in later".
  - `proof-projection.rst`: "As promised in the outline". The outline is the internal
    `tasks/reference/book-outline.md`.
  - `relative-graph-paper.rst`: "Placeholder — content to come" sits above drafted content.
  - `projection-rejection-3d.rst`: a stale TODO waits on "after proof-projection is restructured as
    2D-then-3D", which is already done.
- **Draft disclosure is inconsistent.**
  - Four pages carry the "agent-drafted, voice pass pending" note: `vector-addition`,
    `relative-graph-paper`, `rotation-from-vectors` and `levels-of-abstraction`.
  - Pages with as much prose carry none: `proof-rotate`, `proof-rotate-from-a-to-b`,
    `geometric-product`, `rotation-graph-paper`, `blade-square-sign`, `proof-projection` and
    `proof-cross`.
  - Only two voice-pass tasks exist. Git history doesn't show which pages had the maintainer's voice
    pass. → Question 4.
  - Pages with a TODO but no Draft note: `projection`, `projection-rejection-3d`, `frames-qr`.

### 3.6 Smaller book issues

- **`proof-cross` is in the main toctree**, against the outline's rule that proof pages hang off
  their chapter. Its notebook sits in a `:hidden:` toctree, unlike every other page.
- **Licence headers:** only 10 of the 30 `.rst` files carry the GFDL-1.3 header. The book-wide pass
  from `tasks/archive/2026/08/03/port-rotation-explanation-from-mvp.md` has no task.
- **`api.rst`** omits `gacalc.standardposition` (cited by `proof-projection`) and `gacalc.nbplotutils`.
  The generated `g1`–`g5` are absent too, probably on purpose (LEAD).
- **`rotation-graph-paper.rst`** calls a rotation "**deformed** graph paper", but a rotation is rigid.
  Its sentence-case title differs from every other page's Title Case.
- **No action needed:** `proof-rotate.rst` keeps the CC0 SVG for its first figure. That is consistent
  with the 2026-10-06 ePiX decision.

### 3.7 README

- The "Layout" block omits `functions.py` and `nbplotutils.py`. VERIFIED.
- `make release` tells the maintainer to `git push origin v…`, but `origin` is the self-hosted box.
  `lean.yml` runs on GitHub tags, so the push that triggers it is to the `github` remote. VERIFIED
  (remotes read with `git remote -v`).

### 3.8 Demo notebooks (`notebooks/*.py`)

Found by the tests + notebooks reader; all VERIFIED.

- **Leftovers in `displaymv.py`:**
  - stray `5` cells at :691, :698, :705, :709;
  - a TODO at :651;
  - duplicated "Draw relative graph paper" cells at :569 and :597;
  - `T`/`S`/`R` aliases at :504-512, which the alias carve-out doesn't cover;
  - a history comment at :506.
- **`math.radians(53.130102)` where `math.atan2(4, 3)` is exact:** `displayg2.py:381,396` and
  `displaymv.py:551,569,597`.
- **`inner_product` presented as "the dot product":** `displayg2.py:491,507`, `displayg3.py:362,371`
  and `displaygraded.py:106`. This touches the dot-vs-scalar conflict in §1.1.
- **Bare blades used as coordinate vectors:** `displaygraded.py:184,356`. History comments at
  `displaygraded.py:275,281`.
- No `print` calls were found, and the licence headers are correct.

---

## 4. Code quality (`src/gacalc/`, hand-written)

### 4.1 High

- **`src/gacalc/base.py:1702` — `project` returns a bivector unchanged when projecting onto a
  vector.** VERIFIED; the main thread re-ran it.
  - `MultiVector.project(onto=e_1)(e_1 ^ e_2)` gives `{(1,2): 1}`.
  - `g3.G.project(onto=g3.e_1)(g3.e_1 ^ g3.e_2)` gives `Bivector(e_12=1)`.
  - Projection is an outermorphism, so the answer is `P(e₁) ∧ P(e₂) = e₁ ∧ 0 = 0`.
  - Cause: the code takes the 2.9c branch `(A·B) * B⁻¹` for every r-vector. Its own 2.9a branch,
    `(A·B)·B⁻¹`, gives 0. The grade narrowing `r_vector_part(r)` hides the mistake.
  - Fix: use 2.9c only when grade(A) ≤ grade(B), otherwise return zero. Check H&S's stated domain
    for 2.9c (LEAD: believed to be r ≤ s).
- **`src/gacalc/nbplotutils.py:470-474` — `draw_ndc` draws a pentagon, not the [−1,1]² square.**
  VERIFIED (re-read).
  - A stray comma splits `(1.0) * ex + (1.0) * ey` into the two list items `(1.0) * ex,` and
    `+(1.0) * ey,`.
  - The (1,1) corner is missing, and the four corner labels land on the wrong points.
- **`src/gacalc/standardposition.py:56` — `project_sp(a, 1*g3.e_3)` returns
  `Vector(nan, nan, nan)` without raising.** VERIFIED; two readers found it independently and the
  main thread re-ran it.
  - The module docstring documents the caveat, but there is no guard, no `require_vector`, no
    doctest and no test.
  - A `Gn` input crashes with `not enough values to unpack`, because `list(v)` omits zero
    coefficients.
  - Fix: raise `ValueError` when `b_x = b_y = 0`. Either type the functions to `g3`, or read
    coordinates with `coefficient(...)`.

### 4.2 Medium

- **`nbplotutils.py:325` — `sine` returns 0 for graded vectors.** VERIFIED.
  - `type(v1).from_blade_dict({(1,2): 1})` on a `Vector` drops the bivector (the graded "exp()
    trap"). So `sine(1*g2.e_1, 1*g2.e_2)` is 0, while it is 1 on `Gn`/`G`.
  - It is also 0 for perpendicular vectors off the e₁e₂ plane (`sine(e_1, e_3)`).
  - It uses `abs(v1 * v2)`, against the recorded `|a| * |b|` decision (§2.3).
  - It keeps a bare `assert` (:322).
  - It is untested.
  - Fix: `measure.signed_area(v1, v2) / (|v1| * |v2|)`, guarded to 𝒢₂.
- **`base.py:627-631` — `__truediv__` by a number.** VERIFIED.
  - `(1*g2.e_1)/3` gives a float, which breaks "int stays exact".
  - `(1*g2.e_1)/sympy.Integer(0)` gives `Vector(zoo, nan)`, though the docstring promises
    `ZeroDivisionError`.
  - Fix: `sympy.Rational(1, rhs)` for an int, plus an explicit zero check.
- **`transforms.py:681`** labels `uniform_scale`'s inverse `S_{-m}`. It should be `S_{1/m}`;
  `scale_non_uniform` gets this right. VERIFIED.
- **`transforms.py:230`** — `projection_rotation(a, a)` raises `ZeroDivisionError`, but
  `versor_rotation(a, a)` returns the identity. The two are documented as agreeing. VERIFIED.
- **`transforms.py:719`** — `scale_non_uniform` given fewer factors than the dimension zeroes the
  missing axes: `scale_non_uniform(2, 3)` sends `(1,2,3)` to `(2,6,0)`. The docstring doesn't warn
  about it. VERIFIED.
- **`frame.py:701-711`** — `term_and_coordinate` names its vector parameter `n`, shadowing the
  dimension `n`, against "the dimension is `n`". VERIFIED.
- **Remaining bare `assert` vector checks**, against the `require_vector` rule:
  `nbplotutils.py:322`, `base.py:1763`, `transforms.py:223`. Check whether
  `tasks/apply-2026-11-06-naming-and-scope-rules.md` lists them. VERIFIED.
- **`bivector_rotation` (`transforms.py:521`) raises `TypeError` for a wrong grade.** `CLAUDE.md`
  reserves `TypeError` for `isinstance` checks. Non-simple bivectors in 𝒢₄+ are documented as out of
  scope but not rejected. VERIFIED.

### 4.3 Low

- **Docstrings and comments that narrate history** (against "describe the present"):
  - `base.py:225` "Phase 1 (2026-08-15)…"
  - `base.py:529` "the previous…"
  - `base.py:1475` "This replaces the older…"
  - `base.py:2350` "An earlier version…"
  - the `normalize` docstring
  - `base.py:2638`
  - the `transforms.py` module docstring ("removed long before…", "backward compatibility")
  - `frame.py`/`measure.py` "contrast the blade-square-sign task"
  - `nbplotutils` `_to_xy`/`_draw_labelled_triangle`/`_current_axes`/`_blade_terms` ("Was written
    inline…")

  VERIFIED.
- **Notation in docstrings:**
  - `base.py:2168` `2 + 2cos θ = 4cos²(θ/2)`
  - `base.py:424` uses the middle dot as multiplication
  - `unit_pseudoscalar` docstrings write `n(n-1)`
  - the `exp` docstring writes `cosh|A| + sinh|A| Â`
  - `measure.py:252` `a_1 b_2 - a_2 b_1`
  - `frame.py` eq 3.2 is written `reverse(A_{k-1}) · A_k` though the code uses `*`; eq 3.7 and
    `R⁻¹ Qᵀ y` use juxtaposition
  - `functions.py` `Linearity` writes `A x`
  - `vectorcalc.py` writes `⟨a b⟩`
  - the `versor_from_vectors` docstring says "Geometric products are juxtaposition, as elsewhere",
    against the rule

  VERIFIED.
- **Dead code:**
  - `MultiVectorBase.identity` (~`base.py:2048`) is unused and duplicates `functions.identity`.
  - `_coerce`'s `case sympy.Expr()` arm is identical to its default arm.
  - `nbplotutils.py:201` builds and discards `np.array(...buffer_rgba())`.
  - a commented-out `ax.annotate` block
  - the unused `color`/`xcolor`/`ycolor` parameters in the triangle/ndc/screen/basis helpers
  - `draw_ndc` duplicating `_draw_labelled_triangle`

  VERIFIED.
- **Graded classmethods that return zero silently:** `g3.Vector.unit_pseudoscalar(3)` gives a zero
  `Versor`. `bases` and `symbolic_multivector` share the trap. VERIFIED.
- **`measure.py:239`**: the comment says `max_grade()` raises on zero, but it returns 0
  (`default=0`). VERIFIED.
- **`signed_content` on `Gn` with a dependent set** (`[1*e_1, 2*e_1]`): it implies n = 1 and raises
  "wrong count", instead of returning the documented 0. LEAD.
- **`gn.py:76`** "G and G will be specialized…" is garbled and in the future tense. VERIFIED.
- **`Gn` is not frozen, and `to_blade_dict()` returns its internal dict.** Mutating that dict
  corrupts the shared `e_1` constants. LEAD.
- **Unannotated bindings that `tools/check_annotations.py` misses** (§5.2):
  - `nbplotutils.py:493` `labels`
  - `nbplotutils.py:598,601` `xmin, xmax`
  - `nbplotutils.py:603` `fig, ax`
  - the tuple unpacks at `standardposition.py:49,56-57`
  - `rotate_in_*_plane(cos: object, sin: object)`, which should be `Real`

  VERIFIED.
- **Readability:** `gn.py`'s `decrease_grade` selects `identity()` as a function. A plain `if` would
  read better for a student.
- **Typo:** `nbplotutils.py:695` shows students "additon".

---

## 5. Generators and tools (`tools/`)

### 5.1 High

- **`tools/gen_specialized.py:4461-4476` — `Scalar.__iter__` yields the `Scalar` object, and yields
  nothing when it is zero.** VERIFIED (re-run).
  - `list(Scalar.from_real(3))` gives `[g2.Scalar(coeff_scalar=3)]`; `list(Scalar.from_real(0))`
    gives `[]`.
  - This breaks `CLAUDE.md`'s "iteration yields coefficient VALUES" rule and the method's own
    docstring ("Yields: Real").
  - Fix: `iter_method([()])`, yielding `self.coeff_scalar` unconditionally.
- **`gen_specialized.py:4550-4563` (`bilinear`), `:4605-4618` (`linear`), via `coerce_pair_gn`
  (:3178) — full `G` mixed with a graded type returns the slow `Gn`.** VERIFIED (re-run).
  - `type(G.e_1 * Vector.e_1)` and `type(G.e_1 + Vector.e_1)` are both `Gn`, while `Vector * G` gives
    `G`.
  - The `-> G` annotation and the generator's `cast(Self, …)` hide the mismatch.
  - Fix: same-algebra operands go through `_coerce(rhs, G)`. Keep the `Gn` path only for
    `Gn`/foreign operands, which `test_mixing_with_gn_coerces_to_gn` pins.
- **`gen_specialized.py:5415-5429` — the closed-form `Versor.sandwich` loses exactness.** VERIFIED
  (re-run).
  - The CSE reciprocal is emitted as `x2 = 1 / (x0 + x1)`.
  - So `(1 + 1*Versor.e_12).sandwich(1*e_1)` gives `Vector(0.0, -1.0)`, while `Gn` gives `-e_2`
    exactly.
  - Fix: an exact reciprocal for int operands.
- **`tools/reorder_lean.py` — the PLANs are stale, so running it would revert work.** VERIFIED.
  - `G1 --check` reports "WOULD change", because its PLAN is the pre-2026-10-29 order.
  - The `G3` PLAN aborts on 18 names it doesn't place.
  - There is no `G2` PLAN.
  - Nothing wires `--check` in, although its docstring says it "can gate drift".
  - Fix: `git rm` it as a finished one-shot tool, or update it and wire it into a target.

### 5.2 Medium

- **`tools/check_annotations.py` doesn't do what `CLAUDE.md` says it does.** VERIFIED.
  - It always returns 0, and no target or `format.sh` runs it.
  - Its docstring says gitignored files are excluded; that isn't implemented.
  - The `annotated` set is per file, so one annotated `x` exempts every unannotated `x` in that file.
  - Tuple-unpack assignments are never reported. That includes the `sympy.symbols` unpack
    `CLAUDE.md` requires to be declared.
- **`gen_specialized.py:4106-4127` — `Scalar.from_blade_dict` skips `_require_canonical_blades`.**
  `Scalar.from_blade_dict({(2,1): 5})` returns 0 silently, while `Vector` raises `ValueError`. Its
  local `d` is also unannotated. VERIFIED.
- **`gen_specialized.py:5103-5125`, `:4181-4200` — the non-number fallback of `__rmul__` computes
  `self * lhs`, the wrong order.** Called directly, `Vector.__rmul__(e_1, e_2)` gives `+e_12`. The
  normal operators don't reach this code today, so the bug is dormant. VERIFIED.
- **The generator relies on a hidden ruff autofix.**
  - `header()` (:5999) emits an unused `import numpy as np` and an unsorted import block.
  - `ruff check --fix` (:6059) silently fixes both, with its output suppressed.
  - Without ruff the output bytes differ (raw render diffed).
  - Fix: emit clean imports, then run ruff without `--fix` and fail on anything it finds.

  VERIFIED.

### 5.3 Docstrings the generator emits (`CUSTOM_METHOD_DOCS` and the doc constants)

Each was checked by running it. VERIFIED.

- **`scalar|right_contraction` (:1248)** says "x ⌊ s … the operand scaled". In fact `s ⌊ x = 0` for
  grade ≥ 1.
- **`bivector|right_contraction` (:925)** says "grade |C|−|B|". It is k−m, i.e. |B|−|C|.
- **`scalar|dual` (:712)** says "the scalar times the pseudoscalar". It is `s * I⁻¹`; the docstring's
  own example shows `-1 * Bivector.e_12`.
- **`versor|sandwich` (:2070)** says `R * x * R⁻¹` in the summary and `R * x * R̃` under Returns. For
  a non-unit versor these differ: `Versor.from_real(2).sandwich(e_1) == e_1`.
- **`I_DOC` (:2785) and `PLANE_DOC` (:445)** say `cos(t/2) − sin(t/2) * i` returns `i`. It returns
  **−i**. This also conflicts with `CLAUDE.md`'s `R = r * (cos(θ) + I * sin(θ))`. `I_DOC` ships in
  g2/g3 `Versor.i`.
- **Juxtaposition:** `a b = a·b + a∧b` (:1417, :1432), `R R̃ = 1` (:806), `(a ∧ b) I₃⁻¹` (:1596).

### 5.4 Low

- **`term_grade_key` (:271-282)**: the docstring says a CSE temporary "sorts last", but the code
  raises `ValueError`. No current output reaches that path. VERIFIED.
- **Dead code:**
  - `ROTATE_90_METHOD_DOC` (:2686) is never emitted.
  - `result_block_stmts` never uses its `owner` parameter (:3604).
  - `astbuild.return_construct`'s non-final branch and `construct_type_self` are unreachable.
  - `full_name_for(dim)` ignores `dim`.

  VERIFIED.
- **History comments:** "the old cast(Self, …) was unsound", "replaces the old bespoke bodies",
  "until now", and "matching the string gen" (`astbuild.bool_or`). The docstrings also use the stale
  suffixed names `ScalarN`/`Scalar_n`/`Vector_n`. VERIFIED.
- **`check_epix_keywords.py`** scans only the top level of `book/figures/epix`, so the live figures in
  `book/docs/notebooks/frame-qr-*.py` go unchecked (LEAD). It also skips chained calls.
- **`detect_unused_hypotheses.py`** is report-only (exit 0) and wired to nothing. Its text search
  flags hypotheses that are consumed implicitly. It may duplicate Lean's `unusedVariables` (LEAD).
- **`render_epix_figures.py`** catches only `CalledProcessError`, so a `FileNotFoundError` from
  `flatten_png` stops the loop. Outputs of deleted figures are never removed. VERIFIED.
- **Unannotated bindings:**
  - `check_epix_keywords.main`: `edits, unknown`
  - `check_epix_keywords.scan`: `module, name`
  - `bench.py`: `a, b`, `ga, gb`, `va, vb`
  - `reorder_lean.py`: `basename, plan`, `m`
  - `check_annotations.py`: `args`

  VERIFIED.
- **Checked clean:** the overload return types match the runtime types in all 728 graded
  (type, method, rhs-type) cases in g1–g3.

---

## 6. Tests (`tests/`)

### 6.1 High

- **The `project_sp` z-axis NaN is untested.** See §4.1.
- **`tests/test_sandwich_grades.py:63-70`, `test_versor_sandwich_of_bivector_matches_gn_3d`,** says it
  "agrees with the Gn reference" but only asserts the type. No value is compared. VERIFIED (re-read).
- **Tests that compare a value with itself.** VERIFIED (the `conjugate` case re-read).
  - `tests/test_versor_extraction.py:91,106` assert `R.conjugate() == R.reverse()`, but
    `base.py:2247` defines `conjugate` as `return self.reverse()`.
  - `tests/test_multivector.py:341,343` assert `u.normalize() == u * abs(u)**-1`, which is exactly
    `base.py:728`.
  - `tests/test_conformance.py:54`'s `CASES` include `(n, Gn)`, so about 60 parametrizations compare
    `Gn` with `Gn`.
  - Fix: assert the defining property (`R * R̄ == |R|²`, `|û| == 1`), and drop the `Gn` rows.

### 6.2 Medium

- **`tests/test_transforms.py:553-557`**: the reflect→project pipeline can't detect a broken reflect,
  because projecting onto e₁₂ gives e₁ from either e₁+e₃ or e₁−e₃. VERIFIED.
- **Slow cases that may need the `slow` mark** (host timings; the container is slower):
  - `tests/test_frame_class.py::test_iter_yields_the_original_vectors[frame_3d]`: 9.5 s
  - `tests/test_frame.py::test_reciprocal_frame_is_the_kronecker_delta[gn-3d-symbolic]`: 8.6 s
  - `test_reciprocal_frame_reconstructs_a_vector_symbolic[3d]`: 5.4 s
  - `test_forward_sends_basis_to_frame[3d]`: not timed

  Time them in `make test`. VERIFIED (host); LEAD (container).
- **Symbolic "proofs" restricted to the positive orthant**: `tests/test_graded.py:378` ("a real
  symbolic proof") and `tests/test_rotor_from_vectors.py:56,84,100` declare every component
  `positive=True`. Say so, or use `real=True` where sympy copes. LEAD.
- **The annotation auditor reports 49 rows (in 16 files) against the documented floor of 32.**
  - 10 new rows are in tests, and none appear in `tasks/reference/type-annotation-exemptions.md`:
    `test_line_to_line_projection.py:53,71` (`P`), plus 8 invariant `list` parameters in
    `test_frame.py`/`test_frame_class.py`.
  - The auditor misses tuple-unpack targets (`test_odd3.py:43,110`, `test_matrix_template.py:57,329`).
  - `tasks/annotation-auditor-floor-drift.md` still says 43/14.

  VERIFIED.

### 6.3 Low

- **Licence headers:**
  - No header at all: `tests/_helpers.py`, `test_isclose.py`, `test_odd3.py`,
    `test_operator_typing.py`, `test_pseudoscalar_square_sign.py`.
  - `Copyright (c) 2026` instead of `2025-2026`: `test_bivector_rotation.py`, `test_plane_rotation.py`,
    `test_vector_ergonomics.py`.

  VERIFIED.
- **`basis_vector` or aliases used where a constant exists:**
  - `test_plane_rotation.py:41-42` (`E1`/`E2`) and `:93`
  - `test_conformance.py:459,470`
  - `test_transforms.py:254-259,470-512`
  - `test_graded.py:448-450`

  VERIFIED.
- **Bare blades used as coordinate vectors:** `test_measure.py:205-207`,
  `test_bivector_rotation.py:58-60`. VERIFIED.
- **Smaller items:**
  - An orphan `# doc-region-end test add` at `test_multivector.py:56`, with no start marker.
  - History comments: `test_numeric_magnitude.py:68`, `test_exp.py:63`, `test_operator_typing.py`.
  - Bare "Bill's" in `test_measure.py:67` and `test_vector_ergonomics.py:18`.
  - Weak asserts: `assert symbolic.inverse() is not None` (`test_numeric_magnitude.py:87`), and an
    `is_frame == are_linearly_independent` check with no truth value pinned (`test_frame.py:105-106`).

  VERIFIED.

### 6.4 Doctest candidates (`doctests-by-default.md`)

- `test_frame.py::test_kronecker_delta` duplicates the doctest at `frame.py:321-325`; delete it.
- `test_measure.py::test_signed_content_on_gn_full_space` largely duplicates `measure.py:202-204`.
- `test_generator.py`'s `blade_label`/`field_name`/`blades_for_dim`/`_subscript` tests:
  `tools/gen_specialized.py` has no doctests for these functions.
- `test_pseudoscalar_square_sign.py::test_hand_counted_grades_one_through_five`:
  `pseudoscalar_squared_sign` has no doctest.

### 6.5 Coverage table

| Module | Tested | Doctests (`>>>` lines) |
|---|---|---|
| `base.py` | yes; only `add_parens_or_dont` and `pseudoscalar_squared_is_positive` are untested (the latter indirectly covered via `exp`) | 154 |
| `transforms.py` | yes; `compose_intermediate_fns*` by doctest only | 77 |
| `frame.py` | yes, except `Frame.reciprocal_vectors` | 34 |
| `functions.py` | yes | 37 |
| `measure.py` | yes | 52 |
| `standardposition.py` | numeric + symbolic; the z-axis edge is untested | 0 |
| `vectorcalc.py` | yes | 14 |
| `gn.py` | yes | 5 |
| `nbplotutils.py` | **no** (only the private `_expand_numerators_dict`) | 0 |

---

## 7. Proofs (`proofs/`)

`lake build --no-build` reports everything up to date. `#print axioms` was run on all 628 theorems:
every one rests only on `propext`, `Classical.choice` and `Quot.sound`. All 34 files are imported by
`proofs/GacalcProofs.lean`. Every Lean name cited in the book, the notebooks and the `src`
docstrings exists in the file it is attributed to.

### 7.1 High

- **`src/gacalc/base.py:1336-1340` and `CLAUDE.md` › "Assessment" item 2 claim more than Lean
  proves.** VERIFIED (re-read).
  - Both say `A ∧ B = 0 ⟺ A ∥ B` is machine-checked in `Predicates3D.lean`.
  - The file proves one direction only (`wedge_parallel_smul`: `a ∧ (k·a) = 0`), and its own
    header (:11) says "The converse … is not yet stated here".
  - Fix: prove the converse, or reword both places.
- **`proofs/check.sh` misdescribes itself, and its gate has holes.** VERIFIED (re-run).
  - Its header (:4-7) calls "the axioms grep" the reliable gate, but the script never runs one.
  - The grep `\b(sorry|admit)\b` (:46) does not match `sorryAx`; tested with `grep -wE`.
  - It also misses `axiom`, `native_decide` and `implemented_by`.
  - None of these is in the sources today, so nothing is hidden.
  - `.github/workflows/lean.yml` and `make lean`'s help repeat the false claim.
  - Fix: add a `#print axioms` sweep (the method the reader used) and correct the three
    descriptions.

### 7.2 Medium

- **Theorems that take free reals and build `vec …` inside** (the "scalars in" shape `CLAUDE.md`
  forbids). VERIFIED each.
  - G1: `vec_mul`, `wedge_vec`, `vec_mul_eq_dot_add_wedge`, `mul_vec_inverse_self`. `G1.IsVector` is
    defined and never used.
  - G2: `dual_vec_perp` (unused; `Predicates2D`'s doc wrongly says `dual_perp_dot` rests on it).
  - Projection2D: `vec_wedge_I_eq_zero`, `reject_from_I_eq_zero`.
  - G3: `vec_mul_perp` (unused).
  - Projection3D: `wedge_reject`, `plane_eq_wedge`, `mul_vec_inverse_self`.
  - Sandwich: `sandwich_fixes_orthogonal` and `sandwich_plane_invariant` (unused, uncited);
    `normSq_mul` and `inverse_mul` take versor components.
  - Measures: `signedArea` is defined over four reals.
  - Exp: `expBivectorGeneral p q r`.
  - RotateFromTo2D: `rotateFromTo_collapse`, `_carries`.
  - CrossStandardPosition: `cross_via_reduction_of_vectors` takes seven reals.
- **`_coord` leaves that fail the rule** (to be justified, a leaf must be fragile *and* shared by at
  least two object theorems). VERIFIED by grep.
  - One consumer each: `versor_mul_from_eq_bisector_coord`/`from_mul_versor_eq_bisector_coord`
    (2D and 3D), `sandwich_comp_coord` (a two-line `rw`), `rotation_fixes_normal_coord`, and G2's
    `reject_vec_eq_coord`.
  - Projection3D: `reject_eq_proj_normal_coord` and `project_eq_sub_reject_coord` serve only
    `proj_plane_eq_project_onto`, while object twins exist with duplicate proofs. Rewriting it needs
    a G3 `isBivector_wedge_of_isVector` (LEAD).
  - ProjectionRotation3D: 16 leaves, each with a single wrapper, several of them plain `rw` chains.
    ProjectionRotation2D shows the getter-native form works.
  - Dead wrappers: `wedge_vec_wedge_self`, `reject_in_plane_self`, `project_onto_in_plane_self`,
    `inner_vb_mul_reverse_self`.
- **The same fact proved twice.** VERIFIED each.
  - `normSq_uvec`/`magnitude_uvec` (Rotor) vs `uvec_magnitude` (TrigEquiv).
  - `normalize` (Rotor) vs `normalizeVec` (Normalize, ProjectionRotation2D).
  - `normSq_wedge_vec'` (ReciprocalFrame2D) vs `G2.normSq_wedge_vec`.
  - `normSq_wedge_vec3`/`crossSq`/`det3` (ReciprocalFrame3D) restate `G3.normSq_wedge_vec` and
    `signedVolume`.
  - Inside G3: the `wedge_self_vec_coord`, `mul_vec_self_coord`, `dot_self_vec_eq_normSq_coord` and
    `vec_mul_eq_dot_add_wedge` twins.
  - `rotor_unit'` is unused.
  - `rotation_preserves_dot` re-derives `isEvenVersor_versorFromVectors` inline.
  - `Rotation3D.vec_mul_mul_self` is dead.
- **Teaching-order violations** (`tasks/reference/algebra-teaching-order.md`). VERIFIED.
  - Laws that live outside their algebra: `G2.sub_mul` (StandardPosition2D:183); G3's
    `zero_mul`/`add_zero`/`zero_add` (ProjectionRotation3D:34-38).
  - There are no addition laws (Part II principle 3).
  - Distributivity comes before identity (G2:149-160, G3:161-180), against principle 4.
  - G3 defines `dot` at :222, after the laws.
- **Stale or wrong doc comments.** VERIFIED.
  - Projection3D:15 "Still to come" (it's done).
  - Rotation3D:27-35, a plan plus history.
  - RotateComponents:6 "currently carries Stage 1".
  - G3 `vec_anticomm_perp` names the wrong lemma it relies on.
  - Predicates2D:4 says `dot` is in Versor2D (it's G2:118).
  - Predicates3D:98 cites a note that doesn't exist.
  - Projection2D:9 claims a result no theorem proves.
  - CrossStandardPosition:224 says the angles are hidden, but they are parameters.
  - Sandwich:724 "wrappers" header.
  - G2:69 has a malformed "`mul e_1*e_2`".
  - The dangling task links listed in §2.4.
- **Statement mismatches.** VERIFIED unless marked.
  - `from_mul_versor_eq_bisector` (2D and 3D) multiplies by the *to*-vector, not the from-vector.
  - `rotateFromTo_carries`: no hypothesis ties `mb` to `|b|`, and nothing proves the middle
    (cos, sin) pair is a unit pair.
  - `rejectSP_eq_reject` (2D and 3D) takes both `magnitude b ≠ 0` and the equivalent
    `normSq b ≠ 0`.
  - `area_sq_vec`'s `IsVector` hypotheses look unneeded (LEAD; confirm by delete-and-rebuild).
  - `uvec_dot`/`uvec_wedge` state `.s`/`.c12` rather than `dot`/`wedge`.
- **Rechecked earlier leads:**
  - Confirmed: `tasks/lean-proofs-remove-extras.md` is still unapplied. The build replays the
    unused-`ring` warnings at G2:264 and ProjectionRotation3D:99 and four `hn` warnings, and
    `check.sh` has no `--wfail`.
  - Refuted: the earlier lead that ReciprocalFrame3D takes scalars. `recip*_vec`/`reject_*_vec` are
    permitted coordinate-computation leaves, and every theorem built on them takes objects; the real
    issue there is the duplication above.

### 7.3 Low

- **Notation in Lean doc comments** (and `proofs/README.md`):
  - Juxtaposition: G2:9-12, G3:6, Sandwich `R R̃`, Rotor:306 `2cos(θ/2)`, Rotation2D:244.
  - The middle dot used as multiplication: G1:36; G2:74,170,210,460,464; G3:58,62,190,227,231;
    Cross:62; Exp:15,61,144; Projection3D:9,145,179; Rotation2D:273.
  - A spaced star at CrossStandardPosition:301, against the no-space rule for Lean doc comments.
  - `cos²|B|` at Exp:152.

  VERIFIED.
- **History in comments:** G2:176, Rotor:135,268, ProjectionRotation2D:25, Rotation3D:7-11.
  VERIFIED.
- **Misplaced code:**
  - The G2 wedge-preservation theorems sit in Projection2D.
  - G2's `mul_vec_self` sits in ProjectionRotation2D.
  - G3's `rVectorPart` uses struct literals where G2's uses the basis constants.

---

## 8. Build, container, CI, packaging

### 8.1 Makefile, Dockerfile, entrypoint

- **Security: `make jupyter` exposes an unauthenticated JupyterLab to the network.** VERIFIED.
  - `entrypoint/jupyter.sh` runs with `--ip=0.0.0.0`, `--ServerApp.token=''`, `--ServerApp.password=''`
    and `--ServerApp.disable_check_xsrf=True`.
  - The Makefile publishes it with `EXPOSE_PORT = -p 8888:8888`, which binds every host interface.
  - So anyone who can reach the host on port 8888 can run code in the container, which has the repo
    mounted read-write. The script's comment ("super dangerous, but for our purposes, it's fine")
    assumes localhost only.
  - Fix: `-p 127.0.0.1:8888:8888`. This also affects `make shell`, which publishes the same port.
- **The Dockerfile masks a failed base install.** VERIFIED.
  - `Dockerfile:76-78` runs `/usr/local/bin/01-install-base.sh ;` and then the optional groups with
    `;`.
  - The `RUN`'s status is that of the final `uv pip install` chain, so a failing
    `01-install-base.sh` (which does accumulate its status) does not fail the build.
  - The template convention is to dispatch group scripts with `&&`.
- **`ENTRYPOINT ["/entrypoint.sh"]` names a file the image never contains.** VERIFIED.
  - `entrypoint/entrypoint.sh` is only bind-mounted (`FILES_TO_MOUNT`); it is never `COPY`'d.
  - Every Makefile target overrides it with `--entrypoint /bin/bash`, but a bare
    `podman run gacalc` fails.
  - The Dockerfile bakes the package source "for a non-mounted/pulled image" (:205-207), so that
    image can't start without an override.
- **`make image` passes `$(ELPA_MOUNT)` to `podman build`.** VERIFIED.
  - With the default `USE_EMACS=1`, the build gets `-v …/elpa:/root/.emacs.d/elpa:U,z`.
  - The comment above `ELPA_MOUNT` (Makefile:78-81) says the default is off, which went stale when
    `USE_EMACS` became `?= … 1`.
  - Mounting the vendored tree into the build is at odds with "packages are never baked". The
    `:U` chown on a build mount also changes the host tree's ownership. LEAD for the effect.
- **`test-all-dims` lacks the `: image` prerequisite** that every other container target has, and
  that `CLAUDE.md` › "Continuous integration" requires. VERIFIED.
- **No standalone `type-check` target.** The personal overlay names gacalc's `ty`-in-`format.sh` as
  legacy drift, to converge on a separate read-only `make type-check`. VERIFIED.
- **Stale comments:**
  - `Dockerfile:8-10` says flags are "full on a host, lean when built nested". Since 2026-09-27,
    nested builds are full unless `MINIMAL_IMAGE=1`.
  - `Dockerfile:186` lists "dnf/MELPA/TeX"; MELPA is no longer baked.
  - `entrypoint/05-install-emacs.sh` says "skips it in a lean nested image".
  - `entrypoint/03-install-notebook-tex.sh` says "Always installed … unconditionally" (§2.1).
  - `entrypoint/jupyter.sh` and `entrypoint/shell.sh` say "(scalar/g1/g2/g3.py)", but there is no
    `scalar.py`.
  - The Makefile `check-format` comment suggests `BUILD_DOCS=0 USE_EMACS=0 USE_SPYDER=0` rather than
    `MINIMAL_IMAGE=1`.
  - The `pyproject.toml` licence comment cites `gacalc.g2.Vector2`, which was renamed to `Vector`.

  VERIFIED.
- **Dead or vestigial pieces:**
  - `entrypoint/spyder.sh` only activates the venv; it never starts Spyder. `USE_SPYDER` stays 0
    everywhere.
  - `entrypoint/percentToIpynb.sh` converts only `displaymv.py`, and no target calls it.
  - Both are still bind-mounted by `FILES_TO_MOUNT`.

  VERIFIED that nothing invokes them; LEAD whether the maintainer still uses them by hand.
- **Script modes and shebangs:**
  - `entrypoint/docs.sh` is committed `100644`; every other entrypoint script is `100755`. It works
    because the target runs it through `bash`, but the template wants committed entrypoint scripts
    `+x`.
  - `docs.sh`, `entrypoint.sh`, `format.sh` and `percentToIpynb.sh` use `#!/bin/env bash` rather
    than `/usr/bin/env`. `format.sh` is meant to be host-runnable, and `/bin/env` isn't present on
    every host.
  - `shell.sh`, `jupyter.sh` and `spyder.sh` have no shebang.

  VERIFIED.
- **Two pytest configurations.** `pyproject.toml` `[tool.pytest] testpaths = ["tests"]`, but
  `pytest.ini` (`testpaths = src tests tools`) takes precedence. The pyproject block is dead and
  contradicts the real setting. VERIFIED.
- **Unpinned dependencies make an image rebuild unreproducible.** LEAD/convention.
  - `pyproject.toml` leaves every dependency loose, on purpose for consumers ("a library shouldn't
    force exact versions").
  - The image installs straight from that list (`-r pyproject.toml`), and pyright is npm-installed
    unpinned (`01-install-base.sh`).
  - So two `make image` runs months apart can resolve different versions.
  - The personal overlay's Python rule is to pin every direct dependency, and a lockfile or a
    constraints file is the usual way to pin the image without pinning consumers.
  - An exported image is unaffected (it is self-contained).

### 8.2 CI (`.github/workflows/`)

- **Every per-push job builds the full image, including Lean + Mathlib.** VERIFIED.
  - `checks.yml` runs its three jobs (`format`, `test`, `generated`) with
    `BUILD_DOCS=0 USE_EMACS=0 USE_SPYDER=0`.
  - The Makefile defaults `USE_LEAN`, `USE_EPIX` and `USE_JUPYTER` to 1 unless `MINIMAL_IMAGE=1`.
  - So each job builds the elan toolchain, the multi-GB Mathlib cache, ePiX from source and the
    XeLaTeX set: three times per push, for gates that need none of them.
  - `lean.yml` also builds ePiX needlessly.
  - Fix: `make <target> MINIMAL_IMAGE=1` in `checks.yml`, and `MINIMAL_IMAGE=1 USE_LEAN=1` in
    `lean.yml`. `CLAUDE.md` already describes `MINIMAL_IMAGE` as the flag for "fast CI".
- **Gates that exist but CI doesn't run:**
  - `make check-notebooks` (pyright over `notebooks/`).
  - The book's notebook execution, through `make docs`; no job builds the book.
  - `make lean` runs on tags only, by a recorded decision.

  VERIFIED.
- **`lean.yml`'s comment repeats the false "sorryAx axioms gate"** (§7.1). VERIFIED.

### 8.3 Versions, changelog, tags

- **`pyproject.toml` says `version = "0.1.0"`, and `CHANGELOG.md` has `## [0.1.0] — 2026-09-28`, but
  there is no `v0.1.0` tag.** The newest tag is `v0.0.20` (`git tag --sort=-v:refname`).
  - Either 0.1.0 shipped to PyPI without a pushed tag, or the changelog heading was promoted without
    a release. LEAD; check the PyPI JSON API.
  - `[Unreleased]` holds ~150 lines, including a changed default (`Frame.to_invertible_function` now
    defaults to `"reciprocal"`). So the next release needs a version bump, to `0.2.0` if it counts as
    breaking.

### 8.4 Checked clean

- `PODMAN_RUN_FLAGS` is threaded into every `run` line and no `build` line.
- `shell`/`shell-exec` share `SHELL_RUN_FLAGS`; `shell-exec: image`; `shell.sh` is bind-mounted, uses
  `set -e` and ends with `exec bash "$@"`.
- The feature-flag guards on `jupyter`/`docs`/`lean` follow the flag-echo pattern.
- The ARGs are declared per layer, with Lean first.
- `.dockerignore` is `**/`-anchored and excludes elpa.
- `format.sh` accumulates every step's status.
- The `image-export`/`image-import` pair is present.
- CI actions are pinned at `@v5`.

---

## 9. Open-task backlog (`tasks/*.md`)

### 9.1 Done, overlapping, or premise overturned

No open task is fully done in the code. VERIFIED unless marked.

- **`tasks/generalize-sandwich-other-grades.md`** (P8, "in progress"): only optional 𝒢₄/𝒢₅ tests
  remain. Its "Update" section contradicts its own 2026-10-22 work record. Archive it, with a one-line
  follow-up.
- **`tasks/define-frame.md`**: its Status still waits on the representation decision, which was made
  2026-11-04. It needs a rewrite, a re-rating and a BLUF.
- **Lean frame coverage: three docs disagree.** VERIFIED that they disagree; LEAD which is right.
  - `tasks/lean-frame-class-invertible-function.md` says theorems 1/5/6 are proved, yet its Open Q1
    still asks where theorem 1 goes.
  - `lean-ga-proof-architecture.md`'s table lists `make_orthogonal_frame*` as NONE.
  - `tasks/lean-frame-coverage.md`'s BLUF predates the ReciprocalFrame files, and it puts
    Priority/Difficulty inline in the Status line.
- **`tasks/frame-inverse-head-first-recursion.md`**: Q3 is marked "yes" while the next sentence
  recommends "no". `tasks/apply-2026-11-06-naming-and-scope-rules.md` still calls it blocked; it was
  unblocked on 2026-11-07.
- **`tasks/frame-svd-investigation.md`** waits on a task that finished on 2026-11-04.
- **`tasks/annotation-auditor-floor-drift.md`** says 43 findings in 14 files; it is now 49 in 16.
- **Three proof-notebook tasks overlap**, and two of them state the same `show_cancellation` /
  `\underbrace` requirement:
  - `tasks/investigate-lean-to-python-proof-notebooks.md`
  - `tasks/reference-doc-lean-workflow-and-proof-notebooks.md`
  - `tasks/proof-notebooks-student-math-notation-style.md`

  Make one the umbrella.
- **`tasks/generalize-reject-reflect-higher-grade.md`** Q6 overlaps
  `tasks/line-to-line-rejection-invertible-function.md` and
  `tasks/vector-and-plane-invertible-project-reject.md`.
- **`tasks/push-delicate-coordinate-core-tier.md`** lists deleted `_coord` lemmas as retained. There
  are 37 live `_coord` declarations, and §7.2 lists the ones that fail the rule.
- **`tasks/lean-proofs-remove-extras.md`** audited 32 files; there are 34. None of its fixes is
  applied (rechecked in §7.2).
- **`tasks/port-book-to-osbook-latex.md`**: the investigation it waits on is archived (2026-10-09),
  so its "revisit after" condition is met.
- **`tasks/displaygraded-geometric-plots.md`** points at the archived `epix-plot-integration.md`.

### 9.2 Missing structure

VERIFIED.

- **No `## BLUF`:** affine-flats-lines-planes-from-points, branded-coordinate-space-types,
  composable-function-followups, define-frame, displaygraded-geometric-plots,
  document-codegen-flow-pedagogical, generalize-reject-reflect-higher-grade,
  generalize-sandwich-other-grades, grassmann-absolute-relative-units,
  notebook-dot-wedge-projection-demo, parallelogram-foundational-narrative.
- **No `## Context`:** branded-coordinate-space-types, define-frame, displaygraded-geometric-plots,
  generalize-reject-reflect-higher-grade, generalize-sandwich-other-grades,
  proof-notebooks-student-math-notation-style, push-delicate-coordinate-core-tier.
- **Non-standard statuses:** "on hold" and "investigated".
- **Umbrella already archived:** two tasks say "Part of" the archived
  `tasks/archive/2026/10/04/investigate-lean-proofs-for-ga.md`.
- **Paths not repo-root-relative:** four tasks use `2026/…/x.md` paths.
- **Blocked tasks:** all have `Blocked on:`/`Recheck:`. grassmann's "do not re-raise unprompted"
  conflicts with having a Recheck.

### 9.3 Open tasks as rated (Priority/Difficulty), easy wins first

- **P4:** annotation-auditor-floor-drift D2
- **P5:**
  - displaygraded-geometric-plots D4
  - generalize-reject-reflect-higher-grade D4
  - reciprocal-frame-proof-book-page D4
  - apply-2026-11-06-naming-and-scope-rules D6
  - proof-notebooks-student-math-notation-style D6
- **P6:**
  - lean-proofs-remove-extras D2
  - composable-function-followups D4
  - reference-doc-lean-workflow-and-proof-notebooks D4
  - line-to-line-rejection-invertible-function D5
  - frame-svd-investigation D6
- **P7:**
  - port-cayley-graph-from-mvp-investigation D2
  - levels-of-abstraction-book-voice-pass D3
  - proof-projection-book-voice-pass D3
  - frame-inverse-head-first-recursion D4
  - model-higher-odd-and-mixed-graded-types D5
  - vector-and-plane-invertible-project-reject D6
  - investigate-lean-to-python-proof-notebooks D7
  - lean-general-multivector-inverse D7
- **P8:**
  - generalize-sandwich-other-grades D5
  - gn-graded-typing-implement D6
  - define-frame D7
  - push-delicate-coordinate-core-tier D8
- **Blocked:**
  - notebook-dot-wedge-projection-demo 6/2
  - parallelogram-foundational-narrative 6/3
  - document-codegen-flow-pedagogical 6/3
  - grassmann-absolute-relative-units 7/3
  - affine-flats-lines-planes-from-points 7/7
- **Parked / on hold:**
  - lean-frame-coverage 8/5
  - lean-frame-class-invertible-function 8/6
  - branded-coordinate-space-types 9/7
  - grade-simp-tactic-reduce-proof-boilerplate 9/6
  - lean-general-gn-product-and-hestenes-dot-wedge 9/8
  - port-book-to-osbook-latex 10/9

**Ratings that don't match the content:**

- generalize-sandwich (archive it);
- define-frame (its blocker is gone);
- push-delicate (P8 despite the maintainer's "GO"; confirm);
- port-cayley (P7 for a one-word decision).

**Nothing in the backlog covers** most of §4–§8 of this record. That includes the library, generator
and test bugs, the CI image size and the Jupyter exposure.

### 9.4 Book work, tracked vs untracked

- **Tracked:**
  - `tasks/levels-of-abstraction-book-voice-pass.md`
  - `tasks/proof-projection-book-voice-pass.md` (with the B2/B3/N1 ideas)
  - `tasks/reciprocal-frame-proof-book-page.md` (decided: `proof-reciprocal-frame.rst`)
  - parallelogram-foundational-narrative (blocked)
  - port-book-to-osbook-latex (parked)
- **Untracked:**
  - the other voice passes (§3.5)
  - the reflection chapter
  - the GFDL licence pass (§3.6)
  - the full reciprocal-frame figure (LEAD)
  - all of §3.2–§3.4

---

## 10. Archive hygiene (`tasks/archive/2026/`)

### 10.1 Not rewritten into done-records

VERIFIED, and systemic: about 130 of the 295 archived docs still carry plan scaffolding.

- **June–July (100 docs):**
  - Counts: 47 still have Open questions, 40 a Plan, 25 unchecked boxes, and 19 an "(original plan
    below)" section. None has a BLUF.
  - Status lines frozen before commit:
    - `06/07/graded-class-e_n-zero-vs-basis-vector.md` ("awaiting author commit")
    - `07/09/plane-rotation-pretag-and-mvp-adoption.md` ("ready to tag v0.0.8 after …")
    - `07/09/upgrade-rotation-and-ctc-vector-mapping.md`
    - `07/22/precise-dual-typing.md`
    - `06/27/descriptive-names-in-generator.md`, `07/29/jupytext-default-viewer.md` and
      `07/29/suppress-jupyter-news-prompt.md` ("ready to archive")
  - Bare "Bill" appears 159 times across 52 files. These are historical; rewrite them only during a
    done-record pass.
- **August–September (76 docs):** 42 keep plan scaffolding. The worst:
  - `08/15/redo-exp-book-referenced.md` (439 lines, "in progress")
  - `08/16/prove-blade-square-sign-equals-pseudoscalar-squared.md`
  - `08/26/precise-typing-remaining-methods.md`
  - `09/27/minimal-nested-image.md` (its BLUF describes the abandoned `NESTED_PODMAN` idiom)
  - `08/04/graded-typed-module-basis-constants.md`
  - `08/22/generated-dual-default-dimension.md`
  - the two `08/13/harvest-*` docs (COMPLETED, every item unchecked)
  - `09/14/trim-claude-md.md`
  - the 09/30 `lean-*` docs
- **October–November (~119 docs):**
  - Unchecked plans: `10/05/add-lagrange-identity-references.md`,
    `10/05/consolidate-symbolic-equality-predicate.md`, `10/05/rotor-extract-r-i-theta-a-b.md`,
    `10/22/github-actions-pypi-publish-on-tag.md`, `10/07/epix-plot-integration.md`.
  - "Context (read first)" plus a Plan: `10/19/vector-addition-translate-partial-binding.md`,
    `10/05/consider-renaming-scalar-to-real.md`, `10/07/book-epix-figures-step-{1,2,3}`.
  - Stale "Ready to archive": two `10/27/` docs.
  - Minor: the 22 `10/09` docs keep an empty "Open questions: None.".
  - One bare first name, in `10/09/coordinate-subscripts-indices-not-xyz.md:13`.
  - The November archives are lean.

### 10.2 Superseded decisions with no "superseded" note

VERIFIED. Each of these old docs states a decision that was later reversed, and none says so:

- **`06/06/codegen-checkin-strategy.md`**: "keep generated g*.py checked in". Reversed the next day
  (`06/07/build-time-codegen-dist.md`; `design-decisions.md:19`).
- **`06/06/regen-diff-ci-guard.md`**: a `git diff --exit-code` over committed g*.py. Now gitignored,
  with a determinism check (`design-decisions.md:45`).
- **`06/06/clarify-2d-only-transforms.md`**: removed `rotate_90_degrees`. It came back g2-only on
  2026-09-06.
- **`06/06/add-python-types.md`**: "light-touch typing". Now "annotate every binding".
- **`06/06/graded-blade-subtypes.md`**: `Vector2`/`Rotor2`, a shared `scalar.py`, "no Odd type". All
  three were later changed.
- **`06/06/inverse-exact-reciprocal-fix.md`**: "escape hatch not taken". The 06/13 numeric-magnitude
  work took it.

Reversals that are already documented elsewhere and need no note: the `isclose` default, the
`AlgebraLaws.lean` fold-in (`cefc3ed`), the `Projection3D` rename, and `Rotor` → `Versor`.

### 10.3 Dangling references

VERIFIED.

- **SHAs that no longer resolve:**
  - `6c88fae` (`06/07/graded-class-e_n-…`; likely now `9e28603`, LEAD)
  - `237ede7` (`07/09/upgrade-rotation-…`; likely now `a0bedea`, LEAD)
  - `e6e1643`, `e5e829f`, `257b40a`, `bf026eb`, `76ac097` (`10/09/coordinate-proofs-alongside-early-results.md`)
- **Hashes that are fine:** the doc-region hashes in `emit-doc-region-markers.md`; SHAs from other
  repos, when labelled (epix-mirror, galgebra `ff0a938`); and the image ID `b294e77bfbc7`.
- **Pointers to `tasks/<slug>.md` that have moved** (about 100 in total):
  - June–July: 46 missing paths. 34 are gacalc moves (worst: `tasks/model-odd-graded-type.md`,
    7 hits), 11 are mvp tasks cited without a URL, and 1 resolves nowhere
    (`tasks/show-mult-expand.md`).
  - August–September: 15 moved. Worst: `tasks/investigate-lean-proofs-for-ga.md`, the "Part of"
    header in 8 Lean docs.
  - October–November: about 40, e.g. `tasks/reciprocal-frame-hestenes.md`, still described as
    blocking.
- **Wrong paths:**
  - `tasks/archive/specialized-multivectors.md` and `…/06/05/…` (the real one is `…/06/03/…`)
  - `10/05/python-book-rotor-naming-after-lean.md` → `unit-bivector-and-versors.md` (the real file is
    `unit-bivector-and-rotors.md`)
- **Container-absolute paths:** `/mvp/tasks/gacalc-math-migration.md` (×2), `/mvp/venv`,
  `/foo/opt/modelviewprojection`.
- **Unexplained missing file:** `entrypoint/README`, cited by
  `06/07/emacs-package-install-strategy.md:111`.
- **Path-less wiki-links:** 15 June–July docs.

### 10.4 One-shot scripts never removed

`tasks/adhoc/drop-graded-type-dimension-suffixes/codemod.py` and `prose_codemod.py` are still
tracked, though their task is archived. They should have been `git rm`'d in the archive commit.
VERIFIED.

<!-- notation-rule: end -->

---

## Carried over from the previous review

None. This is the first review.

## Suggested follow-ups

Tagged by urgency. The maintainer will turn these into tasks, citing this record by section.

- **Required:** wrong in front of a reader or user, a gate that silently doesn't run, or a security
  exposure.
  - Fix `project` for grade(A) > grade(B) (§4.1).
  - Fix the three generator bugs: `Scalar.__iter__`, `G` with graded operands returning `Gn`, and the
    inexact `sandwich` (§5.1).
  - Fix `draw_ndc`'s stray comma (§4.1).
  - Guard `project_sp` against `b` on the z-axis, with a test (§4.1).
  - Reword or prove the `A ∧ B = 0 ⟺ A ∥ B` claim in `base.py` and `CLAUDE.md` (§7.1).
  - Make `proofs/check.sh` actually check axioms, and correct its three descriptions (§7.1).
  - Either add the `ty` step and `: image` to `make test-all-dims`, or correct the three docs that
    describe it (§2.1).
  - Bind Jupyter to `127.0.0.1` (§8.1).
  - Fix the sin(θ) formula and the `pseudoscalar_squared_sign` claim in the book (§3.3).
  - Delete or update `tools/reorder_lean.py` before anyone runs it (§5.1).
- **Recommended:**
  - Use `MINIMAL_IMAGE=1` in CI, and add `check-notebooks` to CI (§8.2).
  - Fix the Dockerfile's masked base install, and bake or drop the `ENTRYPOINT` (§8.1).
  - Make `check_annotations.py` fail and wire it into a gate, or stop calling it enforcement (§5.2).
  - Rewrite the tests that cannot fail, and the bivector-sandwich test (§6.1).
  - Fix the medium library bugs (§4.2) and the misleading generated docstrings (§5.3).
  - Answer Questions 1–3, then restructure the book order and the Part I/II split (§3.2).
  - Do a notation sweep of the book and notebooks, and pick one basis-vector spelling (§3.4).
  - Fix the broken cross-references and the author-facing notes (§3.2, §3.5).
  - Flesh out `rotate.rst` and its notebook (§3.2).
  - Refresh `book-outline.md` (§1.2).
  - Fix the false Lean-gate and architecture claims (§1.1).
  - Move `lean-proof-corpus-review-2026-10-04.md` out of `tasks/reference/` (§1.2).
  - Resolve the `CLAUDE.md` dot-product contradiction (§1.1).
  - Archive `generalize-sandwich-other-grades.md`, re-rate `define-frame.md`, and reconcile the three
    Lean frame-coverage docs (§9.1).
  - Record the decisions listed in §2.3.
  - Replace the bare asserts (§4.2).
  - Fix the Lean teaching-order and "scalars in" violations (§7.2).
  - Resolve the `0.1.0` tag/version question (§8.3).
- **Optional:**
  - A done-record pass over the ~130 archived docs, with "superseded" banners (§10.1–§10.2).
  - Repoint the moved pointers and dead SHAs (§10.3), and the archived-task citations in source
    (§2.4).
  - GFDL headers on the remaining 20 pages (§3.6), and the test licence headers (§6.3).
  - Add `standardposition` to `api.rst` (§3.6).
  - Merge the three proof-notebook tasks (§9.1), and add BLUF/Context where missing (§9.2).
  - `git rm` the leftover ad-hoc scripts (§10.4) and `TODO.org` (§1.2).
  - Clean up the Lean duplication and dead lemmas (§7.2).
  - The low items in §4.3, §5.4, §6.3, §7.3 and §8.1.
  - Add doctests in place of the duplicate tests (§6.4).
  - Pin or lock the image's dependencies (§8.1).

## Open questions for the maintainer

Unanswered as of 2026-11-08. Each blocks the book work that depends on it.

1. **The geometric-product story:**
   - (a) keep "the product comes from rotation" as the book's story, cut `proof-projection.rst`'s
     promise to build it from projection later, and park (b) as its own task; or
   - (b) add a chapter that builds the product from projection and rejection, and reword
     `geometric-product.rst` to match.

   The reviewer recommends (a). See §3.2.
2. **Move `blade-square-sign` and `levels-of-abstraction` to after `defining-g2`**, where blades,
   grades, the reverse and dot/wedge are defined? The reviewer recommends yes. See §3.2.
3. **Move Part I's 3D material to Part II, and split `index.rst` into two captioned toctrees?** The
   material: `proof-projection`'s 3D section, the 𝒢₃ cells of `levels-of-abstraction`, and the grade
   3–5 examples of `blade-square-sign`. The reviewer recommends yes. See §3.2.
4. **Which book pages has the maintainer already voice-passed?** Every page not yet passed would get
   the Draft note and a voice-pass task. See §3.5.
