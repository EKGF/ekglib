#!/usr/bin/env bash

# This scriptlet creates a Python 3.8 virtual environment under the project folder (not to be checked in)
# and then once it is available it enters it and executes all the tests in the tests folder

if [[ ! $(which python3) ]] ; then
  echo "Python 3 not installed, please install Python 3.8, e.g. by running %brew install python@3.8"
  exit 1
fi

if [ -d ./venv38 ] ; then
  source venv38/bin/activate || exit $?
  echo "Inside Python 3.8 Virtual Environment"
else
  echo "WARNING: Cannot run tests, no Virtual Environment was found. Will create one NOW!" >&2
  python3 -m venv venv38 || exit $?
  source venv38/bin/activate || exit $?
  python3 -m pip install --upgrade pip wheel setuptools \
    && python3 -m pip install flake8 pytest pytest-cov --use-feature=2020-resolver \
    && python3 -m pip install -r requirements.txt --no-cache-dir --use-feature=2020-resolver \
    && python3 -m pip wheel -r requirements.txt \
    || exit $?
  echo "Virtual Enviroment has been initialised successfully, please re-run this script to run tests now"
  exit 2
fi

echo "========================== tests"
# shellcheck disable=SC2086
python3 -m pytest tests/ -rA \
  --doctest-modules \
  --junitxml=junit/test-results.xml \
  --cov-report=html \
  --maxfail=2 \
  --showlocals \
  --tb=short ${opts}
rc=$?
echo "pytest ended with rc=${rc}"
exit ${rc}
