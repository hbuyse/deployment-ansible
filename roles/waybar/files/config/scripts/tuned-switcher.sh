#! /usr/bin/env bash

SERVICE="tuned.service"
PROGRAM="$(command -v tuned-adm)"

declare -A PROFILE_SWITCHER
PROFILE_SWITCHER["powersave"]="balanced"
PROFILE_SWITCHER["balanced"]="accelerator-performance"
PROFILE_SWITCHER["accelerator-performance"]="powersave"

declare -A ICONS
ICONS["powersave"]=" "
ICONS["balanced"]=" "
ICONS["accelerator-performance"]=" "

send_signal() {
    pkill -x -SIGRTMIN+7 'waybar'
}

check() {
    if ! systemctl --quiet is-active "${SERVICE}"; then
        return 1
    fi

    if [ -z "${PROGRAM}" ]; then
        return 2
    fi
}

switch() {
    local current_profile

    current_profile=$(tuned-adm active | awk '{ print $4 }')

    if [[ -v "ICONS[${current_profile}]" ]]; then
        ${PROGRAM} profile "${PROFILE_SWITCHER[${current_profile}]}"
    fi
}

get() {
    local current_profile

    current_profile=$(tuned-adm active | awk '{ print $4 }')

    if [[ -v "ICONS[${current_profile}]" ]]; then
        printf '{ "text": "%s", "class": "%s", "tooltip": "Power profile: %s\\nDriver: tuned" }' \
            "${ICONS[${current_profile}]}" \
            "${current_profile}" \
            "${current_profile}"
    else
        printf '{ "text": " ", "class": "unknown", "tooltip": "Power profile: unknown\\nDriver: tuned" }'
    fi
}

case "$1" in
'get')
    get
    ;;
'switch')
    switch
    send_signal
    ;;
'check')
    check
    exit $?
    ;;
*) ;;
esac
