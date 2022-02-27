#!/usr/bin/env bash
#
# run the python tests
#
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"

python_version=3.10.2

flag_file="/tmp/ekglib-last-checked-environment.flag"

#
# Returns true (0) if the python environment should be checked (which takes quite some time,
# we want to be able to continuously run run-test.sh during a development cycle because
# doing it from IntelliJ or other IDEs is not in all cases the easiest option)
#
function shouldCheckEnvironment() {
  #
  # If the flag file doesn't exist yet return true
  #
  [[ -f "${flag_file}" ]] || return 0
  #
  # If the flag file is older than X minutes then return true
  #
  find "${flag_file}" -mmin +5 -type f | grep -q flag && return 0
  #
  # If you added new dependencies then return true
  #
  [[ "${SCRIPT_DIR}/requirements.txt" -nt "${flag_file}" ]] && return 0
  #
  # Add whatever check here that you think should trigger a recheck of the environment
  #
  return 1
}

function checkEnvironment() {

  cd "${SCRIPT_DIR}" || return $?

  echo "========================== check environment"

  if ! shouldCheckEnvironment ; then
    echo "Skipping environment check"
    return 0
  fi

  touch "${flag_file}" || return 1

  # shellcheck disable=SC2035
  rm -f *.whl >/dev/null 2>&1

  if command -v apt-get >/dev/null 2>&1 ; then
    sudo apt-get install -y build-essential libssl-dev zlib1g-dev libbz2-dev \
      libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
      xz-utils tk-dev libffi-dev liblzma-dev python-openssl git
  fi

  if ! command -v asdf >/dev/null 2>&1 ; then
    if [[ "$(uname)" == "Darwin" ]] ; then
      brew install asdf
    fi
  fi

  if command -v asdf >/dev/null 2>&1 ; then
    asdf plugin-add python # takes no time when it's already installed
    if ! asdf install python ${python_version} ; then # takes no time when it's already installed
      echo "ERROR: Could not install python ${python_version}"
      return 1
    fi
    asdf local python ${python_version}
    #
    # See https://gist.github.com/rubencaro/888fb8e4f0811e79fa22b5ac39610c9e#setup-a-new-project
    #
    asdf exec python3 -m venv env
    source env/bin/activate
  else
    echo "ERROR: Please install asdf"
    return 1
  fi

  if ! command -v ~/.asdf/shims/python3 >/dev/null 2>&1 ; then
    echo "ERROR: You don't have ~/.asdf/shims/python3"
    return 1
  fi

  if [[ "$(~/.asdf/shims/python3 -V)" != "Python ${python_version}" ]] ; then
    echo "ERROR: Python version is not ${python_version}: $(~/.asdf/shims/python3 -V)"
    return 1
  fi

  ~/.asdf/shims/python3 -m pip install --upgrade pip wheel setuptools
  ~/.asdf/shims/python3 -m pip install flake8 pytest pytest-cov
  ~/.asdf/shims/python3 -m pip install -r requirements.txt --no-cache-dir
  ~/.asdf/shims/python3 -m pip wheel -r requirements.txt

  # shellcheck disable=SC2035
  rm -f *.whl >/dev/null 2>&1

  return 0
}

function runLint() {

  echo "========================== lint"

  # stop the build if there are Python syntax errors or undefined names
   ~/.asdf/shims/python3 -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || return $?
  # exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
   ~/.asdf/shims/python3 -m flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics || return $?

  echo "Lint was ok"
  return 0
}

#
# Create the .test directory (which is git ignored) with some easy to parse files
# that specify things like the LDAP naming context to use for tests etc.
# This way you can test against your local company server without revealing any
# company names and other confidential information ending up in git.
#
function createTestInfoFiles() {

  mkdir -p "${SCRIPT_DIR}/.test" >/dev/null 2>&1

  if [[ ! -f "${SCRIPT_DIR}/.test/ldap-domain" ]] ; then
    echo "your-kompany.kom" > "${SCRIPT_DIR}/.test/ldap-domain"
  fi

  return 0
}

function runTests() {

  local -r testWildCard="$*"
  local opts=""

  cd "${SCRIPT_DIR}" || return $?

  if [[ -n "${testWildCard}" ]] ; then
    opts+="-k ${testWildCard}"
  fi

  echo "========================== tests"

  # shellcheck disable=SC2086
   ~/.asdf/shims/python3 -m pytest tests/ -rA \
    --doctest-modules \
    --junitxml=junit/test-results.xml \
    --cov-report=html \
    --maxfail=2 \
    --showlocals \
    --tb=short ${opts}
  local -r rc=$?
  echo "pytest ended with rc=${rc}"
  return ${rc}
}

checkEnvironment || exit 1
runLint || exit 1
createTestInfoFiles || exit 1
# shellcheck disable=SC2068
runTests $@
exit $?
