.DEFAULT_GOAL := help

USE_SPYDER ?= 0
USE_EMACS ?= 0
# Build the Sphinx-book toolchain into the image by default (the Dockerfile
# defaults this to 0, so a bare `podman build` stays lean). Set BUILD_DOCS=0 for
# a quicker image if you don't need `make docs`.
BUILD_DOCS ?= 1


CONTAINER_CMD = podman
CONTAINER_NAME = gacalc

TMUX_FILE := $(HOME)/.tmux.conf
TMUX_REAL_PATH := $(shell readlink -f $(TMUX_FILE))
TMUX_MOUNT := $(shell if [ -f $(TMUX_REAL_PATH) ]; then echo "-v $(TMUX_REAL_PATH):/root/.tmux.conf:Z" ; fi)

GITCONFIG_FILE := $(HOME)/.gitconfig
GITCONFIG_REAL_PATH := $(shell readlink -f $(GITCONFIG_FILE))
GITCONFIG_MOUNT := $(shell if [ -f $(GITCONFIG_REAL_PATH) ]; then echo "-v $(GITCONFIG_REAL_PATH):/root/.gitconfig:Z" ; fi)

GNUPG_FILE := $(HOME)/.gnupg
GNUPG_REAL_PATH := $(shell readlink -f $(GNUPG_FILE))
GNUPG_MOUNT := $(shell if [ -d $(GNUPG_REAL_PATH) ]; then echo "-v $(GNUPG_REAL_PATH):/root/.gnupg:Z" ; fi)

# Mount ~/.pypirc (read-only) into the upload targets when it exists, so twine
# reads your saved PyPI/TestPyPI tokens and uploads without prompting.
PYPIRC_FILE := $(HOME)/.pypirc
PYPIRC_REAL_PATH := $(shell readlink -f $(PYPIRC_FILE))
PYPIRC_MOUNT := $(shell if [ -f $(PYPIRC_REAL_PATH) ]; then echo "-v $(PYPIRC_REAL_PATH):/root/.pypirc:ro,z" ; fi)



FILES_TO_MOUNT = -v $(shell pwd):/gacalc/:Z \
		-v ./entrypoint/entrypoint.sh:/entrypoint.sh:Z \
		-v ./entrypoint/jupyter.sh:/usr/local/bin/jupyter.sh:Z \
		-v ./entrypoint/percentToIpynb.sh:/usr/local/bin/percentToIpynb.sh:Z \
		-v ./entrypoint/spyder.sh:/usr/local/bin/spyder.sh:Z \
		-v ./entrypoint/format.sh:/format.sh:Z \
                $(TMUX_MOUNT) \
                $(GNUPG_MOUNT) \
                $(GITCONFIG_MOUNT)

EXPOSE_PORT = -p 8888:8888


X_FLAGS_FOR_CONTAINER = -e DISPLAY=$(DISPLAY) \
	-v /tmp/.X11-unix:/tmp/.X11-unix \
	--security-opt label=type:container_runtime_t

WAYLAND_FLAGS_FOR_CONTAINER = -e "WAYLAND_DISPLAY=${WAYLAND_DISPLAY}" \
                              -e "XDG_RUNTIME_DIR=${XDG_RUNTIME_DIR}" \
                              -v "${XDG_RUNTIME_DIR}:${XDG_RUNTIME_DIR}"


# USE_EMACS=1 bind-mounts the vendored host elpa tree into the container so an
# interactive `make shell USE_EMACS=1` can *use* the vendored packages (:U chowns
# it to the container user, :z relabels for SELinux). Default is off (no mount).
# To *refresh* the vendored packages, use `make update-emacs-packages` below.
ifeq ($(USE_EMACS), 1)
  ELPA_MOUNT= -v $(CURDIR)/entrypoint/dotfiles/.emacs.d/elpa:/root/.emacs.d/elpa:U,z
else
  ELPA_MOUNT=
endif

.PHONY: all
all: image shell ## Build the image and go into the shell

.PHONY: image
image: ## Build the OCI image
	$(CONTAINER_CMD) build -t $(CONTAINER_NAME) \
                         --build-arg USE_SPYDER=$(USE_SPYDER) \
                         --build-arg USE_EMACS=$(USE_EMACS) \
                         --build-arg BUILD_DOCS=$(BUILD_DOCS) \
                         $(ELPA_MOUNT) \
                         .


.PHONY: shell
shell:  ## Get Shell into a ephermeral container made from the image
	$(CONTAINER_CMD) run -it --rm \
		--entrypoint /bin/bash \
		$(FILES_TO_MOUNT) \
		-v ./entrypoint/shell.sh:/shell.sh:Z \
		$(X_FLAGS_FOR_CONTAINER) \
		$(WAYLAND_FLAGS_FOR_CONTAINER) \
		$(EXPOSE_PORT) \
                $(ELPA_MOUNT) \
		$(CONTAINER_NAME) \
		/shell.sh


.PHONY: jupyter
jupyter: image ## Launch JupyterLab (gacalc kernel) on http://127.0.0.1:8888/lab
	$(CONTAINER_CMD) run -it --rm \
		--entrypoint /bin/bash \
		$(FILES_TO_MOUNT) \
		$(X_FLAGS_FOR_CONTAINER) \
		$(WAYLAND_FLAGS_FOR_CONTAINER) \
		$(EXPOSE_PORT) \
                $(ELPA_MOUNT) \
		$(CONTAINER_NAME) \
		/usr/local/bin/jupyter.sh


# Run ruff + ty over the source INSIDE the container (the image's pinned toolchain).
# The g*.py are gitignored, so regenerate them first (so ty can resolve
# them), then run entrypoint/format.sh (ruff check --fix, ruff format, ty check).
.PHONY: format
format: image ## (container) regenerate, then ruff + ty over the source (entrypoint/format.sh)
	$(CONTAINER_CMD) run --rm \
		--entrypoint /bin/bash \
		$(FILES_TO_MOUNT) \
		$(CONTAINER_NAME) \
		-c 'set -e; source /venv/bin/activate; cd /gacalc; python tools/gen_specialized.py; bash /format.sh'


# Build the Sphinx book (HTML + PDF) INSIDE the container and copy it to the
# bind-mounted ./output/. Needs an image built with BUILD_DOCS=1 (the default).
# entrypoint/docs.sh generates the algebras + editable-installs so autodoc can
# import gacalc, then runs the book build.
.PHONY: docs
docs: image ## (container) build the book -> HTML + PDF into ./output/gacalc/
	$(CONTAINER_CMD) run --rm \
		--entrypoint /bin/bash \
		$(FILES_TO_MOUNT) \
		-v ./entrypoint/docs.sh:/docs.sh:Z \
		-v ./output/:/output/:Z \
		$(CONTAINER_NAME) \
		/docs.sh


.PHONY: clean
clean: ## Remove the built book (output/ contents and book/docs/_build/)
	rm -rf output/* book/docs/_build


# Refresh the vendored Emacs packages. Forces USE_EMACS=1 and rebuilds the image
# first (so it doesn't matter whether the last `make image` set USE_EMACS). Then,
# in the container, wipes the elpa tree and reinstalls from MELPA into the host's
# bind-mounted entrypoint/dotfiles/.emacs.d/elpa (the current
# install-melpa-packages.el is mounted read-only, so edits to it take effect
# without a rebuild). Finally strips compiled *.elc/*.eln (regenerated,
# machine-specific build artifacts) and force-stages the whole tree (git add -A
# -f overrides .gitignore's *.elc/*.eln/... patterns) so the vendored tree is
# ready to commit. Needs network access.
.PHONY: update-emacs-packages
update-emacs-packages: ## USE_EMACS=1: rebuild image, wipe+reinstall elpa, strip *.elc/*.eln, git add -f
	$(MAKE) image USE_EMACS=1
	$(CONTAINER_CMD) run --rm \
		-v $(CURDIR)/entrypoint/dotfiles/.emacs.d/elpa:/root/.emacs.d/elpa:U,z \
		-v $(CURDIR)/entrypoint/dotfiles/.emacs.d/install-melpa-packages.el:/root/.emacs.d/install-melpa-packages.el:ro,z \
		--entrypoint /bin/bash \
		$(CONTAINER_NAME) \
		-c 'set -e; find /root/.emacs.d/elpa -mindepth 1 -delete; \
		    emacs --batch --load /root/.emacs.d/install-melpa-packages.el'
	cd $(CURDIR)/entrypoint/dotfiles/.emacs.d/elpa && \
		find . \( -iname '*.elc' -o -iname '*.eln' \) -delete && \
		git add -A -f .
	@echo "Done: reinstalled packages, stripped *.elc/*.eln, staged elpa -- review and commit."



GENERATED = src/gacalc/g1.py \
            src/gacalc/g2.py \
            src/gacalc/g3.py

# g4/g5 are expensive (g4 ~5 min, g5 ~87 min) so they are release-only: dev
# generates only g1--g3, while `dist`/`release` and the opt-in targets below set
# GACALC_DIMS to the full set.  See tasks/reference/generated-algebra-generation-cost.md.
ALL_DIMS := 1,2,3,4,5

.PHONY: generate
generate: ## Generate the specialized algebras (g1/g2/g3.py -- the dev default) -- needs sympy
	python tools/gen_specialized.py

.PHONY: generate-all
generate-all: ## Generate ALL algebras incl. g4/g5 (SLOW: g5 ~87 min) -- release/CI
	GACALC_DIMS=$(ALL_DIMS) python tools/gen_specialized.py

.PHONY: test-all-dims
test-all-dims: ## (container) full-dim gate: generate g1..g5 then run the suite (SLOW ~1.5h)
	$(CONTAINER_CMD) run --rm \
		-v $(CURDIR):/gacalc:Z \
		--entrypoint /bin/bash \
		$(CONTAINER_NAME) \
		-c 'set -e; source /venv/bin/activate; cd /gacalc; GACALC_DIMS=$(ALL_DIMS) python tools/gen_specialized.py; python -m pytest'

.PHONY: check-regions
check-regions: ## Verify doc-region markers are unique/prefix-free/balanced (regen first)
	python tools/gen_specialized.py
	python tools/check_doc_regions.py

.PHONY: check-generated
check-generated: ## Verify tools/gen_specialized.py is deterministic (regen twice, compare)
	python tools/gen_specialized.py
	@cp $(GENERATED) /tmp/
	python tools/gen_specialized.py
	@for f in $(GENERATED); do \
		cmp -s "$$f" "/tmp/$$(basename $$f)" || { \
			echo ""; \
			echo "ERROR: tools/gen_specialized.py is non-deterministic ($$f differs between runs)."; \
			exit 1; \
		}; \
	done
	@rm -f $(addprefix /tmp/,$(notdir $(GENERATED)))
	@echo "generator is deterministic"

# Run the suite INSIDE the container (the image's pinned toolchain), like `dist`.
# The generated g*.py are gitignored, so regenerate them first (into the
# bind-mounted tree), then run pytest.  Exit 0 on success; on failure the inner
# command's nonzero status propagates out (make reports it as a recipe failure).
.PHONY: test
test: ## Run the full test suite INSIDE the container; exit 0 on success, nonzero on failure
	$(CONTAINER_CMD) run --rm \
		-v $(CURDIR):/gacalc:Z \
		--entrypoint /bin/bash \
		$(CONTAINER_NAME) \
		-c 'set -e; source /venv/bin/activate; cd /gacalc; python tools/gen_specialized.py; python -m pytest'

# Releasing runs inside the container (the image's pinned toolchain -- python,
# build, and twine, all baked in via the dev extras).  `dist` builds the
# sdist+wheel into $(DIST_DIR) on the host through a bind mount; `upload` runs
# `twine upload` in an INTERACTIVE (-it) container.  Auth uses an API token
# (TWINE_USERNAME=__token__), resolved in three ways, in order: (1) your
# ~/.pypirc -- mounted read-only when present (PYPIRC_MOUNT), the no-fuss path;
# (2) `export TWINE_PASSWORD=pypi-...` on the host (passed through via
# `-e TWINE_PASSWORD`, the CI-standard way); (3) pasted at the prompt.  `upload`
# uses the [pypi] section, `upload-test` the [testpypi] section (via `--repository
# testpypi`).  Nothing credential-bearing is stored in the image.  The ONLY
# host-side step is `git tag` in `release` -- git stays on the host, per the
# author's workflow.  Needs the image built (`make image`).
#
# NB: a 403 from PyPI/TestPyPI is almost always account-side, not a Makefile bug
# -- most often an UNVERIFIED account email (you must verify it before any upload)
# or a token for the wrong index (pypi.org and test.pypi.org are separate
# accounts/tokens).  Re-run the recipe's twine command with --verbose for the
# server's exact reason.
DIST_DIR ?= $(CURDIR)/dist
VERSION := $(shell python -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])")

# `make upload VERBOSE=1` (or upload-test / release) appends --verbose to twine,
# which prints the full request/response -- use it to see the server's exact
# reason for a 403.
VERBOSE ?=
TWINE_VERBOSE := $(if $(VERBOSE),--verbose)

.PHONY: dist
dist: ## Build sdist + wheel INSIDE the container -> $(DIST_DIR) on the host
	mkdir -p $(DIST_DIR)
	rm -f $(DIST_DIR)/*.whl $(DIST_DIR)/*.tar.gz   # drop stale builds so upload only sees this version
	$(CONTAINER_CMD) run --rm \
		-v $(CURDIR):/gacalc:Z \
		-v $(DIST_DIR):/dist:Z \
		--entrypoint /bin/bash \
		$(CONTAINER_NAME) \
		-c 'set -e; source /venv/bin/activate; cd /gacalc; \
		    GACALC_DIMS=$(ALL_DIMS) python tools/gen_specialized.py; \
		    python -m build --no-isolation --outdir /dist'

.PHONY: upload
upload: dist ## (container) twine check + interactive token upload of $(DIST_DIR)/* to PyPI
	$(CONTAINER_CMD) run --rm -it \
		-v $(DIST_DIR):/dist:Z \
		$(PYPIRC_MOUNT) \
		-e TWINE_USERNAME=__token__ \
		-e TWINE_PASSWORD \
		--entrypoint /bin/bash \
		$(CONTAINER_NAME) \
		-c 'source /venv/bin/activate; twine check /dist/* && twine upload $(TWINE_VERBOSE) /dist/*'

# Rehearse the whole build+upload flow against TestPyPI (a separate index with its
# own account/token -- get a token at https://test.pypi.org/manage/account/token/).
# --repository-url is passed explicitly so it needs no ~/.pypirc in the container.
.PHONY: upload-test
upload-test: dist ## (container) upload $(DIST_DIR)/* to TestPyPI to rehearse; -it, paste your TestPyPI token
	$(CONTAINER_CMD) run --rm -it \
		-v $(DIST_DIR):/dist:Z \
		$(PYPIRC_MOUNT) \
		-e TWINE_USERNAME=__token__ \
		-e TWINE_PASSWORD \
		--entrypoint /bin/bash \
		$(CONTAINER_NAME) \
		-c 'source /venv/bin/activate; twine check /dist/* && twine upload $(TWINE_VERBOSE) --repository testpypi /dist/*'

.PHONY: release
release: dist ## (host) version-tag guard + (container) upload + (host) git tag
	@git rev-parse "v$(VERSION)" >/dev/null 2>&1 \
		&& { echo "tag v$(VERSION) already exists -- bump version in pyproject.toml"; exit 1; } \
		|| true
	$(CONTAINER_CMD) run --rm -it \
		-v $(DIST_DIR):/dist:Z \
		$(PYPIRC_MOUNT) \
		-e TWINE_USERNAME=__token__ \
		-e TWINE_PASSWORD \
		--entrypoint /bin/bash \
		$(CONTAINER_NAME) \
		-c 'source /venv/bin/activate; twine check /dist/* && twine upload $(TWINE_VERBOSE) /dist/*'
	git tag "v$(VERSION)"
	@echo "Released $(VERSION). Push the tag with:  git push origin v$(VERSION)"


.PHONY: image-export
image-export: ## export the OCI image to a timestamped tar in the repo root
	$(CONTAINER_CMD) save $(CONTAINER_NAME) -o $(CONTAINER_NAME)-$(shell date +%m-%d-%Y_%H-%M-%S).tar

.PHONY: image-import
image-import: ## import an OCI image tar: make image-import FILE=foo.tar
	$(CONTAINER_CMD) load -i $(FILE)

.PHONY: help
help:
	@grep --extended-regexp '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
