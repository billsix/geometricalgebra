# Options and mode parameters are enums, not strings

**Created:** 2026-11-10 (William Emerison Six <billsix@gmail.com>) · **Done:** 2026-11-10

Every parameter that picked an option by string now takes an `enum.Enum`, and the code dispatches
on it with `match` (`case _` raises `TypeError` naming the expected enum, so a caller still passing
the old string gets a clear message).

| Was | Now | Defined in |
|---|---|---|
| `Frame.to_invertible_function(inverse_method="reciprocal" \| "peel")` | `InverseMethod.RECIPROCAL` / `.PEEL` | `src/gacalc/frame.py` |
| `to_matrix(..., backend="numpy" \| "sympy")`, `ComposableFunction.to_matrix(...)` | `MatrixBackend.NUMPY` / `.SYMPY` | `src/gacalc/functions.py` (re-exported by `transforms`) |
| generator `TypeSpec.kind: str` (`"scalar"`/`"graded"`/`"full"`) | `TypeKind` | `tools/gen_specialized.py` |
| generator docstring role `str` (`"vector"`, …), `custom_method_doc(role, …)` | `DocRole` | `tools/gen_specialized.py` |

- **Why `MatrixBackend` lives in `functions.py`:** `ComposableFunction.to_matrix` names it in its
  signature, and `functions` is the import-free leaf, so it cannot import it from `transforms`.
- **`DocRole` keeps the `CUSTOM_METHOD_DOCS` keys as strings** (`"vector|reverse"`): the table is data,
  and its key is built from `role.value`, so the ~100 entries did not change.
- **Not converted, with the reason:** the `match kind` over a sympy symbol name prefix (`"a"`/`"b"`)
  in `tools/gen_specialized.py` parses data, not an option; matplotlib values (`"top"`, colours) are
  matplotlib's own API; `str` parameters that are labels, titles, file names or LaTeX are not options.
  `nbplotutils.py` had no option parameters.
- **Discovery:** `tasks/adhoc/options-as-enums/discover.sh` (53 hits, logged in `data/hits.txt`,
  each read). The call sites, book notebooks (`book/docs/notebooks/frame-qr-2d.py`, `frame-qr-3d.py`),
  tests and docs (`CLAUDE.md`, three `tasks/reference/` docs) were rewritten by
  `tasks/adhoc/options-as-enums/codemod.py` (idempotent: the second run changed nothing). The enum
  definitions, signatures and `match` statements were edited by hand. All three one-shot files were
  removed in the archive commit.
- **Decisions** (William Emerison Six <billsix@gmail.com>, 2026-11-10): plain `enum.Enum`, strings no
  longer accepted, a breaking change with a minor bump; scope includes `tools/` and `nbplotutils.py`.
  The version bump `0.0.20` → `0.1.0` was done once, at the end of the batch, so every change of the
  batch lands in the same release section.
- **Tests:** `test_string_inverse_method_raises` (replaces the unknown-name test) and
  `test_to_matrix_string_backend_raises`; `test_frame_class.py` parametrizes over `list(InverseMethod)`.
- **Gate (host):** ruff + ty clean over `src tests tools book/docs/notebooks`; `pytest -m "not slow"`
  795 passed; the generator stayed deterministic (two runs byte-identical).
- The cross-project rule went into the shared Python standard: github.com/billsix/runClaudeInContainer
  `tasks/python-options-as-enums-standard.md` and its runCrushInContainer mirror.
