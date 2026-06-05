# Decide: check in generated code, or build it / generate at runtime?

Status: **open decision** · raised 2026-06-04 · needs a decision

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

## Open question

Stay with checked-in (and just add the CI guard), or switch to runtime generation (option 2)? If
runtime, I can prototype `g2.py` as a dynamic builder so you can compare ergonomics/perf before
committing to it.
