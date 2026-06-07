# Reconsider checking in generated code: build-time generation + `make dist`

**Status:** complete — implemented 2026-06-07 (Option 3, build-time generation; files removed from git)
**Started:** 2026-06-06
**Completed:** 2026-06-07

## Goal

Investigate moving the generated `g1/g2/g3.py` + `scalar.py` **out of the repo** (gitignored),
producing them instead at build/dev time, automake-style:

- **`make dist`** builds the distributable PyPI package (sdist + wheel) with the generated modules
  baked in — the way `automake`'s `make dist` produced a release tarball.
- **`make shell`** (container dev) ensures the generated code exists in the working tree before
  dropping into the shell, so `ty`/`ruff`/IDE/debugger/tests all see real files.

Output of this task is a set of **concrete proposals with tradeoffs**, for the author to choose from.
This **revisits** `tasks/archive/2026/06/06/codegen-checkin-strategy.md` (#4, decided "keep
checked-in") under new context.

## Why now — what changed since the #4 decision

#4 chose Option 1 (check in) largely because there was no build step and the dev tooling needed real
files on disk. Three things have changed:

1. **The generator is now invoked from `make`** (`make check-generated`, this session's #8) — the
   infrastructure to run it as part of a build already exists.
2. **The author develops via `make shell` in a container** (Makefile-driven), so a "generate first"
   step can be made invisible — the container entrypoint can regenerate before the shell starts.
3. **The author wants an `automake`-style `make dist`** to build the package for PyPI.

Crucially, the **hard constraint from #4 still holds and is still satisfied**: a `pip install`ed
student must be able to **read the specialized closed-form source**. Build-time generation (#4's
Option 3) bakes the generated `.py` into the wheel/sdist, so the installed package is fully readable —
which is exactly why Option 3 stayed on the table while Option 2 (runtime / on-import generation, which
produces no readable source) was rejected. **This task is Option 3, not Option 2.**

## The shift: Option 3 (build-time), with the container/Makefile neutralizing its old downsides

#4's Option-3 cons were "editable-install / IDE need a manual regen step; fresh clone/CI blind until
generated." The container workflow defuses these: `make shell` regenerates into the mounted tree, so
in-container the files always exist and every static tool works. The remaining work is doing it
cleanly and documenting the non-container path.

## What to investigate and propose

1. **Build hook (setuptools).** Repo uses setuptools + `src/` layout. Investigate a `cmdclass` /
   build hook (override `build_py`, or a thin PEP 517 backend) that runs `tools/gen_specialized.py`
   and includes the output in **both** the wheel and the sdist. Propose the concrete mechanism and
   confirm the generated files actually land in each artifact (pip-readable).
2. **`make dist` target.** Propose: regenerate → `python -m build` → sdist+wheel in `dist/`. Decide
   whether `make dist` relies on the build hook or regenerates explicitly first (belt-and-suspenders).
3. **`make shell` / container integration.** Propose how the container guarantees `g*.py` exist for
   dev — entrypoint regen, or a `make generate` prerequisite. Keep it idempotent and fast-on-noop
   (note: full regen is ~30s, 𝒢₃ dominates — consider only regenerating if missing/stale).
4. **`.gitignore` + index removal.** Add `src/geometricalgebra/{g1,g2,g3,scalar}.py` to `.gitignore`
   and `git rm --cached` them. Verify nothing imports them at package-import time in a way that breaks
   before first generation (e.g. `nbplotutils`/notebooks import from `gn`, not `g*`, but check).
5. **Fallout — what changes:**
   - **#8 `make check-generated`** becomes moot (nothing committed to diff against). Decide: delete it,
     or repurpose it as a determinism/clean-run check (regenerate twice, assert byte-identical).
   - **Fresh clone / `pip install -e .` (non-container):** needs a generate step first. Propose a
     `make generate` target and document it prominently.
   - **A future CI** must regenerate before `pytest`/`ty`/`ruff` (the files won't be in the tree).
   - **Docs:** CLAUDE.md (Module layout calls `g*.py` "generated … Do not edit"; Code generation; Dev
     workflow) and README ("Generating", "Adding a new algebra") need updating to the new model.
6. **Honest comparison vs. staying checked-in.** Weigh both:
   - *Build-time wins:* no ~thousands of lines of generated code in git history; cleaner diffs/reviews;
     no regen-drift class of bug (so #8 is unneeded).
   - *Build-time costs:* a build hook to maintain; a hard "generate before anything" dependency for
     any non-container dev/test/IDE use; slightly more complex packaging; install-from-sdist must
     either ship the files or run the generator (needs sympy at build time).
   Recommend a direction.

## Constraints to preserve (non-negotiable)

- **pip-installed students can read the generated closed-form source.** (Rules out Option 2 /
  runtime-on-import generation — keep it ruled out.)
- **`ty`/`ruff`/IDE/debugger keep working in the dev environment** — satisfied as long as the files
  exist on disk in-container, which `make shell` must guarantee.

## Open questions for the author

- Bake the generated files into the **sdist** too (recommended), so a `pip install` from a source
  tarball doesn't need the end user to have `sympy` and run a multi-minute generation at install time?
  (Baking into both wheel and sdist keeps installs fast *and* readable.)
- Separate `make generate` convenience target, distinct from `make dist` / `make shell`?
- `make check-generated` (#8): delete, or repurpose as a determinism check?
- Any appetite for keeping the files checked in *and* adding `make dist` (i.e. reject this and just
  add the dist target)? — the minimal alternative if the "generate-before-dev" dependency feels worse
  than generated code in git.

## Concrete Make-target design (added 2026-06-07, author-requested)

This section answers the two concrete asks: (1) `make shell` should **generate the code before
dropping the user into the shell**, and (2) there should be a target that produces a **PyPI-uploadable
unit** with the generated code baked in (for users who aren't on Linux / don't use the container).
Proposal only — nothing changed yet.

### What the study established (facts the design rests on)

- **The generator bootstraps from a fresh tree.** `tools/gen_specialized.py` imports only
  `geometricalgebra.base` + `geometricalgebra.gn` (both hand-written, in git) via a `sys.path` insert;
  it writes `scalar.py` first, then `g1/g2/g3.py` into `src/geometricalgebra/`. **No `__init__.py`
  exists, and nothing imports the generated modules at package-import time** (`base.py`/`gn.py` don't
  import them). So a tree with the generated files *deleted* can still run the generator — there is **no
  chicken-and-egg**. (Tests, `tools/bench.py`, and `displayg2/g3/graded` notebooks *do* import the
  generated modules, so they need generation to have run first — but the generator itself does not.)
- **Build-time dependency is just `sympy`.** The generator imports `sympy`; `ruff` is **best-effort**
  (it warns and emits unformatted files if ruff is missing — not a hard dep). `numpy` is imported only
  by the *generated* modules at their runtime, not during generation.
- **Idempotent + deterministic.** `make check-generated` already proves a regen is byte-identical
  (verified clean this session). Cost: sub-second for 𝒢₁/𝒢₂, ~tens of seconds for 𝒢₃ (~30s total).
- **The dev path is the container.** `make shell` → `podman run --entrypoint /bin/bash … /shell.sh`;
  `shell.sh` does `cd /geometricalgebra && uv pip install --system --no-deps --no-index
  --no-build-isolation -e . && exec bash`. The repo is bind-mounted, so anything written into
  `src/geometricalgebra/` from inside the container lands in the host working tree (and stays gitignored).

### Proposed targets

**1. `make generate` — the single source of truth.**
```make
.PHONY: generate
generate: ## Generate scalar.py / g1.py / g2.py / g3.py from tools/gen_specialized.py
	python tools/gen_specialized.py
```
Everything else composes this. Idempotent; safe to call repeatedly. (Runs wherever `sympy` is present.)

**2. `make shell` — generate inside the container, before the prompt.**
The generation must happen *inside* the container (the host may lack `sympy`/the right Python), and the
files must exist before the editable install and before the user starts typing. Put it in `shell.sh`,
which already runs inside the container with all deps:
```sh
cd /geometricalgebra/
python tools/gen_specialized.py          # <-- new: regenerate into the (gitignored) mounted tree
uv pip install --system --no-deps --no-index --no-build-isolation -e .
exec bash
```
Rationale for `shell.sh` over a setuptools build hook on the editable install: the editable install uses
`--no-build-isolation --no-deps --no-index`, so relying on a custom `build_py` to fire during `-e .` is
fragile; an explicit line is obvious and robust. ~30s on a cold shell; if that annoys, make it
**generate-if-missing** (`[ -f src/geometricalgebra/g3.py ] || python tools/gen_specialized.py`) — but
note that won't pick up generator edits, so prefer unconditional during active development.
*(The `make shell` `podman run` also needs `--cgroups=disabled` to run nested in the sandbox — separate
from this task; proposed but not yet applied to the Makefile.)*

**3. `make dist` — the PyPI unit.**
```make
.PHONY: dist
dist: generate          ## Build sdist + wheel (generated modules baked in) into dist/
	python -m build
```
Depending on `generate` means the files exist in `src/` before `python -m build` runs, so setuptools'
`packages.find` sweeps them into **both** the wheel and the sdist. Belt-and-suspenders with target 4.

**4. setuptools build hook (`setup.py`) — make the artifacts self-sufficient.**
Add a `build_py` subclass that **generates if the files are missing**, so:
- *Building from the repo* (`make dist`, or `pip wheel .`) → generates (dev has `sympy`).
- *Installing from a shipped sdist/wheel* → files already present → hook no-ops → **end user needs no
  `sympy` and no generation step.** This is what makes the non-Linux / non-container `pip install` "just
  work."
```python
from setuptools import setup
from setuptools.command.build_py import build_py
import subprocess, sys, pathlib

GEN = ["scalar.py", "g1.py", "g2.py", "g3.py"]
PKG = pathlib.Path("src/geometricalgebra")

class build_py_with_codegen(build_py):
    def run(self):
        if not all((PKG / f).exists() for f in GEN):
            subprocess.run([sys.executable, "tools/gen_specialized.py"], check=True)
        super().run()

if __name__ == "__main__":
    setup(cmdclass={"build_py": build_py_with_codegen})
```
And add `sympy` to the **build** requires so build-from-repo has it:
```toml
[build-system]
requires = ["setuptools", "wheel", "sympy"]
```
(Open choice: "generate if missing" vs "always generate". *If-missing* keeps install-from-sdist
`sympy`-free and fast; *always* guarantees freshness but forces `sympy` at every build. Recommend
if-missing, paired with `make generate`/`make dist` always regenerating explicitly for the dev/release
path — so releases are always fresh, installs are always cheap.)

**5. `.gitignore` + untrack.**
```
src/geometricalgebra/scalar.py
src/geometricalgebra/g1.py
src/geometricalgebra/g2.py
src/geometricalgebra/g3.py
```
then `git rm --cached` the four files (one-time). Working tree keeps them; git stops tracking.

**6. `make check-generated` (#8) — repurpose or drop.**
Once the files aren't committed there's nothing to `git diff` against, so its drift-guard purpose is
moot. Repurpose it as a **determinism check** (generate twice, assert byte-identical) to catch a
non-deterministic generator, or delete it. (The sdist `MANIFEST`/`tox`-style "build is reproducible"
check is the spiritual successor.)

**7. `make upload` / `make release` — pushing to PyPI (kept *separate* from `dist`).**
`make dist` only *builds* `dist/*.tar.gz` + `dist/*.whl`; it must **not** upload — publishing is
irreversible and outward-facing, so it stays its own target you invoke deliberately:
```make
.PHONY: upload
upload: dist          ## Validate and upload dist/* to PyPI (irreversible)
	twine check dist/*
	twine upload dist/*
```
- `twine check` validates the artifact metadata (long-description rendering, etc.) before the
  irreversible push. Add `twine` to the dev/release tooling (it's not a runtime dep).
- **Version bump is mandatory each release.** PyPI **permanently rejects re-uploading a version that
  already exists** (even after a delete — the filename is burned). So cutting a release means bumping
  `version = "0.0.1"` in `pyproject.toml` *before* `make dist`. Forgetting this is the #1 release
  papercut, so guard it rather than rely on memory. Options:
  - **Manual + guard (simplest):** bump `pyproject.toml` by hand; have `upload` refuse if the version
    is already on PyPI. A lightweight check before `twine upload`:
    ```make
    VERSION := $(shell python -c "import tomllib;print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])")
    release: dist  ## Tag + upload the current pyproject version (fails if already released)
    	@git rev-parse "v$(VERSION)" >/dev/null 2>&1 && { echo "tag v$(VERSION) exists — bump version in pyproject.toml"; exit 1; } || true
    	twine check dist/*
    	twine upload dist/*
    	git tag "v$(VERSION)"
    	@echo "Released $(VERSION). Push the tag:  git push origin v$(VERSION)"
    ```
    (The `git tag` doubles as the "have I already shipped this?" record and a release marker. Tagging is
    a local op, so it's fine for the agent; the `git push` of the tag stays the author's call, per the
    repo's "I commit/push, you don't" convention.)
  - **Automated bump (optional):** a `make bump-patch` / `bump-minor` using `hatch version` or a
    `sed`/`tomlkit` one-liner, if hand-editing gets tedious. Probably overkill for a solo
    pre-1.0 project; note it and skip unless wanted.
- **Dry-run path:** `twine upload --repository testpypi dist/*` to rehearse against TestPyPI before the
  real index. Worth a `make upload-test` if the author wants to verify the end-to-end install once.

### What this buys / costs (recap for the decision)

- **Wins:** ~thousands of lines of generated code leave git history; diffs/reviews get clean; the
  regen-drift bug class disappears (so #8 is unneeded); `make dist` gives an automake-style release;
  `pip install` stays readable (Option 3, *not* runtime/on-import generation) and `sympy`-free for end
  users (files shipped in the sdist/wheel).
- **Costs:** a `build_py` hook to maintain; a hard "generate before tests/IDE/bench" step for any
  non-container dev (mitigated: `make generate`, and `make shell` does it automatically); `sympy` added
  to build requires; fresh clone / a future CI must `make generate` before `pytest`/`ty`/`ruff`.

### Suggested order if approved (do NOT start without go-ahead)

1. `.gitignore` + `git rm --cached` the four files.
2. Add `make generate`; wire it into `shell.sh` (target 2).
3. Add the `build_py` hook + `sympy` build-require (target 4); add `make dist` (target 3).
4. Verify: `make dist` → inspect the sdist (`tar tzf dist/*.tar.gz | grep -E 'g[123]\.py|scalar\.py'`)
   and wheel (`unzip -l dist/*.whl | grep …`) actually contain the generated `.py`. Then in a clean
   venv with **no `sympy`**, `pip install dist/*.whl` and `import geometricalgebra.g2` — proves the
   end-user path needs no generation.
5. Add `make upload` / `make release` (target 7) with the version-already-shipped guard; optionally
   rehearse once against TestPyPI (`make upload-test`). Leave the actual `twine upload` to a deliberate
   author-invoked run — not part of `dist`.
6. Repurpose/drop `make check-generated`; update CLAUDE.md ("Module layout", "Code generation", "Dev
   workflow") + README ("Generating", "Adding a new algebra") to the new model.

## Implemented (2026-06-07)

Decisions taken: **generate-if-missing** hook; **manual-bump + guard** `make release`. What changed:

- **`.gitignore` + untrack.** Added `/src/geometricalgebra/{scalar,g1,g2,g3}.py`; `git rm --cached`
  the four (still on disk, working tree unaffected).
- **`entrypoint/shell.sh`** — runs `python tools/gen_specialized.py` before the editable install, so
  `make shell` hands over a fully-generated tree.
- **`setup.py`** — `build_py` subclass that runs the generator **if the modules are missing**, so
  build-from-repo regenerates while build-from-sdist (ships them) is a no-op.
- **`pyproject.toml`** — `[build-system].requires = ["setuptools","wheel","numpy","sympy"]`,
  `readme = "README.md"`, and a `[project.optional-dependencies] dev = ["build","twine"]` extras group
  (install with `pip install -e ".[dev]"`) so the publish tooling ships with the repo.
- **`Makefile`** — `generate`, `dist` (`generate` → `python -m build`), `upload`, `release`
  (version-tag guard), and `check-generated` **repurposed** to a determinism check (regen twice,
  `cmp`).
- **Docs** — CLAUDE.md (Module layout / Code generation / Dev workflow) + README (Generating + new
  "Building & publishing" section) updated to the not-in-git model.

**Corrections found while implementing (the proposal above was slightly off):**
1. **Build-requires needs `numpy` *and* `sympy`, not just `sympy`.** The generator imports
   `geometricalgebra.base`, which imports `numpy` — so a build env with only `sympy` fails
   (`ModuleNotFoundError: numpy`). Fixed.
2. **"sympy-free end users" was imprecise.** `numpy`/`sympy` are genuine *runtime* deps (in
   `requirements.txt` → dynamic dependencies), so a `pip install` pulls them regardless. The accurate
   claim: installing the **wheel** runs **no build step and no generator** (the `.py` are baked in and
   readable); only an sdist build would touch the build-requires, and the pure-Python `py3-none-any`
   wheel matches every platform so the sdist path is rarely hit.
3. `tools/gen_specialized.py` is **not** shipped in the sdist (only the generated `.py` + `base`/`gn`
   are). Harmless because the sdist always ships the generated files (hook no-ops). If a from-sdist
   *regen* is ever wanted, add `tools/` via `MANIFEST.in`.

**Verified:** `make generate` ✅ · `make check-generated` (determinism) ✅ · `make dist` → sdist+wheel
both contain `scalar/g1/g2/g3.py` ✅ · `twine check` PASSED (clean, after adding `readme`) ✅ ·
wheel installed in a clean venv imports `geometricalgebra.g2` and builds a `G2` ✅ · the `build_py`
hook regenerates into the wheel when the tree has no generated files ✅ · full suite **161 passed**.

**Not done (deliberately):** the `make shell` `podman run` still lacks `--cgroups=disabled` (needed
only to run *nested* in the Claude sandbox; orthogonal to this task — propose separately before
editing). No `git commit` (author commits). Optional `make upload-test` (TestPyPI) / automated
version bump noted but not added.

## Notes

- Parallel/independent investigation — **not** in the current execution order
  (`#9 + #3 → #5 / #7`). Pick up when the author wants; produce proposals first, then decide.
- Cross-refs: `tasks/archive/2026/06/06/codegen-checkin-strategy.md` (the #4 decision this revisits)
  and `tasks/archive/2026/06/06/regen-diff-ci-guard.md` (#8, which this would moot/repurpose).
