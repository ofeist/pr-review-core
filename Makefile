SHELL := /bin/bash
ROOT_DIR := $(abspath .)
SMOKE_VENV := .venv-smoke

.PHONY: smoke-package clean-package-artifacts

clean-package-artifacts:
	rm -rf build dist *.egg-info

smoke-package: clean-package-artifacts
	python3 -m venv $(SMOKE_VENV)
	$(SMOKE_VENV)/bin/python -m pip install --upgrade pip build
	$(SMOKE_VENV)/bin/python -m build
	$(SMOKE_VENV)/bin/pip install --force-reinstall dist/*.whl
	TMP_DIR="$$(mktemp -d)"; \
	  cd "$$TMP_DIR"; \
	  "$(ROOT_DIR)/$(SMOKE_VENV)/bin/python" -c "import core; print(core.__version__)"; \
	  "$(ROOT_DIR)/$(SMOKE_VENV)/bin/python" -m core.review.cli --help > /dev/null; \
	  rm -rf "$$TMP_DIR"

