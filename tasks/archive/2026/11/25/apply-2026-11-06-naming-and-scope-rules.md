# Apply the 2026-11-06 naming and scope rules across geometricalgebra

**Done:** 2026-11-25 (work commit; the archive move follows). Source: the maintainer (William Emerison Six <billsix@gmail.com>, 2026-11-06): "make a task to search through all of geometricalgebra and see if there is programming advice that we added that should be applied to the codebase, to refactor it". Deferred on 2026-11-14 so the maintainer could be present; approved and run on 2026-11-25 as the last of the seven repositories.

## What this did

Five rules entered the shared Python standard on 2026-11-06 (github.com/billsix/runClaudeInContainer, `tasks/reference/python-coding-standard.md`: "Inline a value used once, and name it in a comment instead of a binding" and "What earns an extraction"): inline a binding used once; a binding used twice does not automatically earn a name; declare a name at the point of use; nest a helper with one caller inside that caller; shadow deliberately when nesting. The task surveyed the hand-written Python in `src/gacalc/` (not the generated `g*.py`), `tools/`, `tests/`, `notebooks/`, `book/figures/epix/` and `examples/`, and refactored without changing behaviour. The vendored Emacs tree and `proofs/` (Lean) are out of scope.

## Decisions, in order (William Emerison Six <billsix@gmail.com>, 2026-11-25)

- **Question 1, survey first, or survey and apply:** survey first, then use discretion and apply (taken from the maintainer's 2026-11-24 decision for the same question in the Programming3DComputerGraphics task).
- **Question 2, a helper a test imports:** counts as having a second caller and stays at module level (same source and date).
- **Question 3, the generator's emitted code:** apply the rules to the generator's own source only, not to what it emits. Recorded in `tasks/reference/python-coding-standard-gacalc.md` ("Where the naming and scope rules stop") and `tasks/reference/code-generator-architecture.md` ("How to change it").
- **Question 4, the book notebooks:** include them, but a binding a cell displays or the page's prose names keeps its name. Recorded in the same two docs and in the checklist of `tasks/reference/book-notebook-teaching-style.md`.
- **Mechanics:** rule 4 by the shared `nest_one_caller.py` (runClaudeInContainer `tasks/reference/`); the finished Programming3DComputerGraphics task, archived under `tasks/archive/2026/11/25/` there, is the worked example.

## What was done

- **Survey:** `tasks/adhoc/apply-2026-11-06-naming-and-scope-rules/discover.py` wrote 1,882 leads over the in-scope files: 942 `ONCE`, 754 `TWICE`, 54 `FAR`, 132 `ONE_CALLER`.
- **Nested (rule 4): 83 helpers in 19 files.**
  - **Library, 17:** `_marked_product_latex`, `_coefficients` and `_side_latex` in `nbdisplay.py`; `generategridlines` and `_coef_as_float` in `nbplotutils.py`; `_region` and `_text` in `epixscene/venn_scene.py`; `init_fonts_and_markdown`, `_read_shader`, `compile_program` and `_cross_arrays` in `gl/_pipeline.py`; `gui_button` and `rectangular_prism_lines` in `gl/cayley_gl.py`; `build_basis_shaft` in `gl/grapher2d.py`; `_height_color` in `gl/grapher3d.py`; `_push_matrix` and `_pop_matrix` in `gl/matrix_stack.py`.
  - **Tools, 65:** the generator (`gen_specialized.py`, 35, for example `generate_constants`, `generate_quarter_turn` and `inject_method_docstrings` into `main`, and the class and graded-type helpers into `generate_class` and `generate_graded_type`), `astbuild.py` (4), and the checkers and report scripts (`check_annotations.py` 7, `bench.py` 4, `check_epix_keywords.py` 3, `check_notebook_prose_width.py`, `check_lean_arch_doc_names.py` and `derive_lean_algebra.py` 2 each, `check_doc_regions.py` 1, and the rest).
  - **Notebooks and figures, 1:** `mapping` into `draw` in `notebooks/relative-graph-paper.py`. The tool had moved the jupytext `# %%` cell marker above `mapping` into the function body, which merged two cells; the marker was put back above `draw`, and no repository I nested has another indented cell marker.
  - The tool skipped every helper with a doctest (`doctest` does not collect a nested function) and every helper named in another file (`_require_canonical_blades`, `draw_angle`, `arrow`, `basis_vectors`, `toggle_fullscreen`, `set_current_matrix`, `marker` and a few more); its output repeats each skip once per cascade pass. Notebooks and the non-underscore figure scripts were nested one at a time in a scratch repository (`nest_isolated.sh`), because they are run, never imported, and their same-named helpers are not callers of each other; only one one-caller helper turned up there. A second run of both modes found nothing to nest.
- **No doc-region was touched:** the only hand-written files with real `doc-region` markers (`functions.py`, `transforms.py`) had no helper to nest; the `doc-region` strings in `astbuild.py` and `gen_specialized.py` are text the generator emits.
- **Reformat:** `make format` re-wrapped the deeper code; nine single-line docstrings that the extra indent pushed past 88 columns were shortened or split into a summary line and a second line, and one f-string was split into two adjacent literals.
- **Left alone, with the reason:**
  - The generated `g1`–`g5` (decision 3).
  - Every file in `tests/` (named inputs, expected values and case tables; no test helper was nested).
  - The notebooks and figure scripts' `ONCE` and `TWICE` bindings (decision 4: a student's view shows the name, or the page's prose names it; no comment is added in a notebook).
  - GL handles, pipelines, window state and uniform values in `gl/` (`FAR` leads such as `view`, `win_state`, `line_pipeline`, `label_renderer`: they are set up once at the top of `run` and read in many places, so a declaration at the first use would be repeated).
  - The generator's multi-use `FAR` and `TWICE` locals (`fields`, `self_ann`, `mvb_ann`, `a_mv`, `b_mv`, `has_scalar`: named once and read by many emitted statements) and the 942 `ONCE` leads in `src/` and `tools/`, most of which are comprehension and `for` targets or teaching locals in `src/gacalc/`.
  - No further inline or move was applied in this task: the nesting was verified as a whole, and an inline would have invalidated that verification.

## Result

- Applied: the 83 nestings, the docstring and f-string fixes, and one restored cell marker; 19 files changed. Behaviour is unchanged (see Verification).

## Verification (containerized, lean image, 2026-11-25)

- **The regenerated `g1.py`, `g2.py` and `g3.py` are byte-identical** before and after (checksums recorded before the change), which is the direct proof that nesting 35 helpers in the generator changed what it emits. `make check-generated` (two runs identical) exit 0, `make check-regions` exit 0.
- `make format` exit 0 (ruff check, ruff format, `ty` over `src`, `tests`, `tools`, `notebooks` and `examples`, the changelog check, the epix keyword check and the notebook prose-width check); `make check-notebooks` (pyright) 0 errors, run again after the cell-marker fix.
- `make test`: 1,412 passed, 3 skipped, 12 deselected.
- **Not run:** the 12 tests marked `slow` (`make test-full`, about 27 minutes, which CI runs on push; none of the nested files is exercised by them), `make docs` (needs the full image), the ePiX scene helpers and figure scripts (`venn_scene`, `book/figures/epix`; ePiX is not in the lean image), and the OpenGL toolkit (`gl/`, nine nested helpers; it needs a display).

## Owed

- The maintainer runs `examples/grapher2d.py` and `examples/grapher3d.py` once on a real display (the Light menu and `T` key were already on the list from the 2026-11-25 batch), to see the nested GL helpers draw.
- `make test-full` in CI on the pushed branch is the check for the slow tests.
