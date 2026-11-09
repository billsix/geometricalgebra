# Decide: check in generated code, or build it / generate at runtime?

**Created:** 2026-06-04 · **Completed:** 2026-06-06
**Superseded:** "keep generated g*.py checked in" was reversed the next day; generated modules became gitignored build artifacts (see `tasks/archive/2026/06/07/build-time-codegen-dist.md` and `tasks/reference/design-decisions.md`).

The maintainer asked whether Python has a standard way to not commit the generated `g1`/`g2`/`g3.py`
and build them "through a standard means" instead (the Lisp macro / load-time instinct). The files
were committed at the time, and `tasks/archive/2026/06/06/regen-diff-ci-guard.md` assumed that; this
task recorded a deliberate decision.

## Options

1. **Check in the generated source.** The most idiomatic choice for pure-Python codegen: ruff, ty,
   the IDE and the debugger see real files; no build step; editable installs work; diffs are
   reviewable. Cost: regenerate and keep in sync (mitigated by the regen-diff guard).
2. **Generate at runtime, on import** (closest to a Lisp macro): `g2.py` builds `G2` dynamically
   (`dataclasses.make_dataclass` / `type()` / `exec`). Nothing to keep in sync, but static tools go
   blind, tracebacks get worse, and the type checking that had caught real bugs here would be lost.
3. **Generate at build time** (setuptools `cmdclass` / a hatchling hook). The least common for pure
   Python; interacts badly with editable installs and IDEs (a manual dev regen step is still
   needed); runs only when building from source.

## Decision (2026-06-06): option 1, keep the files checked in

This is a teaching library, and a student who `pip install`s it must be able to read the
closed-form code in `site-packages`. Option 2 produces no readable source (neither the installed
file nor `inspect.getsource` shows the math), which ruled it out. Option 3 keeps pip-readability but
adds a per-checkout regen step (editable installs, IDE, `ty` and CI see nothing until generated) and
a build hook to maintain, buying nothing over option 1 for a solo-maintained repo. Committed files
also keep the code readable when browsing the repo and keep static analysis working.

Consequence: `tasks/archive/2026/06/06/regen-diff-ci-guard.md` was unblocked as the safety net
against committed files drifting from the generator.
