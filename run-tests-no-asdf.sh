#!/usr/bin/env bash
# This scriptlet creates a Python 3.10.8 virtual environment under the project folder (not to be checked in)
# and then once it is available it enters it and executes all the tests in the tests folder
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
VIRTUAL_ENV="${SCRIPT_DIR}/.venv"

if [ -d "${VIRTUAL_ENV}" ] ; then
  # shellcheck source=.venv/bin/activate
  source "${VIRTUAL_ENV}/bin/activate" || exit $?
  echo "Inside Python 3.10 Virtual Environment" >&2
else
  echo "WARNING: No Virtual Environment was found. Will create one NOW!" >&2
  if [[ ! $(which python3) ]] ; then
    echo "Python 3 not installed, please install a recent version of python e.g. by running %brew install python@3.10" >&2
    exit 1
  fi
  python3 -m venv "${VIRTUAL_ENV}" || exit $?
  # shellcheck source=.venv/bin/activate
  source "${VIRTUAL_ENV}/bin/activate" || exit $?
  "${VIRTUAL_ENV}/bin/pip3" install --upgrade pip setuptools && \
    "${VIRTUAL_ENV}/bin/pip3" install flake8 pytest pytest-cov && \
    "${VIRTUAL_ENV}/bin/pipenv" install || exit $?
  "${VIRTUAL_ENV}/bin/pipenv" || exit $?
  "${VIRTUAL_ENV}/bin/pip3" install -e . || exit $?
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
