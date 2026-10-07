# Import epix-mirror at container build time for plot generation

**Status:** in-progress (go-ahead 2026-10-06: "1) yes 2) agreed", and "use git to fetch it"); the image
integration is built and verified (table below); the first book figure is the remaining step. **Fully unblocked 2026-10-06:** the GitHub URL
(`https://github.com/billsix/epix-mirror`, 2026-10-04) *and* the pin — the maintainer wants the image to
pull **commit `ebf3ca607ae6c1d4fa307e8b0359960d875d219c`** (GitHub `master` as of 2026-10-06, the merge of
epix-mirror's `containerFileRework` branch).
**Priority:** 7
**Difficulty:** 5 (was 6 — the epix side now ships host-runnable install scripts and a Meson build, so
the "learn the build" step is done; see Notes)
**Created:** 2026-06-13
**Updated:** 2026-10-06 (William Emerison Six <billsix@gmail.com>, via agent) — pin recorded; plan made
concrete against the pushed epix-mirror layout. Earlier: 2026-10-04 URL recorded, local clone path corrected.

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
      (2026-10-04). **Pin decided 2026-10-06:** commit `ebf3ca607ae6c1d4fa307e8b0359960d875d219c`.
- [x] **Learn the build** (2026-10-06, from the pushed tree — see Notes): Meson, `meson setup build
      --prefix=/usr/local && meson install -C build`; installs `epix`/`elaps`/`flix`/`laps` + `libepix.a` +
      headers + man pages + samples. Runtime: `g++` (the `epix` driver compiles each `.xp`), `bash`,
      `latex`, `ps2epsi`; `gs` for eps→png, ImageMagick for animations. The tree's own
      `entrypoint/01-install-base.sh` / `02-install-render.sh` are host-runnable dnf group scripts.
- [x] **Add it to gacalc's `Dockerfile`** (2026-10-06) behind `USE_EPIX` (`?= $(if $(filter
      1,$(MINIMAL_IMAGE)),0,1)` in the Makefile, `ARG USE_EPIX=0` + `ARG EPIX_COMMIT=ebf3ca6…` in the
      Dockerfile). **Fetched with git** (the maintainer's choice over a tarball): `entrypoint/install-epix.sh`
      does a shallow `git fetch --depth 1 origin $EPIX_COMMIT` + detached checkout, `meson setup`/`meson
      install` into `/usr/local`, removes the build dir and `.git`, keeps the source at `/opt/epix-src`.
      `entrypoint/06-install-epix.sh` installs git, meson/ninja/g++/binutils, ghostscript, ImageMagick and
      the TeX set epix's own `02-install-render.sh` names (overlap with `03-install-notebook-tex.sh` is a
      dnf no-op; listed in full so an epix-only image has `latex`). Placed before `COPY src` for cache
      ordering. Everything lands in committed layers at build time; the pin makes the layer
      reproducible; the installed tools run offline.
- [x] **Replace-vs-coexist decided (2026-10-06, maintainer): coexist.** `nbplotutils.py` (matplotlib)
      stays for the interactive notebooks; ePiX is the book's LaTeX-native figure source.
- [ ] **Wire the first book figure.** `.xp` sources under `book/figures/epix/`, rendered at `make docs`
      to PDF (`elaps --pdf`, for the LuaLaTeX build) and to SVG/PNG for HTML (`gs` from the eps); pick
      one existing book figure to port as the proof. Exposing the Python `epix` package in the gacalc
      venv (nanobind extension, lazy-PNG `Figure`) is a possible second step after that.
- [ ] **Keep both doc paths in mind.** Usable from a future Sphinx build *and* a
      LaTeX port (where epix's native LaTeX/eepic output is a natural fit) — don't
      hard-wire it to one.
- [x] **Document** the dependency: `CLAUDE.md` ("ePiX in the image" bullet + the lean-image flag list).
- [ ] **Document** how to regenerate the book figures once the first one exists.

## Verification (2026-10-06, nested in the runClaudeInContainer sandbox)

| Check | Result |
| --- | --- |
| `make image USE_LEAN=0 USE_EMACS=0` (ePiX on; Lean/Emacs trimmed — the diff touches neither) | built; the ePiX layer logged `epix-mirror at ebf3ca607ae6c1d4fa307e8b0359960d875d219c` and Meson installed 194 files under `/usr/local` |
| tools present | `epix`/`elaps`/`flix`/`laps` on PATH, `libepix.a` + `epix.h` installed, source at `/opt/epix-src` with `.git` removed |
| render `samples/hello.xp` in the image | `epix` → eepic; `elaps --pdf` → `hello.pdf` (4.6 KB) through latex → dvips → ps2epsi → epstopdf |
| gacalc gate (`make test`'s run line) | **696 passed** |
| `make image MINIMAL_IMAGE=1` (flag-off permutation) | built, 2.47 GB; `epix`, `git` and `meson` all absent — the `USE_EPIX` gate holds. The ePiX-enabled image (Lean/Emacs still off) is 3.96 GB |

## Notes / decisions

- **What the 2026-10-06 push unlocked (epix-mirror `ebf3ca6`).** (a) The build is documented and
  scripted: `Dockerfile` + `entrypoint/01-install-base.sh`/`02-install-render.sh` + `meson.build` are the
  whole recipe, and the dnf lists are host-runnable, so gacalc's Dockerfile can reuse them rather than
  guess. (b) The Python front-end (`python/epix`, nanobind) is installable editable with `uv pip` and its
  `Figure` rasterizes **lazily** — building a figure needs only `libepix`; PNG needs TeX + `gs`. That
  makes an `import epix` from a gacalc notebook viable without dragging the render stack into every
  code path. (c) `MINIMAL_IMAGE` flags exist on the epix side, so what gacalc installs can mirror
  exactly the groups it wants (library + drivers; rendering stack only where the book/notebooks render).
  (d) The library builds warning-free at `-Wall -Wextra -Wpedantic` and a real `Complex::operator!=`
  recursion bug is fixed — the pinned commit is a better base than the June tree.
- **Recommendation for open question 3 (coexist, not replace):** keep `nbplotutils.py` (matplotlib) for
  the interactive notebooks; add epix as the **book's** figure source where LaTeX-native output pays —
  `.xp` sources under `book/figures/epix/`, rendered at `make docs` to PDF (`elaps --pdf`, for the
  LuaLaTeX build) and to SVG/PNG for HTML (`gs` from the eps). Whether to also expose the Python
  `epix` package in the gacalc venv can be a second step once a first figure is in the book.

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
2. ~~Pin to a commit/tag, or track a branch?~~ **Answered 2026-10-06:** pin to commit
   `ebf3ca607ae6c1d4fa307e8b0359960d875d219c` (William Emerison Six <billsix@gmail.com>).
3. ~~epix output target / coexistence with `nbplotutils.py`?~~ **Answered 2026-10-06 (William Emerison
   Six <billsix@gmail.com>): coexist** — matplotlib for the notebooks, ePiX for the book's LaTeX-native
   figures (PDF for LuaLaTeX, SVG/PNG for HTML).
