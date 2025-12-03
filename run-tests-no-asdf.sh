#!/usr/bin/env bash
# This scriptlet creates a virtual environment under the project folder (not to be checked in)
# and then once it is available it enters it and executes all the tests in the tests folder
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
VIRTUAL_ENV="${SCRIPT_DIR}/.venv"

if [ -d "${VIRTUAL_ENV}" ] ; then
  # shellcheck source=.venv/bin/activate
  source "${VIRTUAL_ENV}/bin/activate" || exit $?
  echo "Inside Virtual Environment" >&2
else
  echo "WARNING: No Virtual Environment was found. Will create one NOW!" >&2
  if [[ ! $(which uv) ]] ; then
    echo "uv not installed, please install it first: curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
    exit 1
  fi
  uv venv "${VIRTUAL_ENV}" || exit $?
  # shellcheck source=.venv/bin/activate
  source "${VIRTUAL_ENV}/bin/activate" || exit $?
  uv sync || exit $?
  echo "Virtual Environment has been initialised successfully, will run the tests now" >&2
fi

echo "========================== tests" >&2
# shellcheck disable=SC2086
"${VIRTUAL_ENV}/bin/pytest" tests/ -rA \
  --doctest-modules \
  --junitxml=junit/test-results.xml \
  --cov-report=html \
  --maxfail=2 \
  --showlocals \
  --tb=short ${@}
rc=$?
echo "pytest ended with rc=${rc}" >&2
exit ${rc}
