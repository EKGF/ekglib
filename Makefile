
VIRTUAL_ENV := ./.venv
LANG := en

ifeq ($(OS),Windows_NT)
    YOUR_OS := Windows
    INSTALL_TARGET := install-windows
    SYSTEM_PYTHON := python3
else
    YOUR_OS := $(shell sh -c 'uname 2>/dev/null || echo Unknown')
ifeq ($(YOUR_OS), Linux)
    INSTALL_TARGET := install-linux
	MKDOCS := mkdocs
	SYSTEM_PYTHON := python3
endif
ifeq ($(YOUR_OS), Darwin)
	INSTALL_TARGET := install-macos
	OPEN_EDITORS_VERSION_TARGET := open-editors-version-macos
	OPEN_RELEASE_VERSION_TARGET := open-release-version-macos
	MKDOCS := mkdocs
	SYSTEM_PYTHON := python3
endif
endif

VENV_MKDOCS := $(VIRTUAL_ENV)/bin/mkdocs
VENV_PYTHON := $(VIRTUAL_ENV)/bin/python3

CURRENT_BRANCH := $(shell git branch --show-current)

.PHONY: all
all: docs-build

.PHONY: info
info: python-venv
	@echo "Git Branch: ${CURRENT_BRANCH}"
	@echo "Operating System: ${YOUR_OS}"
	@echo "System Python: ${SYSTEM_PYTHON} version: $$($(SYSTEM_PYTHON) --version)"
	@echo "Virtual Env Python: ${VENV_PYTHON} version: $$($(VENV_PYTHON) --version)"
	@echo "install target: ${INSTALL_TARGET}"

.PHONY: clean
clean:
	@echo Cleaning
	@rm -rf site 2>/dev/null |true
	@rm -rf .venv/lib/python3.10/site-packages 2>/dev/null || true

.PHONY: install
install: info install-brew install-brew-packages install-python-packages

.PHONY: install-github-actions
install-github-actions: info install-brew-packages install-python-packages

.PHONY: install-brew-packages
install-brew-packages:
	@echo "Install packages via HomeBrew:"
	brew upgrade cairo || brew install cairo
	brew upgrade freetype || brew install freetype
	brew upgrade libffi || brew install libffi
	brew upgrade pango || brew install pango
	brew upgrade libjpeg || brew install libjpeg
	brew upgrade libpng || brew install libpng
	brew upgrade zlib || brew install zlib
	brew upgrade plantuml || brew install plantuml
	brew upgrade graphviz || brew install graphviz

.PHONY: install-brew
ifeq ($(YOUR_OS), Linux)
install-brew: install-brew-linux
endif
ifeq ($(YOUR_OS), Windows)
install-brew: install-brew-windows
endif
ifeq ($(YOUR_OS), Darwin)
install-brew: install-brew-macos
endif

.PHONY: install-brew-linux
install-brew-linux:
	@if ! command -v brew >/dev/null 2>&1 ; then echo "Install HomeBrew" ; exit 1 ; fi
	brew --version

#
# not sure if HomeBrew can be installed on Windows, this part has not been tested yet!
#
.PHONY: install-brew-windows
install-brew-windows:
	@if ! command -v brew >/dev/null 2>&1 ; then echo "Install HomeBrew" ; exit 1 ; fi
	brew --version

.PHONY: install-brew-macos
install-brew-macos:
	@if ! command -v brew >/dev/null 2>&1 ; then echo "Install HomeBrew" ; exit 1 ; fi
	brew --version

.PHONY: install-python-packages
install-python-packages: install-standard-python-packages install-special-python-packages

.PHONY: install-standard-python-packages
install-standard-python-packages:
	@echo "Install dependencies using uv (uv will create .venv automatically if needed):"
	uv sync

.PHONY: install-special-python-packages
install-special-python-packages:

$(VENV_MKDOCS): install-python-packages

.PHONY: python-venv
python-venv:
	@echo "Note: uv automatically creates .venv when running 'uv sync' or 'uv run'"
	@if [ ! -d "$(VIRTUAL_ENV)" ] ; then \
		uv sync ; \
	fi

.PHONY: format
format:
	uv run ruff format .

.PHONY: format-check
format-check:
	uv run ruff format --check .

.PHONY: lint
lint:
	uv run ruff check .

.PHONY: lint-fix
lint-fix:
	uv run ruff check --fix .

.PHONY: check
check: format-check lint
