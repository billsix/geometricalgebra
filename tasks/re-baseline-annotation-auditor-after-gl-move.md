# Re-baseline the annotation auditor: annotate the moved-in GL / Cayley modules

**Completed:** 2026-11-18 (William Emerison Six <billsix@gmail.com>; overnight batch
`overnight-batch-2026-11-18`)
**Priority:** 6
**Difficulty:** 3
**Created:** 2026-11-18 (found in the session-end sweep)

## Outcome

`python tools/check_annotations.py` went from **167 rows in 29 files** to **69 rows in 23 files**.
`tasks/reference/type-annotation-exemptions.md` records the new floor. Every remaining row is either
classified out (14 type aliases, 31 enum members) or a listed exemption (24).

- **Annotated: the 97 rows in the modules moved in from github.com/billsix/modelviewprojection**
  (`ea5b01f`, `280ddd1`). Loop targets are declared above their `for`, and unpacked locals above
  their assignment, with the modules' own types:
  - `Edge`, `Step`, `N` in `cayley/cayleygraph.py`;
  - `CoordinateFrame[N]`, `InverseOperations[N] | NonInvertibleTransformation`, `TimedStep`,
    `InverseOpsTrack` in `cayleyscene.py`;
  - `GLHandle`, `VertexCount`, `Point3`, `cayleyscene.GuiButton`/`GuiGroup` in `gl/cayley_gl.py`;
  - `AttribSpec` in `gl/_pipeline.py`, `Label` in `gl/labels.py`;
  - `DynamicLines`, `PlottedFunction` in `gl/grapher2d.py`, `Surface` in `gl/grapher3d.py`;
  - the same in `tests/test_matrix_stack.py` and `tests/test_cayley_scene.py`.

  The GLFW window, renderer and ImGui IO are annotated with the existing TYPE_CHECKING alias
  `"GLFWWindow"` and the quoted `"cayley_gl.GlfwRenderer"` / `"cayley_gl.imgui.IO"`; local-variable
  annotations are never evaluated at run time. No `Any` was needed.
- **One gap outside the moved-in code:** `tools/gen_specialized.py` `_by_dimension(examples)` took a
  read-only `dict[int, str]`, which is now `Mapping[int, str]`.
- **The exemptions doc:**
  - the floor paragraph is rewritten with the new count and split, and this task added to its
    records;
  - §5 loses `tests/test_odd.py`, whose `versor` / `conjugated` are annotated now and no longer
    reported;
  - §5 `test_graded`'s count is corrected to 2 LOCAL + 1 LOOP.

## How

The site list came from `tasks/adhoc/re-baseline-annotation-auditor-after-gl-move/discover.sh`,
with a snapshot in `data/rows-before.txt`. `declare.py` inserted the declarations from per-file JSON
specs, bottom-up by line number. Each spec entry carried the expected source line, so a stale line
number would have failed instead of inserting in the wrong place. All of these are one-shot and were
deleted at archive.

## Verification

- ruff was clean on every touched file.
- In the container against the existing image (the GL packages are absent on the host):
  - `ty check --no-respect-ignore-files src`, `ty check tests`, `ty check tools`: all clean;
  - the GL and Cayley tests and doctests passed (53).
- The batch's full container gate at the end covers the rest.
