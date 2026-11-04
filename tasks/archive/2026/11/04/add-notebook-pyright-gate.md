# Add a container `pyright` gate for the notebooks

**Done 2026-11-04** (branch `add-notebook-pyright-gate`; agent under William Emerison Six's batch
authorization). The notebooks are pyright-clean and a `make check-notebooks` gate now guards them.

## What was done

- **`pyrightconfig.json`** (repo root): `include: ["notebooks"]` and `reportUnusedExpression:
  "warning"` (the display cells emit intentional unused-expression warnings; this keeps them
  non-failing — it's also pyright's default, kept explicit as documentation). **No `pythonVersion`
  key** — see the trap below.
- **`make check-notebooks`** (`.PHONY`, `##`-documented, `: image`): runs `pyright notebooks/` in the
  container, mirroring `make test`'s minimal `podman run` (NOT `shell-exec`); regenerates the
  gitignored `g*.py` first so the notebooks' `gacalc.g2/g3` imports resolve. Kept **separate** from
  `make test` so a pyright-version bump can't redden the test gate.
- `CLAUDE.md` › Dev workflow: added the `make check-notebooks` bullet.

## The trap that cost the most time (so it isn't repeated)

**Do NOT hardcode `pythonVersion` in `pyrightconfig.json`.** The first version of the config set
`"pythonVersion": "3.13"`, but the image's Python is **3.15.0**. That mismatch sent pyright into
spurious circular-inference and reported two false `reportGeneralTypeIssues` errors
(`displayrotations.py:170` `R3`, `displayg2.py:521` `lagrange_residual`, both "could not be
determined because it refers to itself"). Isolated by diff: config with `pythonVersion` → 2 errors;
no config → 0; config without `pythonVersion` → 0. Letting pyright auto-detect the version from the
venv is correct and won't rot as the image's Python moves. The notebooks themselves are clean and
were **not** edited.

A second red herring: a **stale cached image** (7-day-old `gacalc:latest`) shipped a non-functional
`pyright` (pip wrapper, no node, `nodeenv` couldn't bootstrap). A fresh `make image` build has a
working pyright — **no Dockerfile/node change is needed**. (The nested `: image` gotcha means `make
check-notebooks` via `make` rebuilds the whole image when run in a sandbox; test it by running the
inner `podman run` line directly, as the verification below did.)

## Decisions

- **Scope: notebooks only** (the gap `ty` doesn't cover). Not adding pyright over `src`/`tests` — `ty`
  covers those; a second checker there is maintenance/divergence for no gain.
- **Separate target, not folded into `make test`** — a pyright-version bump stays isolated.
- **pyright left unpinned** (matches the Dockerfile's existing unpinned `pyright`). A future pyright
  bump can change diagnostics on unchanged code; if that reddens the gate, pin pyright then rather
  than pre-emptively. Noted so the choice is deliberate.

## Verification (direct `podman run` against the fresh `gacalc:latest`, 2026-11-04)

- **Green:** `pyright notebooks/` with the fixed config → `0 errors, 42 warnings`, exit 0. Reproduced
  consistently.
- **Red:** appended a deliberately-wrong annotation (`_pyright_redcase: int = "not an int"`) to a
  notebook → pyright reported the type error and exited 1; the notebook was restored (tree clean).

## Cross-links

- `tasks/archive/2026/08/27/fix-notebook-pyright-type-errors.md` — cleaned the notebooks to 0 errors
  (the prerequisite).
- `tasks/archive/2026/08/27/parameterize-composable-function-annotations.md` — the regression class
  this gate now catches automatically.
