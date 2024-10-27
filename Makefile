
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
ifneq ($(wildcard /home/runner/.*),) # this means we're running in Github Actions
	MKDOCS := mkdocs
	PIP := pip
	SYSTEM_PYTHON := python3
else
	MKDOCS := $(shell asdf where python)/bin/mkdocs
	PIP := $(shell asdf where python)/bin/python -m pip
	SYSTEM_PYTHON := $(shell asdf where python)/bin/python3
endif
endif
ifeq ($(YOUR_OS), Darwin)
	INSTALL_TARGET := install-macos
	OPEN_EDITORS_VERSION_TARGET := open-editors-version-macos
	OPEN_RELEASE_VERSION_TARGET := open-release-version-macos
	MKDOCS := $(shell asdf where python)/bin/mkdocs
	PIP := $(shell asdf where python)/bin/python -m pip
	SYSTEM_PYTHON := $(shell asdf where python)/bin/python3
endif
endif

VENV_POETRY := $(VIRTUAL_ENV)/bin/poetry
VENV_MKDOCS := $(VIRTUAL_ENV)/bin/mkdocs
VENV_PYTHON := $(VIRTUAL_ENV)/bin/python3
VENV_PIP    := $(VIRTUAL_ENV)/bin/pip3
VENV_PIPENV := $(VIRTUAL_ENV)/bin/pipenv

PIPENV_DEFAULT_PYTHON_VERSION := 3.13
PIPENV_VENV_IN_PROJECT := 1

CURRENT_BRANCH := $(shell git branch --show-current)

.PHONY: all
all: docs-build

.PHONY: info
info: python-venv
	@echo "Git Branch: ${CURRENT_BRANCH}"
	@echo "Operating System: ${YOUR_OS}"
	@echo "System Python: ${SYSTEM_PYTHON} version: $$($(SYSTEM_PYTHON) --version)"
	@echo "Virtual Env Python: ${VENV_PYTHON} version: $$($(VENV_PYTHON) --version)"
	@echo "Python pip: ${VENV_PIP}"
	@echo "Python pipenv: ${VENV_PIPENV}"
	@echo "Python poetry: ${VENV_POETRY}"
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

.PHONY: install-asdf
ifneq ($(wildcard /home/runner/.*),)
install-asdf: install-brew
	@echo "Install the asdf package manager:"
	brew upgrade asdf || brew install asdf
	asdf plugin add python || true
	asdf plugin add nodejs || true
	asdf plugin add java || true
else
install-asdf:
endif

.PHONY: install-asdf-packages
install-asdf-packages: install-asdf
	@echo "Install packages via asdf:"
	asdf install

.PHONY: install-python-packages
install-python-packages: install-asdf-packages install-standard-python-packages install-special-python-packages

.PHONY: install-standard-python-packages
install-standard-python-packages: python-venv
	@echo "Install standard python packages via pip:"
	$(VENV_PIP) install --upgrade pip setuptools
	$(VENV_PIP) install poetry
	$(VENV_POETRY) config virtualenvs.in-project true

.PHONY: install-special-python-packages
install-special-python-packages:

$(VENV_MKDOCS): install-python-packages

.PHONY: python-venv
python-venv:
	$(SYSTEM_PYTHON) -m venv --upgrade --upgrade-deps $(VIRTUAL_ENV)
