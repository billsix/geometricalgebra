# Import epix-mirror at container build time for plot generation

**Status:** proposed — needs go-ahead; not started. The former blocker (the GitHub URL) was cleared
2026-10-04: **`https://github.com/billsix/epix-mirror`** (stated by the maintainer; the local clone
at `/mnt/sda1/epix-mirror` has only a Pi `origin` remote, no `github` remote).
**Priority:** 7
**Difficulty:** 6
**Created:** 2026-06-13
**Updated:** 2026-10-04 (William Emerison Six <billsix@gmail.com>) — URL recorded, unblocked; local
clone path corrected.

## Goal

At **container build time**, pull in the maintainer's **epix-mirror** code from GitHub and
build/install it into the gacalc image, so it's available as a plot-generation
tool. The plots are for the project's visual material — the **notebooks** and any
**book** — and the integration should work whether docs are built with **Sphinx**
or via a **LaTeX port** (gacalc's Sphinx book is described in
`tasks/reference/book-and-docs-pipeline.md`).

(epix-mirror is the maintainer's mirror of ePiX, a C++ library that produces precise
mathematical figures with LaTeX-quality output. A copy is also mounted locally at
`/mnt/sda1/epix-mirror` (a sandbox path; it now carries its own `Dockerfile`, `Makefile`,
and `CLAUDE.md`), usable to learn the build before the GitHub URL is given.)

## Plan

- [x] **Get the GitHub URL from the maintainer** — `https://github.com/billsix/epix-mirror`
      (2026-10-04). Decide
      whether to pin to a commit/tag for reproducible image builds.
- [ ] **Learn the build.** Inspect `/mnt/sda1/epix-mirror` (and the upstream repo
      once the URL lands): build system, dependencies (a TeX toolchain + a C++
      compiler at minimum), and what it installs (the `epix` driver/scripts and any
      libraries).
- [ ] **Add it to gacalc's `Dockerfile`.** `git clone <url>` (pinned) at build
      time, build, and install into the image, in the family-template style
      alongside the existing installs. Account for its TeX dependencies.
- [ ] **Wire it into the plot flow.** Work out how epix output fits with gacalc's
      existing plotting: `src/gacalc/nbplotutils.py` and the `notebooks/`
      (`displayg2.py`, `displayg3.py`, `displaymv.py`, `displaygraded.py`,
      `displayrotations.py`), plus the `jupyter.sh` / `percentToIpynb.sh` workflow.
      Decide replace-vs-coexist with the current plotting and where generated
      figures land.
- [ ] **Keep both doc paths in mind.** Usable from a future Sphinx build *and* a
      LaTeX port (where epix's native LaTeX/eepic output is a natural fit) — don't
      hard-wire it to one.
- [ ] **Document.** Update this task as it progresses; once landed, note the new
      dependency in `CLAUDE.md` / `README` and how to regenerate plots.

## Notes / decisions

- Moved here from modelviewprojection per the maintainer's decision (this is gacalc's epix
  import; mvp's plotting is a separate concern and got no epix task).
- A local copy of epix-mirror is at `/mnt/sda1/epix-mirror` — usable to study the
  build before the canonical GitHub URL arrives.
- This is a **permanent** build-file change (a real plot dependency the image
  should carry), so per the cross-project build-file conventions it needs the maintainer's
  go-ahead before it lands in the committed `Dockerfile` (this task records intent).
- gacalc has a Sphinx book ("Geometry 2") built with `make docs`; its pipeline is
  documented in `tasks/reference/book-and-docs-pipeline.md`.

## Open questions

1. ~~What's the epix-mirror GitHub URL?~~ **Answered 2026-10-04:** `https://github.com/billsix/epix-mirror`.
2. Pin to a commit/tag, or track a branch?
3. epix output target: pre-rendered PNG/SVG for notebooks, native LaTeX/eepic for a
   book/LaTeX port, or both? How should it coexist with `nbplotutils.py`?
