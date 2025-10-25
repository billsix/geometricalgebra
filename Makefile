.DEFAULT_GOAL := help

CONTAINER_CMD = podman
CONTAINER_NAME = geometricalgebra
FILES_TO_MOUNT = -v $(shell pwd):/geometricalgebra/:Z


.PHONY: all
all: clean image html ## Build the HTML and PDF from scratch in Debian Bulleye

.PHONY: image
image: ## Build a podman image in which to build the book
	$(CONTAINER_CMD) build -t $(CONTAINER_NAME) .


.PHONY: shell
shell:  ## Get Shell into a ephermeral container made from the image
	$(CONTAINER_CMD) run -it --rm \
		--entrypoint /bin/bash \
		$(FILES_TO_MOUNT) \
		-v ./entrypoint/shell.sh:/shell.sh:Z \
		$(USE_X) \
		$(CONTAINER_NAME) \
		/shell.sh



.PHONY: help
help:
	@grep --extended-regexp '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
