#!/usr/bin/env bash

# This scriptlet creates a Python 3.10.7 virtual environment under the project folder (not to be checked in)
# and then once it is available it enters it and executes all the tests in the tests folder

if [[ ! $(which python3) ]] ; then
  echo "Python 3 not installed, please install Python 3.10.7, e.g. by running %brew install python@3.10"
  exit 1
fi
if ! python3 --version 2>/dev/null | grep -q "Python 3.10.7" ; then
  echo "ERROR: Please install Python 3.10.7" >&2
  exit 1
fi

if [ -d ./venv310 ] ; then
  source venv310/bin/activate || exit $?
  echo "Inside Python 3.10 Virtual Environment"
else
  echo "WARNING: No Virtual Environment was found. Will create one NOW!" >&2
  python3 -m venv venv310 || exit $?
  source venv310/bin/activate || exit $?
  python3 -m pip install --upgrade pip wheel setuptools \
    && python3 -m pip install flake8 pytest pytest-cov \
    && python3 -m pip install -r requirements.txt --no-cache-dir \
    && python3 -m pip wheel -r requirements.txt \
    || exit $?
  echo "Virtual Environment has been initialised successfully, will run the tests now"
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
