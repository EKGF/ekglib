#!/usr/bin/env bash
#
# run the python tests
#
GIT_ROOT="$(git rev-parse --show-toplevel)"
# Use $TMPDIR on macOS (user-specific temp dir) or /tmp on Linux
# Remove trailing slash if present to ensure clean path construction
TMP_BASE="${TMPDIR:-/tmp}"
TMP_BASE="${TMP_BASE%/}"
TEST_VENV_DIR="${TMP_BASE}/ekglib-test-venv"
VIRTUAL_ENV="${TEST_VENV_DIR}"

flag_file="${TMP_BASE}/ekglib-last-checked-environment.flag"

function checkEnvironment() {

  cd "${GIT_ROOT}" || return $?

  echo "========================== check environment"

  touch "${flag_file}" || return 1

  echo "Using test virtual environment at: ${VIRTUAL_ENV}"

  # Create venv in temp directory if it doesn't exist
  if [[ ! -d "${VIRTUAL_ENV}" ]] || [[ ! -f "${VIRTUAL_ENV}/bin/python" ]] ; then
    echo "Creating test virtual environment..."
    uv venv "${VIRTUAL_ENV}" || return 1
  fi

  # Install dependencies into the test venv
  # Use uv pip install to install project, runtime dependencies, and dev dependencies
  echo "Installing dependencies into test venv..."
  (
    unset VIRTUAL_ENV
    uv pip install --python "${TEST_VENV_DIR}/bin/python" -e . --group dev || return 1
  ) || return 1

  source "${VIRTUAL_ENV}/bin/activate"
}

function runLint() {

  echo "========================== lint"

  # Format check with ruff (using executable from test venv)
  "${VIRTUAL_ENV}/bin/ruff" format --check . || return $?
  
  # Lint with ruff (includes flake8-compatible checks)
  "${VIRTUAL_ENV}/bin/ruff" check . || return $?

  # Type check with mypy
  "${VIRTUAL_ENV}/bin/mypy" src || return $?

  echo "Lint was ok"
  return 0
}


function runTests() {

  local -r testWildCard="$*"
  local opts=""

  cd "${GIT_ROOT}" || return $?

  if [[ -n "${testWildCard}" ]] ; then
    opts+="-k ${testWildCard}"
  fi

  echo "========================== tests"

  # shellcheck disable=SC2086
  "${VIRTUAL_ENV}/bin/pytest" tests ${opts}
  local -r rc=$?
  echo "pytest ended with rc=${rc}"
  return ${rc}
}

checkEnvironment || exit 1
runLint || exit 1
# shellcheck disable=SC2068
runTests $@
exit $?
