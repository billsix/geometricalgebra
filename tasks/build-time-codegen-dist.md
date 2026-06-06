# Reconsider checking in generated code: build-time generation + `make dist`

**Status:** proposed — investigation/design; produce proposals, then a decision (do NOT implement yet)
**Started:** 2026-06-06

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

## Notes

- Parallel/independent investigation — **not** in the current execution order
  (`#9 + #3 → #5 / #7`). Pick up when the author wants; produce proposals first, then decide.
- Cross-refs: `tasks/archive/2026/06/06/codegen-checkin-strategy.md` (the #4 decision this revisits)
  and `tasks/archive/2026/06/06/regen-diff-ci-guard.md` (#8, which this would moot/repurpose).
