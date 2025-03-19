#! /usr/bin/env bash

# Stop on error
set -e

readonly INSTALL_REPO="${HOME}/Programming/deployment-ansible"

if [ -f "/etc/os-release" ]; then
    readonly OSRELEASE="/etc/os-release"
elif [ -f "/usr/lib/os-release" ]; then
    readonly OSRELEASE="/usr/lib/os-release"
else
    echo "Cannot determine OS"
    exit 1
fi

readonly RED="\e[1;31m"
readonly GREEN="\e[1;32m"
readonly YELLOW="\e[1;33m"
readonly DEFAULT="\e[0m"

OS="$(uname | tr '[:upper:]' '[:lower:]')"
ID="$(grep -w "ID" "${OSRELEASE}" | cut -d'=' -f2)"
IDLIKE="$(grep -w "ID_LIKE" "${OSRELEASE}" | cut -d'=' -f2)"
[ -z "${IDLIKE}" ] && IDLIKE="${ID}"
readonly OS ID IDLIKE

if [ "${UID}" -eq 0 ]; then
    readonly SUDO=""
else
    readonly SUDO="sudo"
fi

function prompt() {
    echo -en "$*: "
}

function display_ko_ok() {
    [ "${1}" -eq 0 ] && echo -e "${GREEN}OK${DEFAULT}" || echo -e "${RED}KO${DEFAULT}"
}

function display_already_installed() {
    echo -e "${YELLOW}already installed${DEFAULT}"
}

function check_sudo() {
    if [ -n "${SUDO}" ]; then
        prompt "Asking for 'sudo' rights: "
        sudo -p "" -v
        display_ko_ok $?
    fi
}

function display_info() {
    # Display some information about the install
    echo "==================================="
    echo "Script: ${1}"
    echo "-----------------------------------"
    echo "Operating System: ${OS}"
    echo "Distribution ID: ${ID}"
    echo "Distribution IDLike: ${IDLIKE}"
    echo "User: ${USER}"
    echo "==================================="
}

# Install packages based on the OS.
# Check that the package is installed before installing it.
function install_packages() {
    local packages_to_install=("$@")
    local packages_not_installed=()
    local install_cmd=""

    # Get the command to install package and check that package is installed
    case "${OS}-${ID}" in
    "linux-endeavouros" | "linux-manjaro" | "linux-arch")
        install_cmd="pacman --sync --refresh --refresh --sysupgrade --needed --noconfirm"
        # Check that package is installed
        for pkg in "${packages_to_install[@]}"; do
            # Check if not already installed
            if ! pacman --query --search --quiet "${pkg}" | grep -qw "${pkg}" 2>&1; then
                packages_not_installed+=("${pkg}")
            fi
        done
        ;;

    "linux-ubuntu")
        install_cmd="apt-get install --assume-yes --quiet"
        # Check that package is installed
        for pkg in "${packages_to_install[@]}"; do
            # Check if not already installed
            if ! dpkg --get-selections | grep -w "${pkg}" | awk '{ print $2 }' | grep -q -w 'install'; then
                packages_not_installed+=("${pkg}")
            fi
        done
        ;;

    "freebsd-freebsd")
        install_cmd="pkg install --automatic --yes"
        # Check that package is installed
        for pkg in "${packages_to_install[@]}"; do
            # Check if already installed
            if ! pkg info | grep -qw "${pkg}"; then
                packages_not_installed+=("${pkg}")
            fi
        done
        ;;

    "linux-opensuse-tumbleweed")
        install_cmd="zypper --quiet --non-interactive install"
        # Check that package is installed
        for pkg in "${packages_to_install[@]}"; do
            # Check if already installed
            if ! zypper --quiet search --installed-only --match-exact "${pkg}" > /dev/null 2>&1; then
                packages_not_installed+=("${pkg}")
            fi
        done
        ;;

    "linux-fedora")
        install_cmd="dnf --assumeyes --quiet install --skip-unavailable"
        # Check that package is installed
        for pkg in "${packages_to_install[@]}"; do
            # Check if already installed
            if ! dnf list --installed "${pkg}" > /dev/null 2>&1; then
                packages_not_installed+=("${pkg}")
            fi
        done
        ;;

    *)
        echo "Unsupported distribution '${ID}' (based on OS '${OS}')"
        exit 1
        ;;
    esac

    # Install only the packages that are not already installed
    if [ ${#packages_not_installed[@]} -ne 0 ]; then
        check_sudo

        prompt "Installing ${packages_not_installed[*]}"
        # shellcheck disable=SC2086
        ${SUDO} ${install_cmd} "${packages_not_installed[@]}"
        display_ko_ok $?
    fi
}

display_info "${0}"

# Install packages
declare -A PACKAGES=(
    ["linux-arch"]="git ansible python-watchdog"
    ["linux-endeavouros"]="git ansible python-watchdog"
    ["linux-manjaro"]="git ansible python-watchdog"
    ["linux-ubuntu"]="git ansible python3-watchdog python3-debian"
    ["linux-debian"]="git ansible python3-watchdog python3-debian"
    ["linux-fedora"]="git ansible python3-watchdog"
    ["linux-opensuse-tumbleweed"]="git ansible python3-watchdog"
)

install_packages ${PACKAGES["${OS}-${ID}"]}

# Clone repo if it does not exist
prompt "Clone repo"
mkdir -p "$(dirname "${INSTALL_REPO}")"
if [ ! -d "${INSTALL_REPO}" ]; then
    git clone https://github.com/hbuyse/deployment-ansible "${INSTALL_REPO}"
    display_ko_ok $?

    echo "---" > "${INSTALL_REPO}"/host_vars/localhost.yml
    echo "git_user_name: \"\"" > "${INSTALL_REPO}"/host_vars/localhost.yml
    echo "git_user_email: \"\"" > "${INSTALL_REPO}"/host_vars/localhost.yml

    echo "DO NOT FORGET TO FILL THE FILE: host_vars/localhost.yml"
else
    display_already_installed
fi
