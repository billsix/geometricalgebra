# Decide: check in generated code, or build it / generate at runtime?

Status: **decided 2026-06-06 — Option 1 (keep checked-in)** · raised 2026-06-04
**Completed:** 2026-06-06

## Background

You asked whether Python has a standard way to **not check the generated `g1`/`g2`/`g3.py` into the
repo** and instead build them "through a standard means" (the Lisp macro / load-time instinct). We
discussed it but never decided — we currently **check them in** (and the proposed
`tasks/regen-diff-ci-guard.md` assumes that). This task records the decision so it's deliberate.

## The three options (from that discussion)

1. **Check in the generated source (current).** Most idiomatic for pure-Python codegen. Pros: ruff /
   ty / IDE / debugger all see real files; no build step; editable installs work; reviewable diffs.
   Cons: must regenerate + keep in sync (mitigated by the regen-diff CI guard).
2. **Generate at runtime, on import** (closest to a Lisp macro / load-time eval). `g2.py` becomes a
   few lines that build `G2` dynamically (`dataclasses.make_dataclass` / `type()` / `exec`). Pros:
   nothing to check in or keep in sync. Cons: static tools (ruff/ty/IDE) go blind; worse tracebacks;
   we'd lose the type checking that caught real bugs in this project.
3. **Generate at build time** (setuptools `cmdclass` / hatchling build hook). Source is produced when
   the wheel is built. Cons: least common for pure Python; bad interaction with editable installs and
   IDEs (you usually still need a manual regen step for dev); only runs when building from source, not
   when installing a prebuilt wheel.

## Recommendation (mine, for the record)

Keep **option 1** (checked-in) + add the regen-diff guard. It's why ruff/ty could vet the generated
files. Option 2 is the "Lispiest" and a legitimate Python idiom if you'd rather not check code in —
the tradeoff is losing static analysis on the specialized classes.

## Decision (2026-06-06)

**Option 1 — keep the generated `g1/g2/g3.py` checked into the repo.**

Rationale: this is a *pedagogical* library, and a `pip install`ed student must be able to read the
specialized closed-form code in `site-packages`. Option 2 (runtime / on-import generation) produces
**no readable source** — the methods are built dynamically at import, so neither the installed file
nor `inspect.getsource` shows the math — and was ruled out on that basis. Option 3 (build-time)
preserves pip-readability but buys nothing over option 1 on readability while adding a per-checkout
regen step (editable installs / IDE / `ty` / CI don't see the files until generated) and a build hook
to maintain — not worth it for a solo-maintained repo. Keeping the files in git also preserves
repo-browse readability and keeps `ruff` / `ty` / IDE / debugger working on the specialized classes
(the reason static analysis caught real bugs here).

**Consequence:** `tasks/regen-diff-ci-guard.md` (#8) is unblocked — since the committed generated
files must not drift from the generator, the regen-diff guard is the right next safety net.
