.DEFAULT_GOAL := help

USE_SPYDER ?= 0
USE_EMACS ?= 0


CONTAINER_CMD = podman
CONTAINER_NAME = geometricalgebra

FILES_TO_MOUNT = -v $(shell pwd):/geometricalgebra/:Z \
		-v ./entrypoint/entrypoint.sh:/entrypoint.sh:Z \
		-v ./entrypoint/jupyter.sh:/usr/local/bin/jupyter.sh:Z \
		-v ./entrypoint/percentToIpynb.sh:/usr/local/bin/percentToIpynb.sh:Z \
		-v ./entrypoint/spyder.sh:/usr/local/bin/spyder.sh:Z \
		-v ./entrypoint/format.sh:/format.sh:Z \
		-v ./entrypoint/.bashrc:/root/.bashrc:Z

EXPOSE_PORT = -p 8888:8888


X_FLAGS_FOR_CONTAINER = -e DISPLAY=$(DISPLAY) \
	-v /tmp/.X11-unix:/tmp/.X11-unix \
	--security-opt label=type:container_runtime_t

WAYLAND_FLAGS_FOR_CONTAINER = -e "WAYLAND_DISPLAY=${WAYLAND_DISPLAY}" \
                              -e "XDG_RUNTIME_DIR=${XDG_RUNTIME_DIR}" \
                              -v "${XDG_RUNTIME_DIR}:${XDG_RUNTIME_DIR}"


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



.PHONY: help
help:
	@grep --extended-regexp '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
