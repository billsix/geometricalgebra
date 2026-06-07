.DEFAULT_GOAL := help

USE_SPYDER ?= 0
USE_EMACS ?= 0


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



GENERATED = src/gacalc/scalar.py \
            src/gacalc/g1.py \
            src/gacalc/g2.py \
            src/gacalc/g3.py

.PHONY: generate
generate: ## Generate the specialized algebras (scalar/g1/g2/g3.py) -- needs sympy
	python tools/gen_specialized.py

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

# Releases are split: the package is BUILT inside the container (the image's
# pinned toolchain -- python, build, numpy/sympy), and the resulting sdist+wheel
# land in $(DIST_DIR) on the host through a bind mount.  PUSHING to PyPI happens
# OUTSIDE the container -- `twine` on the host, with your credentials -- since
# uploading is irreversible and credential-bearing.  Needs the image built
# (`make image`); the host needs `twine` for upload (e.g. `pipx install twine`).
DIST_DIR ?= $(CURDIR)/dist
VERSION := $(shell python -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])")

.PHONY: dist
dist: ## Build sdist + wheel INSIDE the container -> $(DIST_DIR) on the host
	mkdir -p $(DIST_DIR)
	$(CONTAINER_CMD) run --rm \
		-v $(CURDIR):/gacalc:Z \
		-v $(DIST_DIR):/output:Z \
		--entrypoint /bin/bash \
		$(CONTAINER_NAME) \
		-c 'set -e; cd /gacalc; \
		    python tools/gen_specialized.py; \
		    python -m build --no-isolation --outdir /output'

.PHONY: upload
upload: dist ## (host) twine check + upload $(DIST_DIR)/* to PyPI -- irreversible
	twine check $(DIST_DIR)/*
	twine upload $(DIST_DIR)/*

.PHONY: release
release: dist ## Build (in container), then (host) tag + upload the pyproject version
	@git rev-parse "v$(VERSION)" >/dev/null 2>&1 \
		&& { echo "tag v$(VERSION) already exists -- bump version in pyproject.toml"; exit 1; } \
		|| true
	twine check $(DIST_DIR)/*
	twine upload $(DIST_DIR)/*
	git tag "v$(VERSION)"
	@echo "Released $(VERSION). Push the tag with:  git push origin v$(VERSION)"


.PHONY: help
help:
	@grep --extended-regexp '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
