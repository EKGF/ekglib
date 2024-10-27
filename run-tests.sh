#!/usr/bin/env bash
#
# run the python tests
#
GIT_ROOT="$(git rev-parse --show-toplevel)"
VIRTUAL_ENV="${GIT_ROOT}/.venv"

python_version="$(cat "${GIT_ROOT}/.python-version")"

flag_file="/tmp/ekglib-last-checked-environment.flag"

function checkEnvironment() {

  cd "${GIT_ROOT}" || return $?

  echo "========================== check environment"

  touch "${flag_file}" || return 1

  "${GIT_ROOT}/setup.sh" || return 1

  source "${VIRTUAL_ENV}/bin/activate"
}

function runLint() {

  echo "========================== lint"

  # stop the build if there are Python syntax errors or undefined names
  "${VIRTUAL_ENV}/bin/flake8" . --count --select=E9,F63,F7,F82 --show-source --statistics || return $?
  # exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
  "${VIRTUAL_ENV}/bin/flake8" . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics || return $?

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
