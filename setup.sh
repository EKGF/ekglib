#!/usr/bin/env bash
#
# This script is used to set up the environment for the project.
# It installs the required tools and packages and sets up the virtual environment.
#
# Usage: ./setup.sh
#
REPO_NAME="ekgf/ekglib"
GIT_ROOT="$(git rev-parse --show-toplevel)"
GIT_BRANCH="$(git name-rev --name-only HEAD)"
PROJECT_TMP_DIR="/tmp/ekglib/${GIT_BRANCH}/"
ACTUAL_VENV_DIR="${PROJECT_TMP_DIR}/.venv"
LOCAL_VENV_DIR="${GIT_ROOT}/.venv"
UV_PROJECT_ENVIRONMENT=".venv"

green_bold="\033[1;32m"
gray_bold="\033[1;30m"
blue_bold="\033[1;34m"
magenta_bold="\033[1;35m"
red_bold="\033[1;31m"
end_color="\033[0m"

function heading() {
    echo -e "${green_bold}>>>>>>> $* <<<<<<<${end_color}"
}

function subheading() {
    echo -e "${gray_bold}>>>>>>> $* <<<<<<<${end_color}"
}

function check_system() {
    if ! command -v python3 &> /dev/null ; then
        echo -e "${red_bold}ERROR: Python 3 is not installed or not on your PATH.${end_color}" >&2
        return 1
    fi

    return 0
}

function clean() {
    heading "Cleaning up"

    if [[ -d "${PROJECT_TMP_DIR}" ]] ; then
        rm -rf ${PROJECT_TMP_DIR}
    fi
    if [[ -d "${ACTUAL_VENV_DIR}" ]] ; then
        rm -rf ${ACTUAL_VENV_DIR}
    fi
    if [[ -d "${LOCAL_VENV_DIR}" ]] ; then
        rm -rf ${LOCAL_VENV_DIR}
    fi

    return 0
}

function recreate_venv() {
    heading "Recreating virtual environment"

    if [[ ! -d "${ACTUAL_VENV_DIR}" ]] ; then
        mkdir -p "${ACTUAL_VENV_DIR}" || return $?
    fi
    ln -sfn "${ACTUAL_VENV_DIR}" "${LOCAL_VENV_DIR}" || return $?
    if [[ -d "${LOCAL_VENV_DIR}" ]] ; then
        rm -rf "${LOCAL_VENV_DIR}" || return $?
    fi

    # Check if uv is available
    if ! command -v uv &> /dev/null ; then
        echo -e "${red_bold}ERROR: uv is not installed. Please install it first:${end_color}" >&2
        echo -e "${red_bold}  curl -LsSf https://astral.sh/uv/install.sh | sh${end_color}" >&2
        return 1
    fi

    # Create virtual environment using uv
    uv venv --system-site-packages "${LOCAL_VENV_DIR}" || return $?

    return 0
}

function install_stuff() {
    heading "Install stuff"

    if command -v apt-get >/dev/null 2>&1 ; then
        sudo apt-get install -y build-essential libssl-dev zlib1g-dev libbz2-dev \
            libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
            xz-utils tk-dev libffi-dev liblzma-dev python-openssl git
    fi

    # Install the dependencies using uv, which will also install all the tools
    # mentioned under [dependency-groups.dev] in the pyproject.toml file.
    subheading "uv sync"
    uv sync || return $?

    return 0
}

#
# Create the .test directory (which is git ignored) with some easy to parse files
# that specify things like the LDAP naming context to use for tests etc.
# This way you can test against your local company server without revealing any
# company names and other confidential information ending up in git.
#
function prepare_tests() {
    heading "Preparing for tests"

    mkdir -p "${GIT_ROOT}/.test" >/dev/null 2>&1

    if [[ ! -f "${GIT_ROOT}/.test/ldap-domain" ]] ; then
        echo "your-kompany.kom" > "${GIT_ROOT}/.test/ldap-domain"
    fi

    return 0
}

function move_cache() {
    local -r local_path="${1}"
    local -r real_path="${2}"

    if [[ -L "${local_path}" && -d "${local_path}" ]] ; then
        echo -r "${green_bold}${local_path}${end_color} is already a symlink to ${green_bold}$(realpath ${real_path})${end_color}"
    else
        if [[ ! -d "${real_path}" ]] ; then
            mkdir -p "${real_path}" || return $?
        fi
        ln -sfn "${real_path}" "${local_path}" || return $?
    fi

    return 0
}

# We need to move the bulky stuff to /tmp to avoid running out of space
function move_caches() {
    heading "Moving caches to /tmp"

    move_cache "${LOCAL_VENV_DIR}" "${ACTUAL_VENV_DIR}" || return $?
    move_cache "${GIT_ROOT}/.tox" "${PROJECT_TMP_DIR}/.tox" || return $?
    move_cache "${GIT_ROOT}/.mypy_cache" "${PROJECT_TMP_DIR}/.mypy_cache" || return $?
    move_cache "${GIT_ROOT}/.pytest_cache" "${PROJECT_TMP_DIR}/.pytest_cache" || return $?
    move_cache "${GIT_ROOT}/.ruff_cache" "${PROJECT_TMP_DIR}/.ruff_cache" || return $?

    return 0
}

function last_message() {
    heading "Setup complete"

    echo -e "Your environment has been set up successfully, you can now use commands like these:"
    echo -e " - ${blue_bold}source ${LOCAL_VENV_DIR}/bin/activate${end_color}"
    echo -e " - ${blue_bold}uv sync${end_color} to install the dependencies"
    echo -e " - ${blue_bold}tox${end_color} or ${blue_bold}uv run tox${end_color} to run all jobs like tests, linting, etc."
    echo -e " - ${blue_bold}pytest${end_color} or ${blue_bold}uv run pytest${end_color} to run tests"
    echo -e " - ${blue_bold}ruff format${end_color} or ${blue_bold}uv run ruff format${end_color} to format code"
    echo -e " - ${blue_bold}ruff check${end_color} or ${blue_bold}uv run ruff check${end_color} to run the ruff linter"
    echo ""
    echo "NOTE: Running these commands outside the context of an active virtual environment requires ~/.local/bin to be in your PATH"

    return 0
}

function main() {
    heading "Setting up environment for ${REPO_NAME}"

    check_system || return $?
    clean || return $?
    recreate_venv || return $?
    install_stuff || return $?
    move_caches || return $?
    prepare_tests || return $?
    last_message || return $?

    return 0
}

main
exit $?