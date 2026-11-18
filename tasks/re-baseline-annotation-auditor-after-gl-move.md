# Re-baseline the annotation auditor: annotate the moved-in GL / Cayley modules

**Status:** proposed — needs go-ahead
**Priority:** 6
**Difficulty:** 3
**Created:** 2026-11-18 (William Emerison Six <billsix@gmail.com>; found in the 2026-11-18
session-end sweep)

## BLUF

`tasks/reference/type-annotation-exemptions.md` records a floor of **39 rows in 16 files**,
re-baselined on 2026-11-09. `python tools/check_annotations.py` now reports **167 rows in 29
files**. Almost all of the growth comes from the GL and Cayley modules moved in from
github.com/billsix/modelviewprojection on 2026-11-12/13 (`ea5b01f`, `280ddd1`), which were written
before "annotate every binding" applied to them. Done means:
- every new row is annotated, or listed in the exemptions doc with its reason;
- the doc's floor paragraph states the new count and split;
- `ty check` (in the container, where the GL packages exist) and `make test` pass.

## Context (read first)

- **The rule:** annotate every binding, loop targets included (declared on the line above the
  `for`). It is in the shared Python standard (github.com/billsix/runClaudeInContainer
  `tasks/reference/python-coding-standard.md`) and `CLAUDE.md` › "Coding standard (Python)".
- **The auditor:** `tools/check_annotations.py`. It is a report, not a gate, by the maintainer's
  decision of 2026-11-09. `--full` prints every row, and `--path`/`--kind` narrow the output.
  Type aliases (`ALIAS`) and `Enum` members (`ENUM`) are printed but classified out.
- **The exemptions doc:** `tasks/reference/type-annotation-exemptions.md` (§1 `Any` … §6 symbol
  unpacks; the floor paragraph near the top). Earlier rounds:
  - `tasks/archive/2026/10/09/re-baseline-annotation-auditor.md`;
  - `tasks/archive/2026/11/09/annotation-auditor-floor-drift.md`.

## The 167 rows (snapshot 2026-11-18)

- **Classified out, no action:** 45 (31 `ENUM`, 14 `ALIAS`). This was 13 at the floor; the moved-in
  modules add enums and aliases.
- **Moved-in modules, about 97 rows, the bulk of the work** (`LOOP` plus `LOCAL` per file):

  | File | `LOOP` | `LOCAL` |
  | --- | --- | --- |
  | `src/gacalc/gl/grapher3d.py` | 11 | 11 |
  | `src/gacalc/gl/_pipeline.py` | 10 | 7 |
  | `src/gacalc/gl/cayley_gl.py` | 7 | 8 |
  | `src/gacalc/cayley/cayleyscene.py` | 11 | 2 |
  | `src/gacalc/cayley/cayleygraph.py` | 8 | 1 |
  | `src/gacalc/gl/grapher2d.py` | 7 | 2 |
  | `src/gacalc/gl/labels.py` | 3 | 1 |
  | `src/gacalc/gl/matrix_stack.py` | 0 | 2 |
  | `tests/test_matrix_stack.py` | 2 | 3 |
  | `tests/test_cayley_scene.py` | 0 | 1 |
- **Everything else, about 25 rows:** roughly the old listed exemptions. They are:
  - `nbplotutils.py`, 9 `ANY` (§1);
  - `tools/astbuild.py`, `check_annotations.py` and `gen_specialized.py`, 4 `INVAR` (§4);
  - `base.py`, 1 `RET`;
  - `tests/test_conformance.py`, 1 `RET` and 1 `PARAM`;
  - `tests/test_graded.py`, 3;
  - 6 `LOCAL` in `notebooks/display*.py`.

  Confirm each one against its listed exemption. A row that is in neither the doc nor this task is
  a gap.

## Plan

1. Save the discovery as `tasks/adhoc/re-baseline-annotation-auditor-after-gl-move/discover.sh`
   (`python tools/check_annotations.py --full`), with a snapshot of its output in `data/`.
2. Annotate the moved-in modules file by file:
   - loop targets declared above their `for`;
   - locals given their concrete types: numpy arrays as `np.ndarray` or the module's existing
     aliases, GL handles with the types the module already uses.

   Where a binding's type comes from an untyped GL library (PyOpenGL/glfw return values), use the
   narrowest honest annotation. If only `Any` fits, list the row in the exemptions doc (§1) with
   the library named as the reason.
3. Check the ~25 remaining rows against the doc. Fix any that are not exemptions.
4. Rewrite the floor paragraph with the new total and split, and add this task to its records.
5. Gates, all in the container, because `glfw`, PyOpenGL and imgui are absent from a bare host:
   - `ty check --no-respect-ignore-files src`, `ty check tests`;
   - `make format`;
   - `make test`.

   The annotations must not change behaviour, so the GL tests (`tests/test_matrix_stack.py`,
   `tests/test_cayley_*`, `tests/test_gl_import_boundary.py`) must still pass.

## Open questions

None. The report-not-gate decision (2026-11-09) and the annotate-every-binding rule already settle
the policy; this task only applies them to the new code.
